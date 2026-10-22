#!/usr/bin/python3
"""Experimental Webuzo FPM launcher integration. Root-only; never falls back to shared FPM."""
import queue
import argparse,contextlib,fcntl,hashlib,json,os,pathlib,pwd,re,shutil,signal,socket,subprocess,sys,time,select,struct,threading
BASE=pathlib.Path('/etc/webuzo-isolation')
STATE=pathlib.Path('/var/lib/webuzo-isolation')
RUN=pathlib.Path('/run/webuzo-isolation')
SELF=pathlib.Path('/usr/local/sbin/webuzo-isolation.py')
UNITS=pathlib.Path('/etc/systemd/system')
PROXY='/usr/lib/systemd/systemd-socket-proxyd'
MARKER='# WEBUZO-ISOLATION MANAGED LAUNCHER'
CAPACITY_MODEL_VERSION='account-demand-v4'

# Self-contained fallback: no PHP, external assets, scripts, or template file I/O.
CAPACITY_BUSY_HTML = b'<!doctype html>\n<html lang="en">\n<head>\n  <meta charset="utf-8">\n  <meta name="viewport" content="width=device-width, initial-scale=1">\n  <meta name="robots" content="noindex, nofollow">\n  <meta name="color-scheme" content="light">\n  <title>We\'ll be right with you | Temporarily unavailable</title>\n  <style>\n    *{box-sizing:border-box}html{min-height:100%;background:#faf9f7}body{margin:0;min-height:100svh;color:#25252b;font:16px/1.6 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;display:grid;place-items:center;padding:40px 24px;isolation:isolate;overflow-x:hidden}\n    .ambient{position:fixed;z-index:-1;inset:0;pointer-events:none;background:radial-gradient(ellipse at 82% 25%,#ffe9e7aa,transparent 48%),radial-gradient(ellipse at 8% 90%,#f3ebe480,transparent 40%)}.grid{position:fixed;z-index:-1;inset:0;pointer-events:none;background-image:radial-gradient(#c5b6b455 1px,transparent 1px);background-size:24px 24px;mask-image:linear-gradient(transparent,#0003,transparent)}\n    main{width:min(100%,1000px);animation:arrive .7s ease-out both}.brand{display:flex;align-items:center;gap:10px;font-size:11px;font-weight:700;letter-spacing:2px;margin:0 4px 24px;color:#6d6060}.brand svg{width:26px;height:26px}.brand span{letter-spacing:0;font-size:11px;font-weight:400;color:#7c7373;border-left:1px solid #ddd4d1;padding-left:15px;margin-left:6px}\n    .card{position:relative;display:grid;grid-template-columns:1.1fr 1fr;align-items:center;gap:30px;border:1px solid #ece6e3;border-radius:30px;background:#fff;padding:64px;box-shadow:0 30px 80px -40px #714c4930,0 3px 12px #493c3404;overflow:hidden}.card:before{content:"";position:absolute;top:0;left:12%;right:12%;height:2px;background:linear-gradient(90deg,transparent,#eb6c6355,transparent)}\n    .eyebrow{display:inline-flex;align-items:center;gap:8px;padding:5px 10px;border:1px solid #f5d8d5;border-radius:6px;background:#fff5f3;color:#b23d34;font-size:10px;font-weight:650;letter-spacing:1.4px;text-transform:uppercase}.dot{width:5px;height:5px;border-radius:50%;background:#d9564c;box-shadow:0 0 0 3px #d9564c12;animation:pulse 2.5s ease-in-out infinite}h1{font-size:clamp(36px,4.5vw,50px);font-weight:650;letter-spacing:-2.2px;line-height:1.12;margin:25px 0 20px}h1 span{color:#7e7778;font-weight:450}.description{color:#706b70;font-size:14px;line-height:1.8;max-width:340px;margin:0 0 28px}.retry{display:inline-flex;align-items:center;justify-content:center;gap:10px;padding:12px 21px;min-height:48px;border:1px solid #bd4037;border-radius:10px;background:#c3463c;color:#fff;font-size:13px;font-weight:650;text-decoration:none;box-shadow:0 4px 10px #bd403718;transition:background .2s,transform .2s,box-shadow .2s}.retry:hover{background:#a9362e;transform:translateY(-2px);box-shadow:0 8px 20px #bd403728}.retry:focus-visible{outline:3px solid #df8e87;outline-offset:4px}.retry svg{width:16px;height:16px}.hint{display:block;font-size:11px;color:#817878;margin-top:13px}\n    .visual{position:relative;height:340px;display:grid;place-items:center}.halo{position:absolute;width:310px;height:310px;border-radius:50%;background:radial-gradient(circle,#fff1ef,transparent 70%)}.error-number{position:absolute;top:8px;font-size:112px;font-weight:750;letter-spacing:-8px;line-height:1;color:#f8e9e6;user-select:none}.orbit{position:absolute;width:266px;height:266px;border:1px solid #f2ded9;border-radius:50%}.orbit.inner{width:206px;height:206px;border-style:dashed;border-color:#ecd3cd}.satellite{position:absolute;inset:-1px;border-radius:50%;animation:orbit 22s linear infinite}.satellite:before{content:"";position:absolute;top:-4px;left:50%;width:8px;height:8px;background:#df7d72;border:2px solid white;border-radius:50%;box-shadow:0 0 0 4px #f9e6e2}.core{position:relative;width:118px;height:118px;display:grid;place-items:center;border:1px solid #f4d2cc;border-radius:30px;background:linear-gradient(145deg,#fff9f7,#fdeae5);box-shadow:inset 0 2px #fff,0 18px 35px -20px #c8736777;transform:rotate(-8deg);animation:float 6s ease-in-out infinite}.core svg{width:53px;height:53px;color:#c44e42;transform:rotate(8deg)}.alert-badge{position:absolute;right:-10px;top:-10px;width:34px;height:34px;display:grid;place-items:center;border:4px solid white;border-radius:50%;background:#cd5146;color:white;font-size:17px;font-weight:700;line-height:1;box-shadow:0 3px 8px #bf635522}.status{position:absolute;bottom:4px;display:flex;align-items:center;gap:9px;padding:9px 14px;background:#fff;border:1px solid #eee2dd;border-radius:30px;color:#88736e;font-size:10px;box-shadow:0 5px 15px #95605208}.bars{display:flex;gap:3px;align-items:center;height:15px}.bars i{width:3px;height:5px;background:#d9786d;border-radius:2px;animation:bars 1.4s ease-in-out infinite}.bars i:nth-child(2){animation-delay:.15s}.bars i:nth-child(3){animation-delay:.3s}.small-cross{position:absolute;top:70px;right:22px;color:#d49c92;font-size:18px}.code{position:absolute;left:9px;bottom:50px;color:#b1877e;font:9px ui-monospace,monospace;letter-spacing:1.5px}\n    footer{display:flex;justify-content:space-between;align-items:center;gap:20px;margin:22px 4px 0;color:#8b8180;font-size:10px}.foot-status{display:flex;align-items:center;gap:7px}.foot-status:before{content:"";width:5px;height:5px;background:#d17a70;border-radius:50%}\n    @keyframes arrive{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}@keyframes orbit{to{transform:rotate(360deg)}}@keyframes float{50%{transform:translateY(-9px) rotate(-4deg)}}@keyframes pulse{50%{opacity:.45}}@keyframes bars{50%{height:14px}}\n    @media(max-width:700px){body{padding:28px 18px}.brand{margin-bottom:20px;font-size:10px;letter-spacing:1.5px}.brand span{display:none}.card{grid-template-columns:1fr;padding:30px 26px;gap:24px;border-radius:24px}.visual{grid-row:1;height:240px}.orbit{width:200px;height:200px}.orbit.inner{width:154px;height:154px}.error-number{top:0;font-size:88px}.core{width:94px;height:94px;border-radius:24px}.core svg{width:43px;height:43px}.status{bottom:-7px;font-size:9px}.small-cross{top:38px;right:20px}.code{left:0;bottom:26px;font-size:8px}h1{font-size:38px;letter-spacing:-1.8px;margin-top:20px}.description{max-width:100%;font-size:13px}.hint{font-size:10px}footer{align-items:flex-start;font-size:9px;gap:14px}.foot-status{max-width:145px}}\n    @media(prefers-reduced-motion:reduce){*,*:before,*:after{animation:none!important;transition:none!important}}\n  </style>\n</head>\n<body>\n  <div class="ambient" aria-hidden="true"></div><div class="grid" aria-hidden="true"></div>\n  <main>\n    <div class="brand"><svg viewBox="0 0 32 32" fill="none" aria-hidden="true"><rect x="5" y="5" width="22" height="22" rx="8" stroke="#b76b62" stroke-width="1.5"/><path d="M13 12v8m6-8v8" stroke="#b76b62" stroke-width="2.5" stroke-linecap="round"/></svg>A MOMENT, PLEASE<span>We appreciate your patience.</span></div>\n    <section class="card" aria-labelledby="title">\n      <div class="copy">\n        <div class="eyebrow"><span class="dot" aria-hidden="true"></span>Temporarily at capacity</div>\n        <h1 id="title">A little pause.<br><span>We\'ll be right<br>with you.</span></h1>\n        <p class="description">We\'re experiencing high demand right now. Please give us a moment, then try this page again.</p>\n        <a class="retry" href=""><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 7v5h-5M4.5 9a8 8 0 0113.2-3L20 9M4 17v-5h5m10.5 3a8 8 0 01-13.2 3L4 15"/></svg>Try Again</a>\n        <small class="hint">Wait a few seconds before trying again.</small>\n      </div>\n      <div class="visual" aria-hidden="true"><div class="halo"></div><span class="error-number">503</span><div class="orbit"><div class="satellite"></div></div><div class="orbit inner"></div><span class="small-cross">+</span><div class="core"><span class="alert-badge">!</span><svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="12" y="12" width="40" height="16" rx="5"/><rect x="12" y="36" width="40" height="16" rx="5"/><path d="M20 20h1m-1 24h1m17-24h6m-6 24h6M32 28v8"/></svg></div><span class="code">PLEASE STAND BY</span><div class="status"><span class="bars"><i></i><i></i><i></i></span>A moment to catch our breath.</div></div>\n    </section>\n    <footer><span>Thank you for your patience.</span><span class="foot-status">503 &middot; Service temporarily unavailable</span></footer>\n  </main>\n</body>\n</html>\n'

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
    for key in ['maxActivePools','hostReserveMiB','poolBudgetMiB','phpBudgetMiB','workerRssMiB','idleSeconds']:
        if not isinstance(data.get(key),int) or data[key]<=0:raise ValueError('Invalid policy '+key)
    if type(data.get('opcacheMiB')) is not int or data['opcacheMiB']<0:raise ValueError('Invalid opcacheMiB')
    if data['opcacheMiB']>512 or data['maxActivePools']>64 or data['idleSeconds']<15:raise ValueError('Policy outside tested limits')
    if type(data.get('accountRuntimeCaps',False)) is not bool:raise ValueError('Invalid accountRuntimeCaps')
    return data

def versions():
    return sorted(p.name for p in pathlib.Path('/usr/local/apps').glob('php*') if re.fullmatch(r'php\d{2,3}',p.name) and (p/'sbin/php-fpm').is_file() and (p/'etc/php-fpm.conf').is_file())

def paths(version):
    if not re.fullmatch(r'php\d{2,3}',version):raise ValueError('Invalid PHP version')
    return pathlib.Path('/usr/local/apps')/version


def account_slice(uid):
    return ('golden-' if (pathlib.Path('/var/lib/golden-shield/installed.json').exists() and not pathlib.Path('/var/lib/golden-shield/disabling.json').exists()) else '')+str(uid)+'.slice'

def account_cgroup(uid):
    return ('/golden.slice/' if (pathlib.Path('/var/lib/golden-shield/installed.json').exists() and not pathlib.Path('/var/lib/golden-shield/disabling.json').exists()) else '/')+account_slice(uid)

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
    if (pathlib.Path('/var/lib/golden-shield/installed.json').exists() and not pathlib.Path('/var/lib/golden-shield/disabling.json').exists()):
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
            # PHP-FPM uses 511 on Linux when listen.backlog is omitted.
            if key=='listen.backlog' and not found:return '511'
            if len(found)!=1:raise ValueError('Expected one '+key+' for pool '+name)
            return found[0].strip().strip('"\'')
        user=field('user')
        if not re.fullmatch(r'[a-z_][a-z0-9_-]{0,31}',user):raise ValueError('Invalid pool username')
        try:
            account=pwd.getpwnam(user)
        except KeyError:
            # Native deletion can remove passwd/userdata before regenerating FPM.
            # Quarantine this dead, standard-shaped pool, never route it through
            # another UID or stop unrelated accounts while the vendor catches up.
            expected=str(prefix/'var'/('fpm-'+user+'.sock'))
            if (pathlib.Path('/var/webuzo/users')/user).exists() or field('group')!=user or field('listen')!=expected:
                raise ValueError('Missing account with nonstandard native pool: '+user)
            print('Ignoring native pool pending deleted-account regeneration: '+version+' '+user,file=sys.stderr,flush=True)
            continue
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

def validate_fpm(args):
    # Native maintenance can terminate a concurrent syntax-only PHP process.
    # Retry that signal only; syntax errors and admission/start failures fail closed.
    for attempt in range(3):
        result=execute(args,check=False)
        if result.returncode==0:return result
        if result.returncode!=-15 or attempt==2:raise RuntimeError('PHP syntax verification failed: '+str(args)+': exit='+str(result.returncode)+' '+result.stdout[-1200:]+result.stderr[-1200:])
        time.sleep(.5)

def pool_config(version,row):
    prefix=paths(version);backend=RUN/(version+'-'+row['user']+'.sock')
    part=re.sub(r'^(\s*listen\s*=).*$',r'\1 '+str(backend),row['pool'],flags=re.M)
    return '[global]\npid = '+str(RUN/(version+'-'+row['user']+'.pid'))+'\nerror_log = '+str(prefix/'var/log'/('wpiso-'+row['user']+'.log'))+'\n'+row['global']+'\n'+part

def request_seconds(pool, fallback=120):
    values=re.findall(r'^\s*request_terminate_timeout\s*=\s*(\d+)\s*([smhd]?)\s*(?:;.*)?$',pool,re.M)
    if len(values)>1:raise ValueError('Duplicate native request_terminate_timeout')
    if not values:return int(fallback)
    value,unit=values[0];seconds=int(value)*{'':1,'s':1,'m':60,'h':3600,'d':86400}[unit]
    return seconds or int(fallback)


def proxy_limits(children, backlog, request_timeout):
    """Inherit native pool capacity. Queued sockets do not create threads or PHP workers."""
    children,backlog,request_timeout=int(children),int(backlog),int(request_timeout)
    if not 1<=children<=128:raise ValueError('Unsupported native worker count')
    if not 1<=backlog<=65535:raise ValueError('Use a finite native listen.backlog from 1 to 65535')
    if not 1<=request_timeout<=86400:raise ValueError('Request timeout must be finite, from 1 to 86400 seconds')
    # Interpreter baseline + per-relay working buffers + bounded queued socket metadata.
    memory=24+children*2+(backlog+100)//100
    budget=max(1,request_timeout-max(1,(request_timeout+19)//20))
    return {'workers':children,'queue':backlog,'timeout':budget,
            'tasks':children+4,'memoryMiB':memory,'fileLimit':2*children+backlog+32}


def account_worker_ceiling(native_children, memory_max, memory_high, tasks_max, p, backlog, timeout):
    """Automatic runtime exception; native global Webuzo settings are never edited here."""
    ceiling=int(native_children)
    if not p.get('accountRuntimeCaps',False):return ceiling
    # A finite account hard boundary is mandatory; optional high/task maxima inherit it.
    allowance=int(memory_max)*.9
    if str(memory_high)!='max':allowance=min(allowance,int(memory_high))
    if str(tasks_max)!='max':ceiling=min(ceiling,max(0,(int(tasks_max)-8)//2))
    while ceiling>0:
        relay=proxy_limits(ceiling,backlog,timeout)
        if ceiling*p['workerRssMiB']+48+p['opcacheMiB']+relay['memoryMiB']<=allowance/1048576:return ceiling
        ceiling-=1
    raise ValueError('Native account memory/task limits cannot fit one planned PHP worker')


def runtime_ceiling(uid,native_children,p,backlog,timeout):
    if not p.get('accountRuntimeCaps',False):return int(native_children)
    group=pathlib.Path('/sys/fs/cgroup'+account_cgroup(uid))
    return account_worker_ceiling(native_children,(group/'memory.max').read_text().strip(),
        (group/'memory.high').read_text().strip(),(group/'pids.max').read_text().strip(),p,backlog,timeout)


def runtime_pool(pool,children):
    if len(re.findall(r'^\s*pm\.max_children\s*=',pool,re.M))!=1:raise ValueError('Expected one native max_children directive')
    return re.sub(r'^(\s*pm\.max_children\s*=).*$',r'\g<1> '+str(children),pool,flags=re.M)


def demand_grant(ceiling,relay_memory,p,reserved,available,account_available=None):
    """Borrow only unreserved shared PHP capacity; account count is deliberately not an input."""
    overhead=48+p['opcacheMiB']+relay_memory
    allowance=min(p['phpBudgetMiB']-reserved,available-p['hostReserveMiB'])
    if account_available is not None:allowance=min(allowance,account_available)
    children=min(ceiling,int((allowance-overhead)//p['workerRssMiB']))
    return (children,children*p['workerRssMiB']+overhead) if children>=1 else (0,0)


def waiting_units(exclude=None):
    """Root-written, short-lived admission demand; registered accounts never count."""
    result=set();directory=RUN/'waiting'
    if not directory.exists():return result
    for path in directory.iterdir():
        if path.name==exclude or not re.fullmatch(r'wpiso-fpm-php\d{2,3}-[a-z_][a-z0-9_-]*\.service',path.name):continue
        try:
            row=json.loads(path.read_text())
            if type(row.get('expires')) in (int,float) and time.monotonic()<row['expires']<float('inf'):result.add(path.name)
        except (OSError,ValueError,TypeError):continue
    return result


def contention_ceiling(ceiling,relay_memory,p,pool_count):
    """Share a pressured cold grant; final admission still charges complete leases."""
    overhead=48+p['opcacheMiB']+relay_memory
    fair=int((p['phpBudgetMiB']/max(1,pool_count)-overhead)//p['workerRssMiB'])
    return min(ceiling,max(1,fair))


def account_memory_usage(current,stat_text):
    """Admission estimate, not a replacement for kernel memory.current/limits.

    Only clean inactive file cache can be reclaimed for a new lease. Keep active
    file cache, anonymous memory, dirty/writeback pages and all kernel charges.
    Missing or malformed counters retain the original conservative accounting.
    """
    if type(current) is not int or current<0:raise ValueError('Invalid account memory.current')
    required={'file','inactive_file','file_dirty','file_writeback'};values={}
    for line in stat_text.splitlines():
        row=line.split()
        if not row or row[0] not in required:continue
        if len(row)!=2 or row[0] in values or not row[1].isdigit():return current,0,current
        values[row[0]]=int(row[1])
    if set(values)!=required:return current,0,current
    if values['inactive_file']>values['file'] or values['file']>current:return current,0,current
    reclaimable=max(0,min(current,values['file'],values['inactive_file'])-values['file_dirty']-values['file_writeback'])
    return current,reclaimable,current-reclaimable


def write_pool(version,row,p):
    prefix=paths(version);user=row['user'];fpm,proxy,sock=names(version,user)
    backend=RUN/(version+'-'+user+'.sock');config=BASE/version/(user+'.conf')
    timeout=request_seconds(row['pool'],p.get('requestTimeoutSeconds',120))
    ceiling=runtime_ceiling(row['uid'],row['maxChildren'],p,row['backlog'],timeout)
    limits=proxy_limits(ceiling,row['backlog'],timeout)
    # Native global source stays inherited; optional runtime ceiling affects only this private copy.
    text=pool_config(version,row)
    if p.get('accountRuntimeCaps',False):text=runtime_pool(text,ceiling)
    atomic(config,text)
    validate_fpm([str(prefix/'sbin/php-fpm'),'-t','-y',str(config),'-c',str(prefix/'etc/php.ini'),'-d','opcache.memory_consumption='+str(p['opcacheMiB'])])
    unit='[Unit]\nDescription=Isolated Webuzo PHP pool '+version+' '+user+'\nStopWhenUnneeded=no\nRequires='+str(row['uid'])+'.slice\nAfter='+str(row['uid'])+'.slice\n[Service]\nType=simple\nSlice='+account_slice(row['uid'])+'\nWorkingDirectory='+str(prefix)+'\nExecStartPre=/usr/bin/python3 '+str(SELF)+' admit '+fpm+' '+str(row['maxChildren'])+'\nExecStart='+str(prefix/'sbin/php-fpm')+' -F -y '+str(config)+' -c '+str(prefix/'etc/php.ini')+' -d opcache.memory_consumption='+str(p['opcacheMiB'])+'\nExecStartPost=/usr/bin/python3 '+str(SELF)+' wait-socket '+str(backend)+'\nExecStopPost=/usr/bin/python3 '+str(SELF)+' release '+fpm+'\nKillSignal=SIGTERM\nTimeoutStartSec=45\nTimeoutStopSec=10\nRestart=no\n'
    atomic(UNITS/fpm,unit,0o644)
    unit='[Unit]\nDescription=Bounded FastCGI admission for '+version+' '+user+'\n[Service]\nSlice='+account_slice(row['uid'])+'\nType=simple\nExecStart=/usr/bin/python3 '+str(SELF)+' proxy '+fpm+' '+str(backend)+' '+str(p['idleSeconds'])+' '+str(limits['workers'])+' '+str(limits['queue'])+' '+str(limits['timeout'])+'\nMemoryMax='+str(limits['memoryMiB'])+'M\nMemorySwapMax=0\nTasksMax='+str(limits['tasks'])+'\nLimitNOFILE='+str(limits['fileLimit'])+'\nExecStopPost=/usr/bin/systemctl stop '+fpm+'\nTimeoutStopSec=20\n'
    atomic(UNITS/proxy,unit,0o644)
    unit='[Unit]\nDescription=Preserve native Webuzo socket for '+version+' '+user+'\n[Socket]\nListenStream='+row['originalSocket']+'\nSocketUser=nobody\nSocketGroup=nobody\nSocketMode=0660\nDirectoryMode=0755\nBacklog='+str(row['backlog'])+'\nRemoveOnStop=yes\nService='+proxy+'\n'
    atomic(UNITS/sock,unit,0o644)

def ensure_health(version):
    prefix=paths(version);conf=BASE/(version+'-health.conf');unit='wpiso-health-'+version+'.service'
    text='[global]\npid = /var/run/php-fpm'+version[3:]+'.pid\nerror_log = '+str(prefix/'var/log/wpiso-health.log')+'\n[private-health-only]\nuser = nobody\ngroup = nobody\nlisten = '+str(RUN/(version+'-health.sock'))+'\nlisten.owner = root\nlisten.group = root\nlisten.mode = 0600\npm = ondemand\npm.max_children = 1\npm.process_idle_timeout = 10\nrequest_terminate_timeout = 5\nphp_admin_value[memory_limit] = 32M\n'
    if not conf.exists() or conf.read_text()!=text:atomic(conf,text)
    text='[Unit]\nDescription=Private native PHP health master '+version+' (no customer pools)\nPartOf=wpiso-manager-'+version+'.service\n[Service]\nType=simple\nSlice=system.slice\nBindReadOnlyPaths='+str(conf)+':'+str(prefix/'etc/php-fpm.conf')+'\nExecStart='+str(prefix/'sbin/php-fpm')+' -F -y '+str(prefix/'etc/php-fpm.conf')+' -c '+str(prefix/'etc/php.ini')+' -d opcache.memory_consumption=16 -d opcache.interned_strings_buffer=4\nExecStartPost=/usr/bin/python3 '+str(SELF)+' wait-socket '+str(RUN/(version+'-health.sock'))+'\nCPUQuota=10%\nMemoryMax=96M\nMemoryHigh=80M\nMemorySwapMax=0\nTasksMax=16\nLimitNOFILE=128\nTimeoutStartSec=30\nTimeoutStopSec=10\nRestart=on-failure\nRestartSec=2\n'
    if not (UNITS/unit).exists() or (UNITS/unit).read_text()!=text:
        execute(['systemctl','stop',unit],False);atomic(UNITS/unit,text,0o644);execute(['systemctl','daemon-reload'])
    execute(['systemctl','start',unit])

def reconcile(version,restart=False):
    with lock(version):
        assert_launcher(version);p=policy();source=(paths(version)/'etc/php-fpm.conf').read_text();rows=parse_pools(source,version);old=manifest(version)
        # Validate all eligible pools before changing any running routing.
        for row in rows:
            staged=BASE/(version+'-'+row['user']+'-syntax.conf');atomic(staged,pool_config(version,row))
            try:validate_fpm([str(paths(version)/'sbin/php-fpm'),'-t','-y',str(staged),'-c',str(paths(version)/'etc/php.ini'),'-d','opcache.memory_consumption='+str(p['opcacheMiB'])])
            finally:staged.unlink(missing_ok=True)
        hashes={r['user']:hashlib.sha256((r['pool']+r['global']+str(r['uid'])+json.dumps(p,sort_keys=True)+CAPACITY_MODEL_VERSION).encode()).hexdigest() for r in rows}
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
                limits_changed=False if digest!=last else any(pwd.getpwnam(r['user']).pw_uid!=r['uid'] or not (UNITS/(str(r['uid'])+'.slice')).exists() or not (pathlib.Path('/sys/fs/cgroup')/(str(r['uid'])+'.slice')/'cpu.max').exists() or (pathlib.Path('/sys/fs/cgroup')/(str(r['uid'])+'.slice')/'cpu.max').read_text().split()[0]=='max' or (pathlib.Path('/sys/fs/cgroup')/(str(r['uid'])+'.slice')/'memory.max').read_text().strip()=='max' for r in manifest(version)['pools'])
                if limits_changed:
                    for row in manifest(version)['pools']:stop_pool(version,row)
                if digest!=last or failed or limits_changed:
                    count=reconcile(version,failed);last=manifest(version)['sourceHash'];failed=False;notify('STATUS=Isolated sockets ready: '+str(count))
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
    waiting=RUN/'waiting';waiting.mkdir(mode=0o700,exist_ok=True);ticket=waiting/unit
    grant_ceiling=children
    try:
        while True:
            with lock('admission'):
                lease=slots/unit
                if lease.exists():return
                available=int(next(x.split()[1] for x in pathlib.Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))//1024
                pool_path=BASE/account[1]/(account[2]+'.conf')
                pool=pool_path.read_text()
                value=re.search(r'^\s*listen.backlog\s*=\s*(\d+)',pool,re.M)
                backlog=int(value[1]) if value else 511
                timeout=request_seconds(pool,p.get('requestTimeoutSeconds',120))
                ceiling=runtime_ceiling(actual_uid,children,p,backlog,timeout)
                # Reserve the native relay upper bound even if a plan changed since unit generation.
                relay=proxy_limits(children,backlog,timeout)
                lease_paths=list(slots.iterdir());leases=[json.loads(x.read_text()) for x in lease_paths]
                reserved=sum(x['costMiB'] for x in leases)
                dynamic=p.get('accountRuntimeCaps',False)
                account_available=None
                accounting={}
                if dynamic:
                    group=pathlib.Path('/sys/fs/cgroup'+account_cgroup(actual_uid))
                    boundary=int((group/'memory.max').read_text())*.9/1048576
                    high=(group/'memory.high').read_text().strip()
                    if high!='max':boundary=min(boundary,int(high)/1048576)
                    account_reserved=sum(x['costMiB'] for x in leases if x.get('uid')==actual_uid)
                    current=int((group/'memory.current').read_text())
                    try:stat_text=(group/'memory.stat').read_text()
                    except OSError:stat_text=''
                    current,reclaimable,working=account_memory_usage(current,stat_text)
                    account_available=boundary-max(account_reserved,working/1048576)
                    accounting={'accountMemoryMiB':round(current/1048576,2),
                        'accountCleanInactiveFileMiB':round(reclaimable/1048576,2),
                        'accountWorkingSetMiB':round(working/1048576,2),
                        'accountMemoryAccounting':'clean-inactive-file-v1'}
                granted,cost=demand_grant(min(ceiling,grant_ceiling),relay['memoryMiB'],p,reserved,available,account_available)
                eligible=granted>=1 if dynamic else (granted==children and len(list(slots.iterdir()))<p['maxActivePools'])
                if eligible:
                    if dynamic:atomic(pool_path,runtime_pool(pool,granted))
                    atomic(lease,json.dumps({'costMiB':cost,'startedAt':time.time(),
                        'nativeMaxChildren':children,'accountCeiling':ceiling,'runtimeMaxChildren':granted,
                        'contentionCeiling':min(ceiling,grant_ceiling),'uid':actual_uid,'mode':'account-aware' if dynamic else 'global-default',**accounting}));return
                # Do not recycle other accounts for this account's own RAM shortage.
                minimum=p['workerRssMiB']+48+p['opcacheMiB']+relay['memoryMiB']
                if dynamic and account_available>=minimum:
                    peers={x.name for x in lease_paths}|waiting_units()|{unit}
                    grant_ceiling=min(grant_ceiling,contention_ceiling(ceiling,relay['memoryMiB'],p,len(peers)))
                    atomic(ticket,json.dumps({'expires':deadline,'uid':actual_uid,'ceiling':grant_ceiling}))
            if time.monotonic()>=deadline:raise RuntimeError('Host PHP admission budget full after bounded wait; no shared fallback')
            time.sleep(.25)
    finally:
        ticket.unlink(missing_ok=True)


def connect_backend(unit, backend, start_lock, deadline=None):
    """Warm requests need no subprocess; serialize only a genuinely cold start."""
    def connect():
        upstream = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        remaining=3 if deadline is None else min(3,deadline-time.monotonic())
        if remaining<=0:
            upstream.close();raise TimeoutError('Backend connection deadline')
        upstream.settimeout(remaining)
        try:
            upstream.connect(backend)
            return upstream
        except OSError:
            upstream.close()
            raise
    try:
        return connect()
    except (FileNotFoundError, ConnectionRefusedError):
        remaining=12 if deadline is None else max(0,deadline-time.monotonic())
        if not start_lock.acquire(timeout=remaining):raise TimeoutError('Cold start lock deadline')
        try:
            # A preceding thread may already have started the private backend.
            try:
                return connect()
            except (FileNotFoundError, ConnectionRefusedError):
                remaining=12 if deadline is None else min(12,deadline-time.monotonic())
                if remaining<=0:raise TimeoutError('Backend startup deadline')
                r = execute(['systemctl', 'start', unit], False, timeout=remaining)
                if r.returncode:
                    raise ConnectionRefusedError('Private PHP backend could not start')
                return connect()
        finally:start_lock.release()

def serve_proxy(listener,unit,backend,idle,limits,stop_backend=True):
    """Fixed relays plus a bounded socket queue, all inside the existing account slice."""
    listener.settimeout(1)
    pending=queue.Queue(maxsize=limits['queue']);lock=threading.Lock();start_lock=threading.Lock()
    stopping=threading.Event();activity={'last':time.monotonic(),'active':0}
    old_signals={}
    if threading.current_thread() is threading.main_thread():
        for sig in (signal.SIGTERM,signal.SIGINT):
            old_signals[sig]=signal.signal(sig,lambda *_:stopping.set())
    def diagnostic(reason, **details):
        print(json.dumps({'event':'php_proxy','unit':unit,'reason':reason,**details}),file=sys.stderr,flush=True)
    def unavailable(client):
        client.settimeout(2);header=b''
        while len(header)<8:
            chunk=client.recv(8-len(header))
            if not chunk:return
            header+=chunk
        version,kind,rid,length,padding,reserved=struct.unpack('!BBHHBB',header)
        if version!=1 or not rid:return
        content=(b'Status: 503 Service Unavailable\r\nContent-Type: text/html; charset=utf-8\r\nRetry-After: 5\r\nCache-Control: no-store\r\nX-Content-Type-Options: nosniff\r\nContent-Security-Policy: default-src \'none\'; style-src \'unsafe-inline\'; base-uri \'none\'; frame-ancestors \'none\'\r\n\r\n'+CAPACITY_BUSY_HTML)
        def record(kind,payload):return struct.pack('!BBHHBB',1,kind,rid,len(payload),0,0)+payload
        client.sendall(record(6,content)+record(6,b'')+record(3,b'\0'*8))
    def handle(client,deadline,accepted):
        forwarded=False
        try:
            with client:
                if time.monotonic()>=deadline:
                    diagnostic('queue_deadline',waitSeconds=round(time.monotonic()-accepted,3));unavailable(client);return
                # Retry only connection/startup BEFORE any request bytes are forwarded.
                while True:
                    try:
                        upstream_connection=connect_backend(unit,backend,start_lock,deadline)
                        break
                    except (OSError,subprocess.TimeoutExpired) as error:
                        if stopping.is_set() or time.monotonic()+2>=deadline:
                            diagnostic('backend_unavailable',error=type(error).__name__);unavailable(client);return
                        time.sleep(min(2,max(0,deadline-time.monotonic())))
                with upstream_connection as upstream:
                    response_buffer=bytearray()
                    while time.monotonic()<deadline and not stopping.is_set():
                        ready,_,_=select.select([client,upstream],[],[],min(1,max(.001,deadline-time.monotonic())))
                        for source in ready:
                            remaining=max(.001,deadline-time.monotonic())
                            source.settimeout(min(5,remaining))
                            data=source.recv(65536)
                            if not data:return
                            target=upstream if source is client else client
                            target.settimeout(min(5,remaining));target.sendall(data)
                            if source is client:forwarded=True
                            else:
                                response_buffer.extend(data)
                                while len(response_buffer)>=8:
                                    version,kind,rid,length,padding,reserved=struct.unpack('!BBHHBB',response_buffer[:8])
                                    size=8+length+padding
                                    if len(response_buffer)<size:break
                                    del response_buffer[:size]
                                    if kind==3:return
                    diagnostic('request_deadline',elapsedSeconds=round(time.monotonic()-accepted,3),forwarded=forwarded)
                    # Never replay a submitted request or append a 503 to a partial response.
        except (OSError,subprocess.TimeoutExpired) as error:
            diagnostic('relay_io_error',error=type(error).__name__,forwarded=forwarded)
        finally:
            with lock:activity['active']-=1;activity['last']=time.monotonic()
    def worker():
        while not stopping.is_set():
            try:item=pending.get(timeout=.25)
            except queue.Empty:continue
            with lock:activity['active']+=1
            try:handle(*item)
            finally:pending.task_done()
    workers=[]
    try:
        for _ in range(limits['workers']):
            thread=threading.Thread(target=worker,daemon=True);thread.start();workers.append(thread)
        diagnostic('started',**limits)
        while not stopping.is_set():
            # Yield only a genuinely quiescent backend; unfinished_tasks also covers
            # the window after a worker dequeues a request but before active++.
            with lock:quiescent=not activity['active'] and pending.unfinished_tasks==0
            if quiescent and waiting_units(unit):
                diagnostic('idle_lease_yield',reasonDetail='waiting_peer_admission')
                return
            try:client,_=listener.accept()
            except socket.timeout:
                with lock:done=not activity['active'] and pending.empty() and time.monotonic()-activity['last']>=int(idle)
                if done:return
                continue
            accepted=time.monotonic();deadline=accepted+limits['timeout']
            with lock:activity['last']=accepted
            # Apply backpressure; waiting requests never allocate a thread each.
            try:pending.put((client,deadline,accepted),timeout=limits['timeout'])
            except queue.Full:
                diagnostic('queue_full_deadline',queued=pending.qsize())
                try:unavailable(client)
                except OSError:pass
                client.close()
    finally:
        stopping.set()
        while True:
            try:client,_,_=pending.get_nowait()
            except queue.Empty:break
            client.close();pending.task_done()
        for thread in workers:thread.join(timeout=6)
        if stop_backend:execute(['systemctl','stop',unit],False,timeout=20)
        for sig,handler in old_signals.items():signal.signal(sig,handler)


def fastcgi_proxy(unit,backend,idle,children=None,backlog=None,request_timeout=None):
    match=re.fullmatch(r'wpiso-fpm-(php\d{2,3})-([a-z_][a-z0-9_-]*)\.service',unit)
    if not match:raise ValueError('Invalid backend')
    if children is None:
        # Backwards-compatible invocation for older unit files; read the managed native copy.
        pool=(BASE/match[1]/(match[2]+'.conf')).read_text()
        children=re.search(r'^\s*pm.max_children\s*=\s*(\d+)',pool,re.M)[1]
        value=re.search(r'^\s*listen.backlog\s*=\s*(\d+)',pool,re.M)
        backlog=value[1] if value else 511
        request_timeout=request_seconds(pool,policy().get('requestTimeoutSeconds',120))
    limits=proxy_limits(children,backlog,request_timeout)
    listener=socket.fromfd(3,socket.AF_UNIX,socket.SOCK_STREAM)
    try:serve_proxy(listener,unit,backend,idle,limits)
    finally:listener.close()


def release(unit):
    if not re.fullmatch(r'wpiso-fpm-php\d{2,3}-[a-z_][a-z0-9_-]*\.service',unit):raise ValueError('Invalid release unit')
    with lock('admission'):(RUN/'slots'/unit).unlink(missing_ok=True)

def is_managed(version):
    if not (STATE/'installed.json').exists(): return False
    try:
        data = json.loads((STATE/'installed.json').read_text())
        return version in data.get('versions', [])
    except Exception:
        return False

def onboard(version):
    if not re.fullmatch(r'php\d{2,3}', version): raise ValueError('Invalid PHP version: ' + str(version))
    p = paths(version)
    if not (p/'sbin/php-fpm').is_file() or not (p/'etc/php-fpm.conf').is_file() or not (p/'bin/fpmctl').is_file():
        raise RuntimeError('PHP installation incomplete or missing files: ' + version)
    if is_managed(version):
        ctl = p/'bin/fpmctl'
        if not ctl.is_file() or ctl.is_symlink():
            raise RuntimeError('Unexpected launcher symlink ' + version)
        if ctl.read_text() != wrapper(version):
            backups = STATE/'original-launchers'
            backups.mkdir(mode=0o700, exist_ok=True)
            archive = STATE/('backup-vendor-regen-' + str(time.time_ns()))
            archive.mkdir(mode=0o700, exist_ok=True)
            shutil.copy2(ctl, archive/version)
            if not (backups/version).exists():
                shutil.copy2(ctl, backups/version)
            execute([str(ctl), 'stop'], False, timeout=45)
            deadline = time.monotonic() + 15
            while True:
                remaining = []
                for d in pathlib.Path('/proc').iterdir():
                    if not d.name.isdigit(): continue
                    try:
                        if os.readlink(d/'exe') == str(p/'sbin/php-fpm') and b'master process' in (d/'cmdline').read_bytes():
                            remaining.append(d.name)
                    except (FileNotFoundError, ProcessLookupError, PermissionError): pass
                if not remaining: break
                if time.monotonic() > deadline:
                    for pid in remaining:
                        try: os.kill(int(pid), signal.SIGKILL)
                        except OSError: pass
                    break
                time.sleep(.1)
            atomic(ctl, wrapper(version), 0o755)
            print(version + ': repaired vendor-regenerated launcher')
        assert_launcher(version)
        ensure_health(version)
        unit = 'wpiso-manager-' + version + '.service'
        if execute(['systemctl', 'is-active', unit], False).returncode != 0:
            execute(['systemctl', 'enable', '--now', unit])
        reconcile(version, True)
        print(version + ': already onboarded; refreshed coordinator and health master')
        return
    # Parse pools to validate configuration
    parse_pools((p/'etc/php-fpm.conf').read_text(), version)
    backups = STATE/'original-launchers'
    backups.mkdir(mode=0o700, exist_ok=True)
    archive = STATE/('backup-onboard-' + str(time.time_ns()))
    archive.mkdir(mode=0o700, exist_ok=True)
    ctl = p/'bin/fpmctl'
    if ctl.is_symlink(): raise RuntimeError('Unexpected launcher symlink ' + version)
    ctl_text = ctl.read_text()
    if MARKER not in ctl_text:
        shutil.copy2(ctl, archive/version)
        if not (backups/version).exists():
            shutil.copy2(ctl, backups/version)
        execute([str(ctl), 'stop'], False, timeout=45)
        deadline = time.monotonic() + 15
        while True:
            remaining = []
            for d in pathlib.Path('/proc').iterdir():
                if not d.name.isdigit(): continue
                try:
                    if os.readlink(d/'exe') == str(p/'sbin/php-fpm') and b'master process' in (d/'cmdline').read_bytes():
                        remaining.append(d.name)
                except (FileNotFoundError, ProcessLookupError, PermissionError): pass
            if not remaining: break
            if time.monotonic() > deadline: raise RuntimeError('Native FPM master remains; complete maintenance stop first: ' + version)
            time.sleep(.1)
        atomic(ctl, wrapper(version), 0o755)
    # Register in installed.json before starting services so action() recognizes it as managed
    data = json.loads((STATE/'installed.json').read_text()) if (STATE/'installed.json').exists() else {'versions': []}
    if version not in data['versions']:
        data['versions'].append(version)
        data['versions'].sort()
    data.setdefault('nativeServiceEnablement', {})[version] = execute(['systemctl', 'is-enabled', 'php-fpm' + version[3:] + '.service'], False).stdout.strip()
    data['lastOnboardAt'] = time.time()
    atomic(STATE/'installed.json', json.dumps(data, indent=2))

    try:
        unit = 'wpiso-manager-' + version + '.service'
        atomic(UNITS/unit, '[Unit]\nDescription=Experimental Webuzo isolation coordinator ' + version + '\nAfter=network.target\n[Service]\nType=notify\nExecStart=/usr/bin/python3 ' + str(SELF) + ' supervise ' + version + '\nTimeoutStartSec=60\nTimeoutStopSec=60\nRestart=on-failure\nRestartSec=2\n[Install]\nWantedBy=multi-user.target\n', 0o644)
        execute(['systemctl', 'daemon-reload'])
        execute(['systemctl', 'enable', '--now', unit])
        execute(['systemctl', 'reset-failed', 'php-fpm' + version[3:] + '.service'], False)
        add_bridge(version)
        ensure_health(version)
        count = reconcile(version, True)
        print('Successfully onboarded ' + version + ' with ' + str(count) + ' isolated pools.')
    except Exception as exc:
        if version in data['versions']:
            data['versions'].remove(version)
            atomic(STATE/'installed.json', json.dumps(data, indent=2))
        execute(['systemctl', 'disable', '--now', 'wpiso-manager-' + version + '.service'], False)
        execute(['systemctl', 'stop', 'php-fpm' + version[3:] + '.service'], False)
        execute(['systemctl', 'stop', 'wpiso-health-' + version + '.service'], False)
        raise RuntimeError('Failed to initialize managed services for ' + version + ': ' + str(exc))

def retire(version):
    if not re.fullmatch(r'php\d{2,3}', version): raise ValueError('Invalid PHP version: ' + str(version))
    if not is_managed(version):
        print(version + ': not currently managed in isolation; nothing to retire')
        return
    p = paths(version)
    if (p/'etc/php-fpm.conf').is_file():
        try:
            pools = parse_pools((p/'etc/php-fpm.conf').read_text(), version)
            if pools:
                active_users = [r['user'] for r in pools]
                raise RuntimeError('Cannot retire ' + version + ': active customer pools exist: ' + str(active_users) + '. Reassign domains in Webuzo before retiring.')
        except Exception as e:
            if 'Cannot retire' in str(e): raise
    execute(['systemctl', 'disable', '--now', 'wpiso-manager-' + version + '.service'], False, timeout=90)
    unit = 'php-fpm' + version[3:] + '.service'
    path = UNITS/unit
    if path.exists() and path.read_text() == bridge(version):
        execute(['systemctl', 'stop', unit], False, timeout=90)
        wanted = UNITS/'multi-user.target.wants'/unit
        if wanted.is_symlink() and wanted.resolve() == path: wanted.unlink()
        path.unlink()
    execute(['systemctl', 'stop', 'wpiso-health-' + version + '.service'], False)
    (UNITS/('wpiso-health-' + version + '.service')).unlink(missing_ok=True)
    (UNITS/('wpiso-manager-' + version + '.service')).unlink(missing_ok=True)
    m = manifest(version)
    for row in m.get('pools', []): stop_pool(version, row, True)
    ctl = p/'bin/fpmctl'
    if ctl.is_file() and (STATE/'original-launchers'/version).exists():
        if ctl.read_text() == wrapper(version):
            shutil.copy2(STATE/'original-launchers'/version, ctl)
    (STATE/(version + '.json')).unlink(missing_ok=True)
    for sock in RUN.glob(version + '-*.sock'): sock.unlink(missing_ok=True)
    data = json.loads((STATE/'installed.json').read_text())
    if version in data['versions']:
        data['versions'].remove(version)
    data.get('nativeServiceEnablement', {}).pop(version, None)
    data['lastRetireAt'] = time.time()
    atomic(STATE/'installed.json', json.dumps(data, indent=2))
    execute(['systemctl', 'daemon-reload'])
    print('Successfully retired ' + version + ' from isolation.')

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
                private=(BASE/version/(row['user']+'.conf')).read_text()
                native=row['maxChildren'];backlog=re.search(r'^\s*listen.backlog\s*=\s*(\d+)',private,re.M)
                effective=re.search(r'^\s*pm\.max_children\s*=\s*(\d+)',private,re.M)
                ceiling=runtime_ceiling(row['uid'],native,results['policy'],int(backlog[1]) if backlog else 511,request_seconds(private))
                lease=RUN/'slots'/fpm
                item.update({'nativeMaxChildren':native,'accountWorkerCeiling':ceiling,
                    'managedMaxChildren':int(effective[1]) if effective else None,
                    'runtimeCapSource':'automatic-account-boundary' if results['policy'].get('accountRuntimeCaps') else 'native-global',
                    'reservedMiB':json.loads(lease.read_text())['costMiB'] if lease.exists() else 0})
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
    elif ns.command=='repair-launchers':
        data=json.loads((STATE/'installed.json').read_text()) if (STATE/'installed.json').exists() else {'versions':[]}
        for v in data.get('versions',[]):onboard(v)
    elif ns.command=='onboard':onboard(ns.args[0])
    elif ns.command=='retire':retire(ns.args[0])
    elif ns.command=='wait-socket':
        path=pathlib.Path(ns.args[0]);deadline=time.monotonic()+8
        while not path.exists() and time.monotonic()<deadline:time.sleep(.05)
        if not path.exists():raise RuntimeError('Isolated backend socket not ready')
    elif ns.command=='uninstall':uninstall()
    else:raise ValueError('Unknown command')

if __name__=='__main__':
    try:main()
    except Exception as e:print('ISOLATION ERROR: '+str(e),file=sys.stderr);sys.exit(1)
