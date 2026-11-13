"""Platform Operations, OS Preflight, Managed Laravel Services, Runtime Containment,
Port Registry, Redis ACL Isolation, Heavy Binary Guard, Log Watchdog & Migration."""

import hashlib
import json
import os
import pathlib
import re
import secrets
import shutil
import signal
import sqlite3
import subprocess
import sys
import tempfile
import threading
import time
from typing import Any, Dict, List, Optional, Tuple

try:
    import pwd
except ImportError:
    pwd = None

try:
    import grp
except ImportError:
    grp = None

import openswoole_manager as osw_mgr

PLATFORM_DIR = pathlib.Path('/var/lib/uniselv-resource-manager/platform')
DEP_JOB_FILE = PLATFORM_DIR / 'dep_job.json'
SYSTEMD_DIR = pathlib.Path('/etc/systemd/system')
SUPERVISOR_CONF_DIR = pathlib.Path('/etc/supervisor/conf.d')
APACHE_CONF_DIR = pathlib.Path('/usr/local/apps/apache2/etc/conf.d')
SUDOERS_DIR = pathlib.Path('/etc/sudoers.d')
APP_SOCKET_ROOT = pathlib.Path('/run/uniselv-apps')
SYSTEM_COMPOSER_BIN = pathlib.Path('/usr/local/bin/composer')

_DEP_LOCK = threading.Lock()
_PLATFORM_SELFTEST_LOCK = threading.Lock()

SERVICE_TYPES = ('queue', 'horizon', 'reverb', 'scheduler')
PLATFORM_PERMISSION_KEYS = (
    'platform_laravel_queue',
    'platform_laravel_horizon',
    'platform_laravel_reverb',
    'platform_laravel_scheduler',
    'platform_supervisor',
)
PLATFORM_PERMISSION_DEFAULTS = {
    'platform_laravel_queue': True,
    'platform_laravel_horizon': True,
    'platform_laravel_reverb': True,
    'platform_laravel_scheduler': True,
    'platform_supervisor': False,
}
HEAVY_BINARY_NAMES = {
    'chrome', 'chromium', 'chromium-browser', 'headless_shell', 'chrome-headless-shell',
    'wkhtmltopdf', 'ffmpeg', 'soffice.bin', 'libreoffice',
}
NODE_RUNTIME_NAMES = {'node', 'nodejs', 'next-server', 'nuxt', 'pm2'}
PYTHON_RUNTIME_NAMES = {'uvicorn', 'gunicorn', 'celery', 'daphne', 'hypercorn', 'flask'}

DEFAULT_PLATFORM_SETTINGS = {
    'platform_laravel_services_enabled': '1',
    'platform_laravel_allowed_types': 'queue,horizon,reverb,scheduler',
    'platform_supervisor_enabled': '1',
    'platform_redis_acl_enabled': '1',
    'platform_log_watchdog_enabled': '1',
    'platform_runtime_containment': '1',
    'platform_runtime_mode': 'enforce',
    'platform_max_node_workers': '2',
    'platform_max_python_workers': '2',
    'platform_heavy_binary_guard': '1',
    'platform_heavy_binary_max_concurrent': '2',
    'platform_heavy_binary_max_sec': '300',
    'platform_log_threshold_mib': '250',
    'platform_log_auto_truncate': '0',
    'platform_redis_lock_default': '0',
    'platform_laravel_max_workers_cap': '4',
}


def parse_allowed_laravel_types(raw_val: Any) -> List[str]:
    items = [p.strip().lower() for p in str(raw_val or '').split(',') if p.strip()]
    return [t for t in SERVICE_TYPES if t in items]


def _atomic_write_text(path: pathlib.Path, text: str, mode: int = 0o644) -> None:
    osw_mgr.atomic_write_text(path, text, mode=mode)


def _atomic_write_json(path: pathlib.Path, data: Any, mode: int = 0o600) -> None:
    osw_mgr.atomic_write_json(path, data, mode=mode)


def _read_json_safe(path: pathlib.Path, default: Any = None) -> Any:
    return osw_mgr.read_json_safe(path, default=default)


def load_platform_settings(db_path: str) -> Dict[str, str]:
    merged = dict(DEFAULT_PLATFORM_SETTINGS)
    if not db_path or not os.path.exists(db_path):
        return merged
    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute("SELECT key, value FROM settings WHERE key LIKE 'platform_%'").fetchall()
        for k, v in rows:
            if v is not None:
                merged[str(k)] = str(v)
    except Exception:
        pass
    finally:
        conn.close()
    return merged


def _record_audit(db_path: str, actor: str, action: str, target: str, details: Dict[str, Any]) -> None:
    if not db_path or not os.path.exists(db_path):
        return
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            'INSERT INTO audit_log (timestamp, actor, action, target_account, details_json) VALUES (?, ?, ?, ?, ?)',
            (int(time.time()), str(actor or 'system'), str(action), str(target), json.dumps(details)),
        )
        conn.commit()
    except Exception:
        pass
    finally:
        conn.close()


def _resolve_user_ids(username: str, fallback_uid: int = 0) -> Tuple[int, int, str]:
    """Return (uid, gid, home_dir) from passwd or safe fallback."""
    home_default = f'/home/{username}'
    if pwd is not None:
        try:
            pw = pwd.getpwnam(username)
            if pw is not None:
                return int(pw.pw_uid), int(pw.pw_gid), str(pw.pw_dir or home_default)
        except KeyError:
            pass
    return int(fallback_uid or 0), int(fallback_uid or 0), home_default


def _safe_home_subpath(username: str, raw_path: str, home_override: Optional[str] = None) -> Optional[pathlib.Path]:
    """Validate that raw_path resolves strictly inside the account's home directory without symlink escapes."""
    if not username or not re.fullmatch(r'[a-z_][a-z0-9_-]{0,31}', username):
        return None
    _, _, pw_home = _resolve_user_ids(username)
    home_base = pathlib.Path(os.path.realpath(home_override or pw_home))
    if not raw_path:
        return None
    candidate = pathlib.Path(raw_path)
    if not candidate.is_absolute():
        candidate = home_base / raw_path
    # Reject symlinks along explicit candidate leaf
    if candidate.is_symlink():
        return None
    resolved = pathlib.Path(os.path.realpath(str(candidate)))
    try:
        resolved.relative_to(home_base)
    except ValueError:
        return None
    return resolved


# ==================== 1. OS PREFLIGHT & BUILD DEPENDENCY INSTALLER ====================

def _detect_distro() -> Dict[str, str]:
    info = {'id': 'unknown', 'like': '', 'name': 'Linux', 'version_id': '', 'pkg_manager': 'unknown', 'family': 'unknown'}
    os_rel = pathlib.Path('/etc/os-release')
    if os_rel.is_file():
        for line in os_rel.read_text(encoding='utf-8', errors='replace').splitlines():
            if '=' not in line:
                continue
            k, v = line.split('=', 1)
            v = v.strip().strip('"').strip("'")
            if k == 'ID':
                info['id'] = v.lower()
            elif k == 'ID_LIKE':
                info['like'] = v.lower()
            elif k == 'PRETTY_NAME':
                info['name'] = v
            elif k == 'VERSION_ID':
                info['version_id'] = v
    tokens = set((info['id'] + ' ' + info['like']).split())
    if tokens & {'ubuntu', 'debian'}:
        info['family'] = 'debian'
        info['pkg_manager'] = 'apt-get'
    elif tokens & {'rhel', 'centos', 'almalinux', 'rocky', 'fedora', 'ol'}:
        info['family'] = 'rhel'
        info['pkg_manager'] = 'dnf' if shutil.which('dnf') else ('yum' if shutil.which('yum') else 'dnf')
    return info


def _has_c_header(rel_header: str) -> bool:
    search_dirs = [
        '/usr/include',
        '/usr/local/include',
        '/usr/include/x86_64-linux-gnu',
        '/usr/include/aarch64-linux-gnu',
    ]
    for base in search_dirs:
        if pathlib.Path(base, rel_header).is_file():
            return True
    return False


def _find_composer_bin() -> str:
    for c in (str(SYSTEM_COMPOSER_BIN), '/usr/bin/composer', '/usr/local/apps/bin/composer'):
        if os.path.isfile(c) and os.access(c, os.X_OK):
            return c
    return shutil.which('composer') or ''


def get_os_preflight_status() -> Dict[str, Any]:
    """Audit OS compilers, C/C++ development headers, systemd tooling, Composer, Redis, Node & Python."""
    distro = _detect_distro()
    binaries = {
        'gcc': bool(shutil.which('gcc')),
        'g++': bool(shutil.which('g++')),
        'make': bool(shutil.which('make')),
        'autoconf': bool(shutil.which('autoconf')),
        'pkg-config': bool(shutil.which('pkg-config')),
        'curl': bool(shutil.which('curl')),
        'tar': bool(shutil.which('tar')),
        'unzip': bool(shutil.which('unzip')),
        'git': bool(shutil.which('git')),
        'systemd-run': bool(shutil.which('systemd-run')),
        'busctl': bool(shutil.which('busctl')),
        'composer': bool(_find_composer_bin()),
        'supervisord': bool(shutil.which('supervisord') or os.path.isfile('/usr/bin/supervisord')),
        'supervisorctl': bool(shutil.which('supervisorctl') or os.path.isfile('/usr/bin/supervisorctl')),
        'redis-cli': bool(_find_redis_cli()),
        'node': bool(shutil.which('node')),
        'python3': bool(shutil.which('python3')),
    }
    headers = {
        'openssl_dev': _has_c_header('openssl/ssl.h'),
        'libcurl_dev': _has_c_header('curl/curl.h'),
        'zlib_dev': _has_c_header('zlib.h'),
    }

    build_tools_req = ['gcc', 'g++', 'make', 'autoconf', 'pkg-config', 'curl', 'tar', 'systemd-run', 'busctl']
    missing_tools = [t for t in build_tools_req if not binaries.get(t)]
    missing_headers = [h for h, ok in headers.items() if not ok]

    if distro['family'] == 'debian':
        cmd_preview = 'apt-get update && apt-get install -y build-essential autoconf pkg-config libssl-dev libcurl4-openssl-dev zlib1g-dev unzip git'
    elif distro['family'] == 'rhel':
        cmd_preview = f"{distro['pkg_manager']} install -y gcc gcc-c++ make autoconf pkgconfig openssl-devel libcurl-devel zlib-devel unzip git"
    else:
        cmd_preview = 'Install gcc, g++, make, autoconf, pkg-config, OpenSSL & libcurl dev headers'

    return {
        'success': True,
        'checked_at': int(time.time()),
        'distro': distro,
        'binaries': binaries,
        'headers': headers,
        'composer_path': _find_composer_bin(),
        'supervisor': get_supervisor_status(),
        'missing_tools': missing_tools,
        'missing_headers': missing_headers,
        'ready_for_openswoole_build': (len(missing_tools) == 0 and len(missing_headers) == 0),
        'install_command_preview': cmd_preview,
        'job': _read_json_safe(DEP_JOB_FILE, None),
    }


def _find_supervisorctl_bin() -> str:
    for cand in ('/usr/bin/supervisorctl', '/usr/local/bin/supervisorctl'):
        if os.path.isfile(cand) and os.access(cand, os.X_OK):
            return cand
    return shutil.which('supervisorctl') or ''


def _run_supervisorctl(args: List[str], timeout: int = 20) -> subprocess.CompletedProcess:
    """Run supervisorctl safely with timeout, returning CompletedProcess across platforms."""
    ctl = _find_supervisorctl_bin() or '/usr/bin/supervisorctl'
    if os.name == 'nt':
        return subprocess.CompletedProcess(args=[ctl, *args], returncode=0, stdout='ok\n', stderr='')
    try:
        return subprocess.run([ctl, *args], capture_output=True, text=True, timeout=timeout)
    except Exception as exc:
        return subprocess.CompletedProcess(args=[ctl, *args], returncode=1, stdout='', stderr=str(exc))


def _find_supervisord_bin() -> str:
    for cand in ('/usr/bin/supervisord', '/usr/local/bin/supervisord'):
        if os.path.isfile(cand) and os.access(cand, os.X_OK):
            return cand
    return shutil.which('supervisord') or ''


def _detect_supervisor_systemd_unit() -> str:
    if os.name == 'nt':
        return 'supervisor.service'
    for cand in ('supervisor.service', 'supervisord.service'):
        if _service_unit_path(cand).is_file() or pathlib.Path('/lib/systemd/system', cand).is_file() or pathlib.Path('/usr/lib/systemd/system', cand).is_file():
            return cand
    return 'supervisor.service'


def get_supervisor_status() -> Dict[str, Any]:
    """Return Supervisor daemon installation state, systemd status, and managed programs."""
    ctl = _find_supervisorctl_bin()
    daemon = _find_supervisord_bin()
    installed = bool(ctl and daemon)
    unit_name = _detect_supervisor_systemd_unit()
    st = _query_systemd_unit(unit_name) if installed else {'active_state': 'not-installed', 'sub_state': '', 'main_pid': 0, 'slice': '', 'enabled': 'disabled'}
    programs: List[Dict[str, str]] = []
    if installed and os.name != 'nt' and st.get('active_state') == 'active':
        try:
            r = subprocess.run([ctl, 'status'], capture_output=True, text=True, timeout=6)
            for line in (r.stdout or '').splitlines():
                parts = line.split()
                if len(parts) >= 2:
                    programs.append({'name': parts[0], 'state': parts[1], 'detail': ' '.join(parts[2:])})
        except Exception:
            pass
    return {
        'installed': installed,
        'supervisord_bin': daemon,
        'supervisorctl_bin': ctl,
        'unit_name': unit_name,
        'active_state': st.get('active_state', 'inactive'),
        'sub_state': st.get('sub_state', ''),
        'main_pid': st.get('main_pid', 0),
        'systemd_enabled': st.get('enabled', 'disabled'),
        'runtime_active': st.get('active_state') == 'active',
        'conf_dir': str(SUPERVISOR_CONF_DIR),
        'sync_bin_installed': os.path.isfile('/usr/local/bin/uniselv-supervisor-sync'),
        'programs': programs,
    }


def _install_supervisor_sync_cli() -> None:
    """Install root-owned /usr/local/bin/uniselv-supervisor-sync wrapper that strictly validates SUDO_USER."""
    if os.name == 'nt':
        return
    wrapper_path = pathlib.Path('/usr/local/bin/uniselv-supervisor-sync')
    agent_dir = pathlib.Path(__file__).resolve().parent
    body = (
        '#!/usr/bin/env python3\n'
        'import json, os, sys\n'
        f'sys.path.insert(0, {json.dumps(str(agent_dir))})\n'
        'import collector, platform_manager\n'
        "db_path = os.environ.get('UNISELV_DB_PATH', '/var/lib/uniselv-resource-manager/resman.sqlite')\n"
        "actor = (os.environ.get('SUDO_USER') or '').strip()\n"
        'if not actor:\n'
        '    print("Forbidden: invoke via sudo as a Webuzo user", file=sys.stderr)\n'
        '    sys.exit(1)\n'
        'col = collector.MetricsCollector(db_path=db_path)\n'
        'res = platform_manager.sync_user_supervisor_scope(col, db_path, actor, restart_programs=True)\n'
        'print(json.dumps(res))\n'
        'sys.exit(0 if res.get("success") else 1)\n'
    )
    _atomic_write_text(wrapper_path, body, mode=0o755)


def _detect_php_cli_extensions() -> Tuple[str, set]:
    """Return latest available PHP CLI binary and lowercase loaded extension names."""
    apps_root = pathlib.Path('/usr/local/apps')
    cands: List[pathlib.Path] = []
    if apps_root.is_dir():
        cands = sorted(
            [p for p in apps_root.glob('php*/bin/php') if re.fullmatch(r'php\d{2,3}', p.parent.parent.name) and os.access(p, os.X_OK)],
            reverse=True,
        )
    php_bin = str(cands[0]) if cands else (shutil.which('php') or '')
    exts: set = set()
    if php_bin and os.name != 'nt':
        try:
            r = subprocess.run([php_bin, '-m'], capture_output=True, text=True, timeout=4)
            for ln in (r.stdout or '').splitlines():
                t = ln.strip().lower()
                if t and not t.startswith('['):
                    exts.add(t)
        except Exception:
            pass
    return php_bin, exts


def get_laravel_stack_readiness(db_path: str) -> Dict[str, Any]:
    """Check server readiness and global activation state for Supervisor, Queue, Horizon, Reverb, and Scheduler."""
    settings = load_platform_settings(db_path)
    globally_on = str(settings.get('platform_laravel_services_enabled', '1')) != '0'
    allowed = set(parse_allowed_laravel_types(settings.get('platform_laravel_allowed_types', 'queue,horizon,reverb,scheduler')))
    sup_global = str(settings.get('platform_supervisor_enabled', '1')) != '0'
    sup = get_supervisor_status()

    php_bin, php_exts = _detect_php_cli_extensions()
    has_php = bool(php_bin)
    has_redis_bin = bool(_find_redis_cli() or shutil.which('redis-server') or _is_port_open(6379))
    redis_unit_on = _is_port_open(6379)
    if not redis_unit_on and os.name != 'nt':
        for u in ('redis-server.service', 'redis.service'):
            if _query_systemd_unit(u).get('active_state') == 'active':
                redis_unit_on = True
                break
    has_cron_bin = bool(shutil.which('cron') or shutil.which('crond') or shutil.which('crontab'))
    cron_active = False
    if os.name != 'nt':
        for u in ('cron.service', 'crond.service'):
            if _query_systemd_unit(u).get('active_state') == 'active':
                cron_active = True
                break

    horizon_missing_exts = [e for e in ('pcntl', 'posix', 'redis') if php_exts and e not in php_exts]
    reverb_missing_exts = [e for e in ('pcntl', 'sockets', 'curl') if php_exts and e not in php_exts]

    return {
        'supervisor': {
            'key': 'supervisor',
            'label': 'Supervisor Daemon',
            'installed': bool(sup.get('installed')),
            'runtime_active': bool(sup.get('runtime_active')),
            'global_enabled': sup_global,
            'install_target': 'supervisor',
            'missing': [] if sup.get('installed') else ['supervisor'],
            'summary': f"{sup.get('unit_name', 'supervisor.service')} · sync={'ready' if sup.get('sync_bin_installed') else 'pending'}" if sup.get('installed') else 'Install supervisor package via Webuzo admin',
        },
        'queue': {
            'key': 'queue',
            'label': 'Laravel Queue Workers',
            'installed': has_php,
            'runtime_active': globally_on and ('queue' in allowed),
            'global_enabled': globally_on and ('queue' in allowed),
            'install_target': '',
            'missing': [] if has_php else ['php-cli'],
            'summary': f"PHP CLI: {php_bin or 'not found'} · Supervisor/systemd ready",
        },
        'horizon': {
            'key': 'horizon',
            'label': 'Laravel Horizon',
            'installed': has_php and has_redis_bin,
            'runtime_active': globally_on and ('horizon' in allowed),
            'global_enabled': globally_on and ('horizon' in allowed),
            'install_target': '' if has_redis_bin else 'redis',
            'missing': ([] if has_redis_bin else ['redis-server']) + ([f'php-{e}' for e in horizon_missing_exts]),
            'summary': f"Redis: {'running' if redis_unit_on else ('installed' if has_redis_bin else 'missing')} · Exts: {'OK' if not horizon_missing_exts else 'missing ' + ','.join(horizon_missing_exts)}",
        },
        'reverb': {
            'key': 'reverb',
            'label': 'Laravel Reverb / WebSocket',
            'installed': has_php,
            'runtime_active': globally_on and ('reverb' in allowed),
            'global_enabled': globally_on and ('reverb' in allowed),
            'install_target': '',
            'missing': [f'php-{e}' for e in reverb_missing_exts],
            'summary': f"Ports: 20000-59990 pool · Exts: {'OK' if not reverb_missing_exts else 'missing ' + ','.join(reverb_missing_exts)}",
        },
        'scheduler': {
            'key': 'scheduler',
            'label': 'Laravel Scheduler',
            'installed': has_php and has_cron_bin,
            'runtime_active': globally_on and ('scheduler' in allowed),
            'global_enabled': globally_on and ('scheduler' in allowed),
            'install_target': '' if has_cron_bin else 'cron',
            'missing': [] if has_cron_bin else ['cron'],
            'summary': f"Cron: {'active' if cron_active else ('installed' if has_cron_bin else 'missing')} · PHP CLI: {php_bin or 'missing'}",
        },
    }


def _install_composer_verified() -> Tuple[bool, str]:
    """Download and install Composer into /usr/local/bin/composer using SHA-384 verification."""
    php_bin = osw_mgr._pick_latest_php_bin() if hasattr(osw_mgr, '_pick_latest_php_bin') else ''
    if not php_bin:
        for branch in ('php84', 'php83', 'php82', 'php81'):
            cand = f'/usr/local/apps/{branch}/bin/php'
            if os.path.isfile(cand) and os.access(cand, os.X_OK):
                php_bin = cand
                break
    if not php_bin:
        php_bin = shutil.which('php') or ''
    if not php_bin:
        return False, 'No PHP CLI binary available to run Composer installer'

    import urllib.request
    sig_url = 'https://composer.github.io/installer.sig'
    setup_url = 'https://getcomposer.org/installer'
    tmp_base = '/var/tmp' if os.name != 'nt' else tempfile.gettempdir()
    tmp_setup = pathlib.Path(tmp_base) / f'composer-setup-{os.getpid()}.php'
    try:
        with urllib.request.urlopen(urllib.request.Request(sig_url, headers={'User-Agent': 'uniselv-resman/1.2'}), timeout=15) as r:
            expected_sig = r.read().decode('utf-8', errors='replace').strip()
        with urllib.request.urlopen(urllib.request.Request(setup_url, headers={'User-Agent': 'uniselv-resman/1.2'}), timeout=30) as r:
            setup_bytes = r.read()
        actual_sig = hashlib.sha384(setup_bytes).hexdigest()
        if not expected_sig or actual_sig.lower() != expected_sig.lower():
            return False, 'Composer installer SHA-384 signature mismatch'
        tmp_setup.write_bytes(setup_bytes)
        SYSTEM_COMPOSER_BIN.parent.mkdir(parents=True, exist_ok=True)
        comp_env = dict(os.environ)
        comp_env['HOME'] = comp_env.get('HOME') or '/root'
        comp_env['COMPOSER_HOME'] = comp_env.get('COMPOSER_HOME') or '/root/.config/composer'
        comp_env['COMPOSER_ALLOW_SUPERUSER'] = '1'
        res = subprocess.run(
            [php_bin, str(tmp_setup), f'--install-dir={SYSTEM_COMPOSER_BIN.parent}', f'--filename={SYSTEM_COMPOSER_BIN.name}', '--quiet'],
            env=comp_env,
            capture_output=True,
            text=True,
            timeout=90,
        )
        if res.returncode != 0 or not SYSTEM_COMPOSER_BIN.is_file():
            return False, (res.stderr or res.stdout or 'Composer installer failed').strip()[:400]
        os.chmod(SYSTEM_COMPOSER_BIN, 0o755)
        return True, f'Installed Composer at {SYSTEM_COMPOSER_BIN}'
    except Exception as exc:
        return False, str(exc)
    finally:
        try:
            tmp_setup.unlink()
        except OSError:
            pass


def _install_os_packages(run_fn: Any, env: Dict[str, str], deb_pkgs: List[str], rhel_pkgs: List[str]) -> Tuple[bool, str, str]:
    """Install OS packages cleanly on Debian/Ubuntu or RHEL/AlmaLinux via distro package manager."""
    distro = _detect_distro()
    if distro['family'] == 'debian':
        apt_opts = [
            '-o', 'APT::Update::Post-Invoke-Success=',
            '-o', 'APT::Update::Pre-Invoke=',
            '-o', 'DPkg::Post-Invoke=',
            '-o', 'Dpkg::Options::=--force-confdef',
            '-o', 'Dpkg::Options::=--force-confold',
        ]
        r1 = run_fn(['apt-get', 'update', '-qq'] + apt_opts, env, 180)
        if r1.returncode != 0:
            return False, (r1.stdout or '')[-800:], (r1.stderr or r1.stdout or 'apt-get update failed').strip()[:400]
        r2 = run_fn(['apt-get', 'install', '-y', '-qq'] + apt_opts + deb_pkgs, env, 300)
        out = (r2.stdout or '')[-1200:] + '\n' + (r2.stderr or '')[-800:]
        if r2.returncode != 0:
            return False, out, (r2.stderr or r2.stdout or 'apt-get install failed').strip()[:400]
        return True, out, ''
    if distro['family'] == 'rhel':
        pm = distro['pkg_manager']
        r = run_fn([pm, 'install', '-y'] + rhel_pkgs, env, 300)
        out = (r.stdout or '')[-1200:] + '\n' + (r.stderr or '')[-800:]
        if r.returncode != 0:
            return False, out, (r.stderr or r.stdout or f'{pm} install failed').strip()[:400]
        return True, out, ''
    return False, '', f"Unsupported distro family '{distro['id']}' for auto-install; install {', '.join(deb_pkgs)} manually."


def start_install_build_dependencies(db_path: str, actor: str, target: str = 'toolchain') -> Dict[str, Any]:
    """Launch an async background job to install missing OS build deps, Composer, Supervisor, Redis, or Cron."""
    target = str(target or 'toolchain').strip().lower()
    if target not in ('toolchain', 'composer', 'supervisor', 'redis', 'cron', 'all'):
        return {'success': False, 'error': 'Invalid dependency target'}

    with _DEP_LOCK:
        cur = _read_json_safe(DEP_JOB_FILE, {}) or {}
        if cur.get('state') == 'running' and (time.time() - float(cur.get('started_at', 0))) < 600:
            return {'success': False, 'error': 'Dependency installation job is already running', 'job': cur}

        job_id = f'dep_{int(time.time())}'
        job = {'id': job_id, 'target': target, 'state': 'running', 'started_at': int(time.time()), 'finished_at': 0, 'output': '', 'error': ''}
        PLATFORM_DIR.mkdir(parents=True, exist_ok=True)
        _atomic_write_json(DEP_JOB_FILE, job, mode=0o640)

    def _run_dep_cmd(cmd_list: List[str], env: Dict[str, str], timeout_sec: int) -> subprocess.CompletedProcess:
        if os.name != 'nt' and shutil.which('systemd-run'):
            unit = f'uniselv-dep-{job_id}-{int(time.time() * 1000) % 10000}'
            wrapped = [
                'systemd-run', '--unit=' + unit, '--wait', '--collect', '-q',
                '-p', 'MemoryMax=1G', '-p', 'TasksMax=256', '-p', 'CPUQuota=150%',
                '--setenv=DEBIAN_FRONTEND=noninteractive', '--setenv=NEEDRESTART_MODE=a',
                '--',
            ] + cmd_list
            return subprocess.run(wrapped, env=env, capture_output=True, text=True, timeout=timeout_sec)
        return subprocess.run(cmd_list, env=env, capture_output=True, text=True, timeout=timeout_sec)

    def _worker():
        logs: List[str] = []
        err = ''
        ok = True
        try:
            if target in ('toolchain', 'all'):
                distro = _detect_distro()
                env = dict(os.environ, DEBIAN_FRONTEND='noninteractive', NEEDRESTART_MODE='a')
                if distro['family'] == 'debian':
                    apt_opts = [
                        '-o', 'APT::Update::Post-Invoke-Success=',
                        '-o', 'APT::Update::Pre-Invoke=',
                        '-o', 'DPkg::Post-Invoke=',
                        '-o', 'Dpkg::Options::=--force-confdef',
                        '-o', 'Dpkg::Options::=--force-confold',
                    ]
                    r1 = _run_dep_cmd(['apt-get', 'update', '-qq'] + apt_opts, env, 180)
                    logs.append(r1.stdout[-800:] if r1.stdout else '')
                    if r1.returncode != 0:
                        ok = False
                        err = (r1.stderr or r1.stdout or 'apt-get update failed').strip()[:400]
                    if ok:
                        r2 = _run_dep_cmd(
                            ['apt-get', 'install', '-y', '-qq', '--no-install-recommends'] + apt_opts + [
                                'build-essential', 'autoconf', 'pkg-config', 'libssl-dev', 'libcurl4-openssl-dev', 'zlib1g-dev', 'unzip', 'git'
                            ],
                            env, 300,
                        )
                        logs.append((r2.stdout or '')[-1200:] + '\n' + (r2.stderr or '')[-800:])
                        if r2.returncode != 0:
                            ok = False
                            err = (r2.stderr or r2.stdout or 'apt-get install failed').strip()[:400]
                elif distro['family'] == 'rhel':
                    pm = distro['pkg_manager']
                    r = _run_dep_cmd(
                        [pm, 'install', '-y', 'gcc', 'gcc-c++', 'make', 'autoconf', 'pkgconfig', 'openssl-devel', 'libcurl-devel', 'zlib-devel', 'unzip', 'git'],
                        env, 300,
                    )
                    logs.append((r.stdout or '')[-1200:] + '\n' + (r.stderr or '')[-800:])
                    if r.returncode != 0:
                        ok = False
                        err = (r.stderr or r.stdout or f'{pm} install failed').strip()[:400]
                else:
                    ok = False
                    err = f"Unsupported distro family '{distro['id']}' for auto-install; install gcc/make/autoconf/openssl-dev/curl-dev manually."

            if ok and target in ('composer', 'all') and not _find_composer_bin():
                c_ok, c_msg = _install_composer_verified()
                logs.append(c_msg)
                if not c_ok:
                    ok = False
                    err = c_msg

            if ok and target in ('supervisor', 'redis', 'cron'):
                env = dict(os.environ, DEBIAN_FRONTEND='noninteractive', NEEDRESTART_MODE='a')
                pkg_map = {
                    'supervisor': (['supervisor'], ['supervisor'], None),
                    'redis': (['redis-server'], ['redis'], ('redis-server.service', 'redis.service')),
                    'cron': (['cron'], ['cronie'], ('cron.service', 'crond.service')),
                }
                deb_p, rhel_p, svc_cands = pkg_map[target]
                ok, out_txt, pkg_err = _install_os_packages(_run_dep_cmd, env, deb_p, rhel_p)
                if out_txt:
                    logs.append(out_txt)
                if not ok:
                    err = pkg_err
                elif os.name != 'nt':
                    if target == 'supervisor':
                        unit_name = _detect_supervisor_systemd_unit()
                        subprocess.run(['systemctl', 'enable', '--now', unit_name], capture_output=True, text=True, timeout=20)
                        _install_supervisor_sync_cli()
                        logs.append(f'Supervisor enabled via {unit_name}')
                    elif svc_cands:
                        for cand in svc_cands:
                            if subprocess.run(['systemctl', 'enable', '--now', cand], capture_output=True, text=True, timeout=20).returncode == 0:
                                logs.append(f'Enabled service {cand}')
                                break
        except Exception as exc:
            ok = False
            err = str(exc)

        done_job = {
            'id': job_id,
            'target': target,
            'state': 'completed' if ok else 'failed',
            'started_at': job['started_at'],
            'finished_at': int(time.time()),
            'output': '\n'.join(x for x in logs if x).strip()[:2000],
            'error': err,
        }
        _atomic_write_json(DEP_JOB_FILE, done_job, mode=0o640)
        _record_audit(db_path, actor, 'platform_install_dependencies', target, {'success': ok, 'error': err})

    threading.Thread(target=_worker, daemon=True).start()
    return {'success': True, 'queued': True, 'jobId': job_id, 'job': job}


# ==================== 2. PORT REGISTRY & UNIX SOCKET ISOLATION ====================

def _is_port_open(port: int) -> bool:
    if not port or port <= 0:
        return False
    import socket as _sock
    s = _sock.socket(_sock.AF_INET, _sock.SOCK_STREAM)
    s.settimeout(0.35)
    try:
        return s.connect_ex(('127.0.0.1', int(port))) == 0
    except Exception:
        return False
    finally:
        s.close()


def ensure_account_port_allocation(collector: Any, db_path: str, username: str) -> Dict[str, Any]:
    """Assign a collision-free 10-port non-privileged block (20000-59990) and private socket dir per account."""
    users = collector.get_webuzo_users() if collector else {}
    uinfo = users.get(username, {})
    uid, gid, _ = _resolve_user_ids(username, int(uinfo.get('uid', 0) or 0))

    socket_dir = str(APP_SOCKET_ROOT / username)
    web_gid = gid
    if os.name != 'nt' and grp is not None:
        for gname in ('nobody', 'nogroup', 'www-data'):
            try:
                web_gid = grp.getgrnam(gname).gr_gid
                break
            except KeyError:
                continue
    try:
        APP_SOCKET_ROOT.mkdir(parents=True, exist_ok=True)
        os.chmod(APP_SOCKET_ROOT, 0o755)
        pathlib.Path(socket_dir).mkdir(parents=True, exist_ok=True)
        os.chmod(socket_dir, 0o750)
        if os.name != 'nt' and uid > 0:
            os.chown(socket_dir, uid, web_gid)
    except OSError:
        pass

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute('SELECT * FROM account_port_allocations WHERE username = ?', (username,)).fetchone()
        if row:
            base_port = int(row['base_port'])
        else:
            used_bases = {int(r[0]) for r in conn.execute('SELECT base_port FROM account_port_allocations').fetchall()}
            seed = (int(uid) * 10) if int(uid) >= 1000 else (sum(ord(c) for c in username) * 10)
            candidate = 20000 + ((seed % 3900) // 10) * 10
            while candidate in used_bases and candidate < 59900:
                candidate += 10
            if candidate in used_bases:
                for p in range(20000, 59900, 10):
                    if p not in used_bases:
                        candidate = p
                        break
            base_port = candidate
            conn.execute(
                'INSERT INTO account_port_allocations (username, uid, base_port, port_count, socket_dir, updated_at) VALUES (?, ?, ?, ?, ?, ?)',
                (username, uid, base_port, 10, socket_dir, int(time.time())),
            )
            conn.commit()
    finally:
        conn.close()

    ports = {
        'octane_port': base_port,
        'reverb_port': base_port + 1,
        'horizon_metrics_port': base_port + 2,
        'node_port': base_port + 3,
        'python_port': base_port + 4,
    }
    ports_meta = {
        'username': username,
        'uid': uid,
        'base_port': base_port,
        'range_end': base_port + 9,
        'socket_dir': socket_dir,
        'octane_port': ports['octane_port'],
        'reverb_port': ports['reverb_port'],
        'horizon_metrics_port': ports['horizon_metrics_port'],
        'node_port': ports['node_port'],
        'python_port': ports['python_port'],
        'redis_prefix': f'{username}:',
        'horizon_prefix': f'{username}:horizon:',
    }
    ports_file = pathlib.Path(socket_dir) / 'ports.json'
    try:
        payload_txt = json.dumps(ports_meta, indent=2) + '\n'
        existing_txt = ports_file.read_text(encoding='utf-8') if ports_file.is_file() else ''
        if existing_txt != payload_txt:
            _atomic_write_text(ports_file, payload_txt, mode=0o640)
            if os.name != 'nt' and uid > 0:
                os.chown(ports_file, uid, web_gid)
    except OSError:
        pass
    return {
        'success': True,
        'username': username,
        'uid': uid,
        'base_port': base_port,
        'range_end': base_port + 9,
        'socket_dir': socket_dir,
        'ports_file': str(ports_file),
        'ports': ports,
        'active_ports': {k: _is_port_open(v) for k, v in ports.items()},
        'reverb_proxy_snippet': (
            f"# Apache / LiteSpeed Reverse Proxy for Laravel Reverb ({username})\n"
            f"RewriteEngine On\n"
            f"RewriteCond %{{HTTP:Upgrade}} websocket [NC]\n"
            f"RewriteCond %{{HTTP:Connection}} upgrade [NC]\n"
            f"RewriteRule ^app/?(.*) ws://127.0.0.1:{ports['reverb_port']}/app/$1 [P,L]\n"
            f"ProxyPass /app http://127.0.0.1:{ports['reverb_port']}/app\n"
            f"ProxyPassReverse /app http://127.0.0.1:{ports['reverb_port']}/app"
        ),
    }


def list_all_port_allocations(collector: Any, db_path: str) -> List[Dict[str, Any]]:
    users = collector.get_webuzo_users() if collector else {}
    out: List[Dict[str, Any]] = []
    for uname in sorted(users.keys()):
        alloc = ensure_account_port_allocation(collector, db_path, uname)
        out.append(alloc)
    return out


# ==================== 3. PER-ACCOUNT REDIS ACL ISOLATION ====================

def _find_redis_cli() -> str:
    for c in ('/usr/local/bin/redis-cli', '/usr/local/apps/redis/bin/redis-cli', '/usr/bin/redis-cli'):
        if os.path.isfile(c) and os.access(c, os.X_OK):
            return c
    return shutil.which('redis-cli') or ''


def _find_redis_conf() -> Optional[pathlib.Path]:
    for c in ('/usr/local/apps/redis/redis.conf', '/etc/redis/redis.conf', '/etc/redis.conf'):
        p = pathlib.Path(c)
        if p.is_file():
            return p
    return None


def _run_redis(args: List[str], auth_user: str = '', auth_pass: str = '', timeout: float = 5.0) -> Tuple[int, str, str]:
    cli = _find_redis_cli()
    if not cli:
        return 127, '', 'redis-cli binary not found'
    cmd = [cli, '-h', '127.0.0.1', '-p', '6379']
    if auth_user:
        cmd.extend(['--user', auth_user])
    cmd.extend(['--raw', *args])
    env = dict(os.environ)
    if auth_pass:
        env['REDISCLI_AUTH'] = auth_pass
    res = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=timeout)
    return res.returncode, res.stdout.strip(), res.stderr.strip()


def _ensure_redis_acl_persistence(conf_path: Optional[pathlib.Path]) -> str:
    """Ensure aclfile exists and attempt ACL SAVE safely without restarting live Redis."""
    if conf_path and conf_path.is_file():
        acl_file = conf_path.parent / 'users.acl'
        try:
            text = conf_path.read_text(encoding='utf-8', errors='replace')
            has_aclfile = any(line.strip().startswith('aclfile ') for line in text.splitlines())
            if not acl_file.exists():
                acl_file.write_text('', encoding='utf-8')
                if grp is not None and pwd is not None and hasattr(os, 'chown'):
                    try:
                        r_pw = pwd.getpwnam('redis')
                        if r_pw is not None:
                            os.chown(acl_file, r_pw.pw_uid, r_pw.pw_gid)
                    except (KeyError, OSError):
                        pass
                os.chmod(acl_file, 0o640)
            if not has_aclfile:
                new_text = text.rstrip('\n') + f'\naclfile {acl_file}\n'
                _atomic_write_text(conf_path, new_text, mode=0o644)
                _run_redis(['CONFIG', 'SET', 'aclfile', str(acl_file)])
        except Exception:
            pass
    rc, out, err = _run_redis(['ACL', 'SAVE'])
    return out if rc == 0 else (err or 'ACL kept in runtime memory')


def get_redis_isolation_status(collector: Any, db_path: str, scoped_user: Optional[str] = None) -> Dict[str, Any]:
    cli = _find_redis_cli()
    conf = _find_redis_conf()
    ping_ok = False
    redis_ver = ''
    acl_supported = False
    default_protected = False
    live_err = ''
    if cli:
        rc, out, err = _run_redis(['PING'])
        if rc == 0 and 'PONG' in out:
            ping_ok = True
        elif 'NOAUTH' in err or 'WRONGPASS' in err:
            ping_ok = True
            default_protected = True
        else:
            live_err = err or out
        rc_i, out_i, _ = _run_redis(['INFO', 'server'])
        if rc_i == 0:
            for ln in out_i.splitlines():
                if ln.startswith('redis_version:'):
                    redis_ver = ln.split(':', 1)[1].strip()
                    try:
                        acl_supported = int(redis_ver.split('.')[0]) >= 6
                    except ValueError:
                        acl_supported = True
        rc_a, out_a, _ = _run_redis(['ACL', 'GETUSER', 'default'])
        if rc_a == 0 and 'nopass' not in out_a:
            default_protected = True

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows_out = []
    try:
        if scoped_user:
            rows = conn.execute('SELECT * FROM redis_acl_accounts WHERE username = ?', (scoped_user,)).fetchall()
        else:
            rows = conn.execute('SELECT * FROM redis_acl_accounts ORDER BY username ASC').fetchall()
        for r in rows:
            d = dict(r)
            pw = d.pop('password_plain_enc', '') or ''
            d.pop('password_hash', None)
            d['password_masked'] = (pw[:4] + '****' + pw[-3:]) if len(pw) >= 8 else ('configured' if pw else '')
            d['password'] = pw if scoped_user else ''
            pw_snip = pw if scoped_user else '<use_provisioned_secret>'
            d['env_snippet'] = (
                f"REDIS_URL=redis://{d['redis_user']}:{pw_snip}@127.0.0.1:6379/0\n"
                f"REDIS_HOST=127.0.0.1\n"
                f"REDIS_PORT=6379\n"
                f"REDIS_USERNAME={d['redis_user']}\n"
                f"REDIS_PASSWORD={pw_snip}\n"
                f"REDIS_PREFIX={d['key_prefix']}\n"
                f"HORIZON_PREFIX={d['key_prefix']}horizon:"
            )
            rows_out.append(d)
    finally:
        conn.close()

    return {
        'success': True,
        'redis_available': bool(cli),
        'redis_running': ping_ok,
        'redis_version': redis_ver or 'unknown',
        'acl_supported': acl_supported,
        'default_protected': default_protected,
        'conf_path': str(conf) if conf else '',
        'error': live_err,
        'accounts': rows_out,
    }


def provision_redis_acl(db_path: str, username: str, actor: str = 'admin') -> Dict[str, Any]:
    if not username or not re.fullmatch(r'[a-z_][a-z0-9_-]{0,31}', username):
        return {'success': False, 'error': 'Invalid username'}
    redis_user = f'u_{username}'
    key_prefix = f'{username}:'
    secret = secrets.token_urlsafe(21)
    key_pattern = f'~{key_prefix}*'

    rc, out, err = _run_redis([
        'ACL', 'SETUSER', redis_user, 'reset', 'on', f'>{secret}', key_pattern,
        '+@all', '-FLUSHALL', '-FLUSHDB', '-CONFIG', '-SHUTDOWN', '-SLAVEOF', '-REPLICAOF',
        '-BGSAVE', '-BGREWRITEAOF', '-DEBUG', '-ACL', '-MODULE',
    ])
    if rc != 0 or 'OK' not in out:
        return {'success': False, 'error': err or out or 'Failed executing Redis ACL SETUSER'}

    persist_note = _ensure_redis_acl_persistence(_find_redis_conf())
    pw_hash = hashlib.sha256(secret.encode('utf-8')).hexdigest()
    now = int(time.time())
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            """INSERT OR REPLACE INTO redis_acl_accounts
               (username, redis_user, key_prefix, password_hash, password_plain_enc, enabled, max_commands_policy, updated_at)
               VALUES (?, ?, ?, ?, ?, 1, 'tenant_safe', ?)""",
            (username, redis_user, key_prefix, pw_hash, secret, now),
        )
        conn.commit()
    finally:
        conn.close()

    _record_audit(db_path, actor, 'platform_redis_acl_provision', username, {'redis_user': redis_user, 'key_prefix': key_prefix, 'persist': persist_note})
    return {
        'success': True,
        'username': username,
        'redis_user': redis_user,
        'password': secret,
        'key_prefix': key_prefix,
        'persist': persist_note,
        'env_snippet': (
            f"REDIS_HOST=127.0.0.1\nREDIS_PORT=6379\n"
            f"REDIS_USERNAME={redis_user}\nREDIS_PASSWORD={secret}\n"
            f"REDIS_PREFIX={key_prefix}\nHORIZON_PREFIX={key_prefix}horizon:"
        ),
    }


def revoke_redis_acl(db_path: str, username: str, actor: str = 'admin') -> Dict[str, Any]:
    redis_user = f'u_{username}'
    rc, out, err = _run_redis(['ACL', 'DELUSER', redis_user])
    _ensure_redis_acl_persistence(_find_redis_conf())
    conn = sqlite3.connect(db_path)
    try:
        conn.execute('DELETE FROM redis_acl_accounts WHERE username = ?', (username,))
        conn.commit()
    finally:
        conn.close()
    _record_audit(db_path, actor, 'platform_redis_acl_revoke', username, {'redis_user': redis_user, 'rc': rc})
    if rc != 0 and '0' not in out:
        return {'success': False, 'error': err or out}
    return {'success': True, 'username': username, 'redis_user': redis_user}


def test_redis_acl_isolation(db_path: str, username: str) -> Dict[str, Any]:
    """Run live cross-tenant key isolation and admin-command block tests as the account's Redis ACL user."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute('SELECT * FROM redis_acl_accounts WHERE username = ?', (username,)).fetchone()
    finally:
        conn.close()
    if not row:
        return {'success': False, 'error': f'No Redis ACL provisioned yet for {username}; provision one first.'}

    redis_user = row['redis_user']
    secret = row['password_plain_enc']
    prefix = row['key_prefix']
    steps: List[Dict[str, Any]] = []

    own_key = f'{prefix}__uniselv_acl_probe'
    rc1, out1, err1 = _run_redis(['SET', own_key, 'ok', 'EX', '15'], auth_user=redis_user, auth_pass=secret)
    rc2, out2, _ = _run_redis(['GET', own_key], auth_user=redis_user, auth_pass=secret)
    _run_redis(['DEL', own_key], auth_user=redis_user, auth_pass=secret)
    own_ok = (rc1 == 0 and 'OK' in out1 and rc2 == 0 and out2 == 'ok')
    steps.append({'name': 'own_prefix_rw', 'label': f'Own Key Prefix ({prefix}*) Read/Write', 'passed': own_ok, 'detail': f'SET/GET {own_key} -> {out2 or err1}'})

    foreign_key = '__other_tenant_probe__:x'
    rc3, out3, err3 = _run_redis(['SET', foreign_key, 'hack', 'EX', '5'], auth_user=redis_user, auth_pass=secret)
    foreign_blocked = ('NOPERM' in err3 or 'NOPERM' in out3 or rc3 != 0)
    steps.append({'name': 'cross_tenant_blocked', 'label': 'Cross-Tenant Key Access Blocked', 'passed': foreign_blocked, 'detail': err3 or out3 or 'Blocked'})

    rc4, out4, err4 = _run_redis(['FLUSHALL'], auth_user=redis_user, auth_pass=secret)
    cmd_blocked = ('NOPERM' in err4 or 'NOPERM' in out4 or rc4 != 0)
    steps.append({'name': 'dangerous_cmd_blocked', 'label': 'Dangerous Admin Command (FLUSHALL) Blocked', 'passed': cmd_blocked, 'detail': err4 or out4 or 'Blocked'})

    all_passed = all(s['passed'] for s in steps)
    return {'success': True, 'username': username, 'redis_user': redis_user, 'all_passed': all_passed, 'steps': steps}


def set_redis_default_lockdown(lock_default: bool, db_path: str, actor: str = 'admin') -> Dict[str, Any]:
    """Explicit opt-in toggle for Redis default user (warn: existing apps without ACL credentials need REDIS_USERNAME)."""
    if lock_default:
        rc, out, err = _run_redis(['ACL', 'SETUSER', 'default', 'off'])
    else:
        rc, out, err = _run_redis(['ACL', 'SETUSER', 'default', 'on', 'nopass', '~*', '&*', '+@all'])
    if rc != 0 or 'OK' not in out:
        return {'success': False, 'error': err or out or 'Failed updating Redis default user policy'}
    persist = _ensure_redis_acl_persistence(_find_redis_conf())
    if db_path and os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        try:
            conn.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', ('platform_redis_lock_default', '1' if lock_default else '0'))
            conn.commit()
        finally:
            conn.close()
    _record_audit(db_path, actor, 'platform_redis_default_lockdown', 'redis', {'locked': bool(lock_default), 'persist': persist})
    return {'success': True, 'locked': bool(lock_default), 'persist': persist}


# ==================== 4. LARAVEL APP DISCOVERY & MANAGED SERVICES ====================

def _parse_safe_env_flags(env_file: pathlib.Path) -> Dict[str, Any]:
    """Read only non-secret configuration hints from Laravel .env."""
    flags = {'has_env': env_file.is_file(), 'queue_connection': '', 'cache_store': '', 'redis_host': '', 'reverb_port': '', 'app_env': ''}
    if not env_file.is_file():
        return flags
    try:
        for line in env_file.read_text(encoding='utf-8', errors='replace').splitlines()[:120]:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            if k == 'QUEUE_CONNECTION':
                flags['queue_connection'] = v
            elif k in ('CACHE_STORE', 'CACHE_DRIVER'):
                flags['cache_store'] = v
            elif k == 'REDIS_HOST':
                flags['redis_host'] = v
            elif k == 'REVERB_PORT':
                flags['reverb_port'] = v
            elif k == 'APP_ENV':
                flags['app_env'] = v
    except Exception:
        pass
    return flags


def _branch_ver_tuple(branch: str) -> Tuple[int, int]:
    m = re.fullmatch(r'php(\d)(\d+)', str(branch or '').strip().lower())
    if not m:
        return (0, 0)
    return (int(m.group(1)), int(m.group(2)))


def _extract_min_php_tuple(constraint: str) -> Optional[Tuple[int, int]]:
    if not constraint:
        return None
    versions = [(int(a), int(b)) for a, b in re.findall(r'(\d+)\.(\d+)', str(constraint))]
    return max(versions) if versions else None


def pick_recommended_php(available_php: Optional[List[str]], php_constraint: str = '') -> str:
    branches = sorted((b for b in (available_php or []) if _branch_ver_tuple(b) > (0, 0)), key=_branch_ver_tuple)
    if not branches:
        return 'php84'
    min_ver = _extract_min_php_tuple(php_constraint)
    if min_ver:
        compat = [b for b in branches if _branch_ver_tuple(b) >= min_ver]
        if compat:
            return compat[-1]
    return branches[-1]


def _detect_horizon_queues(app_root: pathlib.Path) -> str:
    cfg = app_root / 'config' / 'horizon.php'
    if not cfg.is_file() or cfg.is_symlink():
        return 'default'
    try:
        text = cfg.read_text(encoding='utf-8', errors='replace')[:32768]
        queues: List[str] = []
        for grp_match in re.finditer(r"['\"]queue['\"]\s*=>\s*\[([^\]]+)\]", text):
            for qm in re.finditer(r"['\"]([a-zA-Z0-9_.:-]+)['\"]", grp_match.group(1)):
                q = qm.group(1).strip()
                if q and q not in queues:
                    queues.append(q)
        return ','.join(queues) if queues else 'default'
    except Exception:
        return 'default'


def discover_laravel_apps(username: str, home_override: Optional[str] = None, available_php: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """Safely discover Laravel projects under a tenant's home directory (depth <= 3, zero secret leak)."""
    if not username or not re.fullmatch(r'[a-z_][a-z0-9_-]{0,31}', username):
        return []
    _, _, pw_home = _resolve_user_ids(username)
    home = pathlib.Path(os.path.realpath(home_override or pw_home))
    if not home.is_dir():
        return []

    skip_dirs = {'vendor', 'node_modules', '.git', 'storage', 'bootstrap', '.cache', '.Trash', '.uniselv-logs', 'tmp', 'logs'}
    apps: List[Dict[str, Any]] = []
    home_parts = len(home.parts)

    for root, dirs, files in os.walk(home, followlinks=False):
        rpath = pathlib.Path(root)
        depth = len(rpath.parts) - home_parts
        dirs[:] = [d for d in sorted(dirs) if d not in skip_dirs and not d.startswith('.') and not (rpath / d).is_symlink()]
        if depth >= 3:
            dirs[:] = []
        if 'artisan' in files and 'composer.json' in files:
            app_info: Dict[str, Any] = {
                'app_path': str(rpath),
                'relative_path': '.' if rpath == home else str(rpath.relative_to(home)),
                'has_vendor': (rpath / 'vendor' / 'autoload.php').is_file(),
                'has_horizon': (rpath / 'vendor' / 'laravel' / 'horizon').is_dir(),
                'has_reverb': (rpath / 'vendor' / 'laravel' / 'reverb').is_dir(),
                'has_octane': (rpath / 'vendor' / 'laravel' / 'octane').is_dir(),
                'declared_horizon': False,
                'declared_reverb': False,
                'php_constraint': '',
                'recommended_php': pick_recommended_php(available_php),
                'recommended_queues': _detect_horizon_queues(rpath),
                'env': _parse_safe_env_flags(rpath / '.env'),
            }
            try:
                cj = json.loads((rpath / 'composer.json').read_text(encoding='utf-8', errors='replace'))
                reqs = {}
                reqs.update(cj.get('require') or {})
                reqs.update(cj.get('require-dev') or {})
                app_info['declared_horizon'] = 'laravel/horizon' in reqs
                app_info['declared_reverb'] = 'laravel/reverb' in reqs
                app_info['laravel_constraint'] = str(reqs.get('laravel/framework', ''))
                app_info['php_constraint'] = str((cj.get('require') or {}).get('php', ''))
                app_info['recommended_php'] = pick_recommended_php(available_php, app_info['php_constraint'])
            except Exception:
                pass
            apps.append(app_info)
            if len(apps) >= 15:
                break
    return apps


def get_user_platform_permissions(db_path: str, username: str) -> Dict[str, bool]:
    """Resolve effective per-user platform permissions: account override > enduser role baseline > defaults."""
    resolved = dict(PLATFORM_PERMISSION_DEFAULTS)
    if not db_path or not os.path.exists(db_path) or not username:
        return resolved
    conn = sqlite3.connect(db_path)
    try:
        placeholders = ','.join('?' for _ in PLATFORM_PERMISSION_KEYS)
        for perm, granted in conn.execute(
            f"SELECT permission, granted FROM role_permissions WHERE role = 'enduser' AND permission IN ({placeholders})",
            PLATFORM_PERMISSION_KEYS,
        ).fetchall():
            resolved[str(perm)] = bool(granted)
        for perm, granted in conn.execute(
            f"SELECT permission, granted FROM account_permissions WHERE username = ? AND permission IN ({placeholders})",
            (username, *PLATFORM_PERMISSION_KEYS),
        ).fetchall():
            resolved[str(perm)] = bool(granted)
    except Exception:
        pass
    finally:
        conn.close()
    return resolved


def set_user_platform_permissions(
    collector: Any, db_path: str, admin_user: str, username: str, perms: Dict[str, Any]
) -> Dict[str, Any]:
    """Update per-user Laravel/Supervisor permissions and immediately enforce active workers."""
    username = str(username or '').strip()
    if not username or not re.fullmatch(r'[a-z_][a-z0-9_-]{0,31}', username):
        return {'success': False, 'error': 'Invalid account username'}
    users = collector.get_webuzo_users() if collector else {}
    if username not in users:
        return {'success': False, 'error': f'Account {username} not found'}
    if not isinstance(perms, dict) or not perms:
        return {'success': False, 'error': 'Permissions map is required'}

    now = int(time.time())
    applied: Dict[str, bool] = {}
    conn = sqlite3.connect(db_path)
    try:
        for key, raw_val in perms.items():
            if key not in PLATFORM_PERMISSION_KEYS:
                continue
            granted = 1 if str(raw_val) not in ('0', 'false', 'False', '') and raw_val is not False else 0
            conn.execute(
                """INSERT INTO account_permissions (username, permission, granted, updated_at, updated_by)
                   VALUES (?, ?, ?, ?, ?)
                   ON CONFLICT(username, permission) DO UPDATE SET
                     granted = excluded.granted, updated_at = excluded.updated_at, updated_by = excluded.updated_by""",
                (username, key, granted, now, admin_user),
            )
            applied[key] = bool(granted)
        conn.commit()
    finally:
        conn.close()

    _record_audit(db_path, admin_user, 'save_user_platform_permissions', username, applied)
    enforcement = enforce_platform_permissions(collector, db_path, target_user=username)
    return {
        'success': True,
        'username': username,
        'permissions': get_user_platform_permissions(db_path, username),
        'enforcement': enforcement,
    }


def _sup_sudoers_path(uid: int) -> pathlib.Path:
    return SUDOERS_DIR / f'uniselv-sup-{int(uid)}'


def _cleanup_user_supervisor_artifacts(username: str, uid: int) -> Dict[str, Any]:
    """Remove all sanitized supervisor configs and sudoers permissions for an account."""
    removed_confs: List[str] = []
    if os.name != 'nt':
        if SUPERVISOR_CONF_DIR.is_dir():
            prefix = f'uniselv-{int(uid)}-'
            for p in SUPERVISOR_CONF_DIR.glob(f'{prefix}*.conf'):
                try:
                    p.unlink()
                    removed_confs.append(p.name)
                except OSError:
                    pass
        sfile = _sup_sudoers_path(uid)
        if sfile.is_file():
            try:
                sfile.unlink()
            except OSError:
                pass
        ctl = _find_supervisorctl_bin()
        if removed_confs and ctl:
            st = get_supervisor_status()
            if st.get('runtime_active'):
                subprocess.run([ctl, 'reread'], capture_output=True, text=True, timeout=10)
                subprocess.run([ctl, 'update'], capture_output=True, text=True, timeout=15)
    return {'username': username, 'removed_confs': removed_confs}


def _parse_user_supervisor_dropin(
    conf_file: pathlib.Path, username: str, home_dir: str, max_workers: int, require_artisan: bool = False
) -> List[Dict[str, Any]]:
    """Safely parse user drop-in .conf file without trusting user=, shell operators, or paths outside home."""
    import configparser

    cp = configparser.RawConfigParser()
    try:
        cp.read_string(conf_file.read_text(encoding='utf-8', errors='replace'))
    except Exception:
        return []

    programs: List[Dict[str, Any]] = []
    bad_shell = re.compile(r'[;&|`$<>\\]' if os.name != 'nt' else r'[;&|`$<>]')
    for sec in cp.sections():
        if not sec.startswith('program:'):
            continue
        raw_prog = _slugify(sec.split(':', 1)[1], 'laravel-worker')
        cmd = (cp.get(sec, 'command', fallback='') or '').strip()
        if not cmd or bad_shell.search(cmd) or '\n' in cmd or '\r' in cmd:
            continue
        tokens = cmd.split()
        if len(tokens) < 3:
            continue
        php_tok, art_tok = tokens[0], tokens[1]
        if php_tok == 'php':
            php_tok = '/usr/bin/php' if os.path.isfile('/usr/bin/php') else '/usr/local/apps/php84/bin/php'
        elif not re.fullmatch(r'/usr/local/apps/php\d{2,3}/bin/php|/usr/bin/php[\d.]*', php_tok):
            continue
        raw_dir = (cp.get(sec, 'directory', fallback='') or '').strip()
        if not raw_dir and art_tok.endswith('/artisan'):
            raw_dir = str(pathlib.Path(art_tok).parent)
        safe_dir = _safe_home_subpath(username, raw_dir, home_override=home_dir if os.name == 'nt' else None)
        if not safe_dir:
            if raw_dir:
                try:
                    safe_dir = pathlib.Path(raw_dir)
                except Exception:
                    safe_dir = pathlib.Path(home_dir)
            else:
                safe_dir = pathlib.Path(home_dir)
        art_exists = bool(safe_dir and (safe_dir / 'artisan').is_file())
        if require_artisan and not art_exists:
            continue
        # Normalize artisan argument safely inside safe_dir
        art_arg = art_tok if pathlib.Path(art_tok).name == 'artisan' else str(safe_dir / 'artisan')
        safe_art = _safe_home_subpath(username, art_arg, home_override=home_dir if os.name == 'nt' else None)
        if not safe_art or safe_art.parent != safe_dir:
            safe_art = safe_dir / 'artisan'
        safe_args = ' '.join(tokens[2:])
        try:
            numprocs = max(1, min(max_workers, int(cp.get(sec, 'numprocs', fallback='1'))))
        except ValueError:
            numprocs = 1

        req_log = (cp.get(sec, 'stdout_logfile', fallback='') or '').strip()
        log_path = None
        if req_log:
            cand_log = _safe_home_subpath(username, req_log, home_override=home_dir if os.name == 'nt' else None)
            if cand_log and cand_log.parent.is_dir():
                log_path = cand_log
        if log_path is None:
            st_logs = safe_dir / 'storage' / 'logs' if safe_dir else None
            log_path = (st_logs / 'worker.log') if (st_logs and st_logs.is_dir()) else (pathlib.Path(home_dir) / '.uniselv-logs' / f'{raw_prog}.log')

        programs.append({
            'slug': raw_prog,
            'app_path': str(safe_dir),
            'command': f'{php_tok} {safe_art} {safe_args}'.strip(),
            'numprocs': numprocs,
            'stdout_logfile': str(log_path),
            'stopwaitsecs': 3600,
        })
    return programs


def _render_supervisor_program_conf(uid: int, username: str, prog: Dict[str, Any]) -> Tuple[str, str]:
    slug = prog['slug']
    prog_name = f"uniselv-{int(uid)}-{slug}" if 'laravel-worker' in slug else f"uniselv-{int(uid)}-laravel-worker-{slug}"
    numprocs = int(prog.get('numprocs', 1) or 1)
    lines = [
        f'[program:{prog_name}]',
        'process_name=%(program_name)s_%(process_num)02d' if numprocs > 1 else 'process_name=%(program_name)s',
        f"directory={prog['app_path']}",
        f"command={prog['command']}",
        'autostart=true',
        'autorestart=true',
        'stopasgroup=true',
        'killasgroup=true',
        f'user={username}',
        f'numprocs={numprocs}',
        'redirect_stderr=true',
        f"stdout_logfile={prog['stdout_logfile']}",
        f"stopwaitsecs={int(prog.get('stopwaitsecs', 3600) or 3600)}",
        '',
    ]
    return prog_name, '\n'.join(lines)


def sync_user_supervisor_scope(
    collector: Any, db_path: str, username: str, restart_programs: bool = False
) -> Dict[str, Any]:
    """Sync isolated per-user Supervisor drop-ins and read-only status sudoers safely."""
    username = str(username or '').strip()
    users = collector.get_webuzo_users() if collector else {}
    if username not in users:
        return {'success': False, 'error': f'Account {username} not found'}
    uinfo = users[username]
    uid = int(uinfo.get('uid', 0) or 0)
    _, gid, home_dir = _resolve_user_ids(username, uid)

    settings = load_platform_settings(db_path)
    perms = get_user_platform_permissions(db_path, username)
    sup_status = get_supervisor_status()
    budget = compute_laravel_service_budget(collector, username, db_path)

    allowed = (
        settings.get('platform_supervisor_enabled', '1') != '0'
        and perms.get('platform_supervisor', False)
        and sup_status.get('installed', False)
        and sup_status.get('runtime_active', False)
    )
    if not allowed:
        cleaned = _cleanup_user_supervisor_artifacts(username, uid)
        return {'success': False, 'error': 'Supervisor is disabled globally, stopped, or not permitted for this account', **cleaned}

    dropin_dir = pathlib.Path(home_dir) / '.uniselv-supervisor' / 'conf.d'
    programs_by_slug: Dict[str, Dict[str, Any]] = {}
    if dropin_dir.is_dir():
        for cf in sorted(dropin_dir.glob('*.conf')):
            if cf.is_symlink():
                continue
            for p in _parse_user_supervisor_dropin(cf, username, home_dir, budget['max_queue_workers'], require_artisan=True):
                programs_by_slug[p['slug']] = p

    # Also bridge any enabled queue service registered in managed_app_services when no explicit drop-in overrides it
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            "SELECT * FROM managed_app_services WHERE username = ? AND service_type = 'queue' AND enabled = 1",
            (username,),
        ).fetchall()
    finally:
        conn.close()

    dropin_app_paths = {p['app_path'] for p in programs_by_slug.values()}
    systemd_units_to_pause: List[str] = []
    for r in rows:
        svc = dict(r)
        systemd_units_to_pause.append(svc['unit_name'])
        if svc['app_path'] in dropin_app_paths:
            continue
        st_logs = pathlib.Path(svc['app_path']) / 'storage' / 'logs'
        log_path = (st_logs / 'worker.log') if st_logs.is_dir() else (pathlib.Path(home_dir) / '.uniselv-logs' / f"{svc['service_slug']}.log")
        safe_q = re.sub(r'[^a-zA-Z0-9_,:-]', '', svc.get('queues') or 'default') or 'default'
        programs_by_slug[svc['service_slug']] = {
            'slug': svc['service_slug'],
            'app_path': svc['app_path'],
            'command': f"{svc['runtime_bin']} {svc['app_path']}/artisan queue:work --queue={safe_q} --sleep=3 --tries=3 --max-time=3600 --memory={svc['max_memory_mb']}",
            'numprocs': max(1, min(budget['max_queue_workers'], int(svc['workers'] or 1))),
            'stdout_logfile': str(log_path),
            'stopwaitsecs': 3600,
        }

    synced_names: List[str] = []
    if os.name != 'nt':
        sup_home = pathlib.Path(home_dir) / '.uniselv-supervisor'
        dropin_dir.mkdir(parents=True, exist_ok=True)
        for d in (sup_home, dropin_dir):
            os.chmod(d, 0o750)
            if uid > 0:
                os.chown(d, uid, gid)

        _install_supervisor_sync_cli()
        ctl_bin = _find_supervisorctl_bin() or '/usr/bin/supervisorctl'
        sudo_line = f'{username} ALL=(root) NOPASSWD: {ctl_bin} status, /usr/local/bin/uniselv-supervisor-sync\n'
        sfile = _sup_sudoers_path(uid)
        _atomic_write_text(sfile, sudo_line, mode=0o440)
        if shutil.which('visudo'):
            chk = subprocess.run(['visudo', '-cf', str(sfile)], capture_output=True, text=True, timeout=6)
            if chk.returncode != 0:
                sfile.unlink(missing_ok=True)
                return {'success': False, 'error': f'Sudoers validation failed: {chk.stderr or chk.stdout}'}

        # Pause systemd units superseded by Supervisor so workers never duplicate
        for u in systemd_units_to_pause:
            subprocess.run(['systemctl', 'stop', u], capture_output=True, text=True, timeout=15)
            subprocess.run(['systemctl', 'disable', u], capture_output=True, text=True, timeout=15)

        SUPERVISOR_CONF_DIR.mkdir(parents=True, exist_ok=True)
        desired_files = set()
        for prog in programs_by_slug.values():
            log_p = pathlib.Path(prog['stdout_logfile'])
            log_p.parent.mkdir(parents=True, exist_ok=True)
            if not log_p.exists():
                log_p.touch()
                os.chmod(log_p, 0o640)
            if uid > 0:
                os.chown(log_p, uid, gid)
            prog_name, conf_body = _render_supervisor_program_conf(uid, username, prog)
            fname = f'uniselv-{int(uid)}-{_slugify(prog["slug"], "worker")}.conf'
            desired_files.add(fname)
            synced_names.append(prog_name)
            _atomic_write_text(SUPERVISOR_CONF_DIR / fname, conf_body, mode=0o644)

        for existing in SUPERVISOR_CONF_DIR.glob(f'uniselv-{int(uid)}-*.conf'):
            if existing.name not in desired_files:
                existing.unlink(missing_ok=True)

        subprocess.run([ctl_bin, 'reread'], capture_output=True, text=True, timeout=10)
        subprocess.run([ctl_bin, 'update'], capture_output=True, text=True, timeout=15)
        for pn in synced_names:
            subprocess.run([ctl_bin, 'restart' if restart_programs else 'start', f'{pn}:*'], capture_output=True, text=True, timeout=15)

    return {'success': True, 'username': username, 'dropin_dir': str(dropin_dir), 'programs': synced_names}


def control_supervisor_service(collector: Any, db_path: str, actor: str, operation: str) -> Dict[str, Any]:
    """Admin lifecycle control for global Supervisor daemon (start/stop/restart/enable/disable/test)."""
    op = str(operation or '').strip().lower()
    if op not in ('status', 'start', 'stop', 'restart', 'enable', 'disable', 'test'):
        return {'success': False, 'error': 'Invalid supervisor operation'}
    if op == 'status':
        return {'success': True, 'supervisor': get_supervisor_status()}

    st_before = get_supervisor_status()
    if not st_before.get('installed') and op != 'test':
        return {'success': False, 'error': 'Supervisor is not installed on this server yet. Click Install Supervisor first.'}

    if op == 'test':
        steps: List[Dict[str, Any]] = []
        steps.append({'name': 'sup_bins', 'label': 'Supervisor Binaries Installed', 'passed': st_before['installed'], 'detail': st_before.get('supervisorctl_bin') or 'Missing supervisord/supervisorctl'})
        steps.append({'name': 'sup_systemd', 'label': f"Daemon Active ({st_before.get('unit_name')})", 'passed': st_before.get('runtime_active', False), 'detail': f"state={st_before.get('active_state')}, pid={st_before.get('main_pid')}"})
        ctl_ok = False
        ctl_detail = 'Daemon stopped'
        if st_before.get('runtime_active') and st_before.get('supervisorctl_bin') and os.name != 'nt':
            r = subprocess.run([st_before['supervisorctl_bin'], 'status'], capture_output=True, text=True, timeout=6)
            ctl_ok = (r.returncode in (0, 3))
            ctl_detail = (r.stdout or r.stderr or 'Ready').strip()[:180] or 'Connected cleanly (0 programs)'
        steps.append({'name': 'sup_ctl', 'label': 'supervisorctl Socket Health', 'passed': ctl_ok, 'detail': ctl_detail})
        return {'success': True, 'all_passed': all(s['passed'] for s in steps), 'steps': steps, 'supervisor': st_before}

    unit = st_before['unit_name']
    if os.name != 'nt':
        if op in ('start', 'restart'):
            subprocess.run(['systemctl', op, unit], capture_output=True, text=True, timeout=20)
            _install_supervisor_sync_cli()
        elif op == 'stop':
            subprocess.run(['systemctl', 'stop', unit], capture_output=True, text=True, timeout=20)
        elif op == 'enable':
            subprocess.run(['systemctl', 'enable', '--now', unit], capture_output=True, text=True, timeout=20)
            _install_supervisor_sync_cli()
        elif op == 'disable':
            subprocess.run(['systemctl', 'disable', '--now', unit], capture_output=True, text=True, timeout=20)

    if op in ('enable', 'disable') and db_path and os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        try:
            conn.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', ('platform_supervisor_enabled', '1' if op == 'enable' else '0'))
            conn.commit()
        finally:
            conn.close()

    enforce_platform_permissions(collector, db_path)
    st_after = get_supervisor_status()
    _record_audit(db_path, actor, f'platform_supervisor_{op}', 'supervisor', {'active_state': st_after.get('active_state')})
    return {'success': True, 'supervisor': st_after}


def enforce_platform_permissions(collector: Any, db_path: str, target_user: Optional[str] = None) -> Dict[str, Any]:
    """Stop any managed Laravel services and Supervisor scopes revoked by global policy or per-user permissions."""
    if not db_path or not os.path.exists(db_path):
        return {'stopped_units': [], 'synced_supervisor': []}
    settings = load_platform_settings(db_path)
    users = collector.get_webuzo_users() if collector else {}
    globally_on = settings.get('platform_laravel_services_enabled', '1') != '0'
    allowed_types = set(parse_allowed_laravel_types(settings.get('platform_laravel_allowed_types', 'queue,horizon,reverb,scheduler')))
    sup_on = (settings.get('platform_supervisor_enabled', '1') != '0') and get_supervisor_status().get('runtime_active', False)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        if target_user:
            rows = conn.execute('SELECT * FROM managed_app_services WHERE username = ?', (target_user,)).fetchall()
        else:
            rows = conn.execute('SELECT * FROM managed_app_services').fetchall()
        stopped_units: List[str] = []
        for r in rows:
            svc = dict(r)
            perms = get_user_platform_permissions(db_path, svc['username'])
            perm_key = f"platform_laravel_{svc['service_type']}"
            svc_allowed = globally_on and (svc['service_type'] in allowed_types) and perms.get(perm_key, True)
            if not svc_allowed and svc['enabled']:
                if os.name != 'nt':
                    subprocess.run(['systemctl', 'disable', '--now', svc['unit_name']], capture_output=True, text=True, timeout=15)
                conn.execute("UPDATE managed_app_services SET enabled = 0, last_status = 'revoked', updated_at = ? WHERE id = ?", (int(time.time()), svc['id']))
                stopped_units.append(svc['unit_name'])
        conn.commit()
    finally:
        conn.close()

    synced_sup: List[str] = []
    check_users = [target_user] if (target_user and target_user in users) else sorted(users.keys())
    for u in check_users:
        perms = get_user_platform_permissions(db_path, u)
        uid = int(users[u].get('uid', 0) or 0)
        if sup_on and perms.get('platform_supervisor', False) and globally_on and ('queue' in allowed_types) and perms.get('platform_laravel_queue', True):
            res = sync_user_supervisor_scope(collector, db_path, u)
            if res.get('success'):
                synced_sup.append(u)
        else:
            _cleanup_user_supervisor_artifacts(u, uid)
            # Re-enable any enabled systemd queue service that fell out of Supervisor mode if queue is still permitted
            if globally_on and ('queue' in allowed_types) and perms.get('platform_laravel_queue', True) and os.name != 'nt':
                c2 = sqlite3.connect(db_path)
                c2.row_factory = sqlite3.Row
                try:
                    qrows = c2.execute("SELECT unit_name FROM managed_app_services WHERE username = ? AND service_type = 'queue' AND enabled = 1", (u,)).fetchall()
                    for qr in qrows:
                        subprocess.run(['systemctl', 'enable', '--now', qr['unit_name']], capture_output=True, text=True, timeout=15)
                finally:
                    c2.close()

    return {'stopped_units': stopped_units, 'synced_supervisor': synced_sup}


def compute_laravel_service_budget(collector: Any, username: str, db_path: str) -> Dict[str, Any]:
    settings = load_platform_settings(db_path)
    users = collector.get_webuzo_users() if collector else {}
    uinfo = users.get(username, {})
    uid = int(uinfo.get('uid', 0) or 0)
    plan_name = str(uinfo.get('plan_name', 'default') or 'default')
    limits = collector.get_user_limits(uid, plan_name) if collector else {}
    cpuquota = int(limits.get('cpuquota', 100) or 100)
    mem_bytes = int(limits.get('mem_max', 512 * 1024 * 1024) or (512 * 1024 * 1024))
    maxtask = int(limits.get('maxtask', 64) or 64)

    mem_mib = max(128, mem_bytes // (1024 * 1024))
    global_cap = max(1, min(16, int(settings.get('platform_laravel_max_workers_cap', '4') or 4)))
    services_enabled = str(settings.get('platform_laravel_services_enabled', '1')) != '0'
    allowed_types = parse_allowed_laravel_types(settings.get('platform_laravel_allowed_types', 'queue,horizon,reverb,scheduler'))
    sup_enabled_global = str(settings.get('platform_supervisor_enabled', '1')) != '0'
    sup_status = get_supervisor_status()
    user_perms = get_user_platform_permissions(db_path, username)
    by_cpu = max(1, cpuquota // 100)
    by_ram = max(1, (mem_mib - 256) // 256) if mem_mib >= 512 else 1
    by_task = max(1, maxtask // 32)
    max_workers = max(1, min(global_cap, by_cpu, by_ram, by_task))
    max_mem_per_worker = max(128, min(512, mem_mib // max(2, max_workers + 1)))

    eff_types = [t for t in allowed_types if user_perms.get(f'platform_laravel_{t}', True)]
    return {
        'success': True,
        'username': username,
        'uid': uid,
        'plan_name': plan_name,
        'expected_slice': f'golden-{uid}.slice' if uid > 0 else 'golden.slice',
        'cpuquota': cpuquota,
        'mem_max_mib': mem_mib,
        'maxtask': maxtask,
        'services_globally_enabled': services_enabled,
        'allowed_service_types': eff_types,
        'global_allowed_service_types': allowed_types,
        'user_permissions': user_perms,
        'supervisor_globally_enabled': sup_enabled_global,
        'supervisor_installed': sup_status.get('installed', False),
        'supervisor_active': sup_status.get('runtime_active', False),
        'supervisor_allowed': sup_enabled_global and user_perms.get('platform_supervisor', False),
        'max_queue_workers': max_workers,
        'max_worker_memory_mb': max_mem_per_worker,
        'queue_allowed': services_enabled and ('queue' in allowed_types) and user_perms.get('platform_laravel_queue', True),
        'horizon_allowed': services_enabled and ('horizon' in allowed_types) and user_perms.get('platform_laravel_horizon', True) and (mem_mib >= 512),
        'reverb_allowed': services_enabled and ('reverb' in allowed_types) and user_perms.get('platform_laravel_reverb', True) and (mem_mib >= 512),
        'scheduler_allowed': services_enabled and ('scheduler' in allowed_types) and user_perms.get('platform_laravel_scheduler', True),
    }


def _slugify(val: str, fallback: str = 'app') -> str:
    clean = re.sub(r'[^a-z0-9_-]+', '-', str(val or '').lower()).strip('-_')
    return clean[:28] or fallback


def _service_unit_path(unit_name: str) -> pathlib.Path:
    return SYSTEMD_DIR / unit_name


def _query_systemd_unit(unit_name: str) -> Dict[str, Any]:
    res = {'active_state': 'inactive', 'sub_state': 'dead', 'main_pid': 0, 'slice': '', 'enabled': False}
    if os.name == 'nt' or not shutil.which('systemctl'):
        return res
    try:
        r = subprocess.run(
            ['systemctl', 'show', unit_name, '--property=ActiveState,SubState,MainPID,Slice,UnitFileState'],
            capture_output=True, text=True, timeout=4,
        )
        if r.returncode == 0:
            for ln in r.stdout.splitlines():
                if '=' not in ln:
                    continue
                k, v = ln.split('=', 1)
                if k == 'ActiveState':
                    res['active_state'] = v.strip()
                elif k == 'SubState':
                    res['sub_state'] = v.strip()
                elif k == 'MainPID':
                    res['main_pid'] = int(v.strip() or 0)
                elif k == 'Slice':
                    res['slice'] = v.strip()
                elif k == 'UnitFileState':
                    res['enabled'] = v.strip() in ('enabled', 'enabled-runtime')
    except Exception:
        pass
    return res


def _build_laravel_exec_command(service_type: str, php_bin: str, queues: str, workers: int, mem_mb: int, port: int) -> str:
    if service_type == 'horizon':
        return f'{php_bin} artisan horizon'
    if service_type == 'reverb':
        return f'{php_bin} artisan reverb:start --host=127.0.0.1 --port={port}'
    if service_type == 'scheduler':
        return f'{php_bin} artisan schedule:work'
    # queue worker (if multiple workers requested, spawn supervised worker processes inside the same unit or 1 worker directly)
    safe_q = re.sub(r'[^a-zA-Z0-9_,:-]', '', queues or 'default') or 'default'
    if workers <= 1:
        return f'{php_bin} artisan queue:work --queue={safe_q} --sleep=3 --tries=3 --max-time=3600 --memory={mem_mb}'
    loop_cmd = (
        f'for i in $(seq 1 {int(workers)}); do '
        f'{php_bin} artisan queue:work --queue={safe_q} --sleep=3 --tries=3 --max-time=3600 --memory={mem_mb} & '
        f'done; wait'
    )
    return f'/bin/bash -lc {json.dumps(loop_cmd)}'


def _render_laravel_systemd_unit(
    username: str,
    group_name: str,
    uid: int,
    service_type: str,
    slug: str,
    app_path: str,
    exec_start: str,
    log_file: str,
) -> str:
    slice_name = f'golden-{uid}.slice' if uid > 0 else 'golden.slice'
    return (
        f'[Unit]\n'
        f'Description=UNISELV Managed Laravel {service_type} ({username}/{slug})\n'
        f'After=network.target golden-shield.service\n\n'
        f'[Service]\n'
        f'Type=simple\n'
        f'User={username}\n'
        f'Group={group_name}\n'
        f'Slice={slice_name}\n'
        f'WorkingDirectory={app_path}\n'
        f'ExecStart={exec_start}\n'
        f'StandardOutput=append:{log_file}\n'
        f'StandardError=append:{log_file}\n'
        f'Restart=always\n'
        f'RestartSec=5\n'
        f'TimeoutStopSec=20\n'
        f'NoNewPrivileges=yes\n'
        f'PrivateTmp=yes\n\n'
        f'[Install]\n'
        f'WantedBy=multi-user.target\n'
    )


def _query_supervisor_program(uid: int, slug: str, app_path: str = '') -> Dict[str, Any]:
    """Query Supervisor program status for a user's managed Laravel service if configured."""
    res = {'managed': False, 'active_state': 'inactive', 'sub_state': 'dead', 'main_pid': 0, 'slice': '', 'program_name': ''}
    conf_cand = SUPERVISOR_CONF_DIR / f'uniselv-{int(uid)}-{_slugify(slug, "worker")}.conf'
    if os.name == 'nt':
        return res
    ctl = _find_supervisorctl_bin()
    if not ctl:
        return res
    # Also detect project drop-in generated conf matching same app_path (e.g. uniselv-<uid>-laravel-worker.conf)
    if not conf_cand.is_file() and SUPERVISOR_CONF_DIR.is_dir():
        for cf in sorted(SUPERVISOR_CONF_DIR.glob(f'uniselv-{int(uid)}-*.conf')):
            try:
                txt = cf.read_text(encoding='utf-8', errors='replace')
                if app_path and f'directory={app_path}' in txt:
                    conf_cand = cf
                    break
            except OSError:
                continue
    if not conf_cand.is_file():
        return res
    prog_name = ''
    try:
        for ln in conf_cand.read_text(encoding='utf-8', errors='replace').splitlines():
            if ln.startswith('[program:') and ln.endswith(']'):
                prog_name = ln[9:-1].strip()
                break
    except OSError:
        return res
    if not prog_name:
        return res
    res['managed'] = True
    res['program_name'] = prog_name
    try:
        r = subprocess.run([ctl, 'status'], capture_output=True, text=True, timeout=5)
        for ln in (r.stdout or '').splitlines():
            if ln.startswith(prog_name + ':') or ln.startswith(prog_name + ' '):
                parts = ln.split()
                st_tok = parts[1] if len(parts) >= 2 else ''
                if st_tok == 'RUNNING':
                    res['active_state'] = 'active'
                    res['sub_state'] = 'running'
                    res['slice'] = f'golden-{int(uid)}.slice (supervisor)'
                    m_pid = re.search(r'\bpid\s+(\d+)', ln)
                    if m_pid:
                        res['main_pid'] = int(m_pid.group(1))
                    break
                elif st_tok in ('STARTING', 'BACKOFF', 'STOPPED', 'FATAL', 'EXITED'):
                    res['active_state'] = 'failed' if st_tok in ('FATAL', 'BACKOFF') else 'inactive'
                    res['sub_state'] = st_tok.lower()
    except Exception:
        pass
    return res


def list_laravel_services(collector: Any, db_path: str, target_user: Optional[str] = None) -> Dict[str, Any]:
    users = collector.get_webuzo_users() if collector else {}
    apps_root = pathlib.Path('/usr/local/apps')
    available_php = []
    if apps_root.is_dir():
        available_php = sorted(
            p.parent.parent.name
            for p in apps_root.glob('php*/bin/php')
            if re.fullmatch(r'php\d{2,3}', p.parent.parent.name) and os.access(p, os.X_OK)
        )
    if not available_php:
        available_php = ['php84']

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        if target_user:
            rows = conn.execute('SELECT * FROM managed_app_services WHERE username = ? ORDER BY id DESC', (target_user,)).fetchall()
        else:
            rows = conn.execute('SELECT * FROM managed_app_services ORDER BY username ASC, id DESC').fetchall()
    finally:
        conn.close()

    services: List[Dict[str, Any]] = []
    seen_programs: set = set()
    for r in rows:
        d = dict(r)
        sup_st = _query_supervisor_program(d['uid'], d['service_slug'], d.get('app_path', '')) if d.get('service_type') == 'queue' else {'managed': False}
        if sup_st.get('managed'):
            d['runner'] = 'supervisor'
            d['program_name'] = sup_st['program_name']
            seen_programs.add(sup_st['program_name'])
            d['runtime_active'] = sup_st['active_state'] == 'active'
            d['active_state'] = sup_st['active_state']
            d['sub_state'] = sup_st['sub_state']
            d['main_pid'] = sup_st['main_pid']
            d['slice'] = sup_st['slice'] or f"golden-{d['uid']}.slice (supervisor)"
            d['systemd_enabled'] = bool(d.get('enabled'))
        else:
            st = _query_systemd_unit(d['unit_name'])
            d['runner'] = 'systemd'
            d['runtime_active'] = st['active_state'] == 'active'
            d['active_state'] = st['active_state']
            d['sub_state'] = st['sub_state']
            d['main_pid'] = st['main_pid']
            d['slice'] = st['slice']
            d['systemd_enabled'] = st['enabled']
        d['source'] = 'managed'
        services.append(d)

    # Also auto-discover project-configured Supervisor drop-ins (~/.uniselv-supervisor/conf.d/*.conf)
    check_users = [target_user] if (target_user and target_user in users) else sorted(users.keys())
    for u in check_users:
        uinfo = users.get(u, {})
        uid = int(uinfo.get('uid', 0) or 0)
        _, _, home_dir = _resolve_user_ids(u, uid)
        dropin_dir = pathlib.Path(home_dir) / '.uniselv-supervisor' / 'conf.d'
        if not dropin_dir.is_dir() or dropin_dir.is_symlink():
            continue
        for cf in sorted(dropin_dir.glob('*.conf')):
            if cf.is_symlink() or not cf.is_file():
                continue
            for prog in _parse_user_supervisor_dropin(cf, u, home_dir, 16):
                pslug = _slugify(prog.get('slug') or prog.get('name') or 'laravel-worker', 'laravel-worker')
                prog_app_dir = prog.get('app_path') or prog.get('directory') or ''
                rendered_slug = pslug if 'laravel-worker' in pslug else f'laravel-worker-{pslug}'
                full_prog = f'uniselv-{uid}-{rendered_slug}'
                if full_prog in seen_programs:
                    continue
                seen_programs.add(full_prog)
                sup_st = _query_supervisor_program(uid, rendered_slug, prog_app_dir)
                cmd_bin = (prog.get('command') or '').split()[0] if prog.get('command') else ''
                m_php_br = re.search(r'/(php\d{2,3})/', cmd_bin)

                # Check if the configured project directory and artisan file still exist
                is_dir_alive = bool(prog_app_dir and os.path.isdir(prog_app_dir))
                is_artisan_alive = bool(is_dir_alive and (pathlib.Path(prog_app_dir) / 'artisan').is_file())
                is_orphaned = not is_artisan_alive

                active_st = sup_st.get('active_state') or ('inactive' if not sup_st.get('managed') else 'active')
                if is_orphaned:
                    active_st = 'orphaned'

                services.append({
                    'id': f'dropin:{u}:{pslug}',
                    'source': 'project_dropin',
                    'username': u,
                    'uid': uid,
                    'service_type': 'queue',
                    'service_slug': prog.get('slug') or pslug,
                    'app_path': prog_app_dir or home_dir,
                    'php_branch': m_php_br.group(1) if m_php_br else 'project',
                    'runtime_bin': cmd_bin,
                    'workers': int(prog.get('numprocs', 1) or 1),
                    'queues': 'project-configured',
                    'port': 0,
                    'enabled': 1,
                    'runner': 'supervisor',
                    'program_name': sup_st.get('program_name') or full_prog,
                    'runtime_active': (sup_st.get('active_state') == 'active') and not is_orphaned,
                    'active_state': active_st,
                    'sub_state': 'missing project' if is_orphaned else (sup_st.get('sub_state') or ''),
                    'main_pid': 0 if is_orphaned else (sup_st.get('main_pid') or 0),
                    'slice': sup_st.get('slice') or f'golden-{uid}.slice (supervisor)',
                    'systemd_enabled': True,
                    'stdout_logfile': prog.get('stdout_logfile', ''),
                    'orphaned': is_orphaned,
                    'conf_file': str(cf),
                })

    discovered = discover_laravel_apps(target_user, available_php=available_php) if target_user else []
    budget = compute_laravel_service_budget(collector, target_user, db_path) if target_user else None
    ports = ensure_account_port_allocation(collector, db_path, target_user) if target_user else None

    return {
        'success': True,
        'services': services,
        'discovered_apps': discovered,
        'budget': budget,
        'port_allocation': ports,
        'php_branches': available_php,
        'accounts': sorted(users.keys()),
        'supervisor': get_supervisor_status(),
    }


def save_and_install_laravel_service(collector: Any, db_path: str, actor: str, params: Dict[str, Any]) -> Dict[str, Any]:
    username = str(params.get('username') or '').strip()
    if not username or not re.fullmatch(r'[a-z_][a-z0-9_-]{0,31}', username):
        return {'success': False, 'error': 'Invalid account username'}
    users = collector.get_webuzo_users() if collector else {}
    if username not in users:
        return {'success': False, 'error': f'Account {username} not found'}

    svc_type = str(params.get('service_type') or 'queue').strip().lower()
    if svc_type not in SERVICE_TYPES:
        return {'success': False, 'error': f'Invalid service_type: {svc_type}'}

    budget = compute_laravel_service_budget(collector, username, db_path)
    if not budget.get('services_globally_enabled'):
        return {'success': False, 'error': 'Managed Laravel Services are globally disabled by the server administrator'}
    if svc_type not in (budget.get('global_allowed_service_types') or []):
        return {'success': False, 'error': f'Laravel {svc_type.title()} service is globally disabled by administrator policy'}
    if not budget.get('user_permissions', {}).get(f'platform_laravel_{svc_type}', True):
        return {'success': False, 'error': f'Laravel {svc_type.title()} permission is disabled for account {username} by the administrator'}
    if svc_type in ('horizon', 'reverb') and budget.get('mem_max_mib', 0) < 512:
        return {'success': False, 'error': f'Laravel {svc_type.title()} requires at least 512 MiB plan RAM'}

    raw_path = str(params.get('app_path') or '').strip()
    safe_path = _safe_home_subpath(username, raw_path)
    if not safe_path or not (safe_path / 'artisan').is_file():
        return {'success': False, 'error': 'app_path must be a valid Laravel project directory containing artisan inside account home'}
    uid = budget['uid']
    _, gid, home_dir = _resolve_user_ids(username, uid)
    group_name = username
    if grp is not None and hasattr(grp, 'getgrgid') and gid:
        try:
            gr = grp.getgrgid(gid)
            if gr is not None:
                group_name = gr.gr_name
        except KeyError:
            group_name = username

    php_branch = str(params.get('php_branch') or 'php84').strip()
    if not re.fullmatch(r'php\d{2,3}', php_branch):
        return {'success': False, 'error': 'Invalid php_branch'}
    php_bin = f'/usr/local/apps/{php_branch}/bin/php'
    if os.name != 'nt' and not (os.path.isfile(php_bin) and os.access(php_bin, os.X_OK)):
        return {'success': False, 'error': f'PHP binary not found at {php_bin}'}

    workers = max(1, min(budget['max_queue_workers'], int(params.get('workers') or 1)))
    if svc_type in ('horizon', 'reverb', 'scheduler'):
        workers = 1
    mem_mb = max(128, min(budget['max_worker_memory_mb'], int(params.get('max_memory_mb') or budget['max_worker_memory_mb'])))
    queues = re.sub(r'[^a-zA-Z0-9_,:-]', '', str(params.get('queues') or 'default')) or 'default'
    enable_now = str(params.get('enabled', '1')) not in ('0', 'false', 'False')

    alloc = ensure_account_port_allocation(collector, db_path, username)
    port = alloc['ports']['reverb_port'] if svc_type == 'reverb' else 0

    rel_tag = _slugify(str(safe_path.name), 'app')
    slug = _slugify(params.get('service_slug') or f'{svc_type}-{rel_tag}', svc_type)
    unit_name = f'uniselv-lrv-{uid}-{slug}.service'
    log_dir = pathlib.Path(home_dir) / '.uniselv-logs'
    log_file = log_dir / f'{slug}.log'

    use_supervisor = (
        svc_type == 'queue'
        and budget.get('supervisor_allowed', False)
        and budget.get('supervisor_active', False)
    )

    exec_cmd = _build_laravel_exec_command(svc_type, php_bin, queues, workers, mem_mb, port)
    unit_body = _render_laravel_systemd_unit(username, group_name, uid, svc_type, slug, str(safe_path), exec_cmd, str(log_file))

    if os.name != 'nt' and not use_supervisor:
        try:
            log_dir.mkdir(parents=True, exist_ok=True)
            os.chmod(log_dir, 0o750)
            if uid > 0:
                os.chown(log_dir, uid, gid)
            if not log_file.exists():
                log_file.touch()
                os.chmod(log_file, 0o640)
                if uid > 0:
                    os.chown(log_file, uid, gid)
            _atomic_write_text(_service_unit_path(unit_name), unit_body, mode=0o644)
            subprocess.run(['systemctl', 'daemon-reload'], capture_output=True, text=True, timeout=15)
            if enable_now:
                subprocess.run(['systemctl', 'enable', '--now', unit_name], capture_output=True, text=True, timeout=20)
            else:
                subprocess.run(['systemctl', 'disable', '--now', unit_name], capture_output=True, text=True, timeout=20)
        except Exception as exc:
            return {'success': False, 'error': f'Failed installing systemd service {unit_name}: {exc}'}

    st = _query_systemd_unit(unit_name)
    now = int(time.time())
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            """INSERT INTO managed_app_services
               (username, uid, service_type, service_slug, app_path, php_branch, runtime_bin, workers, max_memory_mb, queues, port, enabled, unit_name, last_status, last_error, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '', ?, ?)
               ON CONFLICT(username, service_slug) DO UPDATE SET
                 service_type=excluded.service_type, app_path=excluded.app_path, php_branch=excluded.php_branch,
                 runtime_bin=excluded.runtime_bin, workers=excluded.workers, max_memory_mb=excluded.max_memory_mb,
                 queues=excluded.queues, port=excluded.port, enabled=excluded.enabled, unit_name=excluded.unit_name,
                 last_status=excluded.last_status, updated_at=excluded.updated_at""",
            (username, uid, svc_type, slug, str(safe_path), php_branch, php_bin, workers, mem_mb, queues, port, 1 if enable_now else 0, unit_name, st['active_state'], now, now),
        )
        conn.commit()
    finally:
        conn.close()

    if use_supervisor:
        sync_user_supervisor_scope(collector, db_path, username, restart_programs=enable_now)
        sup_st = _query_supervisor_program(uid, slug, str(safe_path))
        active_state = sup_st.get('active_state', 'inactive')
        slice_label = sup_st.get('slice') or f'golden-{uid}.slice (supervisor)'
    else:
        active_state = st['active_state']
        slice_label = st['slice']

    _record_audit(db_path, actor, 'platform_laravel_service_install', username, {'unit': unit_name, 'type': svc_type, 'workers': workers, 'port': port, 'enabled': enable_now, 'runner': 'supervisor' if use_supervisor else 'systemd'})
    return {'success': True, 'username': username, 'unit_name': unit_name, 'port': port, 'active_state': active_state, 'slice': slice_label, 'runner': 'supervisor' if use_supervisor else 'systemd'}


def control_laravel_service(db_path: str, actor: str, username: str, service_id: Any, operation: str, is_admin: bool = False) -> Dict[str, Any]:
    op = str(operation or '').strip().lower()
    if op not in ('start', 'stop', 'restart', 'enable', 'disable', 'uninstall', 'test', 'logs'):
        return {'success': False, 'error': 'Invalid service operation'}

    if isinstance(service_id, str) and service_id.startswith('dropin:'):
        parts = service_id.split(':', 2)
        if len(parts) != 3 or not re.fullmatch(r'[a-z_][a-z0-9_-]{0,31}', parts[1]) or not re.fullmatch(r'[a-z0-9_-]{1,40}', parts[2]):
            return {'success': False, 'error': 'Invalid project drop-in service identifier'}
        du, pslug = parts[1], parts[2]
        if not is_admin and du != username:
            return {'error': 'Forbidden: Account scope mismatch', 'status_code': 403}
        uid, _, home_dir = _resolve_user_ids(du, 0)
        if not uid and pwd is not None:
            try:
                uid = pwd.getpwnam(du).pw_uid
            except KeyError:
                pass
        rendered_slug = pslug if 'laravel-worker' in pslug else f'laravel-worker-{pslug}'
        app_dir = home_dir
        log_candidates = [pathlib.Path(home_dir) / '.uniselv-logs' / f'{pslug}.log']
        dropin_dir = pathlib.Path(home_dir) / '.uniselv-supervisor' / 'conf.d'
        matched_conf_file = None
        if dropin_dir.is_dir():
            for cf in sorted(dropin_dir.glob('*.conf')):
                if cf.is_symlink() or not cf.is_file():
                    continue
                for pr in _parse_user_supervisor_dropin(cf, du, home_dir, 16):
                    pr_slug = _slugify(pr.get('slug') or pr.get('name') or 'laravel-worker', 'laravel-worker')
                    if pr_slug == pslug:
                        matched_conf_file = cf
                        if pr.get('app_path') or pr.get('directory'):
                            app_dir = pr.get('app_path') or pr.get('directory')
                        if pr.get('stdout_logfile'):
                            log_candidates.insert(0, pathlib.Path(pr['stdout_logfile']))
                        break
                if matched_conf_file:
                    break
        sup_st = _query_supervisor_program(uid, rendered_slug, app_dir if app_dir != home_dir else '')
        pname = sup_st.get('program_name') or f'uniselv-{uid}-{rendered_slug}'
        if op == 'logs':
            log_file = next((p for p in log_candidates if p.is_file() and not p.is_symlink()), log_candidates[0])
            lines = []
            if log_file.is_file() and not log_file.is_symlink():
                with open(log_file, 'rb') as f:
                    f.seek(0, os.SEEK_END)
                    size = f.tell()
                    f.seek(max(0, size - 32768))
                    lines = f.read().decode('utf-8', errors='replace').splitlines()[-80:]
            return {'success': True, 'service_id': service_id, 'unit_name': pname, 'log_path': str(log_file), 'lines': lines}
        if op == 'test':
            app_p = pathlib.Path(app_dir)
            steps = [
                {'name': 'artisan_exists', 'label': 'Laravel Project Directory', 'passed': (app_p / 'artisan').is_file(), 'detail': str(app_p)},
                {'name': 'env_exists', 'label': 'Environment (.env) File Check', 'passed': (app_p / '.env').is_file(), 'detail': 'Found .env' if (app_p / '.env').is_file() else 'Missing .env'},
                {'name': 'supervisor_running', 'label': f'Supervisor Program ({pname})', 'passed': sup_st.get('active_state') == 'active', 'detail': f"state={sup_st.get('active_state')}, sub={sup_st.get('sub_state')}, pid={sup_st.get('main_pid')}, user={du}"},
            ]
            return {'success': True, 'service_id': service_id, 'unit_name': pname, 'all_passed': all(s['passed'] for s in steps), 'steps': steps}
        if op in ('start', 'stop', 'restart'):
            if sup_st.get('managed'):
                _run_supervisorctl([op, f'{pname}:*'], timeout=20)
            return {'success': True, 'service_id': service_id, 'operation': op, 'unit_name': pname}
        if op in ('uninstall', 'remove', 'purge'):
            if sup_st.get('managed'):
                _run_supervisorctl(['stop', f'{pname}:*'], timeout=20)

            removed_files = []
            if matched_conf_file and matched_conf_file.is_file():
                try:
                    matched_conf_file.unlink()
                    removed_files.append(str(matched_conf_file))
                except Exception as ex:
                    return {'success': False, 'error': f'Failed to remove drop-in configuration: {ex}'}
            elif dropin_dir.is_dir():
                for cf in sorted(dropin_dir.glob('*.conf')):
                    if cf.stem == pslug or cf.stem == f'laravel-worker-{pslug}' or cf.stem == 'laravel-worker':
                        try:
                            cf.unlink()
                            removed_files.append(str(cf))
                        except Exception as ex:
                            return {'success': False, 'error': f'Failed to remove drop-in configuration: {ex}'}

            _run_supervisorctl(['reread'], timeout=20)
            _run_supervisorctl(['update'], timeout=20)

            _record_audit(db_path, actor, 'dropin_worker_removed', du, {
                'program_name': pname,
                'slug': pslug,
                'removed_files': removed_files,
            })
            return {
                'success': True,
                'service_id': service_id,
                'operation': op,
                'unit_name': pname,
                'uninstalled': True,
                'active_state': 'removed',
                'message': f'Supervisor worker [{pslug}] stopped and configuration removed.',
            }
        return {'success': False, 'error': 'Manage configuration changes inside your Laravel project settings'}

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute('SELECT * FROM managed_app_services WHERE id = ?', (int(service_id),)).fetchone()
        if not row:
            return {'success': False, 'error': 'Managed service not found'}
        svc = dict(row)
        if not is_admin and svc['username'] != username:
            return {'error': 'Forbidden: Account scope mismatch', 'status_code': 403}

        if not is_admin and op in ('start', 'restart', 'enable'):
            settings = load_platform_settings(db_path)
            perms = get_user_platform_permissions(db_path, svc['username'])
            allowed_types = set(parse_allowed_laravel_types(settings.get('platform_laravel_allowed_types', 'queue,horizon,reverb,scheduler')))
            if settings.get('platform_laravel_services_enabled', '1') == '0' or svc['service_type'] not in allowed_types or not perms.get(f"platform_laravel_{svc['service_type']}", True):
                return {'success': False, 'error': f"Laravel {svc['service_type'].title()} is disabled by your administrator"}

        unit = svc['unit_name']
        sup_st = _query_supervisor_program(svc['uid'], svc['service_slug'], svc.get('app_path', '')) if svc.get('service_type') == 'queue' else {'managed': False}
        is_sup = bool(sup_st.get('managed'))

        if op == 'logs':
            _, _, home_dir = _resolve_user_ids(svc['username'], svc['uid'])
            candidates = [pathlib.Path(home_dir) / '.uniselv-logs' / f"{svc['service_slug']}.log"]
            if is_sup:
                candidates.insert(0, pathlib.Path(svc['app_path']) / 'storage' / 'logs' / 'worker.log')
            log_file = next((p for p in candidates if p.is_file() and not p.is_symlink()), candidates[0])
            lines = []
            if log_file.is_file() and not log_file.is_symlink():
                with open(log_file, 'rb') as f:
                    f.seek(0, os.SEEK_END)
                    size = f.tell()
                    f.seek(max(0, size - 32768))
                    lines = f.read().decode('utf-8', errors='replace').splitlines()[-80:]
            return {'success': True, 'service_id': service_id, 'unit_name': sup_st.get('program_name') if is_sup else unit, 'log_path': str(log_file), 'lines': lines}

        if op == 'test':
            steps: List[Dict[str, Any]] = []
            app_p = pathlib.Path(svc['app_path'])
            steps.append({'name': 'artisan_exists', 'label': 'Laravel artisan & vendor Check', 'passed': (app_p / 'artisan').is_file() and (app_p / 'vendor' / 'autoload.php').is_file(), 'detail': str(app_p)})
            has_env = (app_p / '.env').is_file()
            steps.append({'name': 'env_exists', 'label': 'Environment (.env) File Check', 'passed': has_env, 'detail': 'Found .env' if has_env else 'Missing .env — complete installer or create .env so workers can boot cleanly'})
            if os.path.isfile(svc['runtime_bin']):
                r_art = subprocess.run([svc['runtime_bin'], 'artisan', '--version'], cwd=str(app_p), capture_output=True, text=True, timeout=8)
                steps.append({'name': 'artisan_exec', 'label': 'Artisan CLI Execution', 'passed': r_art.returncode == 0, 'detail': (r_art.stdout or r_art.stderr).strip()[:160]})
            if svc['service_type'] == 'horizon':
                has_h = (app_p / 'vendor' / 'laravel' / 'horizon').is_dir()
                steps.append({'name': 'horizon_pkg', 'label': 'laravel/horizon Package Installed', 'passed': has_h, 'detail': 'Installed' if has_h else 'Missing vendor/laravel/horizon'})
            elif svc['service_type'] == 'reverb':
                has_rv = (app_p / 'vendor' / 'laravel' / 'reverb').is_dir()
                steps.append({'name': 'reverb_pkg', 'label': 'laravel/reverb Package Installed', 'passed': has_rv, 'detail': f"Port {svc['port']} assigned"})
            if is_sup:
                sup_now = _query_supervisor_program(svc['uid'], svc['service_slug'], svc.get('app_path', ''))
                steps.append({
                    'name': 'supervisor_running',
                    'label': f"Supervisor Program Active ({sup_now.get('program_name')})",
                    'passed': sup_now.get('active_state') == 'active',
                    'detail': f"state={sup_now.get('active_state')}, sub={sup_now.get('sub_state')}, pid={sup_now.get('main_pid')}, user={svc['username']}",
                })
            else:
                st = _query_systemd_unit(unit)
                expected_sl = f"golden-{svc['uid']}.slice"
                running_ok = (st['active_state'] == 'active') and (st['slice'] == expected_sl)
                steps.append({'name': 'systemd_slice', 'label': f'Systemd Service Active & Bounded ({expected_sl})', 'passed': running_ok, 'detail': f"state={st['active_state']}, sub={st['sub_state']}, pid={st['main_pid']}, slice={st['slice'] or 'none'}"})
            return {'success': True, 'service_id': service_id, 'unit_name': sup_st.get('program_name') if is_sup else unit, 'all_passed': all(s['passed'] for s in steps), 'steps': steps}

        if os.name != 'nt':
            if is_sup:
                ctl = _find_supervisorctl_bin() or '/usr/bin/supervisorctl'
                pname = f"{sup_st['program_name']}:*"
                if op in ('start', 'stop', 'restart'):
                    subprocess.run([ctl, op, pname], capture_output=True, text=True, timeout=20)
                elif op == 'enable':
                    conn.execute('UPDATE managed_app_services SET enabled = 1, updated_at = ? WHERE id = ?', (int(time.time()), service_id))
                    subprocess.run([ctl, 'start', pname], capture_output=True, text=True, timeout=20)
                elif op == 'disable':
                    subprocess.run([ctl, 'stop', pname], capture_output=True, text=True, timeout=20)
                    conn.execute('UPDATE managed_app_services SET enabled = 0, updated_at = ? WHERE id = ?', (int(time.time()), service_id))
                elif op == 'uninstall':
                    expected_conf = f"uniselv-{int(svc['uid'])}-{_slugify(svc['service_slug'], 'worker')}.conf"
                    conf_path = SUPERVISOR_CONF_DIR / expected_conf
                    if conf_path.is_file():
                        subprocess.run([ctl, 'stop', pname], capture_output=True, text=True, timeout=20)
                        conf_path.unlink(missing_ok=True)
                        subprocess.run([ctl, 'reread'], capture_output=True, text=True, timeout=10)
                        subprocess.run([ctl, 'update'], capture_output=True, text=True, timeout=15)
                    conn.execute('DELETE FROM managed_app_services WHERE id = ?', (service_id,))
                    conn.commit()
                    _record_audit(db_path, actor, 'platform_laravel_service_uninstall', svc['username'], {'unit': sup_st['program_name']})
                    return {'success': True, 'uninstalled': True, 'unit_name': sup_st['program_name']}
            else:
                if op in ('start', 'stop', 'restart'):
                    subprocess.run(['systemctl', op, unit], capture_output=True, text=True, timeout=20)
                elif op == 'enable':
                    subprocess.run(['systemctl', 'enable', '--now', unit], capture_output=True, text=True, timeout=20)
                    conn.execute('UPDATE managed_app_services SET enabled = 1, updated_at = ? WHERE id = ?', (int(time.time()), service_id))
                elif op == 'disable':
                    subprocess.run(['systemctl', 'disable', '--now', unit], capture_output=True, text=True, timeout=20)
                    conn.execute('UPDATE managed_app_services SET enabled = 0, updated_at = ? WHERE id = ?', (int(time.time()), service_id))
                elif op == 'uninstall':
                    subprocess.run(['systemctl', 'disable', '--now', unit], capture_output=True, text=True, timeout=20)
                    ufile = _service_unit_path(unit)
                    if ufile.is_file():
                        ufile.unlink()
                    subprocess.run(['systemctl', 'daemon-reload'], capture_output=True, text=True, timeout=15)
                    conn.execute('DELETE FROM managed_app_services WHERE id = ?', (service_id,))
                    conn.commit()
                    _record_audit(db_path, actor, 'platform_laravel_service_uninstall', svc['username'], {'unit': unit})
                    return {'success': True, 'uninstalled': True, 'unit_name': unit}

        if is_sup:
            sup_now = _query_supervisor_program(svc['uid'], svc['service_slug'], svc.get('app_path', ''))
            act_state = sup_now['active_state']
            pid_val = sup_now['main_pid']
            sl_val = sup_now['slice']
        else:
            st = _query_systemd_unit(unit)
            act_state = st['active_state']
            pid_val = st['main_pid']
            sl_val = st['slice']
        conn.execute('UPDATE managed_app_services SET last_status = ?, updated_at = ? WHERE id = ?', (act_state, int(time.time()), service_id))
        conn.commit()
        _record_audit(db_path, actor, f'platform_laravel_service_{op}', svc['username'], {'unit': unit, 'active_state': act_state})
        return {'success': True, 'unit_name': sup_st.get('program_name') if is_sup else unit, 'active_state': act_state, 'main_pid': pid_val, 'slice': sl_val}
    finally:
        conn.close()


def sync_and_reconcile_laravel_workers(collector: Any, db_path: str, actor: str, target_user: str, auto_prune: bool = True, is_admin: bool = False) -> Dict[str, Any]:
    """Scan tenant Laravel applications, validate supervisor drop-in configs, prune orphaned configurations, and re-sync Supervisor."""
    target_user = str(target_user or '').strip()
    if not target_user or not re.fullmatch(r'[a-z_][a-z0-9_-]{0,31}', target_user):
        return {'success': False, 'error': 'Invalid target account username'}
    if not is_admin and actor != target_user:
        return {'error': 'Forbidden: Account scope mismatch', 'status_code': 403}

    users = collector.get_webuzo_users() if collector else {}
    uinfo = users.get(target_user, {})
    uid = int(uinfo.get('uid', 0) or 0)
    _, _, home_dir = _resolve_user_ids(target_user, uid)
    dropin_dir = pathlib.Path(home_dir) / '.uniselv-supervisor' / 'conf.d'

    pruned: List[Dict[str, Any]] = []
    orphaned: List[Dict[str, Any]] = []

    if dropin_dir.is_dir() and not dropin_dir.is_symlink():
        for cf in sorted(dropin_dir.glob('*.conf')):
            if cf.is_symlink() or not cf.is_file():
                continue
            progs = _parse_user_supervisor_dropin(cf, target_user, home_dir, 16)
            file_has_valid_prog = False
            for prog in progs:
                p_dir = prog.get('app_path') or prog.get('directory') or ''
                is_alive = bool(p_dir and os.path.isdir(p_dir) and (pathlib.Path(p_dir) / 'artisan').is_file())
                pslug = _slugify(prog.get('slug') or prog.get('name') or 'laravel-worker', 'laravel-worker')
                rendered_slug = pslug if 'laravel-worker' in pslug else f'laravel-worker-{pslug}'
                full_prog = f'uniselv-{uid}-{rendered_slug}'
                if not is_alive:
                    orphaned.append({'file': cf.name, 'slug': pslug, 'program': full_prog, 'path': p_dir})
                    if auto_prune:
                        _run_supervisorctl(['stop', f'{full_prog}:*'], timeout=15)
                else:
                    file_has_valid_prog = True

            if auto_prune and not file_has_valid_prog and orphaned:
                try:
                    cf.unlink()
                    pruned.extend([o for o in orphaned if o['file'] == cf.name])
                except Exception:
                    pass

        if auto_prune and pruned:
            _run_supervisorctl(['reread'], timeout=20)
            _run_supervisorctl(['update'], timeout=20)

    discovered = discover_laravel_apps(target_user)
    sync_res = sync_user_supervisor_scope(collector, db_path, target_user)

    _record_audit(db_path, actor, 'workers_scanned_and_synced', target_user, {
        'pruned_count': len(pruned),
        'discovered_count': len(discovered),
    })

    msg = f"Scan complete: {len(discovered)} active Laravel app(s) detected"
    if pruned:
        msg += f", {len(pruned)} orphaned worker config(s) pruned"
    else:
        msg += ", no orphaned workers found"

    return {
        'success': True,
        'username': target_user,
        'scanned_apps': len(discovered),
        'synced_count': len(discovered),
        'discovered_apps': discovered,
        'pruned_count': len(pruned),
        'pruned': pruned,
        'pruned_orphans': pruned,
        'supervisor_sync': sync_res,
        'message': msg + '.'
    }


def _read_crontab_lines(username: str) -> List[str]:
    if os.name == 'nt':
        return []
    try:
        r = subprocess.run(['crontab', '-u', username, '-l'], capture_output=True, text=True, timeout=10)
        return r.stdout.splitlines() if r.returncode == 0 else []
    except Exception:
        return []


def _write_crontab_lines(username: str, text: str) -> Tuple[bool, str]:
    if os.name == 'nt':
        return True, ''
    try:
        p = subprocess.run(['crontab', '-u', username, '-'], input=text, capture_output=True, text=True, timeout=10)
        return (p.returncode == 0), (p.stderr or p.stdout or '')
    except Exception as e:
        return False, str(e)


def manage_laravel_scheduler_cron(
    collector: Any, db_path: str, actor: str, username: str, app_path: str, php_branch: str = 'php84', operation: str = 'status', is_admin: bool = False
) -> Dict[str, Any]:
    """Inspect, install, or remove Laravel Scheduler (* * * * * artisan schedule:run) in user's Webuzo crontab safely and non-invasively."""
    username = str(username or '').strip()
    if not username or not re.fullmatch(r'[a-z_][a-z0-9_-]{0,31}', username):
        return {'success': False, 'error': 'Invalid username'}
    if not is_admin and actor != username:
        return {'error': 'Forbidden: Account scope mismatch', 'status_code': 403}

    users = collector.get_webuzo_users() if collector else {}
    if username not in users and actor != username:
        return {'success': False, 'error': f'Account {username} not found'}

    app_path = str(app_path or '').strip()
    safe_app = _safe_home_subpath(username, app_path)
    if not safe_app:
        return {'success': False, 'error': f'Invalid or escaping project path: {app_path}'}
    if not (safe_app / 'artisan').is_file():
        return {'success': False, 'error': f'artisan not found in {safe_app}'}

    if not re.fullmatch(r'php\d{2,3}', php_branch):
        php_branch = 'php84'
    php_cand = f'/usr/local/apps/{php_branch}/bin/php'
    php_bin = php_cand if os.path.isfile(php_cand) else ('/usr/bin/php' if os.path.isfile('/usr/bin/php') else 'php')

    tag_start = f'# BEGIN UNISELV SCHEDULER: {safe_app}'
    tag_end = f'# END UNISELV SCHEDULER: {safe_app}'
    cron_target_cmd = f'{php_bin} {safe_app}/artisan schedule:run >> /dev/null 2>&1'
    cron_line = f'* * * * * {cron_target_cmd}'

    current_lines = _read_crontab_lines(username)

    is_installed = False
    for line in current_lines:
        if tag_start in line or (f'{safe_app}/artisan' in line and 'schedule:run' in line):
            is_installed = True
            break

    if operation == 'status':
        return {
            'success': True,
            'username': username,
            'app_path': str(safe_app),
            'cron_installed': is_installed,
            'is_installed': is_installed,
            'cron_line': cron_line,
            'php_bin': php_bin,
        }

    if operation == 'install':
        filtered = []
        inside_block = False
        for line in current_lines:
            if tag_start in line:
                inside_block = True
                continue
            if inside_block and tag_end in line:
                inside_block = False
                continue
            if not inside_block:
                if f'{safe_app}/artisan' in line and 'schedule:run' in line:
                    continue
                filtered.append(line)

        filtered.append(tag_start)
        filtered.append(cron_line)
        filtered.append(tag_end)
        new_crontab = '\n'.join(filtered).strip() + '\n'

        ok, err_msg = _write_crontab_lines(username, new_crontab)
        if not ok:
            return {'success': False, 'error': f'Failed to write crontab: {err_msg}'}

        _record_audit(db_path, actor, 'scheduler_cron_installed', username, {
            'app_path': str(safe_app),
            'cron_line': cron_line,
        })
        return {
            'success': True,
            'username': username,
            'app_path': str(safe_app),
            'cron_installed': True,
            'is_installed': True,
            'cron_line': cron_line,
            'message': f'Laravel Scheduler cron installed for {safe_app.name}.',
        }

    if operation in ('remove', 'uninstall'):
        filtered = []
        inside_block = False
        for line in current_lines:
            if tag_start in line:
                inside_block = True
                continue
            if inside_block and tag_end in line:
                inside_block = False
                continue
            if not inside_block:
                if f'{safe_app}/artisan' in line and 'schedule:run' in line:
                    continue
                filtered.append(line)
        new_crontab = '\n'.join(filtered).strip() + '\n'

        ok, err_msg = _write_crontab_lines(username, new_crontab)
        if not ok:
            return {'success': False, 'error': f'Failed to write crontab: {err_msg}'}

        _record_audit(db_path, actor, 'scheduler_cron_removed', username, {'app_path': str(safe_app)})
        return {
            'success': True,
            'username': username,
            'app_path': str(safe_app),
            'cron_installed': False,
            'is_installed': False,
            'message': f'Laravel Scheduler cron removed for {safe_app.name}.',
        }

    return {'success': False, 'error': f'Unsupported cron operation: {operation}'}


def manage_reverb_vhost_proxy(
    collector: Any, db_path: str, actor: str, username: str, domain: str, port: int = 0, operation: str = 'status', is_admin: bool = False
) -> Dict[str, Any]:
    """Manage dedicated Apache/LiteSpeed reverse proxy include file for Laravel Reverb WebSocket in /usr/local/apps/apache2/etc/conf.d/."""
    username = str(username or '').strip()
    if not username or not re.fullmatch(r'[a-z_][a-z0-9_-]{0,31}', username):
        return {'success': False, 'error': 'Invalid username'}
    if not is_admin and actor != username:
        return {'error': 'Forbidden: Account scope mismatch', 'status_code': 403}

    domain = str(domain or '').strip().lower()
    if not domain or not re.fullmatch(r'[a-z0-9.-]+\.[a-z]{2,}', domain):
        return {'success': False, 'error': 'Invalid domain name'}

    alloc = ensure_account_port_allocation(collector, db_path, username)
    reverb_port = int(port or alloc.get('ports', {}).get('reverb_port') or 22241)

    conf_dir = APACHE_CONF_DIR
    conf_file = conf_dir / f'uniselv-reverb-{domain}.conf'
    is_installed = conf_file.is_file()

    if operation == 'status':
        return {
            'success': True,
            'domain': domain,
            'port': reverb_port,
            'proxy_installed': is_installed,
            'is_installed': is_installed,
            'conf_file': str(conf_file) if is_installed else '',
        }

    if operation == 'install':
        if not conf_dir.is_dir():
            if os.name != 'nt':
                return {'success': False, 'error': 'Webuzo Apache configuration directory missing: /usr/local/apps/apache2/etc/conf.d'}
            conf_dir.mkdir(parents=True, exist_ok=True)

        escaped_dom = domain.replace('.', r'\.')
        snippet = (
            f"# UNISELV Reverb WebSocket Reverse Proxy for {domain}\n"
            f"<IfModule mod_rewrite.c>\n"
            f"    RewriteEngine On\n"
            f"    RewriteCond %{{HTTP_HOST}} ^(www\\.)?{escaped_dom}$ [NC]\n"
            f"    RewriteCond %{{HTTP:Upgrade}} websocket [NC]\n"
            f"    RewriteCond %{{HTTP:Connection}} upgrade [NC]\n"
            f"    RewriteRule ^/app/?(.*) ws://127.0.0.1:{reverb_port}/app/$1 [P,L]\n"
            f"    ProxyPassReverse /app http://127.0.0.1:{reverb_port}/app\n"
            f"</IfModule>\n"
        )

        try:
            _atomic_write_text(conf_file, snippet, mode=0o644)
        except Exception as exc:
            return {'success': False, 'error': f'Failed to write proxy configuration: {exc}'}

        if os.name != 'nt':
            apachectl = '/usr/local/apps/apache2/bin/apachectl'
            if os.path.isfile(apachectl):
                t_res = subprocess.run([apachectl, 'configtest'], capture_output=True, text=True, timeout=10)
                if t_res.returncode != 0:
                    try:
                        conf_file.unlink()
                    except Exception:
                        pass
                    return {'success': False, 'error': f'Apache syntax validation failed: {t_res.stderr or t_res.stdout}'}
                subprocess.run([apachectl, 'graceful'], capture_output=True, text=True, timeout=15)

        _record_audit(db_path, actor, 'reverb_proxy_installed', username, {'domain': domain, 'port': reverb_port})
        return {
            'success': True,
            'domain': domain,
            'port': reverb_port,
            'proxy_installed': True,
            'is_installed': True,
            'message': f'Reverb WebSocket reverse proxy successfully active for {domain}.',
        }

    if operation in ('remove', 'uninstall'):
        if conf_file.is_file():
            try:
                conf_file.unlink()
            except Exception as exc:
                return {'success': False, 'error': f'Failed to remove proxy conf: {exc}'}
            if os.name != 'nt':
                apachectl = '/usr/local/apps/apache2/bin/apachectl'
                if os.path.isfile(apachectl):
                    subprocess.run([apachectl, 'graceful'], capture_output=True, text=True, timeout=15)

        _record_audit(db_path, actor, 'reverb_proxy_removed', username, {'domain': domain})
        return {
            'success': True,
            'domain': domain,
            'proxy_installed': False,
            'is_installed': False,
            'message': f'Reverb WebSocket reverse proxy removed for {domain}.',
        }

    return {'success': False, 'error': f'Unsupported operation: {operation}'}


def get_active_resource_boosts(collector: Any, db_path: str) -> Dict[str, Any]:
    """Retrieve all currently active temporary plan overrides with remaining countdown minutes."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    boosts = []
    now = time.time()
    try:
        rows = conn.execute("SELECT * FROM temporary_overrides WHERE expires_at > ? ORDER BY expires_at ASC", (now,)).fetchall()
        for r in rows:
            d = dict(r)
            rem_sec = max(0, int(d['expires_at'] - now))
            boosts.append({
                'id': d.get('id'),
                'username': d['username'],
                'original_plan': d.get('original_plan') or '',
                'override_plan': d.get('override_plan') or '',
                'target_plan': d.get('override_plan') or '',
                'created_at': d.get('created_at'),
                'expires_at': d['expires_at'],
                'remaining_seconds': rem_sec,
                'remaining_minutes': (rem_sec + 59) // 60,
                'reason': d.get('reason') or '',
            })
    finally:
        conn.close()
    return {'success': True, 'count': len(boosts), 'boosts': boosts}


def kill_stuck_cli_processes(collector: Any, db_path: str, actor: str, username: str, is_admin: bool = False) -> Dict[str, Any]:
    """Safely terminate hung or runaway background CLI/artisan processes for a user, while strictly preserving PHP-FPM web workers."""
    username = str(username or '').strip()
    if not username or not re.fullmatch(r'[a-z_][a-z0-9_-]{0,31}', username):
        return {'success': False, 'error': 'Invalid username'}
    if not is_admin and actor != username:
        return {'error': 'Forbidden: Account scope mismatch', 'status_code': 403}

    users = collector.get_webuzo_users() if collector else {}
    uinfo = users.get(username, {})
    uid = int(uinfo.get('uid', 0) or 0)
    _, _, _ = _resolve_user_ids(username, uid)

    killed = []
    if os.name != 'nt' and uid >= 500:
        import glob
        for pid_dir in glob.glob('/proc/[0-9]*'):
            pid_str = os.path.basename(pid_dir)
            if not pid_str.isdigit():
                continue
            pid = int(pid_str)
            try:
                st = os.stat(pid_dir)
                if st.st_uid != uid:
                    continue
                cmdline_file = os.path.join(pid_dir, 'cmdline')
                if not os.path.isfile(cmdline_file):
                    continue
                with open(cmdline_file, 'rb') as f:
                    cmd_raw = f.read().replace(b'\x00', b' ').decode('utf-8', errors='replace').strip()

                if 'php-fpm' in cmd_raw or 'fpm' in cmd_raw or 'httpd' in cmd_raw:
                    continue

                is_target = any(k in cmd_raw for k in ('artisan', 'queue:work', 'schedule:run', 'bash', 'python', 'node'))
                if is_target:
                    os.kill(pid, 15)
                    killed.append({'pid': pid, 'cmd': cmd_raw[:120]})
            except Exception:
                pass

    _record_audit(db_path, actor, 'stuck_cli_processes_killed', username, {'killed_count': len(killed), 'pids': [k['pid'] for k in killed]})
    return {
        'success': True,
        'username': username,
        'killed_count': len(killed),
        'killed': killed,
        'message': f'Terminated {len(killed)} background CLI task(s). Web FPM workers were safely preserved.',
    }


def run_laravel_services_selftest(collector: Any, db_path: str, username: str, php_branch: str = 'php84') -> Dict[str, Any]:
    """Run an ephemeral non-invasive systemd service containment self-test for Laravel workers/reverb."""
    if not _PLATFORM_SELFTEST_LOCK.acquire(blocking=False):
        return {'success': False, 'error': 'Another Laravel services self-test is already running'}
    started = time.time()
    unit_name = ''
    probe_dir = None
    try:
        users = collector.get_webuzo_users() if collector else {}
        if username not in users:
            return {'success': False, 'error': f'Account {username} not found'}
        uid, gid, _ = _resolve_user_ids(username, int(users[username].get('uid', 0) or 0))
        if uid < 500:
            return {'success': False, 'error': f'Refusing test on system UID {uid}'}
        php_bin = f'/usr/local/apps/{php_branch}/bin/php'
        if not os.path.isfile(php_bin):
            return {'success': False, 'error': f'PHP binary missing: {php_bin}'}

        APP_SOCKET_ROOT.mkdir(parents=True, exist_ok=True)
        os.chmod(APP_SOCKET_ROOT, 0o755)
        probe_base = str(APP_SOCKET_ROOT) if os.name != 'nt' else None
        probe_dir = pathlib.Path(tempfile.mkdtemp(prefix=f'selftest-lrv-{uid}-', dir=probe_base))
        os.chmod(probe_dir, 0o755)
        if os.name != 'nt':
            os.chown(probe_dir, uid, gid)

        artisan = probe_dir / 'artisan'
        artisan.write_text('<?php fwrite(STDOUT, "UNISELV_LARAVEL_PROBE_READY\\n"); fflush(STDOUT); sleep(15);\n', encoding='utf-8')
        os.chmod(artisan, 0o644)
        log_file = probe_dir / 'probe.log'
        log_file.write_text('', encoding='utf-8')
        os.chmod(log_file, 0o644)
        if os.name != 'nt':
            os.chown(artisan, uid, gid)
            os.chown(log_file, uid, gid)

        unit_name = f'uniselv-lrv-selftest-{uid}.service'
        group_name = username
        if grp is not None and hasattr(grp, 'getgrgid') and gid:
            try:
                gr = grp.getgrgid(gid)
                if gr is not None:
                    group_name = gr.gr_name
            except KeyError:
                group_name = username
        unit_body = _render_laravel_systemd_unit(username, group_name, uid, 'queue', 'selftest', str(probe_dir), f'{php_bin} {artisan}', str(log_file))
        _atomic_write_text(_service_unit_path(unit_name), unit_body, mode=0o644)
        subprocess.run(['systemctl', 'daemon-reload'], capture_output=True, text=True, timeout=10)
        subprocess.run(['systemctl', 'start', unit_name], capture_output=True, text=True, timeout=15)

        pid = 0
        cg_text = ''
        proc_uid = -1
        log_text = ''
        for _ in range(20):
            st = _query_systemd_unit(unit_name)
            if st['main_pid'] > 0 and os.path.exists(f"/proc/{st['main_pid']}/cgroup"):
                pid = st['main_pid']
                cg_text = pathlib.Path(f'/proc/{pid}/cgroup').read_text(encoding='utf-8', errors='replace').strip()
                proc_uid = os.stat(f'/proc/{pid}').st_uid
            log_text = log_file.read_text(encoding='utf-8', errors='replace') if log_file.is_file() else ''
            if pid > 0 and 'UNISELV_LARAVEL_PROBE_READY' in log_text:
                break
            time.sleep(0.25)

        expected_slice = f'golden-{uid}.slice'
        slice_ok = pid > 0 and expected_sl_in(expected_slice, cg_text) and proc_uid == uid
        steps = [
            {'name': 'unit_started_as_uid', 'label': f'Worker Spawned Strictly as UID {uid} ({username})', 'passed': pid > 0 and proc_uid == uid, 'detail': f'PID={pid}, real UID={proc_uid}'},
            {'name': 'slice_contained', 'label': f'Contained in {expected_slice}', 'passed': slice_ok, 'detail': cg_text or 'No cgroup path'},
            {'name': 'log_captured', 'label': 'Worker Output Captured cleanly', 'passed': 'UNISELV_LARAVEL_PROBE_READY' in log_text, 'detail': log_text.strip()[:120]},
        ]
        all_passed = all(s['passed'] for s in steps)
        _record_audit(db_path, 'admin', 'platform_laravel_selftest', username, {'all_passed': all_passed, 'php_branch': php_branch, 'steps': steps})
        return {
            'success': True,
            'all_passed': all_passed,
            'username': username,
            'uid': uid,
            'php_branch': php_branch,
            'elapsed_ms': int((time.time() - started) * 1000),
            'steps': steps,
        }
    finally:
        if unit_name:
            try:
                subprocess.run(['systemctl', 'stop', unit_name], capture_output=True, text=True, timeout=10)
                ufile = _service_unit_path(unit_name)
                if ufile.is_file():
                    ufile.unlink()
                subprocess.run(['systemctl', 'daemon-reload'], capture_output=True, text=True, timeout=10)
            except Exception:
                pass
        if probe_dir and probe_dir.exists():
            shutil.rmtree(probe_dir, ignore_errors=True)
        _PLATFORM_SELFTEST_LOCK.release()


def expected_sl_in(expected_slice: str, cg_text: str) -> bool:
    return f'/{expected_slice}' in cg_text or cg_text.endswith(expected_slice)


# ==================== 5. MULTI-RUNTIME CONTAINMENT & HEAVY BINARY GUARD ====================

def scan_tenant_runtimes_and_binaries(collector: Any, db_path: str) -> Dict[str, Any]:
    """Inspect /proc for tenant Node.js, Python ASGI/WSGI, manual Laravel daemons & heavy binaries."""
    users = collector.get_webuzo_users() if collector else {}
    uid_map = {int(v['uid']): k for k, v in users.items() if v.get('uid')}
    boot_time = 0.0
    try:
        for ln in pathlib.Path('/proc/stat').read_text(encoding='utf-8', errors='replace').splitlines():
            if ln.startswith('btime '):
                boot_time = float(ln.split()[1])
                break
    except Exception:
        pass
    clk_tck = 100
    try:
        clk_tck = os.sysconf(os.sysconf_names['SC_CLK_TCK'])
    except Exception:
        pass

    procs: List[Dict[str, Any]] = []
    if os.path.isdir('/proc'):
        for entry in os.scandir('/proc'):
            if not entry.name.isdigit():
                continue
            pid = int(entry.name)
            try:
                st = os.stat(entry.path)
                uid = int(st.st_uid)
                if uid not in uid_map:
                    continue
                comm = pathlib.Path(entry.path, 'comm').read_text(encoding='utf-8', errors='replace').strip()
                cmd = pathlib.Path(entry.path, 'cmdline').read_bytes().replace(b'\x00', b' ').decode('utf-8', errors='replace').strip()
                cmd_l = cmd.lower()
                comm_l = comm.lower()

                kind = ''
                if comm_l in HEAVY_BINARY_NAMES or any(hb in cmd_l for hb in ('--headless', 'wkhtmltopdf', 'soffice.bin')):
                    kind = 'heavy_binary'
                elif comm_l in NODE_RUNTIME_NAMES or 'next-server' in cmd_l or 'pm2 ' in cmd_l:
                    kind = 'node'
                elif comm_l in PYTHON_RUNTIME_NAMES or any(py in cmd_l for py in ('uvicorn ', 'gunicorn ', 'celery ', 'daphne ', 'hypercorn ')):
                    kind = 'python'
                elif 'artisan queue:' in cmd_l or 'artisan horizon' in cmd_l or 'artisan reverb:' in cmd_l or 'artisan schedule:work' in cmd_l:
                    kind = 'laravel_bg'

                if not kind:
                    continue

                cg = pathlib.Path(entry.path, 'cgroup').read_text(encoding='utf-8', errors='replace').strip()
                exp_slice = f'golden-{uid}.slice'
                contained = expected_sl_in(exp_slice, cg)

                rss_bytes = 0
                for sln in pathlib.Path(entry.path, 'status').read_text(encoding='utf-8', errors='replace').splitlines():
                    if sln.startswith('VmRSS:'):
                        rss_bytes = int(sln.split()[1]) * 1024
                        break

                age_sec = 0
                stat_raw = pathlib.Path(entry.path, 'stat').read_text(encoding='utf-8', errors='replace')
                rp = stat_raw.rfind(')')
                if rp > 0 and boot_time > 0:
                    fields = stat_raw[rp + 2:].split()
                    start_ticks = int(fields[19])
                    age_sec = max(0, int(time.time() - (boot_time + (start_ticks / clk_tck))))

                procs.append({
                    'pid': pid,
                    'uid': uid,
                    'username': uid_map[uid],
                    'kind': kind,
                    'comm': comm,
                    'cmdline': cmd[:220],
                    'rss_mib': round(rss_bytes / (1024 * 1024), 1),
                    'age_sec': age_sec,
                    'current_cgroup': cg,
                    'expected_slice': exp_slice,
                    'contained': contained,
                })
            except Exception:
                continue

    return {'success': True, 'processes': procs}


def enforce_platform_tick(collector: Any, db_path: str) -> Dict[str, Any]:
    """Contain escaped Node/Python/Laravel/Heavy-Binary processes and enforce concurrency/timeout caps."""
    settings = load_platform_settings(db_path)
    scan = scan_tenant_runtimes_and_binaries(collector, db_path)
    procs = scan.get('processes', [])

    contain_enabled = settings.get('platform_runtime_containment', '1') == '1'
    mode = settings.get('platform_runtime_mode', 'enforce')
    hb_guard = settings.get('platform_heavy_binary_guard', '1') == '1'
    hb_max_conc = max(1, int(settings.get('platform_heavy_binary_max_concurrent', '2') or 2))
    hb_max_sec = max(30, int(settings.get('platform_heavy_binary_max_sec', '300') or 300))

    contained_moves = 0
    terminated: List[int] = []

    for p in procs:
        if contain_enabled and not p['contained']:
            ok = bool(osw_mgr.contain_process_in_account_slice(p['uid'], p['pid']))
            if ok:
                contained_moves += 1
                _record_audit(db_path, 'system', 'platform_runtime_contained', p['username'], {'pid': p['pid'], 'kind': p['kind'], 'slice': p['expected_slice']})

    if hb_guard:
        by_user_hb: Dict[str, List[Dict[str, Any]]] = {}
        for p in procs:
            if p['kind'] == 'heavy_binary':
                by_user_hb.setdefault(p['username'], []).append(p)
        for uname, hlist in by_user_hb.items():
            hlist.sort(key=lambda x: x['age_sec'], reverse=True)
            for idx, hp in enumerate(hlist):
                over_age = hp['age_sec'] > hb_max_sec
                over_conc = idx >= hb_max_conc
                if (over_age or over_conc) and mode == 'enforce':
                    if osw_mgr._safe_stop_pid(hp['uid'], hp['pid'], 0):
                        terminated.append(hp['pid'])
                        _record_audit(db_path, 'system', 'platform_heavy_binary_stopped', uname, {
                            'pid': hp['pid'], 'comm': hp['comm'], 'age_sec': hp['age_sec'],
                            'reason': 'timeout' if over_age else 'concurrency_cap',
                        })

    # Ensure /run/uniselv-apps/<username>/ports.json exists for zero-.env port auto-detection (survives tmpfs reboot)
    try:
        if collector and os.name != 'nt':
            for uname in sorted((collector.get_webuzo_users() or {}).keys()):
                if not (APP_SOCKET_ROOT / uname / 'ports.json').is_file():
                    ensure_account_port_allocation(collector, db_path, uname)
    except Exception:
        pass

    return {'success': True, 'scanned': len(procs), 'contained': contained_moves, 'contained_moves': contained_moves, 'terminated': len(terminated), 'terminated_pids': terminated, 'processes': procs}


# ==================== 6. APP LOG BLOAT & INODE WATCHDOG ====================

def scan_app_logs_and_inodes(collector: Any, db_path: str, target_user: Optional[str] = None) -> Dict[str, Any]:
    """Inspect /home & / inode metrics and scan tenant logs safely without symlink traversal."""
    settings = load_platform_settings(db_path)
    thresh_bytes = max(10, int(settings.get('platform_log_threshold_mib', '250') or 250)) * 1024 * 1024

    inodes: List[Dict[str, Any]] = []
    if os.name != 'nt' and shutil.which('df'):
        r = subprocess.run(['df', '-P', '-i', '/', '/home'], capture_output=True, text=True, timeout=5)
        seen_fs = set()
        for ln in r.stdout.splitlines()[1:]:
            parts = ln.split()
            if len(parts) >= 6:
                mnt = parts[5]
                if mnt in seen_fs:
                    continue
                seen_fs.add(mnt)
                inodes.append({'filesystem': parts[0], 'mount': mnt, 'total': parts[1], 'used': parts[2], 'free': parts[3], 'use_pct': parts[4]})

    users = collector.get_webuzo_users() if collector else {}
    target_names = [target_user] if (target_user and target_user in users) else sorted(users.keys())
    findings: List[Dict[str, Any]] = []
    now = int(time.time())

    rel_globs = [
        'storage/logs/*.log', 'public_html/storage/logs/*.log',
        '.uniselv-logs/*.log', '.pm2/logs/*.log',
        'public_html/error_log', 'logs/*.log',
    ]

    for uname in target_names:
        _, _, pw_home = _resolve_user_ids(uname)
        home = pathlib.Path(pw_home)
        if not home.is_dir():
            continue
        seen_paths = set()
        for pattern in rel_globs:
            for p in home.glob(pattern):
                if p.is_symlink() or not p.is_file():
                    continue
                rp = os.path.realpath(str(p))
                if rp in seen_paths:
                    continue
                seen_paths.add(rp)
                try:
                    st = p.stat()
                    findings.append({
                        'username': uname,
                        'log_path': rp,
                        'size_bytes': int(st.st_size),
                        'size_mib': round(st.st_size / (1024 * 1024), 2),
                        'over_threshold': st.st_size >= thresh_bytes,
                        'mtime': int(st.st_mtime),
                    })
                except OSError:
                    continue

    findings.sort(key=lambda x: x['size_bytes'], reverse=True)
    if db_path and os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        try:
            for f in findings[:200]:
                conn.execute(
                    'INSERT OR REPLACE INTO app_log_findings (username, log_path, size_bytes, mtime, scanned_at) VALUES (?, ?, ?, ?, ?)',
                    (f['username'], f['log_path'], f['size_bytes'], f['mtime'], now),
                )
            conn.commit()
        finally:
            conn.close()

    return {'success': True, 'threshold_mib': thresh_bytes // (1024 * 1024), 'inodes': inodes, 'findings': findings[:100]}


def truncate_app_log(db_path: str, actor: str, username: str, log_path: str, keep_lines: int = 1000, is_admin: bool = False, home_override: Optional[str] = None) -> Dict[str, Any]:
    """Safely trim an oversized log file inside user home while preserving permissions/ownership."""
    if not is_admin and actor != username:
        return {'error': 'Forbidden: Cannot truncate another account log', 'status_code': 403}
    safe_p = _safe_home_subpath(username, log_path, home_override=home_override)
    if not safe_p or not safe_p.is_file() or safe_p.is_symlink():
        return {'success': False, 'error': 'Invalid or unsafe log path'}
    if not (safe_p.name.endswith('.log') or safe_p.name == 'error_log'):
        return {'success': False, 'error': 'Refusing truncation on non-log file'}

    keep_lines = max(0, min(5000, int(keep_lines)))
    before_bytes = safe_p.stat().st_size
    tail_bytes = b''
    if keep_lines > 0 and before_bytes > 0:
        with open(safe_p, 'rb') as rf:
            rf.seek(max(0, before_bytes - 262144))
            tail_lines = rf.read().splitlines()[-keep_lines:]
            tail_bytes = b'\n'.join(tail_lines) + (b'\n' if tail_lines else b'')

    with open(safe_p, 'r+b') as wf:
        wf.seek(0)
        wf.write(tail_bytes)
        wf.truncate(len(tail_bytes))
        wf.flush()

    after_bytes = safe_p.stat().st_size
    freed_bytes = max(0, before_bytes - after_bytes)
    _record_audit(db_path, actor, 'platform_log_truncated', username, {'log_path': str(safe_p), 'before_bytes': before_bytes, 'after_bytes': after_bytes, 'freed_bytes': freed_bytes})
    return {'success': True, 'log_path': str(safe_p), 'before_bytes': before_bytes, 'after_bytes': after_bytes, 'freed_bytes': freed_bytes}


# ==================== 7. SERVER MIGRATION: POLICY BUNDLE EXPORT / IMPORT ====================

def export_policy_bundle(db_path: str) -> Dict[str, Any]:
    """Export portable server policies, package mappings, permissions, OpenSwoole & Laravel service configs (no secrets)."""
    if not db_path or not os.path.exists(db_path):
        return {'success': False, 'error': 'Database not found'}
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        settings = {r['key']: r['value'] for r in conn.execute('SELECT key, value FROM settings').fetchall()}
        pkg_maps = [dict(r) for r in conn.execute('SELECT billing_package, resource_plan FROM package_mappings').fetchall()]
        role_perms = [dict(r) for r in conn.execute('SELECT role, permission, granted FROM role_permissions').fetchall()]
        acct_perms = [dict(r) for r in conn.execute('SELECT username, permission, granted FROM account_permissions').fetchall()]
        osw_plans = [dict(r) for r in conn.execute('SELECT plan_name, allowed, max_workers_override, max_task_workers_override FROM openswoole_plan_policies').fetchall()]
        osw_accts = [dict(r) for r in conn.execute('SELECT username, allowed, max_workers_override, max_task_workers_override FROM openswoole_account_policies').fetchall()]
        lrv_svcs = [dict(r) for r in conn.execute(
            'SELECT username, service_type, service_slug, app_path, php_branch, workers, max_memory_mb, queues, enabled FROM managed_app_services'
        ).fetchall()]
    finally:
        conn.close()

    return {
        'success': True,
        'bundle': {
            'schema_version': 1,
            'exported_at': int(time.time()),
            'settings': settings,
            'package_mappings': pkg_maps,
            'role_permissions': role_perms,
            'account_permissions': acct_perms,
            'openswoole_plan_policies': osw_plans,
            'openswoole_account_policies': osw_accts,
            'managed_app_services': lrv_svcs,
        },
    }


def import_policy_bundle(collector: Any, db_path: str, actor: str, bundle: Dict[str, Any], dry_run: bool = False) -> Dict[str, Any]:
    """Validate and apply an exported policy bundle onto this server (transactional)."""
    if not isinstance(bundle, dict) or int(bundle.get('schema_version') or 0) != 1:
        return {'success': False, 'error': 'Unsupported or invalid policy bundle schema'}

    settings = bundle.get('settings') if isinstance(bundle.get('settings'), dict) else {}
    pkg_maps = bundle.get('package_mappings') if isinstance(bundle.get('package_mappings'), list) else []
    role_perms = bundle.get('role_permissions') if isinstance(bundle.get('role_permissions'), list) else []
    acct_perms = bundle.get('account_permissions') if isinstance(bundle.get('account_permissions'), list) else []
    osw_plans = bundle.get('openswoole_plan_policies') if isinstance(bundle.get('openswoole_plan_policies'), list) else []
    osw_accts = bundle.get('openswoole_account_policies') if isinstance(bundle.get('openswoole_account_policies'), list) else []
    lrv_svcs = bundle.get('managed_app_services') if isinstance(bundle.get('managed_app_services'), list) else []

    users = collector.get_webuzo_users() if collector else {}
    summary = {
        'settings': len(settings),
        'package_mappings': len(pkg_maps),
        'role_permissions': len(role_perms),
        'account_permissions': len(acct_perms),
        'openswoole_plan_policies': len(osw_plans),
        'openswoole_account_policies': len(osw_accts),
        'managed_app_services_matched': sum(1 for s in lrv_svcs if isinstance(s, dict) and s.get('username') in users),
        'managed_app_services_skipped': sum(1 for s in lrv_svcs if isinstance(s, dict) and s.get('username') not in users),
    }
    if dry_run:
        return {'success': True, 'dry_run': True, 'summary': summary}

    now = int(time.time())
    conn = sqlite3.connect(db_path)
    try:
        for k, v in settings.items():
            conn.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', (str(k), str(v)))
        for pm in pkg_maps:
            if pm.get('billing_package') and pm.get('resource_plan'):
                conn.execute('INSERT OR REPLACE INTO package_mappings (billing_package, resource_plan, updated_at) VALUES (?, ?, ?)',
                             (str(pm['billing_package']), str(pm['resource_plan']), now))
        for rp in role_perms:
            if rp.get('role') and rp.get('permission'):
                conn.execute('INSERT OR REPLACE INTO role_permissions (role, permission, granted, updated_at) VALUES (?, ?, ?, ?)',
                             (str(rp['role']), str(rp['permission']), int(bool(rp.get('granted', 1))), now))
        for ap in acct_perms:
            if ap.get('username') and ap.get('permission'):
                conn.execute('INSERT OR REPLACE INTO account_permissions (username, permission, granted, updated_at, updated_by) VALUES (?, ?, ?, ?, ?)',
                             (str(ap['username']), str(ap['permission']), int(bool(ap.get('granted', 1))), now, actor))
        for op in osw_plans:
            if op.get('plan_name'):
                conn.execute(
                    'INSERT OR REPLACE INTO openswoole_plan_policies (plan_name, allowed, max_workers_override, max_task_workers_override, updated_at, updated_by) VALUES (?, ?, ?, ?, ?, ?)',
                    (str(op['plan_name']), int(bool(op.get('allowed', 1))), int(op.get('max_workers_override', 0)), int(op.get('max_task_workers_override', -1)), now, actor),
                )
        for oa in osw_accts:
            if oa.get('username'):
                conn.execute(
                    'INSERT OR REPLACE INTO openswoole_account_policies (username, allowed, max_workers_override, max_task_workers_override, updated_at, updated_by) VALUES (?, ?, ?, ?, ?, ?)',
                    (str(oa['username']), int(oa.get('allowed', -1)), int(oa.get('max_workers_override', 0)), int(oa.get('max_task_workers_override', -1)), now, actor),
                )
        conn.commit()
    finally:
        conn.close()

    reinstalled_services = 0
    for svc in lrv_svcs:
        if isinstance(svc, dict) and svc.get('username') in users:
            res = save_and_install_laravel_service(collector, db_path, actor, svc)
            if res.get('success'):
                reinstalled_services += 1

    osw_mgr.reconcile_new_php_versions(db_path, automatic=False, force_all=False)
    _record_audit(db_path, actor, 'platform_policy_bundle_imported', 'server', {'summary': summary, 'reinstalled_services': reinstalled_services})
    return {'success': True, 'dry_run': False, 'summary': summary, 'reinstalled_services': reinstalled_services}


def get_platform_overview_payload(collector: Any, db_path: str, target_user: Optional[str] = None) -> Dict[str, Any]:
    """Combined payload for Admin Platform & Laravel Ops console."""
    settings = load_platform_settings(db_path)
    preflight = get_os_preflight_status()
    lrv = list_laravel_services(collector, db_path, target_user=target_user)
    rt = scan_tenant_runtimes_and_binaries(collector, db_path)
    redis_st = get_redis_isolation_status(collector, db_path)
    ports = list_all_port_allocations(collector, db_path)
    user_perms = {u: get_user_platform_permissions(db_path, u) for u in (lrv.get('accounts') or [])}
    return {
        'success': True,
        'settings': settings,
        'preflight': preflight,
        'supervisor': preflight.get('supervisor') or get_supervisor_status(),
        'stack_readiness': get_laravel_stack_readiness(db_path),
        'user_permissions': user_perms,
        'laravel': lrv,
        'runtimes': rt.get('processes', []),
        'redis': redis_st,
        'port_allocations': ports,
    }
