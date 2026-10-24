"""Root-only runtime governance. No tuning values are invented or written here.
Expected values come from the reviewed generator profile; missing evidence blocks automation.
"""
import collections
import hashlib
import importlib.util
import json
import os
import pathlib
import pwd
import grp
import tempfile
import re
import stat
import subprocess
import time
import fcntl

P = pathlib.Path
VERSION = re.compile(r"php\d{2,3}\Z")
STATE = P('/var/lib/webuzo-isolation')
PROFILE = P('/etc/webuzo-isolation/generator-profile.json')
APPS = P('/usr/local/apps')
NATIVE = P('/var/webuzo/conf/php-fpm')
CONTROL = '/usr/local/sbin/webuzo-isolation.py'
STORE = P('/var/lib/uniselv-resource-manager/governance')
# Protocol/observation bounds, not CPU/RAM recommendations.
SCAN_SECONDS = 60
MAX_SCAN_FILES = 10000
MAX_EXCEPTIONS = 500
MAX_JOURNAL_ROWS = 2000


def read_json(path, default=None):
    if not path.exists():
        return default
    s = path.lstat()
    if not stat.S_ISREG(s.st_mode) or s.st_uid != 0 or s.st_mode & 0o022:
        raise ValueError('Unsafe root configuration: ' + str(path))
    if s.st_size > 8 * 1024 * 1024:
        raise ValueError('Configuration exceeds read limit')
    return json.loads(path.read_text())


def read_native_json():
    # Webuzo owns its native global FPM file (observed webuzo:webuzo, 0770).
    # It is a configuration input, never a recovery journal or trusted executable.
    info = NATIVE.lstat()
    owner = pwd.getpwnam('webuzo')
    if not stat.S_ISREG(info.st_mode) or info.st_uid not in (0, owner.pw_uid) or info.st_mode & 0o002 or (info.st_mode & 0o020 and info.st_gid not in (0,owner.pw_gid)):
        raise ValueError('Unsafe Webuzo native PHP configuration')
    if info.st_size > 8*1024*1024: raise ValueError('Native configuration exceeds read limit')
    return json.loads(NATIVE.read_text())


def write_json(path, value):
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    if path.is_symlink() or path.parent.is_symlink():
        raise ValueError('Unsafe governance storage')
    fd, name = tempfile.mkstemp(prefix=path.name+'.stage-', dir=path.parent)
    temp = P(name)
    try:
        with os.fdopen(fd, 'w') as stream:
            json.dump(value, stream)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
        directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try: os.fsync(directory)
        finally: os.close(directory)
    finally:
        temp.unlink(missing_ok=True)


def command(args, timeout=20):
    r = subprocess.run(args, text=True, capture_output=True, timeout=timeout)
    return r.returncode, r.stdout.strip()


def registry():
    data = read_json(STATE / 'installed.json', {'versions': []})
    versions = data.get('versions')
    if not isinstance(versions, list) or any(not isinstance(v, str) or not VERSION.fullmatch(v) for v in versions):
        raise ValueError('Invalid managed PHP registry')
    return sorted(set(versions))


def installed():
    return sorted(p.name for p in APPS.glob('php*') if VERSION.fullmatch(p.name) and
                  not p.is_symlink() and (p / 'bin/php').is_file() and
                  (p / 'sbin/php-fpm').is_file() and (p / 'etc/php-fpm.conf').is_file() and
                  (p / 'bin/fpmctl').is_file())


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def php_values(version, keys):
    # Only requested INI names, never phpinfo/environment/session/config contents.
    script = '$out=[];$saved=[];foreach(array_merge([php_ini_loaded_file()],array_filter(array_map("trim",explode(",",php_ini_scanned_files())))) as $file){$v=parse_ini_file($file,false,INI_SCANNER_RAW);if(is_array($v))$saved=array_merge($saved,$v);}foreach(' + json.dumps(keys) + ' as $k){$out[$k]=in_array($k,["max_execution_time","max_input_time"])?($saved[$k]??null):get_cfg_var($k);}echo json_encode($out);'
    rc, out = command([str(APPS/version/'bin/php'), '-c', str(APPS/version/'etc/php.ini'), '-r', script])
    if rc:
        raise ValueError('PHP configuration query failed: ' + version)
    return json.loads(out)


def drift(profile, versions):
    sections = profile['configuration']['sections']
    expected_ini = sections['phpIni']['settings']
    expected_fpm = sections['phpFpm']['settings']
    native = read_native_json()
    audit = module('resman_config_audit', P(__file__).parent.parent/'core/configuration-audit.py')
    rows = []
    for version in versions:
        expectation = sections['phpIni'].get('byVersion', {}).get(version, expected_ini)
        expectation = {key:(value.replace('{version}', version) if isinstance(value,str) else value) for key,value in expectation.items()}
        actual = php_values(version, list(expectation))
        for key, value in expectation.items():
            a, b = audit.normalized(value), audit.normalized(actual.get(key))
            if key == 'realpath_cache_size':
                a, b = audit.size(value), audit.size(actual.get(key))
            if isinstance(value, bool) and b == '':
                b = 0
            rows.append(dict(version=version, section='phpIni', key=key, expected=value,
                             actual=actual.get(key), match=a == b))
        for key, value in expected_fpm.items():
            field = key.replace('pm_', 'pm.', 1) if key.startswith('pm_') else key
            actual_value = native.get(version, {}).get(field)
            rows.append(dict(version=version, section='phpFpm', key=field, expected=value,
                             actual=actual_value, match=audit.normalized(value) == audit.normalized(actual_value)))
    return rows


def safe_ini_read(path):
    # Resolve every directory using descriptor-relative no-follow opens.
    fd = os.open('/', os.O_RDONLY | os.O_DIRECTORY)
    try:
        for part in path.parts[1:-1]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd); fd = child
        leaf = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
        with os.fdopen(leaf) as stream:
            info = os.fstat(stream.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_size > 65536:
                raise ValueError('Unsafe INI input')
            return stream.read(65537)
    finally:
        os.close(fd)


def document_roots():
    return sorted(P('/home').glob('*/public_html'))


def exceptions(keys):
    """Bounded breadth-first audit, inspecting every root INI before nested content."""
    result, errors, files, visited = [], [], 0, 0
    deadline = time.monotonic() + 8
    roots = document_roots()
    pending = collections.deque()
    reason = None
    def inspect(folder):
        nonlocal files, reason
        path = folder/'.user.ini'
        try:
            if not path.exists() and not path.is_symlink(): return
            text = safe_ini_read(path); files += 1
            for line in text.splitlines():
                match = re.match(r'^\s*([a-zA-Z_][\w.]*)\s*=\s*(.*?)\s*$', line)
                if match and match[1] in keys:
                    result.append({'path':str(path),'key':match[1],'value':match[2][:128]})
                    if len(result) >= MAX_EXCEPTIONS:
                        reason = 'Row limit reached'; return
        except (OSError, UnicodeError, ValueError): errors.append(str(path))
    # Account fairness: a large first site cannot hide another account's root override.
    for root in roots:
        if root.is_symlink(): errors.append(str(root)); continue
        inspect(root); pending.append((root, True))
        if reason or time.monotonic() > deadline:
            reason = reason or 'Time limit reached'; break
    while pending and not reason:
        folder, inspected = pending.popleft()
        if not inspected: inspect(folder)
        if reason: break
        try:
            with os.scandir(folder) as entries:
                for item in entries:
                    visited += 1
                    if visited > MAX_SCAN_FILES or time.monotonic() > deadline:
                        reason = 'Entry limit reached' if visited > MAX_SCAN_FILES else 'Time limit reached'; break
                    if item.is_dir(follow_symlinks=False): pending.append((P(item.path), False))
        except OSError: errors.append(str(folder))
    return {'rows':result,'filesRead':files,'entriesVisited':visited,'rootsFound':len(roots),
            'completeWithinScope': not reason and not errors,'boundedStopReason':reason,
            'unreadable':errors[:20],
            'scope':'/home/*/public_html roots first, then nested directories breadth-first; no symlink traversal; bounded scan. Alternate domain roots, .htaccess, FPM per-pool and application ini_set require separate verification.'}


def lifecycle_status():
    pending = read_json(STATE/'lifecycle-pending.json')
    histories = sorted(STATE.glob('lifecycle-*.json'), key=lambda p: p.stat().st_mtime, reverse=True)
    rows = []
    for path in histories[:20]:
        if path.name == 'lifecycle-pending.json':
            continue
        d = read_json(path, {})
        rows.append({k: d.get(k) for k in ('version', 'operation', 'status', 'startedAt', 'finishedAt', 'restoredAt')})
    return {'pending': {k: pending.get(k) for k in ('version', 'operation', 'status', 'startedAt')} if pending else None,
            'history': rows, 'guidance': 'Recovery restores the recorded pre-operation state. Conflicting staging files or missing installation paths require SSH review; do not delete the journal.'}


def diagnostics():
    # Expanding systemd unit globs can scan the entire journal before applying -n.
    # Bound the shared tail first, then allowlist capacity records below.
    unavailable = ''
    try:
        rc, text = command(['journalctl', '--since=-1h', '--no-pager', '-o', 'cat', '-n', str(MAX_JOURNAL_ROWS)])
        if rc: unavailable = 'Journal command failed; capacity event coverage is unavailable.'
    except (subprocess.TimeoutExpired, OSError):
        rc, text = 1, ''
        unavailable = 'Journal read timed out or was unavailable; capacity event coverage is unavailable.'
    counts, buckets, recent = collections.Counter(), {}, []
    for line in text.splitlines():
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if d.get('event') not in ('php_proxy', 'php_admission'):
            continue
        reason = d.get('reason')
        if reason not in ('queue_deadline', 'queue_full', 'backend_unavailable', 'request_deadline', 'relay_io_error',
                          'host_reserve', 'shared_php_budget', 'account_memory', 'active_pool_limit', 'account_limits'):
            continue
        counts[reason] += 1
        at = d.get('at')
        if isinstance(at, (int, float)):
            minute = int(at)//60*60
            buckets.setdefault(str(minute), collections.Counter())[reason] += 1
        recent.append({k: d[k] for k in ('at', 'unit', 'reason', 'availableMiB', 'reservedMiB', 'accountAvailableMiB') if k in d})
    return {'available': rc == 0, 'windowSeconds': 3600, 'maxJournalRows': MAX_JOURNAL_ROWS,
            'counts': dict(counts), 'minuteBuckets': buckets, 'recent': recent[-30:],
            'error': unavailable,
            'scope': (unavailable+' ' if unavailable else '')+'Bounded last-'+str(MAX_JOURNAL_ROWS)+' all-service journal sample within one hour. Admission attempts and proxy failures are separate events, not unique failed visitors. Empty counts do not prove no overload; unrelated traffic, journal retention/rate limiting and unavailable reads can omit events.'}


def fpm_preflight(version, has_pools):
    config = APPS/version/'etc/php-fpm.conf'
    args = [str(APPS/version/'sbin/php-fpm'), '-t', '-c', str(APPS/version/'etc/php.ini')]
    if has_pools:
        return command(args+['-y',str(config)])[0] == 0
    # FPM rejects a legitimate unused version solely because it has no pools.
    # Syntax-check a private temporary copy with one validation-only pool; no service is started.
    nobody = pwd.getpwnam('nobody')
    group = grp.getgrgid(nobody.pw_gid).gr_name
    with tempfile.NamedTemporaryFile(mode='w', prefix='fpm-preflight-', suffix='.conf', dir=STORE) as temp:
        temp.write(config.read_text()+'\n[resman-syntax-only]\nuser = nobody\ngroup = '+group+'\nlisten = '+str(STORE/'syntax-only.sock')+'\npm = ondemand\npm.max_children = 1\n')
        temp.flush()
        return command(args+['-y',temp.name])[0] == 0


def binary_signature(version):
    return hashlib.sha256(json.dumps([(rel,(APPS/version/rel).stat().st_size,(APPS/version/rel).stat().st_mtime_ns) for rel in ('bin/php','sbin/php-fpm')]).encode()).hexdigest()


def fingerprint(version):
    # Hash vendor configuration + binary metadata. No customer content or secrets exported.
    p = APPS/version
    items = []
    for rel in ('bin/php', 'sbin/php-fpm', 'bin/fpmctl', 'etc/php-fpm.conf', 'etc/php.ini'):
        path = p/rel
        s = path.stat()
        items.append((rel, s.st_size, s.st_mtime_ns))
    return hashlib.sha256(json.dumps(items).encode()).hexdigest()


def reconcile(automatic=True):
    STORE.mkdir(parents=True, mode=0o700, exist_ok=True)
    with open(STORE/'operation.lock', 'a') as stream:
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return {'success': False, 'error': 'Governance operation already running'}
        prior = read_json(STORE/'snapshot.json', {})
        profile = read_json(PROFILE)
        if profile:
            profile = module('resman_config_audit', P(__file__).parent.parent/'core/configuration-audit.py').normalize_profile(profile)
        versions, managed = installed(), registry()
        retired = read_json(STORE/'retired.json', {})
        # An explicit retirement must survive background scans until re-enabled.
        changed_retired = {v:d for v,d in retired.items() if v in versions}
        if changed_retired != retired:
            retired = changed_retired; write_json(STORE/'retired.json', retired)
        report = {'schemaVersion': 1, 'at': int(time.time()), 'success': True,
                  'installed': versions, 'managed': managed, 'automation': automatic,
                  'profileAvailable': bool(profile), 'versions': {}, 'errors': [],
                  'readiness': {'certified': False, 'scope': 'Configured-value and runtime lifecycle monitoring; not workload capacity or complete deployment certification.'}}
        try:
            rows = drift(profile, versions) if profile else []
        except Exception as error:
            rows = []; report['errors'].append(str(error))
        comparison = prior.get('configurationComparison')
        if not comparison or time.time()-comparison.get('at',0) >= SCAN_SECONDS*5:
            try:
                comparison = module('resman_config_audit', P(__file__).parent.parent/'core/configuration-audit.py').audit(PROFILE) if profile else None
            except Exception:
                comparison = {'at': int(time.time()), 'error': 'Full configuration comparison unavailable; check profile and services.'}
        report['configurationComparison'] = comparison
        report['configurationRows'] = rows
        report['drift'] = [r for r in rows if not r['match']]
        runtime = module('resman_governance_runtime', P(CONTROL))
        pending = lifecycle_status()
        report['lifecycle'] = pending
        for version in sorted(set(versions+managed)):
            entry = {'action': 'none', 'state': 'review', 'installed': version in versions, 'managed': version in managed}
            report['versions'][version] = entry
            if version not in versions:
                entry.update(state='blocked', reason='Managed installation missing. Restore installation files for recovery or retire before vendor uninstall. No blind registry deletion.')
                continue
            fp = fingerprint(version); entry['fingerprint'] = fp
            if version in retired:
                entry.update(state='retired', reason='Intentionally retired. Safe to uninstall after moving sites; use Enable Runtime to register again.')
                continue
            previous = prior.get('versions', {}).get(version, {})
            entry['attempts'] = previous.get('attempts', 0) if previous.get('fingerprint') == fp else 0
            entry['lastAttempt'] = previous.get('lastAttempt', 0) if previous.get('fingerprint') == fp else 0
            stable = previous.get('fingerprint') == fp and report['at']-prior.get('at', report['at']) >= SCAN_SECONDS
            entry['stable'] = stable
            entry['binarySignature'] = binary_signature(version)
            binary_changed = previous.get('pendingBinaryChange',False) or (previous.get('binarySignature') is not None and previous['binarySignature'] != entry['binarySignature'])
            entry['pendingBinaryChange'] = binary_changed
            mismatches = [r for r in report['drift'] if r['version'] == version]
            try:
                parsed_pools = runtime.parse_pools((APPS/version/'etc/php-fpm.conf').read_text(), version, False)
                launcher_ok = (APPS/version/'bin/fpmctl').read_text() == runtime.wrapper(version)
                _, mgr = command(['systemctl', 'is-active', 'wpiso-manager-'+version+'.service'])
                _, health = command(['systemctl', 'is-active', 'wpiso-health-'+version+'.service'])
                _, native_bridge = command(['systemctl', 'is-active', 'php-fpm'+version[3:]+'.service'])
                entry.update(coordinator=mgr, healthMaster=health, nativeBridge=native_bridge, launcherMatches=launcher_ok)
                needs = binary_changed or version not in managed or not launcher_ok or mgr != 'active' or health != 'active' or native_bridge != 'active'
                if pending['pending']:
                    entry.update(state='blocked', reason='Pending lifecycle recovery requires review.')
                elif not profile or report['errors'] or mismatches:
                    entry.update(state='blocked', reason='Reviewed global settings missing, unreadable or different. Apply generator values globally for this PHP version; no per-user tuning is created.')
                elif needs and (not automatic or not stable):
                    entry.update(state='waiting', reason='Waiting for a stable installation across two scans or administrator reconciliation.')
                elif needs and (entry['attempts'] >= 3 or time.time()-entry['lastAttempt'] < SCAN_SECONDS*5):
                    entry.update(state='blocked', reason='Automatic retry cooldown/limit reached. Review failure and use Reconcile after resolving it.')
                elif needs:
                    if not fpm_preflight(version, bool(parsed_pools)): raise RuntimeError('Native FPM syntax preflight failed; installation left unchanged.')
                    entry['attempts'] += 1; entry['lastAttempt'] = int(time.time())
                    rc, _ = command(['python3', CONTROL, 'onboard', version], timeout=180)
                    entry['action'] = 'onboard_or_repair'
                    # Do not publish raw subprocess output (could include pool credentials).
                    if rc:
                        raise RuntimeError('Transactional onboarding failed; review lifecycle recovery and server journal.')
                    _, mgr = command(['systemctl', 'is-active', 'wpiso-manager-'+version+'.service'])
                    _, health = command(['systemctl', 'is-active', 'wpiso-health-'+version+'.service'])
                    _, native_bridge = command(['systemctl', 'is-active', 'php-fpm'+version[3:]+'.service'])
                    if version not in registry() or (APPS/version/'bin/fpmctl').read_text() != runtime.wrapper(version) or mgr != 'active' or health != 'active' or native_bridge != 'active':
                        raise RuntimeError('Post-operation service verification failed')
                    entry.update(state='healthy', pendingBinaryChange=False, managed=True, coordinator=mgr, healthMaster=health, nativeBridge=native_bridge,
                                 fingerprint=fingerprint(version), launcherMatches=True, reason='Transactional onboarding/repair and service checks passed.')
                else:
                    entry.update(state='healthy', reason='Global settings, launcher and services match.')
            except Exception as error:
                entry.update(state='blocked', reason=str(error))
        report['managed'] = registry()
        report['lifecycle'] = lifecycle_status()
        report['inheritance'] = exceptions(set(profile['configuration']['sections']['phpIni']['settings'])) if profile else {'rows': [], 'completeWithinScope': False, 'scope': 'No reviewed profile available.'}
        report['diagnostics'] = diagnostics()
        report['success'] = not report['errors'] and bool(comparison) and not comparison.get('error') and not comparison.get('mismatches') and all(e['state'] in ('healthy','retired') for e in report['versions'].values()) and bool(versions)
        write_json(STORE/'snapshot.json', report)
        return report


def snapshot():
    job = read_json(STORE/'job.json') or read_json(STORE/'background-scan.json')
    if job and job.get('state') == 'running' and job.get('agentPid') != os.getpid():
        job = dict(job, state='interrupted', error='Agent restarted during operation. Inspect evidence and pending recovery before retrying.')
    value = read_json(STORE/'snapshot.json')
    return {'success': True, 'snapshot': value, 'stale': not value or time.time()-value['at'] > SCAN_SECONDS*3,
            'job': job}


def full_export():
    result = snapshot()
    result['exportedAt'] = int(time.time())
    audit = module('resman_config_audit', P(__file__).parent.parent/'core/configuration-audit.py')
    try:
        result['configurationComparison'] = audit.audit(PROFILE)
    except Exception:
        result['configurationComparison'] = {'error': 'Full comparison unavailable. Check reviewed profile and service access.'}
    result['success'] = True
    result['scope'] = 'Administrator diagnostic export. Includes account paths, configured values and evidence limitations; excludes credentials, journal text, lifecycle file snapshots and application content.'
    return result
