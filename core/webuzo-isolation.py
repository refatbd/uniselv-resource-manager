#!/usr/bin/python3
"""Experimental Webuzo FPM launcher integration. Root-only; never falls back to shared FPM."""
import argparse,contextlib,fcntl,hashlib,json,os,pathlib,pwd,re,shutil,signal,socket,subprocess,sys,time,select,struct,threading
BASE=pathlib.Path('/etc/webuzo-isolation')
STATE=pathlib.Path('/var/lib/webuzo-isolation')
RUN=pathlib.Path('/run/webuzo-isolation')
SELF=pathlib.Path('/usr/local/sbin/webuzo-isolation.py')
UNITS=pathlib.Path('/etc/systemd/system')
PROXY='/usr/lib/systemd/systemd-socket-proxyd'
MARKER='# WEBUZO-ISOLATION MANAGED LAUNCHER'

def execute(args,check=True,timeout=60):
    r=subprocess.run(args,capture_output=True,text=True,timeout=timeout)
    if check and r.returncode:raise RuntimeError('Command failed: '+str(args)+': exit='+str(r.returncode)+' '+r.stdout[-1200:]+r.stderr[-1200:])
    return r

def atomic(path,text,mode=0o600):
    path=pathlib.Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    if path.is_symlink():raise RuntimeError('Refusing symlink: '+str(path))
    temp=path.with_name(path.name+'.wpiso-new')
    if temp.exists() or temp.is_symlink():raise RuntimeError('Staging path exists: '+str(temp))
    with open(temp,'x',encoding='utf-8',newline='\n') as f:f.write(text)
    os.chmod(temp,mode);os.replace(temp,path)

@contextlib.contextmanager
def lock(name):
    RUN.mkdir(mode=0o755,exist_ok=True)
    with open(RUN/(name+'.lock'),'a') as f:
        fcntl.flock(f,fcntl.LOCK_EX);yield

def policy():
    data=json.loads((BASE/'policy.json').read_text())
    for key in ['maxActivePools','hostReserveMiB','poolBudgetMiB','phpBudgetMiB','workerRssMiB','opcacheMiB','idleSeconds']:
        if not isinstance(data.get(key),int) or data[key]<=0:raise ValueError('Invalid policy '+key)
    if data['opcacheMiB']>512 or data['maxActivePools']>64 or data['idleSeconds']<15:raise ValueError('Policy outside tested limits')
    return data

def versions():
    return sorted(p.name for p in pathlib.Path('/usr/local/apps').glob('php*') if re.fullmatch(r'php\d{2,3}',p.name) and (p/'sbin/php-fpm').is_file() and (p/'etc/php-fpm.conf').is_file())

def paths(version):
    if not re.fullmatch(r'php\d{2,3}',version):raise ValueError('Invalid PHP version')
    return pathlib.Path('/usr/local/apps')/version


def account_slice(uid):
    return 'golden-'+str(uid)+'.slice'

def account_cgroup(uid):
    return '/golden.slice/'+account_slice(uid)

def ensure_limits(user,uid):
    root=pathlib.Path('/sys/fs/cgroup')/(str(uid)+'.slice');unit=UNITS/(str(uid)+'.slice')
    if unit.exists() and not (root/'cpu.max').exists():execute(['systemctl','start',str(uid)+'.slice'])
    valid=unit.exists() and (root/'cpu.max').exists() and (root/'cpu.max').read_text().split()[0]!='max' and (root/'memory.max').read_text().strip()!='max'
    if not valid:
        # Webuzo rebuild-user was observed removing the native slice while retaining plan membership.
        # Reapply the assigned, unchanged native plan through Webuzo; never invent an unlimited slice.
        with lock('native-plan-repair'):
            response=json.loads(execute(['/bin/webuzo','--api','act=resource_limits']).stdout)
            matches=[(name,data) for name,data in response.get('resource_limits',{}).items() if user in data.get('users',[])]
            if len(matches)!=1:raise ValueError('Assign a native Resource Limit Plan first: '+user)
            name,data=matches[0]
            if not re.fullmatch(r'[A-Za-z0-9_-]{1,64}',name):raise ValueError('Unsupported native plan name')
            keys=['cpuquota','read_bw','write_bw','diskread','diskwrite','mem_max','memhigh','maxtask']
            if any(not str(data.get(k,'')).strip() for k in keys):raise ValueError('Blank/unlimited assigned plan is not accepted')
            command=['/bin/webuzo','--api','act=resource_limits','--save=1','--edit='+name,'--plan='+name]+['--'+k+'='+str(data[k]) for k in keys]
            result=json.loads(execute(command,timeout=90).stdout)
            if result.get('error') or not result.get('done'):raise RuntimeError('Native plan reapply failed: '+user)
            execute(['systemctl','daemon-reload']);execute(['systemctl','start',str(uid)+'.slice'])
    if not unit.exists() or not (root/'cpu.max').exists() or (root/'cpu.max').read_text().split()[0]=='max' or (root/'memory.max').read_text().strip()=='max':raise ValueError('Assigned native CPU/RAM limits are not active: '+user)
    execute(['systemctl','set-property',str(uid)+'.slice','MemorySwapMax=0'])
    execute(['/usr/bin/python3','/usr/local/sbin/golden-shield.py','prepare-account',str(uid)])
    return root

def parse_pools(text,version):
    prefix=paths(version);sections=list(re.finditer(r'^\[([^\]\r\n]+)\][ \t]*$',text,re.M));rows=[]
    global_match=re.search(r'^\[global\][ \t]*\n(.*?)(?=^\[|\Z)',text,re.M|re.S)
    global_settings=re.sub(r'^\s*(pid|error_log|daemonize)\s*=.*\n?', '', global_match[1] if global_match else '',flags=re.M)
    active=[x.strip() for x in text.splitlines() if x.strip() and not x.lstrip().startswith(';')]
    if any(re.match(r'include\s*=',x) for x in active):raise ValueError('External pool includes are not supported; refusing shared fallback')
    for i,m in enumerate(sections):
        name=m[1]
        if name=='global':continue
        part=text[m.start():sections[i+1].start() if i+1<len(sections) else len(text)]
        def field(key):
            found=re.findall(r'^\s*'+re.escape(key)+r'\s*=\s*([^;\r\n]+)',part,re.M)
            if len(found)!=1:raise ValueError('Expected one '+key+' for pool '+name)
            return found[0].strip().strip('"\'')
        user=field('user')
        if not re.fullmatch(r'[a-z_][a-z0-9_-]{0,31}',user):raise ValueError('Invalid pool username')
        account=pwd.getpwnam(user)
        if account.pw_uid<1000 or not (pathlib.Path('/var/webuzo/users')/user).exists():raise ValueError('Not an eligible Webuzo account: '+user)
        original=str(prefix/'var'/('fpm-'+user+'.sock'))
        if field('listen')!=original:raise ValueError('Nonstandard listen address for '+user)
        if any(r['user']==user for r in rows):raise ValueError('Multiple pools for same account/version need separate support')
        group=field('group');pwd.getpwnam(user)
        if group!=user:raise ValueError('Unexpected account group')
        for control in ['pm','pm.max_children','listen.backlog']:field(control)
        if field('pm')!='ondemand':raise ValueError('This integration currently requires global ondemand')
        ensure_limits(user,account.pw_uid)
        rows.append({'user':user,'uid':account.pw_uid,'name':name,'originalSocket':original,'pool':part,'global':global_settings,'maxChildren':int(field('pm.max_children')),'backlog':int(field('listen.backlog'))})
    return rows

def names(version,user):
    suffix=version+'-'+user
    return ('wpiso-fpm-'+suffix+'.service','wpiso-proxy-'+suffix+'.service','wpiso-proxy-'+suffix+'.socket')

def manifest(version):
    path=STATE/(version+'.json');return json.loads(path.read_text()) if path.exists() else {'pools':[]}

def assert_launcher(version):
    path=paths(version)/'bin/fpmctl'
    if path.is_symlink() or not path.is_file() or path.read_text()!=wrapper(version):raise RuntimeError('Managed launcher changed; stop and repair in maintenance: '+version)

def wrapper(version):
    return '#!/bin/sh\n'+MARKER+'\nexec /usr/bin/python3 '+str(SELF)+' action '+version+' "${1:-status}"\n'

def bridge(version):
    return '[Unit]\nDescription=Managed Webuzo isolated PHP service '+version+'\nAfter=wpiso-manager-'+version+'.service\n[Service]\nType=oneshot\nRemainAfterExit=yes\nExecStart=/usr/bin/python3 '+str(SELF)+' action '+version+' start\nExecStop=/usr/bin/python3 '+str(SELF)+' action '+version+' bridge-stop\nExecReload=/usr/bin/python3 '+str(SELF)+' action '+version+' reload\nTimeoutStartSec=120\nTimeoutStopSec=120\n[Install]\nWantedBy=multi-user.target\n'

def add_bridge(version):
    unit='php-fpm'+version[3:]+'.service';path=UNITS/unit
    if path.exists() and path.read_text()!=bridge(version):raise RuntimeError('Existing custom PHP unit needs manual integration: '+unit)
    atomic(path,bridge(version),0o644)
    wanted=UNITS/'multi-user.target.wants'/unit
    if wanted.is_symlink():
        if wanted.resolve()!=path:raise RuntimeError('Unexpected PHP enable link: '+unit)
    elif wanted.exists():raise RuntimeError('Unexpected PHP enable file: '+unit)
    else:wanted.symlink_to(path)
    execute(['systemctl','daemon-reload']);execute(['systemctl','start',unit])

def cleanup_workers(version,user,master,account_uid):
    if not master:return
    target=str((paths(version)/'sbin/php-fpm').resolve());matches=[]
    for d in pathlib.Path('/proc').iterdir():
        if not d.name.isdigit():continue
        try:
            status=(d/'status').read_text();parent=int(re.search(r'^PPid:\s*(\d+)',status,re.M)[1]);uid=int(re.search(r'^Uid:\s*(\d+)',status,re.M)[1])
            if parent==master and uid==account_uid and os.readlink(d/'exe')==target:matches.append((int(d.name),(d/'stat').read_text().rsplit(')',1)[1].split()[19]))
        except (FileNotFoundError,ProcessLookupError,PermissionError):pass
    return matches

def stop_pool(version,row,remove=False):
    fpm,proxy,sock=names(version,row['user'])
    main=execute(['systemctl','show',fpm,'-p','MainPID','--value'],False).stdout.strip()
    children=cleanup_workers(version,row['user'],int(main),row['uid']) if main.isdigit() else []
    execute(['systemctl','stop',sock,proxy,fpm],False,timeout=35)
    for pid,start in children or []:
        try:
            d=pathlib.Path('/proc')/str(pid)
            if (d/'stat').read_text().rsplit(')',1)[1].split()[19]==start:os.kill(pid,signal.SIGKILL)
        except (FileNotFoundError,ProcessLookupError):pass
    if remove:
        for name in (fpm,proxy,sock):(UNITS/name).unlink(missing_ok=True)

def pool_config(version,row):
    prefix=paths(version);backend=RUN/(version+'-'+row['user']+'.sock')
    part=re.sub(r'^(\s*listen\s*=).*$',r'\1 '+str(backend),row['pool'],flags=re.M)
    return '[global]\npid = '+str(RUN/(version+'-'+row['user']+'.pid'))+'\nerror_log = '+str(prefix/'var/log'/('wpiso-'+row['user']+'.log'))+'\n'+row['global']+'\n'+part

def write_pool(version,row,p):
    prefix=paths(version);user=row['user'];fpm,proxy,sock=names(version,user)
    backend=RUN/(version+'-'+user+'.sock');config=BASE/version/(user+'.conf')
    # Only routing changes; native PHP/FPM pool settings stay inherited.
    text=pool_config(version,row)
    atomic(config,text)
    execute([str(prefix/'sbin/php-fpm'),'-t','-y',str(config),'-c',str(prefix/'etc/php.ini'),'-d','opcache.memory_consumption='+str(p['opcacheMiB'])])
    unit='[Unit]\nDescription=Isolated Webuzo PHP pool '+version+' '+user+'\nStopWhenUnneeded=no\nRequires='+str(row['uid'])+'.slice\nAfter='+str(row['uid'])+'.slice\n[Service]\nType=simple\nSlice='+account_slice(row['uid'])+'\nWorkingDirectory='+str(prefix)+'\nExecStartPre=/usr/bin/python3 '+str(SELF)+' admit '+fpm+' '+str(row['maxChildren'])+'\nExecStart='+str(prefix/'sbin/php-fpm')+' -F -y '+str(config)+' -c '+str(prefix/'etc/php.ini')+' -d opcache.memory_consumption='+str(p['opcacheMiB'])+'\nExecStartPost=/usr/bin/python3 '+str(SELF)+' wait-socket '+str(backend)+'\nExecStopPost=/usr/bin/python3 '+str(SELF)+' release '+fpm+'\nKillSignal=SIGTERM\nTimeoutStartSec=45\nTimeoutStopSec=10\nRestart=no\n'
    atomic(UNITS/fpm,unit,0o644)
    unit='[Unit]\nDescription=Bounded FastCGI admission for '+version+' '+user+'\n[Service]\nSlice='+account_slice(row['uid'])+'\nType=simple\nExecStart=/usr/bin/python3 '+str(SELF)+' proxy '+fpm+' '+str(backend)+' '+str(p['idleSeconds'])+'\nMemoryMax=32M\nMemorySwapMax=0\nTasksMax=12\nTimeoutStopSec=5\n'
    atomic(UNITS/proxy,unit,0o644)
    unit='[Unit]\nDescription=Preserve native Webuzo socket for '+version+' '+user+'\n[Socket]\nListenStream='+row['originalSocket']+'\nSocketUser=nobody\nSocketGroup=nobody\nSocketMode=0660\nDirectoryMode=0755\nBacklog='+str(row['backlog'])+'\nRemoveOnStop=yes\nService='+proxy+'\n'
    atomic(UNITS/sock,unit,0o644)

def ensure_health(version):
    prefix=paths(version);conf=BASE/(version+'-health.conf');unit='wpiso-health-'+version+'.service'
    text='[global]\npid = /var/run/php-fpm'+version[3:]+'.pid\nerror_log = '+str(prefix/'var/log/wpiso-health.log')+'\n[private-health-only]\nuser = nobody\ngroup = nobody\nlisten = '+str(RUN/(version+'-health.sock'))+'\nlisten.owner = root\nlisten.group = root\nlisten.mode = 0600\npm = ondemand\npm.max_children = 1\npm.process_idle_timeout = 10\nrequest_terminate_timeout = 5\nphp_admin_value[memory_limit] = 32M\n'
    if not conf.exists() or conf.read_text()!=text:atomic(conf,text)
    text='[Unit]\nDescription=Private native PHP health master '+version+' (no customer pools)\nPartOf=wpiso-manager-'+version+'.service\n[Service]\nType=simple\nSlice=system.slice\nBindReadOnlyPaths='+str(conf)+':'+str(prefix/'etc/php-fpm.conf')+'\nExecStart='+str(prefix/'sbin/php-fpm')+' -F -y '+str(prefix/'etc/php-fpm.conf')+' -c '+str(prefix/'etc/php.ini')+' -d opcache.memory_consumption=16\nExecStartPost=/usr/bin/python3 '+str(SELF)+' wait-socket '+str(RUN/(version+'-health.sock'))+'\nCPUQuota=10%\nMemoryMax=96M\nMemoryHigh=80M\nMemorySwapMax=0\nTasksMax=16\nLimitNOFILE=128\nTimeoutStartSec=30\nTimeoutStopSec=10\nRestart=on-failure\nRestartSec=2\n'
    if not (UNITS/unit).exists() or (UNITS/unit).read_text()!=text:
        execute(['systemctl','stop',unit],False);atomic(UNITS/unit,text,0o644);execute(['systemctl','daemon-reload'])
    execute(['systemctl','start',unit])

def reconcile(version,restart=False):
    with lock(version):
        assert_launcher(version);p=policy();source=(paths(version)/'etc/php-fpm.conf').read_text();rows=parse_pools(source,version);old=manifest(version)
        # Validate all eligible pools before changing any running routing.
        for row in rows:
            staged=BASE/(version+'-'+row['user']+'-syntax.conf');atomic(staged,pool_config(version,row))
            try:execute([str(paths(version)/'sbin/php-fpm'),'-t','-y',str(staged),'-c',str(paths(version)/'etc/php.ini'),'-d','opcache.memory_consumption='+str(p['opcacheMiB'])])
            finally:staged.unlink(missing_ok=True)
        hashes={r['user']:hashlib.sha256((r['pool']+r['global']+str(r['uid'])+json.dumps(p,sort_keys=True)).encode()).hexdigest() for r in rows}
        for r in old['pools']:
            if restart or r['user'] not in hashes or r.get('hash')!=hashes.get(r['user']):stop_pool(version,r,r['user'] not in hashes)
        for row in rows:
            execute(['systemctl','set-property',str(row['uid'])+'.slice','MemorySwapMax=0'])
            if restart or not any(r['user']==row['user'] and r.get('hash')==hashes[row['user']] for r in old['pools']):write_pool(version,row,p)
            row['hash']=hashes[row['user']]
        execute(['systemctl','daemon-reload'])
        for row in rows:execute(['systemctl','start',names(version,row['user'])[2]])
        atomic(STATE/(version+'.json'),json.dumps({'sourceHash':hashlib.sha256(source.encode()).hexdigest(),'pools':[{k:r[k] for k in ['user','uid','name','originalSocket','maxChildren','hash']} for r in rows]},indent=2))
        return len(rows)

def notify(message):
    address=os.environ.get('NOTIFY_SOCKET')
    if address:
        if address.startswith('@'):address='\0'+address[1:]
        s=socket.socket(socket.AF_UNIX,socket.SOCK_DGRAM);s.sendto(message.encode(),address);s.close()

def supervise(version):
    alive=True;failed=False
    def end(*_):
        nonlocal alive;alive=False
    for sig in [signal.SIGTERM,signal.SIGINT,signal.SIGQUIT]:signal.signal(sig,end)
    count=reconcile(version,True);ensure_health(version);notify('READY=1\nSTATUS=Isolated sockets ready: '+str(count))
    last=manifest(version)['sourceHash']
    try:
        while alive:
            time.sleep(1)
            try:
                assert_launcher(version);digest=hashlib.sha256((paths(version)/'etc/php-fpm.conf').read_bytes()).hexdigest()
                limits_changed=any(pwd.getpwnam(r['user']).pw_uid!=r['uid'] or not (UNITS/(str(r['uid'])+'.slice')).exists() or not (pathlib.Path('/sys/fs/cgroup')/(str(r['uid'])+'.slice')/'cpu.max').exists() or (pathlib.Path('/sys/fs/cgroup')/(str(r['uid'])+'.slice')/'cpu.max').read_text().split()[0]=='max' or (pathlib.Path('/sys/fs/cgroup')/(str(r['uid'])+'.slice')/'memory.max').read_text().strip()=='max' for r in manifest(version)['pools'])
                if limits_changed:
                    for row in manifest(version)['pools']:stop_pool(version,row)
                if digest!=last or failed or limits_changed:
                    reconcile(version,failed);last=manifest(version)['sourceHash'];failed=False
            except Exception as e:
                if not failed:
                    print('Isolation reconcile error; maintenance required: '+str(e),file=sys.stderr,flush=True)
                    for row in manifest(version)['pools']:stop_pool(version,row)
                failed=True
                notify('STATUS=Fail closed: configuration or launcher invalid')
    finally:
        for row in manifest(version)['pools']:stop_pool(version,row)
        execute(['systemctl','stop','wpiso-health-'+version+'.service'],False)

def admit(unit,children):
    children=int(children)
    account=re.fullmatch(r'wpiso-fpm-(php\d{2,3})-([a-z_][a-z0-9_-]*)\.service',unit)
    if not account:raise ValueError('Invalid admission unit')
    actual_uid=pwd.getpwnam(account[2]).pw_uid
    if not (pathlib.Path('/proc/self/cgroup').read_text().strip()=='0::'+account_cgroup(actual_uid) or pathlib.Path('/proc/self/cgroup').read_text().strip().startswith('0::'+account_cgroup(actual_uid)+'/')):raise ValueError('Stale account UID routing; wait for coordinator reconciliation')
    ensure_limits(account[2],actual_uid)
    if children<1 or children>128:raise ValueError('Invalid worker count')
    if not re.fullmatch(r'wpiso-fpm-php\d{2,3}-[a-z_][a-z0-9_-]*\.service',unit):raise ValueError('Invalid admission unit')
    slots=RUN/'slots';slots.mkdir(mode=0o700,exist_ok=True);p=policy()
    deadline=time.monotonic()+3
    while True:
        with lock('admission'):
            lease=slots/unit
            if lease.exists():return
            available=int(next(x.split()[1] for x in pathlib.Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))//1024
            cost=children*p['workerRssMiB']+48+p['opcacheMiB']
            reserved=sum(json.loads(x.read_text())['costMiB'] for x in slots.iterdir())
            if len(list(slots.iterdir()))<p['maxActivePools'] and reserved+cost<=p['phpBudgetMiB'] and available>=p['hostReserveMiB']+cost:
                atomic(lease,json.dumps({'costMiB':cost,'startedAt':time.time()}));return
        if time.monotonic()>=deadline:raise RuntimeError('Host PHP admission budget full after bounded wait; no shared fallback')
        time.sleep(.25)

def fastcgi_proxy(unit,backend,idle):
    # Accept first; a rejected FPM start must produce an actual FastCGI 503,
    # not leave Apache waiting on an unconsumed socket backlog.
    if not re.fullmatch(r'wpiso-fpm-php\d{2,3}-[a-z_][a-z0-9_-]*\.service',unit):raise ValueError('Invalid backend')
    listener=socket.fromfd(3,socket.AF_UNIX,socket.SOCK_STREAM);listener.settimeout(1)
    slots=threading.BoundedSemaphore(8);lock=threading.Lock();activity={'last':time.monotonic(),'active':0}
    def unavailable(client):
        client.settimeout(2);header=b''
        while len(header)<8:
            chunk=client.recv(8-len(header))
            if not chunk:return
            header+=chunk
        version,kind,rid,length,padding,reserved=struct.unpack('!BBHHBB',header)
        if version!=1 or not rid:return
        content=b'Status: 503 Service Unavailable\r\nContent-Type: text/plain\r\nRetry-After: 5\r\n\r\nHosting PHP capacity is busy. Please retry shortly.\n'
        def record(kind,payload):return struct.pack('!BBHHBB',1,kind,rid,len(payload),0,0)+payload
        client.sendall(record(6,content)+record(6,b'')+record(3,b'\0'*8))
    def handle(client):
        try:
            with client:
                r=execute(['systemctl','start',unit],False,timeout=12)
                if r.returncode:unavailable(client);return
                with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as upstream:
                    upstream.settimeout(3)
                    try:upstream.connect(backend)
                    except OSError:unavailable(client);return
                    client.settimeout(5);upstream.settimeout(5);deadline=time.monotonic()+135
                    while time.monotonic()<deadline:
                        ready,_,_=select.select([client,upstream],[],[],1)
                        for source in ready:
                            data=source.recv(65536)
                            if not data:return
                            (upstream if source is client else client).sendall(data)
        except (OSError,subprocess.TimeoutExpired):pass
        finally:
            with lock:activity['active']-=1;activity['last']=time.monotonic()
            slots.release()
    try:
        while True:
            try:client,_=listener.accept()
            except socket.timeout:
                with lock:done=not activity['active'] and time.monotonic()-activity['last']>=int(idle)
                if done:return
                continue
            if not slots.acquire(False):
                try:unavailable(client)
                except OSError:pass
                client.close();continue
            with lock:activity['active']+=1;activity['last']=time.monotonic()
            threading.Thread(target=handle,args=(client,),daemon=True).start()
    finally:execute(['systemctl','stop',unit],False,timeout=20)

def release(unit):
    if not re.fullmatch(r'wpiso-fpm-php\d{2,3}-[a-z_][a-z0-9_-]*\.service',unit):raise ValueError('Invalid release unit')
    with lock('admission'):(RUN/'slots'/unit).unlink(missing_ok=True)

def action(version,command):
    unit='wpiso-manager-'+version+'.service';assert_launcher(version)
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

def install(policy_file):
    if STATE.exists() and (STATE/'installed.json').exists():raise RuntimeError('Already installed; use repair or uninstall, not overwrite backup')
    if not pathlib.Path(PROXY).is_file():raise RuntimeError('systemd-socket-proxyd missing')
    BASE.mkdir(mode=0o700,exist_ok=True);STATE.mkdir(mode=0o700,exist_ok=True)
    atomic(BASE/'policy.json',pathlib.Path(policy_file).read_text());policy();selected=versions()
    for version in selected:
        native_unit=UNITS/('php-fpm'+version[3:]+'.service')
        if native_unit.exists() or native_unit.is_symlink():raise RuntimeError('Existing custom PHP unit needs manual integration: '+version)
    for version in selected:parse_pools((paths(version)/'etc/php-fpm.conf').read_text(),version)
    backups=STATE/'original-launchers';backups.mkdir(mode=0o700,exist_ok=True)
    archive=STATE/('backup-'+str(time.time_ns()));archive.mkdir(mode=0o700)
    for version in selected:
        ctl=paths(version)/'bin/fpmctl'
        if ctl.is_symlink() or MARKER in ctl.read_text():raise RuntimeError('Unexpected launcher '+version)
        shutil.copy2(ctl,archive/version);shutil.copy2(ctl,backups/version)
    atomic(STATE/'installed.json',json.dumps({'versions':selected,'installedAt':time.time(),'nativeServiceEnablement':{v:execute(['systemctl','is-enabled','php-fpm'+v[3:]+'.service'],False).stdout.strip() for v in selected}}))
    if pathlib.Path(__file__).resolve()!=SELF:atomic(SELF,pathlib.Path(__file__).read_text(),0o755)
    for version in selected:
        ctl=paths(version)/'bin/fpmctl';r=execute([str(ctl),'stop'],False,timeout=45)
        # SIGQUIT completion can lag behind PID-file removal; wait for the actual executable.
        deadline=time.monotonic()+15
        while True:
            remaining=[]
            for d in pathlib.Path('/proc').iterdir():
                if not d.name.isdigit():continue
                try:
                    if os.readlink(d/'exe')==str(paths(version)/'sbin/php-fpm') and b'master process' in (d/'cmdline').read_bytes():remaining.append(d.name)
                except (FileNotFoundError,ProcessLookupError,PermissionError):pass
            if not remaining:break
            if time.monotonic()>deadline:raise RuntimeError('Native FPM master remains; complete maintenance stop first: '+version)
            time.sleep(.1)
        atomic(ctl,wrapper(version),0o755)
        unit='wpiso-manager-'+version+'.service'
        atomic(UNITS/unit,'[Unit]\nDescription=Experimental Webuzo isolation coordinator '+version+'\nAfter=network.target\n[Service]\nType=notify\nExecStart=/usr/bin/python3 '+str(SELF)+' supervise '+version+'\nTimeoutStartSec=60\nTimeoutStopSec=60\nRestart=on-failure\nRestartSec=2\n[Install]\nWantedBy=multi-user.target\n',0o644)
    execute(['systemctl','daemon-reload'])
    for version in selected:execute(['systemctl','enable','--now','wpiso-manager-'+version+'.service']);execute(['systemctl','reset-failed','php-fpm'+version[3:]+'.service'],False);add_bridge(version)
    print('Installed experimental isolation for '+', '.join(selected)+'. Run verify before releasing traffic.')

def verify():
    results={'mode':'experimental-custom-integration','policy':policy(),'versions':{},'mechanicalChecksPass':True}
    for version in json.loads((STATE/'installed.json').read_text())['versions']:
        try:
            assert_launcher(version);m=manifest(version);sourceHash=hashlib.sha256((paths(version)/'etc/php-fpm.conf').read_bytes()).hexdigest();results['mechanicalChecksPass']&=sourceHash==m.get('sourceHash');active=execute(['systemctl','is-active','wpiso-manager-'+version+'.service'],False).returncode==0
            status=execute(['systemctl','show','wpiso-manager-'+version+'.service','-p','StatusText','--value'],False).stdout.strip();results['mechanicalChecksPass']&=not status.startswith('Fail closed')
            rows=[]
            for row in m['pools']:
                fpm,proxy,sock=names(version,row['user']);root=pathlib.Path('/sys/fs/cgroup')/(str(row['uid'])+'.slice');socket_ok=execute(['systemctl','is-active',sock],False).returncode==0
                item={'user':row['user'],'uid':row['uid'],'socketActive':socket_ok,'fpmActive':execute(['systemctl','is-active',fpm],False).returncode==0,'fpmControlGroup':execute(['systemctl','show',fpm,'-p','ControlGroup','--value'],False).stdout.strip(),'swapMax':(root/'memory.swap.max').read_text().strip(),'cpuMax':(root/'cpu.max').read_text().strip(),'memoryMax':(root/'memory.max').read_text().strip()}
                results['mechanicalChecksPass']&=socket_ok and item['swapMax']=='0' and item['cpuMax'].split()[0]!='max' and item['memoryMax']!='max' and pwd.getpwnam(row['user']).pw_uid==row['uid'] and (not item['fpmActive'] or item['fpmControlGroup'].startswith(account_cgroup(row['uid'])+'/'));rows.append(item)
            health=execute(['systemctl','is-active','wpiso-health-'+version+'.service'],False).returncode==0
            native_unit=UNITS/('php-fpm'+version[3:]+'.service');bridge_ok=native_unit.exists() and native_unit.read_text()==bridge(version) and execute(['systemctl','is-active','php-fpm'+version[3:]+'.service'],False).returncode==0
            results['mechanicalChecksPass']&=active and bridge_ok and health;results['versions'][version]={'privateHealthMasterActive':health,'coordinatorActive':active,'nativeServiceBridgeActive':bridge_ok,'pools':rows}
        except Exception as e:results['mechanicalChecksPass']=False;results['versions'][version]={'error':str(e)}
    print(json.dumps(results,indent=2));return results['mechanicalChecksPass']

def uninstall():
    data=json.loads((STATE/'installed.json').read_text())
    for version in data['versions']:execute(['systemctl','disable','--now','wpiso-manager-'+version+'.service'],False,timeout=90)
    for version in data['versions']:
        unit='php-fpm'+version[3:]+'.service';path=UNITS/unit
        if path.exists() and path.read_text()==bridge(version):
            execute(['systemctl','stop',unit],False,timeout=90)
            wanted=UNITS/'multi-user.target.wants'/unit
            if wanted.is_symlink() and wanted.resolve()==path:wanted.unlink()
            path.unlink()
        execute(['systemctl','stop','wpiso-health-'+version+'.service'],False)
        (UNITS/('wpiso-health-'+version+'.service')).unlink(missing_ok=True)
        for row in manifest(version)['pools']:stop_pool(version,row,True)
        ctl=paths(version)/'bin/fpmctl'
        # Do not overwrite a changed vendor launcher after an update.
        if ctl.read_text()!=wrapper(version) and ctl.read_bytes()!=(STATE/'original-launchers'/version).read_bytes():raise RuntimeError('Launcher changed: manually review saved original before restoring '+version)
        shutil.copy2(STATE/'original-launchers'/version,ctl)
        (UNITS/('wpiso-manager-'+version+'.service')).unlink(missing_ok=True)
    execute(['systemctl','daemon-reload'])
    (STATE/'installed.json').rename(STATE/('uninstalled-'+str(time.time_ns())+'.json'))
    for version in data['versions']:
        already=False
        for d in pathlib.Path('/proc').iterdir():
            if not d.name.isdigit():continue
            try:
                if os.readlink(d/'exe')==str(paths(version)/'sbin/php-fpm') and b'master process' in (d/'cmdline').read_bytes():already=True
            except (FileNotFoundError,ProcessLookupError,PermissionError):pass
        if not already and parse_pools((paths(version)/'etc/php-fpm.conf').read_text(),version):execute([str(paths(version)/'bin/fpmctl'),'start'],timeout=45)
    for version in data['versions']:
        if data.get('nativeServiceEnablement',{}).get(version)=='disabled':execute(['systemctl','disable','php-fpm'+version[3:]+'.service'],False)
        execute(['systemctl','reset-failed','wpiso-manager-'+version+'.service','wpiso-health-'+version+'.service'],False)
    print('Native launchers restored. Native startup placement gap returns. PHP tuning and account swap properties were preserved.')

def main():
    if os.geteuid()!=0:raise PermissionError('Run through sudo or a privileged SSH terminal')
    parser=argparse.ArgumentParser();parser.add_argument('command');parser.add_argument('args',nargs='*');ns=parser.parse_args()
    if ns.command=='install':install(ns.args[0] if ns.args else str(pathlib.Path(__file__).parent/'policy.json'))
    elif ns.command=='action':action(*ns.args)
    elif ns.command=='supervise':supervise(ns.args[0])
    elif ns.command=='admit':admit(*ns.args)
    elif ns.command=='release':release(ns.args[0])
    elif ns.command=='proxy':fastcgi_proxy(*ns.args)
    elif ns.command=='verify':sys.exit(0 if verify() else 1)
    elif ns.command=='reconcile':
        for version in json.loads((STATE/'installed.json').read_text())['versions']:reconcile(version,True)
    elif ns.command=='wait-socket':
        path=pathlib.Path(ns.args[0]);deadline=time.monotonic()+8
        while not path.exists() and time.monotonic()<deadline:time.sleep(.05)
        if not path.exists():raise RuntimeError('Isolated backend socket not ready')
    elif ns.command=='uninstall':uninstall()
    else:raise ValueError('Unknown command')

if __name__=='__main__':
    try:main()
    except Exception as e:print('ISOLATION ERROR: '+str(e),file=sys.stderr);sys.exit(1)
