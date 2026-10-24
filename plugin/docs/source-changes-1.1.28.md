# Exact source changes — 1.1.28

Already-applied release source changes relative to 1.1.27; not extra post-install paste steps. Prefer the reviewed complete package.

- Back up existing files and ownership/restoration manifests together.
- Use UTF-8/LF. Replace existing files; do not append duplicate imports, functions or directives. New files start at their first line and end at their final line.
- Install through the reviewed privileged deployment workflow. Restore root ownership and installer execution modes.
- Run Python/PHP/JavaScript syntax, regression, service/API/HTTP and ZIP closure checks. Configuration values and full workload/lifecycle readiness remain distinct.

## uniselv-resman/agent/ipc_server.py

Installed paths: /usr/local/webuzo/plugins/uniselv-resman/agent/ipc_server.py; ALSO /usr/local/uniselv-resman/agent/ipc_server.py

Replace the full file; never append duplicate functions/directives. New files run from first through final line.

### Block 1 — insert

Existing anchor AFTER which:
```text
                        'native_max_children': pool['maxChildren'],
                        'managed_max_children': int(cap[1]) if cap else None,
```

Existing anchor BEFORE which:
```text
                        'reserved_mib': grant.get('costMiB', 0),
                        'state': 'Leased' if grant else 'Idle / no lease',
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                        'concurrency_grant': grant.get('runtimeMaxChildren'),
                        'enforcement': 'Root-only relay gate' if grant.get('relayEnforced') else 'Legacy FPM cap',
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                        'native_max_children': pool['maxChildren'],
                        'managed_max_children': int(cap[1]) if cap else None,
                        'concurrency_grant': grant.get('runtimeMaxChildren'),
                        'enforcement': 'Root-only relay gate' if grant.get('relayEnforced') else 'Legacy FPM cap',
                        'reserved_mib': grant.get('costMiB', 0),
                        'state': 'Leased' if grant else 'Idle / no lease',
```

## uniselv-resman/core/webuzo-isolation.py

Installed paths: /usr/local/webuzo/plugins/uniselv-resman/core/webuzo-isolation.py; ALSO /usr/local/uniselv-resman/core/webuzo-isolation.py; ALSO /usr/local/sbin/webuzo-isolation.py

Replace the full file; never append duplicate functions/directives. New files run from first through final line.

### Block 1 — insert

Existing anchor AFTER which:
```text
    return min(ceiling,max(1,fair))


```

Existing anchor BEFORE which:
```text
def account_memory_usage(current,stat_text):
    """Admission estimate, not a replacement for kernel memory.current/limits.
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
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
        peers=waiting_units(unit)
        leases={path.name:json.loads(path.read_text()) for path in (RUN/'slots').glob('*.service')}
        target=min(ceiling,contention_ceiling(ceiling,limits['memoryMiB'],p,len(set(leases)|peers))) if peers else ceiling
        waiting=RUN/'waiting';waiting.mkdir(mode=0o700,exist_ok=True);ticket=waiting/unit
        def request(cap):
            atomic(ticket,json.dumps({'mode':'elastic','uid':uid,'ceiling':cap,
                'expires':time.monotonic()+limits['timeout']+5}))
        if current>target:
            request(target)
            return {'ceiling':target,'previous':current,'reasonDetail':'peer_fair_share' if peers else 'account_boundary'}
        if demand<=current or current>=target:
            clear_elastic_demand(unit);return None
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
        granted,_=demand_grant(target,limits['memoryMiB'],p,reserved,
            available+min(old_cost,charged),account_available)
        if granted>current:
            if own.get('relayEnforced') and elastic_proxy_ready(unit):
                own.update(runtimeMaxChildren=granted,costMiB=granted*p['workerRssMiB']+48+p['opcacheMiB']+limits['memoryMiB'],lastResizeAt=time.time())
                atomic(lease,json.dumps(own));clear_elastic_demand(unit)
                return {'ceiling':granted,'previous':current,'reasonDetail':'queued_demand_growth','liveGrowth':True}
            request(granted)
            return {'ceiling':granted,'previous':current,'reasonDetail':'queued_demand_growth'}
        next_cost=(current+1)*p['workerRssMiB']+48+p['opcacheMiB']+limits['memoryMiB']
        if account_available>=next_cost and available-p['hostReserveMiB']>=p['workerRssMiB']:
            request(target)  # Partial grants must advertise unsatisfied demand too.
        else:clear_elastic_demand(unit)
        return None


```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text


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
        peers=waiting_units(unit)
        leases={path.name:json.loads(path.read_text()) for path in (RUN/'slots').glob('*.service')}
        target=min(ceiling,contention_ceiling(ceiling,limits['memoryMiB'],p,len(set(leases)|peers))) if peers else ceiling
        waiting=RUN/'waiting';waiting.mkdir(mode=0o700,exist_ok=True);ticket=waiting/unit
        def request(cap):
            atomic(ticket,json.dumps({'mode':'elastic','uid':uid,'ceiling':cap,
                'expires':time.monotonic()+limits['timeout']+5}))
        if current>target:
            request(target)
            return {'ceiling':target,'previous':current,'reasonDetail':'peer_fair_share' if peers else 'account_boundary'}
        if demand<=current or current>=target:
            clear_elastic_demand(unit);return None
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
        granted,_=demand_grant(target,limits['memoryMiB'],p,reserved,
            available+min(old_cost,charged),account_available)
        if granted>current:
            if own.get('relayEnforced') and elastic_proxy_ready(unit):
                own.update(runtimeMaxChildren=granted,costMiB=granted*p['workerRssMiB']+48+p['opcacheMiB']+limits['memoryMiB'],lastResizeAt=time.time())
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
```

### Block 2 — insert

Existing anchor AFTER which:
```text
    grant_ceiling=children
    try:
```

Existing anchor BEFORE which:
```text
        while True:
            with lock('admission'):
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
        prior=json.loads(ticket.read_text()) if ticket.exists() else {}
        if (prior.get('mode')=='elastic' and prior.get('uid')==actual_uid
                and type(prior.get('expires')) in (int,float) and time.monotonic()<prior['expires']<float('inf')
                and type(prior.get('ceiling')) is int and 1<=prior['ceiling']<=children):
            grant_ceiling=prior['ceiling']

```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
    grant_ceiling=children
    try:
        prior=json.loads(ticket.read_text()) if ticket.exists() else {}
        if (prior.get('mode')=='elastic' and prior.get('uid')==actual_uid
                and type(prior.get('expires')) in (int,float) and time.monotonic()<prior['expires']<float('inf')
                and type(prior.get('ceiling')) is int and 1<=prior['ceiling']<=children):
            grant_ceiling=prior['ceiling']

        while True:
            with lock('admission'):
```

### Block 3 — insert

Existing anchor AFTER which:
```text
                        'accountWorkingSetMiB':round(working/1048576,2),
                        'accountMemoryAccounting':'clean-inactive-file-v1'}
```

Existing anchor BEFORE which:
```text
                granted,cost=demand_grant(min(ceiling,grant_ceiling),relay['memoryMiB'],p,reserved,available,account_available)
                eligible=granted>=1 if dynamic else (granted==children and len(list(slots.iterdir()))<p['maxActivePools'])
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                peer_demand=waiting_units(unit)
                if peer_demand:
                    grant_ceiling=min(grant_ceiling,contention_ceiling(ceiling,relay['memoryMiB'],p,len({x.name for x in lease_paths}|peer_demand|{unit})))
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                        'accountWorkingSetMiB':round(working/1048576,2),
                        'accountMemoryAccounting':'clean-inactive-file-v1'}
                peer_demand=waiting_units(unit)
                if peer_demand:
                    grant_ceiling=min(grant_ceiling,contention_ceiling(ceiling,relay['memoryMiB'],p,len({x.name for x in lease_paths}|peer_demand|{unit})))
                granted,cost=demand_grant(min(ceiling,grant_ceiling),relay['memoryMiB'],p,reserved,available,account_available)
                eligible=granted>=1 if dynamic else (granted==children and len(list(slots.iterdir()))<p['maxActivePools'])
```

### Block 4 — replace

Existing anchor AFTER which:
```text
                eligible=granted>=1 if dynamic else (granted==children and len(list(slots.iterdir()))<p['maxActivePools'])
                if eligible:
```

Existing anchor BEFORE which:
```text
                    atomic(lease,json.dumps({'costMiB':cost,'startedAt':time.time(),
                        'nativeMaxChildren':children,'accountCeiling':ceiling,'runtimeMaxChildren':granted,
```

Existing content to replace/remove (not copied):
```text
                    if dynamic:atomic(pool_path,runtime_pool(pool,granted))
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                    relay_enforced=dynamic and elastic_proxy_ready(unit)
                    if dynamic:atomic(pool_path,private_backend(runtime_pool(pool,ceiling if relay_enforced else granted)))
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                eligible=granted>=1 if dynamic else (granted==children and len(list(slots.iterdir()))<p['maxActivePools'])
                if eligible:
                    relay_enforced=dynamic and elastic_proxy_ready(unit)
                    if dynamic:atomic(pool_path,private_backend(runtime_pool(pool,ceiling if relay_enforced else granted)))
                    atomic(lease,json.dumps({'costMiB':cost,'startedAt':time.time(),
                        'nativeMaxChildren':children,'accountCeiling':ceiling,'runtimeMaxChildren':granted,
```

### Block 5 — replace

Existing anchor AFTER which:
```text
                    atomic(lease,json.dumps({'costMiB':cost,'startedAt':time.time(),
                        'nativeMaxChildren':children,'accountCeiling':ceiling,'runtimeMaxChildren':granted,
```

Existing anchor BEFORE which:
```text
                # Do not recycle other accounts for this account's own RAM shortage.
                minimum=p['workerRssMiB']+48+p['opcacheMiB']+relay['memoryMiB']
```

Existing content to replace/remove (not copied):
```text
                        'contentionCeiling':min(ceiling,grant_ceiling),'uid':actual_uid,'mode':'account-aware' if dynamic else 'global-default',**accounting}));return
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                        'contentionCeiling':min(ceiling,grant_ceiling),'relayEnforced':relay_enforced,'fpmMaxChildren':ceiling if relay_enforced else granted,'uid':actual_uid,'mode':'account-aware' if dynamic else 'global-default',**accounting}));return
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                    atomic(lease,json.dumps({'costMiB':cost,'startedAt':time.time(),
                        'nativeMaxChildren':children,'accountCeiling':ceiling,'runtimeMaxChildren':granted,
                        'contentionCeiling':min(ceiling,grant_ceiling),'relayEnforced':relay_enforced,'fpmMaxChildren':ceiling if relay_enforced else granted,'uid':actual_uid,'mode':'account-aware' if dynamic else 'global-default',**accounting}));return
                # Do not recycle other accounts for this account's own RAM shortage.
                minimum=p['workerRssMiB']+48+p['opcacheMiB']+relay['memoryMiB']
```

### Block 6 — replace

Existing anchor AFTER which:
```text
    listener.settimeout(1)
    pending=queue.Queue(maxsize=limits['queue']);lock=threading.Lock();start_lock=threading.Lock()
```

Existing anchor BEFORE which:
```text
    old_signals={}
    if threading.current_thread() is threading.main_thread():
```

Existing content to replace/remove (not copied):
```text
    stopping=threading.Event();activity={'last':time.monotonic(),'active':0}
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
    stopping=threading.Event();activity={'last':time.monotonic(),'active':0,'forwarded':0}
    dispatch=threading.Condition(lock);draining=False;regrant=None;rebalance_after=0;drain_deadline=0;dispatch_limit=1 if stop_backend else limits['workers']
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
    listener.settimeout(1)
    pending=queue.Queue(maxsize=limits['queue']);lock=threading.Lock();start_lock=threading.Lock()
    stopping=threading.Event();activity={'last':time.monotonic(),'active':0,'forwarded':0}
    dispatch=threading.Condition(lock);draining=False;regrant=None;rebalance_after=0;drain_deadline=0;dispatch_limit=1 if stop_backend else limits['workers']
    old_signals={}
    if threading.current_thread() is threading.main_thread():
```

### Block 7 — replace

Existing anchor AFTER which:
```text
                            target=upstream if source is client else client
                            target.settimeout(min(5,remaining));target.sendall(data)
```

Existing anchor BEFORE which:
```text
                            else:
                                response_buffer.extend(data)
```

Existing content to replace/remove (not copied):
```text
                            if source is client:forwarded=True
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                            if source is client:
                                if not forwarded:
                                    with lock:activity['forwarded']+=1
                                forwarded=True
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                            target=upstream if source is client else client
                            target.settimeout(min(5,remaining));target.sendall(data)
                            if source is client:
                                if not forwarded:
                                    with lock:activity['forwarded']+=1
                                forwarded=True
                            else:
                                response_buffer.extend(data)
```

### Block 8 — replace

Existing anchor AFTER which:
```text
            diagnostic('relay_io_error',error=type(error).__name__,forwarded=forwarded)
        finally:
```

Existing anchor BEFORE which:
```text
    def worker():
        while not stopping.is_set():
```

Existing content to replace/remove (not copied):
```text
            with lock:activity['active']-=1;activity['last']=time.monotonic()
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
            with dispatch:
                activity['active']-=1;activity['forwarded']-=int(forwarded)
                activity['last']=time.monotonic();dispatch.notify_all()
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
            diagnostic('relay_io_error',error=type(error).__name__,forwarded=forwarded)
        finally:
            with dispatch:
                activity['active']-=1;activity['forwarded']-=int(forwarded)
                activity['last']=time.monotonic();dispatch.notify_all()
    def worker():
        while not stopping.is_set():
```

### Block 9 — replace

Existing anchor AFTER which:
```text
    def worker():
        while not stopping.is_set():
```

Existing anchor BEFORE which:
```text
            try:handle(*item)
            finally:pending.task_done()
```

Existing content to replace/remove (not copied):
```text
            try:item=pending.get(timeout=.25)
            except queue.Empty:continue
            with lock:activity['active']+=1
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
            with dispatch:
                while not stopping.is_set() and (draining or pending.empty() or activity['active']>=dispatch_limit):dispatch.wait(.25)
                if stopping.is_set():return
                try:item=pending.get_nowait()
                except queue.Empty:continue
                activity['active']+=1
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
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
```

### Block 10 — replace

Existing anchor AFTER which:
```text
                try:available=int(next(x.split()[1] for x in pathlib.Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))//1024
                except (OSError,ValueError,StopIteration):pass
```

Existing anchor BEFORE which:
```text
            if reason:
                diagnostic('warm_idle_retire' if reason=='warm_idle_expired' else 'idle_lease_yield',reasonDetail=reason)
```

Existing content to replace/remove (not copied):
```text
            reason=idle_retirement_reason(time.monotonic()-activity['last'],int(idle),quiescent,bool(waiting_units(unit)),available,host_reserve_mib)
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
            if stop_backend and time.monotonic()>=rebalance_after and not draining:
                rebalance_after=time.monotonic()+1
                try:
                    limit=runtime_dispatch_limit(unit,limits['workers'])
                    with dispatch:dispatch_limit=limit;dispatch.notify_all()
                    with lock:demand=activity['forwarded']+pending.qsize()
                    plan=elastic_regrant_plan(unit,limits,demand)
                    if plan:
                        if plan.get('liveGrowth'):
                            with dispatch:dispatch_limit=runtime_dispatch_limit(unit,limits['workers']);dispatch.notify_all()
                            diagnostic('runtime_grant_grown',**plan)
                        else:
                            with dispatch:draining=True;regrant=plan;drain_deadline=time.monotonic()+limits['timeout']
                            diagnostic('runtime_regrant_drain',**plan)
                except Exception as error:
                    diagnostic('runtime_regrant_error',error=type(error).__name__)
                    rebalance_after=time.monotonic()+max(2,min(15,limits['timeout']/4))
            if draining:
                with lock:drained=activity['active']==0
                if drained and not backend_drained(unit,backend):drained=False
                if not drained and time.monotonic()>=drain_deadline:
                    clear_elastic_demand(unit)
                    with dispatch:draining=False;regrant=None;dispatch.notify_all()
                    rebalance_after=time.monotonic()+max(2,min(15,limits['timeout']/4))
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
            reason=None if draining else idle_retirement_reason(time.monotonic()-activity['last'],int(idle),quiescent,has_lease and bool(waiting_units(unit)),available,host_reserve_mib)
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                try:available=int(next(x.split()[1] for x in pathlib.Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))//1024
                except (OSError,ValueError,StopIteration):pass
            if stop_backend and time.monotonic()>=rebalance_after and not draining:
                rebalance_after=time.monotonic()+1
                try:
                    limit=runtime_dispatch_limit(unit,limits['workers'])
                    with dispatch:dispatch_limit=limit;dispatch.notify_all()
                    with lock:demand=activity['forwarded']+pending.qsize()
                    plan=elastic_regrant_plan(unit,limits,demand)
                    if plan:
                        if plan.get('liveGrowth'):
                            with dispatch:dispatch_limit=runtime_dispatch_limit(unit,limits['workers']);dispatch.notify_all()
                            diagnostic('runtime_grant_grown',**plan)
                        else:
                            with dispatch:draining=True;regrant=plan;drain_deadline=time.monotonic()+limits['timeout']
                            diagnostic('runtime_regrant_drain',**plan)
                except Exception as error:
                    diagnostic('runtime_regrant_error',error=type(error).__name__)
                    rebalance_after=time.monotonic()+max(2,min(15,limits['timeout']/4))
            if draining:
                with lock:drained=activity['active']==0
                if drained and not backend_drained(unit,backend):drained=False
                if not drained and time.monotonic()>=drain_deadline:
                    clear_elastic_demand(unit)
                    with dispatch:draining=False;regrant=None;dispatch.notify_all()
                    rebalance_after=time.monotonic()+max(2,min(15,limits['timeout']/4))
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
            reason=None if draining else idle_retirement_reason(time.monotonic()-activity['last'],int(idle),quiescent,has_lease and bool(waiting_units(unit)),available,host_reserve_mib)
            if reason:
                diagnostic('warm_idle_retire' if reason=='warm_idle_expired' else 'idle_lease_yield',reasonDetail=reason)
```

### Block 11 — insert

Existing anchor AFTER which:
```text
                diagnostic('warm_idle_retire' if reason=='warm_idle_expired' else 'idle_lease_yield',reasonDetail=reason)
                return
```

Existing anchor BEFORE which:
```text
            try:client,_=listener.accept()
            except socket.timeout:
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
            if pending.full():
                stopping.wait(.05);continue
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                diagnostic('warm_idle_retire' if reason=='warm_idle_expired' else 'idle_lease_yield',reasonDetail=reason)
                return
            if pending.full():
                stopping.wait(.05);continue
            try:client,_=listener.accept()
            except socket.timeout:
```

### Block 12 — replace

Existing anchor AFTER which:
```text
            with lock:activity['last']=accepted
            # Apply backpressure; waiting requests never allocate a thread each.
```

Existing anchor BEFORE which:
```text
            except queue.Full:
                diagnostic('queue_full_deadline',queued=pending.qsize())
```

Existing content to replace/remove (not copied):
```text
            try:pending.put((client,deadline,accepted),timeout=limits['timeout'])
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
            try:
                pending.put_nowait((client,deadline,accepted))
                with dispatch:dispatch.notify_all()
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
            with lock:activity['last']=accepted
            # Apply backpressure; waiting requests never allocate a thread each.
            try:
                pending.put_nowait((client,deadline,accepted))
                with dispatch:dispatch.notify_all()
            except queue.Full:
                diagnostic('queue_full_deadline',queued=pending.qsize())
```

### Block 13 — insert

Existing anchor AFTER which:
```text
    finally:
        stopping.set()
```

Existing anchor BEFORE which:
```text
        while True:
            try:client,_,_=pending.get_nowait()
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
        with dispatch:dispatch.notify_all()
        if stop_backend:
            try:clear_elastic_demand(unit)
            except (OSError,ValueError,TypeError):pass
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
    finally:
        stopping.set()
        with dispatch:dispatch.notify_all()
        if stop_backend:
            try:clear_elastic_demand(unit)
            except (OSError,ValueError,TypeError):pass
        while True:
            try:client,_,_=pending.get_nowait()
```

### Block 14 — insert

Existing anchor AFTER which:
```text
        request_timeout=request_seconds(pool,policy().get('requestTimeoutSeconds',120))
    limits=proxy_limits(children,backlog,request_timeout)
```

Existing anchor BEFORE which:
```text
    listener=socket.fromfd(3,socket.AF_UNIX,socket.SOCK_STREAM)
    try:serve_proxy(listener,unit,backend,idle,limits,host_reserve_mib=policy()['hostReserveMiB'])
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
    directory=RUN/'elastic-proxies';directory.mkdir(mode=0o700,exist_ok=True);marker=directory/unit
    pid=os.getpid();start=pathlib.Path('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19]
    atomic(marker,json.dumps({'protocol':1,'pid':pid,'startTicks':start}))
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
        request_timeout=request_seconds(pool,policy().get('requestTimeoutSeconds',120))
    limits=proxy_limits(children,backlog,request_timeout)
    directory=RUN/'elastic-proxies';directory.mkdir(mode=0o700,exist_ok=True);marker=directory/unit
    pid=os.getpid();start=pathlib.Path('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19]
    atomic(marker,json.dumps({'protocol':1,'pid':pid,'startTicks':start}))
    listener=socket.fromfd(3,socket.AF_UNIX,socket.SOCK_STREAM)
    try:serve_proxy(listener,unit,backend,idle,limits,host_reserve_mib=policy()['hostReserveMiB'])
```

### Block 15 — replace

Existing anchor AFTER which:
```text
    listener=socket.fromfd(3,socket.AF_UNIX,socket.SOCK_STREAM)
    try:serve_proxy(listener,unit,backend,idle,limits,host_reserve_mib=policy()['hostReserveMiB'])
```

Existing anchor BEFORE which:
```text


def release(unit):
```

Existing content to replace/remove (not copied):
```text
    finally:listener.close()
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
    finally:
        listener.close()
        try:
            if json.loads(marker.read_text()).get('pid')==pid:marker.unlink(missing_ok=True)
        except (OSError,ValueError,TypeError):pass

```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
    listener=socket.fromfd(3,socket.AF_UNIX,socket.SOCK_STREAM)
    try:serve_proxy(listener,unit,backend,idle,limits,host_reserve_mib=policy()['hostReserveMiB'])
    finally:
        listener.close()
        try:
            if json.loads(marker.read_text()).get('pid')==pid:marker.unlink(missing_ok=True)
        except (OSError,ValueError,TypeError):pass



```

### Block 16 — insert

Existing anchor AFTER which:
```text
                ceiling=runtime_ceiling(row['uid'],native,results['policy'],int(backlog[1]) if backlog else 511,request_seconds(private))
                lease=RUN/'slots'/fpm
```

Existing anchor BEFORE which:
```text
                item.update({'nativeMaxChildren':native,'accountWorkerCeiling':ceiling,
                    'managedMaxChildren':int(effective[1]) if effective else None,
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                grant=json.loads(lease.read_text()) if lease.exists() else {}
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                ceiling=runtime_ceiling(row['uid'],native,results['policy'],int(backlog[1]) if backlog else 511,request_seconds(private))
                lease=RUN/'slots'/fpm
                grant=json.loads(lease.read_text()) if lease.exists() else {}
                item.update({'nativeMaxChildren':native,'accountWorkerCeiling':ceiling,
                    'managedMaxChildren':int(effective[1]) if effective else None,
```

### Block 17 — replace

Existing anchor AFTER which:
```text
                    'managedMaxChildren':int(effective[1]) if effective else None,
                    'runtimeCapSource':'automatic-account-boundary' if results['policy'].get('accountRuntimeCaps') else 'native-global',
```

Existing anchor BEFORE which:
```text
                if row['uid'] not in drift_cache:drift_cache[row['uid']]=native_cgroup_drift(row['uid'])
                item['processPlacement']=drift_cache[row['uid']];results['mechanicalChecksPass']&=item['processPlacement']['pass']
```

Existing content to replace/remove (not copied):
```text
                    'reservedMiB':json.loads(lease.read_text())['costMiB'] if lease.exists() else 0})
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                    'reservedMiB':grant.get('costMiB',0),'runtimeConcurrencyGrant':grant.get('runtimeMaxChildren'),'relayEnforced':bool(grant.get('relayEnforced'))})
                if grant.get('relayEnforced'):
                    backend=RUN/(version+'-'+row['user']+'.sock')
                    backend_private=backend.exists() and backend.stat().st_uid==0 and backend.stat().st_mode&0o777==0o600
                    item['backendRootOnly']=backend_private
                    results['mechanicalChecksPass']&=backend_private and elastic_proxy_ready(fpm) and type(grant.get('runtimeMaxChildren')) is int and 1<=grant['runtimeMaxChildren']<=ceiling and int(effective[1])==ceiling
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
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
  "version": "1.1.27",
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
  "version": "1.1.28",
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
  "name": "UNISELV Resource Manager",
  "slug": "uniselv-resman",
  "version": "1.1.28",
  "author": "<a href=\"https://refat.ovh\" target=\"_blank\">Refat Rahman</a>",
  "developer": {
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
Version: 1.1.27
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
Version: 1.1.28
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
/*
Plugin Name: UNISELV Resource Manager
Version: 1.1.28
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
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '-1.1.27r3' . '"></script>';

    echo '<div class="uniselv-container">';
    
```

Existing content to replace/remove (not copied):
```text
    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '-1.1.27r3' . '">';
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '-1.1.28r1' . '">';
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
    $i18n_dict = uniselv_get_i18n_dict();

    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '-1.1.28r1' . '">';
    echo '<style>:root { --uniselv-primary: ' . $brand_color . '; --primary-color: ' . $brand_color . '; }</style>';
    echo '<script>
```

### Block 3 — replace

Existing anchor AFTER which:
```text
    if (rtrim($brand_docs, '/') === 'https://docs.uniselv.com') $brand_docs = ''; // Historical placeholder; use bundled local Help.

    $panel_url = !empty($globals['panel_url']) ? rtrim($globals['panel_url'], '/') : '';
    $i18n_dict = uniselv_get_i18n_dict();

    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '-1.1.27r3' . '">';
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
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '-1.1.27r3' . '"></script>';
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '-1.1.28r1' . '"></script>';
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
window.UNISELV_TRANSLATIONS = ' . json_encode($i18n_dict[$locale] ?? $i18n_dict['en']) . ';
</script>';
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '-1.1.28r1' . '"></script>';

    echo '<div class="uniselv-container">';
```

### Block 4 — replace

Existing anchor AFTER which:
```text
            </div>
        </div>';
```

Existing anchor BEFORE which:
```text
    foreach (($audit['php_runtime'] ?? []) as $runtime) {
        echo '<tr>';
```

Existing content to replace/remove (not copied):
```text
    echo '<div class="uniselv-card mb-3"><h3>Automatic PHP Runtime Capacity</h3><p>Native global defaults remain inherited. Private runtime caps follow account RAM/Tasks boundaries and available shared PHP capacity. Idle accounts reserve zero; busy pools retain their grant until idle. This is a planning estimate, not a visitor guarantee.</p><div style="overflow-x:auto"><table class="uniselv-table"><thead><tr><th>Account</th><th>PHP</th><th>Native ceiling</th><th>Managed cap</th><th>Reserved MiB</th><th>Lease state</th><th>Source</th></tr></thead><tbody>';
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
    echo '<div class="uniselv-card mb-3"><h3>Automatic PHP Runtime Capacity</h3><p>Native global defaults remain inherited. Private runtime caps follow account RAM/Tasks boundaries and available shared PHP capacity. Unleased accounts reserve zero; warm pools retain a reclaimable reservation. Concurrent grants grow with queued demand; reductions drain forwarded work before restarting the backend. This is a planning estimate, not a visitor guarantee.</p><div style="overflow-x:auto"><table class="uniselv-table"><thead><tr><th>Account</th><th>PHP</th><th>Native ceiling</th><th>Private FPM ceiling</th><th>Concurrent grant</th><th>Enforcement</th><th>Reserved MiB</th><th>Lease state</th><th>Source</th></tr></thead><tbody>';
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
            </div>
        </div>';
    echo '<div class="uniselv-card mb-3"><h3>Automatic PHP Runtime Capacity</h3><p>Native global defaults remain inherited. Private runtime caps follow account RAM/Tasks boundaries and available shared PHP capacity. Unleased accounts reserve zero; warm pools retain a reclaimable reservation. Concurrent grants grow with queued demand; reductions drain forwarded work before restarting the backend. This is a planning estimate, not a visitor guarantee.</p><div style="overflow-x:auto"><table class="uniselv-table"><thead><tr><th>Account</th><th>PHP</th><th>Native ceiling</th><th>Private FPM ceiling</th><th>Concurrent grant</th><th>Enforcement</th><th>Reserved MiB</th><th>Lease state</th><th>Source</th></tr></thead><tbody>';
    foreach (($audit['php_runtime'] ?? []) as $runtime) {
        echo '<tr>';
```

### Block 5 — replace

Existing anchor AFTER which:
```text
    foreach (($audit['php_runtime'] ?? []) as $runtime) {
        echo '<tr>';
```

Existing anchor BEFORE which:
```text
            echo '<td>' . htmlspecialchars((string)($runtime[$field] ?? 'Unknown'), ENT_QUOTES, 'UTF-8') . '</td>';
        }
```

Existing content to replace/remove (not copied):
```text
        foreach (['user','version','native_max_children','managed_max_children','reserved_mib','state','source'] as $field) {
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
        foreach (['user','version','native_max_children','managed_max_children','concurrency_grant','enforcement','reserved_mib','state','source'] as $field) {
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
    foreach (($audit['php_runtime'] ?? []) as $runtime) {
        echo '<tr>';
        foreach (['user','version','native_max_children','managed_max_children','concurrency_grant','enforcement','reserved_mib','state','source'] as $field) {
            echo '<td>' . htmlspecialchars((string)($runtime[$field] ?? 'Unknown'), ENT_QUOTES, 'UTF-8') . '</td>';
        }
```

### Block 6 — replace

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
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '-1.1.27r3' . '"></script>';

    echo '<div class="uniselv-container">';

    // Header
```

Existing content to replace/remove (not copied):
```text
    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '-1.1.27r3' . '">';
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '-1.1.28r1' . '">';
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
    $i18n_dict = uniselv_get_i18n_dict();

    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '-1.1.28r1' . '">';
    echo '<style>:root { --uniselv-primary: ' . $brand_color . '; --primary-color: ' . $brand_color . '; }</style>';
    echo '<script>
```

### Block 7 — replace

Existing anchor AFTER which:
```text
    $limits = isset($dash['limits']) ? $dash['limits'] : [];

    $panel_url = !empty($globals['panel_url']) ? rtrim($globals['panel_url'], '/') : '';
    $i18n_dict = uniselv_get_i18n_dict();

    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '-1.1.27r3' . '">';
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
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '-1.1.27r3' . '"></script>';
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '-1.1.28r1' . '"></script>';
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
window.UNISELV_TRANSLATIONS = ' . json_encode($i18n_dict[$locale] ?? $i18n_dict['en']) . ';
</script>';
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '-1.1.28r1' . '"></script>';

    echo '<div class="uniselv-container">';
```

## uniselv-resman/views/admin_help.php

Installed paths: /usr/local/webuzo/plugins/uniselv-resman/views/admin_help.php

Replace the full file; never append duplicate functions/directives. New files run from first through final line.

### Block 1 — replace

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
                Native PHP-FPM defaults remain global; automatic account runtime caps borrow available shared capacity rather than reserving workers for idle accounts. Tuning values come from the reviewed generator profile, not this help page. Warm masters retain OPcache while headroom permits, with a hardware-derived maximum idle duration; eligible peer demand or low host reserve can reclaim a quiescent lease early. Ondemand workers still retire using inherited global defaults. The native cgroup service uses a plugin-owned coexistence drop-in, preserving the vendor script and managed service descendants.
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                Native PHP-FPM defaults remain global; automatic account runtime caps borrow available shared capacity rather than reserving workers for idle accounts. Tuning values come from the reviewed generator profile, not this help page. Configured vs Effective Audit separates the private FPM ceiling from the current concurrent relay grant. A partial grant advertises queued demand and can grow in place without a PHP/OPcache restart. Fair-share reductions hold new work in the bounded queue and wait for forwarded work and verified backend idleness before re-admission. Root-only backend sockets and a PID/start-token proxy handshake prevent bypass and preserve compatibility with older running proxies. Warm masters retain OPcache while headroom permits, with a hardware-derived maximum idle duration; eligible peer demand or low host reserve can reclaim a quiescent lease early. Ondemand workers still retire using inherited global defaults. The native cgroup service uses a plugin-owned coexistence drop-in, preserving the vendor script and managed service descendants.
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                    <li><strong>Recover or export:</strong> Use <strong>Recover Pending Operation</strong> for an interrupted lifecycle transaction, or <strong>Prepare &amp; Download Comparison</strong> for private diagnostics. Failed recovery retains its journal. Exports contain account paths; share privately.</li>
                </ol>
                Native PHP-FPM defaults remain global; automatic account runtime caps borrow available shared capacity rather than reserving workers for idle accounts. Tuning values come from the reviewed generator profile, not this help page. Configured vs Effective Audit separates the private FPM ceiling from the current concurrent relay grant. A partial grant advertises queued demand and can grow in place without a PHP/OPcache restart. Fair-share reductions hold new work in the bounded queue and wait for forwarded work and verified backend idleness before re-admission. Root-only backend sockets and a PID/start-token proxy handshake prevent bypass and preserve compatibility with older running proxies. Warm masters retain OPcache while headroom permits, with a hardware-derived maximum idle duration; eligible peer demand or low host reserve can reclaim a quiescent lease early. Ondemand workers still retire using inherited global defaults. The native cgroup service uses a plugin-owned coexistence drop-in, preserving the vendor script and managed service descendants.
            </div>
        </div>
```

### Block 2 — replace

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
            <details><summary>Operations, expected profile and verification scope</summary><pre style="white-space:pre-wrap;overflow-wrap:anywhere"><?php echo htmlspecialchars(file_get_contents(__DIR__ . '/../docs/release-1.1.27.md'), ENT_QUOTES, 'UTF-8'); ?></pre></details>
            <details><summary>Exact source replacement and insertion guide</summary><pre style="white-space:pre-wrap;overflow-wrap:anywhere"><?php echo htmlspecialchars(file_get_contents(__DIR__ . '/../docs/source-changes-1.1.27.md'), ENT_QUOTES, 'UTF-8'); ?></pre></details>
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
            <details><summary>Operations, expected profile and verification scope</summary><pre style="white-space:pre-wrap;overflow-wrap:anywhere"><?php echo htmlspecialchars(file_get_contents(__DIR__ . '/../docs/release-1.1.28.md'), ENT_QUOTES, 'UTF-8'); ?></pre></details>
            <details><summary>Exact source replacement and insertion guide</summary><pre style="white-space:pre-wrap;overflow-wrap:anywhere"><?php echo htmlspecialchars(file_get_contents(__DIR__ . '/../docs/source-changes-1.1.28.md'), ENT_QUOTES, 'UTF-8'); ?></pre></details>
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
            <h4 class="uniselv-help-card-title">Runtime Operations, Exact Source Placement &amp; Validation Scope</h4>
            <div class="uniselv-help-card-desc">Release <?php echo $uniselvHelpEscape($uniselvHelpVersion); ?>. These technical guides describe already-applied changes; they are not additional post-install paste steps.</div>
            <details><summary>Operations, expected profile and verification scope</summary><pre style="white-space:pre-wrap;overflow-wrap:anywhere"><?php echo htmlspecialchars(file_get_contents(__DIR__ . '/../docs/release-1.1.28.md'), ENT_QUOTES, 'UTF-8'); ?></pre></details>
            <details><summary>Exact source replacement and insertion guide</summary><pre style="white-space:pre-wrap;overflow-wrap:anywhere"><?php echo htmlspecialchars(file_get_contents(__DIR__ . '/../docs/source-changes-1.1.28.md'), ENT_QUOTES, 'UTF-8'); ?></pre></details>
        </div>

```
