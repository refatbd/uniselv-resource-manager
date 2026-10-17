import os
import sys
import json
import time
import pathlib
import hashlib
import subprocess
import re
import shutil
from typing import Dict, Any, Optional, Tuple, List

BASE = pathlib.Path('/etc/golden-shield')
STATE = pathlib.Path('/var/lib/golden-shield')
RUN = pathlib.Path('/run/golden-shield')
UNITS = pathlib.Path('/etc/systemd/system')
BACKUPS_DIR = pathlib.Path('/var/lib/uniselv-resource-manager/golden-backups')
MANIFEST_FILE = pathlib.Path('/var/lib/uniselv-resource-manager/ownership_manifest.json')
CORE_DIR = pathlib.Path(__file__).resolve().parent.parent / 'core'

class GoldenShieldManager:
    def __init__(self, db_conn_factory=None):
        self.db_conn_factory = db_conn_factory
        BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
        BASE.mkdir(parents=True, exist_ok=True)
        self.ensure_core_scripts_installed()
        self.ensure_systemd_slice_persistence()

    def ensure_systemd_slice_persistence(self):
        """Ensure systemd drop-in override /etc/systemd/system/golden.slice.d/50-uniselv-limits.conf is initialized."""
        dropin_file = UNITS / 'golden.slice.d' / '50-uniselv-limits.conf'
        if not dropin_file.exists():
            policy = self.get_configured_policy()
            if not policy:
                hw = self.detect_hardware()
                policy = self.calculate_auto_policy(hw)
            if policy and 'customerCpuPercent' in policy and 'hostingMemoryMaxMiB' in policy:
                self.persist_systemd_slice_limits(policy['customerCpuPercent'], policy['hostingMemoryMaxMiB'])

    def ensure_core_scripts_installed(self) -> Dict[str, Any]:
        """
        Verify that required protection scripts are installed.
        If missing on a clean server, installs them from the bundled core package
        and records ownership metadata in ownership_manifest.json.
        """
        manifest = {}
        if MANIFEST_FILE.exists():
            try:
                manifest = json.loads(MANIFEST_FILE.read_text(encoding='utf-8'))
            except Exception:
                manifest = {}

        core_scripts = {
            'golden-shield.py': pathlib.Path('/usr/local/sbin/golden-shield.py'),
            'webuzo-isolation.py': pathlib.Path('/usr/local/sbin/webuzo-isolation.py'),
            'webuzo-session-guard.py': pathlib.Path('/usr/local/sbin/webuzo-session-guard.py'),
            'webuzo-session-guard-manager.py': pathlib.Path('/usr/local/sbin/webuzo-session-guard-manager.py')
        }

        updated = False
        for fname, dest_path in core_scripts.items():
            if not dest_path.exists():
                src_bundled = CORE_DIR / fname
                if not src_bundled.exists():
                    # Check alternate bundled location inside plugin
                    src_bundled = pathlib.Path('/usr/local/webuzo/plugins/uniselv-resman/core') / fname

                if src_bundled.exists():
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src_bundled, dest_path)
                    dest_path.chmod(0o750)
                    manifest[fname] = {
                        'ownership': 'plugin_installed',
                        'installed_at': int(time.time()),
                        'sha256': hashlib.sha256(dest_path.read_bytes()).hexdigest()
                    }
                    updated = True
            else:
                if fname not in manifest:
                    manifest[fname] = {
                        'ownership': 'adopted_external',
                        'adopted_at': int(time.time()),
                        'sha256': hashlib.sha256(dest_path.read_bytes()).hexdigest()
                    }
                    updated = True

        if updated:
            MANIFEST_FILE.parent.mkdir(parents=True, exist_ok=True)
            MANIFEST_FILE.write_text(json.dumps(manifest, indent=2), encoding='utf-8')

        return manifest

    def detect_hardware(self) -> Dict[str, Any]:
        """
        Detect visible physical CPU and RAM capacity truthfully.
        Does not use fabricated fallbacks; fails closed with descriptive exception.
        """
        cpu_count = os.cpu_count()
        if not cpu_count or cpu_count < 1:
            raise RuntimeError("Hardware Detection Failure: Unable to determine host CPU core count from kernel")

        mem_total_kib = 0
        swap_total_kib = 0
        try:
            with open('/proc/meminfo', 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith('MemTotal:'):
                        mem_total_kib = int(line.split()[1])
                    elif line.startswith('SwapTotal:'):
                        swap_total_kib = int(line.split()[1])
        except Exception as e:
            raise RuntimeError(f"Hardware Detection Failure: Unable to read /proc/meminfo: {e}")

        if mem_total_kib <= 0:
            raise RuntimeError("Hardware Detection Failure: /proc/meminfo reported invalid zero memory")

        ram_total_mib = mem_total_kib // 1024
        swap_total_mib = swap_total_kib // 1024

        # Read CPU model name if available
        cpu_model = "Generic"
        try:
            with open('/proc/cpuinfo', 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith('model name'):
                        cpu_model = line.split(':', 1)[1].strip()
                        break
        except Exception:
            pass

        fp_raw = f"{cpu_count}:{ram_total_mib}:{swap_total_mib}:{cpu_model}"
        fp = hashlib.sha256(fp_raw.encode()).hexdigest()

        return {
            'cpu_count': cpu_count,
            'ram_total_mib': ram_total_mib,
            'swap_total_mib': swap_total_mib,
            'cpu_model': cpu_model,
            'fingerprint': fp
        }

    def calculate_auto_policy(self, hw: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Calculate hardware-scaled resource policy based on exact visible hardware:
        - Rejects unsupported hardware configurations (< 1024 MiB RAM).
        - CPU: 85% hosting aggregate, 15% system/admin headroom across all cores.
        - RAM: Computes safe system headroom and ensures hostingMemoryMaxMiB + headroom <= ram_total_mib.
        """
        if not hw:
            hw = self.detect_hardware()

        cpu_count = hw['cpu_count']
        ram_mib = hw['ram_total_mib']

        if ram_mib < 1024:
            raise ValueError(f"Unsupported Hardware: UNISELV Resource Manager requires >= 1024 MiB RAM (detected {ram_mib} MiB)")

        # Scale CPU: 85% hosting aggregate, 15% reserved headroom across all cores
        customer_cpu_pct = int(round(cpu_count * 85))
        reserved_cpu_pct = (cpu_count * 100) - customer_cpu_pct

        # Dynamic RAM headroom calculation
        if ram_mib <= 2048:
            headroom_mib = 512
        elif ram_mib <= 4096:
            headroom_mib = 768
        elif ram_mib <= 8192:
            headroom_mib = 1280
        else:
            headroom_mib = max(1536, int(ram_mib * 0.15))

        # Hosting memory cap strictly bounded by physical visible RAM
        hosting_memory_max_mib = max(512, ram_mib - headroom_mib)

        # Sanity assertion: hosting memory + headroom must not exceed physical RAM
        if hosting_memory_max_mib + headroom_mib > ram_mib:
            headroom_mib = max(384, ram_mib - hosting_memory_max_mib)

        panel_low_mib = min(768, max(256, int(headroom_mib * 0.5)))
        ssh_low_mib = 128
        recovery_margin_mib = 512
        recovery_seconds = 30
        guard_mem_low_mib = 64
        guard_mem_max_mib = 192

        return {
            'mode': 'shared-aggregate-cpu',
            'hostCpuCount': cpu_count,
            'customerCpuPercent': customer_cpu_pct,
            'reservedCpuPercent': reserved_cpu_pct,
            'hostingMemoryMaxMiB': hosting_memory_max_mib,
            'headroomMiB': headroom_mib,
            'panelLowMiB': panel_low_mib,
            'sshLowMiB': ssh_low_mib,
            'recoveryMarginMiB': recovery_margin_mib,
            'recoverySeconds': recovery_seconds,
            'guardMemoryLowMiB': guard_mem_low_mib,
            'guardMemoryMaxMiB': guard_mem_max_mib
        }

    def get_persisted_mode(self) -> str:
        """Read explicitly persisted governance mode ('AUTO' or 'MANUAL')."""
        mode_file = BASE / 'mode.json'
        if mode_file.exists():
            try:
                data = json.loads(mode_file.read_text(encoding='utf-8'))
                mode = data.get('mode', 'AUTO').upper()
                if mode in ['AUTO', 'MANUAL']:
                    return mode
            except Exception:
                pass
        return 'AUTO'

    def set_persisted_mode(self, mode: str):
        """Persist governance mode to /etc/golden-shield/mode.json and SQLite settings."""
        mode_str = mode.upper()
        if mode_str not in ['AUTO', 'MANUAL']:
            mode_str = 'AUTO'

        BASE.mkdir(parents=True, exist_ok=True)
        (BASE / 'mode.json').write_text(json.dumps({'mode': mode_str, 'updated_at': int(time.time())}, indent=2), encoding='utf-8')

        if self.db_conn_factory:
            try:
                conn = self.db_conn_factory()
                conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('golden_governance_mode', ?)", (mode_str,))
                conn.commit()
                conn.close()
            except Exception:
                pass

    def get_configured_policy(self) -> Optional[Dict[str, Any]]:
        policy_file = BASE / 'policy.json'
        if policy_file.exists():
            try:
                return json.loads(policy_file.read_text(encoding='utf-8'))
            except Exception:
                pass
        return None

    def get_effective_values(self) -> Dict[str, Any]:
        """Read actual active kernel cgroups v2 values."""
        res = {
            'aggregate_cpu_max': 'max',
            'aggregate_mem_max': 'max',
            'aggregate_swap_max': 'max',
            'services': {},
            'accounts': {}
        }
        root = pathlib.Path('/sys/fs/cgroup/golden.slice')
        if root.exists():
            if (root / 'cpu.max').exists():
                res['aggregate_cpu_max'] = (root / 'cpu.max').read_text().strip()
            if (root / 'memory.max').exists():
                res['aggregate_mem_max'] = (root / 'memory.max').read_text().strip()
            if (root / 'memory.swap.max').exists():
                res['aggregate_swap_max'] = (root / 'memory.swap.max').read_text().strip()

        for s in ['golden-shield.service', 'webuzo.service', 'golden-apache.service', 'mariadb.service']:
            try:
                out = subprocess.run(['systemctl', 'show', s, '-p', 'ActiveState', '-p', 'ControlGroup'], capture_output=True, text=True, timeout=5)
                props = dict(line.split('=', 1) for line in out.stdout.splitlines() if '=' in line)
                res['services'][s] = {
                    'active': props.get('ActiveState', 'inactive'),
                    'cgroup': props.get('ControlGroup', '')
                }
            except Exception:
                res['services'][s] = {'active': 'unknown', 'cgroup': ''}

        return res

    def get_status(self) -> Dict[str, Any]:
        """Return comprehensive status for Admin panel with truthful labeling."""
        hw = self.detect_hardware()
        calc_policy = self.calculate_auto_policy(hw)
        cfg_policy = self.get_configured_policy()
        eff = self.get_effective_values()
        mode = self.get_persisted_mode()

        if not pathlib.Path('/sys/fs/cgroup/cgroup.controllers').exists():
            state = 'Unsupported'
            message = 'Linux cgroups v2 controller hierarchy is not available.'
        elif not (STATE / 'installed.json').exists():
            state = 'Not installed'
            message = 'Golden Shield protection is not installed on this system.'
        else:
            is_active = (eff['services'].get('golden-shield.service', {}).get('active') == 'active' and
                         eff['services'].get('golden-apache.service', {}).get('active') == 'active' and
                         eff['services'].get('mariadb.service', {}).get('active') == 'active')
            if is_active and eff['aggregate_cpu_max'] != 'max' and eff['aggregate_swap_max'] == '0':
                outside = self.check_escaped_processes()
                if len(outside) > 0:
                    state = 'Degraded'
                    message = f"Active with {len(outside)} uncontained processes running outside golden.slice."
                else:
                    state = 'Active'
                    message = 'Golden Shield aggregate CPU & memory protection is actively enforcing.'
            else:
                state = 'Degraded'
                message = 'Service units or cgroup limits are incomplete or failing.'

        return {
            'state': state,
            'message': message,
            'mode': mode,
            'hardware': hw,
            'calculated_policy': calc_policy,
            'configured_policy': cfg_policy,
            'effective_values': eff,
            'outside_processes': self.check_escaped_processes() if state in ['Active', 'Degraded'] else []
        }

    def check_escaped_processes(self) -> List[Dict[str, Any]]:
        """Identify web hosting workers executing outside golden.slice."""
        outside = []
        for d in pathlib.Path('/proc').iterdir():
            if not d.name.isdigit():
                continue
            try:
                exe = os.readlink(d / 'exe')
                cg = (d / 'cgroup').read_text().strip()
                if exe == '/usr/local/apps/apache2/bin/httpd' or exe.startswith('/usr/local/apps/mariadb'):
                    if not cg.startswith('0::/golden.slice/'):
                        outside.append({'pid': int(d.name), 'exe': exe, 'cgroup': cg})
                elif re.fullmatch(r'/usr/local/apps/php\d+/sbin/php-fpm', exe):
                    if 'wpiso-health-' not in cg and not cg.startswith('0::/golden.slice/'):
                        outside.append({'pid': int(d.name), 'exe': exe, 'cgroup': cg})
            except (FileNotFoundError, ProcessLookupError, PermissionError):
                pass
        return outside

    def backup_current_config(self) -> str:
        """Create a timestamped backup before modifying policy."""
        ts = int(time.time())
        bfile = BACKUPS_DIR / f"golden-shield-backup-{ts}.json"
        data = {
            'backup_id': str(ts),
            'timestamp': ts,
            'mode': self.get_persisted_mode(),
            'policy': self.get_configured_policy(),
            'installed_meta': json.loads((STATE / 'installed.json').read_text()) if (STATE / 'installed.json').exists() else None,
            'effective': self.get_effective_values()
        }
        bfile.write_text(json.dumps(data, indent=2), encoding='utf-8')
        return str(ts)

    def list_backups(self) -> List[Dict[str, Any]]:
        """List all verified backups in BACKUPS_DIR."""
        backups = []
        for f in sorted(BACKUPS_DIR.glob('golden-shield-backup-*.json'), reverse=True):
            try:
                data = json.loads(f.read_text(encoding='utf-8'))
                b_id = data.get('backup_id', f.stem.replace('golden-shield-backup-', ''))
                ts = data.get('timestamp', int(f.stat().st_mtime))
                backups.append({
                    'id': b_id,
                    'backup_id': b_id,
                    'timestamp': ts,
                    'created_at': ts,
                    'mode': data.get('mode', 'AUTO'),
                    'policy': data.get('policy')
                })
            except Exception:
                continue
        return backups

    def restore_backup(self, backup_id: str) -> Dict[str, Any]:
        """
        Transactional validated restore of a Golden Shield backup:
        - Validates backup_id against path traversal attacks.
        - Validates backup integrity and schema.
        - Applies policy atomically and rolls back if verification fails.
        """
        if not backup_id or not re.fullmatch(r'[a-zA-Z0-9_-]{1,64}', str(backup_id)):
            return {'success': False, 'error': 'Invalid backup checkpoint identifier or format; path traversal strictly prohibited'}

        target_file = BACKUPS_DIR / f"golden-shield-backup-{backup_id}.json"
        if not target_file.exists():
            return {'success': False, 'error': f"Backup ID {backup_id} not found"}

        try:
            b_data = json.loads(target_file.read_text(encoding='utf-8'))
        except Exception as e:
            return {'success': False, 'error': f"Corrupted backup JSON: {e}"}

        restored_policy = b_data.get('policy')
        if not restored_policy or not isinstance(restored_policy, dict):
            return {'success': False, 'error': 'Backup does not contain a valid policy structure'}

        # Save pre-restore checkpoint
        rollback_id = self.backup_current_config()
        restored_mode = b_data.get('mode', 'AUTO')

        try:
            # Write policy atomically
            tmp_policy = BASE / 'policy.json.tmp'
            tmp_policy.write_text(json.dumps(restored_policy, indent=2), encoding='utf-8')
            tmp_policy.replace(BASE / 'policy.json')

            self.set_persisted_mode(restored_mode)

            # Apply memory cap and CPU quota
            cmd = ['python3', '/usr/local/sbin/golden-shield.py', 'apply-memory-cap']
            subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            # Apply persistent CPU quota and MemoryMax
            self.persist_systemd_slice_limits(restored_policy['customerCpuPercent'], restored_policy['hostingMemoryMaxMiB'])

            v_res = self.verify()
            if not v_res.get('success', False):
                # Rollback on verification failure
                self.restore_backup(rollback_id)
                return {'success': False, 'error': 'Restoration verification failed; safely rolled back to pre-restore state'}

            return {
                'success': True,
                'message': f"Backup {backup_id} successfully restored and verified",
                'restored_policy': restored_policy,
                'mode': restored_mode
            }
        except Exception as e:
            self.restore_backup(rollback_id)
            return {'success': False, 'error': f"Transactional restoration aborted and rolled back: {e}"}

    def persist_systemd_slice_limits(self, customer_cpu_pct: int, hosting_mem_mib: int):
        """
        Write systemd drop-in override so limits persist across server reboot.
        Updates /etc/systemd/system/golden.slice.d/50-uniselv-limits.conf and runtime properties.
        """
        dropin_dir = UNITS / 'golden.slice.d'
        dropin_dir.mkdir(parents=True, exist_ok=True)
        conf_file = dropin_dir / '50-uniselv-limits.conf'
        
        mem_bytes = hosting_mem_mib * 1024 * 1024
        conf_content = f"""# Automatically managed by UNISELV Resource Manager
[Slice]
CPUQuota={customer_cpu_pct}%
MemoryMax={mem_bytes}
MemorySwapMax=0
"""
        conf_file.write_text(conf_content, encoding='utf-8')
        subprocess.run(['systemctl', 'daemon-reload'], timeout=15)
        subprocess.run(['systemctl', 'set-property', '--runtime', 'golden.slice', f'CPUQuota={customer_cpu_pct}%', f'MemoryMax={mem_bytes}', 'MemorySwapMax=0'], timeout=20)

    def verify(self) -> Dict[str, Any]:
        """Execute comprehensive verification check against live kernel."""
        cmd = ['python3', '/usr/local/sbin/golden-shield.py', 'check']
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        try:
            parsed = json.loads(r.stdout)
            checks_pass = (r.returncode == 0 and parsed.get('checksPass', False))
            return {'success': checks_pass, 'report': parsed}
        except Exception:
            return {'success': False, 'raw_output': r.stdout, 'raw_error': r.stderr}

    def verify_until_ready(self, timeout_seconds: float = 30) -> Dict[str, Any]:
        """Wait for asynchronous service startup without relaxing any kernel checks."""
        deadline = time.monotonic() + timeout_seconds
        while True:
            result = self.verify()
            if result.get('success') or time.monotonic() >= deadline:
                return result
            time.sleep(2)

    def reconfigure_or_enable(self, mode: str = 'auto', custom_overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Apply new policy transactionally with complete parameter validation:
        - Validates all manual ranges before any mutation.
        - Persists governance mode ('AUTO' or 'MANUAL').
        - Persists systemd drop-ins so limits survive server reboots.
        - Rolls back to timestamped backup if verification fails.
        """
        mode_clean = str(mode).lower()
        hw = self.detect_hardware()

        if mode_clean == 'manual' and custom_overrides:
            # Strict validation of manual parameters
            policy = self.calculate_auto_policy(hw)
            
            if 'customerCpuPercent' in custom_overrides:
                val = int(custom_overrides['customerCpuPercent'])
                min_cpu = 50
                max_cpu = hw['cpu_count'] * 400
                if val < min_cpu or val > max_cpu:
                    return {'success': False, 'error': f"Invalid CPU Quota: Must be between {min_cpu}% and {max_cpu}%"}
                policy['customerCpuPercent'] = val
                policy['reservedCpuPercent'] = max(10, (hw['cpu_count'] * 100) - val)

            if 'hostingMemoryMaxMiB' in custom_overrides:
                val = int(custom_overrides['hostingMemoryMaxMiB'])
                min_mem = 512
                max_mem = max(512, hw['ram_total_mib'] - 384)
                if val < min_mem or val > max_mem:
                    return {'success': False, 'error': f"Invalid Memory Cap: Must be between {min_mem} MiB and {max_mem} MiB (preserving 384 MiB system reserve); exceeds physical RAM safety budget"}
                
                # Check current memory pressure before reducing memory cap
                eff = self.get_effective_values()
                root = pathlib.Path('/sys/fs/cgroup/golden.slice')
                if root.exists() and (root / 'memory.current').exists():
                    try:
                        cur_bytes = int((root / 'memory.current').read_text().strip())
                        cur_mib = cur_bytes // (1024 * 1024)
                        if val < cur_mib:
                            print(f"[Warning] New memory cap ({val} MiB) is below current usage ({cur_mib} MiB); kernel will reclaim pagecache.")
                    except Exception:
                        pass
                
                policy['hostingMemoryMaxMiB'] = val
                policy['headroomMiB'] = max(384, hw['ram_total_mib'] - val)

            governance_mode = 'MANUAL'
        else:
            policy = self.calculate_auto_policy(hw)
            governance_mode = 'AUTO'

        # Create rollback checkpoint
        rollback_id = self.backup_current_config()

        try:
            # Write policy atomically
            tmp_policy = BASE / 'policy.json.tmp'
            tmp_policy.write_text(json.dumps(policy, indent=2), encoding='utf-8')
            tmp_policy.replace(BASE / 'policy.json')

            self.set_persisted_mode(governance_mode)

            # Record hardware fingerprint
            (BASE / 'hardware.json').write_text(json.dumps(hw, indent=2), encoding='utf-8')

            # Apply limits
            if (STATE / 'installed.json').exists():
                cmd = ['python3', '/usr/local/sbin/golden-shield.py', 'apply-memory-cap']
                subprocess.run(cmd, capture_output=True, text=True, timeout=30, check=True)
                self.persist_systemd_slice_limits(policy['customerCpuPercent'], policy['hostingMemoryMaxMiB'])
                v_res = self.verify_until_ready()
                if not v_res.get('success', False):
                    self.restore_backup(rollback_id)
                    return {'success': False, 'error': 'Verification failed after applying policy; rolled back.', 'verification': v_res}
                return {'success': True, 'mode': governance_mode, 'policy': policy, 'verification': v_res, 'message': 'Golden Shield policy applied and verified.'}
            else:
                cmd = ['python3', '/usr/local/sbin/golden-shield.py', 'install']
                r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
                r.check_returncode()
                self.persist_systemd_slice_limits(policy['customerCpuPercent'], policy['hostingMemoryMaxMiB'])
                v_res = self.verify_until_ready()
                if not v_res.get('success', False):
                    self.restore_backup(rollback_id)
                    return {'success': False, 'error': 'Golden Shield installation verification failed; rolled back.', 'verification': v_res}
                return {'success': True, 'mode': governance_mode, 'policy': policy, 'verification': v_res, 'message': 'Golden Shield installed and verified.'}
        except Exception as e:
            self.restore_backup(rollback_id)
            return {'success': False, 'error': f"Failed to apply policy: {e}; rolled back"}

    def disable(self) -> Dict[str, Any]:
        """Safely uninstall / disable Golden Shield."""
        if not (STATE / 'installed.json').exists():
            return {'success': True, 'message': 'Golden Shield is not currently active.'}
        self.backup_current_config()
        
        # Remove systemd drop-in overrides
        dropin_file = UNITS / 'golden.slice.d' / '50-uniselv-limits.conf'
        if dropin_file.exists():
            try:
                dropin_file.unlink()
                subprocess.run(['systemctl', 'daemon-reload'], timeout=15)
            except Exception:
                pass

        cmd = ['python3', '/usr/local/sbin/golden-shield.py', 'uninstall']
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        return {'success': (r.returncode == 0), 'output': r.stdout, 'error': r.stderr, 'message': 'Golden Shield disabled successfully.'}

    def reconcile_hardware_changes(self) -> Optional[Dict[str, Any]]:
        """
        Check for CPU and RAM hardware modifications (e.g. VPS resize/upgrade/downgrade).
        If mode is AUTO, automatically recomputes and applies the new hardware-scaled policy.
        If mode is MANUAL, preserves overrides and returns an administrative warning.
        """
        hw = self.detect_hardware()
        cur_policy = self.get_configured_policy()
        mode = self.get_persisted_mode()

        last_hw_file = BASE / 'hardware.json'
        last_hw = {}
        if last_hw_file.exists():
            try:
                last_hw = json.loads(last_hw_file.read_text(encoding='utf-8'))
            except Exception:
                last_hw = {}

        if not last_hw:
            # First initialization
            last_hw_file.write_text(json.dumps(hw, indent=2), encoding='utf-8')
            return None

        cpu_changed = (hw['cpu_count'] != last_hw.get('cpu_count'))
        # Consider RAM changed if delta > 5% to ignore dynamic driver jitter
        ram_delta_pct = abs(hw['ram_total_mib'] - last_hw.get('ram_total_mib', hw['ram_total_mib'])) / max(1, last_hw.get('ram_total_mib', hw['ram_total_mib'])) * 100
        ram_changed = ram_delta_pct > 5.0

        if not cpu_changed and not ram_changed:
            return None

        event_desc = f"Hardware capacity change detected: CPU {last_hw.get('cpu_count')} -> {hw['cpu_count']}, RAM {last_hw.get('ram_total_mib')} -> {hw['ram_total_mib']} MiB"
        print(f"[UNISELV Hardware Reconciler] {event_desc}", file=sys.stderr)

        if mode == 'AUTO':
            print("[UNISELV Hardware Reconciler] Automatically reconciling Golden Shield policy...", file=sys.stderr)
            res = self.reconfigure_or_enable('auto')
            last_hw_file.write_text(json.dumps(hw, indent=2), encoding='utf-8')
            return {
                'reconciled': True,
                'mode': 'AUTO',
                'description': event_desc,
                'new_policy': res.get('policy'),
                'success': res.get('success', False)
            }
        else:
            # Mode is MANUAL: preserve overrides but record warning
            last_hw_file.write_text(json.dumps(hw, indent=2), encoding='utf-8')
            return {
                'reconciled': False,
                'mode': 'MANUAL',
                'description': event_desc,
                'warning': "Hardware capacity changed while in MANUAL mode. Preserving custom overrides; review limits in Golden Shield Governor tab."
            }
