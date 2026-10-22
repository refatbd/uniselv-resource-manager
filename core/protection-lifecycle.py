#!/usr/bin/python3
"""Checked installation/removal of plugin-owned protection dependencies."""
import json, os, pathlib, subprocess, sys, hashlib, time, re, math
sys.path.insert(0, '/usr/local/uniselv-resman/agent')
ROOT = pathlib.Path('/var/lib/uniselv-resource-manager')
JOURNAL = ROOT / 'protection-lifecycle.json'
STATES = {'isolation': pathlib.Path('/var/lib/webuzo-isolation/installed.json'),
          'golden': pathlib.Path('/var/lib/golden-shield/installed.json'),
          'pam': pathlib.Path('/var/lib/webuzo-session-guard/files.json')}

def run(args):
    p = subprocess.run(args, capture_output=True, text=True, timeout=240)
    if p.returncode: raise RuntimeError(f'{args[1:3]} failed: {(p.stderr or p.stdout)[-1400:]}')
    return p.stdout

def save(data):
    ROOT.mkdir(parents=True, exist_ok=True)
    temp = JOURNAL.with_suffix('.new')
    temp.write_text(json.dumps(data, indent=2)); temp.chmod(0o600); os.replace(temp, JOURNAL)

def recover_existing_pam_registry():
    registry = STATES['pam']
    if registry.exists(): return False
    directory = registry.parent
    candidates = []
    for archive in directory.glob('uninstalled-files-*.json'):
        try:
            rows = json.loads(archive.read_text())
            if not isinstance(rows, dict) or not rows: continue
            fingerprints = {}
            for name, row in rows.items():
                path, backup = pathlib.Path(name), pathlib.Path(row['backup'])
                if path.parent != pathlib.Path('/etc/pam.d') or path.is_symlink() or backup.parent != directory or backup.is_symlink(): raise ValueError('Untrusted path')
                if hashlib.sha256(path.read_bytes()).hexdigest() != row['hash']: raise ValueError('Current hook differs')
                if hashlib.sha256(backup.read_bytes()).hexdigest() != row['originalHash']: raise ValueError('Original backup differs')
                fingerprints[name] = row['originalHash']
            candidates.append((archive, fingerprints))
        except (OSError, ValueError, KeyError, TypeError): continue
    if not candidates: return False
    if any(fingerprints != candidates[0][1] for _, fingerprints in candidates):
        raise RuntimeError('Conflicting PAM recovery records; retained for review')
    temporary = registry.with_suffix('.recovering')
    temporary.write_bytes(candidates[0][0].read_bytes()); temporary.chmod(0o600); os.replace(temporary, registry)
    return True

def native_admission_policy(php_budget, reserve):
    """Size admission from installed native pools/INI, never an invented per-pool cost."""
    costs=[];rss_values=[];cache_values=[];timeouts=[]
    def mib(value):
        match=re.fullmatch(r'\s*(\d+)\s*([KMG]?)\s*',str(value),re.I)
        if not match:raise ValueError('A finite PHP memory_limit is required for admission planning')
        return int(match[1])*{'':1/1048576,'K':1/1024,'M':1,'G':1024}[match[2].upper()]
    for directory in sorted(pathlib.Path('/usr/local/apps').glob('php*')):
        config=directory/'etc/php-fpm.conf';binary=directory/'bin/php'
        if not config.is_file() or not binary.is_file():continue
        text=config.read_text()
        children=[int(x) for x in re.findall(r'^\s*pm.max_children\s*=\s*(\d+)',text,re.M)]
        if not children:continue
        values=json.loads(run([str(binary),'-c',str(directory/'etc/php.ini'),'-r',
            'echo json_encode(["memory"=>ini_get("memory_limit"),"cache"=>ini_get("opcache.memory_consumption")]);']))
        memory=max([mib(values['memory'])]+[mib(x) for x in re.findall(r'^\s*php_(?:admin_)?value\[memory_limit\]\s*=\s*([^;\r\n]+)',text,re.M)])
        rss=max(96,math.ceil(memory+32));cache=max(0,int(values['cache'] or 0))
        if cache>512:raise ValueError('OPcache above 512 MiB requires a reviewed physical policy')
        backlogs=[int(x) for x in re.findall(r'^\s*listen.backlog\s*=\s*(\d+)',text,re.M)]
        backlog=max(backlogs or [511]);count=max(children)
        proxy_memory=24+count*2+(backlog+100)//100
        costs.append((count,backlog));rss_values.append(rss);cache_values.append(cache)
        for amount,unit in re.findall(r'^\s*request_terminate_timeout\s*=\s*(\d+)\s*([smhd]?)',text,re.M):
            seconds=int(amount)*{'':1,'s':1,'m':60,'h':3600,'d':86400}[unit]
            if seconds:timeouts.append(seconds)
    if not costs:raise RuntimeError('No eligible native PHP pools found; configure global PHP-FPM first')
    # Use the same conservative RSS/cache assumptions across all installed branches.
    pool_cost=max(count*max(rss_values)+48+max(cache_values)+24+count*2+(backlog+100)//100 for count,backlog in costs)
    minimum=max(rss_values)+48+max(cache_values)+max(24+count*2+(backlog+100)//100 for count,backlog in costs)
    if minimum>php_budget:raise RuntimeError('Shared physical PHP admission budget cannot fit one worker')
    return {'accountRuntimeCaps':True,'maxActivePools':min(64,php_budget//minimum),'hostReserveMiB':reserve,
        'poolBudgetMiB':pool_cost,'phpBudgetMiB':php_budget,'workerRssMiB':max(rss_values),
        'opcacheMiB':max(cache_values),'idleSeconds':20,'requestTimeoutSeconds':max(timeouts or [120])}


def reviewed_admission_policy(hw):
    """An explicit root-owned generator export is the optional policy authority.

    Never silently replace an adopted deployment. Hardware or native INI drift
    requires a new export/review; fallback sizing is used only without a profile.
    """
    path=pathlib.Path('/etc/webuzo-isolation/generator-profile.json')
    if not path.exists():return None
    stat=path.stat()
    if path.is_symlink() or stat.st_uid!=0 or stat.st_mode & 0o022:
        raise RuntimeError('Generator profile must be a root-owned, non-writable regular file')
    data=json.loads(path.read_text());config=data['configuration'];hardware=config['globalInputs']['hardware']
    if config.get('validationErrors'):
        raise RuntimeError('Generator export contains validation errors')
    if hardware.get('measuredRamMiB')!=hw['ram_total_mib'] or hardware.get('cpu')!=hw['cpu_count']:
        raise RuntimeError('Generator profile hardware changed; export and review again')
    versions=sorted(p.name for p in pathlib.Path('/usr/local/apps').glob('php*') if (p/'bin/php').is_file() and (p/'etc/php-fpm.conf').is_file())
    if sorted(hardware.get('phpVersions') or [])!=versions:
        raise RuntimeError('Generator PHP versions changed; export and review again')
    expected=config['sections']['isolation']['policy']
    total=hardware['measuredRamMiB'];reserve=expected['hostReserveMiB'];budget=expected['phpBudgetMiB']
    if not (isinstance(reserve,int) and isinstance(budget,int) and reserve>=512 and 0<budget<=total-reserve):
        raise RuntimeError('Generator profile exceeds physical memory')
    native=native_admission_policy(budget,reserve)
    if native!=expected:
        raise RuntimeError('Native PHP defaults differ from the reviewed generator policy')
    return native


def lifecycle(action):
    data = json.loads(JOURNAL.read_text()) if JOURNAL.exists() else {'owned': {}}
    owned = data.setdefault('owned', {})
    if action == 'uninstall':
        for name, script in [('pam', 'webuzo-session-guard-manager.py'), ('golden', 'golden-shield.py'), ('isolation', 'webuzo-isolation.py')]:
            if owned.get(name) and STATES[name].exists():
                run(['/usr/bin/python3', '/usr/local/sbin/' + script, 'uninstall'])
            if owned.get(name) and STATES[name].exists(): raise RuntimeError('Removal did not restore ' + name)
        data['state'] = 'removed'; save(data); return
    if action != 'install': raise ValueError('Use install or uninstall')
    if recover_existing_pam_registry():
        owned['pam'] = False; data['recovered_adopted_pam_registry'] = True; save(data)
    from golden_shield_manager import GoldenShieldManager
    manager = GoldenShieldManager()
    hw = manager.detect_hardware()
    policy = manager.calculate_auto_policy(hw)
    reviewed = reviewed_admission_policy(hw)
    if reviewed and STATES['isolation'].exists():
        current=json.loads(pathlib.Path('/etc/webuzo-isolation/policy.json').read_text())
        if any(current.get(key)!=value for key,value in reviewed.items()):
            raise RuntimeError('Installed admission policy differs from the reviewed generator export; reconcile before proceeding')
    # Journal intent before each mutation; adopted implementations remain external.
    if not STATES['isolation'].exists():
        owned['isolation'] = True; data['state'] = 'installing-isolation'; save(data)
        # Physical budget only. PHP gets half the hosting pool; reserve the rest
        # for Apache, database, cache and accounting overhead.
        php_budget = max(256, policy['hostingMemoryMaxMiB'] // 2)
        iso_policy = reviewed or native_admission_policy(php_budget, policy['headroomMiB'])
        candidate = ROOT / 'isolation-install-policy.json'; candidate.write_text(json.dumps(iso_policy))
        run(['/usr/bin/python3', '/usr/local/sbin/webuzo-isolation.py', 'install', str(candidate)])
    # Native provisioning/regeneration is asynchronous; allow bounded reconciliation.
    for attempt in range(10):
        try:
            run(['/usr/bin/python3', '/usr/local/sbin/webuzo-isolation.py', 'verify']); break
        except RuntimeError:
            if attempt == 9: raise
            time.sleep(2)
    if not STATES['golden'].exists():
        owned['golden'] = True; data['state'] = 'installing-golden'; save(data)
        mode = manager.get_persisted_mode()
        existing = manager.get_configured_policy()
        overrides = {key: existing[key] for key in ('customerCpuPercent', 'hostingMemoryMaxMiB') if key in existing} if mode == 'MANUAL' else None
        result = manager.reconfigure_or_enable(mode, overrides)
        if not result.get('success'): raise RuntimeError('Golden Shield: ' + str(result.get('error')))
    if not STATES['pam'].exists():
        owned['pam'] = True; data['state'] = 'installing-pam'; save(data)
        run(['/usr/bin/python3', '/usr/local/sbin/webuzo-session-guard-manager.py', 'install', '/usr/local/sbin/webuzo-session-guard.py'])
    run(['/usr/bin/python3', '/usr/local/sbin/webuzo-session-guard-manager.py', 'check'])
    verify = manager.verify_until_ready()
    if not verify.get('success'): raise RuntimeError('Final protection verification failed: ' + json.dumps(verify))
    data['state'] = 'verified'; save(data)

if __name__ == '__main__':
    try:
        if os.geteuid() != 0: raise PermissionError('Root required')
        lifecycle(sys.argv[1]); print('Protection lifecycle verified: ' + sys.argv[1])
    except Exception as error:
        print('PROTECTION LIFECYCLE FAILED: ' + str(error), file=sys.stderr); sys.exit(1)
