import json
import os
import pathlib
import re
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
    import fcntl
except ImportError:
    fcntl = None

try:
    import pwd
except ImportError:
    pwd = None

APPS_DIR = pathlib.Path('/usr/local/apps')
STORE_DIR = pathlib.Path('/var/lib/uniselv-resource-manager/openswoole')
CACHE_DIR = STORE_DIR / 'cache'
STATE_FILE = STORE_DIR / 'state.json'
JOB_FILE = STORE_DIR / 'job.json'
POLICY_EXPORT_FILE = STORE_DIR / 'policy.json'
LOCK_FILE = STORE_DIR / 'build.lock'
ISOLATION_SCRIPT = pathlib.Path('/usr/local/sbin/webuzo-isolation.py')

DEFAULT_BUILD_FLAGS = ['--enable-openssl', '--enable-http2', '--enable-hook-curl', '--enable-sockets']

OPENSWOOLE_DEFAULTS = {
    'openswoole_auto_install_new_php': '1',
    'openswoole_enforcement_mode': 'enforce',  # 'monitor' or 'enforce'
    'openswoole_strict_cgroup': '1',
    'openswoole_worker_rss_mib': '128',
    'openswoole_global_max_workers': '4',
    'openswoole_enable_coroutine': '1',
    'openswoole_preemptive_scheduler': '0',
    'openswoole_unixsock_buffer_size': '8388608',
    'openswoole_disabled_versions': '',
}


def atomic_write_text(path: pathlib.Path, content: str, mode: int = 0o644) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        raise RuntimeError(f'Refusing to overwrite symlink: {path}')
    tmp = path.with_name(f'{path.name}.tmp.{os.getpid()}.{time.time_ns()}')
    try:
        with open(tmp, 'w', encoding='utf-8', newline='\n') as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        os.chmod(tmp, mode)
        os.replace(tmp, path)
    finally:
        if tmp.exists() or tmp.is_symlink():
            try:
                tmp.unlink()
            except OSError:
                pass


def atomic_write_json(path: pathlib.Path, data: Any, mode: int = 0o600) -> None:
    atomic_write_text(path, json.dumps(data, indent=2, sort_keys=False) + '\n', mode=mode)


def read_json_safe(path: pathlib.Path, default: Any = None) -> Any:
    try:
        if path.is_file():
            return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        pass
    return default


def compatible_openswoole_candidates(php_version_id: int) -> List[str]:
    """Return PECL OpenSwoole release candidates ordered by stability and PHP compatibility."""
    if php_version_id <= 0:
        return []
    if php_version_id >= 80500:
        return ['26.2.0', '25.2.0']
    if php_version_id >= 80300:
        return ['25.2.0', '26.2.0']
    if php_version_id >= 80200:
        return ['25.2.0', '22.1.2']
    if php_version_id >= 80100:
        return ['22.1.2']
    if php_version_id >= 70400:
        return ['4.12.1']
    return []


def parse_disabled_versions(raw: str) -> set:
    if not raw:
        return set()
    return {v.strip().lower() for v in str(raw).split(',') if re.fullmatch(r'php\d{2,3}', v.strip().lower())}


def serialize_disabled_versions(versions: set) -> str:
    return ','.join(sorted(v for v in versions if re.fullmatch(r'php\d{2,3}', v)))


def load_openswoole_settings(db_path: str) -> Dict[str, str]:
    settings = dict(OPENSWOOLE_DEFAULTS)
    if not db_path or not os.path.exists(db_path):
        return settings
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute("SELECT key, value FROM settings WHERE key LIKE 'openswoole_%'")
        for k, v in cur.fetchall():
            if k in settings and v is not None:
                settings[k] = str(v)
    except Exception:
        pass
    finally:
        conn.close()
    return settings


def golden_shield_active() -> bool:
    return (
        os.path.exists('/var/lib/golden-shield/installed.json')
        and not os.path.exists('/var/lib/golden-shield/disabling.json')
    )


def expected_account_cgroup(uid: int) -> str:
    if golden_shield_active():
        return f'/golden.slice/golden-{uid}.slice'
    return f'/{uid}.slice'


def expected_account_slice_name(uid: int) -> str:
    if golden_shield_active():
        return f'golden-{uid}.slice'
    return f'{uid}.slice'


def find_phpize(prefix: pathlib.Path) -> Optional[str]:
    for cand in (prefix / 'bin' / 'phpize', prefix / 'apache2' / 'bin' / 'phpize'):
        if cand.is_file() and os.access(str(cand), os.X_OK):
            return str(cand)
    return None


def find_php_config(prefix: pathlib.Path) -> Optional[str]:
    for cand in (prefix / 'bin' / 'php-config', prefix / 'apache2' / 'bin' / 'php-config'):
        if cand.is_file() and os.access(str(cand), os.X_OK):
            return str(cand)
    return None


def discover_php_versions(apps_dir: pathlib.Path = APPS_DIR, disabled_versions: Optional[set] = None) -> Dict[str, Dict[str, Any]]:
    """Inspect all installed Webuzo PHP branches cleanly without mutating anything."""
    disabled = disabled_versions or set()
    state = read_json_safe(STATE_FILE, {}) or {}
    version_state = state.get('versions', {}) if isinstance(state, dict) else {}
    results: Dict[str, Dict[str, Any]] = {}

    if not apps_dir.is_dir():
        return results

    for entry in sorted(apps_dir.iterdir()):
        if entry.is_symlink() or not entry.is_dir():
            continue
        ver = entry.name
        if not re.fullmatch(r'php\d{2,3}', ver):
            continue
        php_bin = entry / 'bin' / 'php'
        if not php_bin.is_file() or not os.access(str(php_bin), os.X_OK):
            continue

        info: Dict[str, Any] = {
            'version': ver,
            'prefix': str(entry),
            'php_bin': str(php_bin),
            'php_version': '',
            'php_version_id': 0,
            'extension_dir': '',
            'php_config_ext_dir': '',
            'ini_dir': str(entry / 'etc' / 'php.d'),
            'ini_file': str(entry / 'etc' / 'php.d' / 'openswoole.ini'),
            'ini_exists': (entry / 'etc' / 'php.d' / 'openswoole.ini').is_file(),
            'phpize': find_phpize(entry),
            'php_config': find_php_config(entry),
            'so_exists': False,
            'loaded': False,
            'openswoole_version': '',
            'compatible_versions': [],
            'recommended_release': '',
            'manually_disabled': ver in disabled,
            'status': 'not_installed',
            'last_error': version_state.get(ver, {}).get('last_error', ''),
            'last_build_at': version_state.get(ver, {}).get('last_build_at', 0),
        }

        probe_code = (
            'echo json_encode(['
            '"ver"=>PHP_VERSION,'
            '"id"=>PHP_VERSION_ID,'
            '"ext_dir"=>ini_get("extension_dir"),'
            '"loaded"=>extension_loaded("openswoole"),'
            '"ext_ver"=>extension_loaded("openswoole")?(phpversion("openswoole")?:"loaded"):""'
            ']);'
        )
        try:
            proc = subprocess.run(
                [str(php_bin), '-d', 'display_startup_errors=0', '-r', probe_code],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if proc.returncode == 0 and proc.stdout.strip():
                parsed = json.loads(proc.stdout.strip().splitlines()[-1])
                info['php_version'] = str(parsed.get('ver', ''))
                info['php_version_id'] = int(parsed.get('id', 0) or 0)
                info['extension_dir'] = str(parsed.get('ext_dir', '')).rstrip('/')
                info['loaded'] = bool(parsed.get('loaded', False))
                info['openswoole_version'] = str(parsed.get('ext_ver', ''))
        except Exception as exc:
            info['last_error'] = f'PHP probe error: {exc}'

        if info['php_config']:
            try:
                pc = subprocess.run([info['php_config'], '--extension-dir'], capture_output=True, text=True, timeout=5)
                if pc.returncode == 0:
                    info['php_config_ext_dir'] = pc.stdout.strip().rstrip('/')
            except Exception:
                pass

        if info['extension_dir']:
            so_path = pathlib.Path(info['extension_dir']) / 'openswoole.so'
            info['so_exists'] = so_path.is_file()
        elif info['php_config_ext_dir']:
            so_path = pathlib.Path(info['php_config_ext_dir']) / 'openswoole.so'
            info['so_exists'] = so_path.is_file()

        cands = compatible_openswoole_candidates(info['php_version_id'])
        info['compatible_versions'] = cands
        info['recommended_release'] = cands[0] if cands else ''

        if not cands:
            info['status'] = 'unsupported'
        elif info['loaded'] and info['ini_exists']:
            info['status'] = 'active'
        elif info['loaded'] and not info['ini_exists']:
            info['status'] = 'active_manual'
        elif info['manually_disabled'] and info['so_exists']:
            info['status'] = 'disabled'
        elif info['so_exists'] and not info['ini_exists']:
            info['status'] = 'installed_disabled'
        elif info['ini_exists'] and not info['loaded']:
            info['status'] = 'broken_ini'
        else:
            info['status'] = 'not_installed'

        results[ver] = info

    return results


def render_openswoole_ini(settings: Dict[str, str]) -> str:
    coroutine = 'On' if str(settings.get('openswoole_enable_coroutine', '1')) in ('1', 'true', 'True', 'On') else 'Off'
    preemptive = 'On' if str(settings.get('openswoole_preemptive_scheduler', '0')) in ('1', 'true', 'True', 'On') else 'Off'
    try:
        buf_size = max(1048576, min(67108864, int(settings.get('openswoole_unixsock_buffer_size', '8388608'))))
    except (ValueError, TypeError):
        buf_size = 8388608
    return (
        '; Managed by UNISELV Resource Manager\n'
        'extension=openswoole.so\n'
        f'openswoole.enable_coroutine={coroutine}\n'
        f'openswoole.enable_preemptive_scheduler={preemptive}\n'
        f'openswoole.unixsock_buffer_size={buf_size}\n'
        'openswoole.display_errors=On\n'
    )


def reload_php_runtime(ver: str) -> Tuple[bool, str]:
    """Gracefully reload isolated PHP-FPM or native FPM after INI changes."""
    if not re.fullmatch(r'php\d{2,3}', ver):
        return False, 'Invalid PHP version'
    try:
        if ISOLATION_SCRIPT.is_file():
            is_mgr = subprocess.run(['systemctl', 'is-active', f'wpiso-manager-{ver}.service'], capture_output=True, text=True, timeout=8)
            if is_mgr.returncode == 0:
                res = subprocess.run(['python3', str(ISOLATION_SCRIPT), 'action', ver, 'reload'], capture_output=True, text=True, timeout=45)
                return (res.returncode == 0), (res.stdout or res.stderr).strip()
        native_svc = f'php-fpm{ver[3:]}.service'
        is_native = subprocess.run(['systemctl', 'is-active', native_svc], capture_output=True, text=True, timeout=8)
        if is_native.returncode == 0:
            res = subprocess.run(['systemctl', 'reload', native_svc], capture_output=True, text=True, timeout=30)
            return (res.returncode == 0), (res.stdout or res.stderr).strip()
        return True, 'No active FPM service required reload'
    except Exception as exc:
        return False, str(exc)


def sync_ini_for_active_versions(settings: Dict[str, str], apps_dir: pathlib.Path = APPS_DIR) -> Dict[str, Any]:
    """Update managed openswoole.ini directives on all currently enabled PHP versions."""
    disabled = parse_disabled_versions(settings.get('openswoole_disabled_versions', ''))
    versions = discover_php_versions(apps_dir=apps_dir, disabled_versions=disabled)
    updated: List[str] = []
    errors: List[str] = []
    desired = render_openswoole_ini(settings)

    for ver, meta in versions.items():
        if ver in disabled:
            continue
        ini_path = pathlib.Path(meta['ini_file'])
        if not ini_path.is_file():
            continue
        try:
            current = ini_path.read_text(encoding='utf-8', errors='replace')
            if current != desired:
                atomic_write_text(ini_path, desired, mode=0o644)
                reload_php_runtime(ver)
                updated.append(ver)
        except Exception as exc:
            errors.append(f'{ver}: {exc}')

    return {'updated': updated, 'errors': errors}


def download_pecl_tarball(release_ver: str, cache_dir: pathlib.Path = CACHE_DIR) -> pathlib.Path:
    if not re.fullmatch(r'\d+\.\d+\.\d+', release_ver):
        raise ValueError(f'Invalid OpenSwoole release version: {release_ver}')
    cache_dir.mkdir(parents=True, exist_ok=True)
    target = cache_dir / f'openswoole-{release_ver}.tgz'
    if target.is_file() and target.stat().st_size > 100000:
        return target
    tmp = target.with_name(f'openswoole-{release_ver}.tgz.downloading.{os.getpid()}')
    url = f'https://pecl.php.net/get/openswoole-{release_ver}.tgz'
    try:
        res = subprocess.run(
            ['curl', '-fsSL', '--connect-timeout', '20', '--max-time', '180', '-o', str(tmp), url],
            capture_output=True,
            text=True,
            timeout=200,
        )
        if res.returncode != 0 or not tmp.is_file() or tmp.stat().st_size < 100000:
            raise RuntimeError(f'Failed downloading {url}: {res.stderr.strip() or res.stdout.strip()}')
        os.replace(tmp, target)
        return target
    finally:
        if tmp.exists():
            try:
                tmp.unlink()
            except OSError:
                pass


def _run_compile_step_isolated(script_text: str, php_ver: str) -> Tuple[int, str]:
    """Run compilation outside the agent daemon's 128 MiB systemd slice to prevent OOM."""
    with tempfile.NamedTemporaryFile(mode='w', prefix=f'osw-build-{php_ver}-', suffix='.sh', delete=False, encoding='utf-8', newline='\n') as tf:
        tf.write(script_text)
        script_path = tf.name
    os.chmod(script_path, 0o700)
    try:
        systemd_run = shutil.which('systemd-run')
        has_systemd = os.path.isdir('/run/systemd/system') and bool(systemd_run)
        if has_systemd:
            unit = f'uniselv-openswoole-build-{php_ver}-{int(time.time())}'
            cmd = [
                systemd_run,
                f'--unit={unit}',
                '--description=UNISELV OpenSwoole Extension Builder',
                '--property=MemoryMax=2G',
                '--property=TasksMax=48',
                '--property=CPUQuota=180%',
                '--collect',
                '--wait',
                '--pipe',
                '/bin/bash',
                script_path,
            ]
        else:
            cmd = ['/bin/bash', script_path]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
        combined = ((proc.stdout or '') + '\n' + (proc.stderr or '')).strip()
        return proc.returncode, combined[-6000:]
    finally:
        try:
            os.unlink(script_path)
        except OSError:
            pass


def build_and_enable_php_version(
    ver: str,
    settings: Dict[str, str],
    release_override: str = '',
    force_rebuild: bool = False,
    apps_dir: pathlib.Path = APPS_DIR,
) -> Dict[str, Any]:
    """Compile (if needed) and enable OpenSwoole for a single Webuzo PHP version."""
    if not re.fullmatch(r'php\d{2,3}', ver):
        return {'success': False, 'version': ver, 'error': 'Invalid PHP version identifier'}

    STORE_DIR.mkdir(parents=True, exist_ok=True)
    versions = discover_php_versions(apps_dir=apps_dir, disabled_versions=set())
    meta = versions.get(ver)
    if not meta:
        return {'success': False, 'version': ver, 'error': f'PHP version {ver} is not installed'}

    if not meta['compatible_versions']:
        return {'success': False, 'version': ver, 'error': f"PHP {meta['php_version'] or ver} is not supported by OpenSwoole PECL"}

    if not meta['phpize'] or not meta['php_config']:
        return {'success': False, 'version': ver, 'error': f'phpize/php-config missing for {ver}'}

    ext_dir = meta['extension_dir'] or meta['php_config_ext_dir']
    if not ext_dir:
        return {'success': False, 'version': ver, 'error': f'Could not resolve extension_dir for {ver}'}

    so_target = pathlib.Path(ext_dir) / 'openswoole.so'
    ini_target = pathlib.Path(meta['ini_file'])

    def _record_state(ok: bool, release_used: str = '', err: str = '') -> None:
        st = read_json_safe(STATE_FILE, {}) or {}
        if not isinstance(st, dict):
            st = {}
        st.setdefault('versions', {})
        prev = st['versions'].get(ver, {})
        fails = 0 if ok else int(prev.get('consecutive_failures', 0)) + 1
        st['versions'][ver] = {
            'php_version': meta['php_version'],
            'php_version_id': meta['php_version_id'],
            'openswoole_release': release_used or prev.get('openswoole_release', ''),
            'provisioned': ok,
            'last_build_at': int(time.time()),
            'last_error': '' if ok else err[:500],
            'consecutive_failures': fails,
        }
        st['updated_at'] = int(time.time())
        atomic_write_json(STATE_FILE, st, mode=0o640)

    # Fast enable path when matching .so is already built and loads cleanly
    if not force_rebuild and so_target.is_file():
        atomic_write_text(ini_target, render_openswoole_ini(settings), mode=0o644)
        verify = subprocess.run([meta['php_bin'], '-d', 'display_startup_errors=1', '-r', 'exit(extension_loaded("openswoole") ? 0 : 2);'], capture_output=True, text=True, timeout=10)
        if verify.returncode == 0:
            reload_ok, reload_msg = reload_php_runtime(ver)
            _record_state(True, meta.get('openswoole_version') or meta.get('recommended_release', ''))
            return {
                'success': True,
                'version': ver,
                'action': 'enabled_existing',
                'openswoole_release': meta.get('openswoole_version') or meta.get('recommended_release', ''),
                'extension_dir': ext_dir,
                'reload_ok': reload_ok,
                'reload_message': reload_msg,
            }

    candidates = [release_override] if release_override else list(meta['compatible_versions'])
    jobs = max(1, min(2, os.cpu_count() or 1))
    last_err = ''
    php_cfg_ext = meta.get('php_config_ext_dir') or ext_dir

    with open(LOCK_FILE, 'a', encoding='utf-8') as lf:
        if fcntl is not None:
            fcntl.flock(lf, fcntl.LOCK_EX)
        try:
            for rel in candidates:
                try:
                    tgz = download_pecl_tarball(rel)
                except Exception as exc:
                    last_err = str(exc)
                    continue

                build_flags = [
                    '--enable-swoole-curl' if (flag == '--enable-hook-curl' and rel.startswith('4.')) else flag
                    for flag in DEFAULT_BUILD_FLAGS
                ]
                cxx_flags = 'CXXFLAGS="-O2 -g -include cstdint"'
                build_work = f'/var/tmp/uniselv-osw-build-{ver}-{os.getpid()}'
                compile_sh = (
                    '#!/bin/bash\n'
                    'set -euo pipefail\n'
                    f'WORKDIR="{build_work}"\n'
                    'rm -rf "$WORKDIR"\n'
                    'mkdir -p "$WORKDIR"\n'
                    'trap \'rm -rf "$WORKDIR"\' EXIT\n'
                    f'tar -xzf "{tgz}" -C "$WORKDIR"\n'
                    f'SRCDIR="$WORKDIR/openswoole-{rel}"\n'
                    'if [ ! -d "$SRCDIR" ]; then SRCDIR=$(find "$WORKDIR" -mindepth 1 -maxdepth 1 -type d | head -n 1); fi\n'
                    'cd "$SRCDIR"\n'
                    f'"{meta["phpize"]}"\n'
                    f'{cxx_flags} ./configure --with-php-config="{meta["php_config"]}" ' + ' '.join(build_flags) + '\n'
                    f'make -j{jobs} {cxx_flags}\n'
                    'make install\n'
                    f'BUILT_SO="{php_cfg_ext}/openswoole.so"\n'
                    f'TARGET_SO="{so_target}"\n'
                    'if [ ! -f "$BUILT_SO" ] && [ -f "$SRCDIR/modules/openswoole.so" ]; then BUILT_SO="$SRCDIR/modules/openswoole.so"; fi\n'
                    f'mkdir -p "{ext_dir}"\n'
                    'if [ "$BUILT_SO" != "$TARGET_SO" ]; then cp -f "$BUILT_SO" "$TARGET_SO"; fi\n'
                    'chmod 0755 "$TARGET_SO"\n'
                )
                rc, out = _run_compile_step_isolated(compile_sh, ver)
                if rc != 0:
                    tail = ' | '.join(out.splitlines()[-8:])
                    last_err = f'OpenSwoole {rel} build failed (rc={rc}): {tail}'
                    continue

                atomic_write_text(ini_target, render_openswoole_ini(settings), mode=0o644)
                verify = subprocess.run(
                    [meta['php_bin'], '-d', 'display_startup_errors=1', '-r', 'echo phpversion("openswoole"); exit(extension_loaded("openswoole") ? 0 : 2);'],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if verify.returncode != 0:
                    last_err = f'Compiled {rel} but PHP failed to load extension: {(verify.stderr or verify.stdout).strip()}'
                    continue

                reload_ok, reload_msg = reload_php_runtime(ver)
                _record_state(True, rel)
                return {
                    'success': True,
                    'version': ver,
                    'action': 'compiled_and_enabled',
                    'openswoole_release': verify.stdout.strip() or rel,
                    'extension_dir': ext_dir,
                    'reload_ok': reload_ok,
                    'reload_message': reload_msg,
                }
        finally:
            if fcntl is not None:
                fcntl.flock(lf, fcntl.LOCK_UN)

    _record_state(False, '', last_err or 'Unknown OpenSwoole build error')
    return {'success': False, 'version': ver, 'error': last_err or 'OpenSwoole build failed'}


def set_php_version_enabled(ver: str, enabled: bool, settings: Dict[str, str], db_path: str, apps_dir: pathlib.Path = APPS_DIR) -> Dict[str, Any]:
    if not re.fullmatch(r'php\d{2,3}', ver):
        return {'success': False, 'error': 'Invalid PHP version'}
    versions = discover_php_versions(apps_dir=apps_dir, disabled_versions=set())
    meta = versions.get(ver)
    if not meta:
        return {'success': False, 'error': f'PHP version {ver} not found'}

    disabled = parse_disabled_versions(settings.get('openswoole_disabled_versions', ''))
    ini_path = pathlib.Path(meta['ini_file'])

    if enabled:
        disabled.discard(ver)
        _update_setting(db_path, 'openswoole_disabled_versions', serialize_disabled_versions(disabled))
        settings['openswoole_disabled_versions'] = serialize_disabled_versions(disabled)
        return build_and_enable_php_version(ver, settings, force_rebuild=False, apps_dir=apps_dir)
    else:
        disabled.add(ver)
        _update_setting(db_path, 'openswoole_disabled_versions', serialize_disabled_versions(disabled))
        if ini_path.is_file():
            ini_path.unlink()
        reload_ok, reload_msg = reload_php_runtime(ver)
        return {'success': True, 'version': ver, 'action': 'disabled', 'reload_ok': reload_ok, 'reload_message': reload_msg}


def _update_setting(db_path: str, key: str, value: str) -> None:
    if not db_path:
        return
    conn = sqlite3.connect(db_path)
    try:
        conn.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', (key, str(value)))
        conn.commit()
    finally:
        conn.close()


def reconcile_new_php_versions(
    db_path: str,
    automatic: bool = True,
    force_all: bool = False,
    apps_dir: pathlib.Path = APPS_DIR,
) -> Dict[str, Any]:
    """Auto-enable OpenSwoole on newly installed Webuzo PHP versions or manual sync."""
    settings = load_openswoole_settings(db_path)
    auto_enabled = str(settings.get('openswoole_auto_install_new_php', '1')) == '1'
    if automatic and not auto_enabled and not force_all:
        return {'success': True, 'skipped': True, 'reason': 'Auto-install for new PHP versions is disabled'}

    disabled = parse_disabled_versions(settings.get('openswoole_disabled_versions', ''))
    versions = discover_php_versions(apps_dir=apps_dir, disabled_versions=disabled)
    state = read_json_safe(STATE_FILE, {}) or {}
    version_state = state.get('versions', {}) if isinstance(state, dict) else {}
    now = int(time.time())

    provisioned: List[Dict[str, Any]] = []
    skipped: List[Dict[str, Any]] = []
    failed: List[Dict[str, Any]] = []

    for ver, meta in versions.items():
        if ver in disabled:
            skipped.append({'version': ver, 'reason': 'manually_disabled'})
            continue
        if not meta['compatible_versions']:
            skipped.append({'version': ver, 'reason': 'unsupported_php_version'})
            continue
        if meta['status'] == 'active':
            if force_all:
                ini_path = pathlib.Path(meta['ini_file'])
                desired = render_openswoole_ini(settings)
                try:
                    current = ini_path.read_text(encoding='utf-8', errors='replace') if ini_path.is_file() else ''
                    if current != desired:
                        atomic_write_text(ini_path, desired, mode=0o644)
                        reload_ok, reload_msg = reload_php_runtime(ver)
                        provisioned.append({
                            'success': True,
                            'version': ver,
                            'action': 'ini_synced',
                            'openswoole_release': meta.get('openswoole_version') or meta.get('recommended_release', ''),
                            'extension_dir': meta.get('extension_dir', ''),
                            'reload_ok': reload_ok,
                            'reload_message': reload_msg,
                        })
                except Exception as exc:
                    failed.append({'success': False, 'version': ver, 'error': str(exc)})
            continue

        prev = version_state.get(ver, {})
        if not force_all:
            # Wait one scan interval (~60s) on first sighting so a mid-flight Webuzo PHP install completes cleanly.
            first_seen = int(prev.get('first_seen_at', 0) or 0)
            if first_seen == 0:
                state.setdefault('versions', {}).setdefault(ver, {})['first_seen_at'] = now
                atomic_write_json(STATE_FILE, state, mode=0o640)
                skipped.append({'version': ver, 'reason': 'waiting_install_stability'})
                continue
            fails = int(prev.get('consecutive_failures', 0) or 0)
            last_attempt = int(prev.get('last_build_at', 0) or 0)
            if fails >= 3 and (now - last_attempt) < 3600:
                skipped.append({'version': ver, 'reason': 'retry_cooldown'})
                continue
            if fails > 0 and (now - last_attempt) < 900:
                skipped.append({'version': ver, 'reason': 'failure_backoff'})
                continue

        res = build_and_enable_php_version(ver, settings, force_rebuild=False, apps_dir=apps_dir)
        if res.get('success'):
            provisioned.append(res)
            _record_audit(db_path, 'system' if automatic else 'admin', 'openswoole_auto_provision', ver, res)
        else:
            failed.append(res)
            _record_audit(db_path, 'system' if automatic else 'admin', 'openswoole_provision_failed', ver, res)

    return {
        'success': len(failed) == 0,
        'provisioned': provisioned,
        'skipped': skipped,
        'failed': failed,
        'total_versions': len(versions),
    }


def _record_audit(db_path: str, actor: str, action: str, target: str, details: Dict[str, Any]) -> None:
    if not db_path or not os.path.exists(db_path):
        return
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            'INSERT INTO audit_log (timestamp, actor, action, target_account, details_json) VALUES (?, ?, ?, ?, ?)',
            (int(time.time()), actor, action, target, json.dumps(details)),
        )
        conn.commit()
    except Exception:
        pass
    finally:
        conn.close()


def _record_event_dedup(collector: Any, uname: str, uid: int, event_type: str, severity: str, message: str, details: Dict[str, Any], cooldown_sec: int = 120) -> None:
    now = time.time()
    cache = getattr(collector, '_openswoole_event_ts', None)
    if cache is None:
        cache = {}
        setattr(collector, '_openswoole_event_ts', cache)
    key = (uid, event_type)
    if (now - cache.get(key, 0.0)) < cooldown_sec:
        return
    cache[key] = now
    try:
        collector.record_event(uname, uid, event_type, severity, message, details)
    except Exception:
        pass


def load_openswoole_policies(db_path: str) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, Dict[str, Any]]]:
    plan_policies: Dict[str, Dict[str, Any]] = {}
    account_policies: Dict[str, Dict[str, Any]] = {}
    if not db_path or not os.path.exists(db_path):
        return plan_policies, account_policies
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        for row in conn.execute('SELECT * FROM openswoole_plan_policies').fetchall():
            plan_policies[row['plan_name']] = dict(row)
        for row in conn.execute('SELECT * FROM openswoole_account_policies').fetchall():
            account_policies[row['username']] = dict(row)
    except Exception:
        pass
    finally:
        conn.close()
    return plan_policies, account_policies


def compute_account_policy(
    username: str,
    uid: int,
    plan_name: str,
    limits: Dict[str, Any],
    settings: Dict[str, str],
    plan_policy: Optional[Dict[str, Any]] = None,
    account_policy: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Derive effective OpenSwoole resource limits strictly bound to the user's assigned resources."""
    cpuquota = max(25, int(limits.get('cpuquota', 100) or 100))
    mem_max_bytes = max(128 * 1024 * 1024, int(limits.get('mem_max', 512 * 1024 * 1024) or 512 * 1024 * 1024))
    mem_max_mib = max(128, int(mem_max_bytes // (1024 * 1024)))
    maxtask = max(16, int(limits.get('maxtask', 64) or 64))

    try:
        worker_rss_mib = max(64, min(512, int(settings.get('openswoole_worker_rss_mib', '128'))))
    except (ValueError, TypeError):
        worker_rss_mib = 128
    try:
        global_cap = max(1, min(64, int(settings.get('openswoole_global_max_workers', '4'))))
    except (ValueError, TypeError):
        global_cap = 4

    cpu_workers = max(1, cpuquota // 100)
    # Keep 256 MiB base reserve (OS/FPM/OPcache overhead inside account slice) when RAM >= 512 MiB.
    reserve_mib = 256 if mem_max_mib >= 512 else 128
    mem_workers = max(1, (mem_max_mib - reserve_mib) // worker_rss_mib)
    tasks_workers = max(1, maxtask // 8)
    auto_workers = max(1, min(cpu_workers, mem_workers, tasks_workers, global_cap))

    # Resolve allow/deny inheritance: Account override -> Plan policy -> Global default (Allowed)
    allowed = True
    policy_source = 'plan_derived'
    if plan_policy is not None:
        allowed = bool(int(plan_policy.get('allowed', 1)))
        policy_source = f'plan:{plan_name}'
    if account_policy is not None and int(account_policy.get('allowed', -1)) in (0, 1):
        allowed = bool(int(account_policy['allowed']))
        policy_source = 'account_override'

    worker_override = 0
    if plan_policy and int(plan_policy.get('max_workers_override', 0) or 0) > 0:
        worker_override = int(plan_policy['max_workers_override'])
    if account_policy and int(account_policy.get('max_workers_override', 0) or 0) > 0:
        worker_override = int(account_policy['max_workers_override'])

    # Never let an operator override allocate more workers than hard 64 MiB/worker account memory ceiling unless explicitly zeroed by deny.
    hard_mem_ceiling = max(1, mem_max_mib // 64)
    effective_workers = auto_workers if worker_override <= 0 else min(64, max(1, worker_override), hard_mem_ceiling)
    if not allowed:
        effective_workers = 0

    task_override = -1
    if plan_policy and int(plan_policy.get('max_task_workers_override', -1)) >= 0:
        task_override = int(plan_policy['max_task_workers_override'])
    if account_policy and int(account_policy.get('max_task_workers_override', -1)) >= 0:
        task_override = int(account_policy['max_task_workers_override'])

    if not allowed:
        effective_task_workers = 0
    elif task_override >= 0:
        effective_task_workers = min(effective_workers * 2, task_override)
    else:
        effective_task_workers = 0 if (effective_workers == 1 and mem_max_mib < 1024) else max(0, min(effective_workers, effective_workers // 2))

    return {
        'username': username,
        'uid': uid,
        'plan_name': plan_name,
        'allowed': allowed,
        'policy_source': policy_source,
        'max_workers': effective_workers,
        'auto_calculated_workers': auto_workers,
        'max_task_workers': effective_task_workers,
        'worker_rss_budget_mib': worker_rss_mib,
        'assigned_cpu_quota_pct': cpuquota,
        'assigned_mem_max_mib': mem_max_mib,
        'assigned_tasks_max': maxtask,
        'expected_cgroup': expected_account_cgroup(uid),
        'expected_slice': expected_account_slice_name(uid),
        'enforcement_mode': settings.get('openswoole_enforcement_mode', 'enforce'),
        'strict_cgroup': str(settings.get('openswoole_strict_cgroup', '1')) == '1',
    }


def export_policy_manifest(collector: Any, db_path: str) -> Dict[int, Dict[str, Any]]:
    """Persist non-sensitive per-UID OpenSwoole quotas so helpers/launchers can read their assigned limits."""
    settings = load_openswoole_settings(db_path)
    plan_policies, account_policies = load_openswoole_policies(db_path)
    users = collector.get_webuzo_users()
    by_uid: Dict[int, Dict[str, Any]] = {}
    for uname, udata in users.items():
        uid = int(udata.get('uid', 0) or 0)
        if uid < 1000:
            continue
        plan_name = udata.get('plan_name', 'default')
        limits = collector.get_user_limits(uid, plan_name)
        pol = compute_account_policy(
            uname,
            uid,
            plan_name,
            limits,
            settings,
            plan_policies.get(plan_name),
            account_policies.get(uname),
        )
        by_uid[uid] = pol
    try:
        STORE_DIR.mkdir(parents=True, exist_ok=True)
        payload = {'generated_at': int(time.time()), 'accounts_by_uid': {str(k): v for k, v in by_uid.items()}}
        atomic_write_json(POLICY_EXPORT_FILE, payload, mode=0o644)
    except Exception:
        pass
    return by_uid


def _classify_openswoole_role(cmdline: str, comm: str) -> str:
    low = (cmdline + ' ' + comm).lower()
    if 'task_worker' in low or 'task worker' in low or 'swoole: task' in low or 'taskworker' in low:
        return 'task'
    if 'worker' in low or 'octane:worker' in low or 'swoole: worker' in low:
        return 'worker'
    if 'manager' in low or 'swoole: manager' in low:
        return 'manager'
    if 'reactor' in low:
        return 'reactor'
    if 'master' in low or 'octane:start' in low or 'artisan octane' in low:
        return 'master'
    return 'app'


def _read_listening_socket_inodes() -> set:
    """Collect socket inodes actively in TCP/TCP6 LISTEN state (st == 0A)."""
    inodes = set()
    for path in ('/proc/net/tcp', '/proc/net/tcp6'):
        try:
            with open(path, 'r', encoding='utf-8', errors='replace') as fh:
                next(fh, None)
                for line in fh:
                    cols = line.split()
                    if len(cols) >= 10 and cols[3] == '0A':
                        inodes.add(cols[9])
        except Exception:
            continue
    return inodes


def _pid_holds_listening_socket(pid: int, listening_inodes: set) -> bool:
    if not listening_inodes:
        return False
    fddir = f'/proc/{pid}/fd'
    try:
        for fd in os.listdir(fddir):
            try:
                target = os.readlink(f'{fddir}/{fd}')
                if target.startswith('socket:[') and target.endswith(']'):
                    if target[8:-1] in listening_inodes:
                        return True
            except OSError:
                continue
    except OSError:
        pass
    return False


def _pid_loads_openswoole(pid: int) -> bool:
    try:
        maps = pathlib.Path(f'/proc/{pid}/maps').read_text(encoding='utf-8', errors='replace')
        return ('openswoole.so' in maps) or ('swoole.so' in maps)
    except Exception:
        return False


def _is_openswoole_cmdline(cmdline: str, comm: str, exe_path: str) -> bool:
    if 'php-fpm' in exe_path or 'php-fpm' in comm.lower() or 'httpd' in exe_path:
        return False
    low = (cmdline + ' ' + comm).lower()
    return any(tok in low for tok in ('openswoole', 'swoole', 'octane:start', 'octane:watch', 'swoole_http', 'swoole_server'))


def _is_openswoole_process(
    cmdline: str,
    comm: str,
    exe_path: str,
    pid: int,
    listening_inodes: Optional[set] = None,
) -> bool:
    if 'php-fpm' in exe_path or 'php-fpm' in comm.lower() or 'httpd' in exe_path:
        return False
    if _is_openswoole_cmdline(cmdline, comm, exe_path):
        return True
    if ('php' in comm.lower() or '/php' in exe_path) and listening_inodes:
        if _pid_holds_listening_socket(pid, listening_inodes) and _pid_loads_openswoole(pid):
            return True
    return False


def _infer_tree_roles(found: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Infer Master -> Manager -> Worker topology when custom swoole process titles are absent."""
    by_uid_procs: Dict[int, List[Dict[str, Any]]] = {}
    for p in found:
        by_uid_procs.setdefault(p['uid'], []).append(p)
    for u_list in by_uid_procs.values():
        pid_map = {p['pid']: p for p in u_list}
        children: Dict[int, List[int]] = {}
        for p in u_list:
            children.setdefault(p['ppid'], []).append(p['pid'])
        for p in u_list:
            if p.get('role') != 'app':
                continue
            kids = children.get(p['pid'], [])
            parent_in_tree = p['ppid'] in pid_map
            if not parent_in_tree and kids:
                p['role'] = 'master'
            elif parent_in_tree and kids:
                p['role'] = 'manager'
            elif parent_in_tree and not kids:
                parent_role = pid_map.get(p['ppid'], {}).get('role', '')
                if parent_role in ('master', 'manager', 'app') or children.get(pid_map.get(p['ppid'], {}).get('ppid', -1)):
                    p['role'] = 'worker'
    return found


def scan_openswoole_processes(users: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Enumerate all customer-owned OpenSwoole/Octane processes and verify their cgroup boundary."""
    uid_to_name = {int(v['uid']): k for k, v in users.items() if int(v.get('uid', 0) or 0) >= 1000}
    if not uid_to_name:
        return []

    listening_inodes = _read_listening_socket_inodes()
    page_size = os.sysconf('SC_PAGE_SIZE') if hasattr(os, 'sysconf') else 4096

    found: List[Dict[str, Any]] = []
    confirmed_pids = set()
    candidates: List[Dict[str, Any]] = []

    for entry in os.listdir('/proc'):
        if not entry.isdigit():
            continue
        pid = int(entry)
        pdir = pathlib.Path('/proc') / entry
        try:
            st = os.stat(pdir)
            uid = st.st_uid
            if uid not in uid_to_name:
                continue
            exe = ''
            try:
                exe = os.readlink(pdir / 'exe')
            except Exception:
                pass
            stat_txt = (pdir / 'stat').read_text(encoding='utf-8', errors='replace')
            rp = stat_txt.rfind(')')
            lp = stat_txt.find('(')
            comm = stat_txt[lp + 1:rp] if lp != -1 and rp != -1 else ''
            parts = stat_txt[rp + 2:].split() if rp != -1 else []
            ppid = int(parts[1]) if len(parts) > 1 else 0
            threads = int(parts[17]) if len(parts) > 17 else 1
            start_ticks = int(parts[19]) if len(parts) > 19 else 0
            rss_pages = int(parts[21]) if len(parts) > 21 else 0

            raw_cmd = (pdir / 'cmdline').read_bytes().replace(b'\x00', b' ').decode('utf-8', errors='replace').strip()
            if 'php-fpm' in exe or 'php-fpm' in comm.lower() or 'httpd' in exe:
                continue

            is_direct = _is_openswoole_process(raw_cmd, comm, exe, pid, listening_inodes)
            is_php_cli = 'php' in comm.lower() or '/php' in exe
            if not is_direct and not is_php_cli:
                continue

            cg = (pdir / 'cgroup').read_text(encoding='utf-8', errors='replace').strip()
            exp_cg = expected_account_cgroup(uid)
            contained = cg == f'0::{exp_cg}' or cg.startswith(f'0::{exp_cg}/')
            php_ver = ''
            m = re.search(r'/usr/local/apps/(php\d{2,3})/', exe or raw_cmd)
            if m:
                php_ver = m.group(1)

            rec = {
                'pid': pid,
                'ppid': ppid,
                'uid': uid,
                'username': uid_to_name[uid],
                'comm': comm,
                'cmdline': raw_cmd[:220],
                'exe': exe,
                'php_version': php_ver,
                'role': _classify_openswoole_role(raw_cmd, comm),
                'rss_bytes': rss_pages * page_size,
                'threads': threads,
                'start_ticks': start_ticks,
                'current_cgroup': cg,
                'expected_cgroup': exp_cg,
                'contained': contained,
            }
            if is_direct:
                found.append(rec)
                confirmed_pids.add(pid)
            else:
                candidates.append(rec)
        except (FileNotFoundError, ProcessLookupError, PermissionError):
            continue
        except Exception:
            continue

    # Promote child manager/worker PHP processes descended from any confirmed OpenSwoole master/manager.
    for _ in range(4):
        progressed = False
        remaining = []
        for cand in candidates:
            if cand['ppid'] in confirmed_pids and _pid_loads_openswoole(cand['pid']):
                found.append(cand)
                confirmed_pids.add(cand['pid'])
                progressed = True
            else:
                remaining.append(cand)
        candidates = remaining
        if not progressed or not candidates:
            break

    return _infer_tree_roles(found)


def contain_process_in_account_slice(uid: int, pid: int) -> Tuple[bool, str]:
    """Place an escaped OpenSwoole process inside the user's assigned cgroup v2 slice."""
    if not pathlib.Path(f'/proc/{pid}').exists():
        return False, 'Process exited'
    try:
        if pathlib.Path(f'/proc/{pid}').stat().st_uid != uid:
            return False, 'UID ownership changed'
    except OSError as exc:
        return False, str(exc)

    slice_name = expected_account_slice_name(uid)
    if slice_name.startswith('golden-'):
        unit = f'uniselv-osw-u{uid}-p{pid}-{time.time_ns()}.scope'
        cmd = [
            '/usr/bin/busctl', 'call',
            'org.freedesktop.systemd1', '/org/freedesktop/systemd1',
            'org.freedesktop.systemd1.Manager', 'StartTransientUnit',
            'ssa(sv)a(sa(sv))',
            unit, 'fail', '3',
            'Slice', 's', slice_name,
            'PIDs', 'au', '1', str(pid),
            'MemorySwapMax', 't', '0',
            '0',
        ]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if r.returncode == 0:
            return True, f'Contained PID {pid} in {slice_name}'
        subprocess.run(['systemctl', 'reset-failed', unit], capture_output=True, text=True, timeout=5)
        return False, (r.stderr or r.stdout).strip()[:200]
    else:
        target = pathlib.Path(f'/sys/fs/cgroup/{uid}.slice/cgroup.procs')
        if not target.exists():
            return False, f'Missing cgroup target {target}'
        target.write_text(str(pid), encoding='utf-8')
        return True, f'Moved PID {pid} to /{uid}.slice'


def enforce_runtime_policies(collector: Any, db_path: str) -> Dict[str, Any]:
    """Verify every OpenSwoole process obeys user cgroups v2 slice and assigned worker quotas."""
    settings = load_openswoole_settings(db_path)
    users = collector.get_webuzo_users()
    policies_by_uid = export_policy_manifest(collector, db_path)
    procs = scan_openswoole_processes(users)

    contained_moves = 0
    terminated_pids: List[int] = []
    violations: List[Dict[str, Any]] = []
    strict_cgroup = str(settings.get('openswoole_strict_cgroup', '1')) == '1'
    mode = str(settings.get('openswoole_enforcement_mode', 'enforce')).lower()

    # 1. Cgroup containment check first (applies in both monitor and enforce when strict_cgroup is enabled)
    for proc in procs:
        if not proc['contained']:
            uid = proc['uid']
            uname = proc['username']
            if strict_cgroup:
                ok, msg = contain_process_in_account_slice(uid, proc['pid'])
                if ok:
                    contained_moves += 1
                    proc['contained'] = True
                    _record_audit(db_path, 'system', 'openswoole_cgroup_contained', uname, {'pid': proc['pid'], 'msg': msg})
                _record_event_dedup(
                    collector, uname, uid, 'openswoole_cgroup_escape', 'warning',
                    f"OpenSwoole process PID {proc['pid']} was placed into assigned slice {expected_account_slice_name(uid)}.",
                    {'pid': proc['pid'], 'orig_cgroup': proc['current_cgroup'], 'contained': ok, 'detail': msg},
                )
            else:
                _record_event_dedup(
                    collector, uname, uid, 'openswoole_cgroup_escape', 'warning',
                    f"OpenSwoole process PID {proc['pid']} detected outside assigned slice {expected_account_slice_name(uid)}.",
                    {'pid': proc['pid'], 'orig_cgroup': proc['current_cgroup']},
                )

    # 2. Group by UID and evaluate account allowance + worker cap
    by_uid: Dict[int, List[Dict[str, Any]]] = {}
    for p in procs:
        by_uid.setdefault(p['uid'], []).append(p)

    repeat_tracker = getattr(collector, '_openswoole_overlimit_strikes', None)
    if repeat_tracker is None:
        repeat_tracker = {}
        setattr(collector, '_openswoole_overlimit_strikes', repeat_tracker)

    now = time.time()
    for uid, u_procs in by_uid.items():
        pol = policies_by_uid.get(uid)
        if not pol:
            continue
        uname = pol['username']

        # Case A: OpenSwoole is disabled for this account/plan
        if not pol['allowed']:
            violations.append({'uid': uid, 'username': uname, 'reason': 'openswoole_disabled', 'pids': [p['pid'] for p in u_procs]})
            if mode == 'enforce':
                for p in sorted(u_procs, key=lambda x: x['pid'], reverse=True):
                    if _safe_stop_pid(uid, p['pid'], p['start_ticks']):
                        terminated_pids.append(p['pid'])
                _record_audit(db_path, 'system', 'openswoole_blocked_stopped', uname, {'pids': [p['pid'] for p in u_procs], 'policy': pol['policy_source']})
                _record_event_dedup(
                    collector, uname, uid, 'openswoole_policy_blocked', 'critical',
                    'Unauthorized OpenSwoole processes were terminated because OpenSwoole is disabled on this account/plan.',
                    {'terminated_pids': [p['pid'] for p in u_procs]},
                )
            else:
                _record_event_dedup(
                    collector, uname, uid, 'openswoole_policy_blocked', 'warning',
                    'OpenSwoole activity detected on an account where OpenSwoole is disabled (monitor mode).',
                    {'pids': [p['pid'] for p in u_procs]},
                )
            continue

        # Case B: Worker / task worker ceiling enforcement
        workers = [p for p in u_procs if p['role'] == 'worker']
        tasks = [p for p in u_procs if p['role'] == 'task']
        # If process names do not tag roles cleanly (single-process OpenSwoole servers), count app processes only above limit.
        apps = [p for p in u_procs if p['role'] == 'app']
        effective_worker_count = len(workers) if workers else len(apps)
        total_allowed = int(pol['max_workers'])
        total_task_allowed = int(pol['max_task_workers'])

        over_workers = effective_worker_count > total_allowed
        over_tasks = len(tasks) > total_task_allowed
        if not (over_workers or over_tasks):
            repeat_tracker.pop(uid, None)
            continue

        violations.append({
            'uid': uid,
            'username': uname,
            'reason': 'worker_budget_exceeded',
            'active_workers': effective_worker_count,
            'max_workers': total_allowed,
            'active_task_workers': len(tasks),
            'max_task_workers': total_task_allowed,
        })

        if mode == 'enforce':
            excess: List[Dict[str, Any]] = []
            if over_workers:
                pool = sorted(workers or apps, key=lambda x: x['pid'], reverse=True)
                excess.extend(pool[: max(0, len(pool) - total_allowed)])
            if over_tasks:
                t_pool = sorted(tasks, key=lambda x: x['pid'], reverse=True)
                excess.extend(t_pool[: max(0, len(t_pool) - total_task_allowed)])

            strikes, last_ts = repeat_tracker.get(uid, (0, 0.0))
            strikes = (strikes + 1) if (now - last_ts) < 90 else 1
            repeat_tracker[uid] = (strikes, now)

            # Stop excess workers immediately; when a Swoole master+manager supervisor tree exceeds plan budget,
            # killing only leaf workers triggers instant Manager respawns, so shut down the supervisor root cleanly.
            targets = list(excess)
            masters = [p for p in u_procs if p['role'] == 'master']
            has_manager = any(p['role'] == 'manager' for p in u_procs)
            if (masters and has_manager) or strikes >= 2:
                supervisors = [p for p in u_procs if p['role'] in ('master', 'manager')]
                targets = sorted(masters or supervisors or excess, key=lambda x: x['pid'])
                repeat_tracker[uid] = (0, now)

            stopped_here = []
            for p in targets:
                if _safe_stop_pid(uid, p['pid'], p['start_ticks']):
                    terminated_pids.append(p['pid'])
                    stopped_here.append(p['pid'])

            _record_audit(db_path, 'system', 'openswoole_worker_cap_enforced', uname, {
                'active_workers': effective_worker_count,
                'max_workers': total_allowed,
                'active_task_workers': len(tasks),
                'max_task_workers': total_task_allowed,
                'stopped_pids': stopped_here,
                'strikes': strikes,
            })
            _record_event_dedup(
                collector, uname, uid, 'openswoole_worker_cap', 'warning',
                f'OpenSwoole exceeded assigned plan budget ({effective_worker_count}/{total_allowed} workers); excess processes constrained.',
                {'stopped_pids': stopped_here, 'max_workers': total_allowed},
            )
        else:
            _record_event_dedup(
                collector, uname, uid, 'openswoole_worker_cap', 'warning',
                f'OpenSwoole running {effective_worker_count} workers above assigned budget ({total_allowed}).',
                {'active_workers': effective_worker_count, 'max_workers': total_allowed},
            )

    return {
        'scanned': len(procs),
        'contained_moves': contained_moves,
        'terminated_pids': terminated_pids,
        'violations': violations,
    }


def _safe_stop_pid(expected_uid: int, pid: int, expected_start_ticks: int) -> bool:
    """Verify UID and start time right before signaling to eliminate PID reuse race conditions."""
    pdir = pathlib.Path(f'/proc/{pid}')
    try:
        if not pdir.exists():
            return False
        if pdir.stat().st_uid != expected_uid:
            return False
        stat_txt = (pdir / 'stat').read_text(encoding='utf-8', errors='replace')
        rp = stat_txt.rfind(')')
        parts = stat_txt[rp + 2:].split() if rp != -1 else []
        actual_start = int(parts[19]) if len(parts) > 19 else -1
        if expected_start_ticks and actual_start != expected_start_ticks:
            return False
        os.kill(pid, signal.SIGTERM)
        return True
    except (FileNotFoundError, ProcessLookupError, PermissionError, OSError):
        return False


def build_launch_guidance(policy: Dict[str, Any], php_versions: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    active_phps = [v for v, m in sorted(php_versions.items()) if m.get('status') == 'active']
    pref_php = 'php84' if 'php84' in active_phps else (active_phps[-1] if active_phps else 'php84')
    php_bin = f'/usr/local/apps/{pref_php}/bin/php'
    w = max(1, int(policy.get('max_workers', 1) or 1))
    tw = max(0, int(policy.get('max_task_workers', 0) or 0))
    mem_mb = int(policy.get('assigned_mem_max_mib', 512) or 512)
    per_worker_ini = max(128, min(512, mem_mb // max(1, w + tw + 1)))
    slice_name = policy.get('expected_slice', '')
    return {
        'preferred_php_bin': php_bin,
        'active_php_versions': active_phps,
        'recommended_octane_command': (
            f'{php_bin} -d memory_limit={per_worker_ini}M artisan octane:start '
            f'--server=swoole --workers={w} --task-workers={tw} --max-requests=500'
        ),
        'recommended_swoole_set': {
            'worker_num': w,
            'task_worker_num': tw,
            'max_request': 500,
        },
        'cgroup_slice': slice_name,
    }


def get_admin_status_payload(collector: Any, db_path: str) -> Dict[str, Any]:
    settings = load_openswoole_settings(db_path)
    disabled = parse_disabled_versions(settings.get('openswoole_disabled_versions', ''))
    php_versions = discover_php_versions(disabled_versions=disabled)
    users = collector.get_webuzo_users()
    plan_policies, account_policies = load_openswoole_policies(db_path)
    live_procs = scan_openswoole_processes(users)
    job = read_json_safe(JOB_FILE)

    if job and job.get('state') == 'running' and job.get('agentPid') not in (None, os.getpid()):
        job = dict(job, state='interrupted', error='Agent restarted while OpenSwoole job was running')

    # Summarize per plan
    plan_names = sorted({udata.get('plan_name', 'default') for udata in users.values()})
    cgroups_dir = pathlib.Path('/var/webuzo/cgroups')
    if cgroups_dir.is_dir():
        for pf in sorted(cgroups_dir.iterdir()):
            if pf.is_file() and pf.name not in plan_names:
                plan_names.append(pf.name)

    plans_summary = []
    for pname in sorted(set(plan_names)):
        limits = collector.get_plan_limits(pname)
        pol = compute_account_policy('_plan_' + pname, 0, pname, limits, settings, plan_policies.get(pname), None)
        p_row = plan_policies.get(pname, {})
        plans_summary.append({
            'plan_name': pname,
            'allowed': pol['allowed'],
            'max_workers': pol['max_workers'],
            'auto_calculated_workers': pol['auto_calculated_workers'],
            'max_task_workers': pol['max_task_workers'],
            'max_workers_override': int(p_row.get('max_workers_override', 0) or 0),
            'max_task_workers_override': int(p_row.get('max_task_workers_override', -1)),
            'cpuquota': limits.get('cpuquota', 100),
            'mem_max_mib': round(int(limits.get('mem_max', 0)) / (1024 * 1024)),
            'maxtask': limits.get('maxtask', 64),
        })

    # Per account effective policy + active OpenSwoole counts
    proc_by_uid: Dict[int, List[Dict[str, Any]]] = {}
    for p in live_procs:
        proc_by_uid.setdefault(p['uid'], []).append(p)

    accounts_summary = []
    for uname, udata in sorted(users.items()):
        uid = int(udata.get('uid', 0) or 0)
        if uid < 1000:
            continue
        pname = udata.get('plan_name', 'default')
        limits = collector.get_user_limits(uid, pname)
        pol = compute_account_policy(uname, uid, pname, limits, settings, plan_policies.get(pname), account_policies.get(uname))
        a_row = account_policies.get(uname, {})
        u_procs = proc_by_uid.get(uid, [])
        workers = [p for p in u_procs if p['role'] in ('worker', 'app')]
        accounts_summary.append({
            **pol,
            'override_allowed': int(a_row.get('allowed', -1)) if a_row else -1,
            'override_max_workers': int(a_row.get('max_workers_override', 0) or 0) if a_row else 0,
            'override_max_task_workers': int(a_row.get('max_task_workers_override', -1)) if a_row else -1,
            'active_process_count': len(u_procs),
            'active_worker_count': len(workers),
            'active_rss_mib': round(sum(p['rss_bytes'] for p in u_procs) / (1024 * 1024), 1),
            'escaped_count': sum(1 for p in u_procs if not p['contained']),
        })

    return {
        'success': True,
        'settings': settings,
        'php_versions': php_versions,
        'plans': plans_summary,
        'accounts': accounts_summary,
        'live_processes': live_procs,
        'audit_logs': recent_openswoole_audit(db_path),
        'job': job,
    }


def recent_openswoole_audit(db_path: str, limit: int = 25) -> List[Dict[str, Any]]:
    """Return recent OpenSwoole provisioning, policy, containment, and self-test audit rows."""
    if not db_path or not os.path.exists(db_path):
        return []
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            """SELECT id, timestamp, actor, action, target_account, details_json
               FROM audit_log
               WHERE action LIKE '%openswoole%'
               ORDER BY id DESC LIMIT ?""",
            (max(1, min(100, int(limit))),),
        ).fetchall()
        out = []
        for r in rows:
            d = dict(r)
            try:
                d['details'] = json.loads(d.get('details_json') or '{}')
            except Exception:
                d['details'] = {}
            d.pop('details_json', None)
            out.append(d)
        return out
    except Exception:
        return []
    finally:
        conn.close()


def run_openswoole_readiness_check(db_path: str, apps_dir: pathlib.Path = APPS_DIR) -> Dict[str, Any]:
    """Audit all installed PHP runtimes, extension_dir/INI parity, build toolchain, and policy manifest."""
    settings = load_openswoole_settings(db_path)
    disabled = parse_disabled_versions(settings.get('openswoole_disabled_versions', ''))
    versions = discover_php_versions(apps_dir=apps_dir, disabled_versions=disabled)
    desired_ini = render_openswoole_ini(settings).strip()

    php_checks: List[Dict[str, Any]] = []
    all_php_ok = True
    for ver, meta in sorted(versions.items()):
        ini_path = pathlib.Path(meta['ini_file'])
        ini_synced = False
        if ini_path.is_file():
            try:
                ini_synced = ini_path.read_text(encoding='utf-8', errors='replace').strip() == desired_ini
            except Exception:
                ini_synced = False
        startup_ok = False
        startup_err = ''
        if meta.get('php_bin'):
            try:
                pr = subprocess.run(
                    [meta['php_bin'], '-d', 'display_startup_errors=1', '-r', 'echo extension_loaded("openswoole") ? "1" : "0";'],
                    capture_output=True,
                    text=True,
                    timeout=8,
                )
                startup_ok = (pr.returncode == 0 and pr.stdout.strip().endswith('1') and 'Warning' not in (pr.stderr or ''))
                if not startup_ok:
                    startup_err = (pr.stderr or pr.stdout or '').strip()[:220]
            except Exception as exc:
                startup_err = str(exc)

        fpm_active = False
        try:
            r_fpm = subprocess.run(['systemctl', 'is-active', f'wpiso-manager-{ver}.service'], capture_output=True, text=True, timeout=5)
            fpm_active = (r_fpm.returncode == 0)
        except Exception:
            pass

        is_disabled = ver in disabled
        row_ok = True if is_disabled else (bool(meta.get('loaded')) and bool(meta.get('so_exists')) and ini_synced and startup_ok)
        if not row_ok and meta.get('compatible_versions'):
            all_php_ok = False

        php_checks.append({
            'version': ver,
            'php_version': meta.get('php_version', ''),
            'status': meta.get('status', ''),
            'openswoole_version': meta.get('openswoole_version', ''),
            'so_exists': bool(meta.get('so_exists')),
            'extension_dir': meta.get('extension_dir', ''),
            'ini_exists': bool(meta.get('ini_exists')),
            'ini_synced': ini_synced,
            'startup_ok': startup_ok,
            'fpm_isolated_active': fpm_active,
            'error': startup_err or meta.get('last_error', ''),
            'passed': row_ok,
        })

    tools_required = ['gcc', 'g++', 'make', 'autoconf', 'curl', 'tar', 'systemd-run', 'busctl']
    toolchain = {t: bool(shutil.which(t)) for t in tools_required}
    toolchain['webuzo_isolation'] = ISOLATION_SCRIPT.is_file()
    policy_manifest_ok = POLICY_EXPORT_FILE.is_file() and (POLICY_EXPORT_FILE.stat().st_size > 10)

    return {
        'success': True,
        'checked_at': int(time.time()),
        'all_passed': all_php_ok and all(toolchain.values()) and policy_manifest_ok,
        'php_checks': php_checks,
        'toolchain': toolchain,
        'policy_manifest_ok': policy_manifest_ok,
        'policy_manifest_path': str(POLICY_EXPORT_FILE),
    }


_SELFTEST_LOCK = threading.Lock()


def run_openswoole_self_test(
    collector: Any,
    db_path: str,
    actor: str = 'root',
    username: str = '',
    php_version: str = '',
) -> Dict[str, Any]:
    """Execute a live, ephemeral loopback self-test proving cgroup containment, worker caps, and cron safety."""
    if not _SELFTEST_LOCK.acquire(blocking=False):
        return {'success': False, 'error': 'Another OpenSwoole self-test is already running'}

    started_at = time.time()
    token = f'{os.getpid()}_{time.time_ns()}'
    steps: List[Dict[str, Any]] = []
    scripts_to_clean: List[pathlib.Path] = []
    units_to_clean: List[str] = []

    try:
        settings = load_openswoole_settings(db_path)
        disabled = parse_disabled_versions(settings.get('openswoole_disabled_versions', ''))
        versions = discover_php_versions(disabled_versions=disabled)
        active_phps = [v for v, m in sorted(versions.items()) if m.get('loaded')]
        if not active_phps:
            return {'success': False, 'error': 'No PHP version with active OpenSwoole found to run self-test.'}

        chosen_php = php_version if (php_version in versions and versions[php_version].get('loaded')) else (
            'php84' if 'php84' in active_phps else active_phps[-1]
        )
        php_bin = versions[chosen_php]['php_bin']

        users = collector.get_webuzo_users()
        candidates = sorted((u, d) for u, d in users.items() if int(d.get('uid', 0) or 0) >= 1000)
        if not candidates:
            return {'success': False, 'error': 'No customer accounts (UID >= 1000) available for live self-test.'}

        if username and username in users and int(users[username].get('uid', 0) or 0) >= 1000:
            chosen_user, udata = username, users[username]
        else:
            chosen_user, udata = candidates[0]

        uid = int(udata['uid'])
        pname = udata.get('plan_name', 'default')
        limits = collector.get_user_limits(uid, pname)
        plan_policies, account_policies = load_openswoole_policies(db_path)
        pol = compute_account_policy(chosen_user, uid, pname, limits, settings, plan_policies.get(pname), account_policies.get(chosen_user))

        # Phase 1: Ordinary PHP CLI cron without listening socket must NEVER be flagged
        cron_flag = _is_openswoole_process(
            f'{php_bin} artisan queue:work --once',
            'php',
            php_bin,
            os.getpid(),
            listening_inodes=set(),
        )
        steps.append({
            'name': 'cron_false_positive_guard',
            'label': 'Ordinary PHP CLI Cron Safety Guard',
            'passed': (cron_flag is False),
            'detail': 'Non-listening PHP CLI process ignored even with openswoole.so loaded globally.' if not cron_flag else 'Unexpectedly flagged non-listening CLI script!',
        })

        systemd_run = shutil.which('systemd-run')
        if not systemd_run or not os.path.isdir('/run/systemd/system'):
            steps.append({
                'name': 'live_sandbox_probe',
                'label': 'Live Cgroup & Worker-Cap Probe',
                'passed': False,
                'detail': 'systemd-run unavailable on host to launch isolated escape probe.',
            })
            return {
                'success': True,
                'all_passed': False,
                'username': chosen_user,
                'uid': uid,
                'plan_name': pname,
                'php_version': chosen_php,
                'policy': pol,
                'steps': steps,
                'elapsed_ms': round((time.time() - started_at) * 1000),
            }

        def _launch_probe(tag: str, workers: int) -> Tuple[str, pathlib.Path, List[Dict[str, Any]]]:
            script_path = pathlib.Path(f'/tmp/osw_st_{token}_{tag}.php')
            scripts_to_clean.append(script_path)
            script_path.write_text(
                '<?php\n'
                '$serverClass = class_exists("OpenSwoole\\\\HTTP\\\\Server") ? "OpenSwoole\\\\HTTP\\\\Server" : "Swoole\\\\Http\\\\Server";\n'
                '$srv = new $serverClass("127.0.0.1", 0);\n'
                f'$srv->set(["worker_num" => {int(workers)}, "daemonize" => false, "log_file" => "/dev/null"]);\n'
                '$srv->on("request", function($req, $res) { $res->end("ok"); });\n'
                '$srv->start();\n',
                encoding='utf-8',
            )
            os.chmod(script_path, 0o644)
            unit = f'uniselv-osw-st-{token}-{tag}'
            units_to_clean.append(unit)
            subprocess.run(
                [systemd_run, f'--unit={unit}', f'--property=User={chosen_user}', f'--property=Group={chosen_user}', php_bin, str(script_path)],
                capture_output=True,
                text=True,
                timeout=10,
            )
            matched: List[Dict[str, Any]] = []
            deadline = time.time() + 2.8
            expected_min = workers + 2  # Master + Manager + workers
            while time.time() < deadline:
                found_all = [p for p in scan_openswoole_processes(users) if str(script_path) in (p.get('cmdline') or '')]
                if len(found_all) >= expected_min:
                    matched = found_all
                    break
                if found_all:
                    matched = found_all
                time.sleep(0.15)
            return unit, script_path, matched

        def _cleanup_probe(unit: str, script_path: pathlib.Path) -> None:
            subprocess.run(['systemctl', 'stop', f'{unit}.service'], capture_output=True, text=True, timeout=8)
            subprocess.run(['pkill', '-9', '-u', chosen_user, '-f', str(script_path)], capture_output=True, text=True, timeout=5)
            try:
                if script_path.exists():
                    script_path.unlink()
            except OSError:
                pass

        # Phase 2: Compliant probe (worker_num = 1) launched in system.slice must be moved into golden-<uid>.slice
        unit_ok, path_ok, before_ok = _launch_probe('ok', 1)
        try:
            orig_cgs = sorted({p['current_cgroup'] for p in before_ok})
            enf_ok = enforce_runtime_policies(collector, db_path)
            after_ok = [p for p in scan_openswoole_processes(users) if str(path_ok) in (p.get('cmdline') or '')]
            all_contained = bool(after_ok) and all(p['contained'] for p in after_ok)
            terminated_set = set(enf_ok.get('terminated_pids', []))
            probe_pids = {p['pid'] for p in before_ok}

            if pol['allowed']:
                kept_alive = bool(after_ok) and not (probe_pids & terminated_set)
                passed2 = bool(before_ok) and all_contained and kept_alive
                detail2 = (
                    f"Detected {len(before_ok)} probe procs outside slice ({', '.join(orig_cgs) or 'n/a'}); "
                    f"moved to {pol['expected_cgroup']} ({len(after_ok)}/{len(before_ok)} contained, 0 killed)."
                )
            else:
                stopped_ok = (len(after_ok) == 0) or bool(probe_pids & terminated_set)
                passed2 = bool(before_ok) and all_contained and stopped_ok
                detail2 = f"Account has OpenSwoole blocked: contained probe and terminated unauthorized launch ({len(probe_pids & terminated_set)} stopped)."

            steps.append({
                'name': 'cgroup_containment_and_budget_allowance',
                'label': f"Cgroup v2 Containment ({pol['expected_slice']}) & Compliant Run",
                'passed': passed2,
                'detail': detail2,
            })
        finally:
            _cleanup_probe(unit_ok, path_ok)

        # Phase 3: Over-budget probe (worker_num = max_workers + 2) when account allows OpenSwoole
        if pol['allowed']:
            over_workers = min(12, max(2, int(pol['max_workers']) + 2))
            unit_bad, path_bad, before_bad = _launch_probe('bad', over_workers)
            try:
                enf_bad = enforce_runtime_policies(collector, db_path)
                time.sleep(0.5)
                after_bad = [p for p in scan_openswoole_processes(users) if str(path_bad) in (p.get('cmdline') or '')]
                probe_bad_pids = {p['pid'] for p in before_bad}
                stopped_bad = probe_bad_pids & set(enf_bad.get('terminated_pids', []))
                has_violation = any(v.get('uid') == uid and v.get('reason') == 'worker_budget_exceeded' for v in enf_bad.get('violations', []))
                mode = str(settings.get('openswoole_enforcement_mode', 'enforce')).lower()
                if mode == 'enforce':
                    passed3 = bool(before_bad) and has_violation and (len(after_bad) == 0 or bool(stopped_bad))
                    detail3 = (
                        f"Launched {over_workers} workers (limit {pol['max_workers']}): violation detected, "
                        f"stopped supervisor PID(s) {sorted(stopped_bad)}, remaining probe procs: {len(after_bad)}."
                    )
                else:
                    passed3 = bool(before_bad) and has_violation
                    detail3 = f"Monitor mode active: detected {over_workers}/{pol['max_workers']} over-budget violation cleanly without killing."

                steps.append({
                    'name': 'worker_cap_enforcement',
                    'label': f"Worker-Cap Enforcement ({over_workers}w > limit {pol['max_workers']}w)",
                    'passed': passed3,
                    'detail': detail3,
                })
            finally:
                _cleanup_probe(unit_bad, path_bad)

        all_passed = all(s['passed'] for s in steps)
        summary = {
            'success': True,
            'all_passed': all_passed,
            'username': chosen_user,
            'uid': uid,
            'plan_name': pname,
            'php_version': chosen_php,
            'policy': pol,
            'steps': steps,
            'elapsed_ms': round((time.time() - started_at) * 1000),
        }
        _record_audit(db_path, actor, 'openswoole_self_test', chosen_user, {
            'php_version': chosen_php,
            'all_passed': all_passed,
            'steps': [{'name': s['name'], 'passed': s['passed']} for s in steps],
        })
        return summary
    finally:
        for u in units_to_clean:
            try:
                subprocess.run(['systemctl', 'stop', f'{u}.service'], capture_output=True, text=True, timeout=5)
            except Exception:
                pass
        for sp in scripts_to_clean:
            try:
                if sp.exists():
                    sp.unlink()
            except OSError:
                pass
        _SELFTEST_LOCK.release()


def get_enduser_status_payload(collector: Any, db_path: str, username: str) -> Dict[str, Any]:
    settings = load_openswoole_settings(db_path)
    disabled = parse_disabled_versions(settings.get('openswoole_disabled_versions', ''))
    php_versions = discover_php_versions(disabled_versions=disabled)
    users = collector.get_webuzo_users()
    udata = users.get(username)
    if not udata:
        return {'success': False, 'error': f'Account {username} not found'}
    uid = int(udata.get('uid', 0) or 0)
    pname = udata.get('plan_name', 'default')
    limits = collector.get_user_limits(uid, pname)
    plan_policies, account_policies = load_openswoole_policies(db_path)
    pol = compute_account_policy(username, uid, pname, limits, settings, plan_policies.get(pname), account_policies.get(username))
    live_procs = [p for p in scan_openswoole_processes({username: udata}) if p['uid'] == uid]

    return {
        'success': True,
        'policy': pol,
        'guidance': build_launch_guidance(pol, php_versions),
        'php_versions': [
            {
                'version': ver,
                'php_version': m['php_version'],
                'status': m['status'],
                'openswoole_version': m['openswoole_version'],
            }
            for ver, m in sorted(php_versions.items())
        ],
        'live_processes': live_procs,
    }
