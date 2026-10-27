# Exact source guide — Resman 1.1.33

Use the complete reviewed module archive. These changes are already installed by that archive; they are not additional commands after installation.

Runtime paths (same complete source):

- `/usr/local/sbin/webuzo-isolation.py`
- `/usr/local/uniselv-resman/core/webuzo-isolation.py`
- `/usr/local/webuzo/plugins/uniselv-resman/core/webuzo-isolation.py`

## runtime-model

Operation: replacement.

AFTER this verified existing line:

```python
MARKER='# WEBUZO-ISOLATION MANAGED LAUNCHER'
```

BEFORE this verified existing line:

```python
NATIVE_CGROUP_USERS=pathlib.Path('/var/webuzo/conf/cgroupusers')
```

Replace this existing block completely:

```python
CAPACITY_MODEL_VERSION='account-demand-v7-stable-sharing'
```

Copyable generated code (no surrounding context):

```python
CAPACITY_MODEL_VERSION='account-demand-v8-native-reload-safety'
```

Illustrative AFTER-edit excerpt; context only, do not paste again:

```python
MARKER='# WEBUZO-ISOLATION MANAGED LAUNCHER'

CAPACITY_MODEL_VERSION='account-demand-v8-native-reload-safety'

NATIVE_CGROUP_USERS=pathlib.Path('/var/webuzo/conf/cgroupusers')
```

Replace the old block once. If the exact generated helper/block already exists, do not append another copy. Stop on different surrounding content and review the complete file.

## managed-master-grace

Operation: replacement plus missing-helper insertion in one block.

AFTER this verified existing line:

```python
        time.sleep(.5)
```

BEFORE this verified existing line:

```python
def request_seconds(pool, fallback=120):
```

Replace this existing block completely:

```python
def pool_config(version,row):
    prefix=paths(version);backend=RUN/(version+'-'+row['user']+'.sock')
    part=re.sub(r'^(\s*listen\s*=).*$',r'\1 '+str(backend),row['pool'],flags=re.M)
    return '[global]\npid = '+str(RUN/(version+'-'+row['user']+'.pid'))+'\nerror_log = '+str(prefix/'var/log'/('wpiso-'+row['user']+'.log'))+'\n'+row['global']+'\n'+part
```

Copyable generated code (no surrounding context):

```python
def reload_control_settings(global_settings,request_timeout):
    """Do not escalate a graceful reload before valid native requests can finish."""
    timeout=int(request_timeout)
    if not 1<=timeout<=86400:raise ValueError('Finite native request timeout required for reload safety')
    lines=re.findall(r'^\s*process_control_timeout\s*=\s*([^;\r\n]+)',global_settings,re.M)
    if len(lines)>1:raise ValueError('Duplicate global process_control_timeout')
    if lines:
        match=re.fullmatch(r'(\d+)\s*([smhd]?)',lines[0].strip())
        if not match:raise ValueError('Invalid global process_control_timeout')
        current=int(match[1])*{'':1,'s':1,'m':60,'h':3600,'d':86400}[match[2]]
        if current>=timeout:return global_settings
        return re.sub(r'^(\s*process_control_timeout\s*=).*$',lambda m:m[1]+' '+str(timeout)+'s',global_settings,flags=re.M)
    return global_settings.rstrip()+'\nprocess_control_timeout = '+str(timeout)+'s\n'


def pool_config(version,row):
    prefix=paths(version);backend=RUN/(version+'-'+row['user']+'.sock')
    part=re.sub(r'^(\s*listen\s*=).*$',r'\1 '+str(backend),row['pool'],flags=re.M)
    global_settings=reload_control_settings(row['global'],request_seconds(part))
    return '[global]\npid = '+str(RUN/(version+'-'+row['user']+'.pid'))+'\nerror_log = '+str(prefix/'var/log'/('wpiso-'+row['user']+'.log'))+'\n'+global_settings+'\n'+part
```

Illustrative AFTER-edit excerpt; context only, do not paste again:

```python
        time.sleep(.5)

def reload_control_settings(global_settings,request_timeout):
    """Do not escalate a graceful reload before valid native requests can finish."""
    timeout=int(request_timeout)
    if not 1<=timeout<=86400:raise ValueError('Finite native request timeout required for reload safety')
    lines=re.findall(r'^\s*process_control_timeout\s*=\s*([^;\r\n]+)',global_settings,re.M)
    if len(lines)>1:raise ValueError('Duplicate global process_control_timeout')
    if lines:
        match=re.fullmatch(r'(\d+)\s*([smhd]?)',lines[0].strip())
        if not match:raise ValueError('Invalid global process_control_timeout')
        current=int(match[1])*{'':1,'s':1,'m':60,'h':3600,'d':86400}[match[2]]
        if current>=timeout:return global_settings
        return re.sub(r'^(\s*process_control_timeout\s*=).*$',lambda m:m[1]+' '+str(timeout)+'s',global_settings,flags=re.M)
    return global_settings.rstrip()+'\nprocess_control_timeout = '+str(timeout)+'s\n'


def pool_config(version,row):
    prefix=paths(version);backend=RUN/(version+'-'+row['user']+'.sock')
    part=re.sub(r'^(\s*listen\s*=).*$',r'\1 '+str(backend),row['pool'],flags=re.M)
    global_settings=reload_control_settings(row['global'],request_seconds(part))
    return '[global]\npid = '+str(RUN/(version+'-'+row['user']+'.pid'))+'\nerror_log = '+str(prefix/'var/log'/('wpiso-'+row['user']+'.log'))+'\n'+global_settings+'\n'+part

def request_seconds(pool, fallback=120):
```

Replace the old block once. If the exact generated helper/block already exists, do not append another copy. Stop on different surrounding content and review the complete file.

## native-reload

Operation: replacement plus missing-helper insertion in one block.

AFTER this verified existing line:

```python
    print('Successfully retired ' + version + ' from isolation.')
```

BEFORE this verified existing line:

```python
def install(policy_file):
```

Replace this existing block completely:

```python
def action(version,command):
    unit='wpiso-manager-'+version+'.service'
    if not is_managed(version):
        raise RuntimeError('PHP version ' + version + ' is not onboarded in isolation. Run webuzo-isolation.py onboard ' + version + ' first.')
    assert_launcher(version)
    if command in ['start','restart','reload']:
        if execute(['systemctl','is-active',unit],False).returncode==0:reconcile(version,command in ['restart','reload'])
        else:execute(['systemctl','start',unit])
        print(version+': isolated socket routing active')
    elif command=='bridge-stop':execute(['systemctl','--no-block','stop',unit]);print(version+': isolated stop scheduled')
    elif command in ['stop','force-quit']:execute(['systemctl','stop',unit]);print(version+': isolated routing stopped')
    elif command=='configtest':print(version+': '+str(len(parse_pools((paths(version)/'etc/php-fpm.conf').read_text(),version)))+' eligible native pools; no shared fallback')
    elif command=='status':
        r=execute(['systemctl','is-active',unit],False);print('php-fpm is running' if r.returncode==0 else 'php-fpm is stopped');sys.exit(r.returncode)
    else:raise ValueError('Unsupported fpmctl action')
```

Copyable generated code (no surrounding context):

```python
def graceful_reload(version):
    """Apply native configuration without turning an unchanged reload into a stop.

    Changed routing/pool definitions still use normal checked reconciliation.
    Surviving FPM masters re-exec gracefully so php.ini/extensions are refreshed,
    while public socket/proxy units and charged runtime leases remain in place.
    """
    count=reconcile(version,False)
    with lock(version):
        targets=[names(version,row['user'])[0] for row in manifest(version)['pools']]
        targets.append('wpiso-health-'+version+'.service')
        for target in targets:
            if execute(['systemctl','is-active',target],False).returncode!=0:continue
            result=execute(['systemctl','kill','--kill-whom=main','--signal=USR2',target],False)
            # An idle pool may have retired after the state check. Never start it
            # merely to reload, and never hide a failure of a still-live master.
            if result.returncode and execute(['systemctl','is-active',target],False).returncode==0:
                raise RuntimeError('Native graceful PHP reload failed: '+target)
    return count


def action(version,command):
    unit='wpiso-manager-'+version+'.service'
    if not is_managed(version):
        raise RuntimeError('PHP version ' + version + ' is not onboarded in isolation. Run webuzo-isolation.py onboard ' + version + ' first.')
    assert_launcher(version)
    if command in ['start','restart','reload']:
        if execute(['systemctl','is-active',unit],False).returncode==0:
            if command=='reload':graceful_reload(version)
            else:reconcile(version,command=='restart')
        else:execute(['systemctl','start',unit])
        print(version+': isolated socket routing active')
    elif command=='bridge-stop':execute(['systemctl','--no-block','stop',unit]);print(version+': isolated stop scheduled')
    elif command in ['stop','force-quit']:execute(['systemctl','stop',unit]);print(version+': isolated routing stopped')
    elif command=='configtest':print(version+': '+str(len(parse_pools((paths(version)/'etc/php-fpm.conf').read_text(),version)))+' eligible native pools; no shared fallback')
    elif command=='status':
        r=execute(['systemctl','is-active',unit],False);print('php-fpm is running' if r.returncode==0 else 'php-fpm is stopped');sys.exit(r.returncode)
    else:raise ValueError('Unsupported fpmctl action')
```

Illustrative AFTER-edit excerpt; context only, do not paste again:

```python
    print('Successfully retired ' + version + ' from isolation.')

def graceful_reload(version):
    """Apply native configuration without turning an unchanged reload into a stop.

    Changed routing/pool definitions still use normal checked reconciliation.
    Surviving FPM masters re-exec gracefully so php.ini/extensions are refreshed,
    while public socket/proxy units and charged runtime leases remain in place.
    """
    count=reconcile(version,False)
    with lock(version):
        targets=[names(version,row['user'])[0] for row in manifest(version)['pools']]
        targets.append('wpiso-health-'+version+'.service')
        for target in targets:
            if execute(['systemctl','is-active',target],False).returncode!=0:continue
            result=execute(['systemctl','kill','--kill-whom=main','--signal=USR2',target],False)
            # An idle pool may have retired after the state check. Never start it
            # merely to reload, and never hide a failure of a still-live master.
            if result.returncode and execute(['systemctl','is-active',target],False).returncode==0:
                raise RuntimeError('Native graceful PHP reload failed: '+target)
    return count


def action(version,command):
    unit='wpiso-manager-'+version+'.service'
    if not is_managed(version):
        raise RuntimeError('PHP version ' + version + ' is not onboarded in isolation. Run webuzo-isolation.py onboard ' + version + ' first.')
    assert_launcher(version)
    if command in ['start','restart','reload']:
        if execute(['systemctl','is-active',unit],False).returncode==0:
            if command=='reload':graceful_reload(version)
            else:reconcile(version,command=='restart')
        else:execute(['systemctl','start',unit])
        print(version+': isolated socket routing active')
    elif command=='bridge-stop':execute(['systemctl','--no-block','stop',unit]);print(version+': isolated stop scheduled')
    elif command in ['stop','force-quit']:execute(['systemctl','stop',unit]);print(version+': isolated routing stopped')
    elif command=='configtest':print(version+': '+str(len(parse_pools((paths(version)/'etc/php-fpm.conf').read_text(),version)))+' eligible native pools; no shared fallback')
    elif command=='status':
        r=execute(['systemctl','is-active',unit],False);print('php-fpm is running' if r.returncode==0 else 'php-fpm is stopped');sys.exit(r.returncode)
    else:raise ValueError('Unsupported fpmctl action')

def install(policy_file):
```

Replace the old block once. If the exact generated helper/block already exists, do not append another copy. Stop on different surrounding content and review the complete file.

## mechanical-reload-guard

Operation: missing-directive insertion.

AFTER this verified existing line:

```python
                private=(BASE/version/(row['user']+'.conf')).read_text()
```

BEFORE this verified existing line:

```python
                native=row['maxChildren'];backlog=re.search(r'^\s*listen.backlog\s*=\s*(\d+)',private,re.M)
```

Copyable generated code (no surrounding context):

```python
                private_global=re.search(r'^\[global\]\s*\n(.*?)(?=^\[|\Z)',private,re.M|re.S)
                item['managedReloadTimeoutSafe']=bool(private_global) and reload_control_settings(private_global[1],request_seconds(private))==private_global[1]
                results['mechanicalChecksPass']&=item['managedReloadTimeoutSafe']
```

Illustrative AFTER-edit excerpt; context only, do not paste again:

```python
                private=(BASE/version/(row['user']+'.conf')).read_text()

                private_global=re.search(r'^\[global\]\s*\n(.*?)(?=^\[|\Z)',private,re.M|re.S)
                item['managedReloadTimeoutSafe']=bool(private_global) and reload_control_settings(private_global[1],request_seconds(private))==private_global[1]
                results['mechanicalChecksPass']&=item['managedReloadTimeoutSafe']

                native=row['maxChildren'];backlog=re.search(r'^\s*listen.backlog\s*=\s*(\d+)',private,re.M)
```

Replace the old block once. If the exact generated helper/block already exists, do not append another copy. Stop on different surrounding content and review the complete file.

## Canonical generator embedded source

Replace the complete `uniselv.win/webuzo-planner/free-shield-assets.json` from document start to document end with the supplied reviewed file, or regenerate its two logical keys using the existing JSON build workflow. The generated Python source belongs inside `files.isolation.py` as a JSON string, with its LF UTF-8 hash inside `sha256.isolation.py`. Do not append Python after JSON, or create duplicate keys. The full replacement file is provided separately in the canonical archive.

## Save and verification

1. Save complete UTF-8 LF files, preserving original root ownership and installed modes.
2. Update owned runtime hashes/restoration manifests together through the reviewed updater; do not hand-edit a running controller without a drained rollback plan.
3. Compile Python and run the native reload regressions before deployment.
4. Restart coordinators in a controlled drained maintenance window after source replacement so existing proxy processes load the new code.
5. Run webuzo-isolation.py verify, golden-shield.py check and configuration-audit.py. ManagedReloadTimeoutSafe must pass for every managed pool.
6. Verify public uncached product responses and native foreground/background reload completion. Never infer workload capacity from matching values alone.
