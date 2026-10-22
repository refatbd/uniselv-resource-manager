import os
import sys
import time
import json
import stat
import sqlite3
import pathlib
import re
import glob
import subprocess
import signal
from typing import Dict, List, Optional, Tuple, Any

# Ensure we can import schema
from schema import init_db

def parse_bw_to_bytes(val: Any) -> Tuple[int, int]:
    """Returns tuple of (decimal_bytes, binary_bytes) for bandwidth limit strings."""
    if not val:
        return (0, 0)
    s = str(val).strip().upper()
    if s.endswith('K'):
        num = float(s[:-1])
        return (int(num * 1000), int(num * 1024))
    elif s.endswith('M'):
        num = float(s[:-1])
        return (int(num * 1000 * 1000), int(num * 1024 * 1024))
    elif s.endswith('G'):
        num = float(s[:-1])
        return (int(num * 1000 * 1000 * 1000), int(num * 1024 * 1024 * 1024))
    elif s.endswith('T'):
        num = float(s[:-1])
        return (int(num * 1000 * 1000 * 1000 * 1000), int(num * 1024 * 1024 * 1024 * 1024))
    elif s.isdigit():
        n = int(s)
        return (n, n)
    return (0, 0)

def parse_iops(val: Any) -> int:
    """Parses integer IOPS value from string/int."""
    if not val:
        return 0
    s = str(val).strip()
    if s.isdigit():
        return int(s)
    return 0

def format_bytes(b: Any) -> str:
    if not b:
        return "0 B"
    if isinstance(b, str):
        if not b.isdigit():
            dec, _ = parse_bw_to_bytes(b)
            if dec > 0:
                b = dec
            else:
                return str(b)
        else:
            b = int(b)
    elif not isinstance(b, (int, float)):
        try:
            b = int(b)
        except Exception:
            return str(b)

    if b < 1024:
        return f"{b} B"
    elif b < 1024 * 1024:
        return f"{round(b / 1024, 1)} KiB"
    elif b < 1024 * 1024 * 1024:
        return f"{round(b / 1024 / 1024, 1)} MiB"
    else:
        return f"{round(b / 1024 / 1024 / 1024, 2)} GiB"


def parse_key_value_file(path: str) -> Dict[str, str]:
    res = {}
    if not os.path.exists(path):
        return res
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 2:
                    res[parts[0]] = parts[1]
    except Exception:
        pass
    return res

def parse_int_file(path: str) -> int:
    if not os.path.exists(path):
        return 0
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            c = f.read().strip()
            if c == 'max' or c == 'infinity':
                return -1
            return int(c)
    except Exception:
        return 0

def parse_io_stat(path: str) -> Dict[str, int]:
    res = {'rbytes': 0, 'wbytes': 0, 'rios': 0, 'wios': 0}
    if not os.path.exists(path):
        return res
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) > 1:
                    for item in parts[1:]:
                        if '=' in item:
                            k, v = item.split('=', 1)
                            if k in res and v.isdigit():
                                res[k] += int(v)
    except Exception:
        pass
    return res

def redact_command_line(cmdline: str) -> str:
    """Sanitize sensitive arguments, passwords, credentials, tokens."""
    if not cmdline:
        return ""
    # Redact common credential patterns
    patterns = [
        (r'(--(?:password|pass|secret|token|apikey|key|auth|dbpass|pin)=)(?:[^\s]+)', r'\1[REDACTED]'),
        (r'(-p)(?:[^\s]+)', r'-p[REDACTED]'),
        (r'(bearer\s+)[a-zA-Z0-9_\-\.]+', r'\1[REDACTED]'),
        (r'([a-zA-Z0-9_\-\.]*token[a-zA-Z0-9_\-\.]*=)[^\s&]+', r'\1[REDACTED]'),
        (r'(pass(?:word)?=)[^\s&]+', r'\1[REDACTED]'),
    ]
    redacted = cmdline
    for pat, rep in patterns:
        redacted = re.sub(pat, rep, redacted, flags=re.IGNORECASE)
    return redacted

class MetricsCollector:
    def __init__(self, db_path: str = '/var/lib/uniselv-resource-manager/resman.sqlite'):
        self.db_path = db_path
        init_db(self.db_path)
        self.prev_user_stats: Dict[str, Dict[str, Any]] = {}
        self.prev_sys_cpu: Optional[Tuple[int, int]] = None
        self.prev_time = time.monotonic()
        self.prev_epoch = int(time.time())
        self.host_cpu_count = os.cpu_count() or 4
        self.settings: Dict[str, Any] = {}
        self.last_snapshot_time: Dict[str, float] = {}
        self.last_hourly_snapshot_time: Dict[str, float] = {}
        self.pressure_history: Dict[str, List[bool]] = {}
        self.last_sustained_event_time: Dict[str, float] = {}
        self.runaway_proc_tracker: Dict[Tuple[int, int], Dict[str, Any]] = {}
        self.proc_prev_ticks: Dict[Tuple[int, int], Tuple[int, float, int]] = {}
        self.circuit_breaker_active: bool = False
        self.circuit_breaker_throttled_users: Dict[int, int] = {}
        self.circuit_breaker_tripped_at: float = 0.0
        self.circuit_breaker_min_hold_down_sec: float = 30.0
        self.reload_settings()
        self._load_circuit_breaker_durable_state()

    def reload_settings(self):
        """Load feature settings, toggles and thresholds from SQLite settings table."""
        conn = self.get_db_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT key, value FROM settings")
            rows = dict(cur.fetchall())
            cpus = self.host_cpu_count or 4
            def_load = round(cpus * 0.80, 2)
            def_rec = round(cpus * 0.55, 2)
            self.settings = {
                'telemetry_enabled': bool(int(rows.get('telemetry_enabled', '1'))),
                'telemetry_interval': int(rows.get('telemetry_interval', '5')),
                'snapshot_on_throttle': bool(int(rows.get('snapshot_on_throttle', '1'))),
                'snapshot_on_oom': bool(int(rows.get('snapshot_on_oom', '1'))),
                'snapshot_on_task_limit': bool(int(rows.get('snapshot_on_task_limit', '1'))),
                'snapshot_cooldown_sec': int(rows.get('snapshot_cooldown_sec', '60')),
                'alert_threshold_cpu': int(rows.get('alert_threshold_cpu', '75')),
                'alert_threshold_mem': int(rows.get('alert_threshold_mem', '80')),
                'alert_threshold_tasks': int(rows.get('alert_threshold_tasks', '80')),
                'enduser_allow_kill': bool(int(rows.get('enduser_allow_kill', '1'))),
                'enduser_allow_export': bool(int(rows.get('enduser_allow_export', '1'))),
                'enduser_allow_db_trace': bool(int(rows.get('enduser_allow_db_trace', '1'))),
                'auto_prune_hourly': bool(int(rows.get('auto_prune_hourly', '1'))),
                'retention_samples_days': int(rows.get('retention_samples_days', '30')),
                'retention_snapshots_days': int(rows.get('retention_snapshots_days', '14')),
                'retention_events_days': int(rows.get('retention_events_days', '30')),
                'retention_audit_days': int(rows.get('retention_audit_days', '90')),
                'retention_max_storage_mib': int(rows.get('retention_max_storage_mib', '100')),
                'enable_runaway_watchdog': bool(int(rows.get('enable_runaway_watchdog', '1'))),
                'watchdog_action': str(rows.get('watchdog_action', 'notify')),
                'runaway_watchdog_kill_enabled': bool(int(rows.get('runaway_watchdog_kill_enabled', '0'))),
                'watchdog_require_account_saturation': bool(int(rows.get('watchdog_require_account_saturation', '1'))),
                'watchdog_excluded_commands': str(rows.get('watchdog_excluded_commands', '')),
                'runaway_cpu_percent': int(rows.get('runaway_cpu_percent', '80')),
                'runaway_max_duration_sec': int(rows.get('runaway_max_duration_sec', '120')),
                'enable_circuit_breaker': bool(int(rows.get('enable_circuit_breaker', '1'))),
                'circuit_breaker_load_threshold': float(rows.get('circuit_breaker_load_threshold', str(def_load))),
                'circuit_breaker_recovery_threshold': float(rows.get('circuit_breaker_recovery_threshold', str(def_rec))),
            }
        except Exception:
            cpus = self.host_cpu_count or 4
            def_load = round(cpus * 0.80, 2)
            def_rec = round(cpus * 0.55, 2)
            self.settings = {
                'telemetry_enabled': True,
                'telemetry_interval': 5,
                'snapshot_on_throttle': True,
                'snapshot_on_oom': True,
                'snapshot_on_task_limit': True,
                'snapshot_cooldown_sec': 60,
                'alert_threshold_cpu': 75,
                'alert_threshold_mem': 80,
                'alert_threshold_tasks': 80,
                'enduser_allow_kill': True,
                'enduser_allow_export': True,
                'enduser_allow_db_trace': True,
                'auto_prune_hourly': True,
                'retention_samples_days': 30,
                'retention_snapshots_days': 14,
                'retention_events_days': 30,
                'retention_audit_days': 90,
                'retention_max_storage_mib': 100,
                'enable_runaway_watchdog': True,
                'watchdog_action': 'notify',
                'runaway_watchdog_kill_enabled': False,
                'watchdog_require_account_saturation': True,
                'watchdog_excluded_commands': '',
                'runaway_cpu_percent': 80,
                'runaway_max_duration_sec': 120,
                'enable_circuit_breaker': True,
                'circuit_breaker_load_threshold': def_load,
                'circuit_breaker_recovery_threshold': def_rec,
            }
        finally:
            conn.close()

    def get_db_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=30)
        conn.row_factory = sqlite3.Row
        return conn

    def get_webuzo_users(self) -> Dict[str, Dict[str, Any]]:
        """Discover Webuzo users, UIDs, and assigned resource plans."""
        users = {}
        users_dir = '/var/webuzo/users'
        if not os.path.exists(users_dir):
            return users

        for uname in os.listdir(users_dir):
            info_file = os.path.join(users_dir, uname, 'info')
            if os.path.isfile(info_file):
                try:
                    with open(info_file, 'r', encoding='utf-8', errors='replace') as f:
                        data = json.load(f)
                        plan_name = data.get('resource_limit', 'default')
                        # Get UID from system
                        import pwd
                        try:
                            pw = pwd.getpwnam(uname)
                            uid = pw.pw_uid
                        except KeyError:
                            continue
                        users[uname] = {
                            'username': uname,
                            'uid': uid,
                            'plan_name': plan_name,
                            'domain': data.get('domain', f"{uname}.local"),
                            'owner': data.get('owner') or 'root',
                            'reseller': str(data.get('reseller', '')).strip().lower() in ('1', 'true', 'yes', 'on')
                        }
                except Exception:
                    pass
        return users

    def get_plan_limits(self, plan_name: str) -> Dict[str, Any]:
        """Read native Webuzo resource limit plan definition."""
        plan_file = f'/var/webuzo/cgroups/{plan_name}'
        limits = {
            'cpuquota': 100,  # default 100% = 1 core
            'mem_max': 1024 * 1024 * 1024,
            'memhigh': 800 * 1024 * 1024,
            'maxtask': 128,
            'read_bw': 100 * 1024 * 1024,
            'write_bw': 50 * 1024 * 1024,
            'diskread': 1000,
            'diskwrite': 500
        }
        if os.path.exists(plan_file):
            try:
                with open(plan_file, 'r', encoding='utf-8', errors='replace') as f:
                    data = json.load(f)
                    if 'cpuquota' in data and data['cpuquota']:
                        limits['cpuquota'] = int(data['cpuquota'])
                    if 'maxtask' in data and data['maxtask']:
                        limits['maxtask'] = int(data['maxtask'])
                    if 'mem_max' in data and data['mem_max']:
                        raw = data['mem_max'].upper()
                        if raw.endswith('M'):
                            limits['mem_max'] = int(raw[:-1]) * 1024 * 1024
                        elif raw.endswith('G'):
                            limits['mem_max'] = int(raw[:-1]) * 1024 * 1024 * 1024
                        elif raw.isdigit():
                            limits['mem_max'] = int(raw)
                    if 'memhigh' in data and data['memhigh']:
                        raw = data['memhigh'].upper()
                        if raw.endswith('M'):
                            limits['memhigh'] = int(raw[:-1]) * 1024 * 1024
                        elif raw.endswith('G'):
                            limits['memhigh'] = int(raw[:-1]) * 1024 * 1024 * 1024
                        elif raw.isdigit():
                            limits['memhigh'] = int(raw)
                    if 'read_bw' in data and data['read_bw']:
                        limits['read_bw'] = data['read_bw']
                    if 'write_bw' in data and data['write_bw']:
                        limits['write_bw'] = data['write_bw']
                    if 'diskread' in data and data['diskread']:
                        limits['diskread'] = int(data['diskread']) if str(data['diskread']).isdigit() else data['diskread']
                    if 'diskwrite' in data and data['diskwrite']:
                        limits['diskwrite'] = int(data['diskwrite']) if str(data['diskwrite']).isdigit() else data['diskwrite']
            except Exception:
                pass
        return limits

    def read_user_cgroup(self, uid: int) -> Tuple[str, Dict[str, Any]]:
        """Locate active cgroup slice for UID and parse stats."""
        # Check native slice and golden shield slice
        candidates = [
            f'/sys/fs/cgroup/golden.slice/golden-{uid}.slice',
            f'/sys/fs/cgroup/{uid}.slice'
        ]
        chosen = None
        for cand in candidates:
            if os.path.exists(cand):
                chosen = cand
                # Prefer one that has current processes or memory > 0
                mem_cur = parse_int_file(os.path.join(cand, 'memory.current'))
                if mem_cur > 0:
                    break

        if not chosen:
            chosen = f'/sys/fs/cgroup/{uid}.slice'

        stats = {
            'slice_path': chosen,
            'cpu_usage_usec': 0,
            'nr_throttled': 0,
            'throttled_usec': 0,
            'mem_current': 0,
            'mem_anon': 0,
            'mem_file': 0,
            'mem_swap': 0,
            'oom_kill': 0,
            'mem_high_events': 0,
            'mem_max_events': 0,
            'tasks_current': 0,
            'task_limit_events': 0,
            'io': {'rbytes': 0, 'wbytes': 0, 'rios': 0, 'wios': 0}
        }

        if os.path.exists(chosen):
            # CPU
            cpu_stat = parse_key_value_file(os.path.join(chosen, 'cpu.stat'))
            stats['cpu_usage_usec'] = int(cpu_stat.get('usage_usec', 0))
            stats['nr_throttled'] = int(cpu_stat.get('nr_throttled', 0))
            stats['throttled_usec'] = int(cpu_stat.get('throttled_usec', 0))

            # Memory
            stats['mem_current'] = parse_int_file(os.path.join(chosen, 'memory.current'))
            stats['mem_swap'] = parse_int_file(os.path.join(chosen, 'memory.swap.current'))
            mem_stat = parse_key_value_file(os.path.join(chosen, 'memory.stat'))
            stats['mem_anon'] = int(mem_stat.get('anon', 0))
            stats['mem_file'] = int(mem_stat.get('file', 0))

            mem_events = parse_key_value_file(os.path.join(chosen, 'memory.events'))
            stats['oom_kill'] = int(mem_events.get('oom_kill', 0))
            stats['mem_high_events'] = int(mem_events.get('high', 0))
            stats['mem_max_events'] = int(mem_events.get('max', 0))

            # Tasks
            stats['tasks_current'] = parse_int_file(os.path.join(chosen, 'pids.current'))
            pid_events = parse_key_value_file(os.path.join(chosen, 'pids.events'))
            stats['task_limit_events'] = int(pid_events.get('max', 0))

            # IO
            stats['io'] = parse_io_stat(os.path.join(chosen, 'io.stat'))

        return chosen, stats

    def read_system_cpu(self) -> Tuple[int, int]:
        """Read /proc/stat CPU totals for delta calculation."""
        try:
            with open('/proc/stat', 'r') as f:
                first_line = f.readline()
                fields = [int(x) for x in first_line.split()[1:]]
                idle = fields[3] + fields[4]
                total = sum(fields)
                return total, idle
        except Exception:
            return 0, 0

    def get_process_list_for_user(self, uid: int, slice_path: str) -> List[Dict[str, Any]]:
        """Get list of active processes belonging to user with sanitized cmdline."""
        procs = []
        pids_file = os.path.join(slice_path, 'cgroup.procs')
        pids = []
        if os.path.exists(pids_file):
            try:
                with open(pids_file, 'r') as f:
                    pids = [int(p.strip()) for p in f if p.strip().isdigit()]
            except Exception:
                pass

        # If cgroup.procs is empty, also check by UID in /proc as fallback
        if not pids:
            for entry in os.listdir('/proc'):
                if entry.isdigit():
                    pid = int(entry)
                    try:
                        stat_path = f'/proc/{pid}'
                        if os.stat(stat_path).st_uid == uid:
                            pids.append(pid)
                    except Exception:
                        pass

        uptime = 0.0
        try:
            with open('/proc/uptime', 'r') as uf:
                uptime = float(uf.read().split()[0])
        except Exception:
            pass

        clk_tck = os.sysconf('SC_CLK_TCK') if hasattr(os, 'sysconf') else 100
        page_size = os.sysconf('SC_PAGE_SIZE') if hasattr(os, 'sysconf') else 4096

        for pid in pids:
            try:
                proc_stat_path = f'/proc/{pid}/stat'
                cmdline_path = f'/proc/{pid}/cmdline'

                if not os.path.exists(proc_stat_path):
                    continue

                with open(proc_stat_path, 'r', encoding='utf-8', errors='replace') as f:
                    stat_content = f.read()
                    # format: pid (comm) state ppid pgrp session tty_nr tpgid flags minflt cminflt majflt cmajflt utime stime cutime cstime priority nice num_threads itrealvalue starttime vsize rss ...
                    m = re.match(r'^(\d+)\s+\((.+?)\)\s+([A-Z])\s+(\d+)\s+.*?\s+(\d+)\s+(\d+)\s+(\d+)\s+.*?\s+(\d+)\s+(\d+)\s+(\d+)', stat_content)
                    comm = "unknown"
                    ppid = 0
                    start_time = 0
                    rss_pages = 0
                    utime = 0
                    stime = 0
                    if m:
                        comm = m.group(2)
                        ppid = int(m.group(4))
                        parts = stat_content[stat_content.rfind(')') + 2:].split()
                        utime = int(parts[11]) if len(parts) > 11 else 0
                        stime = int(parts[12]) if len(parts) > 12 else 0
                        start_time = int(parts[19]) if len(parts) > 19 else 0
                        rss_pages = int(parts[21]) if len(parts) > 21 else 0

                raw_cmdline = ""
                if os.path.exists(cmdline_path):
                    with open(cmdline_path, 'rb') as f:
                        raw_bytes = f.read()
                        raw_cmdline = raw_bytes.replace(b'\x00', b' ').decode('utf-8', errors='replace').strip()

                if not raw_cmdline:
                    raw_cmdline = f"[{comm}]"

                sanitized_cmdline = redact_command_line(raw_cmdline)
                rss_bytes = rss_pages * page_size
                rss_mb = round(rss_bytes / (1024 * 1024))

                elapsed_sec = max(0.05, uptime - (start_time / clk_tck))
                cpu_sec = (utime + stime) / clk_tck
                cpu_percent = round((cpu_sec / elapsed_sec) * 100.0, 1)

                now_t = time.time()
                key = (uid, pid)
                prev_t = self.proc_prev_ticks.get(key)
                if prev_t and prev_t[2] == start_time:
                    delta_ticks = (utime + stime) - prev_t[0]
                    delta_time = now_t - prev_t[1]
                    if delta_time >= 0.5:
                        instant_cpu = round(((delta_ticks / clk_tck) / delta_time) * 100.0, 1)
                        if instant_cpu > cpu_percent:
                            cpu_percent = instant_cpu
                self.proc_prev_ticks[key] = (utime + stime, now_t, start_time)

                # Real-Time Process & Script Identification (cPanel / CloudLinux Parity)
                display_cmd = sanitized_cmdline
                tooltip = sanitized_cmdline
                script_path = ""
                req_uri = ""
                is_php = ('php-fpm' in comm.lower() or 'php-fpm' in raw_cmdline.lower() or comm.lower().startswith('php'))

                if is_php:
                    # 1. Check ultra-low overhead shared-memory worker tracker in /dev/shm with strict security checks
                    shm_file = f'/dev/shm/uniselv_fpm/{pid}'
                    if os.path.exists(shm_file):
                        try:
                            # Hardening: refuse symlinks, verify regular file, enforce ownership & bounded size
                            st = os.lstat(shm_file)
                            if stat.S_ISREG(st.st_mode) and not os.path.islink(shm_file):
                                # Validate ownership: file must be owned by the target user or nobody (FPM pool user) or root
                                if st.st_uid == uid or st.st_uid == 65534 or st.st_uid == 0:
                                    if st.st_size <= 4096:
                                        with open(shm_file, 'r', encoding='utf-8', errors='replace') as sf:
                                            raw_content = sf.read(4096).strip()
                                            t_data = json.loads(raw_content)
                                            raw_script = t_data.get('script', '')
                                            raw_uri = t_data.get('uri', '')
                                            # Redact sensitive parameters
                                            clean_uri = re.sub(r'([?&](?:password|pass|pwd|token|secret|auth|nonce|key|session)=)[^&]*', r'\1[REDACTED]', raw_uri, flags=re.I)
                                            # Sanitize script path: must be a valid path string under home or web root
                                            if raw_script and ('/' in raw_script) and ('\0' not in raw_script):
                                                script_path = raw_script[:256]
                                                req_uri = clean_uri[:256]
                        except Exception:
                            pass

                    # 2. Fallback: inspect /proc/{pid}/fd/ for open *.php files under user's home
                    if not script_path and os.path.isdir(f'/proc/{pid}/fd'):
                        try:
                            for fd in os.listdir(f'/proc/{pid}/fd'):
                                try:
                                    target = os.readlink(f'/proc/{pid}/fd/{fd}')
                                    if target.endswith('.php') and ('/home/' in target or '/public_html/' in target):
                                        script_path = target
                                        break
                                except Exception:
                                    continue
                        except Exception:
                            pass

                    # 3. Format command line with exact cPanel CloudLinux conventions
                    if script_path:
                        display_cmd = f"php-fpm:{script_path}"
                        tooltip = f"php-fpm:{script_path}" + (f" ({req_uri})" if req_uri else "")
                    else:
                        # Idle PHP worker waiting for requests
                        display_cmd = "php-fpm"
                        tooltip = "php-fpm (idle worker)"

                procs.append({
                    'pid': pid,
                    'ppid': ppid,
                    'comm': comm,
                    'cmdline': display_cmd,
                    'tooltip': tooltip,
                    'script': script_path,
                    'uri': req_uri,
                    'is_php': is_php,
                    'start_time': start_time,
                    'rss_bytes': rss_bytes,
                    'mem_mb': rss_mb,
                    'mem_formatted': str(rss_mb),
                    'rss_formatted': f"{rss_mb} MB",
                    'cpu_percent': cpu_percent,
                    'cpu_formatted': f"{int(round(cpu_percent))}%"
                })
            except Exception:
                continue

        # Sort primarily by CPU % descending, then by RSS descending (cPanel parity)
        procs.sort(key=lambda x: (x['cpu_percent'], x['rss_bytes']), reverse=True)
        return procs[:50]

    def get_web_diagnostics(self, domain: str) -> List[Dict[str, Any]]:
        """Read recent requests from Apache access log for user's domain."""
        logs = []
        log_path = f'/usr/local/apps/apache2/logs/{domain}.log'
        if os.path.exists(log_path):
            try:
                # Tail last 25 lines
                cmd = ['tail', '-n', '25', log_path]
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                for line in res.stdout.splitlines():
                    if line.strip():
                        # Apache combined format: IP - - [date] "METHOD /path HTTP/1.1" status bytes "ref" "ua"
                        # Redact potential sensitive tokens in URL
                        sanitized_line = redact_command_line(line.strip())
                        logs.append({'raw': sanitized_line})
            except Exception:
                pass
        return logs

    def get_user_db_identities(self, username: str) -> List[str]:
        """Fetch exact verified database usernames owned by the Webuzo user from mysql.db metadata."""
        identities = set()
        if not username or not re.fullmatch(r'[a-z_][a-z0-9_-]{0,31}', username):
            return []

        # Always include the exact username itself as a candidate
        identities.add(username)

        # Query Webuzo's central database metadata table: /var/webuzo/db/mysql.db
        meta_db = '/var/webuzo/db/mysql.db'
        if os.path.exists(meta_db):
            try:
                conn = sqlite3.connect(meta_db, timeout=5)
                cur = conn.cursor()
                cur.execute("SELECT name FROM mysql WHERE owner = ? AND type = 'user'", (username,))
                for row in cur.fetchall():
                    if row[0]:
                        identities.add(row[0])
                conn.close()
            except Exception:
                pass
        return sorted(list(identities))

    def get_db_diagnostics(self, username: str) -> List[Dict[str, Any]]:
        """
        Query MariaDB processlist for queries matching EXACT verified user database identities.
        Fails closed if ownership cannot be verified.
        Diagnostic visibility only - does NOT substitute for database cgroup/quota enforcement.
        """
        queries = []
        user_ids = self.get_user_db_identities(username)
        if not user_ids:
            return queries

        # Build exact match clause with quoted identifiers
        # E.g. USER IN ('ub1', 'ub1_db1') - strictly prevents matching ub10 or other accounts
        escaped_users = "', '".join(u.replace("'", "''") for u in user_ids)
        sql_clause = f"USER IN ('{escaped_users}')"

        try:
            cmd = ['mysql', '-N', '-e', f"SELECT ID, USER, HOST, DB, COMMAND, TIME, STATE, INFO FROM information_schema.processlist WHERE {sql_clause} LIMIT 20;"]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if res.returncode == 0:
                for line in res.stdout.splitlines():
                    parts = line.split('\t')
                    if len(parts) >= 8:
                        raw_info = parts[7]
                        # Redact query literal values (strings and numbers)
                        sanitized_info = re.sub(r"'[^']*'", "'?'", raw_info)
                        sanitized_info = re.sub(r"\b\d+\b", "?", sanitized_info)
                        queries.append({
                            'id': parts[0],
                            'user': parts[1],
                            'host': parts[2],
                            'db': parts[3],
                            'command': parts[4],
                            'time_seconds': parts[5],
                            'state': parts[6],
                            'query': sanitized_info,
                            'enforcement_note': 'Observability diagnostic only; external to account cgroup'
                        })
        except Exception:
            pass
        return queries

    def capture_snapshot(self, uname: str, uid: int, domain: str, slice_path: str, trigger: str, metrics_summary: Dict[str, Any]):
        """Capture and record snapshot to SQLite."""
        procs = self.get_process_list_for_user(uid, slice_path)
        web_diag = self.get_web_diagnostics(domain)
        db_diag = self.get_db_diagnostics(uname)
        ts = int(time.time())

        conn = self.get_db_connection()
        try:
            conn.execute("""
                INSERT INTO snapshots (username, uid, timestamp, trigger_type, processes_json, web_diagnostics_json, db_diagnostics_json, metrics_summary_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (uname, uid, ts, trigger, json.dumps(procs), json.dumps(web_diag), json.dumps(db_diag), json.dumps(metrics_summary)))
            
            # Enforce sliding retention window per tenant: keep max 100 snapshots
            conn.execute("""
                DELETE FROM snapshots 
                WHERE username = ? AND id NOT IN (
                    SELECT id FROM snapshots WHERE username = ? ORDER BY timestamp DESC LIMIT 100
                )
            """, (uname, uname))
            conn.commit()
        finally:
            conn.close()

    def record_event(self, uname: str, uid: int, event_type: str, severity: str, message: str, details: Dict[str, Any]):
        """Record resource event to SQLite."""
        ts = int(time.time())
        conn = self.get_db_connection()
        try:
            conn.execute("""
                INSERT INTO events (username, uid, timestamp, event_type, severity, message, details_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (uname, uid, ts, event_type, severity, message, json.dumps(details)))
            conn.commit()
        finally:
            conn.close()

    def collect_step(self):
        """Execute one complete sampling step across all users and system."""
        if not self.settings.get('telemetry_enabled', True):
            return

        now_mono = time.monotonic()
        now_epoch = int(time.time())
        elapsed = now_mono - self.prev_time
        if elapsed <= 0.1:
            return

        users = self.get_webuzo_users()
        samples_to_insert = []

        now_snap = time.time()
        cooldown = self.settings.get('snapshot_cooldown_sec', 60)

        for uname, udata in users.items():
            uid = udata['uid']
            plan_name = udata['plan_name']
            domain = udata['domain']
            limits = self.get_plan_limits(plan_name)

            slice_path, curr = self.read_user_cgroup(uid)
            prev = self.prev_user_stats.get(uname)

            cpu_percent = 0.0
            cpu_allowance_percent = 0.0
            delta_throttled = 0
            delta_throttled_usec = 0
            delta_oom = 0
            delta_pids_max = 0
            read_bytes_sec = 0.0
            write_bytes_sec = 0.0
            read_iops_sec = 0.0
            write_iops_sec = 0.0

            if prev:
                # CPU delta
                delta_usec = max(0, curr['cpu_usage_usec'] - prev['cpu_usage_usec'])
                cpu_percent = round((delta_usec / (elapsed * 1_000_000)) * 100, 2)
                # Allowance percent
                assigned_quota = limits['cpuquota']
                if assigned_quota > 0:
                    cpu_allowance_percent = round((cpu_percent / assigned_quota) * 100, 2)

                # Throttling
                delta_throttled = max(0, curr['nr_throttled'] - prev['nr_throttled'])
                delta_throttled_usec = max(0, curr['throttled_usec'] - prev['throttled_usec'])

                # OOM
                delta_oom = max(0, curr['oom_kill'] - prev['oom_kill'])

                # PIDs max
                delta_pids_max = max(0, curr['task_limit_events'] - prev['task_limit_events'])

                # IO
                delta_rbytes = max(0, curr['io']['rbytes'] - prev['io']['rbytes'])
                delta_wbytes = max(0, curr['io']['wbytes'] - prev['io']['wbytes'])
                delta_rios = max(0, curr['io']['rios'] - prev['io']['rios'])
                delta_wios = max(0, curr['io']['wios'] - prev['io']['wios'])
                read_bytes_sec = round(delta_rbytes / elapsed, 2)
                write_bytes_sec = round(delta_wbytes / elapsed, 2)
                read_iops_sec = round(delta_rios / elapsed, 2)
                write_iops_sec = round(delta_wios / elapsed, 2)

            self.prev_user_stats[uname] = curr

            # Events trigger checks
            metrics_summary = {
                'cpu_percent': cpu_percent,
                'cpu_allowance_percent': cpu_allowance_percent,
                'mem_current_bytes': curr['mem_current'],
                'mem_limit_bytes': limits['mem_max'],
                'tasks_current': curr['tasks_current'],
                'tasks_limit': limits['maxtask']
            }

            last_snap = self.last_snapshot_time.get(uname, 0)
            can_snap = (now_snap - last_snap >= cooldown)

            if delta_throttled > 0:
                self.record_event(uname, uid, 'throttling', 'warning',
                    f"Account experienced CPU throttling ({delta_throttled} periods throttled, {round(delta_throttled_usec/1000, 1)} ms)",
                    {'throttled_periods': delta_throttled, 'throttled_ms': round(delta_throttled_usec/1000, 1)})
                if can_snap and self.settings.get('snapshot_on_throttle', True):
                    self.capture_snapshot(uname, uid, domain, slice_path, 'cpu_throttle', metrics_summary)
                    self.last_snapshot_time[uname] = now_snap

            if delta_oom > 0:
                self.record_event(uname, uid, 'oom_kill', 'critical',
                    f"Out Of Memory (OOM) killer terminated {delta_oom} process(es) in account cgroup",
                    {'oom_kills': delta_oom, 'mem_limit': limits['mem_max']})
                if can_snap and self.settings.get('snapshot_on_oom', True):
                    self.capture_snapshot(uname, uid, domain, slice_path, 'oom_kill', metrics_summary)
                    self.last_snapshot_time[uname] = now_snap

            if delta_pids_max > 0:
                self.record_event(uname, uid, 'task_limit', 'warning',
                    f"Task limit exceeded ({limits['maxtask']} tasks/threads max reached)",
                    {'task_limit': limits['maxtask'], 'events': delta_pids_max})
                if can_snap and self.settings.get('snapshot_on_task_limit', True):
                    self.capture_snapshot(uname, uid, domain, slice_path, 'task_limit', metrics_summary)
                    self.last_snapshot_time[uname] = now_snap

            # Periodic Hourly Snapshot (cPanel parity):
            # Capture hourly snapshot for active accounts to allow historical point-in-time forensic reviews
            last_hourly = self.last_hourly_snapshot_time.get(uname, 0)
            if (now_snap - last_hourly >= 3600):
                if curr['tasks_current'] > 0 or curr['mem_current'] > 1024 * 1024:
                    self.capture_snapshot(uname, uid, domain, slice_path, 'periodic_hourly', metrics_summary)
                    self.last_hourly_snapshot_time[uname] = now_snap

            # Sustained Pressure Detection & Notification Engine (U13):
            # Evaluates sliding window of 3 consecutive samples (15s) against configured thresholds
            cpu_thresh = self.settings.get('alert_threshold_cpu', 75)
            mem_thresh = self.settings.get('alert_threshold_mem', 80)
            mem_used_pct = (curr['mem_current'] / max(1, limits['mem_max'])) * 100
            is_pressured = (cpu_allowance_percent >= cpu_thresh) or (mem_used_pct >= mem_thresh)
            
            p_hist = self.pressure_history.setdefault(uname, [])
            p_hist.append(is_pressured)
            if len(p_hist) > 3:
                p_hist.pop(0)

            last_sustained = self.last_sustained_event_time.get(uname, 0)
            if len(p_hist) == 3 and all(p_hist) and (now_snap - last_sustained >= 300):
                self.record_event(uname, uid, 'sustained_pressure', 'warning',
                    f"Sustained resource pressure detected ({round(cpu_allowance_percent, 1)}% CPU allowance or {round(mem_used_pct, 1)}% RAM sustained >15s)",
                    {'cpu_allowance_pct': round(cpu_allowance_percent, 1), 'mem_used_pct': round(mem_used_pct, 1), 'threshold_cpu': cpu_thresh, 'threshold_mem': mem_thresh})
                self.last_sustained_event_time[uname] = now_snap

            rbps_num, _ = parse_bw_to_bytes(limits.get('read_bw', 0))
            wbps_num, _ = parse_bw_to_bytes(limits.get('write_bw', 0))
            riops_num = parse_iops(limits.get('diskread', 0))
            wiops_num = parse_iops(limits.get('diskwrite', 0))
            samples_to_insert.append((
                uname, uid, now_epoch, cpu_percent, cpu_allowance_percent,
                delta_throttled, delta_throttled_usec,
                curr['mem_current'], curr['mem_anon'], curr['mem_file'], curr['mem_swap'],
                delta_oom, curr['mem_high_events'], curr['mem_max_events'],
                curr['tasks_current'], delta_pids_max,
                read_bytes_sec, write_bytes_sec, read_iops_sec, write_iops_sec,
                plan_name, limits['cpuquota'], limits['mem_max'], limits['maxtask'],
                rbps_num, wbps_num, riops_num, wiops_num
            ))

        # System metrics
        sys_tot, sys_idle = self.read_system_cpu()
        sys_cpu_percent = 0.0
        if self.prev_sys_cpu:
            p_tot, p_idle = self.prev_sys_cpu
            d_tot = sys_tot - p_tot
            d_idle = sys_idle - p_idle
            if d_tot > 0:
                sys_cpu_percent = round(((d_tot - d_idle) / d_tot) * 100, 2)
        self.prev_sys_cpu = (sys_tot, sys_idle)

        meminfo = parse_key_value_file('/proc/meminfo')
        total_mem = int(meminfo.get('MemTotal:', '0').replace('kB', '')) * 1024
        avail_mem = int(meminfo.get('MemAvailable:', '0').replace('kB', '')) * 1024
        used_mem = max(0, total_mem - avail_mem)
        total_swap = int(meminfo.get('SwapTotal:', '0').replace('kB', '')) * 1024
        free_swap = int(meminfo.get('SwapFree:', '0').replace('kB', '')) * 1024
        used_swap = max(0, total_swap - free_swap)

        # Golden slice usage
        golden_mem = parse_int_file('/sys/fs/cgroup/golden.slice/memory.current')

        load1, load5, load15 = 0.0, 0.0, 0.0
        try:
            with open('/proc/loadavg') as f:
                lparts = f.read().split()
                load1, load5, load15 = float(lparts[0]), float(lparts[1]), float(lparts[2])
        except Exception:
            pass

        # Write samples in a single batch
        conn = self.get_db_connection()
        try:
            conn.executemany("""
                INSERT INTO samples (
                    username, uid, timestamp, cpu_percent, cpu_allowance_percent,
                    cpu_throttled_events, cpu_throttled_usec,
                    mem_current_bytes, mem_anon_bytes, mem_file_bytes, mem_swap_bytes,
                    oom_kill_events, mem_high_events, mem_max_events,
                    tasks_current, task_limit_events,
                    read_bytes_sec, write_bytes_sec, read_iops_sec, write_iops_sec,
                    plan_name, limit_cpu_quota, limit_mem_max_bytes, limit_tasks_max,
                    limit_io_read_bps, limit_io_write_bps, limit_io_read_iops, limit_io_write_iops
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, samples_to_insert)

            conn.execute("""
                INSERT OR REPLACE INTO system_metrics (
                    timestamp, cpu_percent, mem_used_bytes, mem_available_bytes, swap_used_bytes,
                    golden_slice_cpu_percent, golden_slice_mem_bytes, load1, load5, load15
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (now_epoch, sys_cpu_percent, used_mem, avail_mem, used_swap, 0.0, golden_mem, load1, load5, load15))
            conn.commit()
        finally:
            conn.close()

        self.prev_time = now_mono
        self.prev_epoch = now_epoch

    def get_retention_settings(self) -> Dict[str, Any]:
        """Read configured data retention days and storage quotas from settings table."""
        conn = self.get_db_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT key, value FROM settings WHERE key LIKE 'retention_%'")
            rows = dict(cur.fetchall())
            return {
                'samples_days': int(rows.get('retention_samples_days', 30)),
                'snapshots_days': int(rows.get('retention_snapshots_days', 14)),
                'events_days': int(rows.get('retention_events_days', 30)),
                'audit_days': int(rows.get('retention_audit_days', 90)),
                'max_storage_mib': int(rows.get('retention_max_storage_mib', 100))
            }
        except Exception:
            return {
                'samples_days': 30,
                'snapshots_days': 14,
                'events_days': 30,
                'audit_days': 90,
                'max_storage_mib': 100
            }
        finally:
            conn.close()

    def save_retention_settings(self, settings: Dict[str, Any]):
        """Persist data retention settings in SQLite."""
        conn = self.get_db_connection()
        try:
            cur = conn.cursor()
            for k, v in settings.items():
                cur.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (f'retention_{k}', str(v)))
            conn.commit()
        finally:
            conn.close()

    def prune_retention(self, samples_days: int = None, snapshots_days: int = None,
                        events_days: int = None, audit_days: int = None, vacuum: bool = False) -> Dict[str, Any]:
        """Purge stale telemetry, snapshots, and logs according to retention policy."""
        settings = self.get_retention_settings()
        s_days = samples_days if samples_days is not None else settings['samples_days']
        sn_days = snapshots_days if snapshots_days is not None else settings['snapshots_days']
        e_days = events_days if events_days is not None else settings['events_days']
        a_days = audit_days if audit_days is not None else settings['audit_days']

        now = int(time.time())
        cutoff_samples = now - (max(1, s_days) * 86400)
        cutoff_snapshots = now - (max(1, sn_days) * 86400)
        cutoff_events = now - (max(1, e_days) * 86400)
        cutoff_audit = now - (max(1, a_days) * 86400)

        before_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
        deleted_samples = 0
        deleted_snapshots = 0
        deleted_events = 0
        deleted_audit = 0

        conn = self.get_db_connection()
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM samples WHERE timestamp < ?", (cutoff_samples,))
            deleted_samples = cur.rowcount
            cur.execute("DELETE FROM snapshots WHERE timestamp < ?", (cutoff_snapshots,))
            deleted_snapshots = cur.rowcount
            cur.execute("DELETE FROM events WHERE timestamp < ?", (cutoff_events,))
            deleted_events = cur.rowcount
            cur.execute("DELETE FROM system_metrics WHERE timestamp < ?", (cutoff_samples,))
            cur.execute("DELETE FROM audit_log WHERE timestamp < ? AND actor != 'system'", (cutoff_audit,))
            deleted_audit = cur.rowcount
            conn.commit()

            cur.execute("PRAGMA wal_checkpoint(TRUNCATE)")
            if vacuum:
                conn.execute("VACUUM")
                conn.commit()
        except Exception:
            pass
        finally:
            conn.close()

        after_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
        freed_bytes = max(0, before_size - after_size)

        return {
            'deleted_samples': max(0, deleted_samples),
            'deleted_snapshots': max(0, deleted_snapshots),
            'deleted_events': max(0, deleted_events),
            'deleted_audit': max(0, deleted_audit),
            'before_bytes': before_size,
            'after_bytes': after_size,
            'freed_bytes': freed_bytes,
            'freed_formatted': format_bytes(freed_bytes),
            'current_size_formatted': format_bytes(after_size)
        }

    def _save_circuit_breaker_durable_state(self) -> bool:
        """Persist circuit breaker active state and throttled users map to SQLite settings."""
        db = getattr(self, 'db_path', None)
        if not db or not os.path.exists(os.path.dirname(db) or '.'):
            return True
        try:
            conn = self.get_db_connection()
            try:
                val_active = '1' if getattr(self, 'circuit_breaker_active', False) else '0'
                throttled = getattr(self, 'circuit_breaker_throttled_users', {})
                val_throttled = json.dumps({str(k): v for k, v in throttled.items()})
                conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('circuit_breaker_active', ?)", (val_active,))
                conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('circuit_breaker_throttled_users', ?)", (val_throttled,))
                conn.commit()
                return True
            finally:
                conn.close()
        except Exception as e:
            print(f"[Circuit Breaker DB Error] {e}", file=sys.stderr)
            return False

    def get_system_load(self) -> Optional[Tuple[float, float, float]]:
        """Returns 1m, 5m, 15m system load averages from os.getloadavg() or /proc/loadavg."""
        if hasattr(os, 'getloadavg'):
            try:
                return os.getloadavg()
            except Exception:
                pass
        if os.path.exists('/proc/loadavg'):
            try:
                with open('/proc/loadavg', 'r') as f:
                    parts = f.read().strip().split()
                    if len(parts) >= 3:
                        return float(parts[0]), float(parts[1]), float(parts[2])
            except Exception:
                pass
        return None

    def _load_circuit_breaker_durable_state(self):
        """Load durable circuit breaker state from SQLite settings upon daemon boot/collector init and reconcile journal entries."""
        db = getattr(self, 'db_path', None)
        if not db or not os.path.exists(db):
            return
        try:
            conn = self.get_db_connection()
            try:
                cur = conn.cursor()
                cur.execute("SELECT key, value FROM settings WHERE key IN ('circuit_breaker_active', 'circuit_breaker_throttled_users')")
                rows = dict(cur.fetchall())
                self.circuit_breaker_active = bool(int(rows.get('circuit_breaker_active', '0')))
                raw_throttled = rows.get('circuit_breaker_throttled_users', '{}')
                try:
                    loaded = json.loads(raw_throttled)
                    self.circuit_breaker_throttled_users = {int(k): int(v) for k, v in loaded.items()}
                except Exception:
                    self.circuit_breaker_throttled_users = {}

                # Reconcile incomplete crash entries: if active is True but throttled map is empty, reset active
                if self.circuit_breaker_active and not self.circuit_breaker_throttled_users:
                    self.circuit_breaker_active = False
                    conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('circuit_breaker_active', '0')")
                    conn.commit()
            finally:
                conn.close()
        except Exception:
            pass

    def check_runaway_watchdog(self):
        """Detect and monitor/terminate customer runaway processes exceeding abuse criteria."""
        if not self.settings.get('enable_runaway_watchdog', True):
            self.runaway_proc_tracker.clear()
            return

        # Policy configuration:
        # watchdog_action: 'notify' (default, safe non-destructive monitoring) vs 'terminate' (opt-in kill)
        watchdog_action = str(self.settings.get('watchdog_action', 'notify')).lower()
        # Admin kill toggle (defaults to False for safety)
        allow_kill = bool(int(self.settings.get('runaway_watchdog_kill_enabled', '0'))) or (watchdog_action == 'terminate')

        threshold_cpu = float(self.settings.get('runaway_cpu_percent', 80))
        max_duration = float(self.settings.get('runaway_max_duration_sec', 120))
        require_account_saturation = bool(int(self.settings.get('watchdog_require_account_saturation', '1')))
        now = time.time()

        # Legitimate workload exclusions
        default_exclusions = [
            'mysqldump', 'tar', 'gzip', 'bzip2', 'zip', 'unzip', 'rsync', 'backup',
            'composer', 'git', 'wp', 'ffmpeg', 'du', 'find'
        ]
        custom_exclusions = self.settings.get('watchdog_excluded_commands', '')
        if isinstance(custom_exclusions, str) and custom_exclusions:
            user_excl = [x.strip().lower() for x in custom_exclusions.split(',') if x.strip()]
        elif isinstance(custom_exclusions, list):
            user_excl = [str(x).strip().lower() for x in custom_exclusions]
        else:
            user_excl = []
        excluded_commands = set(default_exclusions + user_excl)

        users = self.get_webuzo_users()
        observed_keys = set()

        for uname, udata in users.items():
            uid = udata.get('uid', 0)
            if uid < 1000:
                continue
            slice_path, _ = self.read_user_cgroup(uid)
            procs = self.get_process_list_for_user(uid, slice_path)
            plan_name = udata.get('plan_name', 'default')
            plan_limits = self.get_plan_limits(plan_name)
            account_cpu_quota = float(plan_limits.get('cpuquota', 100))

            # Calculate total user CPU usage across all user processes
            total_user_cpu = sum(p.get('cpu_percent', 0.0) for p in procs)

            for p in procs:
                pid = p['pid']
                start_time = p['start_time']
                cpu = p['cpu_percent']
                comm = p.get('comm', '').lower()
                cmdline = p.get('cmdline', '').lower()
                key = (uid, pid)
                observed_keys.add(key)

                # Check workload exclusions
                is_excluded = any(excl in comm or excl in cmdline for excl in excluded_commands)
                if is_excluded:
                    if key in self.runaway_proc_tracker:
                        self.runaway_proc_tracker.pop(key, None)
                    continue

                # Abuse criteria:
                # 1. Process CPU >= runaway_cpu_percent
                # 2. If require_account_saturation is True:
                #    Account must be near or exceeding its purchased allowance (total_user_cpu >= 0.90 * account_cpu_quota)
                #    OR the process alone must exceed the account's purchased allowance (cpu > account_cpu_quota)
                is_abuse = (cpu >= threshold_cpu)
                if require_account_saturation and is_abuse:
                    # An Enterprise account with 280% CPU allowance running a 90% CPU job is NOT abusing quota
                    if (total_user_cpu < 0.90 * account_cpu_quota) and (cpu <= account_cpu_quota):
                        is_abuse = False

                if is_abuse:
                    if key not in self.runaway_proc_tracker or self.runaway_proc_tracker[key]['start_time'] != start_time:
                        self.runaway_proc_tracker[key] = {
                            'uid': uid,
                            'pid': pid,
                            'start_time': start_time,
                            'first_seen': now,
                            'last_seen': now,
                            'comm': p['comm'],
                            'cmdline': p['cmdline'],
                            'uname': uname,
                            'peak_cpu': cpu,
                            'warned': False
                        }
                    else:
                        tracker = self.runaway_proc_tracker[key]
                        tracker['last_seen'] = now
                        if cpu > tracker.get('peak_cpu', 0):
                            tracker['peak_cpu'] = cpu

                        duration = now - tracker['first_seen']
                        # Emit warning event if sustained for at least half grace period
                        if duration >= (max_duration / 2) and not tracker.get('warned'):
                            tracker['warned'] = True
                            self.record_event(
                                uname=uname,
                                uid=uid,
                                event_type='runaway_process_warning',
                                severity='info',
                                message=f"Process {p['comm']} (PID {pid}) sustaining high CPU ({tracker['peak_cpu']}%) for {int(duration)}s.",
                                details={
                                    'pid': pid,
                                    'comm': p['comm'],
                                    'cmdline': p['cmdline'],
                                    'peak_cpu': tracker['peak_cpu'],
                                    'duration_sec': round(duration, 1),
                                    'account_quota': account_cpu_quota,
                                    'action': 'warning_only'
                                }
                            )

                        if duration >= max_duration:
                            # Reached maximum allowed duration
                            if allow_kill:
                                # Admin explicitly opted in to termination
                                self._terminate_runaway_process(uname, uid, pid, start_time, tracker, threshold_cpu, duration)
                            else:
                                # Default safe monitoring: log notification without killing legitimate workload
                                self.record_event(
                                    uname=uname,
                                    uid=uid,
                                    event_type='runaway_process_detected',
                                    severity='warning',
                                    message=f"Runaway process detected: {p['comm']} (PID {pid}) sustained {tracker['peak_cpu']}% CPU for {int(duration)}s (non-destructive monitor mode).",
                                    details={
                                        'pid': pid,
                                        'comm': p['comm'],
                                        'cmdline': p['cmdline'],
                                        'peak_cpu': tracker['peak_cpu'],
                                        'duration_sec': round(duration, 1),
                                        'account_quota': account_cpu_quota,
                                        'action': 'monitored_no_kill'
                                    }
                                )
                            self.runaway_proc_tracker.pop(key, None)
                else:
                    if key in self.runaway_proc_tracker:
                        self.runaway_proc_tracker.pop(key, None)

        # Prune stale tracking entries
        stale_keys = [k for k in self.runaway_proc_tracker if k not in observed_keys and (now - self.runaway_proc_tracker[k].get('last_seen', 0) > 15)]
        for k in stale_keys:
            self.runaway_proc_tracker.pop(k, None)

        # Prune proc_prev_ticks to avoid unbounded memory growth
        stale_ticks = [k for k in self.proc_prev_ticks if k not in observed_keys and (now - self.proc_prev_ticks[k][1] > 60)]
        for k in stale_ticks:
            self.proc_prev_ticks.pop(k, None)

    def _terminate_runaway_process(self, uname: str, uid: int, pid: int, start_time: int, tracker: Dict[str, Any], threshold_cpu: float, duration: float):
        """Safely verify process identity via Linux pidfd and escalate SIGTERM -> SIGKILL.
        Fails closed without signalling if kernel lacks pidfd primitives to prevent PID recycling races.
        """
        has_pidfd = getattr(self, 'has_pidfd', hasattr(os, 'pidfd_open') and hasattr(signal, 'pidfd_send_signal'))
        if not has_pidfd:
            print(f"[Runaway Watchdog Safety Abort] Safe process termination requires Linux pidfd (kernel 5.3+). Process signalling aborted to prevent PID recycling races.", file=sys.stderr)
            return

        proc_stat_path = f'/proc/{pid}/stat'
        if not os.path.exists(proc_stat_path):
            return

        try:
            try:
                pidfd = os.pidfd_open(pid, 0)
            except (OSError, ProcessLookupError):
                return

            # Verify UID and start_time of the pinned process
            try:
                stat_st = os.stat(proc_stat_path)
                if stat_st.st_uid != uid:
                    print(f"[Runaway Watchdog Safety Abort] PID {pid} UID mismatch: expected {uid}, got {stat_st.st_uid}", file=sys.stderr)
                    os.close(pidfd)
                    return

                with open(proc_stat_path, 'r', errors='replace') as sf:
                    s_content = sf.read()
                    s_parts = s_content[s_content.rfind(')') + 2:].split()
                    cur_start_time = int(s_parts[19]) if len(s_parts) > 19 else 0
                    if cur_start_time != start_time:
                        print(f"[Runaway Watchdog Safety Abort] PID {pid} start_time mismatch: expected {start_time}, got {cur_start_time}", file=sys.stderr)
                        os.close(pidfd)
                        return
            except (OSError, FileNotFoundError):
                os.close(pidfd)
                return

            # Send SIGTERM through pinned pidfd
            kill_action = 'SIGTERM'
            try:
                signal.pidfd_send_signal(pidfd, signal.SIGTERM)
            except (ProcessLookupError, OSError):
                os.close(pidfd)
                return

            # Grace period for clean termination
            time.sleep(0.2)

            # Check if alive and escalate to SIGKILL
            try:
                signal.pidfd_send_signal(pidfd, 0)
                signal.pidfd_send_signal(pidfd, signal.SIGKILL)
                kill_action = 'SIGTERM -> SIGKILL'
            except (ProcessLookupError, OSError):
                kill_action = 'SIGTERM'
            finally:
                try:
                    os.close(pidfd)
                except Exception:
                    pass

            peak_cpu = tracker.get('peak_cpu', threshold_cpu)
            comm = tracker.get('comm', 'unknown')
            cmdline = tracker.get('cmdline', '')

            # Record to events table
            self.record_event(
                uname=uname,
                uid=uid,
                event_type='runaway_process_terminated',
                severity='warning',
                message=f"Terminated runaway process {comm} (PID {pid}) sustaining {peak_cpu}% CPU for {int(duration)}s.",
                details={
                    'pid': pid,
                    'comm': comm,
                    'cmdline': cmdline,
                    'peak_cpu': peak_cpu,
                    'duration_sec': round(duration, 1),
                    'action': kill_action
                }
            )

            # Record to audit_log
            conn = self.get_db_connection()
            try:
                conn.execute("""
                    INSERT INTO audit_log (timestamp, actor, action, target_account, details_json)
                    VALUES (?, 'watchdog', 'terminate_runaway_process', ?, ?)
                """, (int(time.time()), uname, json.dumps({
                    'pid': pid,
                    'comm': comm,
                    'cmdline': cmdline,
                    'peak_cpu': peak_cpu,
                    'duration_sec': round(duration, 1),
                    'action': kill_action
                })))
                conn.commit()
            finally:
                conn.close()

            print(f"[Runaway Watchdog] Successfully terminated PID {pid} ({comm}) for account '{uname}' ({duration:.1f}s at {peak_cpu}%)", file=sys.stderr)

        except Exception as e:
            if pidfd is not None:
                try: os.close(pidfd)
                except Exception: pass
            print(f"[Runaway Watchdog Error] Failed to terminate PID {pid}: {e}", file=sys.stderr)

    def _is_effective_quota_throttled(self, uid: int, orig_quota: int, throttled_quota: int) -> Optional[bool]:
        """
        Check effective kernel cgroup cpu.max for golden-{uid}.slice to resolve command outcome uncertainty.
        Returns:
            True if effective quota matches throttled_quota (quota was definitely applied).
            False if effective quota matches orig_quota (quota was definitely NOT applied).
            None if cgroup is absent, unreadable, or ambiguous (uncertain outcome -> retain journal).
        """
        cg_cpu_max = f'/sys/fs/cgroup/golden.slice/golden-{uid}.slice/cpu.max'
        if not os.path.exists(cg_cpu_max):
            return None
        try:
            with open(cg_cpu_max, 'r') as f:
                c_val = f.read().strip()
            parts = c_val.split()
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit() and int(parts[1]) > 0:
                eff_pct = round((int(parts[0]) / int(parts[1])) * 100, 1)
                if abs(eff_pct - float(throttled_quota)) <= 1.0:
                    return True
                if abs(eff_pct - float(orig_quota)) <= 1.0:
                    return False
        except Exception:
            return None
        return None

    def _aggregate_cpu_headroom_enforced(self):
        """Runnable/throttled PHP increases load average even under a healthy parent quota."""
        try:
            quota,period=pathlib.Path('/sys/fs/cgroup/golden.slice/cpu.max').read_text().split()
            cpus=int(self.host_cpu_count)
            return cpus>0 and quota.isdigit() and int(period)>0 and 0<int(quota)/int(period)<=cpus*.85+1e-6
        except (OSError,ValueError,TypeError):
            return False

    def check_overload_circuit_breaker(self):
        """Retain parent protection; do not halve plan quotas for load generated by quota waiting."""
        enabled = self.settings.get('enable_circuit_breaker', True)
        if not enabled:
            if self.circuit_breaker_active:
                self._restore_circuit_breaker_quotas()
            return

        threshold = float(self.settings.get('circuit_breaker_load_threshold', 3.2))
        recovery_threshold = float(self.settings.get('circuit_breaker_recovery_threshold', 2.2))

        load_tuple = self.get_system_load()
        if not load_tuple:
            return
        load1, _, _ = load_tuple

        now = time.time()
        if self._aggregate_cpu_headroom_enforced():
            # The aggregate kernel quota already preserves the shared 15% CPU headroom.
            # A second 50% cut creates a feedback loop: more throttling raises runnable load.
            if self.circuit_breaker_active:
                self._restore_circuit_breaker_quotas()
            if load1>=threshold and now-getattr(self,'_last_bounded_load_event',0)>=60:
                self._last_bounded_load_event=now
                self.record_event(uname='system',uid=0,event_type='bounded_hosting_load',severity='info',
                    message='High runnable load observed inside the protected aggregate CPU budget; native plan quotas retained.',
                    details={'load1':round(load1,2),'threshold':threshold,'aggregateHeadroomEnforced':True})
            return
        users = self.get_webuzo_users()

        # Dynamic Coverage during Active Incident:
        # If already active, check if new accounts or plan changes occurred that need throttling
        if self.circuit_breaker_active:
            for uname, udata in users.items():
                uid = udata.get('uid', 0)
                if uid < 1000:
                    continue
                if uid not in self.circuit_breaker_throttled_users:
                    plan_name = udata.get('plan_name', 'default')
                    limits = self.get_plan_limits(plan_name)
                    orig_quota = limits.get('cpuquota', 100)
                    if orig_quota <= 0:
                        orig_quota = 100
                    throttled_quota = max(20, int(orig_quota * 0.5))

                    # CRITICAL (P2): Durably journal intended mutation BEFORE applying slice change
                    self.circuit_breaker_throttled_users[uid] = orig_quota
                    if not self._save_circuit_breaker_durable_state():
                        print(f"[Circuit Breaker Error] Refusing to throttle new UID {uid}: durable state save failed.", file=sys.stderr)
                        del self.circuit_breaker_throttled_users[uid]
                        continue

                    res = None
                    try:
                        cmd = ['systemctl', 'set-property', '--runtime', f'golden-{uid}.slice', f'CPUQuota={throttled_quota}%']
                        res = subprocess.run(cmd, capture_output=True, timeout=5)
                    except Exception as cmd_err:
                        print(f"[Circuit Breaker Command Exception] New UID {uid}: {cmd_err}", file=sys.stderr)

                    if res is not None and res.returncode == 0:
                        pass
                    else:
                        eff_throttled = self._is_effective_quota_throttled(uid, orig_quota, throttled_quota)
                        if eff_throttled is False:
                            del self.circuit_breaker_throttled_users[uid]
                            self._save_circuit_breaker_durable_state()
                        else:
                            print(f"[Circuit Breaker Retention] UID {uid} command outcome uncertain; journal retained for recovery.", file=sys.stderr)

        # Trip Condition
        if not self.circuit_breaker_active:
            if load1 >= threshold:
                self.circuit_breaker_active = True
                self.circuit_breaker_tripped_at = now
                self.circuit_breaker_throttled_users = {}

                # Persist active trip intent before applying slice mutations
                if not self._save_circuit_breaker_durable_state():
                    print("[Circuit Breaker Error] Refusing to throttle slices: durable state save failed.", file=sys.stderr)
                    self.circuit_breaker_active = False
                    return

                throttled_summary = []
                for uname, udata in users.items():
                    uid = udata.get('uid', 0)
                    if uid < 1000:
                        continue
                    slice_name = f'golden-{uid}.slice'
                    plan_name = udata.get('plan_name', 'default')
                    limits = self.get_plan_limits(plan_name)
                    orig_quota = limits.get('cpuquota', 100)
                    if orig_quota <= 0:
                        orig_quota = 100

                    throttled_quota = max(20, int(orig_quota * 0.5))

                    # CRITICAL (P2): Durably journal intended mutation BEFORE applying slice change
                    self.circuit_breaker_throttled_users[uid] = orig_quota
                    if not self._save_circuit_breaker_durable_state():
                        print(f"[Circuit Breaker Error] Refusing to throttle UID {uid}: durable state save failed.", file=sys.stderr)
                        del self.circuit_breaker_throttled_users[uid]
                        # Fail-closed: Stop iterating further mutations on persistence failure
                        break

                    res = None
                    try:
                        cmd = ['systemctl', 'set-property', '--runtime', slice_name, f'CPUQuota={throttled_quota}%']
                        res = subprocess.run(cmd, capture_output=True, timeout=5)
                    except Exception as cmd_err:
                        print(f"[Circuit Breaker Command Exception] UID {uid}: {cmd_err}", file=sys.stderr)

                    if res is not None and res.returncode == 0:
                        throttled_summary.append(f"{uname}(UID {uid}): {orig_quota}% -> {throttled_quota}%")
                    else:
                        eff_throttled = self._is_effective_quota_throttled(uid, orig_quota, throttled_quota)
                        if eff_throttled is False:
                            print(f"[Circuit Breaker Rollback] UID {uid} verified untouched: reverting journal entry.", file=sys.stderr)
                            del self.circuit_breaker_throttled_users[uid]
                            self._save_circuit_breaker_durable_state()
                        else:
                            print(f"[Circuit Breaker Retention] UID {uid} command outcome uncertain; journal retained for recovery.", file=sys.stderr)
                            throttled_summary.append(f"{uname}(UID {uid}): uncertain outcome (journal retained for recovery)")

                if not self.circuit_breaker_throttled_users:
                    # No tenants were throttled (e.g. persistence failed on all or no eligible tenants)
                    self.circuit_breaker_active = False
                    self._save_circuit_breaker_durable_state()
                    return

                # Record event and audit_log
                self.record_event(
                    uname='system',
                    uid=0,
                    event_type='circuit_breaker_tripped',
                    severity='warning',
                    message=f"System load {load1:.2f} reached threshold {threshold}. Overload circuit breaker engaged; tenant CPU quotas throttled by 50%.",
                    details={
                        'load1': round(load1, 2),
                        'threshold': threshold,
                        'throttled_accounts': throttled_summary
                    }
                )
                conn = self.get_db_connection()
                try:
                    conn.execute("""
                        INSERT INTO audit_log (timestamp, actor, action, target_account, details_json)
                        VALUES (?, 'circuit_breaker', 'circuit_breaker_tripped', 'system', ?)
                    """, (int(now), json.dumps({
                        'load1': round(load1, 2),
                        'threshold': threshold,
                        'throttled_count': len(self.circuit_breaker_throttled_users)
                    })))
                    conn.commit()
                finally:
                    conn.close()

                print(f"[Circuit Breaker Tripped] System load {load1:.2f} >= {threshold}. Throttled {len(throttled_summary)} tenant slices.", file=sys.stderr)

        # Recovery Condition
        elif self.circuit_breaker_active:
            tripped_at = getattr(self, 'circuit_breaker_tripped_at', None) or 0.0
            hold_down = getattr(self, 'circuit_breaker_min_hold_down_sec', 30.0)
            if (now - tripped_at) < hold_down:
                return

            if load1 <= recovery_threshold:
                restore_res = self._restore_circuit_breaker_quotas()
                if not self.circuit_breaker_throttled_users:
                    duration = round(now - self.circuit_breaker_tripped_at, 1) if self.circuit_breaker_tripped_at else 0.0

                    self.record_event(
                        uname='system',
                        uid=0,
                        event_type='circuit_breaker_recovered',
                        severity='info',
                        message=f"System load {load1:.2f} stabilized below recovery threshold {recovery_threshold}. Tenant CPU quotas restored to normal.",
                        details={
                            'load1': round(load1, 2),
                            'recovery_threshold': recovery_threshold,
                            'duration_sec': duration,
                            'restored_accounts_count': len(restore_res.get('restored', []))
                        }
                    )
                    conn = self.get_db_connection()
                    try:
                        conn.execute("""
                            INSERT INTO audit_log (timestamp, actor, action, target_account, details_json)
                            VALUES (?, 'circuit_breaker', 'circuit_breaker_recovered', 'system', ?)
                        """, (int(now), json.dumps({
                            'load1': round(load1, 2),
                            'recovery_threshold': recovery_threshold,
                            'duration_sec': duration
                        })))
                        conn.commit()
                    finally:
                        conn.close()

                    print(f"[Circuit Breaker Recovered] System load {load1:.2f} <= {recovery_threshold}. Restored original quotas.", file=sys.stderr)

    def _restore_circuit_breaker_quotas(self) -> Dict[str, Any]:
        """Restore native plan CPUQuota on tenant slices with verified command exit codes, cgroup limits, and boost composition."""
        restored = []
        failed = []

        # Find any active temporary boosts to avoid restoring stale quotas
        active_overrides = {}
        db = getattr(self, 'db_path', None)
        if db and os.path.exists(db):
            try:
                conn = self.get_db_connection()
                cur = conn.cursor()
                cur.execute("SELECT uid, override_plan FROM temporary_overrides WHERE status = 'active' AND expires_at > ?", (int(time.time()),))
                for r in cur.fetchall():
                    active_overrides[int(r['uid'])] = r['override_plan']
                conn.close()
            except Exception:
                pass

        users = getattr(self, 'get_webuzo_users', lambda: {})()
        user_by_uid = {udata['uid']: (uname, udata) for uname, udata in users.items()} if users else {}

        for uid in list(self.circuit_breaker_throttled_users.keys()):
            orig_quota = self.circuit_breaker_throttled_users[uid]
            slice_name = f'golden-{uid}.slice'

            target_quota = orig_quota
            if uid in user_by_uid:
                uname, udata = user_by_uid[uid]
                cur_plan = active_overrides.get(uid, udata.get('plan_name', 'default'))
                cur_limits = self.get_plan_limits(cur_plan)
                target_quota = cur_limits.get('cpuquota', orig_quota)
                if target_quota <= 0:
                    target_quota = 100

            try:
                cmd = ['systemctl', 'set-property', '--runtime', slice_name, f'CPUQuota={target_quota}%']
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                if res.returncode != 0:
                    failed.append(uid)
                    print(f"[Circuit Breaker Restore Fail] UID {uid} systemctl exit {res.returncode}: {res.stderr or res.stdout}", file=sys.stderr)
                    continue

                # Mandatory readable, well-formed finite desired-versus-effective quota verification
                cg_cpu_max = f'/sys/fs/cgroup/golden.slice/golden-{uid}.slice/cpu.max'
                if not os.path.exists(cg_cpu_max):
                    # Explicit safe handling for deleted accounts:
                    # If user inventory is available and account is truly absent, clean up safely
                    if users and uid not in user_by_uid:
                        self.circuit_breaker_throttled_users.pop(uid, None)
                        restored.append(uid)
                        continue
                    failed.append(uid)
                    print(f"[Circuit Breaker Restore Fail] UID {uid} effective cgroup file absent: {cg_cpu_max}", file=sys.stderr)
                    continue

                try:
                    with open(cg_cpu_max, 'r') as f:
                        c_val = f.read().strip()
                except Exception as read_err:
                    failed.append(uid)
                    print(f"[Circuit Breaker Restore Fail] UID {uid} unreadable {cg_cpu_max}: {read_err}", file=sys.stderr)
                    continue

                if ' ' not in c_val:
                    failed.append(uid)
                    print(f"[Circuit Breaker Restore Fail] UID {uid} malformed cpu.max format: '{c_val}'", file=sys.stderr)
                    continue

                parts = c_val.split()
                if len(parts) != 2:
                    failed.append(uid)
                    print(f"[Circuit Breaker Restore Fail] UID {uid} invalid cpu.max parts: '{c_val}'", file=sys.stderr)
                    continue

                q_us, p_us = parts
                if q_us == 'max' or not q_us.isdigit() or not p_us.isdigit() or int(p_us) <= 0:
                    failed.append(uid)
                    print(f"[Circuit Breaker Restore Fail] UID {uid} unlimited or non-numeric cpu.max: '{c_val}'", file=sys.stderr)
                    continue

                eff_pct = round((int(q_us) / int(p_us)) * 100, 1)
                if abs(eff_pct - float(target_quota)) > 1.0:
                    failed.append(uid)
                    print(f"[Circuit Breaker Restore Fail] UID {uid} effective CPU quota {eff_pct}% != expected {target_quota}%", file=sys.stderr)
                    continue

                # Command and verification passed! Safe to remove from recovery map
                self.circuit_breaker_throttled_users.pop(uid, None)
                restored.append(uid)

            except Exception as e:
                failed.append(uid)
                print(f"[Circuit Breaker Restore Error] UID {uid}: {e}", file=sys.stderr)

        # Update durable state in SQLite
        if not self.circuit_breaker_throttled_users:
            self.circuit_breaker_active = False
        self._save_circuit_breaker_durable_state()

        return {'restored': restored, 'failed': failed, 'remaining': len(self.circuit_breaker_throttled_users)}

