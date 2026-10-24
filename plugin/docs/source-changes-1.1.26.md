# Exact source changes â€” 1.1.26

Already-applied release source changes relative to 1.1.25; not extra post-install paste steps. Prefer the reviewed complete package.

- Back up existing files and ownership/restoration manifests together.
- Use UTF-8/LF. Replace existing files; do not append duplicate imports, functions or directives. New files start at their first line and end at their final line.
- Install through the reviewed privileged deployment workflow. Restore root ownership and installer execution modes.
- Run Python/PHP/JavaScript syntax, regression, service/API/HTTP and ZIP closure checks. Configuration values and full workload/lifecycle readiness remain distinct.

## uniselv-resman/agent/collector.py

Installed paths: /usr/local/webuzo/plugins/uniselv-resman/agent/collector.py; ALSO /usr/local/uniselv-resman/agent/collector.py

Replace the full file; never append duplicate functions/directives. New files run from first through final line.

### Block 1 â€” replace

Existing anchor AFTER which:
```text

    def read_user_cgroup(self, uid: int) -> Tuple[str, Dict[str, Any]]:
```

Existing anchor BEFORE which:
```text

        if not chosen:
```

Existing content to replace/remove (not copied):
```text
        """Locate active cgroup slice for UID and parse stats."""
        # Check native slice and golden shield slice
        candidates = [
            f'/sys/fs/cgroup/golden.slice/golden-{uid}.slice',
            f'/sys/fs/cgroup/{uid}.slice'
        ]
        chosen = None
        for cand in candidates:
            if os.path.exists(cand):
                chosen = cand
                # Prefer one that has current processes or memory > 0
                mem_cur = parse_int_file(os.path.join(cand, 'memory.current'))
                if mem_cur > 0:
                    break
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
        """Sum disjoint native/managed UID roots; never choose by resident memory.
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text

    def read_user_cgroup(self, uid: int) -> Tuple[str, Dict[str, Any]]:
        """Sum disjoint native/managed UID roots; never choose by resident memory.

        Historical charges can remain in an empty native root after migration.
```

### Block 2 â€” replace

Existing anchor AFTER which:
```text
                if mem_cur > 0:
                    break

```

Existing anchor BEFORE which:
```text
        return chosen, stats

```

Existing content to replace/remove (not copied):
```text
        if not chosen:
            chosen = f'/sys/fs/cgroup/{uid}.slice'

        stats = {
            'slice_path': chosen,
            'cpu_usage_usec': 0,
            'nr_throttled': 0,
            'throttled_usec': 0,
            'mem_current': 0,
            'mem_anon': 0,
            'mem_file': 0,
            'mem_swap': 0,
            'oom_kill': 0,
            'mem_high_events': 0,
            'mem_max_events': 0,
            'tasks_current': 0,
            'task_limit_events': 0,
            'io': {'rbytes': 0, 'wbytes': 0, 'rios': 0, 'wios': 0}
        }

        if os.path.exists(chosen):
            # CPU
            cpu_stat = parse_key_value_file(os.path.join(chosen, 'cpu.stat'))
            stats['cpu_usage_usec'] = int(cpu_stat.get('usage_usec', 0))
            stats['nr_throttled'] = int(cpu_stat.get('nr_throttled', 0))
            stats['throttled_usec'] = int(cpu_stat.get('throttled_usec', 0))

            # Memory
            stats['mem_current'] = parse_int_file(os.path.join(chosen, 'memory.current'))
            stats['mem_swap'] = parse_int_file(os.path.join(chosen, 'memory.swap.current'))
            mem_stat = parse_key_value_file(os.path.join(chosen, 'memory.stat'))
            stats['mem_anon'] = int(mem_stat.get('anon', 0))
            stats['mem_file'] = int(mem_stat.get('file', 0))

            mem_events = parse_key_value_file(os.path.join(chosen, 'memory.events'))
            stats['oom_kill'] = int(mem_events.get('oom_kill', 0))
            stats['mem_high_events'] = int(mem_events.get('high', 0))
            stats['mem_max_events'] = int(mem_events.get('max', 0))

            # Tasks
            stats['tasks_current'] = parse_int_file(os.path.join(chosen, 'pids.current'))
            pid_events = parse_key_value_file(os.path.join(chosen, 'pids.events'))
            stats['task_limit_events'] = int(pid_events.get('max', 0))

            # IO
            stats['io'] = parse_io_stat(os.path.join(chosen, 'io.stat'))

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
        Historical charges can remain in an empty native root after migration.
        Count those honestly, but use cgroup.events/populated for live drift.
        Each root includes descendants already; do not add child counters again.
        """
        candidates = [f'/sys/fs/cgroup/golden.slice/golden-{uid}.slice', f'/sys/fs/cgroup/{uid}.slice']
        golden_active = os.path.exists('/var/lib/golden-shield/installed.json') and not os.path.exists('/var/lib/golden-shield/disabling.json')
        if not golden_active: candidates.reverse()
        sources = [p for p in candidates if os.path.exists(p)]
        chosen = sources[0] if sources else f'/sys/fs/cgroup/{uid}.slice'
        stats = {'slice_path': chosen, 'slice_paths': sources,
                 'isolation_drift': False, 'cpu_usage_usec': 0, 'nr_throttled': 0,
                 'throttled_usec': 0, 'mem_current': 0, 'mem_anon': 0, 'mem_file': 0,
                 'mem_swap': 0, 'oom_kill': 0, 'mem_high_events': 0, 'mem_max_events': 0,
                 'tasks_current': 0, 'task_limit_events': 0,
                 'io': {'rbytes': 0, 'wbytes': 0, 'rios': 0, 'wios': 0}}
        for source in sources:
            cpu = parse_key_value_file(os.path.join(source, 'cpu.stat'))
            for dst, key in [('cpu_usage_usec','usage_usec'),('nr_throttled','nr_throttled'),('throttled_usec','throttled_usec')]:
                stats[dst] += int(cpu.get(key, 0))
            for dst, filename in [('mem_current','memory.current'),('mem_swap','memory.swap.current'),('tasks_current','pids.current')]:
                stats[dst] += parse_int_file(os.path.join(source, filename))
            memory = parse_key_value_file(os.path.join(source, 'memory.stat'))
            stats['mem_anon'] += int(memory.get('anon', 0)); stats['mem_file'] += int(memory.get('file', 0))
            events = parse_key_value_file(os.path.join(source, 'memory.events'))
            for dst,key in [('oom_kill','oom_kill'),('mem_high_events','high'),('mem_max_events','max')]:
                stats[dst] += int(events.get(key, 0))
            stats['task_limit_events'] += int(parse_key_value_file(os.path.join(source, 'pids.events')).get('max', 0))
            io = parse_io_stat(os.path.join(source, 'io.stat'))
            for key in stats['io']: stats['io'][key] += io.get(key, 0)
            if source != chosen:
                populated = parse_key_value_file(os.path.join(source, 'cgroup.events')).get('populated', 0)
                stats['isolation_drift'] |= int(populated) > 0
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
        """Sum disjoint native/managed UID roots; never choose by resident memory.

        Historical charges can remain in an empty native root after migration.
        Count those honestly, but use cgroup.events/populated for live drift.
        Each root includes descendants already; do not add child counters again.
        """
        candidates = [f'/sys/fs/cgroup/golden.slice/golden-{uid}.slice', f'/sys/fs/cgroup/{uid}.slice']
        golden_active = os.path.exists('/var/lib/golden-shield/installed.json') and not os.path.exists('/var/lib/golden-shield/disabling.json')
        if not golden_active: candidates.reverse()
        sources = [p for p in candidates if os.path.exists(p)]
        chosen = sources[0] if sources else f'/sys/fs/cgroup/{uid}.slice'
        stats = {'slice_path': chosen, 'slice_paths': sources,
                 'isolation_drift': False, 'cpu_usage_usec': 0, 'nr_throttled': 0,
                 'throttled_usec': 0, 'mem_current': 0, 'mem_anon': 0, 'mem_file': 0,
                 'mem_swap': 0, 'oom_kill': 0, 'mem_high_events': 0, 'mem_max_events': 0,
                 'tasks_current': 0, 'task_limit_events': 0,
                 'io': {'rbytes': 0, 'wbytes': 0, 'rios': 0, 'wios': 0}}
        for source in sources:
            cpu = parse_key_value_file(os.path.join(source, 'cpu.stat'))
            for dst, key in [('cpu_usage_usec','usage_usec'),('nr_throttled','nr_throttled'),('throttled_usec','throttled_usec')]:
                stats[dst] += int(cpu.get(key, 0))
            for dst, filename in [('mem_current','memory.current'),('mem_swap','memory.swap.current'),('tasks_current','pids.current')]:
                stats[dst] += parse_int_file(os.path.join(source, filename))
            memory = parse_key_value_file(os.path.join(source, 'memory.stat'))
            stats['mem_anon'] += int(memory.get('anon', 0)); stats['mem_file'] += int(memory.get('file', 0))
            events = parse_key_value_file(os.path.join(source, 'memory.events'))
            for dst,key in [('oom_kill','oom_kill'),('mem_high_events','high'),('mem_max_events','max')]:
                stats[dst] += int(events.get(key, 0))
            stats['task_limit_events'] += int(parse_key_value_file(os.path.join(source, 'pids.events')).get('max', 0))
            io = parse_io_stat(os.path.join(source, 'io.stat'))
            for key in stats['io']: stats['io'][key] += io.get(key, 0)
            if source != chosen:
                populated = parse_key_value_file(os.path.join(source, 'cgroup.events')).get('populated', 0)
                stats['isolation_drift'] |= int(populated) > 0
        return chosen, stats

```

### Block 3 â€” replace

Existing anchor AFTER which:
```text
        """Get list of active processes belonging to user with sanitized cmdline."""
        procs = []
```

Existing anchor BEFORE which:
```text
        pids = []
        if os.path.exists(pids_file):
```

Existing content to replace/remove (not copied):
```text
        pids_file = os.path.join(slice_path, 'cgroup.procs')
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
        # Enumerate by actual UID: service children and migration drift must not
        # disappear merely because the account root has only proxy processes.
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
        """Get list of active processes belonging to user with sanitized cmdline."""
        procs = []
        # Enumerate by actual UID: service children and migration drift must not
        # disappear merely because the account root has only proxy processes.
        pids = []
        for entry in os.listdir('/proc'):
```

### Block 4 â€” replace

Existing anchor AFTER which:
```text
        pids_file = os.path.join(slice_path, 'cgroup.procs')
        pids = []
```

Existing anchor BEFORE which:
```text

        uptime = 0.0
```

Existing content to replace/remove (not copied):
```text
        if os.path.exists(pids_file):
            try:
                with open(pids_file, 'r') as f:
                    pids = [int(p.strip()) for p in f if p.strip().isdigit()]
            except Exception:
                pass

        # If cgroup.procs is empty, also check by UID in /proc as fallback
        if not pids:
            for entry in os.listdir('/proc'):
                if entry.isdigit():
                    pid = int(entry)
                    try:
                        stat_path = f'/proc/{pid}'
                        if os.stat(stat_path).st_uid == uid:
                            pids.append(pid)
                    except Exception:
                        pass
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
        for entry in os.listdir('/proc'):
            if entry.isdigit():
                try:
                    if os.stat('/proc/' + entry).st_uid == uid: pids.append(int(entry))
                except (FileNotFoundError, ProcessLookupError, PermissionError): pass
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
        # disappear merely because the account root has only proxy processes.
        pids = []
        for entry in os.listdir('/proc'):
            if entry.isdigit():
                try:
                    if os.stat('/proc/' + entry).st_uid == uid: pids.append(int(entry))
                except (FileNotFoundError, ProcessLookupError, PermissionError): pass

        uptime = 0.0
```

### Block 5 â€” insert

Existing anchor AFTER which:
```text
        for pid in pids:
            try:
```

Existing anchor BEFORE which:
```text
                proc_stat_path = f'/proc/{pid}/stat'
                cmdline_path = f'/proc/{pid}/cmdline'
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                if os.stat(f'/proc/{pid}').st_uid != uid: continue
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
        for pid in pids:
            try:
                if os.stat(f'/proc/{pid}').st_uid != uid: continue
                proc_stat_path = f'/proc/{pid}/stat'
                cmdline_path = f'/proc/{pid}/cmdline'
```

## uniselv-resman/agent/ipc_server.py

Installed paths: /usr/local/webuzo/plugins/uniselv-resman/agent/ipc_server.py; ALSO /usr/local/uniselv-resman/agent/ipc_server.py

Replace the full file; never append duplicate functions/directives. New files run from first through final line.

### Block 1 â€” insert

Existing anchor AFTER which:
```text
        users = self.collector.get_webuzo_users()
        audit_results = []
```

Existing anchor BEFORE which:
```text
        for uname, udata in users.items():
            uid = udata['uid']
            plan_name = udata['plan_name']
            limits = self.collector.get_plan_limits(plan_name)
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
        outside_users = {r['username'] for r in self.action_admin_out_of_boundary().get('out_of_bounds_processes', [])}
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
        users = self.collector.get_webuzo_users()
        audit_results = []
        outside_users = {r['username'] for r in self.action_admin_out_of_boundary().get('out_of_bounds_processes', [])}
        for uname, udata in users.items():
            uid = udata['uid']
```

### Block 2 â€” replace

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
                cpu_synced and 
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

### Block 3 â€” insert

Existing anchor AFTER which:
```text
                'effective_wiops': effective_wiops,
                'is_synchronized': is_synchronized,
```

Existing anchor BEFORE which:
```text
                'cpu_synced': cpu_synced,
                'mem_synced': mem_synced,
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                'process_placement_synced': uname not in outside_users,
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                'effective_wiops': effective_wiops,
                'is_synchronized': is_synchronized,
                'process_placement_synced': uname not in outside_users,
                'cpu_synced': cpu_synced,
                'mem_synced': mem_synced,
```

### Block 4 â€” insert

Existing anchor AFTER which:
```text
                    p_uid = stat.st_uid
                    if p_uid in uid_to_user:
```

Existing anchor BEFORE which:
```text
                        cgroup_content = pathlib.Path(f'/proc/{pid}/cgroup').read_text().strip()
                        # Defect F Fix: Exact cgroup path match, not substring 'golden'
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                        # Apache workers can temporarily adopt a request UID via
                        # mod_ruid2; they remain a shared, aggregate-owned service.
                        if os.readlink(f'/proc/{pid}/exe') == '/usr/local/apps/apache2/bin/httpd': continue
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                    p_uid = stat.st_uid
                    if p_uid in uid_to_user:
                        # Apache workers can temporarily adopt a request UID via
                        # mod_ruid2; they remain a shared, aggregate-owned service.
                        if os.readlink(f'/proc/{pid}/exe') == '/usr/local/apps/apache2/bin/httpd': continue
                        cgroup_content = pathlib.Path(f'/proc/{pid}/cgroup').read_text().strip()
                        # Defect F Fix: Exact cgroup path match, not substring 'golden'
```

### Block 5 â€” replace

Existing anchor AFTER which:
```text
                        cgroup_content = pathlib.Path(f'/proc/{pid}/cgroup').read_text().strip()
                        # Defect F Fix: Exact cgroup path match, not substring 'golden'
```

Existing anchor BEFORE which:
```text
                        is_contained = (cgroup_content == f"0::{expected_slice}" or 
                                        cgroup_content.startswith(f"0::{expected_slice}/"))
```

Existing content to replace/remove (not copied):
```text
                        expected_slice = f"/golden.slice/golden-{p_uid}.slice"
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                        golden_active = pathlib.Path('/var/lib/golden-shield/installed.json').exists() and not pathlib.Path('/var/lib/golden-shield/disabling.json').exists()
                        expected_slice = f"/golden.slice/golden-{p_uid}.slice" if golden_active else f"/{p_uid}.slice"
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                        cgroup_content = pathlib.Path(f'/proc/{pid}/cgroup').read_text().strip()
                        # Defect F Fix: Exact cgroup path match, not substring 'golden'
                        golden_active = pathlib.Path('/var/lib/golden-shield/installed.json').exists() and not pathlib.Path('/var/lib/golden-shield/disabling.json').exists()
                        expected_slice = f"/golden.slice/golden-{p_uid}.slice" if golden_active else f"/{p_uid}.slice"
                        is_contained = (cgroup_content == f"0::{expected_slice}" or 
                                        cgroup_content.startswith(f"0::{expected_slice}/"))
```

### Block 6 â€” insert

Existing anchor AFTER which:
```text
        except (OSError, ValueError):
            cap_display, cap_bytes = 'Unavailable', None
```

Existing anchor BEFORE which:
```text
        return {
            'memory_cap_formatted': cap_display,
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
        placement = {'status': 'UNAVAILABLE', 'accounts_checked': 0, 'drift_accounts': [], 'native_guard': 'unavailable'}
        try:
            for name, row in self.collector.get_webuzo_users().items():
                if int(row.get('uid', 0)) <= 0: continue
                _, metrics = self.collector.read_user_cgroup(int(row['uid']))
                placement['accounts_checked'] += 1
                if metrics.get('isolation_drift') or not metrics.get('slice_paths'): placement['drift_accounts'].append(name)
            guard = pathlib.Path('/etc/systemd/system/cgroup.service.d/90-uniselv-resman.conf')
            for row in self.action_admin_out_of_boundary().get('out_of_bounds_processes', []):
                if row['username'] not in placement['drift_accounts']: placement['drift_accounts'].append(row['username'])
            required = pathlib.Path('/var/lib/golden-shield/installed.json').exists() and not pathlib.Path('/var/lib/golden-shield/disabling.json').exists() and pathlib.Path('/usr/local/webuzo/bin/cgroup.sh').exists()
            live = subprocess.run(['systemctl', 'show', 'cgroup.service', '-p', 'ActiveState', '-p', 'ExecStart'], capture_output=True, text=True, timeout=3)
            active = guard.is_file() and 'ActiveState=active' in live.stdout and 'native-cgroup-guard' in live.stdout
            placement['native_guard'] = ('active' if active else 'missing_or_inactive') if required else 'not_required'
            placement['status'] = 'DRIFT' if placement['drift_accounts'] or (required and not active) else ('PASS' if placement['accounts_checked'] else 'UNAVAILABLE')
        except (OSError, ValueError, subprocess.SubprocessError, AttributeError):
            pass
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
        except (OSError, ValueError):
            cap_display, cap_bytes = 'Unavailable', None
        placement = {'status': 'UNAVAILABLE', 'accounts_checked': 0, 'drift_accounts': [], 'native_guard': 'unavailable'}
        try:
            for name, row in self.collector.get_webuzo_users().items():
                if int(row.get('uid', 0)) <= 0: continue
                _, metrics = self.collector.read_user_cgroup(int(row['uid']))
                placement['accounts_checked'] += 1
                if metrics.get('isolation_drift') or not metrics.get('slice_paths'): placement['drift_accounts'].append(name)
            guard = pathlib.Path('/etc/systemd/system/cgroup.service.d/90-uniselv-resman.conf')
            for row in self.action_admin_out_of_boundary().get('out_of_bounds_processes', []):
                if row['username'] not in placement['drift_accounts']: placement['drift_accounts'].append(row['username'])
            required = pathlib.Path('/var/lib/golden-shield/installed.json').exists() and not pathlib.Path('/var/lib/golden-shield/disabling.json').exists() and pathlib.Path('/usr/local/webuzo/bin/cgroup.sh').exists()
            live = subprocess.run(['systemctl', 'show', 'cgroup.service', '-p', 'ActiveState', '-p', 'ExecStart'], capture_output=True, text=True, timeout=3)
            active = guard.is_file() and 'ActiveState=active' in live.stdout and 'native-cgroup-guard' in live.stdout
            placement['native_guard'] = ('active' if active else 'missing_or_inactive') if required else 'not_required'
            placement['status'] = 'DRIFT' if placement['drift_accounts'] or (required and not active) else ('PASS' if placement['accounts_checked'] else 'UNAVAILABLE')
        except (OSError, ValueError, subprocess.SubprocessError, AttributeError):
            pass
        return {
            'cgroup_integrity': placement,
```

### Block 7 â€” insert

Existing anchor AFTER which:
```text
            cap_display, cap_bytes = 'Unavailable', None
        return {
```

Existing anchor BEFORE which:
```text
            'memory_cap_formatted': cap_display,
            'agent_pid': daemon_pid,
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
            'cgroup_integrity': placement,
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
            pass
        return {
            'cgroup_integrity': placement,
            'memory_cap_formatted': cap_display,
            'agent_pid': daemon_pid,
```

## uniselv-resman/core/golden-shield.py

Installed paths: /usr/local/webuzo/plugins/uniselv-resman/core/golden-shield.py; ALSO /usr/local/uniselv-resman/core/golden-shield.py; ALSO /usr/local/sbin/golden-shield.py

Replace the full file; never append duplicate functions/directives. New files run from first through final line.

### Block 1 â€” replace

Existing anchor AFTER which:
```text
 # Socket proxies are hosting work too; keep them inside the same aggregate parent.
 compile(source,str(ISO),'exec');managed(ISO,source,0o755)
```

Existing anchor BEFORE which:
```text
def remember(unit,settings):
 path=STATE/'shared-properties.json';data=json.loads(path.read_text()) if path.exists() else {}
```

Existing content to replace/remove (not copied):
```text
 scanner=SCANNER.read_text();needle='\t\t\t\techo $pid >>'
 if needle not in scanner:raise RuntimeError('Unsupported native process scanner.')
 scanner=scanner if "grep -q '/golden.slice/' /proc/$pid/cgroup 2>/dev/null && continue" in scanner else scanner.replace(needle,"\t\t\t\t# Golden Shield: never move already-contained workers out of the aggregate group.\n\t\t\t\tgrep -q '/golden.slice/' /proc/$pid/cgroup 2>/dev/null && continue\n"+needle)
 managed(SCANNER,scanner,0o755)
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
 # The owned service drop-in survives a vendor scanner refresh.
 command(['/usr/bin/python3',str(ISO),'native-cgroup-install'])

```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
 # Socket proxies are hosting work too; keep them inside the same aggregate parent.
 compile(source,str(ISO),'exec');managed(ISO,source,0o755)
 # The owned service drop-in survives a vendor scanner refresh.
 command(['/usr/bin/python3',str(ISO),'native-cgroup-install'])

def remember(unit,settings):
 path=STATE/'shared-properties.json';data=json.loads(path.read_text()) if path.exists() else {}
```

### Block 2 â€” replace

Existing anchor AFTER which:
```text
 if not (STATE/'installed.json').exists():raise RuntimeError('No partial installation to resume')
 prerequisites(policy());data=files()
```

Existing anchor BEFORE which:
```text
 if not INIT.is_symlink():required.append(str(INIT))
 elif INIT.resolve()!=APACHE.resolve():raise RuntimeError('Apache init target changed')
```

Existing content to replace/remove (not copied):
```text
 required=[str(ISO),str(SCANNER),str(APACHE),str(UNITS/'httpd.service'),str(UNITS/'mariadb.service.d'/'90-golden-shared.conf')]
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
 required=[str(ISO),str(APACHE),str(UNITS/'httpd.service'),str(UNITS/'mariadb.service.d'/'90-golden-shared.conf')]
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
 if not (STATE/'installed.json').exists():raise RuntimeError('No partial installation to resume')
 prerequisites(policy());data=files()
 required=[str(ISO),str(APACHE),str(UNITS/'httpd.service'),str(UNITS/'mariadb.service.d'/'90-golden-shared.conf')]
 if not INIT.is_symlink():required.append(str(INIT))
 elif INIT.resolve()!=APACHE.resolve():raise RuntimeError('Apache init target changed')
```

### Block 3 â€” insert

Existing anchor AFTER which:
```text
 versions=json.loads(pathlib.Path('/var/lib/webuzo-isolation/installed.json').read_text())['versions']
 for version in versions:command(['systemctl','stop','wpiso-manager-'+version+'.service'])
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
 command(['/usr/bin/python3',str(ISO),'native-cgroup-remove'])
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
 versions=json.loads(pathlib.Path('/var/lib/webuzo-isolation/installed.json').read_text())['versions']
 for version in versions:command(['systemctl','stop','wpiso-manager-'+version+'.service'])
 command(['/usr/bin/python3',str(ISO),'native-cgroup-remove'])
 for name,row in data.items():
  path=pathlib.Path(name)
```

## uniselv-resman/core/webuzo-isolation.py

Installed paths: /usr/local/webuzo/plugins/uniselv-resman/core/webuzo-isolation.py; ALSO /usr/local/uniselv-resman/core/webuzo-isolation.py; ALSO /usr/local/sbin/webuzo-isolation.py

Replace the full file; never append duplicate functions/directives. New files run from first through final line.

### Block 1 â€” replace

Existing anchor AFTER which:
```text
PROXY='/usr/lib/systemd/systemd-socket-proxyd'
MARKER='# WEBUZO-ISOLATION MANAGED LAUNCHER'
```

Existing anchor BEFORE which:
```text

# Self-contained fallback: no PHP, external assets, scripts, or template file I/O.
```

Existing content to replace/remove (not copied):
```text
CAPACITY_MODEL_VERSION='account-demand-v4'
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
CAPACITY_MODEL_VERSION='account-demand-v5-warm'
NATIVE_CGROUP_USERS=pathlib.Path('/var/webuzo/conf/cgroupusers')
NATIVE_CGROUP_DROPIN=UNITS/'cgroup.service.d/90-uniselv-resman.conf'
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
PROXY='/usr/lib/systemd/systemd-socket-proxyd'
MARKER='# WEBUZO-ISOLATION MANAGED LAUNCHER'
CAPACITY_MODEL_VERSION='account-demand-v5-warm'
NATIVE_CGROUP_USERS=pathlib.Path('/var/webuzo/conf/cgroupusers')
NATIVE_CGROUP_DROPIN=UNITS/'cgroup.service.d/90-uniselv-resman.conf'

# Self-contained fallback: no PHP, external assets, scripts, or template file I/O.
```

### Block 2 â€” insert

Existing anchor AFTER which:
```text
    if data['opcacheMiB']>512 or data['maxActivePools']>64 or data['idleSeconds']<15:raise ValueError('Policy outside tested limits')
    if type(data.get('accountRuntimeCaps',False)) is not bool:raise ValueError('Invalid accountRuntimeCaps')
```

Existing anchor BEFORE which:
```text
    return data

```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
    # Retire ondemand workers independently; preserve the master's opcode cache
    # while measured headroom permits. Waiting peers can reclaim its lease early.
    data.setdefault('warmIdleSeconds',warm_idle_seconds(data))
    if type(data['warmIdleSeconds']) is not int or not 15<=data['warmIdleSeconds']<=3600:raise ValueError('Invalid warmIdleSeconds')
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
    if data['opcacheMiB']>512 or data['maxActivePools']>64 or data['idleSeconds']<15:raise ValueError('Policy outside tested limits')
    if type(data.get('accountRuntimeCaps',False)) is not bool:raise ValueError('Invalid accountRuntimeCaps')
    # Retire ondemand workers independently; preserve the master's opcode cache
    # while measured headroom permits. Waiting peers can reclaim its lease early.
    data.setdefault('warmIdleSeconds',warm_idle_seconds(data))
    if type(data['warmIdleSeconds']) is not int or not 15<=data['warmIdleSeconds']<=3600:raise ValueError('Invalid warmIdleSeconds')
    return data

```

### Block 3 â€” insert

Existing anchor AFTER which:
```text
    if type(data.get('accountRuntimeCaps',False)) is not bool:raise ValueError('Invalid accountRuntimeCaps')
    return data
```

Existing anchor BEFORE which:
```text

def versions():
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text


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
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
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
```

### Block 4 â€” replace

Existing anchor AFTER which:
```text
    unit='[Unit]\nDescription=Isolated Webuzo PHP pool '+version+' '+user+'\nStopWhenUnneeded=no\nRequires='+str(row['uid'])+'.slice\nAfter='+str(row['uid'])+'.slice\n[Service]\nType=simple\nSlice='+account_slice(row['uid'])+'\nWorkingDirectory='+str(prefix)+'\nExecStartPre=/usr/bin/python3 '+str(SELF)+' admit '+fpm+' '+str(row['maxChildren'])+'\nExecStart='+str(prefix/'sbin/php-fpm')+' -F -y '+str(config)+' -c '+str(prefix/'etc/php.ini')+' -d opcache.memory_consumption='+str(p['opcacheMiB'])+'\nExecStartPost=/usr/bin/python3 '+str(SELF)+' wait-socket '+str(backend)+'\nExecStopPost=/usr/bin/python3 '+str(SELF)+' release '+fpm+'\nKillSignal=SIGTERM\nTimeoutStartSec=45\nTimeoutStopSec=10\nRestart=no\n'
    atomic(UNITS/fpm,unit,0o644)
```

Existing anchor BEFORE which:
```text
    atomic(UNITS/proxy,unit,0o644)
    unit='[Unit]\nDescription=Preserve native Webuzo socket for '+version+' '+user+'\n[Socket]\nListenStream='+row['originalSocket']+'\nSocketUser=nobody\nSocketGroup=nobody\nSocketMode=0660\nDirectoryMode=0755\nBacklog='+str(row['backlog'])+'\nRemoveOnStop=yes\nService='+proxy+'\n'
```

Existing content to replace/remove (not copied):
```text
    unit='[Unit]\nDescription=Bounded FastCGI admission for '+version+' '+user+'\n[Service]\nSlice='+account_slice(row['uid'])+'\nType=simple\nExecStart=/usr/bin/python3 '+str(SELF)+' proxy '+fpm+' '+str(backend)+' '+str(p['idleSeconds'])+' '+str(limits['workers'])+' '+str(limits['queue'])+' '+str(limits['timeout'])+'\nMemoryMax='+str(limits['memoryMiB'])+'M\nMemorySwapMax=0\nTasksMax='+str(limits['tasks'])+'\nLimitNOFILE='+str(limits['fileLimit'])+'\nExecStopPost=/usr/bin/systemctl stop '+fpm+'\nTimeoutStopSec=20\n'
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
    unit='[Unit]\nDescription=Bounded FastCGI admission for '+version+' '+user+'\n[Service]\nSlice='+account_slice(row['uid'])+'\nType=simple\nExecStart=/usr/bin/python3 '+str(SELF)+' proxy '+fpm+' '+str(backend)+' '+str(p['warmIdleSeconds'])+' '+str(limits['workers'])+' '+str(limits['queue'])+' '+str(limits['timeout'])+'\nMemoryMax='+str(limits['memoryMiB'])+'M\nMemorySwapMax=0\nTasksMax='+str(limits['tasks'])+'\nLimitNOFILE='+str(limits['fileLimit'])+'\nExecStopPost=/usr/bin/systemctl stop '+fpm+'\nTimeoutStopSec=20\n'
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
    unit='[Unit]\nDescription=Isolated Webuzo PHP pool '+version+' '+user+'\nStopWhenUnneeded=no\nRequires='+str(row['uid'])+'.slice\nAfter='+str(row['uid'])+'.slice\n[Service]\nType=simple\nSlice='+account_slice(row['uid'])+'\nWorkingDirectory='+str(prefix)+'\nExecStartPre=/usr/bin/python3 '+str(SELF)+' admit '+fpm+' '+str(row['maxChildren'])+'\nExecStart='+str(prefix/'sbin/php-fpm')+' -F -y '+str(config)+' -c '+str(prefix/'etc/php.ini')+' -d opcache.memory_consumption='+str(p['opcacheMiB'])+'\nExecStartPost=/usr/bin/python3 '+str(SELF)+' wait-socket '+str(backend)+'\nExecStopPost=/usr/bin/python3 '+str(SELF)+' release '+fpm+'\nKillSignal=SIGTERM\nTimeoutStartSec=45\nTimeoutStopSec=10\nRestart=no\n'
    atomic(UNITS/fpm,unit,0o644)
    unit='[Unit]\nDescription=Bounded FastCGI admission for '+version+' '+user+'\n[Service]\nSlice='+account_slice(row['uid'])+'\nType=simple\nExecStart=/usr/bin/python3 '+str(SELF)+' proxy '+fpm+' '+str(backend)+' '+str(p['warmIdleSeconds'])+' '+str(limits['workers'])+' '+str(limits['queue'])+' '+str(limits['timeout'])+'\nMemoryMax='+str(limits['memoryMiB'])+'M\nMemorySwapMax=0\nTasksMax='+str(limits['tasks'])+'\nLimitNOFILE='+str(limits['fileLimit'])+'\nExecStopPost=/usr/bin/systemctl stop '+fpm+'\nTimeoutStopSec=20\n'
    atomic(UNITS/proxy,unit,0o644)
    unit='[Unit]\nDescription=Preserve native Webuzo socket for '+version+' '+user+'\n[Socket]\nListenStream='+row['originalSocket']+'\nSocketUser=nobody\nSocketGroup=nobody\nSocketMode=0660\nDirectoryMode=0755\nBacklog='+str(row['backlog'])+'\nRemoveOnStop=yes\nService='+proxy+'\n'
```

### Block 5 â€” insert

Existing anchor AFTER which:
```text

def reconcile(version,restart=False):
```

Existing anchor BEFORE which:
```text
    with lock(version):
        assert_launcher(version);p=policy();source=(paths(version)/'etc/php-fpm.conf').read_text();rows=parse_pools(source,version);old=manifest(version)
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
    ensure_native_cgroup_guard()
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text

def reconcile(version,restart=False):
    ensure_native_cgroup_guard()
    with lock(version):
        assert_launcher(version);p=policy();source=(paths(version)/'etc/php-fpm.conf').read_text();rows=parse_pools(source,version);old=manifest(version)
```

### Block 6 â€” replace

Existing anchor AFTER which:
```text
        finally:start_lock.release()

```

Existing anchor BEFORE which:
```text
    """Fixed relays plus a bounded socket queue, all inside the existing account slice."""
    listener.settimeout(1)
```

Existing content to replace/remove (not copied):
```text
def serve_proxy(listener,unit,backend,idle,limits,stop_backend=True):
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
def serve_proxy(listener,unit,backend,idle,limits,stop_backend=True,host_reserve_mib=0):
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
        finally:start_lock.release()

def serve_proxy(listener,unit,backend,idle,limits,stop_backend=True,host_reserve_mib=0):
    """Fixed relays plus a bounded socket queue, all inside the existing account slice."""
    listener.settimeout(1)
```

### Block 7 â€” replace

Existing anchor AFTER which:
```text
            # the window after a worker dequeues a request but before active++.
            with lock:quiescent=not activity['active'] and pending.unfinished_tasks==0
```

Existing anchor BEFORE which:
```text
                return
            try:client,_=listener.accept()
```

Existing content to replace/remove (not copied):
```text
            if quiescent and waiting_units(unit):
                diagnostic('idle_lease_yield',reasonDetail='waiting_peer_admission')
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
            available=None
            if quiescent and host_reserve_mib:
                try:available=int(next(x.split()[1] for x in pathlib.Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))//1024
                except (OSError,ValueError,StopIteration):pass
            reason=idle_retirement_reason(time.monotonic()-activity['last'],int(idle),quiescent,bool(waiting_units(unit)),available,host_reserve_mib)
            if reason:
                diagnostic('warm_idle_retire' if reason=='warm_idle_expired' else 'idle_lease_yield',reasonDetail=reason)
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
            # the window after a worker dequeues a request but before active++.
            with lock:quiescent=not activity['active'] and pending.unfinished_tasks==0
            available=None
            if quiescent and host_reserve_mib:
                try:available=int(next(x.split()[1] for x in pathlib.Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))//1024
                except (OSError,ValueError,StopIteration):pass
            reason=idle_retirement_reason(time.monotonic()-activity['last'],int(idle),quiescent,bool(waiting_units(unit)),available,host_reserve_mib)
            if reason:
                diagnostic('warm_idle_retire' if reason=='warm_idle_expired' else 'idle_lease_yield',reasonDetail=reason)
                return
            try:client,_=listener.accept()
```

### Block 8 â€” remove

Existing anchor AFTER which:
```text
            try:client,_=listener.accept()
            except socket.timeout:
```

Existing anchor BEFORE which:
```text
                continue
            accepted=time.monotonic();deadline=accepted+limits['timeout']
```

Existing content to replace/remove (not copied):
```text
                with lock:done=not activity['active'] and pending.empty() and time.monotonic()-activity['last']>=int(idle)
                if done:return
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text

```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
            try:client,_=listener.accept()
            except socket.timeout:
                continue
            accepted=time.monotonic();deadline=accepted+limits['timeout']
```

### Block 9 â€” replace

Existing anchor AFTER which:
```text
    limits=proxy_limits(children,backlog,request_timeout)
    listener=socket.fromfd(3,socket.AF_UNIX,socket.SOCK_STREAM)
```

Existing anchor BEFORE which:
```text
    finally:listener.close()

```

Existing content to replace/remove (not copied):
```text
    try:serve_proxy(listener,unit,backend,idle,limits)
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
    try:serve_proxy(listener,unit,backend,idle,limits,host_reserve_mib=policy()['hostReserveMiB'])
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
    limits=proxy_limits(children,backlog,request_timeout)
    listener=socket.fromfd(3,socket.AF_UNIX,socket.SOCK_STREAM)
    try:serve_proxy(listener,unit,backend,idle,limits,host_reserve_mib=policy()['hostReserveMiB'])
    finally:listener.close()

```

### Block 10 â€” insert

Existing anchor AFTER which:
```text
    atomic(STATE/'installed.json',json.dumps({'versions':selected,'installedAt':time.time(),'nativeServiceEnablement':{v:execute(['systemctl','is-enabled','php-fpm'+v[3:]+'.service'],False).stdout.strip() for v in selected}}))
    if pathlib.Path(__file__).resolve()!=SELF:atomic(SELF,pathlib.Path(__file__).read_text(),0o755)
```

Existing anchor BEFORE which:
```text
    for version in selected:
        ctl=paths(version)/'bin/fpmctl';r=execute([str(ctl),'stop'],False,timeout=45)
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
    ensure_native_cgroup_guard()
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
    atomic(STATE/'installed.json',json.dumps({'versions':selected,'installedAt':time.time(),'nativeServiceEnablement':{v:execute(['systemctl','is-enabled','php-fpm'+v[3:]+'.service'],False).stdout.strip() for v in selected}}))
    if pathlib.Path(__file__).resolve()!=SELF:atomic(SELF,pathlib.Path(__file__).read_text(),0o755)
    ensure_native_cgroup_guard()
    for version in selected:
        ctl=paths(version)/'bin/fpmctl';r=execute([str(ctl),'stop'],False,timeout=45)
```

### Block 11 â€” insert

Existing anchor AFTER which:
```text
def verify():
    results={'mode':'experimental-custom-integration','policy':policy(),'versions':{},'mechanicalChecksPass':True}
```

Existing anchor BEFORE which:
```text
    for version in json.loads((STATE/'installed.json').read_text())['versions']:
        try:
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
    drift_cache={}
    if account_slice(1).startswith('golden-') and pathlib.Path('/usr/local/webuzo/bin/cgroup.sh').exists():
        guard_ok=NATIVE_CGROUP_DROPIN.exists() and NATIVE_CGROUP_DROPIN.read_text()==native_guard_dropin() and execute(['systemctl','is-active','cgroup.service'],False).returncode==0
        results['nativeCgroupGuardActive']=guard_ok;results['mechanicalChecksPass']&=guard_ok
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
def verify():
    results={'mode':'experimental-custom-integration','policy':policy(),'versions':{},'mechanicalChecksPass':True}
    drift_cache={}
    if account_slice(1).startswith('golden-') and pathlib.Path('/usr/local/webuzo/bin/cgroup.sh').exists():
        guard_ok=NATIVE_CGROUP_DROPIN.exists() and NATIVE_CGROUP_DROPIN.read_text()==native_guard_dropin() and execute(['systemctl','is-active','cgroup.service'],False).returncode==0
        results['nativeCgroupGuardActive']=guard_ok;results['mechanicalChecksPass']&=guard_ok
    for version in json.loads((STATE/'installed.json').read_text())['versions']:
        try:
```

### Block 12 â€” insert

Existing anchor AFTER which:
```text
                    'runtimeCapSource':'automatic-account-boundary' if results['policy'].get('accountRuntimeCaps') else 'native-global',
                    'reservedMiB':json.loads(lease.read_text())['costMiB'] if lease.exists() else 0})
```

Existing anchor BEFORE which:
```text
                results['mechanicalChecksPass']&=socket_ok and item['swapMax']=='0' and item['cpuMax'].split()[0]!='max' and item['memoryMax']!='max' and pwd.getpwnam(row['user']).pw_uid==row['uid'] and (not item['fpmActive'] or item['fpmControlGroup'].startswith(account_cgroup(row['uid'])+'/'));rows.append(item)
            health=execute(['systemctl','is-active','wpiso-health-'+version+'.service'],False).returncode==0
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                if row['uid'] not in drift_cache:drift_cache[row['uid']]=native_cgroup_drift(row['uid'])
                item['processPlacement']=drift_cache[row['uid']];results['mechanicalChecksPass']&=item['processPlacement']['pass']
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                    'runtimeCapSource':'automatic-account-boundary' if results['policy'].get('accountRuntimeCaps') else 'native-global',
                    'reservedMiB':json.loads(lease.read_text())['costMiB'] if lease.exists() else 0})
                if row['uid'] not in drift_cache:drift_cache[row['uid']]=native_cgroup_drift(row['uid'])
                item['processPlacement']=drift_cache[row['uid']];results['mechanicalChecksPass']&=item['processPlacement']['pass']
                results['mechanicalChecksPass']&=socket_ok and item['swapMax']=='0' and item['cpuMax'].split()[0]!='max' and item['memoryMax']!='max' and pwd.getpwnam(row['user']).pw_uid==row['uid'] and (not item['fpmActive'] or item['fpmControlGroup'].startswith(account_cgroup(row['uid'])+'/'));rows.append(item)
            health=execute(['systemctl','is-active','wpiso-health-'+version+'.service'],False).returncode==0
```

### Block 13 â€” insert

Existing anchor AFTER which:
```text
        if data.get('nativeServiceEnablement',{}).get(version)=='disabled':execute(['systemctl','disable','php-fpm'+version[3:]+'.service'],False)
        execute(['systemctl','reset-failed','wpiso-manager-'+version+'.service','wpiso-health-'+version+'.service'],False)
```

Existing anchor BEFORE which:
```text
    print('Native launchers restored. Native startup placement gap returns. PHP tuning and account swap properties were preserved.')

```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
    remove_native_cgroup_guard()
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
        if data.get('nativeServiceEnablement',{}).get(version)=='disabled':execute(['systemctl','disable','php-fpm'+version[3:]+'.service'],False)
        execute(['systemctl','reset-failed','wpiso-manager-'+version+'.service','wpiso-health-'+version+'.service'],False)
    remove_native_cgroup_guard()
    print('Native launchers restored. Native startup placement gap returns. PHP tuning and account swap properties were preserved.')

```

### Block 14 â€” insert

Existing anchor AFTER which:
```text
    elif ns.command=='release':release(ns.args[0])
    elif ns.command=='proxy':fastcgi_proxy(*ns.args)
```

Existing anchor BEFORE which:
```text
    elif ns.command=='verify':sys.exit(0 if verify() else 1)
    elif ns.command=='reconcile':
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
    elif ns.command=='native-cgroup-install':print(json.dumps(ensure_native_cgroup_guard()))
    elif ns.command=='native-cgroup-remove':remove_native_cgroup_guard()
    elif ns.command=='native-cgroup-guard':native_cgroup_guard()
    elif ns.command=='native-cgroup-repair':print(json.dumps(native_cgroup_pass()))
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
    elif ns.command=='release':release(ns.args[0])
    elif ns.command=='proxy':fastcgi_proxy(*ns.args)
    elif ns.command=='native-cgroup-install':print(json.dumps(ensure_native_cgroup_guard()))
    elif ns.command=='native-cgroup-remove':remove_native_cgroup_guard()
    elif ns.command=='native-cgroup-guard':native_cgroup_guard()
    elif ns.command=='native-cgroup-repair':print(json.dumps(native_cgroup_pass()))
    elif ns.command=='verify':sys.exit(0 if verify() else 1)
    elif ns.command=='reconcile':
```

## uniselv-resman/info.json

Installed paths: /usr/local/webuzo/plugins/uniselv-resman/info.json

Replace the full file; never append duplicate functions/directives. New files run from first through final line.

### Block 1 â€” replace

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
  "version": "1.1.25",
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
  "version": "1.1.26",
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
  "name": "UNISELV Resource Manager",
  "slug": "uniselv-resman",
  "version": "1.1.26",
  "author": "<a href=\"https://refat.ovh\" target=\"_blank\">Refat Rahman</a>",
  "developer": {
```

## uniselv-resman/uniselv-resman.php

Installed paths: /usr/local/webuzo/plugins/uniselv-resman/uniselv-resman.php

Replace the full file; never append duplicate functions/directives. New files run from first through final line.

### Block 1 â€” replace

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
Version: 1.1.25
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
Version: 1.1.26
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
/*
Plugin Name: UNISELV Resource Manager
Version: 1.1.26
Description: Enterprise Resource Management, Cgroups v2 Isolation, Real-Time Monitoring & Telemetry for Webuzo.
Author: Refat Rahman
```

### Block 2 â€” replace

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
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '-1.1.25r2' . '"></script>';

    echo '<div class="uniselv-container">';
    
```

Existing content to replace/remove (not copied):
```text
    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '-1.1.25r2' . '">';
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '-1.1.26r2' . '">';
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
    $i18n_dict = uniselv_get_i18n_dict();

    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '-1.1.26r2' . '">';
    echo '<style>:root { --uniselv-primary: ' . $brand_color . '; --primary-color: ' . $brand_color . '; }</style>';
    echo '<script>
```

### Block 3 â€” replace

Existing anchor AFTER which:
```text
    if (rtrim($brand_docs, '/') === 'https://docs.uniselv.com') $brand_docs = ''; // Historical placeholder; use bundled local Help.

    $panel_url = !empty($globals['panel_url']) ? rtrim($globals['panel_url'], '/') : '';
    $i18n_dict = uniselv_get_i18n_dict();

    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '-1.1.25r2' . '">';
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
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '-1.1.25r2' . '"></script>';
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '-1.1.26r2' . '"></script>';
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
window.UNISELV_TRANSLATIONS = ' . json_encode($i18n_dict[$locale] ?? $i18n_dict['en']) . ';
</script>';
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '-1.1.26r2' . '"></script>';

    echo '<div class="uniselv-container">';
```

### Block 4 â€” insert

Existing anchor AFTER which:
```text
                        <div style="font-weight: 700; font-size: 1.1rem; color: var(--uniselv-success);">' . (isset($health['memory_cap_formatted']) ? htmlspecialchars($health['memory_cap_formatted']) : 'Unavailable') . '</div>
                    </div>
                </div>

```

Existing anchor BEFORE which:
```text
                <div style="display: flex; gap: 14px; align-items: center; flex-wrap: wrap; margin-top: 20px;">
                    <button class="uniselv-btn btn-outline" onclick="UniselvResMan.toggleMaintenanceMode(' . (empty($health['maintenance_mode']) ? 'true' : 'false') . ')">
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                <div style="margin-top:16px;padding:14px;border:1px solid #cbd5e1;border-radius:10px;">
                    <strong>Account cgroup placement: ' . htmlspecialchars($health['cgroup_integrity']['status'] ?? 'UNAVAILABLE') . '</strong>
                    <div>Accounts checked: ' . intval($health['cgroup_integrity']['accounts_checked'] ?? 0) . ' · Native coexistence guard: ' . htmlspecialchars($health['cgroup_integrity']['native_guard'] ?? 'unavailable') . '</div>
                    <small>Page-load audit. Usage combines disjoint native and managed account groups. A DRIFT result requires investigation; it is not a healthy isolation certificate.</small>
                    <div>' . htmlspecialchars(implode(', ', $health['cgroup_integrity']['drift_accounts'] ?? [])) . '</div>
                </div>

```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                </div>

                <div style="margin-top:16px;padding:14px;border:1px solid #cbd5e1;border-radius:10px;">
                    <strong>Account cgroup placement: ' . htmlspecialchars($health['cgroup_integrity']['status'] ?? 'UNAVAILABLE') . '</strong>
                    <div>Accounts checked: ' . intval($health['cgroup_integrity']['accounts_checked'] ?? 0) . ' · Native coexistence guard: ' . htmlspecialchars($health['cgroup_integrity']['native_guard'] ?? 'unavailable') . '</div>
                    <small>Page-load audit. Usage combines disjoint native and managed account groups. A DRIFT result requires investigation; it is not a healthy isolation certificate.</small>
                    <div>' . htmlspecialchars(implode(', ', $health['cgroup_integrity']['drift_accounts'] ?? [])) . '</div>
                </div>

                <div style="display: flex; gap: 14px; align-items: center; flex-wrap: wrap; margin-top: 20px;">
                    <button class="uniselv-btn btn-outline" onclick="UniselvResMan.toggleMaintenanceMode(' . (empty($health['maintenance_mode']) ? 'true' : 'false') . ')">
```

### Block 5 â€” replace

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
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '-1.1.25r2' . '"></script>';

    echo '<div class="uniselv-container">';

    // Header
```

Existing content to replace/remove (not copied):
```text
    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '-1.1.25r2' . '">';
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '-1.1.26r2' . '">';
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
    $i18n_dict = uniselv_get_i18n_dict();

    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '-1.1.26r2' . '">';
    echo '<style>:root { --uniselv-primary: ' . $brand_color . '; --primary-color: ' . $brand_color . '; }</style>';
    echo '<script>
```

### Block 6 â€” replace

Existing anchor AFTER which:
```text
    $limits = isset($dash['limits']) ? $dash['limits'] : [];

    $panel_url = !empty($globals['panel_url']) ? rtrim($globals['panel_url'], '/') : '';
    $i18n_dict = uniselv_get_i18n_dict();

    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '-1.1.25r2' . '">';
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
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '-1.1.25r2' . '"></script>';
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '-1.1.26r2' . '"></script>';
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
window.UNISELV_TRANSLATIONS = ' . json_encode($i18n_dict[$locale] ?? $i18n_dict['en']) . ';
</script>';
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '-1.1.26r2' . '"></script>';

    echo '<div class="uniselv-container">';
```

## uniselv-resman/views/admin_help.php

Installed paths: /usr/local/webuzo/plugins/uniselv-resman/views/admin_help.php

Replace the full file; never append duplicate functions/directives. New files run from first through final line.

### Block 1 â€” replace

Existing anchor AFTER which:
```text
                    <li><strong>Recover or export:</strong> Use <strong>Recover Pending Operation</strong> for an interrupted lifecycle transaction, or <strong>Prepare &amp; Download Comparison</strong> for private diagnostics. Failed recovery retains its journal. Exports contain account paths; share privately.</li>
                </ol>
```

Existing anchor BEFORE which:
```text
            </div>
        </div>
        <div class="uniselv-help-card" data-cat="trouble" id="help-topic-runtime-advanced">
```

Existing content to replace/remove (not copied):
```text
                Native PHP-FPM defaults remain global; automatic account runtime caps borrow available shared capacity rather than reserving workers for idle accounts. Tuning values come from the reviewed generator profile, not this help page.
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                Native PHP-FPM defaults remain global; automatic account runtime caps borrow available shared capacity rather than reserving workers for idle accounts. Tuning values come from the reviewed generator profile, not this help page. Warm masters retain OPcache while headroom permits, with a hardware-derived maximum idle duration; eligible peer demand or low host reserve can reclaim a quiescent lease early. Ondemand workers still retire using inherited global defaults. The native cgroup service uses a plugin-owned coexistence drop-in, preserving the vendor script and managed service descendants.
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                    <li><strong>Recover or export:</strong> Use <strong>Recover Pending Operation</strong> for an interrupted lifecycle transaction, or <strong>Prepare &amp; Download Comparison</strong> for private diagnostics. Failed recovery retains its journal. Exports contain account paths; share privately.</li>
                </ol>
                Native PHP-FPM defaults remain global; automatic account runtime caps borrow available shared capacity rather than reserving workers for idle accounts. Tuning values come from the reviewed generator profile, not this help page. Warm masters retain OPcache while headroom permits, with a hardware-derived maximum idle duration; eligible peer demand or low host reserve can reclaim a quiescent lease early. Ondemand workers still retire using inherited global defaults. The native cgroup service uses a plugin-owned coexistence drop-in, preserving the vendor script and managed service descendants.
            </div>
        </div>
```

### Block 2 â€” replace

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
            <details><summary>Operations, expected profile and verification scope</summary><pre style="white-space:pre-wrap;overflow-wrap:anywhere"><?php echo htmlspecialchars(file_get_contents(__DIR__ . '/../docs/release-1.1.25.md'), ENT_QUOTES, 'UTF-8'); ?></pre></details>
            <details><summary>Exact source replacement and insertion guide</summary><pre style="white-space:pre-wrap;overflow-wrap:anywhere"><?php echo htmlspecialchars(file_get_contents(__DIR__ . '/../docs/source-changes-1.1.25.md'), ENT_QUOTES, 'UTF-8'); ?></pre></details>
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
            <details><summary>Operations, expected profile and verification scope</summary><pre style="white-space:pre-wrap;overflow-wrap:anywhere"><?php echo htmlspecialchars(file_get_contents(__DIR__ . '/../docs/release-1.1.26.md'), ENT_QUOTES, 'UTF-8'); ?></pre></details>
            <details><summary>Exact source replacement and insertion guide</summary><pre style="white-space:pre-wrap;overflow-wrap:anywhere"><?php echo htmlspecialchars(file_get_contents(__DIR__ . '/../docs/source-changes-1.1.26.md'), ENT_QUOTES, 'UTF-8'); ?></pre></details>
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
            <h4 class="uniselv-help-card-title">Runtime Operations, Exact Source Placement &amp; Validation Scope</h4>
            <div class="uniselv-help-card-desc">Release <?php echo $uniselvHelpEscape($uniselvHelpVersion); ?>. These technical guides describe already-applied changes; they are not additional post-install paste steps.</div>
            <details><summary>Operations, expected profile and verification scope</summary><pre style="white-space:pre-wrap;overflow-wrap:anywhere"><?php echo htmlspecialchars(file_get_contents(__DIR__ . '/../docs/release-1.1.26.md'), ENT_QUOTES, 'UTF-8'); ?></pre></details>
            <details><summary>Exact source replacement and insertion guide</summary><pre style="white-space:pre-wrap;overflow-wrap:anywhere"><?php echo htmlspecialchars(file_get_contents(__DIR__ . '/../docs/source-changes-1.1.26.md'), ENT_QUOTES, 'UTF-8'); ?></pre></details>
        </div>

```

### Block 3 â€” insert

Existing anchor AFTER which:
```text
                6. <code>io.max</code> read/write throughput and IOPS rules match the configured plan where limits apply.<br>
                7. <strong>Ancestor Slice:</strong> The slice is strictly located inside <code>/sys/fs/cgroup/golden.slice/</code>.<br>
```

Existing anchor BEFORE which:
```text
                <strong>Menu:</strong> <em>Configured vs Effective Audit</em> tab.<br>
                <strong>Action:</strong> If any slice shows <em>MISCONFIGURED</em>, click <strong>Bulk Sync All Plans</strong> to reconcile immediately.
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                8. <strong>Process Placement:</strong> Observed customer processes remain inside the account boundary; shared Apache workers are audited at the hosting aggregate, not attributed as private account workers.<br>
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                6. <code>io.max</code> read/write throughput and IOPS rules match the configured plan where limits apply.<br>
                7. <strong>Ancestor Slice:</strong> The slice is strictly located inside <code>/sys/fs/cgroup/golden.slice/</code>.<br>
                8. <strong>Process Placement:</strong> Observed customer processes remain inside the account boundary; shared Apache workers are audited at the hosting aggregate, not attributed as private account workers.<br>
                <strong>Menu:</strong> <em>Configured vs Effective Audit</em> tab.<br>
                <strong>Action:</strong> If any slice shows <em>MISCONFIGURED</em>, click <strong>Bulk Sync All Plans</strong> to reconcile immediately.
```
