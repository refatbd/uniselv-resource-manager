# Exact source changes — 1.1.30

Already-applied release source changes relative to 1.1.29; not extra post-install paste steps. Prefer the reviewed complete package.

- Back up existing files and ownership/restoration manifests together.
- Use UTF-8/LF. Replace existing files; do not append duplicate imports, functions or directives. New files start at their first line and end at their final line.
- Install through the reviewed privileged deployment workflow. Restore root ownership and installer execution modes.
- Run Python/PHP/JavaScript syntax, regression, service/API/HTTP and ZIP closure checks. Configuration values and full workload/lifecycle readiness remain distinct.

## uniselv-resman/agent/ipc_server.py

Installed paths: /usr/local/webuzo/plugins/uniselv-resman/agent/ipc_server.py; ALSO /usr/local/uniselv-resman/agent/ipc_server.py

Replace the full file; never append duplicate functions/directives. New files run from first through final line.

### Block 1 — replace

Existing anchor AFTER which:
```text
            # Strict complete synchronization requires all parameters, I/O, and ancestor isolation to match
            is_synchronized = (
```

Existing anchor BEFORE which:
```text
                mem_synced and 
                mem_high_synced and 
```

Existing content to replace/remove (not copied):
```text
                uname not in outside_users and cpu_synced and 
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                uname not in outside_users and cpu_synced and
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
            # Strict complete synchronization requires all parameters, I/O, and ancestor isolation to match
            is_synchronized = (
                uname not in outside_users and cpu_synced and
                mem_synced and 
                mem_high_synced and 
```

## uniselv-resman/agent/runtime_governance.py

Installed paths: /usr/local/webuzo/plugins/uniselv-resman/agent/runtime_governance.py; ALSO /usr/local/uniselv-resman/agent/runtime_governance.py

Replace the full file; never append duplicate functions/directives. New files run from first through final line.

### Block 1 — replace

Existing anchor AFTER which:
```text
                _, mgr = command(['systemctl', 'is-active', 'wpiso-manager-'+version+'.service'])
                _, health = command(['systemctl', 'is-active', 'wpiso-health-'+version+'.service'])
```

Existing anchor BEFORE which:
```text
                if pending['pending']:
                    entry.update(state='blocked', reason='Pending lifecycle recovery requires review.')
```

Existing content to replace/remove (not copied):
```text
                entry.update(coordinator=mgr, healthMaster=health, launcherMatches=launcher_ok)
                needs = binary_changed or version not in managed or not launcher_ok or mgr != 'active' or health != 'active'
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                _, native_bridge = command(['systemctl', 'is-active', 'php-fpm'+version[3:]+'.service'])
                entry.update(coordinator=mgr, healthMaster=health, nativeBridge=native_bridge, launcherMatches=launcher_ok)
                needs = binary_changed or version not in managed or not launcher_ok or mgr != 'active' or health != 'active' or native_bridge != 'active'
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                _, mgr = command(['systemctl', 'is-active', 'wpiso-manager-'+version+'.service'])
                _, health = command(['systemctl', 'is-active', 'wpiso-health-'+version+'.service'])
                _, native_bridge = command(['systemctl', 'is-active', 'php-fpm'+version[3:]+'.service'])
                entry.update(coordinator=mgr, healthMaster=health, nativeBridge=native_bridge, launcherMatches=launcher_ok)
                needs = binary_changed or version not in managed or not launcher_ok or mgr != 'active' or health != 'active' or native_bridge != 'active'
                if pending['pending']:
                    entry.update(state='blocked', reason='Pending lifecycle recovery requires review.')
```

### Block 2 — replace

Existing anchor AFTER which:
```text
                    _, mgr = command(['systemctl', 'is-active', 'wpiso-manager-'+version+'.service'])
                    _, health = command(['systemctl', 'is-active', 'wpiso-health-'+version+'.service'])
```

Existing anchor BEFORE which:
```text
                        raise RuntimeError('Post-operation service verification failed')
                    entry.update(state='healthy', pendingBinaryChange=False, managed=True, coordinator=mgr, healthMaster=health,
```

Existing content to replace/remove (not copied):
```text
                    if version not in registry() or (APPS/version/'bin/fpmctl').read_text() != runtime.wrapper(version) or mgr != 'active' or health != 'active':
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                    _, native_bridge = command(['systemctl', 'is-active', 'php-fpm'+version[3:]+'.service'])
                    if version not in registry() or (APPS/version/'bin/fpmctl').read_text() != runtime.wrapper(version) or mgr != 'active' or health != 'active' or native_bridge != 'active':
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                    _, mgr = command(['systemctl', 'is-active', 'wpiso-manager-'+version+'.service'])
                    _, health = command(['systemctl', 'is-active', 'wpiso-health-'+version+'.service'])
                    _, native_bridge = command(['systemctl', 'is-active', 'php-fpm'+version[3:]+'.service'])
                    if version not in registry() or (APPS/version/'bin/fpmctl').read_text() != runtime.wrapper(version) or mgr != 'active' or health != 'active' or native_bridge != 'active':
                        raise RuntimeError('Post-operation service verification failed')
                    entry.update(state='healthy', pendingBinaryChange=False, managed=True, coordinator=mgr, healthMaster=health, nativeBridge=native_bridge,
```

### Block 3 — replace

Existing anchor AFTER which:
```text
                    if version not in registry() or (APPS/version/'bin/fpmctl').read_text() != runtime.wrapper(version) or mgr != 'active' or health != 'active':
                        raise RuntimeError('Post-operation service verification failed')
```

Existing anchor BEFORE which:
```text
                                 fingerprint=fingerprint(version), launcherMatches=True, reason='Transactional onboarding/repair and service checks passed.')
                else:
```

Existing content to replace/remove (not copied):
```text
                    entry.update(state='healthy', pendingBinaryChange=False, managed=True, coordinator=mgr, healthMaster=health,
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                    entry.update(state='healthy', pendingBinaryChange=False, managed=True, coordinator=mgr, healthMaster=health, nativeBridge=native_bridge,
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                    if version not in registry() or (APPS/version/'bin/fpmctl').read_text() != runtime.wrapper(version) or mgr != 'active' or health != 'active' or native_bridge != 'active':
                        raise RuntimeError('Post-operation service verification failed')
                    entry.update(state='healthy', pendingBinaryChange=False, managed=True, coordinator=mgr, healthMaster=health, nativeBridge=native_bridge,
                                 fingerprint=fingerprint(version), launcherMatches=True, reason='Transactional onboarding/repair and service checks passed.')
                else:
```

## uniselv-resman/core/golden-shield.py

Installed paths: /usr/local/webuzo/plugins/uniselv-resman/core/golden-shield.py; ALSO /usr/local/uniselv-resman/core/golden-shield.py; ALSO /usr/local/sbin/golden-shield.py

Replace the full file; never append duplicate functions/directives. New files run from first through final line.

### Block 1 — replace

Existing anchor AFTER which:
```text
   if path.exists():
    backup=STATE/'backups'/(hashlib.sha256(key.encode()).hexdigest()+'-'+str(time.time_ns()));atomic(backup,path.read_text(),path.stat().st_mode&0o777)
```

Existing anchor BEFORE which:
```text
  elif path.exists() and hashlib.sha256(path.read_bytes()).hexdigest()!=data[key]['hash']:
   raise RuntimeError('Managed file changed; review before overwriting: '+key)
```

Existing content to replace/remove (not copied):
```text
    data[key]={'backup':str(backup),'mode':path.stat().st_mode&0o777}
   else:data[key]={'backup':None,'mode':mode}
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
    data[key]={'backup':str(backup),'mode':path.stat().st_mode&0o777,'uid':path.stat().st_uid,'gid':path.stat().st_gid}
   else:data[key]={'backup':None,'mode':mode,'uid':0,'gid':0}
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
   if path.exists():
    backup=STATE/'backups'/(hashlib.sha256(key.encode()).hexdigest()+'-'+str(time.time_ns()));atomic(backup,path.read_text(),path.stat().st_mode&0o777)
    data[key]={'backup':str(backup),'mode':path.stat().st_mode&0o777,'uid':path.stat().st_uid,'gid':path.stat().st_gid}
   else:data[key]={'backup':None,'mode':mode,'uid':0,'gid':0}
  elif path.exists() and hashlib.sha256(path.read_bytes()).hexdigest()!=data[key]['hash']:
   raise RuntimeError('Managed file changed; review before overwriting: '+key)
```

### Block 2 — replace

Existing anchor AFTER which:
```text
  elif path.exists() and hashlib.sha256(path.read_bytes()).hexdigest()!=data[key]['hash']:
   raise RuntimeError('Managed file changed; review before overwriting: '+key)
```

Existing anchor BEFORE which:
```text

def derive_auto_policy(cpus, total_ram):
```

Existing content to replace/remove (not copied):
```text
  atomic(path,text,mode);data[key]['hash']=hashlib.sha256(path.read_bytes()).hexdigest();atomic(STATE/'shared-files.json',json.dumps(data,indent=2))
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
  atomic(path,text,mode);os.chown(path,data[key].get('uid',0),data[key].get('gid',0));data[key]['hash']=hashlib.sha256(path.read_bytes()).hexdigest();atomic(STATE/'shared-files.json',json.dumps(data,indent=2))
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
  elif path.exists() and hashlib.sha256(path.read_bytes()).hexdigest()!=data[key]['hash']:
   raise RuntimeError('Managed file changed; review before overwriting: '+key)
  atomic(path,text,mode);os.chown(path,data[key].get('uid',0),data[key].get('gid',0));data[key]['hash']=hashlib.sha256(path.read_bytes()).hexdigest();atomic(STATE/'shared-files.json',json.dumps(data,indent=2))

def derive_auto_policy(cpus, total_ram):
```

### Block 3 — insert

Existing anchor AFTER which:
```text
  time.sleep(2)

```

Existing anchor BEFORE which:
```text
def restart_coordinator(version):
 unit='wpiso-manager-'+version+'.service'
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
# Shared Redis integration is optional, aggregate-bounded, and never creates per-user settings.
REDIS_CONFIG=pathlib.Path('/usr/local/apps/redis/redis.conf')
REDIS_DROPIN=UNITS/'redis.service.d/90-golden-shared.conf'

def shared_redis_model(profile,cpus,total):
 config=profile.get('configuration',profile);hardware=config['globalInputs']['hardware'];m=config['sections']['redis']['model']
 if hardware.get('cpu')!=cpus or hardware.get('measuredRamMiB')!=total:raise RuntimeError('Shared Redis profile hardware differs; regenerate Global Inputs')
 dataset=max(16,int(float(hardware['ram'])*1024//64//16)*16);budget=dataset*4;clients=max(32,cpus*32)
 if m.get('datasetMiB')!=dataset or m.get('serviceBudgetMiB')!=budget or m.get('maxclients')!=clients or config['globalInputs']['sharedServiceBudget']['redisMiB']!=budget:raise RuntimeError('Shared Redis model differs from the common physical budget')
 if budget>total-config['sections']['golden']['golden']['headroomMiB']:raise RuntimeError('Shared Redis exceeds physical hosting budget')
 return {'hostCpuCount':cpus,'measuredRamMiB':total,'datasetMiB':dataset,'memoryMiB':budget,'maxclients':clients,'cacheOnly':True}

def shared_redis_config(text,model):
 marker=r'(?ms)^# BEGIN Webuzo Planner Shared Redis\n.*?^# END Webuzo Planner Shared Redis\n?'
 if text.count('# BEGIN Webuzo Planner Shared Redis')!=text.count('# END Webuzo Planner Shared Redis'):raise RuntimeError('Unbalanced shared Redis config markers')
 text=re.sub(marker,'',text)
 lines=[line for line in text.splitlines() if not re.match(r'^\s*(?:maxmemory|maxmemory-policy|maxclients|protected-mode)\s+',line)]
 return '\n'.join(lines).rstrip()+'\n\n# BEGIN Webuzo Planner Shared Redis\nmaxmemory '+str(model['datasetMiB'])+'mb\nmaxmemory-policy allkeys-lru\nmaxclients '+str(model['maxclients'])+'\nprotected-mode yes\n# END Webuzo Planner Shared Redis\n'

def apply_shared_redis(profile_file=None,cache_only=False):
 if not (STATE/'installed.json').exists():raise RuntimeError('Install Golden Shield before shared Redis resource integration')
 cpus=len(os.sched_getaffinity(0));total=int(next(x.split()[1] for x in pathlib.Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemTotal:')))//1024
 saved=BASE/'shared-redis-policy.json'
 if profile_file:
  if not cache_only:raise RuntimeError('Explicit --cache-only confirmation required; do not evict sessions/queues/primary data')
  source=pathlib.Path(profile_file)
  if not source.is_file() or source.is_symlink() or source.stat().st_uid!=0 or source.stat().st_mode&0o022:raise RuntimeError('Shared Redis profile must be a root-owned, non-writable regular file')
  model=shared_redis_model(json.loads(source.read_text()),cpus,total)
 else:
  if not saved.is_file() or saved.is_symlink() or saved.stat().st_uid!=0 or saved.stat().st_mode&0o022:raise RuntimeError('Shared Redis policy requires reviewed setup')
  model=json.loads(saved.read_text())
 if model.get('hostCpuCount')!=cpus or model.get('measuredRamMiB')!=total or model.get('cacheOnly') is not True:raise RuntimeError('Shared Redis policy requires new hardware/application review')
 if not all(type(model.get(k)) is int and model[k]>0 for k in ['datasetMiB','memoryMiB','maxclients']) or model['memoryMiB']!=model['datasetMiB']*4 or model['memoryMiB']>policy()['hostingMemoryMaxMiB']:raise RuntimeError('Invalid shared Redis safety budget')
 if not REDIS_CONFIG.is_file() or REDIS_CONFIG.is_symlink() or REDIS_CONFIG.stat().st_uid not in (0,pwd.getpwnam('redis').pw_uid) or REDIS_CONFIG.stat().st_mode&0o022 or REDIS_CONFIG.parent.stat().st_uid!=0 or REDIS_CONFIG.parent.stat().st_mode&0o022:raise RuntimeError('Unsafe native shared Redis configuration')
 current=json.loads(command(['redis-cli','--json','CONFIG','GET','bind','port','protected-mode']).stdout)
 if current.get('port')!='6379' or current.get('protected-mode')!='yes' or not current.get('bind') or any(x not in ['127.0.0.1','::1','-::1'] for x in current['bind'].split()):raise RuntimeError('Expected existing loopback-only Shared Redis service; mode/auth changes require review')
 snapshots={p:(p.read_text(),p.stat().st_mode&0o777,p.stat().st_uid,p.stat().st_gid) if p.exists() and not p.is_symlink() else None for p in [REDIS_CONFIG,REDIS_DROPIN,saved]}
 if REDIS_DROPIN.is_symlink() or saved.is_symlink():raise RuntimeError('Refusing shared Redis managed-path symlink')
 registry=files()
 try:
  managed(REDIS_CONFIG,shared_redis_config(snapshots[REDIS_CONFIG][0],model),snapshots[REDIS_CONFIG][1])
  managed(REDIS_DROPIN,'[Service]\nSlice=golden.slice\nMemoryMax='+str(model['memoryMiB'])+'M\nMemorySwapMax=0\n',0o644)
  atomic(saved,json.dumps(model,indent=2));command(['systemctl','daemon-reload']);command(['systemctl','restart','redis.service'])
  deadline=time.monotonic()+30
  while True:
   result=command(['redis-cli','--json','CONFIG','GET','maxmemory','maxmemory-policy','maxclients','protected-mode'],False)
   try:actual=json.loads(result.stdout) if result.returncode==0 else {}
   except ValueError:actual={}
   unit=properties('redis.service',['ControlGroup','MemoryMax','MemorySwapMax','ActiveState'])
   if actual.get('maxmemory')==str(model['datasetMiB']*1048576) and actual.get('maxmemory-policy')=='allkeys-lru' and actual.get('maxclients')==str(model['maxclients']) and actual.get('protected-mode')=='yes' and unit.get('ActiveState')=='active' and unit.get('ControlGroup','').startswith('/golden.slice/') and unit.get('MemoryMax')==str(model['memoryMiB']*1048576) and unit.get('MemorySwapMax')=='0':break
   if time.monotonic()>deadline:raise RuntimeError('Shared Redis runtime readback failed')
   time.sleep(.25)
 except BaseException:
  for path,row in snapshots.items():
   if row:
    atomic(path,row[0],row[1]);os.chown(path,row[2],row[3])
   else:path.unlink(missing_ok=True)
  atomic(STATE/'shared-files.json',json.dumps(registry,indent=2));command(['systemctl','daemon-reload'],False);command(['systemctl','restart','redis.service'],False)
  raise
 print(json.dumps({'sharedRedisApplied':True,'model':model,'tenantScope':'Shared service; unique cache prefixes are not Unix-account isolation'}))


```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
  time.sleep(2)

# Shared Redis integration is optional, aggregate-bounded, and never creates per-user settings.
REDIS_CONFIG=pathlib.Path('/usr/local/apps/redis/redis.conf')
REDIS_DROPIN=UNITS/'redis.service.d/90-golden-shared.conf'

def shared_redis_model(profile,cpus,total):
 config=profile.get('configuration',profile);hardware=config['globalInputs']['hardware'];m=config['sections']['redis']['model']
 if hardware.get('cpu')!=cpus or hardware.get('measuredRamMiB')!=total:raise RuntimeError('Shared Redis profile hardware differs; regenerate Global Inputs')
 dataset=max(16,int(float(hardware['ram'])*1024//64//16)*16);budget=dataset*4;clients=max(32,cpus*32)
 if m.get('datasetMiB')!=dataset or m.get('serviceBudgetMiB')!=budget or m.get('maxclients')!=clients or config['globalInputs']['sharedServiceBudget']['redisMiB']!=budget:raise RuntimeError('Shared Redis model differs from the common physical budget')
 if budget>total-config['sections']['golden']['golden']['headroomMiB']:raise RuntimeError('Shared Redis exceeds physical hosting budget')
 return {'hostCpuCount':cpus,'measuredRamMiB':total,'datasetMiB':dataset,'memoryMiB':budget,'maxclients':clients,'cacheOnly':True}

def shared_redis_config(text,model):
 marker=r'(?ms)^# BEGIN Webuzo Planner Shared Redis\n.*?^# END Webuzo Planner Shared Redis\n?'
 if text.count('# BEGIN Webuzo Planner Shared Redis')!=text.count('# END Webuzo Planner Shared Redis'):raise RuntimeError('Unbalanced shared Redis config markers')
 text=re.sub(marker,'',text)
 lines=[line for line in text.splitlines() if not re.match(r'^\s*(?:maxmemory|maxmemory-policy|maxclients|protected-mode)\s+',line)]
 return '\n'.join(lines).rstrip()+'\n\n# BEGIN Webuzo Planner Shared Redis\nmaxmemory '+str(model['datasetMiB'])+'mb\nmaxmemory-policy allkeys-lru\nmaxclients '+str(model['maxclients'])+'\nprotected-mode yes\n# END Webuzo Planner Shared Redis\n'

def apply_shared_redis(profile_file=None,cache_only=False):
 if not (STATE/'installed.json').exists():raise RuntimeError('Install Golden Shield before shared Redis resource integration')
 cpus=len(os.sched_getaffinity(0));total=int(next(x.split()[1] for x in pathlib.Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemTotal:')))//1024
 saved=BASE/'shared-redis-policy.json'
 if profile_file:
  if not cache_only:raise RuntimeError('Explicit --cache-only confirmation required; do not evict sessions/queues/primary data')
  source=pathlib.Path(profile_file)
  if not source.is_file() or source.is_symlink() or source.stat().st_uid!=0 or source.stat().st_mode&0o022:raise RuntimeError('Shared Redis profile must be a root-owned, non-writable regular file')
  model=shared_redis_model(json.loads(source.read_text()),cpus,total)
 else:
  if not saved.is_file() or saved.is_symlink() or saved.stat().st_uid!=0 or saved.stat().st_mode&0o022:raise RuntimeError('Shared Redis policy requires reviewed setup')
  model=json.loads(saved.read_text())
 if model.get('hostCpuCount')!=cpus or model.get('measuredRamMiB')!=total or model.get('cacheOnly') is not True:raise RuntimeError('Shared Redis policy requires new hardware/application review')
 if not all(type(model.get(k)) is int and model[k]>0 for k in ['datasetMiB','memoryMiB','maxclients']) or model['memoryMiB']!=model['datasetMiB']*4 or model['memoryMiB']>policy()['hostingMemoryMaxMiB']:raise RuntimeError('Invalid shared Redis safety budget')
 if not REDIS_CONFIG.is_file() or REDIS_CONFIG.is_symlink() or REDIS_CONFIG.stat().st_uid not in (0,pwd.getpwnam('redis').pw_uid) or REDIS_CONFIG.stat().st_mode&0o022 or REDIS_CONFIG.parent.stat().st_uid!=0 or REDIS_CONFIG.parent.stat().st_mode&0o022:raise RuntimeError('Unsafe native shared Redis configuration')
 current=json.loads(command(['redis-cli','--json','CONFIG','GET','bind','port','protected-mode']).stdout)
 if current.get('port')!='6379' or current.get('protected-mode')!='yes' or not current.get('bind') or any(x not in ['127.0.0.1','::1','-::1'] for x in current['bind'].split()):raise RuntimeError('Expected existing loopback-only Shared Redis service; mode/auth changes require review')
 snapshots={p:(p.read_text(),p.stat().st_mode&0o777,p.stat().st_uid,p.stat().st_gid) if p.exists() and not p.is_symlink() else None for p in [REDIS_CONFIG,REDIS_DROPIN,saved]}
 if REDIS_DROPIN.is_symlink() or saved.is_symlink():raise RuntimeError('Refusing shared Redis managed-path symlink')
 registry=files()
 try:
  managed(REDIS_CONFIG,shared_redis_config(snapshots[REDIS_CONFIG][0],model),snapshots[REDIS_CONFIG][1])
  managed(REDIS_DROPIN,'[Service]\nSlice=golden.slice\nMemoryMax='+str(model['memoryMiB'])+'M\nMemorySwapMax=0\n',0o644)
  atomic(saved,json.dumps(model,indent=2));command(['systemctl','daemon-reload']);command(['systemctl','restart','redis.service'])
  deadline=time.monotonic()+30
  while True:
   result=command(['redis-cli','--json','CONFIG','GET','maxmemory','maxmemory-policy','maxclients','protected-mode'],False)
   try:actual=json.loads(result.stdout) if result.returncode==0 else {}
   except ValueError:actual={}
   unit=properties('redis.service',['ControlGroup','MemoryMax','MemorySwapMax','ActiveState'])
   if actual.get('maxmemory')==str(model['datasetMiB']*1048576) and actual.get('maxmemory-policy')=='allkeys-lru' and actual.get('maxclients')==str(model['maxclients']) and actual.get('protected-mode')=='yes' and unit.get('ActiveState')=='active' and unit.get('ControlGroup','').startswith('/golden.slice/') and unit.get('MemoryMax')==str(model['memoryMiB']*1048576) and unit.get('MemorySwapMax')=='0':break
   if time.monotonic()>deadline:raise RuntimeError('Shared Redis runtime readback failed')
   time.sleep(.25)
 except BaseException:
  for path,row in snapshots.items():
   if row:
    atomic(path,row[0],row[1]);os.chown(path,row[2],row[3])
   else:path.unlink(missing_ok=True)
  atomic(STATE/'shared-files.json',json.dumps(registry,indent=2));command(['systemctl','daemon-reload'],False);command(['systemctl','restart','redis.service'],False)
  raise
 print(json.dumps({'sharedRedisApplied':True,'model':model,'tenantScope':'Shared service; unique cache prefixes are not Unix-account isolation'}))


def restart_coordinator(version):
 unit='wpiso-manager-'+version+'.service'
```

### Block 4 — insert

Existing anchor AFTER which:
```text
 guard='[Unit]\nDescription=Golden Shield shared CPU and memory guard\nAfter=webuzo.service golden-apache.service mariadb.service\n[Service]\nType=simple\nExecStart=/usr/bin/python3 /usr/local/sbin/golden-shield.py serve\nRestart=on-failure\nRestartSec=2\nCPUWeight=10000\nMemoryLow='+str(p['guardMemoryLowMiB'])+'M\nMemoryMax='+str(p['guardMemoryMaxMiB'])+'M\n[Install]\nWantedBy=multi-user.target\n'
 managed(UNITS/'golden-shield.service',guard);command(['systemctl','daemon-reload']);command(['systemctl','enable','--now','golden-shield.service'])
```

Existing anchor BEFORE which:
```text

def resume_install():
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
 if (BASE/'shared-redis-policy.json').exists():apply_shared_redis()
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
 guard='[Unit]\nDescription=Golden Shield shared CPU and memory guard\nAfter=webuzo.service golden-apache.service mariadb.service\n[Service]\nType=simple\nExecStart=/usr/bin/python3 /usr/local/sbin/golden-shield.py serve\nRestart=on-failure\nRestartSec=2\nCPUWeight=10000\nMemoryLow='+str(p['guardMemoryLowMiB'])+'M\nMemoryMax='+str(p['guardMemoryMaxMiB'])+'M\n[Install]\nWantedBy=multi-user.target\n'
 managed(UNITS/'golden-shield.service',guard);command(['systemctl','daemon-reload']);command(['systemctl','enable','--now','golden-shield.service'])
 if (BASE/'shared-redis-policy.json').exists():apply_shared_redis()

def resume_install():
```

### Block 5 — insert

Existing anchor AFTER which:
```text
 report['outsideManagedGroup']=outside;report['checksPass'] &= not outside
 if (RUN/'pressure.json').exists():report['pressure']=json.loads((RUN/'pressure.json').read_text())
```

Existing anchor BEFORE which:
```text
 print(json.dumps(report,indent=2));return report['checksPass']

```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
 if (BASE/'shared-redis-policy.json').exists():
  try:
   cache=json.loads((BASE/'shared-redis-policy.json').read_text());row=properties('redis.service',['ActiveState','ControlGroup','MemoryMax','MemorySwapMax']);values=json.loads(command(['redis-cli','--json','CONFIG','GET','maxmemory','maxmemory-policy','maxclients','protected-mode']).stdout)
   ok=row.get('ActiveState')=='active' and row.get('ControlGroup','').startswith('/golden.slice/') and row.get('MemoryMax')==str(cache['memoryMiB']*1048576) and row.get('MemorySwapMax')=='0' and values.get('maxmemory')==str(cache['datasetMiB']*1048576) and values.get('maxmemory-policy')=='allkeys-lru' and values.get('maxclients')==str(cache['maxclients']) and str(REDIS_CONFIG) in files()
   report['sharedRedis']={'passed':ok,'service':row,'settings':values};report['checksPass'] &= ok
  except Exception:
   report['sharedRedis']={'passed':False,'reason':'Shared Redis runtime verification unavailable; review selected shared policy and native service'};report['checksPass']=False
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
 report['outsideManagedGroup']=outside;report['checksPass'] &= not outside
 if (RUN/'pressure.json').exists():report['pressure']=json.loads((RUN/'pressure.json').read_text())
 if (BASE/'shared-redis-policy.json').exists():
  try:
   cache=json.loads((BASE/'shared-redis-policy.json').read_text());row=properties('redis.service',['ActiveState','ControlGroup','MemoryMax','MemorySwapMax']);values=json.loads(command(['redis-cli','--json','CONFIG','GET','maxmemory','maxmemory-policy','maxclients','protected-mode']).stdout)
   ok=row.get('ActiveState')=='active' and row.get('ControlGroup','').startswith('/golden.slice/') and row.get('MemoryMax')==str(cache['memoryMiB']*1048576) and row.get('MemorySwapMax')=='0' and values.get('maxmemory')==str(cache['datasetMiB']*1048576) and values.get('maxmemory-policy')=='allkeys-lru' and values.get('maxclients')==str(cache['maxclients']) and str(REDIS_CONFIG) in files()
   report['sharedRedis']={'passed':ok,'service':row,'settings':values};report['checksPass'] &= ok
  except Exception:
   report['sharedRedis']={'passed':False,'reason':'Shared Redis runtime verification unavailable; review selected shared policy and native service'};report['checksPass']=False
 print(json.dumps(report,indent=2));return report['checksPass']

```

### Block 6 — insert

Existing anchor AFTER which:
```text
 for version in versions:command(['systemctl','stop','wpiso-manager-'+version+'.service'])
 command(['/usr/bin/python3',str(ISO),'native-cgroup-remove'])
```

Existing anchor BEFORE which:
```text
 for name,row in data.items():
  path=pathlib.Path(name)
  if row['backup']:atomic(path,pathlib.Path(row['backup']).read_text(),row['mode'])
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
 redis_managed=str(REDIS_CONFIG) in data
 if redis_managed:command(['systemctl','stop','redis.service'])
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
 for version in versions:command(['systemctl','stop','wpiso-manager-'+version+'.service'])
 command(['/usr/bin/python3',str(ISO),'native-cgroup-remove'])
 redis_managed=str(REDIS_CONFIG) in data
 if redis_managed:command(['systemctl','stop','redis.service'])
 for name,row in data.items():
  path=pathlib.Path(name)
```

### Block 7 — replace

Existing anchor AFTER which:
```text
 command(['/usr/bin/python3',str(ISO),'native-cgroup-remove'])
 for name,row in data.items():
  path=pathlib.Path(name)
```

Existing anchor BEFORE which:
```text
  else:path.unlink(missing_ok=True)
 # Shared-unit runtime properties disappear when their units are stopped below.
```

Existing content to replace/remove (not copied):
```text
  if row['backup']:atomic(path,pathlib.Path(row['backup']).read_text(),row['mode'])
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
  if row['backup']:
   atomic(path,pathlib.Path(row['backup']).read_text(),row['mode']);os.chown(path,row.get('uid',0),row.get('gid',0))
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
 for name,row in data.items():
  path=pathlib.Path(name)
  if row['backup']:
   atomic(path,pathlib.Path(row['backup']).read_text(),row['mode']);os.chown(path,row.get('uid',0),row.get('gid',0))
  else:path.unlink(missing_ok=True)
 # Shared-unit runtime properties disappear when their units are stopped below.
```

### Block 8 — insert

Existing anchor AFTER which:
```text
 command(['systemctl','daemon-reload']);command(['systemctl','restart','mariadb.service'])
 command([str(APACHE),'start']);command(['systemctl','restart','cgroup.service'])
```

Existing anchor BEFORE which:
```text
 # Switch routing before restart, but retain the installation marker until all
 # restoration steps finish so a failed uninstall cannot masquerade as removed.
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
 if redis_managed:command(['systemctl','restart','redis.service'])
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
 command(['systemctl','daemon-reload']);command(['systemctl','restart','mariadb.service'])
 command([str(APACHE),'start']);command(['systemctl','restart','cgroup.service'])
 if redis_managed:command(['systemctl','restart','redis.service'])
 # Switch routing before restart, but retain the installation marker until all
 # restoration steps finish so a failed uninstall cannot masquerade as removed.
```

### Block 9 — replace

Existing anchor AFTER which:
```text
def main():
 if os.geteuid()!=0:raise RuntimeError('Run through sudo.')
```

Existing anchor BEFORE which:
```text
 if args.action=='install':install()
 elif args.action=='resume':resume_install()
```

Existing content to replace/remove (not copied):
```text
 parser=argparse.ArgumentParser();parser.add_argument('action',choices=['install','resume','check','serve','uninstall','prepare-account','preflight','repair-native-ownership','apply-memory-cap'],nargs='?',default='install');parser.add_argument('uid',nargs='?');args=parser.parse_args()
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
 parser=argparse.ArgumentParser();parser.add_argument('action',choices=['install','resume','check','serve','uninstall','prepare-account','preflight','repair-native-ownership','apply-memory-cap','apply-shared-redis'],nargs='?',default='install');parser.add_argument('uid',nargs='?');parser.add_argument('--cache-only',action='store_true');args=parser.parse_args()
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
def main():
 if os.geteuid()!=0:raise RuntimeError('Run through sudo.')
 parser=argparse.ArgumentParser();parser.add_argument('action',choices=['install','resume','check','serve','uninstall','prepare-account','preflight','repair-native-ownership','apply-memory-cap','apply-shared-redis'],nargs='?',default='install');parser.add_argument('uid',nargs='?');parser.add_argument('--cache-only',action='store_true');args=parser.parse_args()
 if args.action=='install':install()
 elif args.action=='resume':resume_install()
```

### Block 10 — insert

Existing anchor AFTER which:
```text
 elif args.action=='uninstall':uninstall()
 elif args.action=='apply-memory-cap':apply_memory_cap()
```

Existing anchor BEFORE which:
```text
 elif args.action=='repair-native-ownership':repair_native_ownership()
 else:sys.exit(0 if check() else 1)
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
 elif args.action=='apply-shared-redis':apply_shared_redis(args.uid,args.cache_only)
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
 elif args.action=='uninstall':uninstall()
 elif args.action=='apply-memory-cap':apply_memory_cap()
 elif args.action=='apply-shared-redis':apply_shared_redis(args.uid,args.cache_only)
 elif args.action=='repair-native-ownership':repair_native_ownership()
 else:sys.exit(0 if check() else 1)
```

## uniselv-resman/core/webuzo-isolation.py

Installed paths: /usr/local/webuzo/plugins/uniselv-resman/core/webuzo-isolation.py; ALSO /usr/local/uniselv-resman/core/webuzo-isolation.py; ALSO /usr/local/sbin/webuzo-isolation.py

Replace the full file; never append duplicate functions/directives. New files run from first through final line.

### Block 1 — insert

Existing anchor AFTER which:
```text
        if execute(['systemctl', 'is-active', unit], False).returncode != 0:
            execute(['systemctl', 'enable', '--now', unit])
```

Existing anchor BEFORE which:
```text
        reconcile(version, True)
        print(version + ': already onboarded; refreshed coordinator and health master')
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
        # Native regeneration can leave the compatibility bridge inactive while
        # the coordinator is healthy. Repair and activate the checked bridge too.
        add_bridge(version)
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
        if execute(['systemctl', 'is-active', unit], False).returncode != 0:
            execute(['systemctl', 'enable', '--now', unit])
        # Native regeneration can leave the compatibility bridge inactive while
        # the coordinator is healthy. Repair and activate the checked bridge too.
        add_bridge(version)
        reconcile(version, True)
        print(version + ': already onboarded; refreshed coordinator and health master')
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
  "version": "1.1.29",
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
  "version": "1.1.30",
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
  "name": "UNISELV Resource Manager",
  "slug": "uniselv-resman",
  "version": "1.1.30",
  "author": "<a href=\"https://refat.ovh\" target=\"_blank\">Refat Rahman</a>",
  "developer": {
```

### Block 2 — replace

Existing anchor AFTER which:
```text
  "download_url": "https://refat.ovh/plugins/uniselv-resman/",
  "download_link": "https://refat.ovh/plugins/uniselv-resman/uniselv-resman.zip",
```

Existing anchor BEFORE which:
```text
  "homepage": "https://refat.ovh"
}
```

Existing content to replace/remove (not copied):
```text
  "last_updated": "2026-10-24",
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
  "last_updated": "2026-10-25",
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
  "download_url": "https://refat.ovh/plugins/uniselv-resman/",
  "download_link": "https://refat.ovh/plugins/uniselv-resman/uniselv-resman.zip",
  "last_updated": "2026-10-25",
  "homepage": "https://refat.ovh"
}
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
Version: 1.1.29
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
Version: 1.1.30
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
/*
Plugin Name: UNISELV Resource Manager
Version: 1.1.30
Description: Enterprise Resource Management, Cgroups v2 Isolation, Real-Time Monitoring & Telemetry for Webuzo.
Author: Refat Rahman
```

### Block 2 — replace

Existing anchor AFTER which:
```text
    if (rtrim($brand_docs, '/') === 'https://docs.uniselv.com') $brand_docs = ''; // Historical placeholder; use bundled local Help.

    $panel_url = !empty($globals['panel_url']) ? rtrim($globals['panel_url'], '/') : '';
    $i18n_dict = uniselv_get_i18n_dict();

```

Existing anchor BEFORE which:
```text
    echo '<style>:root { --uniselv-primary: ' . $brand_color . '; --primary-color: ' . $brand_color . '; }</style>';
    echo '<script>
window.UNISELV_LOCALE = ' . json_encode($locale) . ';
window.UNISELV_TRANSLATIONS = ' . json_encode($i18n_dict[$locale] ?? $i18n_dict['en']) . ';
</script>';
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '-1.1.29r1' . '"></script>';

    echo '<div class="uniselv-container">';
    
```

Existing content to replace/remove (not copied):
```text
    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '-1.1.29r1' . '">';
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '-1.1.30r1' . '">';
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
    $i18n_dict = uniselv_get_i18n_dict();

    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '-1.1.30r1' . '">';
    echo '<style>:root { --uniselv-primary: ' . $brand_color . '; --primary-color: ' . $brand_color . '; }</style>';
    echo '<script>
```

### Block 3 — replace

Existing anchor AFTER which:
```text
    if (rtrim($brand_docs, '/') === 'https://docs.uniselv.com') $brand_docs = ''; // Historical placeholder; use bundled local Help.

    $panel_url = !empty($globals['panel_url']) ? rtrim($globals['panel_url'], '/') : '';
    $i18n_dict = uniselv_get_i18n_dict();

    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '-1.1.29r1' . '">';
    echo '<style>:root { --uniselv-primary: ' . $brand_color . '; --primary-color: ' . $brand_color . '; }</style>';
    echo '<script>
window.UNISELV_LOCALE = ' . json_encode($locale) . ';
window.UNISELV_TRANSLATIONS = ' . json_encode($i18n_dict[$locale] ?? $i18n_dict['en']) . ';
</script>';
```

Existing anchor BEFORE which:
```text

    echo '<div class="uniselv-container">';
    
```

Existing content to replace/remove (not copied):
```text
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '-1.1.29r1' . '"></script>';
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '-1.1.30r1' . '"></script>';
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
window.UNISELV_TRANSLATIONS = ' . json_encode($i18n_dict[$locale] ?? $i18n_dict['en']) . ';
</script>';
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '-1.1.30r1' . '"></script>';

    echo '<div class="uniselv-container">';
```

### Block 4 — replace

Existing anchor AFTER which:
```text
    $limits = isset($dash['limits']) ? $dash['limits'] : [];

    $panel_url = !empty($globals['panel_url']) ? rtrim($globals['panel_url'], '/') : '';
    $i18n_dict = uniselv_get_i18n_dict();

```

Existing anchor BEFORE which:
```text
    echo '<style>:root { --uniselv-primary: ' . $brand_color . '; --primary-color: ' . $brand_color . '; }</style>';
    echo '<script>
window.UNISELV_LOCALE = ' . json_encode($locale) . ';
window.UNISELV_TRANSLATIONS = ' . json_encode($i18n_dict[$locale] ?? $i18n_dict['en']) . ';
</script>';
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '-1.1.29r1' . '"></script>';

    echo '<div class="uniselv-container">';

    // Header
```

Existing content to replace/remove (not copied):
```text
    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '-1.1.29r1' . '">';
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '-1.1.30r1' . '">';
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
    $i18n_dict = uniselv_get_i18n_dict();

    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '-1.1.30r1' . '">';
    echo '<style>:root { --uniselv-primary: ' . $brand_color . '; --primary-color: ' . $brand_color . '; }</style>';
    echo '<script>
```

### Block 5 — replace

Existing anchor AFTER which:
```text
    $limits = isset($dash['limits']) ? $dash['limits'] : [];

    $panel_url = !empty($globals['panel_url']) ? rtrim($globals['panel_url'], '/') : '';
    $i18n_dict = uniselv_get_i18n_dict();

    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '-1.1.29r1' . '">';
    echo '<style>:root { --uniselv-primary: ' . $brand_color . '; --primary-color: ' . $brand_color . '; }</style>';
    echo '<script>
window.UNISELV_LOCALE = ' . json_encode($locale) . ';
window.UNISELV_TRANSLATIONS = ' . json_encode($i18n_dict[$locale] ?? $i18n_dict['en']) . ';
</script>';
```

Existing anchor BEFORE which:
```text

    echo '<div class="uniselv-container">';

    // Header
```

Existing content to replace/remove (not copied):
```text
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '-1.1.29r1' . '"></script>';
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '-1.1.30r1' . '"></script>';
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
window.UNISELV_TRANSLATIONS = ' . json_encode($i18n_dict[$locale] ?? $i18n_dict['en']) . ';
</script>';
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '-1.1.30r1' . '"></script>';

    echo '<div class="uniselv-container">';
```

## uniselv-resman/views/admin_help.php

Installed paths: /usr/local/webuzo/plugins/uniselv-resman/views/admin_help.php

Replace the full file; never append duplicate functions/directives. New files run from first through final line.

### Block 1 — replace

Existing anchor AFTER which:
```text
            <h4 class="uniselv-help-card-title">Runtime Operations, Exact Source Placement &amp; Validation Scope</h4>
            <div class="uniselv-help-card-desc">Release <?php echo $uniselvHelpEscape($uniselvHelpVersion); ?>. These technical guides describe already-applied changes; they are not additional post-install paste steps.</div>
```

Existing anchor BEFORE which:
```text
        </div>


        <!-- 1. QUICK START -->
```

Existing content to replace/remove (not copied):
```text
            <details><summary>Operations, expected profile and verification scope</summary><pre style="white-space:pre-wrap;overflow-wrap:anywhere"><?php echo htmlspecialchars(file_get_contents(__DIR__ . '/../docs/release-1.1.29.md'), ENT_QUOTES, 'UTF-8'); ?></pre></details>
            <details><summary>Exact source replacement and insertion guide</summary><pre style="white-space:pre-wrap;overflow-wrap:anywhere"><?php echo htmlspecialchars(file_get_contents(__DIR__ . '/../docs/source-changes-1.1.29.md'), ENT_QUOTES, 'UTF-8'); ?></pre></details>
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
            <details><summary>Operations, expected profile and verification scope</summary><pre style="white-space:pre-wrap;overflow-wrap:anywhere"><?php echo htmlspecialchars(file_get_contents(__DIR__ . '/../docs/release-1.1.30.md'), ENT_QUOTES, 'UTF-8'); ?></pre></details>
            <details><summary>Exact source replacement and insertion guide</summary><pre style="white-space:pre-wrap;overflow-wrap:anywhere"><?php echo htmlspecialchars(file_get_contents(__DIR__ . '/../docs/source-changes-1.1.30.md'), ENT_QUOTES, 'UTF-8'); ?></pre></details>
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
            <h4 class="uniselv-help-card-title">Runtime Operations, Exact Source Placement &amp; Validation Scope</h4>
            <div class="uniselv-help-card-desc">Release <?php echo $uniselvHelpEscape($uniselvHelpVersion); ?>. These technical guides describe already-applied changes; they are not additional post-install paste steps.</div>
            <details><summary>Operations, expected profile and verification scope</summary><pre style="white-space:pre-wrap;overflow-wrap:anywhere"><?php echo htmlspecialchars(file_get_contents(__DIR__ . '/../docs/release-1.1.30.md'), ENT_QUOTES, 'UTF-8'); ?></pre></details>
            <details><summary>Exact source replacement and insertion guide</summary><pre style="white-space:pre-wrap;overflow-wrap:anywhere"><?php echo htmlspecialchars(file_get_contents(__DIR__ . '/../docs/source-changes-1.1.30.md'), ENT_QUOTES, 'UTF-8'); ?></pre></details>
        </div>

```
