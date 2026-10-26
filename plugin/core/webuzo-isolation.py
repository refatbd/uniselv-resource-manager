#!/usr/bin/python3
"""Experimental Webuzo FPM launcher integration. Root-only; never falls back to shared FPM."""
import queue
import base64
import argparse,contextlib,fcntl,hashlib,json,os,pathlib,pwd,re,shutil,signal,socket,subprocess,sys,time,select,struct,threading
BASE=pathlib.Path('/etc/webuzo-isolation')
STATE=pathlib.Path('/var/lib/webuzo-isolation')
RUN=pathlib.Path('/run/webuzo-isolation')
SELF=pathlib.Path('/usr/local/sbin/webuzo-isolation.py')
UNITS=pathlib.Path('/etc/systemd/system')
PROXY='/usr/lib/systemd/systemd-socket-proxyd'
MARKER='# WEBUZO-ISOLATION MANAGED LAUNCHER'
CAPACITY_MODEL_VERSION='account-demand-v7-stable-sharing'
NATIVE_CGROUP_USERS=pathlib.Path('/var/webuzo/conf/cgroupusers')
NATIVE_CGROUP_DROPIN=UNITS/'cgroup.service.d/90-uniselv-resman.conf'

# Self-contained fallback: no PHP, external assets, scripts, or template file I/O.
CAPACITY_BUSY_HTML = b'<!doctype html>\n<html lang="en">\n<head>\n  <meta charset="utf-8">\n  <meta name="viewport" content="width=device-width, initial-scale=1">\n  <meta name="robots" content="noindex, nofollow">\n  <meta name="color-scheme" content="light">\n  <title>We\'ll be right with you | Temporarily unavailable</title>\n  <style>\n    *{box-sizing:border-box}html{min-height:100%;background:#faf9f7}body{margin:0;min-height:100svh;color:#25252b;font:16px/1.6 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;display:grid;place-items:center;padding:40px 24px;isolation:isolate;overflow-x:hidden}\n    .ambient{position:fixed;z-index:-1;inset:0;pointer-events:none;background:radial-gradient(ellipse at 82% 25%,#ffe9e7aa,transparent 48%),radial-gradient(ellipse at 8% 90%,#f3ebe480,transparent 40%)}.grid{position:fixed;z-index:-1;inset:0;pointer-events:none;background-image:radial-gradient(#c5b6b455 1px,transparent 1px);background-size:24px 24px;mask-image:linear-gradient(transparent,#0003,transparent)}\n    main{width:min(100%,1000px);animation:arrive .7s ease-out both}.brand{display:flex;align-items:center;gap:10px;font-size:11px;font-weight:700;letter-spacing:2px;margin:0 4px 24px;color:#6d6060}.brand svg{width:26px;height:26px}.brand span{letter-spacing:0;font-size:11px;font-weight:400;color:#7c7373;border-left:1px solid #ddd4d1;padding-left:15px;margin-left:6px}\n    .card{position:relative;display:grid;grid-template-columns:1.1fr 1fr;align-items:center;gap:30px;border:1px solid #ece6e3;border-radius:30px;background:#fff;padding:64px;box-shadow:0 30px 80px -40px #714c4930,0 3px 12px #493c3404;overflow:hidden}.card:before{content:"";position:absolute;top:0;left:12%;right:12%;height:2px;background:linear-gradient(90deg,transparent,#eb6c6355,transparent)}\n    .eyebrow{display:inline-flex;align-items:center;gap:8px;padding:5px 10px;border:1px solid #f5d8d5;border-radius:6px;background:#fff5f3;color:#b23d34;font-size:10px;font-weight:650;letter-spacing:1.4px;text-transform:uppercase}.dot{width:5px;height:5px;border-radius:50%;background:#d9564c;box-shadow:0 0 0 3px #d9564c12;animation:pulse 2.5s ease-in-out infinite}h1{font-size:clamp(36px,4.5vw,50px);font-weight:650;letter-spacing:-2.2px;line-height:1.12;margin:25px 0 20px}h1 span{color:#7e7778;font-weight:450}.description{color:#706b70;font-size:14px;line-height:1.8;max-width:340px;margin:0 0 28px}.retry{display:inline-flex;align-items:center;justify-content:center;gap:10px;padding:12px 21px;min-height:48px;border:1px solid #bd4037;border-radius:10px;background:#c3463c;color:#fff;font-size:13px;font-weight:650;text-decoration:none;box-shadow:0 4px 10px #bd403718;transition:background .2s,transform .2s,box-shadow .2s}.retry:hover{background:#a9362e;transform:translateY(-2px);box-shadow:0 8px 20px #bd403728}.retry:focus-visible{outline:3px solid #df8e87;outline-offset:4px}.retry svg{width:16px;height:16px}.hint{display:block;font-size:11px;color:#817878;margin-top:13px}\n    .visual{position:relative;height:340px;display:grid;place-items:center}.halo{position:absolute;width:310px;height:310px;border-radius:50%;background:radial-gradient(circle,#fff1ef,transparent 70%)}.error-number{position:absolute;top:8px;font-size:112px;font-weight:750;letter-spacing:-8px;line-height:1;color:#f8e9e6;user-select:none}.orbit{position:absolute;width:266px;height:266px;border:1px solid #f2ded9;border-radius:50%}.orbit.inner{width:206px;height:206px;border-style:dashed;border-color:#ecd3cd}.satellite{position:absolute;inset:-1px;border-radius:50%;animation:orbit 22s linear infinite}.satellite:before{content:"";position:absolute;top:-4px;left:50%;width:8px;height:8px;background:#df7d72;border:2px solid white;border-radius:50%;box-shadow:0 0 0 4px #f9e6e2}.core{position:relative;width:118px;height:118px;display:grid;place-items:center;border:1px solid #f4d2cc;border-radius:30px;background:linear-gradient(145deg,#fff9f7,#fdeae5);box-shadow:inset 0 2px #fff,0 18px 35px -20px #c8736777;transform:rotate(-8deg);animation:float 6s ease-in-out infinite}.core svg{width:53px;height:53px;color:#c44e42;transform:rotate(8deg)}.alert-badge{position:absolute;right:-10px;top:-10px;width:34px;height:34px;display:grid;place-items:center;border:4px solid white;border-radius:50%;background:#cd5146;color:white;font-size:17px;font-weight:700;line-height:1;box-shadow:0 3px 8px #bf635522}.status{position:absolute;bottom:4px;display:flex;align-items:center;gap:9px;padding:9px 14px;background:#fff;border:1px solid #eee2dd;border-radius:30px;color:#88736e;font-size:10px;box-shadow:0 5px 15px #95605208}.bars{display:flex;gap:3px;align-items:center;height:15px}.bars i{width:3px;height:5px;background:#d9786d;border-radius:2px;animation:bars 1.4s ease-in-out infinite}.bars i:nth-child(2){animation-delay:.15s}.bars i:nth-child(3){animation-delay:.3s}.small-cross{position:absolute;top:70px;right:22px;color:#d49c92;font-size:18px}.code{position:absolute;left:9px;bottom:50px;color:#b1877e;font:9px ui-monospace,monospace;letter-spacing:1.5px}\n    footer{display:flex;justify-content:space-between;align-items:center;gap:20px;margin:22px 4px 0;color:#8b8180;font-size:10px}.foot-status{display:flex;align-items:center;gap:7px}.foot-status:before{content:"";width:5px;height:5px;background:#d17a70;border-radius:50%}\n    @keyframes arrive{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}@keyframes orbit{to{transform:rotate(360deg)}}@keyframes float{50%{transform:translateY(-9px) rotate(-4deg)}}@keyframes pulse{50%{opacity:.45}}@keyframes bars{50%{height:14px}}\n    @media(max-width:700px){body{padding:28px 18px}.brand{margin-bottom:20px;font-size:10px;letter-spacing:1.5px}.brand span{display:none}.card{grid-template-columns:1fr;padding:30px 26px;gap:24px;border-radius:24px}.visual{grid-row:1;height:240px}.orbit{width:200px;height:200px}.orbit.inner{width:154px;height:154px}.error-number{top:0;font-size:88px}.core{width:94px;height:94px;border-radius:24px}.core svg{width:43px;height:43px}.status{bottom:-7px;font-size:9px}.small-cross{top:38px;right:20px}.code{left:0;bottom:26px;font-size:8px}h1{font-size:38px;letter-spacing:-1.8px;margin-top:20px}.description{max-width:100%;font-size:13px}.hint{font-size:10px}footer{align-items:flex-start;font-size:9px;gap:14px}.foot-status{max-width:145px}}\n    @media(prefers-reduced-motion:reduce){*,*:before,*:after{animation:none!important;transition:none!important}}\n  </style>\n</head>\n<body>\n  <div class="ambient" aria-hidden="true"></div><div class="grid" aria-hidden="true"></div>\n  <main>\n    <div class="brand"><svg viewBox="0 0 32 32" fill="none" aria-hidden="true"><rect x="5" y="5" width="22" height="22" rx="8" stroke="#b76b62" stroke-width="1.5"/><path d="M13 12v8m6-8v8" stroke="#b76b62" stroke-width="2.5" stroke-linecap="round"/></svg>A MOMENT, PLEASE<span>We appreciate your patience.</span></div>\n    <section class="card" aria-labelledby="title">\n      <div class="copy">\n        <div class="eyebrow"><span class="dot" aria-hidden="true"></span>Temporarily at capacity</div>\n        <h1 id="title">A little pause.<br><span>We\'ll be right<br>with you.</span></h1>\n        <p class="description">We\'re experiencing high demand right now. Please give us a moment, then try this page again.</p>\n        <a class="retry" href=""><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 7v5h-5M4.5 9a8 8 0 0113.2-3L20 9M4 17v-5h5m10.5 3a8 8 0 01-13.2 3L4 15"/></svg>Try Again</a>\n        <small class="hint">Wait a few seconds before trying again.</small>\n      </div>\n      <div class="visual" aria-hidden="true"><div class="halo"></div><span class="error-number">503</span><div class="orbit"><div class="satellite"></div></div><div class="orbit inner"></div><span class="small-cross">+</span><div class="core"><span class="alert-badge">!</span><svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="12" y="12" width="40" height="16" rx="5"/><rect x="12" y="36" width="40" height="16" rx="5"/><path d="M20 20h1m-1 24h1m17-24h6m-6 24h6M32 28v8"/></svg></div><span class="code">PLEASE STAND BY</span><div class="status"><span class="bars"><i></i><i></i><i></i></span>A moment to catch our breath.</div></div>\n    </section>\n    <footer><span>Thank you for your patience.</span><span class="foot-status">503 &middot; Service temporarily unavailable</span></footer>\n  </main>\n</body>\n</html>\n'

def execute(args,check=True,timeout=60):
    # Only this supervisor owns its service notification endpoint. PHP syntax
    # checks and other children must not publish readiness/watchdog messages.
    env={key:value for key,value in os.environ.items() if key not in
         ('NOTIFY_SOCKET','WATCHDOG_PID','WATCHDOG_USEC')}
    r=subprocess.run(args,capture_output=True,text=True,timeout=timeout,env=env)
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
    # Retire ondemand workers independently; preserve the master's opcode cache
    # while measured headroom permits. Waiting peers can reclaim its lease early.
    data.setdefault('warmIdleSeconds',warm_idle_seconds(data))
    if type(data['warmIdleSeconds']) is not int or not 15<=data['warmIdleSeconds']<=3600:raise ValueError('Invalid warmIdleSeconds')
    return data


def warm_idle_seconds(p):
    """One minute per affordable warm-master footprint, bounded operational TTL."""
    return max(60,min(900,int(p['phpBudgetMiB'])//max(1,48+int(p['opcacheMiB']))*60))


def idle_retirement_reason(elapsed,ttl,quiescent,peer_waiting,available_mib,reserve_mib):
    if not quiescent:return None
    if peer_waiting:return 'waiting_peer_admission'
    if reserve_mib and (available_mib is None or available_mib<reserve_mib):return 'host_memory_reserve'
    if elapsed>=ttl:return 'warm_idle_expired'
    return None


def native_account_uids():
    """Re-read Webuzo's root-owned assignment registry; provisioning is dynamic."""
    if not NATIVE_CGROUP_USERS.exists():return set()
    # Webuzo owns this registry as its private service account on native Ubuntu.
    owners={0};groups={0}
    try:
        vendor=pwd.getpwnam('webuzo');owners.add(vendor.pw_uid);groups.add(vendor.pw_gid)
    except KeyError:pass
    info=NATIVE_CGROUP_USERS.stat()
    if (NATIVE_CGROUP_USERS.is_symlink() or info.st_uid not in owners or info.st_mode&0o002
            or (info.st_mode&0o020 and info.st_gid not in groups)):
        raise RuntimeError('Unsafe native cgroup registry')
    values=NATIVE_CGROUP_USERS.read_text().split()
    if any(not value.isdigit() or int(value)<1 for value in values):raise ValueError('Invalid native account UID registry')
    result=set()
    for value in values:
        uid=int(value)
        try:user=pwd.getpwuid(uid).pw_name
        except KeyError:continue
        # Native registries may also contain nobody/shared service UIDs.
        if (pathlib.Path('/var/webuzo/users')/user).is_dir():result.add(uid)
    return result


def native_cgroup_target(uid):
    target=pathlib.Path('/sys/fs/cgroup')/account_cgroup(uid).lstrip('/')
    if not target.exists() and account_slice(uid).startswith('golden-'):
        execute(['/usr/bin/python3','/usr/local/sbin/golden-shield.py','prepare-account',str(uid)],timeout=30)
    if not (target/'cgroup.procs').exists():raise RuntimeError('Account cgroup is not provisioned: '+str(uid))
    return target


def native_cgroup_pass():
    """Preserve managed service subgroups; repair legacy UID placement once per sweep.

    This replaces only the vendor service command through an owned drop-in, never
    the vendor script. Native-only installations retain the original UID target.
    """
    uids=native_account_uids();targets={};moved=0;errors=[]
    for uid in uids:
        try:targets[uid]=native_cgroup_target(uid)
        except (OSError,RuntimeError,ValueError) as exc:
            # Deletion/provisioning of one account must not stop reconciliation
            # for every other account. Its own FPM admission remains fail-closed.
            errors.append({'uid':uid,'error':str(exc)[:160]})
    for proc in pathlib.Path('/proc').iterdir():
        if not proc.name.isdigit():continue
        try:
            uid=proc.stat().st_uid
            if uid not in targets:continue
            if os.readlink(proc/'exe')=='/usr/local/apps/apache2/bin/httpd':continue
            current=(proc/'cgroup').read_text().strip()
            expected='0::'+account_cgroup(uid)
            if current==expected or current.startswith(expected+'/'):continue
            # Recheck ownership immediately before migration; exited PIDs are benign.
            if proc.stat().st_uid!=uid:continue
            place_native_process(uid,int(proc.name),targets[uid])
            moved+=1
        except (FileNotFoundError,ProcessLookupError):continue
        except (OSError,ValueError) as exc:errors.append({'pid':int(proc.name),'error':str(exc)[:160]})
    return {'moved':moved,'errors':errors,'accounts':len(uids)}


def place_native_process(uid,pid,target):
    if account_slice(uid).startswith('golden-'):
        # cgroup v2 forbids internal processes in a slice with enabled child
        # controllers. Adopt legacy CLI/session PIDs into a proper child scope.
        unit='resman-native-u'+str(uid)+'-p'+str(pid)+'-'+str(time.time_ns())+'.scope'
        execute(['/usr/bin/busctl','call','org.freedesktop.systemd1','/org/freedesktop/systemd1',
                 'org.freedesktop.systemd1.Manager','StartTransientUnit','ssa(sv)a(sa(sv))',
                 unit,'fail','3','Slice','s',account_slice(uid),'PIDs','au','1',str(pid),
                 'MemorySwapMax','t','0','0'],timeout=10)
    else:(target/'cgroup.procs').write_text(str(pid))


def native_guard_dropin():
    return ('# UNISELV-RESMAN native cgroup coexistence; vendor source preserved\n'
            '[Service]\nExecStart=\nExecStart=/usr/bin/python3 '+str(SELF)+' native-cgroup-guard\n'
            'Restart=on-failure\nRestartSec=2\n')


def ensure_native_cgroup_guard():
    if not account_slice(1).startswith('golden-'):
        # Without Golden the vendor and managed services already share the
        # native UID boundary. Restore the untouched vendor command on rollback.
        remove_native_cgroup_guard()
        return {'required':False}
    # No native mover means there is no command to replace on that installation.
    vendor=pathlib.Path('/usr/local/webuzo/bin/cgroup.sh')
    if not vendor.exists():return {'required':False}
    source=vendor.read_text()
    if 'cgroup.procs' not in source or '/sys/fs/cgroup/' not in source:raise RuntimeError('Unrecognized native cgroup mover; review vendor integration')
    desired=native_guard_dropin()
    with lock('native-cgroup-guard'):
        if NATIVE_CGROUP_DROPIN.is_symlink():raise RuntimeError('Unsafe native cgroup drop-in')
        if NATIVE_CGROUP_DROPIN.exists() and NATIVE_CGROUP_DROPIN.read_text()!=desired:raise RuntimeError('Native cgroup drop-in changed; refusing overwrite')
        if not NATIVE_CGROUP_DROPIN.exists():
            command=execute(['systemctl','show','cgroup.service','-p','ExecStart','--value'],False).stdout
            if '/usr/local/webuzo/bin/cgroup.sh' not in command:raise RuntimeError('Unexpected cgroup.service command; refusing replacement')
            # Validate every assigned destination before replacing the competing writer.
            for uid in native_account_uids():native_cgroup_target(uid)
            atomic(NATIVE_CGROUP_DROPIN,desired,0o644)
            try:
                execute(['systemctl','daemon-reload']);execute(['systemctl','restart','cgroup.service'])
            except Exception:
                NATIVE_CGROUP_DROPIN.unlink(missing_ok=True);execute(['systemctl','daemon-reload'],False);execute(['systemctl','restart','cgroup.service'],False);raise
        if execute(['systemctl','is-active','cgroup.service'],False).returncode:
            execute(['systemctl','start','cgroup.service'])
        # Old Golden releases patched the vendor scanner itself. Relinquish
        # ownership explicitly so a later vendor refresh is neither overwritten
        # nor mistaken for a change to our new drop-in. Preserve the old receipt.
        registry=pathlib.Path('/var/lib/golden-shield/shared-files.json')
        if registry.exists():
            data=json.loads(registry.read_text());key=str(vendor)
            if key in data:
                receipt={'path':key,'retired':data[key],'currentVendorSha256':hashlib.sha256(vendor.read_bytes()).hexdigest(),'at':time.time(),'reason':'Replaced vendor-file patch with owned service drop-in'}
                atomic(STATE/('native-scanner-ownership-retired-'+str(time.time_ns())+'.json'),json.dumps(receipt,indent=2))
                del data[key];atomic(registry,json.dumps(data,indent=2))
    return {'required':True,'active':True}


def native_cgroup_guard():
    alive=threading.Event();alive.set()
    def stop(*_):alive.clear()
    for sig in (signal.SIGTERM,signal.SIGINT):signal.signal(sig,stop)
    while alive.is_set():
        result=native_cgroup_pass()
        if result['errors']:print(json.dumps({'event':'native_cgroup_guard',**result}),file=sys.stderr,flush=True)
        # Five seconds matches the inspected vendor reconciliation cadence.
        for _ in range(50):
            if not alive.is_set():break
            time.sleep(.1)


def native_cgroup_drift(uid):
    """Check actual worker placement, not just the service's declared ControlGroup."""
    expected='0::'+account_cgroup(uid);outside=[];checked=0
    for proc in pathlib.Path('/proc').iterdir():
        if not proc.name.isdigit():continue
        try:
            if proc.stat().st_uid!=int(uid):continue
            if os.readlink(proc/'exe')=='/usr/local/apps/apache2/bin/httpd':continue
            actual=(proc/'cgroup').read_text().strip();checked+=1
            if actual!=expected and not actual.startswith(expected+'/'):outside.append(int(proc.name))
        except (FileNotFoundError,ProcessLookupError,PermissionError):continue
    return {'expected':account_cgroup(uid),'processesChecked':checked,'outsidePids':outside,'pass':not outside}


def remove_native_cgroup_guard():
    if NATIVE_CGROUP_DROPIN.exists():
        if NATIVE_CGROUP_DROPIN.read_text()!=native_guard_dropin():raise RuntimeError('Changed native cgroup integration; refusing removal')
        NATIVE_CGROUP_DROPIN.unlink();execute(['systemctl','daemon-reload']);execute(['systemctl','restart','cgroup.service'])

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

def parse_pools(text,version,prepare=True):
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
        if prepare:ensure_limits(user,account.pw_uid)
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


def peer_budget_pressure(leases, peers, p):
    """Warm peers alone are not demand. Yield only for an unfunded next worker."""
    if not peers:return False
    free=p['phpBudgetMiB']-sum(int(row['costMiB']) for row in leases.values())
    minimum=[]
    for name in peers:
        if name in leases:
            minimum.append(p['workerRssMiB']);continue
        # Versions may have different native relay sizes. The admitting peer
        # publishes its own complete minimum instead of borrowing our overhead.
        try:
            row=json.loads((RUN/'waiting'/name).read_text());cost=row['minimumMiB']
            if type(cost) is not int or cost<1:raise ValueError('Invalid peer minimum')
            minimum.append(cost)
        except (OSError,ValueError,KeyError,TypeError):
            return True  # Legacy/unknown demand cannot establish spare capacity.
    required=min(minimum)
    return free<required


def publish_runtime_demand(unit,uid,ceiling,demand,minimum_mib=None):
    """A granted busy peer remains demand; a cleared waiting ticket is not idleness."""
    if type(demand) is not int or demand<0:raise ValueError('Invalid runtime demand')
    directory=RUN/'demand';directory.mkdir(mode=0o700,exist_ok=True);path=directory/unit
    if not demand:path.unlink(missing_ok=True);return
    row={'uid':uid,'wanted':min(ceiling,demand),'ceiling':ceiling,'expires':time.monotonic()+3}
    if minimum_mib is not None:row['minimumMiB']=minimum_mib
    atomic(path,json.dumps(row))


def refresh_draining_demand(unit):
    """A proxy still owns queued demand while its old backend drains/restarts."""
    with lock('admission'):
        path=RUN/'demand'/unit
        try:row=json.loads(path.read_text())
        except FileNotFoundError:return
        row['expires']=time.monotonic()+3
        atomic(path,json.dumps(row))


def clear_runtime_demand(unit):
    (RUN/'demand'/unit).unlink(missing_ok=True)


def fair_demand_ceiling(unit,ceiling,demand,leases,peers,p):
    """Water-fill live demand, charging idle leases in full before sharing workers.

    Persistent busy-peer heartbeats prevent grow/shrink ping-pong when a peer's
    waiting ticket disappears after a successful grant. Nothing here releases a
    reservation; admission and drained regrant still enforce actual lease costs.
    """
    if demand<1:return ceiling
    own=leases[unit];rss=p['workerRssMiB'];claims={};idle_cost=0;now=time.monotonic()
    def fallback():
        return min(ceiling,contention_ceiling(ceiling,int(own['costMiB'])-int(own['runtimeMaxChildren'])*rss-48-p['opcacheMiB'],p,len(set(leases)|peers))) if peer_budget_pressure(leases,peers,p) else ceiling
    for name,row in leases.items():
        current=int(row['runtimeMaxChildren']);overhead=int(row['costMiB'])-current*rss
        if name==unit:claims[name]={'wanted':min(ceiling,demand),'overhead':overhead};continue
        wanted=None
        try:
            record=json.loads((RUN/'demand'/name).read_text())
            if (record.get('uid')==row['uid'] and type(record.get('expires')) in (int,float)
                    and now<record['expires']<float('inf') and type(record.get('wanted')) is int
                    and type(record.get('ceiling')) is int and 1<=record['wanted']<=record['ceiling']<=int(row['nativeMaxChildren'])):
                wanted=record['wanted']
        except (OSError,ValueError,TypeError,KeyError):pass
        if wanted is None and name in peers:
            try:
                ticket=json.loads((RUN/'waiting'/name).read_text());cap=ticket['ceiling']
                if ticket.get('uid')!=row['uid'] or type(cap) is not int or not 1<=cap<=int(row['nativeMaxChildren']):return fallback()
                wanted=cap
            except (OSError,ValueError,TypeError,KeyError):return fallback()
        if wanted is None:idle_cost+=int(row['costMiB'])
        else:claims[name]={'wanted':wanted,'overhead':overhead}
    # A restarted backend temporarily has no lease, but its live proxy still
    # owns queued demand. Do not let peers steal that claimant's fair target.
    unleased=set(peers)-set(leases)
    for path in (RUN/'demand').glob('*.service'):
        if path.name in leases:continue
        try:
            record=json.loads(path.read_text());match=re.fullmatch(r'wpiso-fpm-php\d{2,3}-([a-z_][a-z0-9_-]*)\.service',path.name)
            if (not match or record.get('uid')!=pwd.getpwnam(match[1]).pw_uid
                    or type(record.get('expires')) not in (int,float) or not now<record['expires']<float('inf')
                    or type(record.get('wanted')) is not int or type(record.get('ceiling')) is not int
                    or not 1<=record['wanted']<=record['ceiling']<=128):continue
            minimum=record['minimumMiB']
            if type(minimum) is not int or minimum<rss+48+p['opcacheMiB']:continue
            claims[path.name]={'wanted':record['wanted'],'overhead':minimum-rss};unleased.discard(path.name)
        except (OSError,ValueError,TypeError,KeyError):continue
    for name in unleased:
        try:
            ticket=json.loads((RUN/'waiting'/name).read_text());minimum=ticket['minimumMiB'];cap=ticket['ceiling']
            if type(minimum) is not int or minimum<rss+48+p['opcacheMiB'] or type(cap) is not int or not 1<=cap<=128:return fallback()
            claims[name]={'wanted':cap,'overhead':minimum-rss}
        except (OSError,ValueError,TypeError,KeyError):return fallback()
    if len(claims)<2:return ceiling  # Idle peers must still receive an unfunded-demand ticket.
    needed=idle_cost+sum(c['overhead']+rss*(max(int(own['runtimeMaxChildren']),c['wanted']) if n==unit else c['wanted']) for n,c in claims.items())
    if needed<=p['phpBudgetMiB']:return ceiling
    available=p['phpBudgetMiB']-idle_cost-sum(c['overhead'] for c in claims.values());grants={name:0 for name in claims}
    while available>=rss:
        changed=False
        for name in sorted(claims):
            if grants[name]<claims[name]['wanted'] and available>=rss:
                grants[name]+=1;available-=rss;changed=True
        if not changed:break
    return min(ceiling,max(1,grants[unit]))


def compact_idle_lease(unit, limits):
    """Release excess reservation after surplus native children have exited.

    The master retains one fully charged worker plus opcode/relay overhead.
    The caller holds its dispatch mutex with an empty request queue throughout.
    A sole remaining child must be proven idle on the private listener. Unknown
    proc state or excessive charged memory never earns a smaller reservation.
    """
    match=re.fullmatch(r'wpiso-fpm-(php\d{2,3})-([a-z_][a-z0-9_-]*)\.service',unit)
    if not match:return False
    p=policy()
    if not p.get('accountRuntimeCaps',False):return False
    with lock('admission'):
        path=RUN/'slots'/unit
        if not path.exists():return False
        row=json.loads(path.read_text())
        if not row.get('relayEnforced') or int(row['runtimeMaxChildren'])<=1:return False
        uid=pwd.getpwnam(match[2]).pw_uid
        if row.get('uid')!=uid:raise ValueError('Idle runtime UID changed')
        pid=int((RUN/(match[1]+'-'+match[2]+'.pid')).read_text())
        proc=pathlib.Path('/proc')/str(pid);expected=account_cgroup(uid)+'/'+unit
        if (proc/'cgroup').read_text().strip()!='0::'+expected:return False
        if not re.search(r'^Uid:\s+0\b',(proc/'status').read_text(),re.M):return False
        children=(proc/'task'/str(pid)/'children').read_text().split()
        if len(children)>1:return False
        if children and not backend_drained(unit,RUN/(match[1]+'-'+match[2]+'.sock')):return False
        cost=p['workerRssMiB']+48+p['opcacheMiB']+limits['memoryMiB']
        charged=int((pathlib.Path('/sys/fs/cgroup'+expected)/'memory.current').read_text())
        if charged>cost*1048576:return False
        previous=int(row['runtimeMaxChildren'])
        row.update(runtimeMaxChildren=1,costMiB=cost,lastResizeAt=time.time(),idleCompacted=True)
        atomic(path,json.dumps(row))
        return {'previous':previous,'ceiling':1,'releasedMiB':(previous-1)*p['workerRssMiB']}


def idle_peer_pressure(unit, limits):
    p=policy()
    with lock('admission'):
        leases={path.name:json.loads(path.read_text()) for path in (RUN/'slots').glob('*.service')}
        return peer_budget_pressure(leases,waiting_units(unit),p)


def contention_ceiling(ceiling,relay_memory,p,pool_count):
    """Share a pressured cold grant; final admission still charges complete leases."""
    overhead=48+p['opcacheMiB']+relay_memory
    fair=int((p['phpBudgetMiB']/max(1,pool_count)-overhead)//p['workerRssMiB'])
    return min(ceiling,max(1,fair))


def private_backend(pool):
    # Only the root proxy may reach the backend; Apache keeps its native front socket.
    if re.search(r'^\s*listen\.acl_(users|groups)\s*=\s*[^;\s]',pool,re.M):
        raise ValueError('Private relay backend does not support native listen ACL overrides')
    for key,value in [('listen.owner','root'),('listen.group','root'),('listen.mode','0600')]:
        pattern=r'^(\s*'+re.escape(key)+r'\s*=).*$'
        count=len(re.findall(pattern,pool,re.M))
        if count>1:raise ValueError('Duplicate private backend directive: '+key)
        pool=re.sub(pattern,lambda m:m[1]+' '+value,pool,flags=re.M) if count else pool+'\n'+key+' = '+value+'\n'
    return pool


def elastic_proxy_ready(unit):
    """A PID/start-token handshake prevents old proxies bypassing the new relay gate."""
    try:
        match=re.fullmatch(r'wpiso-fpm-(php\d{2,3})-([a-z_][a-z0-9_-]*)\.service',unit)
        if not match:return False
        marker=RUN/'elastic-proxies'/unit
        if marker.is_symlink():return False
        row=json.loads(marker.read_text());pid=row['pid']
        if type(pid) is not int or pid<1:return False
        proc=pathlib.Path('/proc')/str(pid)
        if (proc/'stat').read_text().rsplit(')',1)[1].split()[19]!=str(row['startTicks']):return False
        uid=pwd.getpwnam(match[2]).pw_uid
        if (proc/'cgroup').read_text().strip()!='0::'+account_cgroup(uid)+'/'+unit.replace('wpiso-fpm-','wpiso-proxy-',1):return False
        args=(proc/'cmdline').read_bytes().split(b'\0')
        return row.get('protocol')==1 and len(args)>3 and args[1:4]==[str(SELF).encode(),b'proxy',unit.encode()]
    except (OSError,ValueError,TypeError,KeyError,IndexError):return False


def runtime_dispatch_limit(unit,upper):
    lease=RUN/'slots'/unit
    if not lease.exists():return 1  # One cold starter establishes a verified lease.
    row=json.loads(lease.read_text())
    grant=row.get('runtimeMaxChildren')
    if type(grant) is not int or not 1<=grant<=128:raise ValueError('Invalid relay grant')
    return min(upper,grant) if row.get('relayEnforced') else upper


def clear_elastic_demand(unit):
    ticket=RUN/'waiting'/unit
    try:
        if json.loads(ticket.read_text()).get('mode')=='elastic':ticket.unlink(missing_ok=True)
    except FileNotFoundError:pass


def backend_drained(unit,backend):
    """Verify FPM children are gone or blocked accepting on this private listener.

    A disconnected client is not proof that its PHP/background job has finished.
    Unknown kernels/proc visibility fail closed until ondemand children exit.
    """
    match=re.fullmatch(r'wpiso-fpm-(php\d{2,3})-([a-z_][a-z0-9_-]*)\.service',unit)
    if not match:raise ValueError('Invalid backend drain unit')
    uid=pwd.getpwnam(match[2]).pw_uid;expected=account_cgroup(uid)+'/'+unit
    pidfile=RUN/(match[1]+'-'+match[2]+'.pid')
    try:
        pid=int(pidfile.read_text());master=pathlib.Path('/proc')/str(pid)
        if (master/'cgroup').read_text().strip()!='0::'+expected:return False
        if not re.search(r'^Uid:\s+0\b',(master/'status').read_text(),re.M):return False
        children=(master/'task'/str(pid)/'children').read_text().split()
        if not children:return True
        inode=None
        for line in pathlib.Path('/proc/net/unix').read_text().splitlines():
            values=line.split(maxsplit=7)
            if len(values)==8 and values[7]==str(backend) and values[3:6]==['00010000','0001','01']:
                inode=values[6];break
        if inode is None:return False
        for child in children:
            proc=pathlib.Path('/proc')/child
            try:
                if (proc/'cgroup').read_text().strip()!='0::'+expected:return False
                if not re.search(r'^Uid:\s+'+str(uid)+r'\b',(proc/'status').read_text(),re.M):return False
                call=(proc/'syscall').read_text().split()
                if len(call)<2 or not (proc/'wchan').read_text().strip().endswith('skb_wait_for_more_packets'):return False
                fd=int(call[1],0)
                if str((proc/'fd'/str(fd)).readlink())!='socket:['+inode+']':return False
            except FileNotFoundError:
                if proc.exists():return False
        return True
    except (OSError,ValueError,IndexError):return False


def elastic_regrant_plan(unit,limits,demand):
    """Plan a drained restart, never resize/stop an in-flight FPM request here."""
    match=re.fullmatch(r'wpiso-fpm-(php\d{2,3})-([a-z_][a-z0-9_-]*)\.service',unit)
    if not match:raise ValueError('Invalid elastic runtime unit')
    p=policy()
    if not p.get('accountRuntimeCaps',False):return None
    with lock('admission'):
        lease=RUN/'slots'/unit
        if not lease.exists():return None
        own=json.loads(lease.read_text());uid=pwd.getpwnam(match[2]).pw_uid
        if own.get('uid')!=uid:raise ValueError('Elastic runtime UID changed')
        native=int(own['nativeMaxChildren']);current=int(own['runtimeMaxChildren']);old_cost=int(own['costMiB'])
        if not 1<=current<=native<=128:raise ValueError('Invalid elastic worker lease')
        ceiling=runtime_ceiling(uid,native,p,limits['queue'],limits['timeout'])
        publish_runtime_demand(unit,uid,ceiling,demand,p['workerRssMiB']+48+p['opcacheMiB']+limits['memoryMiB'])
        peers=waiting_units(unit)
        leases={path.name:json.loads(path.read_text()) for path in (RUN/'slots').glob('*.service')}
        target=fair_demand_ceiling(unit,ceiling,demand,leases,peers,p)
        waiting=RUN/'waiting';waiting.mkdir(mode=0o700,exist_ok=True);ticket=waiting/unit
        def request(cap):
            atomic(ticket,json.dumps({'mode':'elastic','uid':uid,'ceiling':cap,
                'minimumMiB':p['workerRssMiB']+48+p['opcacheMiB']+limits['memoryMiB'],
                'expires':time.monotonic()+limits['timeout']+5}))
        if current>target:
            # No queued/forwarded request means this is an idle or post-response
            # backend. Let verified idle compaction/yield handle it; restarting
            # here would discard its warm cache or interrupt background work.
            if demand==0:
                clear_elastic_demand(unit);return None
            request(target)
            return {'ceiling':target,'previous':current,'reasonDetail':'peer_fair_share' if target<ceiling else 'account_boundary'}
        if demand<=current or current>=ceiling:
            clear_elastic_demand(unit);return None
        if current>=target:
            request(target);return None  # Let idle reservations yield without destabilizing busy peers.
        group=pathlib.Path('/sys/fs/cgroup'+account_cgroup(uid))
        boundary=int((group/'memory.max').read_text())*.9/1048576
        high=(group/'memory.high').read_text().strip()
        if high!='max':boundary=min(boundary,int(high)/1048576)
        _,_,working=account_memory_usage(int((group/'memory.current').read_text()),(group/'memory.stat').read_text())
        account_reserved=sum(int(row['costMiB']) for row in leases.values() if row.get('uid')==uid)
        account_available=boundary-max(account_reserved,working/1048576)+old_cost
        available=int(next(x.split()[1] for x in pathlib.Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))//1024
        # Credit only physically charged backend memory in the host-headroom check.
        charged=int((group/unit/'memory.current').read_text())/1048576
        reserved=sum(int(row['costMiB']) for name,row in leases.items() if name!=unit)
        granted,_=demand_grant(min(target,max(current,demand)),limits['memoryMiB'],p,reserved,
            available+min(old_cost,charged),account_available)
        if granted>current:
            if own.get('relayEnforced') and elastic_proxy_ready(unit):
                own.update(runtimeMaxChildren=granted,costMiB=granted*p['workerRssMiB']+48+p['opcacheMiB']+limits['memoryMiB'],lastResizeAt=time.time(),idleCompacted=False)
                atomic(lease,json.dumps(own));clear_elastic_demand(unit)
                return {'ceiling':granted,'previous':current,'reasonDetail':'queued_demand_growth','liveGrowth':True}
            request(granted)
            return {'ceiling':granted,'previous':current,'reasonDetail':'queued_demand_growth'}
        next_cost=(current+1)*p['workerRssMiB']+48+p['opcacheMiB']+limits['memoryMiB']
        if account_available>=next_cost and available-p['hostReserveMiB']>=p['workerRssMiB']:
            request(target)  # Partial grants must advertise unsatisfied demand too.
        else:clear_elastic_demand(unit)
        return None


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
    unit='[Unit]\nDescription=Bounded FastCGI admission for '+version+' '+user+'\n[Service]\nSlice='+account_slice(row['uid'])+'\nType=simple\nExecStart=/usr/bin/python3 '+str(SELF)+' proxy '+fpm+' '+str(backend)+' '+str(p['warmIdleSeconds'])+' '+str(limits['workers'])+' '+str(limits['queue'])+' '+str(limits['timeout'])+'\nMemoryMax='+str(limits['memoryMiB'])+'M\nMemorySwapMax=0\nTasksMax='+str(limits['tasks'])+'\nLimitNOFILE='+str(limits['fileLimit'])+'\nExecStopPost=/usr/bin/systemctl stop '+fpm+'\nTimeoutStopSec=20\n'
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
    ensure_native_cgroup_guard()
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
    regrant=False
    try:
        prior=json.loads(ticket.read_text()) if ticket.exists() else {}
        if (prior.get('mode')=='elastic' and prior.get('uid')==actual_uid
                and type(prior.get('expires')) in (int,float) and time.monotonic()<prior['expires']<float('inf')
                and type(prior.get('ceiling')) is int and 1<=prior['ceiling']<=children):
            grant_ceiling=prior['ceiling']
            regrant=True

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
                try:ceiling=runtime_ceiling(actual_uid,children,p,backlog,timeout)
                except (ValueError,OSError):
                    print(json.dumps({'event':'php_admission','at':time.time(),'unit':unit,'reason':'account_limits'}),file=sys.stderr,flush=True)
                    raise
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
                peer_demand=waiting_units(unit)
                if peer_demand:
                    grant_ceiling=min(grant_ceiling,contention_ceiling(ceiling,relay['memoryMiB'],p,len({x.name for x in lease_paths}|peer_demand|{unit})))
                relay_enforced=dynamic and elastic_proxy_ready(unit)
                # One cold request needs one reservation. Verified relays can
                # acquire further capacity before dispatching queued requests.
                if relay_enforced and not regrant:grant_ceiling=min(grant_ceiling,1)
                granted,cost=demand_grant(min(ceiling,grant_ceiling),relay['memoryMiB'],p,reserved,available,account_available)
                eligible=granted>=1 if dynamic else (granted==children and len(list(slots.iterdir()))<p['maxActivePools'])
                if eligible:
                    if dynamic:atomic(pool_path,private_backend(runtime_pool(pool,ceiling if relay_enforced else granted)))
                    atomic(lease,json.dumps({'costMiB':cost,'startedAt':time.time(),
                        'nativeMaxChildren':children,'accountCeiling':ceiling,'runtimeMaxChildren':granted,
                        'contentionCeiling':min(ceiling,grant_ceiling),'relayEnforced':relay_enforced,'fpmMaxChildren':ceiling if relay_enforced else granted,'uid':actual_uid,'mode':'account-aware' if dynamic else 'global-default',**accounting}));return
                # Do not recycle other accounts for this account's own RAM shortage.
                minimum=p['workerRssMiB']+48+p['opcacheMiB']+relay['memoryMiB']
                if dynamic and account_available>=minimum:
                    peers={x.name for x in lease_paths}|waiting_units()|{unit}
                    grant_ceiling=min(grant_ceiling,contention_ceiling(ceiling,relay['memoryMiB'],p,len(peers)))
                    atomic(ticket,json.dumps({'expires':deadline,'uid':actual_uid,'ceiling':grant_ceiling,'minimumMiB':minimum}))
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

def serve_proxy(listener,unit,backend,idle,limits,stop_backend=True,host_reserve_mib=0):
    """Fixed relays plus a bounded socket queue, all inside the existing account slice."""
    listener.settimeout(1)
    pending=queue.Queue(maxsize=limits['queue']);lock=threading.Lock();start_lock=threading.Lock()
    stopping=threading.Event();activity={'last':time.monotonic(),'active':0,'forwarded':0}
    dispatch=threading.Condition(lock);draining=False;regrant=None;rebalance_after=0;shrink_after=0;drain_deadline=0;dispatch_limit=1 if stop_backend else limits['workers']
    old_signals={}
    if threading.current_thread() is threading.main_thread():
        for sig in (signal.SIGTERM,signal.SIGINT):
            old_signals[sig]=signal.signal(sig,lambda *_:stopping.set())
    def diagnostic(reason, **details):
        print(json.dumps({'event':'php_proxy','at':time.time(),'unit':unit,'reason':reason,**details}),file=sys.stderr,flush=True)
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
                            if source is client:
                                if not forwarded:
                                    with lock:activity['forwarded']+=1
                                forwarded=True
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
            with dispatch:
                activity['active']-=1;activity['forwarded']-=int(forwarded)
                activity['last']=time.monotonic();dispatch.notify_all()
    def worker():
        while not stopping.is_set():
            with dispatch:
                while not stopping.is_set() and (draining or pending.empty() or activity['active']>=dispatch_limit):dispatch.wait(.25)
                if stopping.is_set():return
                try:item=pending.get_nowait()
                except queue.Empty:continue
                activity['active']+=1
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
            available=None
            if quiescent and host_reserve_mib:
                try:available=int(next(x.split()[1] for x in pathlib.Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))//1024
                except (OSError,ValueError,StopIteration):pass
            if stop_backend and time.monotonic()>=rebalance_after and not draining:
                rebalance_after=time.monotonic()+1
                try:
                    limit=runtime_dispatch_limit(unit,limits['workers'])
                    with dispatch:dispatch_limit=limit;dispatch.notify_all()
                    with lock:demand=activity['active']+pending.qsize()
                    plan=elastic_regrant_plan(unit,limits,demand)
                    if plan:
                        if plan.get('liveGrowth'):
                            with dispatch:dispatch_limit=runtime_dispatch_limit(unit,limits['workers']);dispatch.notify_all()
                            diagnostic('runtime_grant_grown',**plan)
                        elif time.monotonic()>=shrink_after:
                            # Rebalancing must not consume a whole client deadline while
                            # an unforwarded/background PHP job prevents idle proof.
                            # Retain the full charged grant and resume its queue if this
                            # small, native-timeout-derived drain window expires.
                            drain_budget=min(limits['timeout'],max(1,(limits['timeout']+19)//20))
                            with dispatch:draining=True;regrant=plan;drain_deadline=time.monotonic()+drain_budget
                            diagnostic('runtime_regrant_drain',drainBudgetSeconds=drain_budget,**plan)
                except Exception as error:
                    diagnostic('runtime_regrant_error',error=type(error).__name__)
                    rebalance_after=time.monotonic()+max(2,min(15,limits['timeout']/4))
            if draining:
                refresh_draining_demand(unit)
                with lock:drained=activity['active']==0
                if drained and not backend_drained(unit,backend):drained=False
                if not drained and time.monotonic()>=drain_deadline:
                    clear_elastic_demand(unit)
                    with dispatch:draining=False;regrant=None;dispatch.notify_all()
                    rebalance_after=time.monotonic()+max(2,min(15,limits['timeout']/4))
                    shrink_after=rebalance_after
                    diagnostic('runtime_regrant_deferred',reasonDetail='backend_not_proven_idle')
                if drained:
                    # Already-forwarded work completed before any backend stop.
                    # Queued requests keep their original deadline and are never replayed.
                    try:
                        result=execute(['systemctl','stop',unit],False,timeout=20)
                        if result.returncode:raise RuntimeError('Backend drain stop failed')
                        diagnostic('runtime_regrant_ready',**regrant)
                    except Exception as error:
                        clear_elastic_demand(unit)
                        diagnostic('runtime_regrant_failed',error=type(error).__name__)
                    finally:
                        with dispatch:draining=False;regrant=None;dispatch.notify_all()
                        with dispatch:dispatch_limit=1;dispatch.notify_all()
                        rebalance_after=time.monotonic()+1
                # Accept into the bounded queue while current work drains.
            has_lease=not stop_backend or (RUN/'slots'/unit).exists()
            elapsed=time.monotonic()-activity['last']
            pressure=has_lease and bool(waiting_units(unit))
            if stop_backend and quiescent and not draining:
                try:
                    # Native surplus children must have exited; a sole remaining
                    # child must be proven accepting. Do not add another arbitrary
                    # idle delay or compete with a dequeued request.
                    with dispatch:
                        if activity['active']==0 and pending.unfinished_tasks==0:
                            compacted=compact_idle_lease(unit,limits)
                            if compacted:
                                dispatch_limit=runtime_dispatch_limit(unit,limits['workers'])
                                diagnostic('idle_grant_compacted',**compacted)
                    pressure=has_lease and elapsed>=policy()['idleSeconds'] and idle_peer_pressure(unit,limits)
                except (OSError,ValueError,KeyError,TypeError) as error:
                    # Retain the conservative grant; an unknown state never releases
                    # memory reservations or forces a peer-driven cache eviction.
                    pressure=False;diagnostic('idle_compaction_unavailable',error=type(error).__name__)
            reason=None if draining else idle_retirement_reason(elapsed,int(idle),quiescent,pressure,available,host_reserve_mib)
            if reason and stop_backend and has_lease and not backend_drained(unit,backend):
                reason=None  # Relay completion does not prove post-response PHP finished.
            if reason:
                diagnostic('warm_idle_retire' if reason=='warm_idle_expired' else 'idle_lease_yield',reasonDetail=reason)
                return
            if pending.full():
                stopping.wait(.05);continue
            try:client,_=listener.accept()
            except socket.timeout:
                continue
            accepted=time.monotonic();deadline=accepted+limits['timeout']
            with lock:activity['last']=accepted
            # Apply backpressure; waiting requests never allocate a thread each.
            try:
                pending.put_nowait((client,deadline,accepted))
                with dispatch:
                    # New burst demand should not wait for the periodic tick.
                    # Allocation still passes the same locked budget checks.
                    if stop_backend and activity['active']+pending.qsize()>dispatch_limit:
                        # Wake live growth immediately, but never erase the
                        # separate cooldown of a deferred background-job drain.
                        rebalance_after=0
                    dispatch.notify_all()
            except queue.Full:
                diagnostic('queue_full_deadline',queued=pending.qsize())
                try:unavailable(client)
                except OSError:pass
                client.close()
    finally:
        stopping.set()
        with dispatch:dispatch.notify_all()
        if stop_backend:
            try:clear_elastic_demand(unit)
            except (OSError,ValueError,TypeError):pass
            try:clear_runtime_demand(unit)
            except OSError:pass  # Expiry still bounds a failed cleanup; finish shutdown.
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
    directory=RUN/'elastic-proxies';directory.mkdir(mode=0o700,exist_ok=True);marker=directory/unit
    pid=os.getpid();start=pathlib.Path('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19]
    atomic(marker,json.dumps({'protocol':1,'pid':pid,'startTicks':start}))
    listener=socket.fromfd(3,socket.AF_UNIX,socket.SOCK_STREAM)
    try:serve_proxy(listener,unit,backend,idle,limits,host_reserve_mib=policy()['hostReserveMiB'])
    finally:
        listener.close()
        try:
            if json.loads(marker.read_text()).get('pid')==pid:marker.unlink(missing_ok=True)
        except (OSError,ValueError,TypeError):pass



def release(unit):
    if not re.fullmatch(r'wpiso-fpm-php\d{2,3}-[a-z_][a-z0-9_-]*\.service',unit):raise ValueError('Invalid release unit')
    with lock('admission'):
        (RUN/'slots'/unit).unlink(missing_ok=True)
        # The proxy may still own queued work during a drained regrant.
        # Proxy shutdown clears demand; a crashed proxy expires automatically.

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
        if state['enabled'] in ('enabled','disabled'):
            # Restored owned symlinks already express enablement. Re-running enable
            # unnecessarily invokes Webuzo's SysV shim, which can lack runlevels.
            actual=execute(['systemctl','is-enabled',unit],False).stdout.strip()
            if actual!=state['enabled']:
                execute(['systemctl','enable' if state['enabled']=='enabled' else 'disable',unit])
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
            automatic_warm=current.get('warmIdleSeconds',warm_idle_seconds(current))==warm_idle_seconds(current)
            current['phpBudgetMiB']=budget
            if automatic_warm:current['warmIdleSeconds']=warm_idle_seconds(current)
            atomic(BASE/'policy.json',json.dumps(current,indent=2))
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
    return lifecycle_transaction(version,'onboard')


def retire(version):
    return lifecycle_transaction(version,'retire')


def _onboard(version):
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
            shutil.copy2(ctl, backups/version) # Rebase restoration onto the current vendor launcher; transaction archives the prior baseline.
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
                if time.monotonic() > deadline: raise RuntimeError('Native master did not stop gracefully; no forced kill: '+version)
                time.sleep(.1)
            atomic(ctl, wrapper(version), 0o755)
            print(version + ': repaired vendor-regenerated launcher')
        assert_launcher(version)
        ensure_health(version)
        unit = 'wpiso-manager-' + version + '.service'
        if execute(['systemctl', 'is-active', unit], False).returncode != 0:
            execute(['systemctl', 'enable', '--now', unit])
        # Native regeneration can leave the compatibility bridge inactive while
        # the coordinator is healthy. Repair and activate the checked bridge too.
        add_bridge(version)
        reconcile(version, True)
        print(version + ': already onboarded; refreshed coordinator and health master')
        return
    # Parse pools to validate configuration
    parse_pools((p/'etc/php-fpm.conf').read_text(), version,False)
    backups = STATE/'original-launchers'
    backups.mkdir(mode=0o700, exist_ok=True)
    archive = STATE/('backup-onboard-' + str(time.time_ns()))
    archive.mkdir(mode=0o700, exist_ok=True)
    ctl = p/'bin/fpmctl'
    if ctl.is_symlink(): raise RuntimeError('Unexpected launcher symlink ' + version)
    ctl_text = ctl.read_text()
    if MARKER in ctl_text: raise RuntimeError('Unregistered managed launcher; recover the lifecycle journal before onboarding: '+version)
    if MARKER not in ctl_text:
        shutil.copy2(ctl, archive/version)
        shutil.copy2(ctl, backups/version) # Current native baseline; historical snapshot is retained by transaction.
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
    except Exception:
        raise # Durable outer transaction restores registration, files and prior service states.


def _retire(version):
    if not re.fullmatch(r'php\d{2,3}', version): raise ValueError('Invalid PHP version: ' + str(version))
    if not is_managed(version):
        print(version + ': not currently managed in isolation; nothing to retire')
        return
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
    if path.exists() and path.read_text() == bridge(version):
        execute(['systemctl', 'stop', unit], timeout=90)
        wanted = UNITS/'multi-user.target.wants'/unit
        if wanted.is_symlink() and wanted.resolve() == path: wanted.unlink()
        path.unlink()
    execute(['systemctl', 'stop', 'wpiso-health-' + version + '.service'])
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
    (BASE/(version+'-health.conf')).unlink(missing_ok=True)
    for unit in lifecycle_units(version):execute(['systemctl','reset-failed',unit],False)
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
    ensure_native_cgroup_guard()
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
    drift_cache={}
    if account_slice(1).startswith('golden-') and pathlib.Path('/usr/local/webuzo/bin/cgroup.sh').exists():
        guard_ok=NATIVE_CGROUP_DROPIN.exists() and NATIVE_CGROUP_DROPIN.read_text()==native_guard_dropin() and execute(['systemctl','is-active','cgroup.service'],False).returncode==0
        results['nativeCgroupGuardActive']=guard_ok;results['mechanicalChecksPass']&=guard_ok
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
                grant=json.loads(lease.read_text()) if lease.exists() else {}
                item.update({'nativeMaxChildren':native,'accountWorkerCeiling':ceiling,
                    'managedMaxChildren':int(effective[1]) if effective else None,
                    'runtimeCapSource':'automatic-account-boundary' if results['policy'].get('accountRuntimeCaps') else 'native-global',
                    'reservedMiB':grant.get('costMiB',0),'runtimeConcurrencyGrant':grant.get('runtimeMaxChildren'),'relayEnforced':bool(grant.get('relayEnforced'))})
                if grant.get('relayEnforced'):
                    backend=RUN/(version+'-'+row['user']+'.sock')
                    backend_private=backend.exists() and backend.stat().st_uid==0 and backend.stat().st_mode&0o777==0o600
                    item['backendRootOnly']=backend_private
                    results['mechanicalChecksPass']&=backend_private and elastic_proxy_ready(fpm) and type(grant.get('runtimeMaxChildren')) is int and 1<=grant['runtimeMaxChildren']<=ceiling and int(effective[1])==ceiling
                if row['uid'] not in drift_cache:drift_cache[row['uid']]=native_cgroup_drift(row['uid'])
                item['processPlacement']=drift_cache[row['uid']];results['mechanicalChecksPass']&=item['processPlacement']['pass']
                results['mechanicalChecksPass']&=socket_ok and item['swapMax']=='0' and item['cpuMax'].split()[0]!='max' and item['memoryMax']!='max' and pwd.getpwnam(row['user']).pw_uid==row['uid'] and (not item['fpmActive'] or item['fpmControlGroup'].startswith(account_cgroup(row['uid'])+'/'));rows.append(item)
            health=execute(['systemctl','is-active','wpiso-health-'+version+'.service'],False).returncode==0
            native_unit=UNITS/('php-fpm'+version[3:]+'.service');bridge_ok=native_unit.exists() and native_unit.read_text()==bridge(version) and execute(['systemctl','is-active','php-fpm'+version[3:]+'.service'],False).returncode==0
            results['mechanicalChecksPass']&=active and bridge_ok and health;results['versions'][version]={'privateHealthMasterActive':health,'coordinatorActive':active,'nativeServiceBridgeActive':bridge_ok,'pools':rows}
        except Exception as e:results['mechanicalChecksPass']=False;results['versions'][version]={'error':str(e)}
    print(json.dumps(results,indent=2));return results['mechanicalChecksPass']

def uninstall():
    if pathlib.Path('/var/lib/golden-shield/installed.json').exists():
        raise RuntimeError('Remove Golden Shield through the reviewed dependency workflow before PHP isolation.')
    data=json.loads((STATE/'installed.json').read_text())
    versions=data.get('versions')
    if not isinstance(versions,list) or any(not isinstance(v,str) or not re.fullmatch(r'php\d{2,3}',v) for v in versions):
        raise ValueError('Invalid managed PHP registry; no services changed')
    # Validate the entire restore set before stopping the first coordinator.
    for version in versions:
        ctl=paths(version)/'bin/fpmctl';original=STATE/'original-launchers'/version
        if ctl.is_symlink() or original.is_symlink() or not ctl.is_file() or not original.is_file():
            raise RuntimeError('Unsafe or missing launcher recovery files: '+version)
        if ctl.read_text()!=wrapper(version) and ctl.read_bytes()!=original.read_bytes():
            raise RuntimeError('Launcher changed: manually review saved original before restoring '+version)
        native=UNITS/('php-fpm'+version[3:]+'.service')
        if native.is_symlink() or (native.exists() and native.read_text()!=bridge(version)):
            raise RuntimeError('Native service bridge changed; review before removal: '+version)
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
    remove_native_cgroup_guard()
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
    elif ns.command=='native-cgroup-install':print(json.dumps(ensure_native_cgroup_guard()))
    elif ns.command=='native-cgroup-remove':remove_native_cgroup_guard()
    elif ns.command=='native-cgroup-guard':native_cgroup_guard()
    elif ns.command=='native-cgroup-repair':print(json.dumps(native_cgroup_pass()))
    elif ns.command=='verify':sys.exit(0 if verify() else 1)
    elif ns.command=='reconcile':
        for version in json.loads((STATE/'installed.json').read_text())['versions']:reconcile(version,True)
    elif ns.command=='repair-launchers':
        data=json.loads((STATE/'installed.json').read_text()) if (STATE/'installed.json').exists() else {'versions':[]}
        for v in data.get('versions',[]):onboard(v)
    elif ns.command=='recover-lifecycle':recover_lifecycle()
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
