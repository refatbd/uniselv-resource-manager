# Exact source changes — 1.1.23

Already applied; prefer complete file replacement. Do not append duplicate functions. Use complete existing blocks to disambiguate repeated anchors. Save UTF-8/LF and verify syntax/regressions.

## /usr/local/sbin/webuzo-isolation.py

Replace the complete installed file with reviewed release content. Do not append duplicate functions.

AFTER: `import queue`

BEFORE: `import argparse,contextlib,fcntl,hashlib,json,os,pathlib,pwd,re,shutil,signal,socket,subprocess,sys,time,select,struct,threading`

Existing code:
```

```

Generated replacement/insertion:
```
import base64
```

Illustrative after-edit context:
```
"""Experimental Webuzo FPM launcher integration. Root-only; never falls back to shared FPM."""
import queue
import base64
import argparse,contextlib,fcntl,hashlib,json,os,pathlib,pwd,re,shutil,signal,socket,subprocess,sys,time,select,struct,threading
BASE=pathlib.Path('/etc/webuzo-isolation')
```

AFTER: ``

BEFORE: `    prefix=paths(version);sections=list(re.finditer(r'^\[([^\]\r\n]+)\][ \t]*$',text,re.M));rows=[]`

Existing code:
```
def parse_pools(text,version):
```

Generated replacement/insertion:
```
def parse_pools(text,version,prepare=True):
```

Illustrative after-edit context:
```
    return root

def parse_pools(text,version,prepare=True):
    prefix=paths(version);sections=list(re.finditer(r'^\[([^\]\r\n]+)\][ \t]*$',text,re.M));rows=[]
    global_match=re.search(r'^\[global\][ \t]*\n(.*?)(?=^\[|\Z)',text,re.M|re.S)
```

AFTER: `        if field('pm')!='ondemand':raise ValueError('This integration currently requires global ondemand')`

BEFORE: `        rows.append({'user':user,'uid':account.pw_uid,'name':name,'originalSocket':original,'pool':part,'global':global_settings,'maxChildren':int(field('pm.max_children')),'backlog':int(field('listen.backlog'))})`

Existing code:
```
        ensure_limits(user,account.pw_uid)
```

Generated replacement/insertion:
```
        if prepare:ensure_limits(user,account.pw_uid)
```

Illustrative after-edit context:
```
        for control in ['pm','pm.max_children','listen.backlog']:field(control)
        if field('pm')!='ondemand':raise ValueError('This integration currently requires global ondemand')
        if prepare:ensure_limits(user,account.pw_uid)
        rows.append({'user':user,'uid':account.pw_uid,'name':name,'originalSocket':original,'pool':part,'global':global_settings,'maxChildren':int(field('pm.max_children')),'backlog':int(field('listen.backlog'))})
    return rows
```

AFTER: `    if not (STATE/'installed.json').exists(): return False`

BEFORE: ``

Existing code:
```
    try:
        data = json.loads((STATE/'installed.json').read_text())
        return version in data.get('versions', [])
    except Exception:
        return False
```

Generated replacement/insertion:
```
    data = json.loads((STATE/'installed.json').read_text())
    versions = data.get('versions')
    if not isinstance(versions,list) or any(not isinstance(v,str) or not re.fullmatch(r'php\d{2,3}',v) for v in versions):
        raise ValueError('Invalid managed PHP registry')
    return version in versions


def lifecycle_files(version):
    """Only this version's owned control files; never snapshot customer content."""
    exact=[paths(version)/'bin/fpmctl',STATE/'original-launchers'/version,STATE/'installed.json',
           STATE/(version+'.json'),BASE/'policy.json']
    prefixes=['wpiso-manager-'+version,'wpiso-health-'+version,'wpiso-fpm-'+version+'-',
              'wpiso-proxy-'+version+'-']
    for directory in [UNITS,UNITS/'multi-user.target.wants',UNITS/'sockets.target.wants']:
        if directory.exists():
            exact.extend(p for p in directory.iterdir() if p.name.startswith(tuple(prefixes)) or p.name=='php-fpm'+version[3:]+'.service')
    exact.extend(UNITS/n for n in ['wpiso-manager-'+version+'.service','wpiso-health-'+version+'.service','php-fpm'+version[3:]+'.service'])
    if BASE.exists():
        exact.extend(p for p in BASE.glob(version+'-*') if p.is_file())
    if (BASE/version).exists():exact.extend(p for p in (BASE/version).rglob('*') if p.is_file() or p.is_symlink())
    return sorted(set(exact),key=str)


def lifecycle_units(version):
    units={'wpiso-manager-'+version+'.service','wpiso-health-'+version+'.service','php-fpm'+version[3:]+'.service'}
    for p in lifecycle_files(version):
        if p.parent==UNITS and p.suffix in ['.service','.socket']:units.add(p.name)
    return sorted(units)


def snapshot_file(path):
    if path.is_symlink():return {'kind':'symlink','target':os.readlink(path)}
    if not path.exists():return {'kind':'absent'}
    if not path.is_file():raise RuntimeError('Unexpected lifecycle file type: '+str(path))
    return {'kind':'file','data':base64.b64encode(path.read_bytes()).decode(),'mode':path.stat().st_mode&0o777}


def restore_file(path,record):
    if path.is_symlink():path.unlink()
    if record['kind']=='absent':path.unlink(missing_ok=True)
    elif record['kind']=='symlink':
        path.unlink(missing_ok=True);path.parent.mkdir(parents=True,exist_ok=True);path.symlink_to(record['target'])
    else:
        # Lifecycle control files are UTF-8 text. Existing atomic writer rejects unsafe staging/symlink paths.
        atomic(path,base64.b64decode(record['data']).decode('utf-8'),record['mode'])


def journal_write(path,data):
    atomic(path,json.dumps(data))
    with open(path,'r+b') as stream:os.fsync(stream.fileno())
    if os.name!='nt':
        fd=os.open(str(pathlib.Path(path).parent),os.O_RDONLY|os.O_DIRECTORY)
        try:os.fsync(fd)
        finally:os.close(fd)


def restore_lifecycle(journal):
    version=journal['version']
    # Stop new routing before restoring its registration/files. Do not stop a native
    # service after its original launcher has been restored.
    for unit in lifecycle_units(version):
        stopped=execute(['systemctl','stop',unit],False,timeout=90)
        if stopped.returncode not in [0,4,5]:raise RuntimeError('Cannot stop routing for rollback: '+unit)
    for p in lifecycle_files(version):
        if str(p) not in journal['files']:p.unlink(missing_ok=True)
    for name,record in journal['files'].items():restore_file(pathlib.Path(name),record)
    execute(['systemctl','daemon-reload'])
    for unit in lifecycle_units(version):execute(['systemctl','reset-failed',unit],False)
    for unit,state in journal['units'].items():
        if state['enabled']=='enabled':execute(['systemctl','enable',unit])
        elif state['enabled']=='disabled':execute(['systemctl','disable',unit])
    for unit,state in journal['units'].items():
        if state['active']:execute(['systemctl','start',unit],timeout=90)
    journal['status']='rolled-back';journal['restoredAt']=time.time()


def prepare_version_budget(version,operation):
    data=json.loads((STATE/'installed.json').read_text())
    current=policy()
    base=data.setdefault('versionBudgetBase',{'count':len(data['versions']),'phpBudgetMiB':current['phpBudgetMiB']})
    target=len(data['versions'])+(1 if operation=='onboard' and version not in data['versions'] else 0)
    # Match the generator's per-version 16-MiB bookkeeping + 16-MiB
    # private health-master estimate. Pool OPcache remains charged per lease.
    previous=base.get('appliedBudgetMiB',base['phpBudgetMiB'])
    if current['phpBudgetMiB']!=previous:raise RuntimeError('Reviewed PHP budget changed externally; regenerate version budget accounting before lifecycle changes')
    budget=base['phpBudgetMiB']-max(0,target-base['count'])*32
    if budget<current['workerRssMiB']+48+current['opcacheMiB']+32:
        raise RuntimeError('Additional PHP version cannot fit the reviewed physical budget')
    if budget!=current['phpBudgetMiB']:
        with lock('admission'):
            reserved=0
            for lease in (RUN/'slots').glob('*.service'):
                reserved+=int(json.loads(lease.read_text())['costMiB'])
            if reserved>budget:raise RuntimeError('Wait for PHP leases to quiesce before adding version overhead')
            current['phpBudgetMiB']=budget
            atomic(BASE/'policy.json',json.dumps(current,indent=2))
    base['appliedBudgetMiB']=budget
    atomic(STATE/'installed.json',json.dumps(data,indent=2))


def lifecycle_transaction(version,operation):
    if not re.fullmatch(r'php\d{2,3}',version):raise ValueError('Invalid PHP version')
    # Serialize registration read/modify/write across different PHP versions too.
    with lock('php-lifecycle'):
        pending=STATE/'lifecycle-pending.json'
        if pending.exists():
            previous=json.loads(pending.read_text())
            if previous['status']=='pending':
                restore_lifecycle(previous)
                atomic(STATE/('lifecycle-recovered-'+str(time.time_ns())+'.json'),json.dumps(previous))
            pending.unlink()
        ctl=paths(version)/'bin/fpmctl'
        if ctl.is_symlink() or (STATE/'original-launchers'/version).is_symlink():raise RuntimeError('Refusing launcher/backup symlink: '+version)
        # Validate pools on both first onboarding and managed repair, before stopping anything.
        config=paths(version)/'etc/php-fpm.conf'
        if not config.is_file():raise RuntimeError('Native PHP config missing: '+version)
        parse_pools(config.read_text(),version,False)
        if operation=='retire':
            if not is_managed(version):return _retire(version)
            if parse_pools(config.read_text(),version,False) or manifest(version).get('pools'):
                raise RuntimeError('Cannot retire '+version+': customer pools remain.')
            assert_launcher(version)
            if not (STATE/'original-launchers'/version).is_file():raise RuntimeError('Native restoration backup missing')
        elif not is_managed(version):
            native=UNITS/('php-fpm'+version[3:]+'.service')
            if native.exists() or native.is_symlink():raise RuntimeError('Existing custom PHP unit requires manual review: '+version)
        if not (STATE/'installed.json').is_file():raise RuntimeError('Install the reviewed protection stack before PHP lifecycle operations')
        journal={'version':version,'operation':operation,'status':'pending','startedAt':time.time(),
                 'files':{str(p):snapshot_file(p) for p in lifecycle_files(version)},'units':{}}
        for unit in lifecycle_units(version):
            journal['units'][unit]={'active':execute(['systemctl','is-active',unit],False).returncode==0,
                'enabled':execute(['systemctl','is-enabled',unit],False).stdout.strip()}
        journal_write(pending,journal)
        try:
            prepare_version_budget(version,operation)
            (_onboard if operation=='onboard' else _retire)(version)
            if operation=='retire':prepare_version_budget(version,'retired')
            journal['status']='committed';journal['finishedAt']=time.time()
            journal_write(pending,journal)
        except BaseException as exc:
            try:restore_lifecycle(journal)
            except Exception as recovery:
                raise RuntimeError('Lifecycle failed; recovery is incomplete. Journal retained at '+str(pending)+': '+str(recovery)) from exc
            atomic(STATE/('lifecycle-rollback-'+str(time.time_ns())+'.json'),json.dumps(journal))
            pending.unlink(missing_ok=True)
            raise
        atomic(STATE/('lifecycle-'+str(time.time_ns())+'.json'),json.dumps(journal))
        pending.unlink()

```

Illustrative after-edit context:
```
def is_managed(version):
    if not (STATE/'installed.json').exists(): return False
    data = json.loads((STATE/'installed.json').read_text())
    versions = data.get('versions')
    if not isinstance(versions,list) or any(not isinstance(v,str) or not re.fullmatch(r'php\d{2,3}',v) for v in versions):
        raise ValueError('Invalid managed PHP registry')
    return version in versions


def lifecycle_files(version):
    """Only this version's owned control files; never snapshot customer content."""
    exact=[paths(version)/'bin/fpmctl',STATE/'original-launchers'/version,STATE/'installed.json',
           STATE/(version+'.json'),BASE/'policy.json']
    prefixes=['wpiso-manager-'+version,'wpiso-health-'+version,'wpiso-fpm-'+version+'-',
              'wpiso-proxy-'+version+'-']
    for directory in [UNITS,UNITS/'multi-user.target.wants',UNITS/'sockets.target.wants']:
        if directory.exists():
            exact.extend(p for p in directory.iterdir() if p.name.startswith(tuple(prefixes)) or p.name=='php-fpm'+version[3:]+'.service')
    exact.extend(UNITS/n for n in ['wpiso-manager-'+version+'.service','wpiso-health-'+version+'.service','php-fpm'+version[3:]+'.service'])
    if BASE.exists():
        exact.extend(p for p in BASE.glob(version+'-*') if p.is_file())
    if (BASE/version).exists():exact.extend(p for p in (BASE/version).rglob('*') if p.is_file() or p.is_symlink())
    return sorted(set(exact),key=str)


def lifecycle_units(version):
    units={'wpiso-manager-'+version+'.service','wpiso-health-'+version+'.service','php-fpm'+version[3:]+'.service'}
    for p in lifecycle_files(version):
        if p.parent==UNITS and p.suffix in ['.service','.socket']:units.add(p.name)
    return sorted(units)


def snapshot_file(path):
    if path.is_symlink():return {'kind':'symlink','target':os.readlink(path)}
    if not path.exists():return {'kind':'absent'}
    if not path.is_file():raise RuntimeError('Unexpected lifecycle file type: '+str(path))
    return {'kind':'file','data':base64.b64encode(path.read_bytes()).decode(),'mode':path.stat().st_mode&0o777}


def restore_file(path,record):
    if path.is_symlink():path.unlink()
    if record['kind']=='absent':path.unlink(missing_ok=True)
    elif record['kind']=='symlink':
        path.unlink(missing_ok=True);path.parent.mkdir(parents=True,exist_ok=True);path.symlink_to(record['target'])
    else:
        # Lifecycle control files are UTF-8 text. Existing atomic writer rejects unsafe staging/symlink paths.
        atomic(path,base64.b64decode(record['data']).decode('utf-8'),record['mode'])


def journal_write(path,data):
    atomic(path,json.dumps(data))
    with open(path,'r+b') as stream:os.fsync(stream.fileno())
    if os.name!='nt':
        fd=os.open(str(pathlib.Path(path).parent),os.O_RDONLY|os.O_DIRECTORY)
        try:os.fsync(fd)
        finally:os.close(fd)


def restore_lifecycle(journal):
    version=journal['version']
    # Stop new routing before restoring its registration/files. Do not stop a native
    # service after its original launcher has been restored.
    for unit in lifecycle_units(version):
        stopped=execute(['systemctl','stop',unit],False,timeout=90)
        if stopped.returncode not in [0,4,5]:raise RuntimeError('Cannot stop routing for rollback: '+unit)
    for p in lifecycle_files(version):
        if str(p) not in journal['files']:p.unlink(missing_ok=True)
    for name,record in journal['files'].items():restore_file(pathlib.Path(name),record)
    execute(['systemctl','daemon-reload'])
    for unit in lifecycle_units(version):execute(['systemctl','reset-failed',unit],False)
    for unit,state in journal['units'].items():
        if state['enabled']=='enabled':execute(['systemctl','enable',unit])
        elif state['enabled']=='disabled':execute(['systemctl','disable',unit])
    for unit,state in journal['units'].items():
        if state['active']:execute(['systemctl','start',unit],timeout=90)
    journal['status']='rolled-back';journal['restoredAt']=time.time()


def prepare_version_budget(version,operation):
    data=json.loads((STATE/'installed.json').read_text())
    current=policy()
    base=data.setdefault('versionBudgetBase',{'count':len(data['versions']),'phpBudgetMiB':current['phpBudgetMiB']})
    target=len(data['versions'])+(1 if operation=='onboard' and version not in data['versions'] else 0)
    # Match the generator's per-version 16-MiB bookkeeping + 16-MiB
    # private health-master estimate. Pool OPcache remains charged per lease.
    previous=base.get('appliedBudgetMiB',base['phpBudgetMiB'])
    if current['phpBudgetMiB']!=previous:raise RuntimeError('Reviewed PHP budget changed externally; regenerate version budget accounting before lifecycle changes')
    budget=base['phpBudgetMiB']-max(0,target-base['count'])*32
    if budget<current['workerRssMiB']+48+current['opcacheMiB']+32:
        raise RuntimeError('Additional PHP version cannot fit the reviewed physical budget')
    if budget!=current['phpBudgetMiB']:
        with lock('admission'):
            reserved=0
            for lease in (RUN/'slots').glob('*.service'):
                reserved+=int(json.loads(lease.read_text())['costMiB'])
            if reserved>budget:raise RuntimeError('Wait for PHP leases to quiesce before adding version overhead')
            current['phpBudgetMiB']=budget
            atomic(BASE/'policy.json',json.dumps(current,indent=2))
    base['appliedBudgetMiB']=budget
    atomic(STATE/'installed.json',json.dumps(data,indent=2))


def lifecycle_transaction(version,operation):
    if not re.fullmatch(r'php\d{2,3}',version):raise ValueError('Invalid PHP version')
    # Serialize registration read/modify/write across different PHP versions too.
    with lock('php-lifecycle'):
        pending=STATE/'lifecycle-pending.json'
        if pending.exists():
            previous=json.loads(pending.read_text())
            if previous['status']=='pending':
                restore_lifecycle(previous)
                atomic(STATE/('lifecycle-recovered-'+str(time.time_ns())+'.json'),json.dumps(previous))
            pending.unlink()
        ctl=paths(version)/'bin/fpmctl'
        if ctl.is_symlink() or (STATE/'original-launchers'/version).is_symlink():raise RuntimeError('Refusing launcher/backup symlink: '+version)
        # Validate pools on both first onboarding and managed repair, before stopping anything.
        config=paths(version)/'etc/php-fpm.conf'
        if not config.is_file():raise RuntimeError('Native PHP config missing: '+version)
        parse_pools(config.read_text(),version,False)
        if operation=='retire':
            if not is_managed(version):return _retire(version)
            if parse_pools(config.read_text(),version,False) or manifest(version).get('pools'):
                raise RuntimeError('Cannot retire '+version+': customer pools remain.')
            assert_launcher(version)
            if not (STATE/'original-launchers'/version).is_file():raise RuntimeError('Native restoration backup missing')
        elif not is_managed(version):
            native=UNITS/('php-fpm'+version[3:]+'.service')
            if native.exists() or native.is_symlink():raise RuntimeError('Existing custom PHP unit requires manual review: '+version)
        if not (STATE/'installed.json').is_file():raise RuntimeError('Install the reviewed protection stack before PHP lifecycle operations')
        journal={'version':version,'operation':operation,'status':'pending','startedAt':time.time(),
                 'files':{str(p):snapshot_file(p) for p in lifecycle_files(version)},'units':{}}
        for unit in lifecycle_units(version):
            journal['units'][unit]={'active':execute(['systemctl','is-active',unit],False).returncode==0,
                'enabled':execute(['systemctl','is-enabled',unit],False).stdout.strip()}
        journal_write(pending,journal)
        try:
            prepare_version_budget(version,operation)
            (_onboard if operation=='onboard' else _retire)(version)
            if operation=='retire':prepare_version_budget(version,'retired')
            journal['status']='committed';journal['finishedAt']=time.time()
            journal_write(pending,journal)
        except BaseException as exc:
            try:restore_lifecycle(journal)
            except Exception as recovery:
                raise RuntimeError('Lifecycle failed; recovery is incomplete. Journal retained at '+str(pending)+': '+str(recovery)) from exc
            atomic(STATE/('lifecycle-rollback-'+str(time.time_ns())+'.json'),json.dumps(journal))
            pending.unlink(missing_ok=True)
            raise
        atomic(STATE/('lifecycle-'+str(time.time_ns())+'.json'),json.dumps(journal))
        pending.unlink()


def onboard(version):
```

AFTER: `def onboard(version):`

BEFORE: `    if not re.fullmatch(r'php\d{2,3}', version): raise ValueError('Invalid PHP version: ' + str(version))`

Existing code:
```

```

Generated replacement/insertion:
```
    return lifecycle_transaction(version,'onboard')


def retire(version):
    return lifecycle_transaction(version,'retire')


def _onboard(version):
```

Illustrative after-edit context:
```

def onboard(version):
    return lifecycle_transaction(version,'onboard')


def retire(version):
    return lifecycle_transaction(version,'retire')


def _onboard(version):
    if not re.fullmatch(r'php\d{2,3}', version): raise ValueError('Invalid PHP version: ' + str(version))
    p = paths(version)
```

AFTER: `            shutil.copy2(ctl, archive/version)`

BEFORE: `            execute([str(ctl), 'stop'], False, timeout=45)`

Existing code:
```
            if not (backups/version).exists():
                shutil.copy2(ctl, backups/version)
```

Generated replacement/insertion:
```
            shutil.copy2(ctl, backups/version) # Rebase restoration onto the current vendor launcher; transaction archives the prior baseline.
```

Illustrative after-edit context:
```
            archive.mkdir(mode=0o700, exist_ok=True)
            shutil.copy2(ctl, archive/version)
            shutil.copy2(ctl, backups/version) # Rebase restoration onto the current vendor launcher; transaction archives the prior baseline.
            execute([str(ctl), 'stop'], False, timeout=45)
            deadline = time.monotonic() + 15
```

AFTER: `                if not remaining: break`

BEFORE: `                time.sleep(.1)`

Existing code:
```
                if time.monotonic() > deadline:
                    for pid in remaining:
                        try: os.kill(int(pid), signal.SIGKILL)
                        except OSError: pass
                    break
```

Generated replacement/insertion:
```
                if time.monotonic() > deadline: raise RuntimeError('Native master did not stop gracefully; no forced kill: '+version)
```

Illustrative after-edit context:
```
                    except (FileNotFoundError, ProcessLookupError, PermissionError): pass
                if not remaining: break
                if time.monotonic() > deadline: raise RuntimeError('Native master did not stop gracefully; no forced kill: '+version)
                time.sleep(.1)
            atomic(ctl, wrapper(version), 0o755)
```

AFTER: `    # Parse pools to validate configuration`

BEFORE: `    backups = STATE/'original-launchers'`

Existing code:
```
    parse_pools((p/'etc/php-fpm.conf').read_text(), version)
```

Generated replacement/insertion:
```
    parse_pools((p/'etc/php-fpm.conf').read_text(), version,False)
```

Illustrative after-edit context:
```
        return
    # Parse pools to validate configuration
    parse_pools((p/'etc/php-fpm.conf').read_text(), version,False)
    backups = STATE/'original-launchers'
    backups.mkdir(mode=0o700, exist_ok=True)
```

AFTER: `    ctl_text = ctl.read_text()`

BEFORE: `    if MARKER not in ctl_text:`

Existing code:
```

```

Generated replacement/insertion:
```
    if MARKER in ctl_text: raise RuntimeError('Unregistered managed launcher; recover the lifecycle journal before onboarding: '+version)
```

Illustrative after-edit context:
```
    if ctl.is_symlink(): raise RuntimeError('Unexpected launcher symlink ' + version)
    ctl_text = ctl.read_text()
    if MARKER in ctl_text: raise RuntimeError('Unregistered managed launcher; recover the lifecycle journal before onboarding: '+version)
    if MARKER not in ctl_text:
        shutil.copy2(ctl, archive/version)
```

AFTER: `        shutil.copy2(ctl, archive/version)`

BEFORE: `        execute([str(ctl), 'stop'], False, timeout=45)`

Existing code:
```
        if not (backups/version).exists():
            shutil.copy2(ctl, backups/version)
```

Generated replacement/insertion:
```
        shutil.copy2(ctl, backups/version) # Current native baseline; historical snapshot is retained by transaction.
```

Illustrative after-edit context:
```
    if MARKER not in ctl_text:
        shutil.copy2(ctl, archive/version)
        shutil.copy2(ctl, backups/version) # Current native baseline; historical snapshot is retained by transaction.
        execute([str(ctl), 'stop'], False, timeout=45)
        deadline = time.monotonic() + 15
```

AFTER: `        print('Successfully onboarded ' + version + ' with ' + str(count) + ' isolated pools.')`

BEFORE: ``

Existing code:
```
    except Exception as exc:
        if version in data['versions']:
            data['versions'].remove(version)
            atomic(STATE/'installed.json', json.dumps(data, indent=2))
        execute(['systemctl', 'disable', '--now', 'wpiso-manager-' + version + '.service'], False)
        execute(['systemctl', 'stop', 'php-fpm' + version[3:] + '.service'], False)
        execute(['systemctl', 'stop', 'wpiso-health-' + version + '.service'], False)
        raise RuntimeError('Failed to initialize managed services for ' + version + ': ' + str(exc))
```

Generated replacement/insertion:
```
    except Exception:
        raise # Durable outer transaction restores registration, files and prior service states.
```

Illustrative after-edit context:
```
        count = reconcile(version, True)
        print('Successfully onboarded ' + version + ' with ' + str(count) + ' isolated pools.')
    except Exception:
        raise # Durable outer transaction restores registration, files and prior service states.


```

AFTER: ``

BEFORE: `    if not re.fullmatch(r'php\d{2,3}', version): raise ValueError('Invalid PHP version: ' + str(version))`

Existing code:
```
def retire(version):
```

Generated replacement/insertion:
```

def _retire(version):
```

Illustrative after-edit context:
```
        raise # Durable outer transaction restores registration, files and prior service states.


def _retire(version):
    if not re.fullmatch(r'php\d{2,3}', version): raise ValueError('Invalid PHP version: ' + str(version))
    if not is_managed(version):
```

AFTER: `    if (p/'etc/php-fpm.conf').is_file():`

BEFORE: `    unit = 'php-fpm' + version[3:] + '.service'`

Existing code:
```
        try:
            pools = parse_pools((p/'etc/php-fpm.conf').read_text(), version)
            if pools:
                active_users = [r['user'] for r in pools]
                raise RuntimeError('Cannot retire ' + version + ': active customer pools exist: ' + str(active_users) + '. Reassign domains in Webuzo before retiring.')
        except Exception as e:
            if 'Cannot retire' in str(e): raise
    execute(['systemctl', 'disable', '--now', 'wpiso-manager-' + version + '.service'], False, timeout=90)
```

Generated replacement/insertion:
```
        pools = parse_pools((p/'etc/php-fpm.conf').read_text(), version,False)
        if pools or manifest(version).get('pools'):
            raise RuntimeError('Cannot retire '+version+': customer pools remain; reassign domains and reconcile first.')
    else:
        raise RuntimeError('Cannot validate retirement: native PHP configuration is missing for '+version)
    ctl = p/'bin/fpmctl'
    if ctl.is_symlink() or not ctl.is_file() or ctl.read_text()!=wrapper(version):
        raise RuntimeError('Cannot retire changed native launcher; review vendor regeneration first: '+version)
    if not (STATE/'original-launchers'/version).is_file():
        raise RuntimeError('Cannot retire without an approved native launcher backup: '+version)
    execute(['systemctl', 'disable', '--now', 'wpiso-manager-' + version + '.service'], timeout=90)
```

Illustrative after-edit context:
```
    p = paths(version)
    if (p/'etc/php-fpm.conf').is_file():
        pools = parse_pools((p/'etc/php-fpm.conf').read_text(), version,False)
        if pools or manifest(version).get('pools'):
            raise RuntimeError('Cannot retire '+version+': customer pools remain; reassign domains and reconcile first.')
    else:
        raise RuntimeError('Cannot validate retirement: native PHP configuration is missing for '+version)
    ctl = p/'bin/fpmctl'
    if ctl.is_symlink() or not ctl.is_file() or ctl.read_text()!=wrapper(version):
        raise RuntimeError('Cannot retire changed native launcher; review vendor regeneration first: '+version)
    if not (STATE/'original-launchers'/version).is_file():
        raise RuntimeError('Cannot retire without an approved native launcher backup: '+version)
    execute(['systemctl', 'disable', '--now', 'wpiso-manager-' + version + '.service'], timeout=90)
    unit = 'php-fpm' + version[3:] + '.service'
    path = UNITS/unit
```

AFTER: `    if path.exists() and path.read_text() == bridge(version):`

BEFORE: `        wanted = UNITS/'multi-user.target.wants'/unit`

Existing code:
```
        execute(['systemctl', 'stop', unit], False, timeout=90)
```

Generated replacement/insertion:
```
        execute(['systemctl', 'stop', unit], timeout=90)
```

Illustrative after-edit context:
```
    path = UNITS/unit
    if path.exists() and path.read_text() == bridge(version):
        execute(['systemctl', 'stop', unit], timeout=90)
        wanted = UNITS/'multi-user.target.wants'/unit
        if wanted.is_symlink() and wanted.resolve() == path: wanted.unlink()
```

AFTER: `        path.unlink()`

BEFORE: `    (UNITS/('wpiso-health-' + version + '.service')).unlink(missing_ok=True)`

Existing code:
```
    execute(['systemctl', 'stop', 'wpiso-health-' + version + '.service'], False)
```

Generated replacement/insertion:
```
    execute(['systemctl', 'stop', 'wpiso-health-' + version + '.service'])
```

Illustrative after-edit context:
```
        if wanted.is_symlink() and wanted.resolve() == path: wanted.unlink()
        path.unlink()
    execute(['systemctl', 'stop', 'wpiso-health-' + version + '.service'])
    (UNITS/('wpiso-health-' + version + '.service')).unlink(missing_ok=True)
    (UNITS/('wpiso-manager-' + version + '.service')).unlink(missing_ok=True)
```

AFTER: `    execute(['systemctl', 'daemon-reload'])`

BEFORE: `    print('Successfully retired ' + version + ' from isolation.')`

Existing code:
```

```

Generated replacement/insertion:
```
    (BASE/(version+'-health.conf')).unlink(missing_ok=True)
    for unit in lifecycle_units(version):execute(['systemctl','reset-failed',unit],False)
```

Illustrative after-edit context:
```
    atomic(STATE/'installed.json', json.dumps(data, indent=2))
    execute(['systemctl', 'daemon-reload'])
    (BASE/(version+'-health.conf')).unlink(missing_ok=True)
    for unit in lifecycle_units(version):execute(['systemctl','reset-failed',unit],False)
    print('Successfully retired ' + version + ' from isolation.')

```

## /usr/local/uniselv-resman/agent/ipc_server.py

Replace the complete installed file with reviewed release content. Do not append duplicate functions.

AFTER: `        inst_file = pathlib.Path('/var/lib/webuzo-isolation/installed.json')`

BEFORE: ``

Existing code:
```
        if inst_file.exists():
            try:
                data = json.loads(inst_file.read_text(encoding='utf-8'))
                versions = data.get('versions', [])
                if versions and isinstance(versions, list):
                    return sorted(versions)
            except Exception:
                pass
        return self.get_installed_phps()
```

Generated replacement/insertion:
```
        if not inst_file.exists():
            return []
        data = json.loads(inst_file.read_text(encoding='utf-8'))
        versions = data.get('versions')
        if not isinstance(versions, list) or any(not isinstance(v,str) or not re.fullmatch(r'php\d{2,3}',v) for v in versions):
            raise ValueError('Invalid managed PHP registry; refusing physical-version fallback')
        return sorted(set(versions))
```

Illustrative after-edit context:
```
    def get_managed_phps(self) -> List[str]:
        inst_file = pathlib.Path('/var/lib/webuzo-isolation/installed.json')
        if not inst_file.exists():
            return []
        data = json.loads(inst_file.read_text(encoding='utf-8'))
        versions = data.get('versions')
        if not isinstance(versions, list) or any(not isinstance(v,str) or not re.fullmatch(r'php\d{2,3}',v) for v in versions):
            raise ValueError('Invalid managed PHP registry; refusing physical-version fallback')
        return sorted(set(versions))

    def is_reseller_actor(self, auth: Dict[str, Any], params: Dict[str, Any]) -> tuple:
```

AFTER: ``

BEFORE: `        for ver in self.get_managed_phps():`

Existing code:
```
        # Reconcile isolation on managed PHP versions
```

Generated replacement/insertion:
```
        # Report runtime failures instead of returning a false plan-sync success.
        runtime_errors = []
```

Illustrative after-edit context:
```
        subprocess.run(['systemctl', 'daemon-reload'], check=False)

        # Report runtime failures instead of returning a false plan-sync success.
        runtime_errors = []
        for ver in self.get_managed_phps():
            try:
```

AFTER: `            try:`

BEFORE: ``

Existing code:
```
                subprocess.run(['python3', '/usr/local/sbin/webuzo-isolation.py', 'action', ver, 'reload'], capture_output=True, timeout=30)
            except Exception:
                pass
```

Generated replacement/insertion:
```
                result = subprocess.run(['python3', '/usr/local/sbin/webuzo-isolation.py', 'action', ver, 'reload'], capture_output=True, text=True, timeout=90)
                if result.returncode:
                    runtime_errors.append({'version':ver,'error':result.stderr or result.stdout or 'Runtime reload failed'})
            except Exception as exc:
                runtime_errors.append({'version':ver,'error':str(exc)})
```

Illustrative after-edit context:
```
        for ver in self.get_managed_phps():
            try:
                result = subprocess.run(['python3', '/usr/local/sbin/webuzo-isolation.py', 'action', ver, 'reload'], capture_output=True, text=True, timeout=90)
                if result.returncode:
                    runtime_errors.append({'version':ver,'error':result.stderr or result.stdout or 'Runtime reload failed'})
            except Exception as exc:
                runtime_errors.append({'version':ver,'error':str(exc)})

        conn = self.get_db()
```

AFTER: `        return {`

BEFORE: `            'synced_count': len(synced_accounts),`

Existing code:
```
            'success': (len(failed_accounts) == 0),
```

Generated replacement/insertion:
```
            'success': (len(failed_accounts) == 0 and not runtime_errors),
            'runtime_errors': runtime_errors,
```

Illustrative after-edit context:
```

        return {
            'success': (len(failed_accounts) == 0 and not runtime_errors),
            'runtime_errors': runtime_errors,
            'synced_count': len(synced_accounts),
            'failed_count': len(failed_accounts),
```

## /usr/local/webuzo/plugins/uniselv-resman/assets/app.js

Replace the complete installed file with reviewed release content. Do not append duplicate functions.

AFTER: `            } else if (resolved === 'health') {`

BEFORE: `                this.loadFeatureSettings();`

Existing code:
```

```

Generated replacement/insertion:
```
                this.loadPhpLifecycle();
```

Illustrative after-edit context:
```
                this.loadAdminOverview();
            } else if (resolved === 'health') {
                this.loadPhpLifecycle();
                this.loadFeatureSettings();
                this.loadStorageSettings();
```

AFTER: `        });`

BEFORE: `    },`

Existing code:
```

```

Generated replacement/insertion:
```
    },

    loadPhpLifecycle: function() {
        const host = document.getElementById('uniselv-php-lifecycle');
        if (!this.isAdmin || !host) return;
        host.textContent = 'Loading PHP runtime status...';
        this.callApi('php_lifecycle', {}, (err, res) => {
            const versions = res?.versions || res?.data?.versions;
            if (err || !versions) { host.textContent = 'PHP runtime status unavailable. Check agent health and retry.'; return; }
            const table = document.createElement('table'); table.className = 'uniselv-table';
            const head = table.createTHead().insertRow();
            ['PHP version','Installed','Registered','Coordinator','Health master','Pools'].forEach(label => {
                const th = document.createElement('th'); th.scope = 'col'; th.textContent = label; head.append(th);
            });
            const body = table.createTBody();
            Object.entries(versions).forEach(([version, state]) => {
                const row = body.insertRow();
                [version,state.installed?'Yes':'Missing',state.managed?'Yes':'No',state.coordinator_active?'Active':'Stopped',state.health_master_active?'Active':'Stopped',String(state.pool_count)].forEach(value => { row.insertCell().textContent = value; });
            });
            host.replaceChildren(table);
            if (!Object.keys(versions).length) host.textContent = 'No PHP runtime registrations found.';
        }, {timeoutMs:20000});
```

Illustrative after-edit context:
```
            }
        });
    },

    loadPhpLifecycle: function() {
        const host = document.getElementById('uniselv-php-lifecycle');
        if (!this.isAdmin || !host) return;
        host.textContent = 'Loading PHP runtime status...';
        this.callApi('php_lifecycle', {}, (err, res) => {
            const versions = res?.versions || res?.data?.versions;
            if (err || !versions) { host.textContent = 'PHP runtime status unavailable. Check agent health and retry.'; return; }
            const table = document.createElement('table'); table.className = 'uniselv-table';
            const head = table.createTHead().insertRow();
            ['PHP version','Installed','Registered','Coordinator','Health master','Pools'].forEach(label => {
                const th = document.createElement('th'); th.scope = 'col'; th.textContent = label; head.append(th);
            });
            const body = table.createTBody();
            Object.entries(versions).forEach(([version, state]) => {
                const row = body.insertRow();
                [version,state.installed?'Yes':'Missing',state.managed?'Yes':'No',state.coordinator_active?'Active':'Stopped',state.health_master_active?'Active':'Stopped',String(state.pool_count)].forEach(value => { row.insertCell().textContent = value; });
            });
            host.replaceChildren(table);
            if (!Object.keys(versions).length) host.textContent = 'No PHP runtime registrations found.';
        }, {timeoutMs:20000});
    },

```

AFTER: `                this.callApi('sync_plans', {}, (err, res) => {`

BEFORE: `                    }`

Existing code:
```
                    if (err || res.error) {
                        UniselvNotify.error(`Sync failed: ${err || res.error}`);
                    } else {
                        UniselvNotify.success(`Successfully synchronized ${res.synced_plans.length} native resource plans.`);
                        setTimeout(() => location.reload(), 1200);
```

Generated replacement/insertion:
```
                    const runtimeErrors = res?.runtime_errors || [];
                    if (err || !res || res.error || res.success === false || runtimeErrors.length || Number(res.failed_count || 0) > 0) {
                        const reason = err || res?.error || (runtimeErrors.length ? 'PHP runtime reload failed: ' + runtimeErrors.map(x => x.version).join(', ') : 'Some accounts could not be synchronized.');
                        UniselvNotify.error(`Sync failed: ${reason}`);
                        return;
```

Illustrative after-edit context:
```
            onConfirm: () => {
                this.callApi('sync_plans', {}, (err, res) => {
                    const runtimeErrors = res?.runtime_errors || [];
                    if (err || !res || res.error || res.success === false || runtimeErrors.length || Number(res.failed_count || 0) > 0) {
                        const reason = err || res?.error || (runtimeErrors.length ? 'PHP runtime reload failed: ' + runtimeErrors.map(x => x.version).join(', ') : 'Some accounts could not be synchronized.');
                        UniselvNotify.error(`Sync failed: ${reason}`);
                        return;
                    }
                    const accounts = Number.isFinite(res.synced_count) ? res.synced_count : null;
```

AFTER: `                    }`

BEFORE: `                });`

Existing code:
```

```

Generated replacement/insertion:
```
                    const accounts = Number.isFinite(res.synced_count) ? res.synced_count : null;
                    const plans = Array.isArray(res.synced_plans) ? res.synced_plans.length : null;
                    if (accounts === null && plans === null) { UniselvNotify.error('Sync result could not be verified. Check the audit log.'); return; }
                    UniselvNotify.success(`Successfully synchronized ${accounts ?? plans} ${accounts !== null ? 'accounts' : 'resource plans'}.`);
                    setTimeout(() => location.reload(), 1200);
```

Illustrative after-edit context:
```
                        return;
                    }
                    const accounts = Number.isFinite(res.synced_count) ? res.synced_count : null;
                    const plans = Array.isArray(res.synced_plans) ? res.synced_plans.length : null;
                    if (accounts === null && plans === null) { UniselvNotify.error('Sync result could not be verified. Check the audit log.'); return; }
                    UniselvNotify.success(`Successfully synchronized ${accounts ?? plans} ${accounts !== null ? 'accounts' : 'resource plans'}.`);
                    setTimeout(() => location.reload(), 1200);
                });
            }
```

## /usr/local/webuzo/plugins/uniselv-resman/uniselv-resman.php

Replace the complete installed file with reviewed release content. Do not append duplicate functions.

AFTER: `Plugin Name: UNISELV Resource Manager`

BEFORE: `Description: Enterprise Resource Management, Cgroups v2 Isolation, Real-Time Monitoring & Telemetry for Webuzo.`

Existing code:
```
Version: 1.1.22
```

Generated replacement/insertion:
```
Version: 1.1.23
```

Illustrative after-edit context:
```
/*
Plugin Name: UNISELV Resource Manager
Version: 1.1.23
Description: Enterprise Resource Management, Cgroups v2 Isolation, Real-Time Monitoring & Telemetry for Webuzo.
Author: Refat Rahman
```

AFTER: ``

BEFORE: `    echo '<style>:root { --uniselv-primary: ' . $brand_color . '; --primary-color: ' . $brand_color . '; }</style>';`

Existing code:
```
    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '-1.1.22r4' . '">';
```

Generated replacement/insertion:
```
    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '-1.1.23r2' . '">';
```

Illustrative after-edit context:
```
    $i18n_dict = uniselv_get_i18n_dict();

    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '-1.1.23r2' . '">';
    echo '<style>:root { --uniselv-primary: ' . $brand_color . '; --primary-color: ' . $brand_color . '; }</style>';
    echo '<script>
```

AFTER: `</script>';`

BEFORE: ``

Existing code:
```
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '-1.1.22r4' . '"></script>';
```

Generated replacement/insertion:
```
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '-1.1.23r2' . '"></script>';
```

Illustrative after-edit context:
```
window.UNISELV_TRANSLATIONS = ' . json_encode($i18n_dict[$locale] ?? $i18n_dict['en']) . ';
</script>';
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '-1.1.23r2' . '"></script>';

    echo '<div class="uniselv-container">';
```

AFTER: `                        <span class="uniselv-metric-big" id="admin-card-hw-cpu">' . $cpu_cores . ' vCPUs</span>`

BEFORE: `                    </div>`

Existing code:
```
                        <span class="uniselv-metric-core">Physical Cores</span>
```

Generated replacement/insertion:
```
                        <span class="uniselv-metric-core">Virtual CPUs</span>
```

Illustrative after-edit context:
```
                    <div class="uniselv-gauge-center">
                        <span class="uniselv-metric-big" id="admin-card-hw-cpu">' . $cpu_cores . ' vCPUs</span>
                        <span class="uniselv-metric-core">Virtual CPUs</span>
                    </div>
                </div>
```

AFTER: `    echo '<div id="tab-health" class="uniselv-tab-content">`

BEFORE: `        <!-- Card 1: Feature Controls & Self-Service Governance -->`

Existing code:
```

```

Generated replacement/insertion:
```
        <div class="uniselv-card mb-4">
            <div style="display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;align-items:center">
                <h5>PHP Runtime Registration</h5>
                <button class="uniselv-btn btn-outline" onclick="UniselvResMan.loadPhpLifecycle()">Refresh PHP Status</button>
            </div>
            <p>Global PHP settings are inherited. Installed versions must also be registered with the managed runtime. Stopped services need review before assigning a site.</p>
            <div id="uniselv-php-lifecycle" class="uniselv-table-wrap" role="status" aria-live="polite">Open this section to load PHP status.</div>
        </div>
```

Illustrative after-edit context:
```
    // TAB 5: HEALTH, FEATURE GOVERNANCE & RETENTION SETTINGS
    echo '<div id="tab-health" class="uniselv-tab-content">
        <div class="uniselv-card mb-4">
            <div style="display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;align-items:center">
                <h5>PHP Runtime Registration</h5>
                <button class="uniselv-btn btn-outline" onclick="UniselvResMan.loadPhpLifecycle()">Refresh PHP Status</button>
            </div>
            <p>Global PHP settings are inherited. Installed versions must also be registered with the managed runtime. Stopped services need review before assigning a site.</p>
            <div id="uniselv-php-lifecycle" class="uniselv-table-wrap" role="status" aria-live="polite">Open this section to load PHP status.</div>
        </div>
        <!-- Card 1: Feature Controls & Self-Service Governance -->
        <div class="uniselv-card mb-4">
```

AFTER: ``

BEFORE: `    echo '<style>:root { --uniselv-primary: ' . $brand_color . '; --primary-color: ' . $brand_color . '; }</style>';`

Existing code:
```
    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '-1.1.22r4' . '">';
```

Generated replacement/insertion:
```
    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '-1.1.23r2' . '">';
```

Illustrative after-edit context:
```
    $i18n_dict = uniselv_get_i18n_dict();

    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '-1.1.23r2' . '">';
    echo '<style>:root { --uniselv-primary: ' . $brand_color . '; --primary-color: ' . $brand_color . '; }</style>';
    echo '<script>
```

AFTER: `</script>';`

BEFORE: ``

Existing code:
```
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '-1.1.22r4' . '"></script>';
```

Generated replacement/insertion:
```
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '-1.1.23r2' . '"></script>';
```

Illustrative after-edit context:
```
window.UNISELV_TRANSLATIONS = ' . json_encode($i18n_dict[$locale] ?? $i18n_dict['en']) . ';
</script>';
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '-1.1.23r2' . '"></script>';

    echo '<div class="uniselv-container">';
```

## /usr/local/webuzo/plugins/uniselv-resman/info.json

Replace the complete installed file with reviewed release content. Do not append duplicate functions.

AFTER: `  "slug": "uniselv-resman",`

BEFORE: `  "author": "<a href=\"https://refat.ovh\" target=\"_blank\">Refat Rahman</a>",`

Existing code:
```
  "version": "1.1.22",
```

Generated replacement/insertion:
```
  "version": "1.1.23",
```

Illustrative after-edit context:
```
  "name": "UNISELV Resource Manager",
  "slug": "uniselv-resman",
  "version": "1.1.23",
  "author": "<a href=\"https://refat.ovh\" target=\"_blank\">Refat Rahman</a>",
  "developer": {
```

AFTER: `  "download_link": "https://refat.ovh/plugins/uniselv-resman/uniselv-resman.zip",`

BEFORE: `  "homepage": "https://refat.ovh"`

Existing code:
```
  "last_updated": "2026-10-22",
```

Generated replacement/insertion:
```
  "last_updated": "2026-10-24",
```

Illustrative after-edit context:
```
  "download_url": "https://refat.ovh/plugins/uniselv-resman/",
  "download_link": "https://refat.ovh/plugins/uniselv-resman/uniselv-resman.zip",
  "last_updated": "2026-10-24",
  "homepage": "https://refat.ovh"
}
```

