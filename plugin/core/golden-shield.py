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
 data=files();key=str(path)
 if key not in data:
  if path.exists():
   backup=STATE/'backups'/(hashlib.sha256(key.encode()).hexdigest()+'-'+str(time.time_ns()));atomic(backup,path.read_text(),path.stat().st_mode&0o777)
   data[key]={'backup':str(backup),'mode':path.stat().st_mode&0o777}
  else:data[key]={'backup':None,'mode':mode}
 elif path.exists() and hashlib.sha256(path.read_bytes()).hexdigest()!=data[key]['hash']:
  raise RuntimeError('Managed file changed; review before overwriting: '+key)
 atomic(path,text,mode);data[key]['hash']=hashlib.sha256(path.read_bytes()).hexdigest();atomic(STATE/'shared-files.json',json.dumps(data,indent=2))
def policy():
 p=json.loads((BASE/'policy.json').read_text())
 if p.get('mode')!='shared-aggregate-cpu':raise RuntimeError('Not a shared-mode policy; uninstall the previous mode before installing v2.')
 if not isinstance(p.get('headroomMiB'),int) or p['headroomMiB']<512:raise RuntimeError('Invalid memory policy.')
 if not 0<p['customerCpuPercent']<p['hostCpuCount']*100:raise RuntimeError('Invalid aggregate CPU budget.')
 return p
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
def prepare_account(uid):
 if not re.fullmatch(r'\d+',uid) or uid+'.slice' not in account_units():raise RuntimeError('Not a native account slice.')
 with open(STATE/'shared.lock','a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
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
 helper="\ndef account_slice(uid):\n    return 'golden-'+str(uid)+'.slice'\n\ndef account_cgroup(uid):\n    return '/golden.slice/'+account_slice(uid)\n\n"
 if 'def account_slice(' in source:raise RuntimeError('An existing slice integration needs manual review.')
 source=source.replace('def ensure_limits(user,uid):',helper+'def ensure_limits(user,uid):')
 anchor='    return root\n'
 if source.count(anchor)!=1:raise RuntimeError('Unsupported ensure_limits layout.')
 source=source.replace(anchor,"    execute(['/usr/bin/python3','/usr/local/sbin/golden-shield.py','prepare-account',str(uid)])\n"+anchor)
 source=source.replace("str(args[:3])+': '+r.stderr[-1200:]", "str(args)+': exit='+str(r.returncode)+' '+r.stdout[-1200:]+r.stderr[-1200:]")
 source=source.replace("Slice='+str(row['uid'])+'.slice\\n", "Slice='+account_slice(row['uid'])+'\\n")
 old="    if not (pathlib.Path('/proc/self/cgroup').read_text().strip()=='0::/'+str(actual_uid)+'.slice' or pathlib.Path('/proc/self/cgroup').read_text().strip().startswith('0::/'+str(actual_uid)+'.slice/')):"
 new="    if not (pathlib.Path('/proc/self/cgroup').read_text().strip()=='0::'+account_cgroup(actual_uid) or pathlib.Path('/proc/self/cgroup').read_text().strip().startswith('0::'+account_cgroup(actual_uid)+'/')):"
 if old not in source:raise RuntimeError('Unsupported admission layout.')
 source=source.replace(old,new)
 source=source.replace("startswith('/'+str(row['uid'])+'.slice/')", "startswith(account_cgroup(row['uid'])+'/')")
 # Socket proxies are hosting work too; keep them inside the same aggregate parent.
 compile(source,str(ISO),'exec');managed(ISO,source,0o755)
 scanner=SCANNER.read_text();needle='\t\t\t\techo $pid >>'
 if needle not in scanner:raise RuntimeError('Unsupported native process scanner.')
 scanner=scanner.replace(needle,"\t\t\t\t# Golden Shield: never move already-contained workers out of the aggregate group.\n\t\t\t\tgrep -q '/golden.slice/' /proc/$pid/cgroup 2>/dev/null && continue\n"+needle)
 managed(SCANNER,scanner,0o755)
def remember(unit,settings):
 path=STATE/'shared-properties.json';data=json.loads(path.read_text()) if path.exists() else {}
 if unit not in data:data[unit]=properties(unit,list(settings));atomic(path,json.dumps(data,indent=2))
 managed(UNITS/(unit+'.d')/'90-golden-shield.conf','[Slice]\n'+'\n'.join(k+'='+v for k,v in settings.items())+'\n' if unit.endswith('.slice') else '[Service]\n'+'\n'.join(k+'='+v for k,v in settings.items())+'\n')
 command(['systemctl','set-property','--runtime',unit]+[k+'='+v for k,v in settings.items()])
def apache_integration():
 # Preserve both native control entry points. The managed unit executes the saved original, avoiding recursion.
 if INIT.is_symlink() and INIT.resolve()!=APACHE.resolve():raise RuntimeError('Unsupported Apache init symlink target.')
 original=STATE/'apachectl.original'
 atomic(original,APACHE.read_text(),0o755)
 wrapper='#!/bin/sh\n# Golden Shield shared Apache launcher\ncase "${1:-}" in\n start|stop|restart|reload) exec /bin/systemctl "$1" golden-apache.service ;;\n graceful) exec /bin/systemctl reload golden-apache.service ;;\n graceful-stop) exec /bin/systemctl stop golden-apache.service ;;\n *) exec '+shlex.quote(str(original))+' "$@" ;;\nesac\n'
 command([str(APACHE),'configtest'])
 pidfile=pathlib.Path('/usr/local/apps/apache2/logs/httpd.pid')
 old=int(pidfile.read_text().strip()) if pidfile.exists() else None
 command([str(APACHE),'stop'])
 deadline=time.monotonic()+20
 while old and pathlib.Path('/proc',str(old)).exists():
  if time.monotonic()>deadline:raise RuntimeError('Old Apache master has not stopped; review before retrying.')
  time.sleep(.2)
 unit='[Unit]\nDescription=Golden Shield shared hosting Apache\nAfter=network.target\n[Service]\nType=forking\nSlice=golden.slice\nPIDFile=/usr/local/apps/apache2/logs/httpd.pid\nExecStart='+str(original)+' start\nExecStop='+str(original)+' graceful-stop\nExecReload='+str(original)+' graceful\nTimeoutStopSec=30\n[Install]\nWantedBy=multi-user.target\n'
 managed(UNITS/'golden-apache.service',unit);managed(APACHE,wrapper,0o755)
 if not INIT.is_symlink():managed(INIT,wrapper,0o755)
 command(['systemctl','daemon-reload']);command(['systemctl','enable','--now','golden-apache.service'])
def repair_native_ownership():
 # Do not let SysV PID guessing adopt the managed Apache master twice.
 bridge='[Unit]\nDescription=Webuzo Apache control bridge to Golden Shield\nWants=golden-apache.service\nAfter=golden-apache.service\n[Service]\nType=oneshot\nRemainAfterExit=yes\nExecStart=/bin/systemctl start golden-apache.service\nExecStop=/bin/systemctl stop golden-apache.service\nExecReload=/bin/systemctl reload golden-apache.service\n[Install]\nWantedBy=multi-user.target\n'
 managed(UNITS/'httpd.service',bridge,0o644)
 managed(UNITS/'webuzo-onboot.service.d'/'60-golden-ownership.conf','[Service]\nType=oneshot\nRemainAfterExit=yes\n',0o644)
 apache_unit=UNITS/'golden-apache.service'
 apache_text=apache_unit.read_text()
 if 'Wants=httpd.service\n' not in apache_text:
  managed(apache_unit,apache_text.replace('[Unit]\n','[Unit]\nWants=httpd.service\n',1))
 command(['systemctl','daemon-reload'])
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

def resume_install():
 if not (STATE/'installed.json').exists():raise RuntimeError('No partial installation to resume')
 prerequisites(policy());data=files()
 required=[str(ISO),str(SCANNER),str(APACHE),str(UNITS/'httpd.service'),str(UNITS/'mariadb.service.d'/'90-golden-shared.conf')]
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
 for name in ['shared-files.json','shared-properties.json']:
  if (STATE/name).exists():(STATE/name).rename(STATE/(name+'.previous-'+str(time.time_ns())))
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
 for name,row in data.items():
  path=pathlib.Path(name)
  if row['backup']:atomic(path,pathlib.Path(row['backup']).read_text(),row['mode'])
  else:path.unlink(missing_ok=True)
 # Shared-unit runtime properties disappear when their units are stopped below.
 props=STATE/'shared-properties.json'
 if props.exists():
  for unit,values in json.loads(props.read_text()).items():
   command(['systemctl','set-property','--runtime',unit]+[k+'='+('100' if v=='[not set]' else v) for k,v in values.items()])
 command(['systemctl','daemon-reload']);command(['systemctl','restart','mariadb.service'])
 command([str(APACHE),'start']);command(['systemctl','restart','cgroup.service'])
 for version in versions:restart_coordinator(version)
 command(['/usr/bin/python3',str(ISO),'reconcile'])
 for name in data:
  if re.fullmatch(r'/etc/systemd/system/golden-\d+\.slice',name):command(['systemctl','stop',pathlib.Path(name).name],False)
 command(['systemctl','stop','golden.slice'],False)
 (STATE/'installed.json').rename(STATE/('uninstalled-shared-'+str(time.time_ns())+'.json'))
 print('Shared Golden Shield removed. Native launchers, placement and recorded properties restored; verify HTTP and services.')

def main():
 if os.geteuid()!=0:raise RuntimeError('Run through sudo.')
 parser=argparse.ArgumentParser();parser.add_argument('action',choices=['install','resume','check','serve','uninstall','prepare-account','preflight','repair-native-ownership','apply-memory-cap'],nargs='?',default='install');parser.add_argument('uid',nargs='?');args=parser.parse_args()
 if args.action=='install':install()
 elif args.action=='resume':resume_install()
 elif args.action=='preflight':prerequisites(DEFAULT_POLICY);print('New policy preflight passed.')
 elif args.action=='serve':serve()
 elif args.action=='prepare-account':prepare_account(args.uid or '')
 elif args.action=='uninstall':uninstall()
 elif args.action=='apply-memory-cap':apply_memory_cap()
 elif args.action=='repair-native-ownership':repair_native_ownership()
 else:sys.exit(0 if check() else 1)
if __name__=='__main__':
 try:main()
 except Exception as e:print('GOLDEN SHIELD ERROR: '+str(e),file=sys.stderr);sys.exit(1)
