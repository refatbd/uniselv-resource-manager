# Exact source changes — 1.1.24

Already-applied release source changes relative to 1.1.23; not extra post-install paste steps. Prefer the reviewed complete package.

- Back up existing files and ownership/restoration manifests together.
- Use UTF-8/LF. Replace existing files; do not append duplicate imports, functions or directives. New files start at their first line and end at their final line.
- Install through the reviewed privileged deployment workflow. Restore root ownership and installer execution modes.
- Run Python/PHP/JavaScript syntax, regression, service/API/HTTP and ZIP closure checks. Configuration values and full workload/lifecycle readiness remain distinct.

## uniselv-resman/agent/agent_daemon.py

Installed paths: /usr/local/webuzo/plugins/uniselv-resman/agent/agent_daemon.py; ALSO /usr/local/uniselv-resman/agent/agent_daemon.py

Replace the full file; never append duplicate functions/directives. New files run from first through final line.

### Block 1 — insert

Existing anchor AFTER which:
```text
            time.sleep(max(3, min(60, interval)))

```

Existing anchor BEFORE which:
```text
    def run_ipc_server(self):
        """UNIX domain socket server loop with strict permissions and peer credentials."""
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
    def governance_loop(self):
        while self.running:
            try:
                if not self.handler.maintenance_mode:
                    self.handler.governance_tick()
            except Exception as error:
                print('[Runtime Governance Error] ' + str(error), file=sys.stderr)
            for _ in range(60):
                if not self.running: return
                time.sleep(1)

```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
            time.sleep(max(3, min(60, interval)))

    def governance_loop(self):
        while self.running:
            try:
                if not self.handler.maintenance_mode:
                    self.handler.governance_tick()
            except Exception as error:
                print('[Runtime Governance Error] ' + str(error), file=sys.stderr)
            for _ in range(60):
                if not self.running: return
                time.sleep(1)

    def run_ipc_server(self):
        """UNIX domain socket server loop with strict permissions and peer credentials."""
```

### Block 2 — insert

Existing anchor AFTER which:
```text
        collector_thread.start()

```

Existing anchor BEFORE which:
```text
        self.run_ipc_server()

```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
        threading.Thread(target=self.governance_loop, daemon=True).start()
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
        collector_thread.start()

        threading.Thread(target=self.governance_loop, daemon=True).start()
        self.run_ipc_server()

```

## uniselv-resman/agent/ipc_server.py

Installed paths: /usr/local/webuzo/plugins/uniselv-resman/agent/ipc_server.py; ALSO /usr/local/uniselv-resman/agent/ipc_server.py

Replace the full file; never append duplicate functions/directives. New files run from first through final line.

### Block 1 — insert

Existing anchor AFTER which:
```text
import uuid
import stat
```

Existing anchor BEFORE which:
```text
try:
    import fcntl
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
import threading
import runtime_governance as governance
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
import uuid
import stat
import threading
import runtime_governance as governance
try:
    import fcntl
```

### Block 2 — insert

Existing anchor AFTER which:
```text
            elif action == 'run_adapter_sync':
                return self.action_run_adapter_sync(user, params)
```

Existing anchor BEFORE which:
```text
            elif action == 'get_php_lifecycle':
                return self.action_get_php_lifecycle()
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
            elif action == 'get_runtime_governance':
                return governance.snapshot()
            elif action == 'run_runtime_governance':
                return self.action_runtime_governance(user, params)
            elif action == 'export_runtime_governance':
                return {'success': True, 'export': governance.read_json(governance.STORE/'export.json')}
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
            elif action == 'run_adapter_sync':
                return self.action_run_adapter_sync(user, params)
            elif action == 'get_runtime_governance':
                return governance.snapshot()
            elif action == 'run_runtime_governance':
                return self.action_runtime_governance(user, params)
            elif action == 'export_runtime_governance':
                return {'success': True, 'export': governance.read_json(governance.STORE/'export.json')}
            elif action == 'get_php_lifecycle':
                return self.action_get_php_lifecycle()
```

### Block 3 — insert

Existing anchor AFTER which:
```text
        }

```

Existing anchor BEFORE which:
```text
    def action_get_php_lifecycle(self) -> Dict[str, Any]:
        installed = self.get_installed_phps()
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
    _governance_mutex = threading.Lock()

    def action_runtime_governance(self, actor, params):
        operation = str(params.get('operation', 'scan'))
        background = actor == 'system' and params.get('_background') is True
        version = str(params.get('version', ''))
        if operation not in ('scan', 'export', 'recover', 'retire', 'activate'):
            return {'success': False, 'error': 'Unknown governance operation'}
        if operation in ('retire', 'activate') and not governance.VERSION.fullmatch(version):
            return {'success': False, 'error': 'Choose a valid registered PHP version'}
        if not self._governance_mutex.acquire(blocking=False):
            return {'success': False, 'error': 'A governance operation is already running'}
        job = {'id': uuid.uuid4().hex, 'operation': operation, 'actor': actor, 'version': version,
               'startedAt': int(time.time()), 'state': 'running', 'agentPid': os.getpid()}
        job_path = governance.STORE/('background-scan.json' if background else 'job.json')
        try: governance.write_json(job_path, job)
        except Exception:
            self._governance_mutex.release()
            raise
        def work():
            try:
                governance.write_json(job_path, job)
                if operation in ('recover', 'retire'):
                    args = ['python3', governance.CONTROL, 'recover-lifecycle' if operation == 'recover' else 'retire']
                    if operation == 'retire': args.append(version)
                    rc, _ = governance.command(args, timeout=240)
                    if rc: raise RuntimeError('Lifecycle operation failed; review the retained recovery journal and server logs.')
                if operation in ('retire', 'activate'):
                    retired = governance.read_json(governance.STORE/'retired.json', {})
                    if operation == 'retire': retired[version] = {'at': int(time.time()), 'actor': actor}
                    else: retired.pop(version, None)
                    governance.write_json(governance.STORE/'retired.json', retired)
                if operation == 'scan' and not background:
                    old = governance.read_json(governance.STORE/'snapshot.json', {})
                    for entry in old.get('versions', {}).values(): entry.update(attempts=0, lastAttempt=0)
                    old.pop('configurationComparison', None)
                    if old: governance.write_json(governance.STORE/'snapshot.json', old)
                if operation == 'export':
                    governance.write_json(governance.STORE/'export.json', governance.full_export())
                else:
                    result = governance.reconcile(automatic=True)
                    if result.get('error'): raise RuntimeError(result['error'])
                job['state'] = 'completed'
            except Exception as error:
                job.update(state='failed', error=str(error))
            finally:
                try:
                    job['finishedAt'] = int(time.time())
                    governance.write_json(job_path, job)
                    record = not background or job['state']=='failed' or any(e.get('action')!='none' for e in locals().get('result',{}).get('versions',{}).values())
                    if record:
                        conn = self.get_db()
                        try:
                            conn.execute("INSERT INTO audit_log (timestamp, actor, action, target_account, details_json) VALUES (?, ?, 'runtime_governance', 'system', ?)",
                                         (job['finishedAt'], actor, json.dumps(job)))
                            conn.commit()
                        finally: conn.close()
                finally: self._governance_mutex.release()
        threading.Thread(target=work, daemon=True).start()
        return {'success': True, 'queued': True, 'operation': operation, 'jobId': job['id']}

    def governance_tick(self):
        # Background automation uses the same serialized worker, independent of telemetry sampling.
        if not self._governance_mutex.acquire(blocking=False): return
        self._governance_mutex.release()
        # Internal background value is not accepted from untrusted API parameters.
        self.action_runtime_governance('system', {'operation': 'scan', '_background': True})

```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
        }

    _governance_mutex = threading.Lock()

    def action_runtime_governance(self, actor, params):
        operation = str(params.get('operation', 'scan'))
        background = actor == 'system' and params.get('_background') is True
        version = str(params.get('version', ''))
        if operation not in ('scan', 'export', 'recover', 'retire', 'activate'):
            return {'success': False, 'error': 'Unknown governance operation'}
        if operation in ('retire', 'activate') and not governance.VERSION.fullmatch(version):
            return {'success': False, 'error': 'Choose a valid registered PHP version'}
        if not self._governance_mutex.acquire(blocking=False):
            return {'success': False, 'error': 'A governance operation is already running'}
        job = {'id': uuid.uuid4().hex, 'operation': operation, 'actor': actor, 'version': version,
               'startedAt': int(time.time()), 'state': 'running', 'agentPid': os.getpid()}
        job_path = governance.STORE/('background-scan.json' if background else 'job.json')
        try: governance.write_json(job_path, job)
        except Exception:
            self._governance_mutex.release()
            raise
        def work():
            try:
                governance.write_json(job_path, job)
                if operation in ('recover', 'retire'):
                    args = ['python3', governance.CONTROL, 'recover-lifecycle' if operation == 'recover' else 'retire']
                    if operation == 'retire': args.append(version)
                    rc, _ = governance.command(args, timeout=240)
                    if rc: raise RuntimeError('Lifecycle operation failed; review the retained recovery journal and server logs.')
                if operation in ('retire', 'activate'):
                    retired = governance.read_json(governance.STORE/'retired.json', {})
                    if operation == 'retire': retired[version] = {'at': int(time.time()), 'actor': actor}
                    else: retired.pop(version, None)
                    governance.write_json(governance.STORE/'retired.json', retired)
                if operation == 'scan' and not background:
                    old = governance.read_json(governance.STORE/'snapshot.json', {})
                    for entry in old.get('versions', {}).values(): entry.update(attempts=0, lastAttempt=0)
                    old.pop('configurationComparison', None)
                    if old: governance.write_json(governance.STORE/'snapshot.json', old)
                if operation == 'export':
                    governance.write_json(governance.STORE/'export.json', governance.full_export())
                else:
                    result = governance.reconcile(automatic=True)
                    if result.get('error'): raise RuntimeError(result['error'])
                job['state'] = 'completed'
            except Exception as error:
                job.update(state='failed', error=str(error))
            finally:
                try:
                    job['finishedAt'] = int(time.time())
                    governance.write_json(job_path, job)
                    record = not background or job['state']=='failed' or any(e.get('action')!='none' for e in locals().get('result',{}).get('versions',{}).values())
                    if record:
                        conn = self.get_db()
                        try:
                            conn.execute("INSERT INTO audit_log (timestamp, actor, action, target_account, details_json) VALUES (?, ?, 'runtime_governance', 'system', ?)",
                                         (job['finishedAt'], actor, json.dumps(job)))
                            conn.commit()
                        finally: conn.close()
                finally: self._governance_mutex.release()
        threading.Thread(target=work, daemon=True).start()
        return {'success': True, 'queued': True, 'operation': operation, 'jobId': job['id']}

    def governance_tick(self):
        # Background automation uses the same serialized worker, independent of telemetry sampling.
        if not self._governance_mutex.acquire(blocking=False): return
        self._governance_mutex.release()
        # Internal background value is not accepted from untrusted API parameters.
        self.action_runtime_governance('system', {'operation': 'scan', '_background': True})

    def action_get_php_lifecycle(self) -> Dict[str, Any]:
        installed = self.get_installed_phps()
```

## uniselv-resman/agent/runtime_governance.py

Installed paths: /usr/local/webuzo/plugins/uniselv-resman/agent/runtime_governance.py; ALSO /usr/local/uniselv-resman/agent/runtime_governance.py

Replace the full file; never append duplicate functions/directives. New files run from first through final line.

### Block 1 — new-file

Existing anchor AFTER which:
```text
<START OF FILE>
```

Existing anchor BEFORE which:
```text
<END OF FILE>
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
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
    rc, text = command(['journalctl', '--since=-1h', '--no-pager', '-o', 'cat', '-n', str(MAX_JOURNAL_ROWS),
                        '-u', 'wpiso-proxy-*.service', '-u', 'wpiso-fpm-*.service'])
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
            'scope': 'Bounded journal sample. Admission attempts and proxy failures are separate events, not unique failed visitors. No events does not prove no overload; journal retention/rate limiting applies.'}


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
                entry.update(coordinator=mgr, healthMaster=health, launcherMatches=launcher_ok)
                needs = binary_changed or version not in managed or not launcher_ok or mgr != 'active' or health != 'active'
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
                    if version not in registry() or (APPS/version/'bin/fpmctl').read_text() != runtime.wrapper(version) or mgr != 'active' or health != 'active':
                        raise RuntimeError('Post-operation service verification failed')
                    entry.update(state='healthy', pendingBinaryChange=False, managed=True, coordinator=mgr, healthMaster=health,
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
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
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
    rc, text = command(['journalctl', '--since=-1h', '--no-pager', '-o', 'cat', '-n', str(MAX_JOURNAL_ROWS),
                        '-u', 'wpiso-proxy-*.service', '-u', 'wpiso-fpm-*.service'])
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
            'scope': 'Bounded journal sample. Admission attempts and proxy failures are separate events, not unique failed visitors. No events does not prove no overload; journal retention/rate limiting applies.'}


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
                entry.update(coordinator=mgr, healthMaster=health, launcherMatches=launcher_ok)
                needs = binary_changed or version not in managed or not launcher_ok or mgr != 'active' or health != 'active'
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
                    if version not in registry() or (APPS/version/'bin/fpmctl').read_text() != runtime.wrapper(version) or mgr != 'active' or health != 'active':
                        raise RuntimeError('Post-operation service verification failed')
                    entry.update(state='healthy', pendingBinaryChange=False, managed=True, coordinator=mgr, healthMaster=health,
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
```

## uniselv-resman/assets/app.js

Installed paths: /usr/local/webuzo/plugins/uniselv-resman/assets/app.js

Replace the full file; never append duplicate functions/directives. New files run from first through final line.

### Block 1 — replace

Existing anchor AFTER which:
```text
            <div class="uniselv-toast-icon">${icons[type] || icons.info}</div>
            <div class="uniselv-toast-body">
```

Existing anchor BEFORE which:
```text
            </div>
            <button class="uniselv-toast-close" title="Dismiss">&times;</button>
```

Existing content to replace/remove (not copied):
```text
                <div class="uniselv-toast-title">${title}</div>
                <div class="uniselv-toast-msg">${message}</div>
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                <div class="uniselv-toast-title">${safe(title)}</div>
                <div class="uniselv-toast-msg">${safe(message)}</div>
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
            <div class="uniselv-toast-icon">${icons[type] || icons.info}</div>
            <div class="uniselv-toast-body">
                <div class="uniselv-toast-title">${safe(title)}</div>
                <div class="uniselv-toast-msg">${safe(message)}</div>
            </div>
            <button class="uniselv-toast-close" title="Dismiss">&times;</button>
```

### Block 2 — insert

Existing anchor AFTER which:
```text
            } else if (resolved === 'health') {
                this.loadPhpLifecycle();
```

Existing anchor BEFORE which:
```text
                this.loadFeatureSettings();
                this.loadStorageSettings();
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                this.loadRuntimeGovernance();
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
            } else if (resolved === 'health') {
                this.loadPhpLifecycle();
                this.loadRuntimeGovernance();
                this.loadFeatureSettings();
                this.loadStorageSettings();
```

### Block 3 — insert

Existing anchor AFTER which:
```text
                });
            }
```

Existing anchor BEFORE which:
```text
        });
    },
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
        });
    },

    loadRuntimeGovernance: function() {
        const host = document.getElementById('uniselv-runtime-governance');
        if (!this.isAdmin || !host) return;
        const bind = (id, fn) => {const b=document.getElementById(id);if(b)b.onclick=fn;};
        bind('governance-refresh',()=>this.loadRuntimeGovernance());
        bind('governance-scan',()=>this.runGovernance('scan'));
        bind('governance-recover',()=>this.confirmGovernance('recover'));
        bind('governance-export',()=>this.runGovernance('export'));
        this.callApi('runtime_governance',{},(err,response)=>{
            const data=response?.data || response;
            if(err || !data?.success){host.textContent='Evidence unavailable. Check agent health and retry.';return;}
            const job=document.getElementById('governance-job');
            if(job && !this.governancePolling)job.textContent=data.job ? `Last operation: ${data.job.operation} — ${data.job.state}${data.job.error ? ': '+data.job.error : ''}` : '';
            const value=data.snapshot;host.replaceChildren();
            if(!value){host.textContent='No scan has completed yet. Choose Reconcile PHP Changes.';return;}
            const note=(text)=>{const p=document.createElement('p');p.textContent=text;host.append(p);};
            note(`Observed: ${new Date(value.at*1000).toLocaleString()}${data.stale ? ' — STALE' : ''}. Global setting differences: ${(value.drift || []).length}. ${value.readiness?.scope || ''}`);
            const table=(title,labels,rows)=>{
                const details=document.createElement('details');details.className='uniselv-governance-detail';
                const summary=document.createElement('summary');summary.textContent=title;details.append(summary);
                const wrap=document.createElement('div');wrap.className='uniselv-table-wrap';
                const element=document.createElement('table');element.className='uniselv-table';
                const head=element.createTHead().insertRow();labels.forEach(label=>{const th=document.createElement('th');th.scope='col';th.textContent=label;head.append(th);});
                const body=element.createTBody();rows.forEach(cells=>{const row=body.insertRow();cells.forEach(value=>{const cell=row.insertCell();if(value instanceof Node)cell.append(value);else cell.textContent=String(value ?? 'Unavailable');});});
                if(!rows.length){const cell=body.insertRow().insertCell();cell.colSpan=labels.length;cell.textContent='No entries in this observation.';}
                wrap.append(element);details.append(wrap);host.append(details);return details;
            };
            table('PHP Lifecycle Automation',['Version','State','Last action','Explanation','Maintenance'],Object.entries(value.versions || {}).map(([version,state])=>{
                const b=document.createElement('button');b.className='uniselv-btn btn-outline';b.textContent=state.state==='retired'?'Enable Runtime':'Retire Runtime';b.disabled=!state.managed && state.state!=='retired';b.onclick=()=>state.state==='retired'?this.runGovernance('activate',version):this.confirmGovernance('retire',version);
                return [version,state.state,state.action,state.reason,b];
            })).open=true;
            table('Global Settings Drift — Expected vs Actual',['PHP','Section','Directive','Expected','Actual'],(value.drift || []).map(r=>[r.version,r.section,r.key,r.expected,r.actual]));
            table('Server Configuration Drift — All Reviewed Sections',['Section','Directive','Expected','Actual'],(value.configurationComparison?.mismatches || []).map(r=>[r.section,r.key,r.expected,r.actual]));
            note(value.configurationComparison?.error || `Server comparison: ${value.configurationComparison?.checks ?? 0} configured-value checks; observed ${value.configurationComparison?.at ? new Date(value.configurationComparison.at*1000).toLocaleString() : 'unavailable'}. Workload tests are separate.`);
            table('Configuration Audit Coverage — All Generator Sections',['Section','Checks','Evidence'],(value.configurationComparison?.sectionCoverage || []).map(r=>[r.section,r.checks,r.status]));
            table('Account Inheritance Exceptions',['File','Directive','Override'],(value.inheritance?.rows || []).map(r=>[r.path,r.key,r.value]));
            note(`Override coverage: ${value.inheritance?.scope || 'Unavailable'} Complete within scope: ${value.inheritance?.completeWithinScope ? 'Yes':'No'}. ${value.inheritance?.boundedStopReason || ''}`);
            table('Capacity Events — Last Hour, Bounded Journal Sample',['Reason','Observed events'],Object.entries(value.diagnostics?.counts || {}));
            note(value.diagnostics?.scope || 'Journal diagnostics unavailable.');
            table('Recent Capacity Event Timeline',['Time','Unit','Reason'],(value.diagnostics?.recent || []).map(r=>[r.at ? new Date(r.at*1000).toLocaleString():'Before timestamp instrumentation',r.unit,r.reason]));
            table('Lifecycle Recovery History',['PHP','Operation','Status','Started'],(value.lifecycle?.history || []).map(r=>[r.version,r.operation,r.status,r.startedAt ? new Date(r.startedAt*1000).toLocaleString():'Unavailable']));
            note(value.lifecycle?.pending ? `PENDING: ${value.lifecycle.pending.operation} ${value.lifecycle.pending.version}. ${value.lifecycle.guidance}` : 'No pending lifecycle journal.');
            (value.errors || []).forEach(note);
        },{timeoutMs:15000});
    },

    confirmGovernance: function(operation,version='') {
        UniselvModal.confirm({title:operation==='retire'?'Retire PHP Runtime':'Recover Pending Operation',
            message:operation==='retire'?`Retire ${version} before vendor uninstall. Move all sites first. Native launcher restoration requires valid installation files.`:'Restore the recorded pre-operation state. Conflicting files stop recovery for administrator review.',
            onConfirm:()=>this.runGovernance(operation,version)});
    },

    runGovernance: function(operation,version='') {
        if(this.governancePolling){UniselvNotify.error('Wait for the current operation to finish.');return;}
        this.callApi('run_governance',{operation,version},(err,response)=>{
            const result=response?.data || response;
            if(err || !result?.success || !result.jobId){UniselvNotify.error(result?.error || 'Could not queue operation.');return;}
            this.governancePolling=true;let remaining=100;
            const poll=()=>this.callApi('runtime_governance',{},(error,reply)=>{
                const data=reply?.data || reply;const job=data?.job;const status=document.getElementById('governance-job');
                if(status)status.textContent=`${operation}: ${job?.id===result.jobId ? job.state:'waiting for status'}...`;
                if(!error && job?.id===result.jobId && job.state!=='running'){
                    this.governancePolling=false;
                    if(job.state!=='completed')UniselvNotify.error(job.error || 'Operation failed.');
                    else if(operation==='export')this.downloadGovernanceExport();
                    this.loadRuntimeGovernance();this.loadPhpLifecycle();return;
                }
                if(--remaining>0){setTimeout(poll,3000);return;}
                this.governancePolling=false;if(status)status.textContent='Still running or unavailable. Refresh Evidence later; the server operation continues.';
            },{timeoutMs:10000});poll();
        });
    },

    downloadGovernanceExport: function() {
        this.callApi('export_governance',{},(err,response)=>{
            const data=response?.data || response;
            if(err || !data?.export){UniselvNotify.error('Comparison export unavailable.');return;}
            const url=URL.createObjectURL(new Blob([JSON.stringify(data.export,null,2)],{type:'application/json'}));
            const link=document.createElement('a');link.href=url;link.download='runtime-configuration-comparison.json';link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                });
            }
        });
    },

    loadRuntimeGovernance: function() {
        const host = document.getElementById('uniselv-runtime-governance');
        if (!this.isAdmin || !host) return;
        const bind = (id, fn) => {const b=document.getElementById(id);if(b)b.onclick=fn;};
        bind('governance-refresh',()=>this.loadRuntimeGovernance());
        bind('governance-scan',()=>this.runGovernance('scan'));
        bind('governance-recover',()=>this.confirmGovernance('recover'));
        bind('governance-export',()=>this.runGovernance('export'));
        this.callApi('runtime_governance',{},(err,response)=>{
            const data=response?.data || response;
            if(err || !data?.success){host.textContent='Evidence unavailable. Check agent health and retry.';return;}
            const job=document.getElementById('governance-job');
            if(job && !this.governancePolling)job.textContent=data.job ? `Last operation: ${data.job.operation} — ${data.job.state}${data.job.error ? ': '+data.job.error : ''}` : '';
            const value=data.snapshot;host.replaceChildren();
            if(!value){host.textContent='No scan has completed yet. Choose Reconcile PHP Changes.';return;}
            const note=(text)=>{const p=document.createElement('p');p.textContent=text;host.append(p);};
            note(`Observed: ${new Date(value.at*1000).toLocaleString()}${data.stale ? ' — STALE' : ''}. Global setting differences: ${(value.drift || []).length}. ${value.readiness?.scope || ''}`);
            const table=(title,labels,rows)=>{
                const details=document.createElement('details');details.className='uniselv-governance-detail';
                const summary=document.createElement('summary');summary.textContent=title;details.append(summary);
                const wrap=document.createElement('div');wrap.className='uniselv-table-wrap';
                const element=document.createElement('table');element.className='uniselv-table';
                const head=element.createTHead().insertRow();labels.forEach(label=>{const th=document.createElement('th');th.scope='col';th.textContent=label;head.append(th);});
                const body=element.createTBody();rows.forEach(cells=>{const row=body.insertRow();cells.forEach(value=>{const cell=row.insertCell();if(value instanceof Node)cell.append(value);else cell.textContent=String(value ?? 'Unavailable');});});
                if(!rows.length){const cell=body.insertRow().insertCell();cell.colSpan=labels.length;cell.textContent='No entries in this observation.';}
                wrap.append(element);details.append(wrap);host.append(details);return details;
            };
            table('PHP Lifecycle Automation',['Version','State','Last action','Explanation','Maintenance'],Object.entries(value.versions || {}).map(([version,state])=>{
                const b=document.createElement('button');b.className='uniselv-btn btn-outline';b.textContent=state.state==='retired'?'Enable Runtime':'Retire Runtime';b.disabled=!state.managed && state.state!=='retired';b.onclick=()=>state.state==='retired'?this.runGovernance('activate',version):this.confirmGovernance('retire',version);
                return [version,state.state,state.action,state.reason,b];
            })).open=true;
            table('Global Settings Drift — Expected vs Actual',['PHP','Section','Directive','Expected','Actual'],(value.drift || []).map(r=>[r.version,r.section,r.key,r.expected,r.actual]));
            table('Server Configuration Drift — All Reviewed Sections',['Section','Directive','Expected','Actual'],(value.configurationComparison?.mismatches || []).map(r=>[r.section,r.key,r.expected,r.actual]));
            note(value.configurationComparison?.error || `Server comparison: ${value.configurationComparison?.checks ?? 0} configured-value checks; observed ${value.configurationComparison?.at ? new Date(value.configurationComparison.at*1000).toLocaleString() : 'unavailable'}. Workload tests are separate.`);
            table('Configuration Audit Coverage — All Generator Sections',['Section','Checks','Evidence'],(value.configurationComparison?.sectionCoverage || []).map(r=>[r.section,r.checks,r.status]));
            table('Account Inheritance Exceptions',['File','Directive','Override'],(value.inheritance?.rows || []).map(r=>[r.path,r.key,r.value]));
            note(`Override coverage: ${value.inheritance?.scope || 'Unavailable'} Complete within scope: ${value.inheritance?.completeWithinScope ? 'Yes':'No'}. ${value.inheritance?.boundedStopReason || ''}`);
            table('Capacity Events — Last Hour, Bounded Journal Sample',['Reason','Observed events'],Object.entries(value.diagnostics?.counts || {}));
            note(value.diagnostics?.scope || 'Journal diagnostics unavailable.');
            table('Recent Capacity Event Timeline',['Time','Unit','Reason'],(value.diagnostics?.recent || []).map(r=>[r.at ? new Date(r.at*1000).toLocaleString():'Before timestamp instrumentation',r.unit,r.reason]));
            table('Lifecycle Recovery History',['PHP','Operation','Status','Started'],(value.lifecycle?.history || []).map(r=>[r.version,r.operation,r.status,r.startedAt ? new Date(r.startedAt*1000).toLocaleString():'Unavailable']));
            note(value.lifecycle?.pending ? `PENDING: ${value.lifecycle.pending.operation} ${value.lifecycle.pending.version}. ${value.lifecycle.guidance}` : 'No pending lifecycle journal.');
            (value.errors || []).forEach(note);
        },{timeoutMs:15000});
    },

    confirmGovernance: function(operation,version='') {
        UniselvModal.confirm({title:operation==='retire'?'Retire PHP Runtime':'Recover Pending Operation',
            message:operation==='retire'?`Retire ${version} before vendor uninstall. Move all sites first. Native launcher restoration requires valid installation files.`:'Restore the recorded pre-operation state. Conflicting files stop recovery for administrator review.',
            onConfirm:()=>this.runGovernance(operation,version)});
    },

    runGovernance: function(operation,version='') {
        if(this.governancePolling){UniselvNotify.error('Wait for the current operation to finish.');return;}
        this.callApi('run_governance',{operation,version},(err,response)=>{
            const result=response?.data || response;
            if(err || !result?.success || !result.jobId){UniselvNotify.error(result?.error || 'Could not queue operation.');return;}
            this.governancePolling=true;let remaining=100;
            const poll=()=>this.callApi('runtime_governance',{},(error,reply)=>{
                const data=reply?.data || reply;const job=data?.job;const status=document.getElementById('governance-job');
                if(status)status.textContent=`${operation}: ${job?.id===result.jobId ? job.state:'waiting for status'}...`;
                if(!error && job?.id===result.jobId && job.state!=='running'){
                    this.governancePolling=false;
                    if(job.state!=='completed')UniselvNotify.error(job.error || 'Operation failed.');
                    else if(operation==='export')this.downloadGovernanceExport();
                    this.loadRuntimeGovernance();this.loadPhpLifecycle();return;
                }
                if(--remaining>0){setTimeout(poll,3000);return;}
                this.governancePolling=false;if(status)status.textContent='Still running or unavailable. Refresh Evidence later; the server operation continues.';
            },{timeoutMs:10000});poll();
        });
    },

    downloadGovernanceExport: function() {
        this.callApi('export_governance',{},(err,response)=>{
            const data=response?.data || response;
            if(err || !data?.export){UniselvNotify.error('Comparison export unavailable.');return;}
            const url=URL.createObjectURL(new Blob([JSON.stringify(data.export,null,2)],{type:'application/json'}));
            const link=document.createElement('a');link.href=url;link.download='runtime-configuration-comparison.json';link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
        });
    },
```

## uniselv-resman/assets/style.css

Installed paths: /usr/local/webuzo/plugins/uniselv-resman/assets/style.css

Replace the full file; never append duplicate functions/directives. New files run from first through final line.

### Block 1 — insert

Existing anchor AFTER which:
```text
    100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
}
```

Existing anchor BEFORE which:
```text
<END OF FILE>
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text

/* Governance uses keyboard-native disclosure and bounded responsive tables. */
.uniselv-governance-actions{display:flex;flex-wrap:wrap;gap:10px;margin:16px 0}
.uniselv-governance-detail{border:1px solid var(--uniselv-border);border-radius:10px;margin:12px 0;overflow:hidden}
.uniselv-governance-detail summary{padding:14px;cursor:pointer;font-weight:600;overflow-wrap:anywhere}
#uniselv-runtime-governance{min-width:0}
#uniselv-runtime-governance p,.uniselv-governance-note{overflow-wrap:anywhere;font-size:.9rem;line-height:1.6}
#uniselv-runtime-governance td{white-space:normal;overflow-wrap:anywhere;max-width:420px;min-width:100px}
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
    100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
}

/* Governance uses keyboard-native disclosure and bounded responsive tables. */
.uniselv-governance-actions{display:flex;flex-wrap:wrap;gap:10px;margin:16px 0}
.uniselv-governance-detail{border:1px solid var(--uniselv-border);border-radius:10px;margin:12px 0;overflow:hidden}
.uniselv-governance-detail summary{padding:14px;cursor:pointer;font-weight:600;overflow-wrap:anywhere}
#uniselv-runtime-governance{min-width:0}
#uniselv-runtime-governance p,.uniselv-governance-note{overflow-wrap:anywhere;font-size:.9rem;line-height:1.6}
#uniselv-runtime-governance td{white-space:normal;overflow-wrap:anywhere;max-width:420px;min-width:100px}
```

## uniselv-resman/core/configuration-audit.py

Installed paths: /usr/local/webuzo/plugins/uniselv-resman/core/configuration-audit.py; ALSO /usr/local/uniselv-resman/core/configuration-audit.py

Replace the full file; never append duplicate functions/directives. New files run from first through final line.

### Block 1 — insert

Existing anchor AFTER which:
```text
 match=re.fullmatch(r'(\d+)\s*([KMGT]?)',str(value),re.I)
 return int(match[1])*{'':1,'K':1024,'M':1024**2,'G':1024**3,'T':1024**4}[match[2].upper()] if match else value
```

Existing anchor BEFORE which:
```text
def audit(path):
 st=path.stat()
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
def normalize_profile(document):
 # Accept the native Global Inputs export as well as the historical reviewed wrapper.
 doc=json.loads(json.dumps(document));c=doc.get('configuration',doc)
 if not isinstance(c,dict) or not isinstance(c.get('sections'),dict):raise ValueError('Invalid generator configuration export')
 if c.get('validationErrors'):raise ValueError('Generator export contains validation errors')
 sections=c['sections'];combined=sections.get('golden',{})
 if isinstance(combined.get('golden'),dict):
  if not isinstance(sections.get('isolation',{}).get('policy'),dict):sections['isolation']={'policy':combined['isolation']}
  sections['golden']={'policy':combined['golden']}
 hardware=c.get('globalInputs',{}).get('hardware',{})
 if not hardware.get('phpVersions'):
  hardware['phpVersions']=c.get('globalInputs',{}).get('workload',{}).get('versions',list(sections.get('phpIni',{}).get('byVersion',{})))
 return {'configuration':c}

def section_coverage(sections, rows):
 result=[]
 for section in sections:
  checks=[r for r in rows if r['section']==section]
  result.append({'section':section,'checks':len(checks),'status':('Mismatch' if any(not r['match'] for r in checks) else 'Configured values matched') if checks else 'Not checked by this audit','scope':'Configured-value sample only; lifecycle, application and full deployment evidence are separate.'})
 return result

```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
 match=re.fullmatch(r'(\d+)\s*([KMGT]?)',str(value),re.I)
 return int(match[1])*{'':1,'K':1024,'M':1024**2,'G':1024**3,'T':1024**4}[match[2].upper()] if match else value
def normalize_profile(document):
 # Accept the native Global Inputs export as well as the historical reviewed wrapper.
 doc=json.loads(json.dumps(document));c=doc.get('configuration',doc)
 if not isinstance(c,dict) or not isinstance(c.get('sections'),dict):raise ValueError('Invalid generator configuration export')
 if c.get('validationErrors'):raise ValueError('Generator export contains validation errors')
 sections=c['sections'];combined=sections.get('golden',{})
 if isinstance(combined.get('golden'),dict):
  if not isinstance(sections.get('isolation',{}).get('policy'),dict):sections['isolation']={'policy':combined['isolation']}
  sections['golden']={'policy':combined['golden']}
 hardware=c.get('globalInputs',{}).get('hardware',{})
 if not hardware.get('phpVersions'):
  hardware['phpVersions']=c.get('globalInputs',{}).get('workload',{}).get('versions',list(sections.get('phpIni',{}).get('byVersion',{})))
 return {'configuration':c}

def section_coverage(sections, rows):
 result=[]
 for section in sections:
  checks=[r for r in rows if r['section']==section]
  result.append({'section':section,'checks':len(checks),'status':('Mismatch' if any(not r['match'] for r in checks) else 'Configured values matched') if checks else 'Not checked by this audit','scope':'Configured-value sample only; lifecycle, application and full deployment evidence are separate.'})
 return result

def audit(path):
 st=path.stat()
```

### Block 2 — replace

Existing anchor AFTER which:
```text
 st=path.stat()
 if path.is_symlink() or st.st_uid!=0 or st.st_mode&0o022:raise RuntimeError('Profile must be a root-owned non-writable file')
```

Existing anchor BEFORE which:
```text
 def compare(section,key,expected,actual,kind=None):
  a,b=(size(expected),size(actual)) if kind=='size' else (normalized(expected),normalized(actual))
```

Existing content to replace/remove (not copied):
```text
 raw=path.read_bytes();doc=json.loads(raw);c=doc['configuration'];h=c['globalInputs']['hardware'];sections=c['sections'];rows=[]
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
 raw=path.read_bytes();doc=normalize_profile(json.loads(raw));c=doc['configuration'];h=c['globalInputs']['hardware'];sections=c['sections'];rows=[]
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
 st=path.stat()
 if path.is_symlink() or st.st_uid!=0 or st.st_mode&0o022:raise RuntimeError('Profile must be a root-owned non-writable file')
 raw=path.read_bytes();doc=normalize_profile(json.loads(raw));c=doc['configuration'];h=c['globalInputs']['hardware'];sections=c['sections'];rows=[]
 def compare(section,key,expected,actual,kind=None):
  a,b=(size(expected),size(actual)) if kind=='size' else (normalized(expected),normalized(actual))
```

### Block 3 — replace

Existing anchor AFTER which:
```text
   match=re.match(r'^\s*([a-zA-Z_][\w.]*)\s*=',line)
   if match and match[1] in ini_keys:exceptions.append({'path':str(file),'key':match[1]})
```

Existing anchor BEFORE which:
```text
 return report
if __name__=='__main__':
```

Existing content to replace/remove (not copied):
```text
 report={'schemaVersion':1,'at':int(time.time()),'profileSha256':hashlib.sha256(raw).hexdigest(),'scope':'Allowlisted saved/configured values, service state and kernel aggregate limits; HTTP and load evidence are separate. Root document .user.ini exceptions are listed; nested/application overrides require HTTP checks. Not a complete virtual-host parser or lifecycle certificate.','checks':len(rows),'mismatches':[row for row in rows if not row['match']],'inheritanceExceptions':exceptions,'rows':rows}
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
 report={'schemaVersion':1,'at':int(time.time()),'profileSha256':hashlib.sha256(raw).hexdigest(),'scope':'Allowlisted saved/configured values, service state and kernel aggregate limits; HTTP and load evidence are separate. Root document .user.ini exceptions are listed; nested/application overrides require HTTP checks. Not a complete virtual-host parser or lifecycle certificate.','checks':len(rows),'sectionCoverage':section_coverage(sections,rows),'mismatches':[row for row in rows if not row['match']],'inheritanceExceptions':exceptions,'rows':rows}
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
   match=re.match(r'^\s*([a-zA-Z_][\w.]*)\s*=',line)
   if match and match[1] in ini_keys:exceptions.append({'path':str(file),'key':match[1]})
 report={'schemaVersion':1,'at':int(time.time()),'profileSha256':hashlib.sha256(raw).hexdigest(),'scope':'Allowlisted saved/configured values, service state and kernel aggregate limits; HTTP and load evidence are separate. Root document .user.ini exceptions are listed; nested/application overrides require HTTP checks. Not a complete virtual-host parser or lifecycle certificate.','checks':len(rows),'sectionCoverage':section_coverage(sections,rows),'mismatches':[row for row in rows if not row['match']],'inheritanceExceptions':exceptions,'rows':rows}
 return report
if __name__=='__main__':
```

## uniselv-resman/core/webuzo-isolation.py

Installed paths: /usr/local/webuzo/plugins/uniselv-resman/core/webuzo-isolation.py; ALSO /usr/local/uniselv-resman/core/webuzo-isolation.py; ALSO /usr/local/sbin/webuzo-isolation.py

Replace the full file; never append duplicate functions/directives. New files run from first through final line.

### Block 1 — replace

Existing anchor AFTER which:
```text
                backlog=int(value[1]) if value else 511
                timeout=request_seconds(pool,p.get('requestTimeoutSeconds',120))
```

Existing anchor BEFORE which:
```text
                # Reserve the native relay upper bound even if a plan changed since unit generation.
                relay=proxy_limits(children,backlog,timeout)
```

Existing content to replace/remove (not copied):
```text
                ceiling=runtime_ceiling(actual_uid,children,p,backlog,timeout)
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                try:ceiling=runtime_ceiling(actual_uid,children,p,backlog,timeout)
                except (ValueError,OSError):
                    print(json.dumps({'event':'php_admission','at':time.time(),'unit':unit,'reason':'account_limits'}),file=sys.stderr,flush=True)
                    raise
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                backlog=int(value[1]) if value else 511
                timeout=request_seconds(pool,p.get('requestTimeoutSeconds',120))
                try:ceiling=runtime_ceiling(actual_uid,children,p,backlog,timeout)
                except (ValueError,OSError):
                    print(json.dumps({'event':'php_admission','at':time.time(),'unit':unit,'reason':'account_limits'}),file=sys.stderr,flush=True)
                    raise
                # Reserve the native relay upper bound even if a plan changed since unit generation.
                relay=proxy_limits(children,backlog,timeout)
```

### Block 2 — replace

Existing anchor AFTER which:
```text
                    grant_ceiling=min(grant_ceiling,contention_ceiling(ceiling,relay['memoryMiB'],p,len(peers)))
                    atomic(ticket,json.dumps({'expires':deadline,'uid':actual_uid,'ceiling':grant_ceiling}))
```

Existing anchor BEFORE which:
```text
            time.sleep(.25)
    finally:
```

Existing content to replace/remove (not copied):
```text
            if time.monotonic()>=deadline:raise RuntimeError('Host PHP admission budget full after bounded wait; no shared fallback')
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
            if time.monotonic()>=deadline:
                minimum=p['workerRssMiB']+48+p['opcacheMiB']+relay['memoryMiB']
                reasons=[]
                if available-p['hostReserveMiB']<minimum:reasons.append('host_reserve')
                if p['phpBudgetMiB']-reserved<minimum:reasons.append('shared_php_budget')
                if account_available is not None and account_available<minimum:reasons.append('account_memory')
                if not dynamic and len(leases)>=p['maxActivePools']:reasons.append('active_pool_limit')
                for reason in reasons or ['account_limits']:
                    print(json.dumps({'event':'php_admission','at':time.time(),'unit':unit,'reason':reason,
                        'availableMiB':available,'reservedMiB':reserved,'accountAvailableMiB':account_available}),file=sys.stderr,flush=True)
                raise RuntimeError('Host PHP admission budget full after bounded wait; no shared fallback')
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                    grant_ceiling=min(grant_ceiling,contention_ceiling(ceiling,relay['memoryMiB'],p,len(peers)))
                    atomic(ticket,json.dumps({'expires':deadline,'uid':actual_uid,'ceiling':grant_ceiling}))
            if time.monotonic()>=deadline:
                minimum=p['workerRssMiB']+48+p['opcacheMiB']+relay['memoryMiB']
                reasons=[]
                if available-p['hostReserveMiB']<minimum:reasons.append('host_reserve')
                if p['phpBudgetMiB']-reserved<minimum:reasons.append('shared_php_budget')
                if account_available is not None and account_available<minimum:reasons.append('account_memory')
                if not dynamic and len(leases)>=p['maxActivePools']:reasons.append('active_pool_limit')
                for reason in reasons or ['account_limits']:
                    print(json.dumps({'event':'php_admission','at':time.time(),'unit':unit,'reason':reason,
                        'availableMiB':available,'reservedMiB':reserved,'accountAvailableMiB':account_available}),file=sys.stderr,flush=True)
                raise RuntimeError('Host PHP admission budget full after bounded wait; no shared fallback')
            time.sleep(.25)
    finally:
```

### Block 3 — replace

Existing anchor AFTER which:
```text
            old_signals[sig]=signal.signal(sig,lambda *_:stopping.set())
    def diagnostic(reason, **details):
```

Existing anchor BEFORE which:
```text
    def unavailable(client):
        client.settimeout(2);header=b''
```

Existing content to replace/remove (not copied):
```text
        print(json.dumps({'event':'php_proxy','unit':unit,'reason':reason,**details}),file=sys.stderr,flush=True)
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
        print(json.dumps({'event':'php_proxy','at':time.time(),'unit':unit,'reason':reason,**details}),file=sys.stderr,flush=True)
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
            old_signals[sig]=signal.signal(sig,lambda *_:stopping.set())
    def diagnostic(reason, **details):
        print(json.dumps({'event':'php_proxy','at':time.time(),'unit':unit,'reason':reason,**details}),file=sys.stderr,flush=True)
    def unavailable(client):
        client.settimeout(2);header=b''
```

### Block 4 — insert

Existing anchor AFTER which:
```text
    base['appliedBudgetMiB']=budget
    atomic(STATE/'installed.json',json.dumps(data,indent=2))
```

Existing anchor BEFORE which:
```text


```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text


def recover_lifecycle():
    with lock('php-lifecycle'):
        pending=STATE/'lifecycle-pending.json'
        if not pending.exists():return
        previous=json.loads(pending.read_text())
        version=previous.get('version','')
        if not re.fullmatch(r'php\d{2,3}',version):raise ValueError('Invalid lifecycle recovery version')
        fixed={str(paths(version)/'bin/fpmctl'),str(STATE/'original-launchers'/version),
               str(STATE/'installed.json'),str(STATE/(version+'.json')),str(BASE/'policy.json')}
        prefixes=('wpiso-manager-'+version,'wpiso-health-'+version,'wpiso-fpm-'+version+'-','wpiso-proxy-'+version+'-')
        for name in previous.get('files',{}):
            path=pathlib.Path(name)
            allowed=(name in fixed or (path.parent in [UNITS,UNITS/'multi-user.target.wants',UNITS/'sockets.target.wants'] and
                     (path.name.startswith(prefixes) or path.name=='php-fpm'+version[3:]+'.service')) or
                     (path.parent==BASE and path.name.startswith(version+'-')) or
                     (path.is_absolute() and '..' not in path.parts and path.is_relative_to(BASE/version)))
            if not allowed:raise ValueError('Recovery journal contains unowned path')
        if not fixed.issubset(previous.get('files',{})) or not {'wpiso-manager-'+version+'.service','wpiso-health-'+version+'.service','php-fpm'+version[3:]+'.service'}.issubset(previous.get('units',{})) or any(not (u.startswith(prefixes) or u=='php-fpm'+version[3:]+'.service') or '/' in u or '..' in u for u in previous.get('units',{})):
            raise ValueError('Recovery journal does not match owned lifecycle files/units')
        if previous.get('status')=='pending':
            restore_lifecycle(previous)
            journal_write(STATE/('lifecycle-recovered-'+str(time.time_ns())+'.json'),previous)
        elif previous.get('status') not in ('committed','rolled-back'):
            raise ValueError('Unknown lifecycle journal status')
        pending.unlink()
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
    base['appliedBudgetMiB']=budget
    atomic(STATE/'installed.json',json.dumps(data,indent=2))


def recover_lifecycle():
    with lock('php-lifecycle'):
        pending=STATE/'lifecycle-pending.json'
        if not pending.exists():return
        previous=json.loads(pending.read_text())
        version=previous.get('version','')
        if not re.fullmatch(r'php\d{2,3}',version):raise ValueError('Invalid lifecycle recovery version')
        fixed={str(paths(version)/'bin/fpmctl'),str(STATE/'original-launchers'/version),
               str(STATE/'installed.json'),str(STATE/(version+'.json')),str(BASE/'policy.json')}
        prefixes=('wpiso-manager-'+version,'wpiso-health-'+version,'wpiso-fpm-'+version+'-','wpiso-proxy-'+version+'-')
        for name in previous.get('files',{}):
            path=pathlib.Path(name)
            allowed=(name in fixed or (path.parent in [UNITS,UNITS/'multi-user.target.wants',UNITS/'sockets.target.wants'] and
                     (path.name.startswith(prefixes) or path.name=='php-fpm'+version[3:]+'.service')) or
                     (path.parent==BASE and path.name.startswith(version+'-')) or
                     (path.is_absolute() and '..' not in path.parts and path.is_relative_to(BASE/version)))
            if not allowed:raise ValueError('Recovery journal contains unowned path')
        if not fixed.issubset(previous.get('files',{})) or not {'wpiso-manager-'+version+'.service','wpiso-health-'+version+'.service','php-fpm'+version[3:]+'.service'}.issubset(previous.get('units',{})) or any(not (u.startswith(prefixes) or u=='php-fpm'+version[3:]+'.service') or '/' in u or '..' in u for u in previous.get('units',{})):
            raise ValueError('Recovery journal does not match owned lifecycle files/units')
        if previous.get('status')=='pending':
            restore_lifecycle(previous)
            journal_write(STATE/('lifecycle-recovered-'+str(time.time_ns())+'.json'),previous)
        elif previous.get('status') not in ('committed','rolled-back'):
            raise ValueError('Unknown lifecycle journal status')
        pending.unlink()


```

### Block 5 — insert

Existing anchor AFTER which:
```text
        data=json.loads((STATE/'installed.json').read_text()) if (STATE/'installed.json').exists() else {'versions':[]}
        for v in data.get('versions',[]):onboard(v)
```

Existing anchor BEFORE which:
```text
    elif ns.command=='onboard':onboard(ns.args[0])
    elif ns.command=='retire':retire(ns.args[0])
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
    elif ns.command=='recover-lifecycle':recover_lifecycle()
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
        data=json.loads((STATE/'installed.json').read_text()) if (STATE/'installed.json').exists() else {'versions':[]}
        for v in data.get('versions',[]):onboard(v)
    elif ns.command=='recover-lifecycle':recover_lifecycle()
    elif ns.command=='onboard':onboard(ns.args[0])
    elif ns.command=='retire':retire(ns.args[0])
```

## uniselv-resman/info.json

Installed paths: /usr/local/webuzo/plugins/uniselv-resman/info.json

Replace the full file; never append duplicate functions/directives. New files run from first through final line.

### Block 1 — replace

Existing anchor AFTER which:
```text
  "name": "UNISELV Resource Manager",
  "slug": "uniselv-resman",
```

Existing anchor BEFORE which:
```text
  "author": "<a href=\"https://refat.ovh\" target=\"_blank\">Refat Rahman</a>",
  "developer": {
```

Existing content to replace/remove (not copied):
```text
  "version": "1.1.23",
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
  "version": "1.1.24",
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
  "name": "UNISELV Resource Manager",
  "slug": "uniselv-resman",
  "version": "1.1.24",
  "author": "<a href=\"https://refat.ovh\" target=\"_blank\">Refat Rahman</a>",
  "developer": {
```

## uniselv-resman/install.php

Installed paths: /usr/local/webuzo/plugins/uniselv-resman/install.php

Replace the full file; never append duplicate functions/directives. New files run from first through final line.

### Block 1 — insert

Existing anchor AFTER which:
```text
if (PHP_SAPI !== 'cli' || !function_exists('posix_geteuid') || posix_geteuid() !== 0) {
    uniselv_lifecycle_fail('Installer requires root CLI execution; activate through the privileged Webuzo dispatcher');
```

Existing anchor BEFORE which:
```text
}

```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
}

// Preflight adopted runtime compatibility before copying any agent files.
$preflight_runtime = '/usr/local/sbin/webuzo-isolation.py';
$preflight_bundle = __DIR__ . '/core/webuzo-isolation.py';
if (is_file($preflight_runtime) && (!is_file($preflight_bundle) || is_link($preflight_runtime) ||
    hash_file('sha256', $preflight_runtime) !== hash_file('sha256', $preflight_bundle))) {
    uniselv_lifecycle_fail('Existing isolation runtime differs. Perform a reviewed maintenance upgrade with backups before activation; no agent files were changed');
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
if (PHP_SAPI !== 'cli' || !function_exists('posix_geteuid') || posix_geteuid() !== 0) {
    uniselv_lifecycle_fail('Installer requires root CLI execution; activate through the privileged Webuzo dispatcher');
}

// Preflight adopted runtime compatibility before copying any agent files.
$preflight_runtime = '/usr/local/sbin/webuzo-isolation.py';
$preflight_bundle = __DIR__ . '/core/webuzo-isolation.py';
if (is_file($preflight_runtime) && (!is_file($preflight_bundle) || is_link($preflight_runtime) ||
    hash_file('sha256', $preflight_runtime) !== hash_file('sha256', $preflight_bundle))) {
    uniselv_lifecycle_fail('Existing isolation runtime differs. Perform a reviewed maintenance upgrade with backups before activation; no agent files were changed');
}

```

### Block 2 — insert

Existing anchor AFTER which:
```text
    'apache-fcgi-guard.py' => $agent_dir . '/core/apache-fcgi-guard.py',
    'protection-lifecycle.py' => $agent_dir . '/core/protection-lifecycle.py',
```

Existing anchor BEFORE which:
```text
    'fpm_worker_tracker.php' => $agent_dir . '/core/fpm_worker_tracker.php'
];
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
    'configuration-audit.py' => $agent_dir . '/core/configuration-audit.py',
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
    'apache-fcgi-guard.py' => $agent_dir . '/core/apache-fcgi-guard.py',
    'protection-lifecycle.py' => $agent_dir . '/core/protection-lifecycle.py',
    'configuration-audit.py' => $agent_dir . '/core/configuration-audit.py',
    'fpm_worker_tracker.php' => $agent_dir . '/core/fpm_worker_tracker.php'
];
```

### Block 3 — replace

Existing anchor AFTER which:
```text
            uniselv_checked_copy($src_file, $agent_dir . '/core/' . $fname, ($fname === 'fpm_worker_tracker.php') ? 0755 : 0750);
            
```

Existing anchor BEFORE which:
```text
                if (!file_exists($dest_path)) {
                    uniselv_checked_copy($src_file, $dest_path, 0750);
```

Existing content to replace/remove (not copied):
```text
            if (!in_array($fname, ['fpm_worker_tracker.php', 'apache-fcgi-guard.py', 'protection-lifecycle.py'])) {
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
            if (!in_array($fname, ['fpm_worker_tracker.php', 'apache-fcgi-guard.py', 'protection-lifecycle.py', 'configuration-audit.py'])) {
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
            uniselv_checked_copy($src_file, $agent_dir . '/core/' . $fname, ($fname === 'fpm_worker_tracker.php') ? 0755 : 0750);
            
            if (!in_array($fname, ['fpm_worker_tracker.php', 'apache-fcgi-guard.py', 'protection-lifecycle.py', 'configuration-audit.py'])) {
                if (!file_exists($dest_path)) {
                    uniselv_checked_copy($src_file, $dest_path, 0750);
```

## uniselv-resman/uniselv-resman.php

Installed paths: /usr/local/webuzo/plugins/uniselv-resman/uniselv-resman.php

Replace the full file; never append duplicate functions/directives. New files run from first through final line.

### Block 1 — replace

Existing anchor AFTER which:
```text
/*
Plugin Name: UNISELV Resource Manager
```

Existing anchor BEFORE which:
```text
Description: Enterprise Resource Management, Cgroups v2 Isolation, Real-Time Monitoring & Telemetry for Webuzo.
Author: Refat Rahman
```

Existing content to replace/remove (not copied):
```text
Version: 1.1.23
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
Version: 1.1.24
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
/*
Plugin Name: UNISELV Resource Manager
Version: 1.1.24
Description: Enterprise Resource Management, Cgroups v2 Isolation, Real-Time Monitoring & Telemetry for Webuzo.
Author: Refat Rahman
```

### Block 2 — replace

Existing anchor AFTER which:
```text
            'save_package_mapping', 'delete_package_mapping', 'webhook',
            'save_account_permission', 'save_role_permission',
```

Existing anchor BEFORE which:
```text
        ];
        
```

Existing content to replace/remove (not copied):
```text
            'clear_audit_logs', 'purge_snapshots', 'onboard_php', 'retire_php'
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
            'clear_audit_logs', 'purge_snapshots', 'onboard_php', 'retire_php', 'run_governance'
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
            'save_package_mapping', 'delete_package_mapping', 'webhook',
            'save_account_permission', 'save_role_permission',
            'clear_audit_logs', 'purge_snapshots', 'onboard_php', 'retire_php', 'run_governance'
        ];
        
```

### Block 3 — replace

Existing anchor AFTER which:
```text
            'onboard_php' => 'onboard_php_version',
            'retire_php' => 'retire_php_version',
```

Existing anchor BEFORE which:
```text
        ];

```

Existing content to replace/remove (not copied):
```text
            'php_lifecycle' => 'get_php_lifecycle'
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
            'php_lifecycle' => 'get_php_lifecycle',
            'runtime_governance' => 'get_runtime_governance',
            'run_governance' => 'run_runtime_governance',
            'export_governance' => 'export_runtime_governance'
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
            'onboard_php' => 'onboard_php_version',
            'retire_php' => 'retire_php_version',
            'php_lifecycle' => 'get_php_lifecycle',
            'runtime_governance' => 'get_runtime_governance',
            'run_governance' => 'run_runtime_governance',
            'export_governance' => 'export_runtime_governance'
        ];

```

### Block 4 — replace

Existing anchor AFTER which:
```text
    $i18n_dict = uniselv_get_i18n_dict();

```

Existing anchor BEFORE which:
```text
    echo '<style>:root { --uniselv-primary: ' . $brand_color . '; --primary-color: ' . $brand_color . '; }</style>';
    echo '<script>
```

Existing content to replace/remove (not copied):
```text
    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '-1.1.23r2' . '">';
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '-1.1.24r2' . '">';
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
    $i18n_dict = uniselv_get_i18n_dict();

    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '-1.1.24r2' . '">';
    echo '<style>:root { --uniselv-primary: ' . $brand_color . '; --primary-color: ' . $brand_color . '; }</style>';
    echo '<script>
```

### Block 5 — replace

Existing anchor AFTER which:
```text
window.UNISELV_TRANSLATIONS = ' . json_encode($i18n_dict[$locale] ?? $i18n_dict['en']) . ';
</script>';
```

Existing anchor BEFORE which:
```text

    echo '<div class="uniselv-container">';
```

Existing content to replace/remove (not copied):
```text
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '-1.1.23r2' . '"></script>';
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '-1.1.24r2' . '"></script>';
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
window.UNISELV_TRANSLATIONS = ' . json_encode($i18n_dict[$locale] ?? $i18n_dict['en']) . ';
</script>';
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '-1.1.24r2' . '"></script>';

    echo '<div class="uniselv-container">';
```

### Block 6 — insert

Existing anchor AFTER which:
```text
            <div id="uniselv-php-lifecycle" class="uniselv-table-wrap" role="status" aria-live="polite">Open this section to load PHP status.</div>
        </div>
```

Existing anchor BEFORE which:
```text
        <!-- Card 1: Feature Controls & Self-Service Governance -->
        <div class="uniselv-card mb-4">
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
        <div class="uniselv-card mb-4" id="uniselv-governance-card">
            <h5>Runtime Governance &amp; Configuration Evidence</h5>
            <p>PHP installations and vendor changes are checked every minute. Automatic onboarding/repair requires a stable installation, matching reviewed global settings and successful lifecycle preflight. No account-specific PHP settings are created.</p>
            <div class="uniselv-governance-actions">
                <button class="uniselv-btn btn-outline" id="governance-refresh">Refresh Evidence</button>
                <button class="uniselv-btn btn-primary" id="governance-scan">Reconcile PHP Changes</button>
                <button class="uniselv-btn btn-outline" id="governance-recover">Recover Pending Operation</button>
                <button class="uniselv-btn btn-outline" id="governance-export">Prepare &amp; Download Comparison</button>
            </div>
            <p id="governance-job" role="status" aria-live="polite"></p>
            <div id="uniselv-runtime-governance">Open this section to load evidence.</div>
            <p class="uniselv-governance-note">Before uninstalling PHP, move its sites to another registered version, then use Retire Runtime below. Missing installation files block automatic retirement. Exports contain account paths; share only with your administrator.</p>
        </div>
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
            <div id="uniselv-php-lifecycle" class="uniselv-table-wrap" role="status" aria-live="polite">Open this section to load PHP status.</div>
        </div>
        <div class="uniselv-card mb-4" id="uniselv-governance-card">
            <h5>Runtime Governance &amp; Configuration Evidence</h5>
            <p>PHP installations and vendor changes are checked every minute. Automatic onboarding/repair requires a stable installation, matching reviewed global settings and successful lifecycle preflight. No account-specific PHP settings are created.</p>
            <div class="uniselv-governance-actions">
                <button class="uniselv-btn btn-outline" id="governance-refresh">Refresh Evidence</button>
                <button class="uniselv-btn btn-primary" id="governance-scan">Reconcile PHP Changes</button>
                <button class="uniselv-btn btn-outline" id="governance-recover">Recover Pending Operation</button>
                <button class="uniselv-btn btn-outline" id="governance-export">Prepare &amp; Download Comparison</button>
            </div>
            <p id="governance-job" role="status" aria-live="polite"></p>
            <div id="uniselv-runtime-governance">Open this section to load evidence.</div>
            <p class="uniselv-governance-note">Before uninstalling PHP, move its sites to another registered version, then use Retire Runtime below. Missing installation files block automatic retirement. Exports contain account paths; share only with your administrator.</p>
        </div>
        <!-- Card 1: Feature Controls & Self-Service Governance -->
        <div class="uniselv-card mb-4">
```

### Block 7 — replace

Existing anchor AFTER which:
```text
    $i18n_dict = uniselv_get_i18n_dict();

```

Existing anchor BEFORE which:
```text
    echo '<style>:root { --uniselv-primary: ' . $brand_color . '; --primary-color: ' . $brand_color . '; }</style>';
    echo '<script>
```

Existing content to replace/remove (not copied):
```text
    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '-1.1.23r2' . '">';
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '-1.1.24r2' . '">';
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
    $i18n_dict = uniselv_get_i18n_dict();

    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '-1.1.24r2' . '">';
    echo '<style>:root { --uniselv-primary: ' . $brand_color . '; --primary-color: ' . $brand_color . '; }</style>';
    echo '<script>
```

### Block 8 — replace

Existing anchor AFTER which:
```text
window.UNISELV_TRANSLATIONS = ' . json_encode($i18n_dict[$locale] ?? $i18n_dict['en']) . ';
</script>';
```

Existing anchor BEFORE which:
```text

    echo '<div class="uniselv-container">';
```

Existing content to replace/remove (not copied):
```text
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '-1.1.23r2' . '"></script>';
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '-1.1.24r2' . '"></script>';
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
window.UNISELV_TRANSLATIONS = ' . json_encode($i18n_dict[$locale] ?? $i18n_dict['en']) . ';
</script>';
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '-1.1.24r2' . '"></script>';

    echo '<div class="uniselv-container">';
```

## uniselv-resman/views/admin_help.php

Installed paths: /usr/local/webuzo/plugins/uniselv-resman/views/admin_help.php

Replace the full file; never append duplicate functions/directives. New files run from first through final line.

### Block 1 — insert

Existing anchor AFTER which:
```text
 * Role-specific, searchable, responsive enterprise documentation for Webuzo Administrators.
 */
```

Existing anchor BEFORE which:
```text
?>
<div id="tab-help" class="uniselv-tab-content">
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
$uniselvHelpInfo = json_decode(file_get_contents(__DIR__ . '/../info.json'), true) ?: [];
$uniselvHelpOs = @parse_ini_file('/etc/os-release', false, INI_SCANNER_RAW) ?: [];
$uniselvHelpEscape = static function($value) { return htmlspecialchars((string)$value, ENT_QUOTES, 'UTF-8'); };
$uniselvHelpVersion = $uniselvHelpInfo['version'] ?? 'Unavailable';
$uniselvHelpPanel = isset($globals['version']) && is_scalar($globals['version']) ? $globals['version'] : 'Read the current Webuzo panel header';
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
 * Role-specific, searchable, responsive enterprise documentation for Webuzo Administrators.
 */
$uniselvHelpInfo = json_decode(file_get_contents(__DIR__ . '/../info.json'), true) ?: [];
$uniselvHelpOs = @parse_ini_file('/etc/os-release', false, INI_SCANNER_RAW) ?: [];
$uniselvHelpEscape = static function($value) { return htmlspecialchars((string)$value, ENT_QUOTES, 'UTF-8'); };
$uniselvHelpVersion = $uniselvHelpInfo['version'] ?? 'Unavailable';
$uniselvHelpPanel = isset($globals['version']) && is_scalar($globals['version']) ? $globals['version'] : 'Read the current Webuzo panel header';
?>
<div id="tab-help" class="uniselv-tab-content">
```

### Block 2 — insert

Existing anchor AFTER which:
```text
    <!-- Documentation Articles Grid -->
    <div class="uniselv-help-grid">
```

Existing anchor BEFORE which:
```text

        <!-- 1. QUICK START -->
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
        <div class="uniselv-help-card" data-cat="features" id="help-topic-runtime">
            <span class="uniselv-help-badge badge-cat-features">Runtime Governance</span>
            <h4 class="uniselv-help-card-title">PHP Lifecycle, Configuration Drift &amp; Recovery</h4>
            <div class="uniselv-help-card-desc">
                <strong>Menu:</strong> System &amp; Agent Health &gt; Runtime Governance &amp; Configuration Evidence.
                <ol>
                    <li><strong>Install or update PHP:</strong> Apply the generator values globally for that version. Automatic onboarding/repair waits for stable observations, matching reviewed settings and successful preflight. Maintenance Mode pauses background governance.</li>
                    <li><strong>Review differences:</strong> Choose <strong>Refresh Evidence</strong>. Expected/actual settings, account INI exceptions and per-section coverage are displayed. Incomplete scans and sections not checked are labelled; no differences is not full deployment certification.</li>
                    <li><strong>Retry after fixing a cause:</strong> Choose <strong>Reconcile PHP Changes</strong>. This resets retry history without bypassing safety checks.</li>
                    <li><strong>Uninstall PHP:</strong> Move its sites first, then choose <strong>Retire Runtime</strong> and confirm successful retirement before removing software in Webuzo. <strong>Enable Runtime</strong> permits registration again. Missing files or remaining pools block unsafe retirement.</li>
                    <li><strong>Investigate busy responses:</strong> Read <strong>Capacity Events</strong> and <strong>Recent Capacity Event Timeline</strong>. These are bounded journal events, not unique visitors; account limits, shared budget and queues can have different causes.</li>
                    <li><strong>Recover or export:</strong> Use <strong>Recover Pending Operation</strong> for an interrupted lifecycle transaction, or <strong>Prepare &amp; Download Comparison</strong> for private diagnostics. Failed recovery retains its journal. Exports contain account paths; share privately.</li>
                </ol>
                Native PHP-FPM defaults remain global; automatic account runtime caps borrow available shared capacity rather than reserving workers for idle accounts. Tuning values come from the reviewed generator profile, not this help page.
            </div>
        </div>
        <div class="uniselv-help-card" data-cat="trouble" id="help-topic-runtime-advanced">
            <span class="uniselv-help-badge">Advanced Runbook</span>
            <h4 class="uniselv-help-card-title">Runtime Operations, Exact Source Placement &amp; Validation Scope</h4>
            <div class="uniselv-help-card-desc">Release <?php echo $uniselvHelpEscape($uniselvHelpVersion); ?>. These technical guides describe already-applied changes; they are not additional post-install paste steps.</div>
            <details><summary>Operations, expected profile and verification scope</summary><pre style="white-space:pre-wrap;overflow-wrap:anywhere"><?php echo htmlspecialchars(file_get_contents(__DIR__ . '/../docs/release-1.1.24.md'), ENT_QUOTES, 'UTF-8'); ?></pre></details>
            <details><summary>Exact source replacement and insertion guide</summary><pre style="white-space:pre-wrap;overflow-wrap:anywhere"><?php echo htmlspecialchars(file_get_contents(__DIR__ . '/../docs/source-changes-1.1.24.md'), ENT_QUOTES, 'UTF-8'); ?></pre></details>
        </div>

```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
    <!-- Documentation Articles Grid -->
    <div class="uniselv-help-grid">
        <div class="uniselv-help-card" data-cat="features" id="help-topic-runtime">
            <span class="uniselv-help-badge badge-cat-features">Runtime Governance</span>
            <h4 class="uniselv-help-card-title">PHP Lifecycle, Configuration Drift &amp; Recovery</h4>
            <div class="uniselv-help-card-desc">
                <strong>Menu:</strong> System &amp; Agent Health &gt; Runtime Governance &amp; Configuration Evidence.
                <ol>
                    <li><strong>Install or update PHP:</strong> Apply the generator values globally for that version. Automatic onboarding/repair waits for stable observations, matching reviewed settings and successful preflight. Maintenance Mode pauses background governance.</li>
                    <li><strong>Review differences:</strong> Choose <strong>Refresh Evidence</strong>. Expected/actual settings, account INI exceptions and per-section coverage are displayed. Incomplete scans and sections not checked are labelled; no differences is not full deployment certification.</li>
                    <li><strong>Retry after fixing a cause:</strong> Choose <strong>Reconcile PHP Changes</strong>. This resets retry history without bypassing safety checks.</li>
                    <li><strong>Uninstall PHP:</strong> Move its sites first, then choose <strong>Retire Runtime</strong> and confirm successful retirement before removing software in Webuzo. <strong>Enable Runtime</strong> permits registration again. Missing files or remaining pools block unsafe retirement.</li>
                    <li><strong>Investigate busy responses:</strong> Read <strong>Capacity Events</strong> and <strong>Recent Capacity Event Timeline</strong>. These are bounded journal events, not unique visitors; account limits, shared budget and queues can have different causes.</li>
                    <li><strong>Recover or export:</strong> Use <strong>Recover Pending Operation</strong> for an interrupted lifecycle transaction, or <strong>Prepare &amp; Download Comparison</strong> for private diagnostics. Failed recovery retains its journal. Exports contain account paths; share privately.</li>
                </ol>
                Native PHP-FPM defaults remain global; automatic account runtime caps borrow available shared capacity rather than reserving workers for idle accounts. Tuning values come from the reviewed generator profile, not this help page.
            </div>
        </div>
        <div class="uniselv-help-card" data-cat="trouble" id="help-topic-runtime-advanced">
            <span class="uniselv-help-badge">Advanced Runbook</span>
            <h4 class="uniselv-help-card-title">Runtime Operations, Exact Source Placement &amp; Validation Scope</h4>
            <div class="uniselv-help-card-desc">Release <?php echo $uniselvHelpEscape($uniselvHelpVersion); ?>. These technical guides describe already-applied changes; they are not additional post-install paste steps.</div>
            <details><summary>Operations, expected profile and verification scope</summary><pre style="white-space:pre-wrap;overflow-wrap:anywhere"><?php echo htmlspecialchars(file_get_contents(__DIR__ . '/../docs/release-1.1.24.md'), ENT_QUOTES, 'UTF-8'); ?></pre></details>
            <details><summary>Exact source replacement and insertion guide</summary><pre style="white-space:pre-wrap;overflow-wrap:anywhere"><?php echo htmlspecialchars(file_get_contents(__DIR__ . '/../docs/source-changes-1.1.24.md'), ENT_QUOTES, 'UTF-8'); ?></pre></details>
        </div>


        <!-- 1. QUICK START -->
```

### Block 3 — replace

Existing anchor AFTER which:
```text
            </div>
            <ol style="margin: 0 0 14px 20px; padding: 0; color: #475569; font-size: 0.9rem; line-height: 1.6;">
```

Existing anchor BEFORE which:
```text
                <li><strong>Native Plan Synchronization:</strong> Click <strong>Bulk Sync All Plans</strong> at the top right to verify that all Webuzo plans are propagated into individual account slices (<code>golden-&lt;uid&gt;.slice</code>).</li>
                <li><strong>Golden Shield Safety Cap:</strong> Check the <strong>Golden Shield & Capacity</strong> tab to confirm that parent aggregate limits (<code>golden.slice</code>) are active with shared aggregate CPU headroom (e.g. 340% hosting + 60% system headroom on 4 vCPUs).</li>
```

Existing content to replace/remove (not copied):
```text
                <li><strong>Automatic Governance:</strong> The background agent (<code>uniselv-resman-agent.service</code>) starts automatically, collects 10-second telemetry samples, manages database retention, and validates cgroup sync.</li>
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                <li><strong>Automatic Governance:</strong> The background agent (<code>uniselv-resman-agent.service</code>) starts automatically, collects telemetry at the frequency selected under System &amp; Agent Health (5 seconds is the default), manages database retention, and validates cgroup sync.</li>
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
            </div>
            <ol style="margin: 0 0 14px 20px; padding: 0; color: #475569; font-size: 0.9rem; line-height: 1.6;">
                <li><strong>Automatic Governance:</strong> The background agent (<code>uniselv-resman-agent.service</code>) starts automatically, collects telemetry at the frequency selected under System &amp; Agent Health (5 seconds is the default), manages database retention, and validates cgroup sync.</li>
                <li><strong>Native Plan Synchronization:</strong> Click <strong>Bulk Sync All Plans</strong> at the top right to verify that all Webuzo plans are propagated into individual account slices (<code>golden-&lt;uid&gt;.slice</code>).</li>
                <li><strong>Golden Shield Safety Cap:</strong> Check the <strong>Golden Shield Governance</strong> tab to confirm that parent aggregate limits (<code>golden.slice</code>) are active with shared aggregate CPU headroom (e.g. 340% hosting + 60% system headroom on 4 vCPUs).</li>
```

### Block 4 — replace

Existing anchor AFTER which:
```text
                <li><strong>Automatic Governance:</strong> The background agent (<code>uniselv-resman-agent.service</code>) starts automatically, collects 10-second telemetry samples, manages database retention, and validates cgroup sync.</li>
                <li><strong>Native Plan Synchronization:</strong> Click <strong>Bulk Sync All Plans</strong> at the top right to verify that all Webuzo plans are propagated into individual account slices (<code>golden-&lt;uid&gt;.slice</code>).</li>
```

Existing anchor BEFORE which:
```text
            </ol>
            <div class="uniselv-code-block">
```

Existing content to replace/remove (not copied):
```text
                <li><strong>Golden Shield Safety Cap:</strong> Check the <strong>Golden Shield & Capacity</strong> tab to confirm that parent aggregate limits (<code>golden.slice</code>) are active with shared aggregate CPU headroom (e.g. 340% hosting + 60% system headroom on 4 vCPUs).</li>
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                <li><strong>Golden Shield Safety Cap:</strong> Check the <strong>Golden Shield Governance</strong> tab to confirm that parent aggregate limits (<code>golden.slice</code>) are active with shared aggregate CPU headroom (e.g. 340% hosting + 60% system headroom on 4 vCPUs).</li>
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                <li><strong>Automatic Governance:</strong> The background agent (<code>uniselv-resman-agent.service</code>) starts automatically, collects telemetry at the frequency selected under System &amp; Agent Health (5 seconds is the default), manages database retention, and validates cgroup sync.</li>
                <li><strong>Native Plan Synchronization:</strong> Click <strong>Bulk Sync All Plans</strong> at the top right to verify that all Webuzo plans are propagated into individual account slices (<code>golden-&lt;uid&gt;.slice</code>).</li>
                <li><strong>Golden Shield Safety Cap:</strong> Check the <strong>Golden Shield Governance</strong> tab to confirm that parent aggregate limits (<code>golden.slice</code>) are active with shared aggregate CPU headroom (e.g. 340% hosting + 60% system headroom on 4 vCPUs).</li>
            </ol>
            <div class="uniselv-code-block">
```

### Block 5 — replace

Existing anchor AFTER which:
```text
            <h4 class="uniselv-help-card-title">Server Overview & Top Consumers Dashboard</h4>
            <div class="uniselv-help-card-desc">
```

Existing anchor BEFORE which:
```text
                <strong>Menu:</strong> <em>Server Overview</em> tab.<br>
                <strong>Prerequisites:</strong> Active background agent daemon.<br>
```

Existing content to replace/remove (not copied):
```text
                <strong>What it does:</strong> Provides instant visual telemetry of physical hardware, aggregate shared headroom, active RAM safety budget, 1m/5m/15m system loads, and live ranking of the top consuming hosting accounts.<br>
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                <strong>What it does:</strong> Provides telemetry of visible server hardware, aggregate shared headroom, active RAM safety budget, 1m/5m/15m system loads, and live ranking of the top consuming hosting accounts.<br>
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
            <h4 class="uniselv-help-card-title">Server Overview & Top Consumers Dashboard</h4>
            <div class="uniselv-help-card-desc">
                <strong>What it does:</strong> Provides telemetry of visible server hardware, aggregate shared headroom, active RAM safety budget, 1m/5m/15m system loads, and live ranking of the top consuming hosting accounts.<br>
                <strong>Menu:</strong> <em>Server Overview</em> tab.<br>
                <strong>Prerequisites:</strong> Active background agent daemon.<br>
```

### Block 6 — replace

Existing anchor AFTER which:
```text
                <strong>Usage Steps:</strong>
                <ol style="margin: 6px 0 10px 20px; padding: 0;">
```

Existing anchor BEFORE which:
```text
                    <li>Inspect the <strong>Top Resource Consumers</strong> table to spot accounts approaching 100% of their CPU allowance or suffering throttling.</li>
                    <li>Click <strong>Grant Boost</strong> to provide temporary emergency headroom to any account experiencing a traffic spike.</li>
```

Existing content to replace/remove (not copied):
```text
                    <li>Review the hardware detection card for accurate physical core and RAM readings.</li>
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                    <li>Review the hardware detection card for accurate vCPU and RAM readings.</li>
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                <strong>Usage Steps:</strong>
                <ol style="margin: 6px 0 10px 20px; padding: 0;">
                    <li>Review the hardware detection card for accurate vCPU and RAM readings.</li>
                    <li>Inspect the <strong>Top Resource Consumers</strong> table to spot accounts approaching 100% of their CPU allowance or suffering throttling.</li>
                    <li>Click <strong>Grant Boost</strong> to provide temporary emergency headroom to any account experiencing a traffic spike.</li>
```

### Block 7 — replace

Existing anchor AFTER which:
```text
                    <li>Click <strong>Grant Boost</strong> to provide temporary emergency headroom to any account experiencing a traffic spike.</li>
                </ol>
```

Existing anchor BEFORE which:
```text
            </div>
        </div>
```

Existing content to replace/remove (not copied):
```text
                <strong>Expected Result:</strong> Real-time animated telemetry updates with zero browser lag.
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                <strong>Expected Result:</strong> Telemetry refreshes while the dashboard is active. Check sample age; responsiveness depends on browser and server load.
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                    <li>Click <strong>Grant Boost</strong> to provide temporary emergency headroom to any account experiencing a traffic spike.</li>
                </ol>
                <strong>Expected Result:</strong> Telemetry refreshes while the dashboard is active. Check sample age; responsiveness depends on browser and server load.
            </div>
        </div>
```

### Block 8 — replace

Existing anchor AFTER which:
```text
                <strong>What it does:</strong> Comprehensive inventory of all Webuzo accounts showing assigned plan, core-equivalent CPU %, allowance utilization %, memory footprint, task counts, and throttling incidents. Allows granting temporary plan upgrades that expire cleanly.<br>
                <strong>Menu:</strong> <em>All Accounts</em> tab.<br>
```

Existing anchor BEFORE which:
```text
                <strong>Reversal Steps:</strong> To cancel early, open the modal and select cancel, or wait for the timer to expire automatically.
            </div>
```

Existing content to replace/remove (not copied):
```text
                <strong>Realistic Example:</strong> An e-commerce customer runs a flash sale and their site begins throwing 503 errors due to task exhaustion. An administrator grants a <strong>Turbo</strong> boost (200% CPU, 3072M RAM) for 120 minutes. The agent dynamically reconfigures the slice without touching permanent billing plans, and cleanly restores the original plan upon expiration.<br>
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                <strong>Realistic Example:</strong> An e-commerce site experiences a flash-sale slowdown. First identify the limiting account, shared budget or queue. If the account is constrained and aggregate headroom exists, select a suitable higher plan using its displayed current limits and a bounded duration. A temporary boost does not create more physical RAM or CPU and cannot guarantee removal of 503 errors. Verify restoration or any reported failure after expiry.<br>
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                <strong>What it does:</strong> Comprehensive inventory of all Webuzo accounts showing assigned plan, core-equivalent CPU %, allowance utilization %, memory footprint, task counts, and throttling incidents. Allows granting temporary plan upgrades that expire cleanly.<br>
                <strong>Menu:</strong> <em>All Accounts</em> tab.<br>
                <strong>Realistic Example:</strong> An e-commerce site experiences a flash-sale slowdown. First identify the limiting account, shared budget or queue. If the account is constrained and aggregate headroom exists, select a suitable higher plan using its displayed current limits and a bounded duration. A temporary boost does not create more physical RAM or CPU and cannot guarantee removal of 503 errors. Verify restoration or any reported failure after expiry.<br>
                <strong>Reversal Steps:</strong> To cancel early, open the modal and select cancel, or wait for the timer to expire automatically.
            </div>
```

### Block 9 — replace

Existing anchor AFTER which:
```text
            <h4 class="uniselv-help-card-title">Configured vs Effective Kernel Limit Audit</h4>
            <div class="uniselv-help-card-desc">
```

Existing anchor BEFORE which:
```text
                1. <code>cpu.max</code> numerical quota matches plan CPUQuota.<br>
                2. <code>memory.max</code> matches plan configured memory ceiling.<br>
```

Existing content to replace/remove (not copied):
```text
                <strong>What it does:</strong> Rigorously audits every configured Webuzo plan limit against actual kernel cgroup v2 parameters. A customer slice is only labeled <strong>SYNCHRONIZED</strong> if all six criteria match:<br>
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                <strong>What it does:</strong> Rigorously audits every configured Webuzo plan limit against actual kernel cgroup v2 parameters. A customer slice is only labeled <strong>SYNCHRONIZED</strong> when its implemented checks match, including:<br>
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
            <h4 class="uniselv-help-card-title">Configured vs Effective Kernel Limit Audit</h4>
            <div class="uniselv-help-card-desc">
                <strong>What it does:</strong> Rigorously audits every configured Webuzo plan limit against actual kernel cgroup v2 parameters. A customer slice is only labeled <strong>SYNCHRONIZED</strong> when its implemented checks match, including:<br>
                1. <code>cpu.max</code> numerical quota matches plan CPUQuota.<br>
                2. <code>memory.max</code> matches plan configured memory ceiling.<br>
```

### Block 10 — replace

Existing anchor AFTER which:
```text
                4. <code>memory.swap.max</code> is strictly enforced to 0 bytes.<br>
                5. <code>pids.max</code> matches plan maxtask.<br>
```

Existing anchor BEFORE which:
```text
                <strong>Menu:</strong> <em>Configured vs Effective Audit</em> tab.<br>
                <strong>Action:</strong> If any slice shows <em>MISCONFIGURED</em>, click <strong>Bulk Sync All Plans</strong> to reconcile immediately.
```

Existing content to replace/remove (not copied):
```text
                6. <strong>Ancestor Slice:</strong> The slice is strictly located inside <code>/sys/fs/cgroup/golden.slice/</code>.<br>
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                6. <code>io.max</code> read/write throughput and IOPS rules match the configured plan where limits apply.<br>
                7. <strong>Ancestor Slice:</strong> The slice is strictly located inside <code>/sys/fs/cgroup/golden.slice/</code>.<br>
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                4. <code>memory.swap.max</code> is strictly enforced to 0 bytes.<br>
                5. <code>pids.max</code> matches plan maxtask.<br>
                6. <code>io.max</code> read/write throughput and IOPS rules match the configured plan where limits apply.<br>
                7. <strong>Ancestor Slice:</strong> The slice is strictly located inside <code>/sys/fs/cgroup/golden.slice/</code>.<br>
                <strong>Menu:</strong> <em>Configured vs Effective Audit</em> tab.<br>
                <strong>Action:</strong> If any slice shows <em>MISCONFIGURED</em>, click <strong>Bulk Sync All Plans</strong> to reconcile immediately.
```

### Block 11 — replace

Existing anchor AFTER which:
```text
            <h4 class="uniselv-help-card-title">Resource Metrics & Allowance Mathematics</h4>
            <div class="uniselv-help-card-desc">
```

Existing anchor BEFORE which:
```text
                <strong>Allowance Percentage Example:</strong> If an account is assigned a 200% CPU quota (2 cores) and consumes 150% CPU, its allowance usage is:
                <div style="background:#f1f5f9; padding:8px 12px; border-radius:6px; margin:6px 0; font-family:monospace; font-size:0.85rem;">
```

Existing content to replace/remove (not copied):
```text
                <strong>1. CPU % (Core Equivalent):</strong> 100% CPU equals exactly one full physical CPU core. On a 4 vCPU server, 400% represents total machine capacity.<br>
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                <strong>1. CPU % (Core Equivalent):</strong> 100% CPU represents one logical CPU/vCPU worth of scheduled execution time; it does not guarantee a dedicated physical core. On a 4 vCPU server, 400% represents total machine capacity.<br>
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
            <h4 class="uniselv-help-card-title">Resource Metrics & Allowance Mathematics</h4>
            <div class="uniselv-help-card-desc">
                <strong>1. CPU % (Core Equivalent):</strong> 100% CPU represents one logical CPU/vCPU worth of scheduled execution time; it does not guarantee a dedicated physical core. On a 4 vCPU server, 400% represents total machine capacity.<br>
                <strong>Allowance Percentage Example:</strong> If an account is assigned a 200% CPU quota (2 cores) and consumes 150% CPU, its allowance usage is:
                <div style="background:#f1f5f9; padding:8px 12px; border-radius:6px; margin:6px 0; font-family:monospace; font-size:0.85rem;">
```

### Block 12 — replace

Existing anchor AFTER which:
```text
                <strong>2. Memory Breakdown (Anon vs Cache vs Swap):</strong>
                <ul style="margin:6px 0 6px 20px; padding:0;">
```

Existing anchor BEFORE which:
```text
                    <li><strong>Swap Max = 0:</strong> Strict zero swap enforcement prevents VPS disk thrashing and protects NVMe performance.</li>
                </ul>
```

Existing content to replace/remove (not copied):
```text
                    <li><strong>Anonymous (RSS):</strong> Real application code, PHP-FPM variables, opcache, and MySQL query buffers. Cannot be freed without terminating workers.</li>
                    <li><strong>File Page Cache:</strong> Cached disk files managed by Linux. Automatically reclaimed under pressure; does not trigger OOM.</li>
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                    <li><strong>Anonymous memory:</strong> Heap and stack allocations, including PHP request data. Processes can release memory; anonymous memory is not synonymous with total RSS or shared MySQL memory.</li>
                    <li><strong>File Page Cache:</strong> Cached file data can count toward cgroup memory usage. Reclaimability varies; cache does not make an account immune to OOM.</li>
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                <strong>2. Memory Breakdown (Anon vs Cache vs Swap):</strong>
                <ul style="margin:6px 0 6px 20px; padding:0;">
                    <li><strong>Anonymous memory:</strong> Heap and stack allocations, including PHP request data. Processes can release memory; anonymous memory is not synonymous with total RSS or shared MySQL memory.</li>
                    <li><strong>File Page Cache:</strong> Cached file data can count toward cgroup memory usage. Reclaimability varies; cache does not make an account immune to OOM.</li>
                    <li><strong>Swap Max = 0:</strong> Strict zero swap enforcement prevents VPS disk thrashing and protects NVMe performance.</li>
                </ul>
```

### Block 13 — insert

Existing anchor AFTER which:
```text
                    <li><strong>Swap Max = 0:</strong> Strict zero swap enforcement prevents VPS disk thrashing and protects NVMe performance.</li>
                </ul>
```

Existing anchor BEFORE which:
```text
                <strong>3. Tasks / PIDs (<code>pids.max</code>):</strong> Maximum concurrent threads, PHP-FPM workers, and background subprocesses permitted in the slice. Prevents fork bombs.<br>
                <strong>4. Throttling Events (<code>nr_throttled</code>):</strong> Number of 100ms quota periods where the CFS scheduler paused execution because the account exceeded its quota.<br>
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                <a href="https://docs.kernel.org/admin-guide/cgroup-v2.html" target="_blank" rel="noopener noreferrer">Linux kernel cgroup v2 reference</a><br>
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                    <li><strong>Swap Max = 0:</strong> Strict zero swap enforcement prevents VPS disk thrashing and protects NVMe performance.</li>
                </ul>
                <a href="https://docs.kernel.org/admin-guide/cgroup-v2.html" target="_blank" rel="noopener noreferrer">Linux kernel cgroup v2 reference</a><br>
                <strong>3. Tasks / PIDs (<code>pids.max</code>):</strong> Maximum concurrent threads, PHP-FPM workers, and background subprocesses permitted in the slice. Prevents fork bombs.<br>
                <strong>4. Throttling Events (<code>nr_throttled</code>):</strong> Number of configured CPU bandwidth periods in which execution was throttled. Read the actual period from <code>cpu.max</code>; do not assume every server uses 100 ms.<br>
```

### Block 14 — replace

Existing anchor AFTER which:
```text
                </ul>
                <strong>3. Tasks / PIDs (<code>pids.max</code>):</strong> Maximum concurrent threads, PHP-FPM workers, and background subprocesses permitted in the slice. Prevents fork bombs.<br>
```

Existing anchor BEFORE which:
```text
            </div>
        </div>
```

Existing content to replace/remove (not copied):
```text
                <strong>4. Throttling Events (<code>nr_throttled</code>):</strong> Number of 100ms quota periods where the CFS scheduler paused execution because the account exceeded its quota.<br>
                <strong>5. OOM Kills (<code>oom_kill</code>):</strong> Number of processes terminated by kernel because total slice memory breached <code>memory.max</code>.
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                <strong>4. Throttling Events (<code>nr_throttled</code>):</strong> Number of configured CPU bandwidth periods in which execution was throttled. Read the actual period from <code>cpu.max</code>; do not assume every server uses 100 ms.<br>
                <strong>5. OOM Kills (<code>oom_kill</code>):</strong> Number of processes killed by an OOM killer in this cgroup. Check memory events and ancestor limits to identify the boundary involved.
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                <a href="https://docs.kernel.org/admin-guide/cgroup-v2.html" target="_blank" rel="noopener noreferrer">Linux kernel cgroup v2 reference</a><br>
                <strong>3. Tasks / PIDs (<code>pids.max</code>):</strong> Maximum concurrent threads, PHP-FPM workers, and background subprocesses permitted in the slice. Prevents fork bombs.<br>
                <strong>4. Throttling Events (<code>nr_throttled</code>):</strong> Number of configured CPU bandwidth periods in which execution was throttled. Read the actual period from <code>cpu.max</code>; do not assume every server uses 100 ms.<br>
                <strong>5. OOM Kills (<code>oom_kill</code>):</strong> Number of processes killed by an OOM killer in this cgroup. Check memory events and ancestor limits to identify the boundary involved.
            </div>
        </div>
```

### Block 15 — replace

Existing anchor AFTER which:
```text
                    <li>Open <em>All Accounts</em> tab and check customer’s active tasks vs maximum task limit.</li>
                    <li>If tasks are exhausted, navigate to Enduser view or use SSH to identify hanging PHP-FPM workers.</li>
```

Existing anchor BEFORE which:
```text
                </ol>
                <strong>Scenario 2: Investigating Rogue Process Outside Boundary:</strong>
```

Existing content to replace/remove (not copied):
```text
                    <li>Grant a temporary <strong>Turbo</strong> boost to relieve immediate congestion while debugging slow database queries.</li>
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                    <li>Review <em>System &amp; Agent Health &gt; Runtime Governance &amp; Configuration Evidence</em> for admission/queue reasons. Grant a suitable temporary boost only when account limits and aggregate headroom justify it; investigate slow application/database work separately.</li>
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                    <li>Open <em>All Accounts</em> tab and check customer’s active tasks vs maximum task limit.</li>
                    <li>If tasks are exhausted, navigate to Enduser view or use SSH to identify hanging PHP-FPM workers.</li>
                    <li>Review <em>System &amp; Agent Health &gt; Runtime Governance &amp; Configuration Evidence</em> for admission/queue reasons. Grant a suitable temporary boost only when account limits and aggregate headroom justify it; investigate slow application/database work separately.</li>
                </ol>
                <strong>Scenario 2: Investigating Rogue Process Outside Boundary:</strong>
```

### Block 16 — replace

Existing anchor AFTER which:
```text
                <strong>Scenario 2: Investigating Rogue Process Outside Boundary:</strong>
                <ol style="margin:6px 0 10px 20px; padding:0;">
```

Existing anchor BEFORE which:
```text
                    <li>If any process is detected outside <code>golden.slice</code>, note the PID and executable.</li>
                    <li>Verify whether the customer process was launched via CLI or cron outside systemd user slices.</li>
```

Existing content to replace/remove (not copied):
```text
                    <li>Open <em>Golden Shield & Capacity</em> tab and check <strong>Enforcement Coverage</strong>.</li>
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                    <li>Open <em>Golden Shield Governance</em> tab and check <strong>Enforcement Coverage</strong>.</li>
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                <strong>Scenario 2: Investigating Rogue Process Outside Boundary:</strong>
                <ol style="margin:6px 0 10px 20px; padding:0;">
                    <li>Open <em>Golden Shield Governance</em> tab and check <strong>Enforcement Coverage</strong>.</li>
                    <li>If any process is detected outside <code>golden.slice</code>, note the PID and executable.</li>
                    <li>Verify whether the customer process was launched via CLI or cron outside systemd user slices.</li>
```

### Block 17 — replace

Existing anchor AFTER which:
```text
                <strong>Scenario 3: Rolling Back Bad Policy Settings:</strong>
                <ol style="margin:6px 0 10px 20px; padding:0;">
```

Existing anchor BEFORE which:
```text
                    <li>Select the desired configuration checkpoint from the list.</li>
                    <li>Click <strong>Restore Selected Backup</strong>. The system verifies kernel status and confirms success.</li>
```

Existing content to replace/remove (not copied):
```text
                    <li>Click <strong>Restore Backup</strong> in the Golden Shield Governor tab.</li>
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                    <li>Click <strong>Restore Backup</strong> in the Golden Shield Governance tab.</li>
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                <strong>Scenario 3: Rolling Back Bad Policy Settings:</strong>
                <ol style="margin:6px 0 10px 20px; padding:0;">
                    <li>Click <strong>Restore Backup</strong> in the Golden Shield Governance tab.</li>
                    <li>Select the desired configuration checkpoint from the list.</li>
                    <li>Click <strong>Restore Selected Backup</strong>. The system verifies kernel status and confirms success.</li>
```

### Block 18 — replace

Existing anchor AFTER which:
```text
            <p style="margin:8px 0 4px 0; font-weight:600; font-size:0.85rem; color:#1e293b;">5. Execute IPC Socket Health Query Directly:</p>
            <div class="uniselv-code-block">
```

Existing anchor BEFORE which:
```text
            </div>
        </div>
```

Existing content to replace/remove (not copied):
```text
                <code>python3 -c "import socket; s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM); s.connect('/run/uniselv-resman/agent.sock'); s.send(b'{\"action\":\"get_agent_health\"}\\n'); print(s.recv(4096).decode())"</code>
                <button class="uniselv-copy-btn" onclick="UniselvResMan.copyToClipboard('python3 -c &quot;import socket; s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM); s.connect(\'/run/uniselv-resman/agent.sock\'); s.send(b\'{\\\&quot;action\\\&quot;:\\\&quot;get_agent_health\\\&quot;}\\n\'); print(s.recv(4096).decode())&quot;', this)">Copy</button>
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                <code>sudo python3 -c "import json,socket; s=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM); s.settimeout(10); s.connect('/run/uniselv-resman/agent.sock'); s.sendall((json.dumps({'action':'get_agent_health','auth':{'user':'root','is_admin':True}})+'\n').encode()); print(s.makefile().readline()); s.close()"</code>
                <button class="uniselv-copy-btn" onclick="UniselvResMan.copyToClipboard(this.previousElementSibling.textContent, this)">Copy</button>
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
            <p style="margin:8px 0 4px 0; font-weight:600; font-size:0.85rem; color:#1e293b;">5. Execute IPC Socket Health Query Directly:</p>
            <div class="uniselv-code-block">
                <code>sudo python3 -c "import json,socket; s=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM); s.settimeout(10); s.connect('/run/uniselv-resman/agent.sock'); s.sendall((json.dumps({'action':'get_agent_health','auth':{'user':'root','is_admin':True}})+'\n').encode()); print(s.makefile().readline()); s.close()"</code>
                <button class="uniselv-copy-btn" onclick="UniselvResMan.copyToClipboard(this.previousElementSibling.textContent, this)">Copy</button>
            </div>
        </div>
```

### Block 19 — replace

Existing anchor AFTER which:
```text
            <div class="uniselv-help-card-desc">
                <table style="width:100%; border-collapse:collapse; font-size:0.88rem; color:#334155;">
```

Existing anchor BEFORE which:
```text
                    <tr style="border-bottom:1px solid #f1f5f9;"><td style="padding:6px 0; font-weight:600;">Cgroups Implementation:</td><td>Cgroups v2 Unified Hierarchy (<code>/sys/fs/cgroup</code>)</td></tr>
                    <tr style="border-bottom:1px solid #f1f5f9;"><td style="padding:6px 0; font-weight:600;">Process Safety:</td><td>Zero-race <code>os.pidfd_open</code> signal delivery</td></tr>
```

Existing content to replace/remove (not copied):
```text
                    <tr style="border-bottom:1px solid #f1f5f9;"><td style="padding:6px 0; font-weight:600; width:220px;">Plugin Version:</td><td>1.1.13 — see bundled docs/FRONTEND-OPTIMIZATION-1.1.13.md and docs/LIFECYCLE-REVIEW-1.1.12.md for tested scope and docs/apache-fcgi-integration.md for automatic Apache integration and rollback.</td></tr>
                    <tr style="border-bottom:1px solid #f1f5f9;"><td style="padding:6px 0; font-weight:600;">Host Operating System:</td><td>Ubuntu 24.04.5 LTS (Noble Numbat)</td></tr>
                    <tr style="border-bottom:1px solid #f1f5f9;"><td style="padding:6px 0; font-weight:600;">Active Linux Kernel:</td><td>6.8.0-147-generic (x86_64)</td></tr>
                    <tr style="border-bottom:1px solid #f1f5f9;"><td style="padding:6px 0; font-weight:600;">Control Panel:</td><td>Webuzo 4.8.4 Enterprise</td></tr>
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                    <tr style="border-bottom:1px solid #f1f5f9;"><td style="padding:6px 0; font-weight:600; width:220px;">Plugin Version:</td><td><?php echo $uniselvHelpEscape($uniselvHelpVersion); ?> — see PHP Lifecycle, Configuration Drift &amp; Recovery and the Advanced Runbook.</td></tr>
                    <tr style="border-bottom:1px solid #f1f5f9;"><td style="padding:6px 0; font-weight:600;">Host Operating System:</td><td><?php echo $uniselvHelpEscape($uniselvHelpOs['PRETTY_NAME'] ?? 'Unavailable'); ?></td></tr>
                    <tr style="border-bottom:1px solid #f1f5f9;"><td style="padding:6px 0; font-weight:600;">Active Linux Kernel:</td><td><?php echo $uniselvHelpEscape(php_uname('r') . ' (' . php_uname('m') . ')'); ?></td></tr>
                    <tr style="border-bottom:1px solid #f1f5f9;"><td style="padding:6px 0; font-weight:600;">Control Panel:</td><td>Webuzo <?php echo $uniselvHelpEscape($uniselvHelpPanel); ?></td></tr>
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
            <div class="uniselv-help-card-desc">
                <table style="width:100%; border-collapse:collapse; font-size:0.88rem; color:#334155;">
                    <tr style="border-bottom:1px solid #f1f5f9;"><td style="padding:6px 0; font-weight:600; width:220px;">Plugin Version:</td><td><?php echo $uniselvHelpEscape($uniselvHelpVersion); ?> — see PHP Lifecycle, Configuration Drift &amp; Recovery and the Advanced Runbook.</td></tr>
                    <tr style="border-bottom:1px solid #f1f5f9;"><td style="padding:6px 0; font-weight:600;">Host Operating System:</td><td><?php echo $uniselvHelpEscape($uniselvHelpOs['PRETTY_NAME'] ?? 'Unavailable'); ?></td></tr>
                    <tr style="border-bottom:1px solid #f1f5f9;"><td style="padding:6px 0; font-weight:600;">Active Linux Kernel:</td><td><?php echo $uniselvHelpEscape(php_uname('r') . ' (' . php_uname('m') . ')'); ?></td></tr>
                    <tr style="border-bottom:1px solid #f1f5f9;"><td style="padding:6px 0; font-weight:600;">Control Panel:</td><td>Webuzo <?php echo $uniselvHelpEscape($uniselvHelpPanel); ?></td></tr>
                    <tr style="border-bottom:1px solid #f1f5f9;"><td style="padding:6px 0; font-weight:600;">Cgroups Implementation:</td><td>Cgroups v2 Unified Hierarchy (<code>/sys/fs/cgroup</code>)</td></tr>
                    <tr style="border-bottom:1px solid #f1f5f9;"><td style="padding:6px 0; font-weight:600;">Process Safety:</td><td>Process identity checks with <code>pidfd</code> where supported; inspect the result of each process action.</td></tr>
```

### Block 20 — replace

Existing anchor AFTER which:
```text
                    <tr style="border-bottom:1px solid #f1f5f9;"><td style="padding:6px 0; font-weight:600;">Control Panel:</td><td>Webuzo 4.8.4 Enterprise</td></tr>
                    <tr style="border-bottom:1px solid #f1f5f9;"><td style="padding:6px 0; font-weight:600;">Cgroups Implementation:</td><td>Cgroups v2 Unified Hierarchy (<code>/sys/fs/cgroup</code>)</td></tr>
```

Existing anchor BEFORE which:
```text
                    <tr style="border-bottom:1px solid #f1f5f9;"><td style="padding:6px 0; font-weight:600;">Ownership Manifest:</td><td><code>/var/lib/uniselv-resource-manager/ownership_manifest.json</code></td></tr>
                    <tr><td style="padding:6px 0; font-weight:600;">Developer:</td><td><strong>Refat Rahman</strong> (<a href="https://refat.ovh" target="_blank" style="color:var(--uniselv-primary); text-decoration:none; font-weight:600;">refat.ovh</a>)</td></tr>
```

Existing content to replace/remove (not copied):
```text
                    <tr style="border-bottom:1px solid #f1f5f9;"><td style="padding:6px 0; font-weight:600;">Process Safety:</td><td>Zero-race <code>os.pidfd_open</code> signal delivery</td></tr>
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                    <tr style="border-bottom:1px solid #f1f5f9;"><td style="padding:6px 0; font-weight:600;">Process Safety:</td><td>Process identity checks with <code>pidfd</code> where supported; inspect the result of each process action.</td></tr>
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                    <tr style="border-bottom:1px solid #f1f5f9;"><td style="padding:6px 0; font-weight:600;">Control Panel:</td><td>Webuzo <?php echo $uniselvHelpEscape($uniselvHelpPanel); ?></td></tr>
                    <tr style="border-bottom:1px solid #f1f5f9;"><td style="padding:6px 0; font-weight:600;">Cgroups Implementation:</td><td>Cgroups v2 Unified Hierarchy (<code>/sys/fs/cgroup</code>)</td></tr>
                    <tr style="border-bottom:1px solid #f1f5f9;"><td style="padding:6px 0; font-weight:600;">Process Safety:</td><td>Process identity checks with <code>pidfd</code> where supported; inspect the result of each process action.</td></tr>
                    <tr style="border-bottom:1px solid #f1f5f9;"><td style="padding:6px 0; font-weight:600;">Ownership Manifest:</td><td><code>/var/lib/uniselv-resource-manager/ownership_manifest.json</code></td></tr>
                    <tr><td style="padding:6px 0; font-weight:600;">Developer:</td><td><strong>Refat Rahman</strong> (<a href="https://refat.ovh" target="_blank" style="color:var(--uniselv-primary); text-decoration:none; font-weight:600;">refat.ovh</a>)</td></tr>
```
