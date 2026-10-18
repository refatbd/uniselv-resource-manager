#!/usr/bin/python3
"""Checked installation/removal of plugin-owned protection dependencies."""
import json, os, pathlib, subprocess, sys, hashlib, time
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
    # Journal intent before each mutation; adopted implementations remain external.
    if not STATES['isolation'].exists():
        owned['isolation'] = True; data['state'] = 'installing-isolation'; save(data)
        # Physical budget only. PHP gets half the hosting pool; reserve the rest
        # for Apache, database, cache and accounting overhead.
        php_budget = max(256, policy['hostingMemoryMaxMiB'] // 2)
        pools = max(1, min(64, hw['cpu_count'], php_budget // 480))
        pool_budget = php_budget // pools
        opcache = min(128, max(32, pool_budget // 4))
        iso_policy = {'maxActivePools': pools, 'hostReserveMiB': policy['headroomMiB'],
            'poolBudgetMiB': pool_budget, 'phpBudgetMiB': php_budget,
            'workerRssMiB': max(64, min(288, pool_budget-opcache-64)), 'opcacheMiB': opcache, 'idleSeconds': 20}
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
