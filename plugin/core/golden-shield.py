#!/usr/bin/python3
"""Golden Shield v2: kernel aggregate CPU quota for managed web hosting."""
import argparse,fcntl,hashlib,json,os,pathlib,pwd,re,shlex,signal,subprocess,sys,time
BASE=pathlib.Path('/etc/golden-shield');STATE=pathlib.Path('/var/lib/golden-shield');RUN=pathlib.Path('/run/golden-shield')
UNITS=pathlib.Path('/etc/systemd/system');SELF=pathlib.Path('/usr/local/sbin/golden-shield.py')
ISO=pathlib.Path('/usr/local/sbin/webuzo-isolation.py');SCANNER=pathlib.Path('/usr/local/webuzo/bin/cgroup.sh')
APACHE=pathlib.Path('/usr/local/apps/apache2/bin/apachectl');INIT=pathlib.Path('/etc/init.d/httpd')
alive=True
def command(args,check=True):
 r=subprocess.run(args,capture_output=True,text=True,timeout=90)
 if check and r.returncode:raise RuntimeError('Command failed: '+str(args)+': exit='+str(r.returncode)+' '+r.stdout[-1200:]+r.stderr[-1200:])
 return r
def atomic(path,text,mode=0o600):
 path.parent.mkdir(parents=True,exist_ok=True)
 if path.is_symlink():raise RuntimeError('Refusing symlink: '+str(path))
 temp=path.with_name(path.name+'.golden-'+str(time.time_ns()))
 with open(temp,'x',encoding='utf-8') as f:f.write(text)
 os.chmod(temp,mode);os.replace(temp,path)
def properties(unit,keys):
 return dict(x.split('=',1) for x in command(['systemctl','show',unit]+[v for k in keys for v in ['-p',k]]).stdout.splitlines())
def files():return json.loads((STATE/'shared-files.json').read_text()) if (STATE/'shared-files.json').exists() else {}
def managed(path,text,mode=0o600):
 STATE.mkdir(parents=True,exist_ok=True,mode=0o700)
 with open(STATE/'managed-files.lock','a') as registry_lock:
  fcntl.flock(registry_lock,fcntl.LOCK_EX)
  data=files();key=str(path)
  if key not in data:
   if path.exists():
    backup=STATE/'backups'/(hashlib.sha256(key.encode()).hexdigest()+'-'+str(time.time_ns()));atomic(backup,path.read_text(),path.stat().st_mode&0o777)
    data[key]={'backup':str(backup),'mode':path.stat().st_mode&0o777,'uid':path.stat().st_uid,'gid':path.stat().st_gid}
   else:data[key]={'backup':None,'mode':mode,'uid':0,'gid':0}
  elif path.exists() and hashlib.sha256(path.read_bytes()).hexdigest()!=data[key]['hash']:
   raise RuntimeError('Managed file changed; review before overwriting: '+key)
  atomic(path,text,mode);os.chown(path,data[key].get('uid',0),data[key].get('gid',0));data[key]['hash']=hashlib.sha256(path.read_bytes()).hexdigest();atomic(STATE/'shared-files.json',json.dumps(data,indent=2))

def derive_auto_policy(cpus, total_ram):
 if total_ram < 1024:
  raise RuntimeError(f"Unsupported Hardware: >= 1024 MiB RAM required (detected {total_ram} MiB)")
 customer_cpu = int(round(cpus * 85))
 reserved_cpu = (cpus * 100) - customer_cpu
 headroom = max(512, ((total_ram * 5 + 8191) // 8192) * 256)
 hosting_ram = max(512, total_ram - headroom)
 if hosting_ram + headroom > total_ram:
  headroom = max(384, total_ram - hosting_ram)
 panel_low = min(768, max(256, int(headroom * 0.5)))
 return {
  'mode': 'shared-aggregate-cpu',
  'hostCpuCount': cpus,
  'customerCpuPercent': customer_cpu,
  'reservedCpuPercent': reserved_cpu,
  'hostingMemoryMaxMiB': hosting_ram,
  'headroomMiB': headroom,
  'recoveryMarginMiB': 512,
  'recoverySeconds': 30,
  'panelLowMiB': panel_low,
  'sshLowMiB': 128,
  'guardMemoryLowMiB': 32,
  'guardMemoryMaxMiB': 128
 }

def policy():
 cpus = len(os.sched_getaffinity(0))
 total_ram = int(next(x.split()[1] for x in pathlib.Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemTotal:')))//1024
 if (BASE/'policy.json').exists():
  try:
   p = json.loads((BASE/'policy.json').read_text())
  except Exception as e:
   raise RuntimeError(f"Invalid policy in {BASE/'policy.json'}: unparseable JSON ({e})")
  if not isinstance(p, dict):
   raise RuntimeError(f"Invalid policy in {BASE/'policy.json'}: must be a JSON object")
  if p.get('mode') != 'shared-aggregate-cpu':
   raise RuntimeError(f"Invalid policy in {BASE/'policy.json'}: mode must be 'shared-aggregate-cpu', got {p.get('mode')}")
  if not isinstance(p.get('headroomMiB'), int) or p['headroomMiB'] < 512:
   raise RuntimeError(f"Invalid policy in {BASE/'policy.json'}: headroomMiB must be integer >= 512")
  if not isinstance(p.get('customerCpuPercent'), int) or not (0 < p['customerCpuPercent'] < cpus * 100):
   raise RuntimeError(f"Invalid policy in {BASE/'policy.json'}: customerCpuPercent out of range")
  if not isinstance(p.get('hostingMemoryMaxMiB'), int) or p['hostingMemoryMaxMiB'] < 512:
   raise RuntimeError(f"Invalid policy in {BASE/'policy.json'}: hostingMemoryMaxMiB must be integer >= 512")
  if p['hostingMemoryMaxMiB'] + p['headroomMiB'] > total_ram:
   raise RuntimeError(f"Invalid policy in {BASE/'policy.json'}: hostingMemoryMaxMiB + headroomMiB exceeds physical RAM ({total_ram} MiB)")
  return p
 return derive_auto_policy(cpus, total_ram)
def available():return int(next(x.split()[1] for x in pathlib.Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))//1024
def aggregate_unit(p):
 cap=p['hostingMemoryMaxMiB']
 return '[Unit]\nDescription=Golden Shield aggregate hosting budget\n[Slice]\nCPUAccounting=yes\nMemoryAccounting=yes\nCPUQuota='+str(p['customerCpuPercent'])+'%\nMemoryMax='+str(cap)+'M\nMemorySwapMax=0\n'

def effective_memory_cap(p):
 total=int(next(x.split()[1] for x in pathlib.Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemTotal:')))//1024
 value=p.get('hostingMemoryMaxMiB',total-p['headroomMiB'])
 if not isinstance(value,int) or value<512:raise RuntimeError('Invalid aggregate memory cap')
 p['hostingMemoryMaxMiB']=min(value,total-p['headroomMiB'])
 if p['hostingMemoryMaxMiB']<512:raise RuntimeError('Not enough physical hosting RAM')
 return p

def apply_memory_cap():
 p=effective_memory_cap(policy());root=pathlib.Path('/sys/fs/cgroup/golden.slice')
 if int((root/'memory.current').read_text())>p['hostingMemoryMaxMiB']*1048576:raise RuntimeError('Current hosting usage exceeds new cap; reduce workload in maintenance first')
 managed(UNITS/'golden.slice',aggregate_unit(p));atomic(BASE/'policy.json',json.dumps(p,indent=2))
 command(['systemctl','daemon-reload']);command(['systemctl','set-property','--runtime','golden.slice','MemoryMax='+str(p['hostingMemoryMaxMiB'])+'M','MemorySwapMax=0'])
 print(json.dumps({'hostingMemoryMaxMiB':p['hostingMemoryMaxMiB'],'aggregateSwapMax':(root/'memory.swap.max').read_text().strip(),'aggregateMemoryMax':(root/'memory.max').read_text().strip()}))

def prerequisites(p):
 if not pathlib.Path('/sys/fs/cgroup/cgroup.controllers').is_file():raise RuntimeError('cgroup v2 required.')
 if len(os.sched_getaffinity(0))!=p['hostCpuCount']:raise RuntimeError('Actual CPU count differs from Global Inputs; regenerate the script.')
 if properties('webuzo.service',['ActiveState']).get('ActiveState')!='active':raise RuntimeError('Native Webuzo service is not active.')
 if not pathlib.Path('/var/lib/webuzo-isolation/installed.json').exists():raise RuntimeError('Section 07 PHP Process Isolation required.')
 total=int(next(x.split()[1] for x in pathlib.Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemTotal:')))//1024
 if p['headroomMiB']>total//3:raise RuntimeError('RAM input/headroom incompatible with actual memory.')
 if not APACHE.is_file() or not INIT.is_file() or not SCANNER.is_file():raise RuntimeError('Unsupported native Apache/cgroup layout.')
def account_units():
 result=[]
 for user in pathlib.Path('/var/webuzo/users').iterdir():
  try:uid=pwd.getpwnam(user.name).pw_uid
  except KeyError:continue
  if uid>=1000 and (UNITS/(str(uid)+'.slice')).is_file():result.append(str(uid)+'.slice')
 return sorted(set(result))
def prepare_initial_registry():
 if (STATE/'installed.json').exists():return
 data=files(); mirrors={}; restored=False
 for name,row in data.items():
  path=pathlib.Path(name)
  if path.is_symlink():raise RuntimeError('Unsafe pre-install recovery path: '+name)
  current=hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
  is_mirror=path.parent==UNITS and re.fullmatch(r'golden-\d+\.slice',path.name)
  if is_mirror and current==row.get('hash'):
   mirrors[name]=row;continue
  original=hashlib.sha256(pathlib.Path(row['backup']).read_bytes()).hexdigest() if row.get('backup') else None
  if current!=original:raise RuntimeError('Prior restoration is incomplete; review before installation: '+name)
  restored=True
 if restored:
  if not list(STATE.glob('uninstalled-shared-*.json')):raise RuntimeError('No completed prior uninstall record; preserve recovery before retry.')
  atomic(STATE/('shared-files.previous-'+str(time.time_ns())+'.json'),json.dumps(data))
  atomic(STATE/'shared-files.json',json.dumps(mirrors))
  props=STATE/'shared-properties.json'
  if props.exists():props.rename(STATE/('shared-properties.previous-'+str(time.time_ns())+'.json'))
 elif (STATE/'shared-properties.json').exists() and json.loads((STATE/'shared-properties.json').read_text()):raise RuntimeError('Existing shared property recovery requires review before installation.')

def prepare_account(uid):
 if not re.fullmatch(r'\d+',uid) or uid+'.slice' not in account_units():raise RuntimeError('Not a native account slice.')
 STATE.mkdir(parents=True,exist_ok=True,mode=0o700)
 with open(STATE/'shared.lock','a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  prepare_initial_registry()
  source=(UNITS/(uid+'.slice')).read_text()
  values=dict(re.findall(r'^(CPUQuota|IOReadBandwidthMax|IOWriteBandwidthMax|IOReadIOPSMax|IOWriteIOPSMax|MemoryMax|MemoryHigh|TasksMax)=(.+)$',source,re.M))
  if len(values)!=8 or any(v.strip() in ['','infinity'] for v in values.values()):raise RuntimeError('Missing finite native plan limits for UID '+uid)
  values['MemorySwapMax']='0';unit='golden-'+uid+'.slice'
  text='[Unit]\nDescription=Golden Shield native-plan mirror '+uid+'\n[Slice]\n'+'\n'.join(k+'='+v for k,v in values.items())+'\n'
  path=UNITS/unit
  if not path.exists() or path.read_text()!=text:
   managed(path,text);command(['systemctl','daemon-reload']);command(['systemctl','start',unit])
   command(['systemctl','set-property','--runtime',unit]+[k+'='+v for k,v in values.items()])
  else:command(['systemctl','start',unit])
def patch_isolation():
 source=ISO.read_text()
 helper="\ndef account_slice(uid):\n    return ('golden-' if (pathlib.Path('/var/lib/golden-shield/installed.json').exists() and not pathlib.Path('/var/lib/golden-shield/disabling.json').exists()) else '')+str(uid)+'.slice'\n\ndef account_cgroup(uid):\n    return ('/golden.slice/' if (pathlib.Path('/var/lib/golden-shield/installed.json').exists() and not pathlib.Path('/var/lib/golden-shield/disabling.json').exists()) else '/')+account_slice(uid)\n\n"
 if 'def account_slice(' in source:
  required=[helper.strip(), "execute(['/usr/bin/python3','/usr/local/sbin/golden-shield.py','prepare-account',str(uid)])", "Slice='+account_slice(row['uid'])+'\\n", "'0::'+account_cgroup(actual_uid)", "startswith(account_cgroup(row['uid'])+'/')"]
  if not all(item in source for item in required):raise RuntimeError('Unsupported existing slice integration; refusing mutation.')
 else:
  source=source.replace('def ensure_limits(user,uid):',helper+'def ensure_limits(user,uid):')
  anchor='    return root\n'
  if source.count(anchor)!=1:raise RuntimeError('Unsupported ensure_limits layout.')
  source=source.replace(anchor,"    if (pathlib.Path('/var/lib/golden-shield/installed.json').exists() and not pathlib.Path('/var/lib/golden-shield/disabling.json').exists()):\n        execute(['/usr/bin/python3','/usr/local/sbin/golden-shield.py','prepare-account',str(uid)])\n"+anchor)
  source=source.replace("str(args[:3])+': '+r.stderr[-1200:]", "str(args)+': exit='+str(r.returncode)+' '+r.stdout[-1200:]+r.stderr[-1200:]")
  source=source.replace("Slice='+str(row['uid'])+'.slice\\n", "Slice='+account_slice(row['uid'])+'\\n")
  old="    if not (pathlib.Path('/proc/self/cgroup').read_text().strip()=='0::/'+str(actual_uid)+'.slice' or pathlib.Path('/proc/self/cgroup').read_text().strip().startswith('0::/'+str(actual_uid)+'.slice/')):"
  new="    if not (pathlib.Path('/proc/self/cgroup').read_text().strip()=='0::'+account_cgroup(actual_uid) or pathlib.Path('/proc/self/cgroup').read_text().strip().startswith('0::'+account_cgroup(actual_uid)+'/')):"
  if old not in source:raise RuntimeError('Unsupported admission layout.')
  source=source.replace(old,new)
  source=source.replace("startswith('/'+str(row['uid'])+'.slice/')", "startswith(account_cgroup(row['uid'])+'/')")
 # Socket proxies are hosting work too; keep them inside the same aggregate parent.
 compile(source,str(ISO),'exec');managed(ISO,source,0o755)
 # The owned service drop-in survives a vendor scanner refresh.
 command(['/usr/bin/python3',str(ISO),'native-cgroup-install'])

def remember(unit,settings):
 path=STATE/'shared-properties.json';data=json.loads(path.read_text()) if path.exists() else {}
 if unit not in data:data[unit]=properties(unit,list(settings));atomic(path,json.dumps(data,indent=2))
 managed(UNITS/(unit+'.d')/'90-golden-shield.conf','[Slice]\n'+'\n'.join(k+'='+v for k,v in settings.items())+'\n' if unit.endswith('.slice') else '[Service]\n'+'\n'.join(k+'='+v for k,v in settings.items())+'\n')
 command(['systemctl','set-property','--runtime',unit]+[k+'='+v for k,v in settings.items()])
def apache_launcher(original):
 return '#!/bin/sh\n# Golden Shield shared Apache launcher\ncase "${1:-}" in\n start|stop|restart|reload) exec /bin/systemctl "$1" golden-apache.service ;;\n graceful) exec /bin/systemctl reload golden-apache.service ;;\n graceful-stop) exec /bin/systemctl stop golden-apache.service ;;\n status) if /bin/systemctl is-active --quiet golden-apache.service; then echo "httpd is running"; else echo "httpd is stopped"; exit 1; fi ;;\n *) exec '+shlex.quote(str(original))+' "$@" ;;\nesac\n'

def apache_service_unit():
 # Track the foreground master directly; native boot cleanup may remove a PID file.
 # Type=simple remains compatible with older supported systemd implementations.
 return '[Unit]\nDescription=Golden Shield shared hosting Apache\nWants=httpd.service\nAfter=network.target\n[Service]\nType=simple\nSlice=golden.slice\nExecStartPre=/usr/local/apps/apache2/bin/httpd -t\nExecStart=/bin/sh -c \'if [ -f /usr/local/apps/apache2/bin/envvars ]; then . /usr/local/apps/apache2/bin/envvars; fi; ulimit -S -n "$$(ulimit -H -n)"; exec /usr/local/apps/apache2/bin/httpd -DFOREGROUND\'\nExecReload=/usr/local/apps/apache2/bin/httpd -t\nExecReload=/bin/kill -USR1 $MAINPID\nKillSignal=SIGWINCH\nKillMode=mixed\nTimeoutStartSec=30\nTimeoutStopSec=30\nRestart=on-failure\nRestartSec=2\n[Install]\nWantedBy=multi-user.target\n'

def apache_integration():
 # Preserve both native control entry points. The managed unit tracks the foreground binary; other commands use the saved original.
 if INIT.is_symlink() and INIT.resolve()!=APACHE.resolve():raise RuntimeError('Unsupported Apache init symlink target.')
 original=STATE/'apachectl.original'
 atomic(original,APACHE.read_text(),0o755)
 wrapper=apache_launcher(original)
 command([str(APACHE),'configtest'])
 pidfile=pathlib.Path('/usr/local/apps/apache2/logs/httpd.pid')
 old=int(pidfile.read_text().strip()) if pidfile.exists() else None
 command([str(APACHE),'stop'])
 deadline=time.monotonic()+20
 while old and pathlib.Path('/proc',str(old)).exists():
  if time.monotonic()>deadline:raise RuntimeError('Old Apache master has not stopped; review before retrying.')
  time.sleep(.2)
 unit=apache_service_unit()
 managed(UNITS/'golden-apache.service',unit);managed(APACHE,wrapper,0o755)
 if not INIT.is_symlink():managed(INIT,wrapper,0o755)
 command(['systemctl','daemon-reload']);command(['systemctl','enable','--now','golden-apache.service'])
def repair_native_ownership():
 apache_unit=UNITS/'golden-apache.service';desired=apache_service_unit()
 changed=apache_unit.read_text()!=desired
 command(['/usr/local/apps/apache2/bin/httpd','-t'])
 managed(apache_unit,desired,0o644)
 wrapper=apache_launcher(STATE/'apachectl.original');managed(APACHE,wrapper,0o755)
 if not INIT.is_symlink():managed(INIT,wrapper,0o755)
 # Do not let SysV PID guessing adopt the managed Apache master twice.
 bridge='[Unit]\nDescription=Webuzo Apache control bridge to Golden Shield\nWants=golden-apache.service\nAfter=golden-apache.service\n[Service]\nType=oneshot\nRemainAfterExit=yes\nExecStart=/bin/systemctl start golden-apache.service\nExecStop=/bin/systemctl stop golden-apache.service\nExecReload=/bin/systemctl reload golden-apache.service\n[Install]\nWantedBy=multi-user.target\n'
 managed(UNITS/'httpd.service',bridge,0o644)
 managed(UNITS/'webuzo-onboot.service.d'/'60-golden-ownership.conf','[Service]\nType=oneshot\nRemainAfterExit=yes\n',0o644)
 command(['systemctl','daemon-reload'])
 if changed:command(['systemctl','restart','golden-apache.service'])
 command(['systemctl','reset-failed','httpd.service','webuzo-onboot.service'],False)
 command(['systemctl','start','httpd.service'])
 # Starting the boot orchestrator is intentionally left to the controlled boot test.

def constrain_customers():
 for unit in account_units():prepare_account(unit.removesuffix('.slice'))
 for unit in ['golden-apache.service','mariadb.service']:
  if properties(unit,['ActiveState']).get('ActiveState')=='active':
   if not properties(unit,['ControlGroup']).get('ControlGroup','').startswith('/golden.slice/'):
    raise RuntimeError('Managed hosting service outside aggregate group: '+unit)

def active_customer_sockets():
 text=command(['systemctl','list-units','--type=socket','--state=active','--no-legend','--plain']).stdout
 return [x.split()[0] for x in text.splitlines() if re.fullmatch(r'wpiso-proxy-php\d+-[a-z_][a-z0-9_-]*\.socket',x.split()[0])]
def save_pressure(p,state):
 atomic(RUN/'pressure.json',json.dumps({'availableMiB':available(),'targetMiB':p['headroomMiB'],'pausedSockets':sorted(state['pausedSockets'])}))
def pressure_tick(p,state,now):
 low=available()<p['headroomMiB']
 if low:
  state['recoverySince']=None
  # Stop new admissions first. Only Section 07 customer sockets/FPMs are eligible.
  for sock in active_customer_sockets():
   state['pausedSockets'].add(sock);save_pressure(p,state);command(['systemctl','stop',sock])
  text=command(['systemctl','list-units','--type=service','--state=active','--no-legend','--plain']).stdout
  candidates=[]
  for line in text.splitlines():
   unit=line.split()[0]
   if re.fullmatch(r'wpiso-fpm-php\d+-[a-z_][a-z0-9_-]*\.service',unit):
    v=properties(unit,['MemoryCurrent']).get('MemoryCurrent','0');candidates.append((int(v) if v.isdigit() else 0,unit))
  for _,unit in sorted(candidates,reverse=True):
   command(['systemctl','stop',unit]);print('Memory pressure: stopped customer '+unit,flush=True)
   if available()>=p['headroomMiB']:break
 elif state['pausedSockets']:
  if available()<p['headroomMiB']+p['recoveryMarginMiB']:state['recoverySince']=None
  elif state['recoverySince'] is None:state['recoverySince']=now
  elif now-state['recoverySince']>=p['recoverySeconds']:
   for sock in list(state['pausedSockets']):
    if properties(sock,['LoadState']).get('LoadState')=='loaded':command(['systemctl','start',sock])
   state['pausedSockets'].clear();state['recoverySince']=None;print('Memory recovered: customer sockets resumed.',flush=True)
 save_pressure(p,state)
def serve():
 global alive
 p=policy();prerequisites(p);RUN.mkdir(parents=True,exist_ok=True)
 def stop(*_):
  global alive;alive=False
 signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
 previous=json.loads((RUN/'pressure.json').read_text()) if (RUN/'pressure.json').exists() else {}
 state={'pausedSockets':set(previous.get('pausedSockets',[])),'recoverySince':None}
 while alive:
  for task in [constrain_customers,lambda:pressure_tick(p,state,time.monotonic())]:
   try:task()
   except Exception as e:print('GUARD ERROR (protection incomplete): '+str(e),flush=True)
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
 result=command(['systemctl','restart',unit],False)
 if result.returncode:
  # Native Webuzo monitoring may replace the same restart job. Await the
  # resulting healthy coordinator instead of leaving a partial install.
  for _ in range(45):
   row=properties(unit,['ActiveState','SubState','StatusText'])
   if row.get('ActiveState')=='active' and row.get('SubState')=='running' and row.get('StatusText','').startswith('Isolated sockets ready:'):return
   time.sleep(1)
  raise RuntimeError('Coordinator did not recover after a competing native restart: '+unit)

def finish_install():
 p=policy()
 for version in json.loads(pathlib.Path('/var/lib/webuzo-isolation/installed.json').read_text())['versions']:
  restart_coordinator(version)
 guard='[Unit]\nDescription=Golden Shield shared CPU and memory guard\nAfter=webuzo.service golden-apache.service mariadb.service\n[Service]\nType=simple\nExecStart=/usr/bin/python3 /usr/local/sbin/golden-shield.py serve\nRestart=on-failure\nRestartSec=2\nCPUWeight=10000\nMemoryLow='+str(p['guardMemoryLowMiB'])+'M\nMemoryMax='+str(p['guardMemoryMaxMiB'])+'M\n[Install]\nWantedBy=multi-user.target\n'
 managed(UNITS/'golden-shield.service',guard);command(['systemctl','daemon-reload']);command(['systemctl','enable','--now','golden-shield.service'])
 if (BASE/'shared-redis-policy.json').exists():apply_shared_redis()

def resume_install():
 if not (STATE/'installed.json').exists():raise RuntimeError('No partial installation to resume')
 prerequisites(policy());data=files()
 required=[str(ISO),str(APACHE),str(UNITS/'httpd.service'),str(UNITS/'mariadb.service.d'/'90-golden-shared.conf')]
 if not INIT.is_symlink():required.append(str(INIT))
 elif INIT.resolve()!=APACHE.resolve():raise RuntimeError('Apache init target changed')
 if not all(k in data for k in required):raise RuntimeError('Earlier install stage incomplete; review rollback, do not resume blindly')
 for name,row in data.items():
  if not pathlib.Path(name).is_file() or hashlib.sha256(pathlib.Path(name).read_bytes()).hexdigest()!=row['hash']:raise RuntimeError('Managed file changed: '+name)
 finish_install()
 if not check():raise RuntimeError('Resumed installation failed verification')

def install():
 if (STATE/'installed.json').exists():raise RuntimeError('Already installed. Uninstall the current version first during maintenance; original backups must not be overwritten.')
 # The plugin writes the validated hardware-scaled Auto/Manual policy first.
 # Never replace it with a policy embedded for a different VPS.
 p=effective_memory_cap(policy())
 if not p or p.get('mode')!='shared-aggregate-cpu':raise RuntimeError('Configure a shared-mode policy through the plugin before installation.')
 prerequisites(p)
 if available()<p['headroomMiB']+p['recoveryMarginMiB']:raise RuntimeError('Not enough RAM headroom for installation.')
 command(['/usr/bin/python3',str(ISO),'verify'])
 for unit in ['golden.slice','golden-apache.service','golden-shield.service']:
  if (UNITS/unit).exists():raise RuntimeError('Existing custom unit needs review: '+unit)
 for folder in [BASE,STATE,RUN]:folder.mkdir(parents=True,exist_ok=True);os.chmod(folder,0o700)
 prepare_initial_registry()
 atomic(BASE/'policy.json',json.dumps(p,indent=2));atomic(SELF,pathlib.Path(__file__).read_text(),0o700)
 atomic(STATE/'installed.json',json.dumps({'version':2,'mode':p['mode'],'installedAt':time.time()}))
 managed(UNITS/'golden.slice',aggregate_unit(p))
 command(['systemctl','daemon-reload']);command(['systemctl','start','golden.slice'])
 remember('system.slice',{'CPUWeight':'1000','MemoryLow':str(p['headroomMiB']*1048576)})
 remember('webuzo.service',{'CPUWeight':'10000','IOWeight':'1000','MemoryLow':str(p['panelLowMiB']*1048576)})
 remember('ssh.service' if pathlib.Path('/etc/os-release').read_text().find('ID=ubuntu')>=0 else 'sshd.service',{'CPUWeight':'10000','IOWeight':'1000','MemoryLow':str(p['sshLowMiB']*1048576)})
 patch_isolation()
 for unit in account_units():prepare_account(unit.removesuffix('.slice'))
 managed(UNITS/'mariadb.service.d'/'90-golden-shared.conf','[Service]\nSlice=golden.slice\n')
 command(['systemctl','daemon-reload']);command(['systemctl','restart','mariadb.service'])
 apache_integration()
 repair_native_ownership()
 command(['systemctl','restart','cgroup.service'])
 # Reload resident supervisors too: their in-memory code must use the new placement.
 finish_install()
 print('Installed shared CPU budget '+str(p['customerCpuPercent'])+'%. All logical CPUs remain available. Run check.')

def check():
 p=policy();prerequisites(p);root=pathlib.Path('/sys/fs/cgroup/golden.slice');q,t=(root/'cpu.max').read_text().split()
 report={'status':'experimental-shared-aggregate','policy':p,'allCpuIds':sorted(os.sched_getaffinity(0)),'aggregateCpuMax':(root/'cpu.max').read_text().strip(),'aggregateCpuStat':(root/'cpu.stat').read_text(),'availableMiB':available(),'services':{},'accounts':{},'checksPass':True}
 report['checksPass'] &= q!='max' and abs(int(q)/int(t)*100-p['customerCpuPercent'])<.01
 report['aggregateMemoryMax']=(root/'memory.max').read_text().strip()
 report['aggregateSwapMax']=(root/'memory.swap.max').read_text().strip()
 report['checksPass'] &= report['aggregateMemoryMax']!='max' and int(report['aggregateMemoryMax'])==p.get('hostingMemoryMaxMiB',0)*1048576 and report['aggregateSwapMax']=='0'
 for unit in ['golden-shield.service','webuzo.service','golden-apache.service','mariadb.service']:
  row=properties(unit,['ActiveState','ControlGroup','MemoryLow','AllowedCPUs']);report['services'][unit]=row
  report['checksPass'] &= row['ActiveState']=='active'
  if unit in ['golden-apache.service','mariadb.service']:report['checksPass'] &= row['ControlGroup'].startswith('/golden.slice/')
  if unit=='webuzo.service':report['checksPass'] &= not row['ControlGroup'].startswith('/golden.slice/') and not row['AllowedCPUs']
 for native in account_units():
  uid=native.removesuffix('.slice');member=root/('golden-'+uid+'.slice');original=pathlib.Path('/sys/fs/cgroup')/native
  row={key:{'native':(original/key).read_text().strip(),'effective':(member/key).read_text().strip()} for key in ['cpu.max','memory.max','memory.high','pids.max','memory.swap.max','io.max']}
  report['accounts'][uid]=row
  report['checksPass'] &= all(v['native']==v['effective'] for v in row.values())
 # The kernel cap applies to contained processes only. Detect actual customer web workers outside it.
 outside=[]
 for d in pathlib.Path('/proc').iterdir():
  if not d.name.isdigit():continue
  try:
   exe=os.readlink(d/'exe');group=(d/'cgroup').read_text().strip()
   if exe=='/usr/local/apps/apache2/bin/httpd' or exe.startswith('/usr/local/apps/mariadb'):
    if not group.startswith('0::/golden.slice/'):outside.append({'pid':d.name,'exe':exe,'group':group})
   elif re.fullmatch(r'/usr/local/apps/php\d+/sbin/php-fpm',exe):
    if 'wpiso-health-' not in group and not group.startswith('0::/golden.slice/'):outside.append({'pid':d.name,'exe':exe,'group':group})
  except OSError:pass
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

def uninstall():
 if not (STATE/'installed.json').exists():raise RuntimeError('No installation snapshot found.')
 if pathlib.Path('/var/lib/webuzo-redis-guard/installed.json').exists():raise RuntimeError('Reset the optional Redis guard before Golden Shield: sudo python3 /usr/local/sbin/webuzo-redis-guard.py uninstall')
 data=files()
 for name,row in data.items():
  path=pathlib.Path(name)
  accepted={row['hash']}
  if row['backup']:accepted.add(hashlib.sha256(pathlib.Path(row['backup']).read_bytes()).hexdigest())
  if path.exists() and hashlib.sha256(path.read_bytes()).hexdigest() not in accepted:raise RuntimeError('Managed file changed; review before rollback: '+name)
 guard=pathlib.Path('/var/lib/webuzo-session-guard/files.json')
 if guard.exists():
  manager=pathlib.Path('/usr/local/sbin/webuzo-session-guard-manager.py')
  if not manager.is_file():raise RuntimeError('Uninstall the PAM session guard before removing Golden Shield.')
  command(['/usr/bin/python3',str(manager),'uninstall'])
 command(['systemctl','disable','--now','golden-shield.service'],False)
 command(['systemctl','disable','--now','golden-apache.service'],False)
 # Stop customer routing while restoring the original native placement implementation.
 versions=json.loads(pathlib.Path('/var/lib/webuzo-isolation/installed.json').read_text())['versions']
 for version in versions:command(['systemctl','stop','wpiso-manager-'+version+'.service'])
 command(['/usr/bin/python3',str(ISO),'native-cgroup-remove'])
 redis_managed=str(REDIS_CONFIG) in data
 if redis_managed:command(['systemctl','stop','redis.service'])
 for name,row in data.items():
  path=pathlib.Path(name)
  if row['backup']:
   atomic(path,pathlib.Path(row['backup']).read_text(),row['mode']);os.chown(path,row.get('uid',0),row.get('gid',0))
  else:path.unlink(missing_ok=True)
 # Shared-unit runtime properties disappear when their units are stopped below.
 props=STATE/'shared-properties.json'
 if props.exists():
  for unit,values in json.loads(props.read_text()).items():
   command(['systemctl','set-property','--runtime',unit]+[k+'='+('100' if v=='[not set]' else v) for k,v in values.items()])
 command(['systemctl','daemon-reload']);command(['systemctl','restart','mariadb.service'])
 command([str(APACHE),'start']);command(['systemctl','restart','cgroup.service'])
 if redis_managed:command(['systemctl','restart','redis.service'])
 # Switch routing before restart, but retain the installation marker until all
 # restoration steps finish so a failed uninstall cannot masquerade as removed.
 atomic(STATE/'disabling.json',json.dumps({'startedAt':time.time()}))
 for version in versions:restart_coordinator(version)
 command(['/usr/bin/python3',str(ISO),'reconcile'])
 for name in data:
  if re.fullmatch(r'/etc/systemd/system/golden-\d+\.slice',name):command(['systemctl','stop',pathlib.Path(name).name],False)
 command(['systemctl','stop','golden.slice'],False)
 (STATE/'installed.json').rename(STATE/('uninstalled-shared-'+str(time.time_ns())+'.json'))
 (STATE/'disabling.json').unlink(missing_ok=True)

 print('Shared Golden Shield removed. Native launchers, placement and recorded properties restored; verify HTTP and services.')

def main():
 if os.geteuid()!=0:raise RuntimeError('Run through sudo.')
 parser=argparse.ArgumentParser();parser.add_argument('action',choices=['install','resume','check','serve','uninstall','prepare-account','preflight','repair-native-ownership','apply-memory-cap','apply-shared-redis'],nargs='?',default='install');parser.add_argument('uid',nargs='?');parser.add_argument('--cache-only',action='store_true');args=parser.parse_args()
 if args.action=='install':install()
 elif args.action=='resume':resume_install()
 elif args.action=='preflight':p=effective_memory_cap(policy());prerequisites(p);print('New policy preflight passed.')
 elif args.action=='serve':serve()
 elif args.action=='prepare-account':prepare_account(args.uid or '')
 elif args.action=='uninstall':uninstall()
 elif args.action=='apply-memory-cap':apply_memory_cap()
 elif args.action=='apply-shared-redis':apply_shared_redis(args.uid,args.cache_only)
 elif args.action=='repair-native-ownership':repair_native_ownership()
 else:sys.exit(0 if check() else 1)
if __name__=='__main__':
 try:main()
 except Exception as e:print('GOLDEN SHIELD ERROR: '+str(e),file=sys.stderr);sys.exit(1)
