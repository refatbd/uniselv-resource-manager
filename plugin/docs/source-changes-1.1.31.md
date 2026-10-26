# Exact source changes — 1.1.31

Already-applied release source changes relative to 1.1.30; not extra post-install paste steps. Prefer the reviewed complete package.

- Back up existing files and ownership/restoration manifests together.
- Use UTF-8/LF. Replace existing files; do not append duplicate imports, functions or directives. New files start at their first line and end at their final line.
- Install through the reviewed privileged deployment workflow. Restore root ownership and installer execution modes.
- Run Python/PHP/JavaScript syntax, regression, service/API/HTTP and ZIP closure checks. Configuration values and full workload/lifecycle readiness remain distinct.

## uniselv-resman/core/webuzo-isolation.py

Installed paths: /usr/local/webuzo/plugins/uniselv-resman/core/webuzo-isolation.py; ALSO /usr/local/uniselv-resman/core/webuzo-isolation.py; ALSO /usr/local/sbin/webuzo-isolation.py

Replace the full file; never append duplicate functions/directives. New files run from first through final line.

### Block 1 — replace

Existing anchor AFTER which:
```text
PROXY='/usr/lib/systemd/systemd-socket-proxyd'
MARKER='# WEBUZO-ISOLATION MANAGED LAUNCHER'
```

Existing anchor BEFORE which:
```text
NATIVE_CGROUP_USERS=pathlib.Path('/var/webuzo/conf/cgroupusers')
NATIVE_CGROUP_DROPIN=UNITS/'cgroup.service.d/90-uniselv-resman.conf'
```

Existing content to replace/remove (not copied):
```text
CAPACITY_MODEL_VERSION='account-demand-v5-warm'
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
CAPACITY_MODEL_VERSION='account-demand-v6-idle-compaction'
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
PROXY='/usr/lib/systemd/systemd-socket-proxyd'
MARKER='# WEBUZO-ISOLATION MANAGED LAUNCHER'
CAPACITY_MODEL_VERSION='account-demand-v6-idle-compaction'
NATIVE_CGROUP_USERS=pathlib.Path('/var/webuzo/conf/cgroupusers')
NATIVE_CGROUP_DROPIN=UNITS/'cgroup.service.d/90-uniselv-resman.conf'
```

### Block 2 — replace

Existing anchor AFTER which:
```text

def execute(args,check=True,timeout=60):
```

Existing anchor BEFORE which:
```text
    if check and r.returncode:raise RuntimeError('Command failed: '+str(args)+': exit='+str(r.returncode)+' '+r.stdout[-1200:]+r.stderr[-1200:])
    return r
```

Existing content to replace/remove (not copied):
```text
    r=subprocess.run(args,capture_output=True,text=True,timeout=timeout)
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
    # Only this supervisor owns its service notification endpoint. PHP syntax
    # checks and other children must not publish readiness/watchdog messages.
    env={key:value for key,value in os.environ.items() if key not in
         ('NOTIFY_SOCKET','WATCHDOG_PID','WATCHDOG_USEC')}
    r=subprocess.run(args,capture_output=True,text=True,timeout=timeout,env=env)
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text

def execute(args,check=True,timeout=60):
    # Only this supervisor owns its service notification endpoint. PHP syntax
    # checks and other children must not publish readiness/watchdog messages.
    env={key:value for key,value in os.environ.items() if key not in
         ('NOTIFY_SOCKET','WATCHDOG_PID','WATCHDOG_USEC')}
    r=subprocess.run(args,capture_output=True,text=True,timeout=timeout,env=env)
    if check and r.returncode:raise RuntimeError('Command failed: '+str(args)+': exit='+str(r.returncode)+' '+r.stdout[-1200:]+r.stderr[-1200:])
    return r
```

### Block 3 — insert

Existing anchor AFTER which:
```text
        except (OSError,ValueError,TypeError):continue
    return result


```

Existing anchor BEFORE which:
```text
def contention_ceiling(ceiling,relay_memory,p,pool_count):
    """Share a pressured cold grant; final admission still charges complete leases."""
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
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


def compact_idle_lease(unit, limits):
    """Release excess worker reservation only after native children have exited.

    The master retains one fully charged worker plus opcode/relay overhead.
    The caller holds its dispatch mutex with an empty request queue throughout.
    Unknown proc state or charged memory never earns a smaller reservation.
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
        if (proc/'task'/str(pid)/'children').read_text().strip():return False
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


```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text


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


def compact_idle_lease(unit, limits):
    """Release excess worker reservation only after native children have exited.

    The master retains one fully charged worker plus opcode/relay overhead.
    The caller holds its dispatch mutex with an empty request queue throughout.
    Unknown proc state or charged memory never earns a smaller reservation.
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
        if (proc/'task'/str(pid)/'children').read_text().strip():return False
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
```

### Block 4 — replace

Existing anchor AFTER which:
```text
        peers=waiting_units(unit)
        leases={path.name:json.loads(path.read_text()) for path in (RUN/'slots').glob('*.service')}
```

Existing anchor BEFORE which:
```text
        waiting=RUN/'waiting';waiting.mkdir(mode=0o700,exist_ok=True);ticket=waiting/unit
        def request(cap):
```

Existing content to replace/remove (not copied):
```text
        target=min(ceiling,contention_ceiling(ceiling,limits['memoryMiB'],p,len(set(leases)|peers))) if peers else ceiling
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
        pressure=peer_budget_pressure(leases,peers,p)
        target=min(ceiling,contention_ceiling(ceiling,limits['memoryMiB'],p,len(set(leases)|peers))) if pressure else ceiling
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
        peers=waiting_units(unit)
        leases={path.name:json.loads(path.read_text()) for path in (RUN/'slots').glob('*.service')}
        pressure=peer_budget_pressure(leases,peers,p)
        target=min(ceiling,contention_ceiling(ceiling,limits['memoryMiB'],p,len(set(leases)|peers))) if pressure else ceiling
        waiting=RUN/'waiting';waiting.mkdir(mode=0o700,exist_ok=True);ticket=waiting/unit
        def request(cap):
```

### Block 5 — insert

Existing anchor AFTER which:
```text
        def request(cap):
            atomic(ticket,json.dumps({'mode':'elastic','uid':uid,'ceiling':cap,
```

Existing anchor BEFORE which:
```text
                'expires':time.monotonic()+limits['timeout']+5}))
        if current>target:
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                'minimumMiB':p['workerRssMiB']+48+p['opcacheMiB']+limits['memoryMiB'],
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
        def request(cap):
            atomic(ticket,json.dumps({'mode':'elastic','uid':uid,'ceiling':cap,
                'minimumMiB':p['workerRssMiB']+48+p['opcacheMiB']+limits['memoryMiB'],
                'expires':time.monotonic()+limits['timeout']+5}))
        if current>target:
```

### Block 6 — insert

Existing anchor AFTER which:
```text
                'expires':time.monotonic()+limits['timeout']+5}))
        if current>target:
```

Existing anchor BEFORE which:
```text
            request(target)
            return {'ceiling':target,'previous':current,'reasonDetail':'peer_fair_share' if peers else 'account_boundary'}
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
            # No queued/forwarded request means this is an idle or post-response
            # backend. Let verified idle compaction/yield handle it; restarting
            # here would discard its warm cache or interrupt background work.
            if demand==0:
                clear_elastic_demand(unit);return None
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                'expires':time.monotonic()+limits['timeout']+5}))
        if current>target:
            # No queued/forwarded request means this is an idle or post-response
            # backend. Let verified idle compaction/yield handle it; restarting
            # here would discard its warm cache or interrupt background work.
            if demand==0:
                clear_elastic_demand(unit);return None
            request(target)
            return {'ceiling':target,'previous':current,'reasonDetail':'peer_fair_share' if peers else 'account_boundary'}
```

### Block 7 — replace

Existing anchor AFTER which:
```text
        charged=int((group/unit/'memory.current').read_text())/1048576
        reserved=sum(int(row['costMiB']) for name,row in leases.items() if name!=unit)
```

Existing anchor BEFORE which:
```text
            available+min(old_cost,charged),account_available)
        if granted>current:
```

Existing content to replace/remove (not copied):
```text
        granted,_=demand_grant(target,limits['memoryMiB'],p,reserved,
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
        granted,_=demand_grant(min(target,max(current,demand)),limits['memoryMiB'],p,reserved,
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
        charged=int((group/unit/'memory.current').read_text())/1048576
        reserved=sum(int(row['costMiB']) for name,row in leases.items() if name!=unit)
        granted,_=demand_grant(min(target,max(current,demand)),limits['memoryMiB'],p,reserved,
            available+min(old_cost,charged),account_available)
        if granted>current:
```

### Block 8 — replace

Existing anchor AFTER which:
```text
        if granted>current:
            if own.get('relayEnforced') and elastic_proxy_ready(unit):
```

Existing anchor BEFORE which:
```text
                atomic(lease,json.dumps(own));clear_elastic_demand(unit)
                return {'ceiling':granted,'previous':current,'reasonDetail':'queued_demand_growth','liveGrowth':True}
```

Existing content to replace/remove (not copied):
```text
                own.update(runtimeMaxChildren=granted,costMiB=granted*p['workerRssMiB']+48+p['opcacheMiB']+limits['memoryMiB'],lastResizeAt=time.time())
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                own.update(runtimeMaxChildren=granted,costMiB=granted*p['workerRssMiB']+48+p['opcacheMiB']+limits['memoryMiB'],lastResizeAt=time.time(),idleCompacted=False)
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
        if granted>current:
            if own.get('relayEnforced') and elastic_proxy_ready(unit):
                own.update(runtimeMaxChildren=granted,costMiB=granted*p['workerRssMiB']+48+p['opcacheMiB']+limits['memoryMiB'],lastResizeAt=time.time(),idleCompacted=False)
                atomic(lease,json.dumps(own));clear_elastic_demand(unit)
                return {'ceiling':granted,'previous':current,'reasonDetail':'queued_demand_growth','liveGrowth':True}
```

### Block 9 — insert

Existing anchor AFTER which:
```text
    waiting=RUN/'waiting';waiting.mkdir(mode=0o700,exist_ok=True);ticket=waiting/unit
    grant_ceiling=children
```

Existing anchor BEFORE which:
```text
    try:
        prior=json.loads(ticket.read_text()) if ticket.exists() else {}
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
    regrant=False
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
    waiting=RUN/'waiting';waiting.mkdir(mode=0o700,exist_ok=True);ticket=waiting/unit
    grant_ceiling=children
    regrant=False
    try:
        prior=json.loads(ticket.read_text()) if ticket.exists() else {}
```

### Block 10 — insert

Existing anchor AFTER which:
```text
                and type(prior.get('ceiling')) is int and 1<=prior['ceiling']<=children):
            grant_ceiling=prior['ceiling']
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
            regrant=True
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                and type(prior.get('ceiling')) is int and 1<=prior['ceiling']<=children):
            grant_ceiling=prior['ceiling']
            regrant=True

        while True:
```

### Block 11 — insert

Existing anchor AFTER which:
```text
                if peer_demand:
                    grant_ceiling=min(grant_ceiling,contention_ceiling(ceiling,relay['memoryMiB'],p,len({x.name for x in lease_paths}|peer_demand|{unit})))
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
                relay_enforced=dynamic and elastic_proxy_ready(unit)
                # One cold request needs one reservation. Verified relays can
                # acquire further capacity before dispatching queued requests.
                if relay_enforced and not regrant:grant_ceiling=min(grant_ceiling,1)
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                if peer_demand:
                    grant_ceiling=min(grant_ceiling,contention_ceiling(ceiling,relay['memoryMiB'],p,len({x.name for x in lease_paths}|peer_demand|{unit})))
                relay_enforced=dynamic and elastic_proxy_ready(unit)
                # One cold request needs one reservation. Verified relays can
                # acquire further capacity before dispatching queued requests.
                if relay_enforced and not regrant:grant_ceiling=min(grant_ceiling,1)
                granted,cost=demand_grant(min(ceiling,grant_ceiling),relay['memoryMiB'],p,reserved,available,account_available)
                eligible=granted>=1 if dynamic else (granted==children and len(list(slots.iterdir()))<p['maxActivePools'])
```

### Block 12 — remove

Existing anchor AFTER which:
```text
                eligible=granted>=1 if dynamic else (granted==children and len(list(slots.iterdir()))<p['maxActivePools'])
                if eligible:
```

Existing anchor BEFORE which:
```text
                    if dynamic:atomic(pool_path,private_backend(runtime_pool(pool,ceiling if relay_enforced else granted)))
                    atomic(lease,json.dumps({'costMiB':cost,'startedAt':time.time(),
```

Existing content to replace/remove (not copied):
```text
                    relay_enforced=dynamic and elastic_proxy_ready(unit)
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text

```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                eligible=granted>=1 if dynamic else (granted==children and len(list(slots.iterdir()))<p['maxActivePools'])
                if eligible:
                    if dynamic:atomic(pool_path,private_backend(runtime_pool(pool,ceiling if relay_enforced else granted)))
                    atomic(lease,json.dumps({'costMiB':cost,'startedAt':time.time(),
```

### Block 13 — replace

Existing anchor AFTER which:
```text
                    peers={x.name for x in lease_paths}|waiting_units()|{unit}
                    grant_ceiling=min(grant_ceiling,contention_ceiling(ceiling,relay['memoryMiB'],p,len(peers)))
```

Existing anchor BEFORE which:
```text
            if time.monotonic()>=deadline:
                minimum=p['workerRssMiB']+48+p['opcacheMiB']+relay['memoryMiB']
```

Existing content to replace/remove (not copied):
```text
                    atomic(ticket,json.dumps({'expires':deadline,'uid':actual_uid,'ceiling':grant_ceiling}))
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                    atomic(ticket,json.dumps({'expires':deadline,'uid':actual_uid,'ceiling':grant_ceiling,'minimumMiB':minimum}))
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                    peers={x.name for x in lease_paths}|waiting_units()|{unit}
                    grant_ceiling=min(grant_ceiling,contention_ceiling(ceiling,relay['memoryMiB'],p,len(peers)))
                    atomic(ticket,json.dumps({'expires':deadline,'uid':actual_uid,'ceiling':grant_ceiling,'minimumMiB':minimum}))
            if time.monotonic()>=deadline:
                minimum=p['workerRssMiB']+48+p['opcacheMiB']+relay['memoryMiB']
```

### Block 14 — replace

Existing anchor AFTER which:
```text
                # Accept into the bounded queue while current work drains.
            has_lease=not stop_backend or (RUN/'slots'/unit).exists()
```

Existing anchor BEFORE which:
```text
            if reason:
                diagnostic('warm_idle_retire' if reason=='warm_idle_expired' else 'idle_lease_yield',reasonDetail=reason)
```

Existing content to replace/remove (not copied):
```text
            reason=None if draining else idle_retirement_reason(time.monotonic()-activity['last'],int(idle),quiescent,has_lease and bool(waiting_units(unit)),available,host_reserve_mib)
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
            elapsed=time.monotonic()-activity['last']
            pressure=has_lease and bool(waiting_units(unit))
            if stop_backend and quiescent and not draining:
                try:
                    # Wait at least the native worker-idle interval before reclaiming
                    # reservations, and never compete with a dequeued request.
                    with dispatch:
                        if activity['active']==0 and pending.unfinished_tasks==0 and elapsed>=policy()['idleSeconds']:
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
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                # Accept into the bounded queue while current work drains.
            has_lease=not stop_backend or (RUN/'slots'/unit).exists()
            elapsed=time.monotonic()-activity['last']
            pressure=has_lease and bool(waiting_units(unit))
            if stop_backend and quiescent and not draining:
                try:
                    # Wait at least the native worker-idle interval before reclaiming
                    # reservations, and never compete with a dequeued request.
                    with dispatch:
                        if activity['active']==0 and pending.unfinished_tasks==0 and elapsed>=policy()['idleSeconds']:
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
```

### Block 15 — replace

Existing anchor AFTER which:
```text
            try:
                pending.put_nowait((client,deadline,accepted))
```

Existing anchor BEFORE which:
```text
            except queue.Full:
                diagnostic('queue_full_deadline',queued=pending.qsize())
```

Existing content to replace/remove (not copied):
```text
                with dispatch:dispatch.notify_all()
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                with dispatch:
                    # New burst demand should not wait for the periodic tick.
                    # Allocation still passes the same locked budget checks.
                    if stop_backend and activity['active']+pending.qsize()>dispatch_limit:
                        rebalance_after=0
                    dispatch.notify_all()
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
            try:
                pending.put_nowait((client,deadline,accepted))
                with dispatch:
                    # New burst demand should not wait for the periodic tick.
                    # Allocation still passes the same locked budget checks.
                    if stop_backend and activity['active']+pending.qsize()>dispatch_limit:
                        rebalance_after=0
                    dispatch.notify_all()
            except queue.Full:
                diagnostic('queue_full_deadline',queued=pending.qsize())
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
  "version": "1.1.30",
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
  "version": "1.1.31",
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
  "name": "UNISELV Resource Manager",
  "slug": "uniselv-resman",
  "version": "1.1.31",
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
Version: 1.1.30
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
Version: 1.1.31
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
/*
Plugin Name: UNISELV Resource Manager
Version: 1.1.31
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
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '-1.1.30r1' . '"></script>';

    echo '<div class="uniselv-container">';
    
```

Existing content to replace/remove (not copied):
```text
    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '-1.1.30r1' . '">';
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '-1.1.31r1' . '">';
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
    $i18n_dict = uniselv_get_i18n_dict();

    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '-1.1.31r1' . '">';
    echo '<style>:root { --uniselv-primary: ' . $brand_color . '; --primary-color: ' . $brand_color . '; }</style>';
    echo '<script>
```

### Block 3 — replace

Existing anchor AFTER which:
```text
    if (rtrim($brand_docs, '/') === 'https://docs.uniselv.com') $brand_docs = ''; // Historical placeholder; use bundled local Help.

    $panel_url = !empty($globals['panel_url']) ? rtrim($globals['panel_url'], '/') : '';
    $i18n_dict = uniselv_get_i18n_dict();

    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '-1.1.30r1' . '">';
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
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '-1.1.30r1' . '"></script>';
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '-1.1.31r1' . '"></script>';
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
window.UNISELV_TRANSLATIONS = ' . json_encode($i18n_dict[$locale] ?? $i18n_dict['en']) . ';
</script>';
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '-1.1.31r1' . '"></script>';

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
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '-1.1.30r1' . '"></script>';

    echo '<div class="uniselv-container">';

    // Header
```

Existing content to replace/remove (not copied):
```text
    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '-1.1.30r1' . '">';
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '-1.1.31r1' . '">';
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
    $i18n_dict = uniselv_get_i18n_dict();

    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '-1.1.31r1' . '">';
    echo '<style>:root { --uniselv-primary: ' . $brand_color . '; --primary-color: ' . $brand_color . '; }</style>';
    echo '<script>
```

### Block 5 — replace

Existing anchor AFTER which:
```text
    $limits = isset($dash['limits']) ? $dash['limits'] : [];

    $panel_url = !empty($globals['panel_url']) ? rtrim($globals['panel_url'], '/') : '';
    $i18n_dict = uniselv_get_i18n_dict();

    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '-1.1.30r1' . '">';
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
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '-1.1.30r1' . '"></script>';
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '-1.1.31r1' . '"></script>';
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
window.UNISELV_TRANSLATIONS = ' . json_encode($i18n_dict[$locale] ?? $i18n_dict['en']) . ';
</script>';
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '-1.1.31r1' . '"></script>';

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
            <details><summary>Operations, expected profile and verification scope</summary><pre style="white-space:pre-wrap;overflow-wrap:anywhere"><?php echo htmlspecialchars(file_get_contents(__DIR__ . '/../docs/release-1.1.30.md'), ENT_QUOTES, 'UTF-8'); ?></pre></details>
            <details><summary>Exact source replacement and insertion guide</summary><pre style="white-space:pre-wrap;overflow-wrap:anywhere"><?php echo htmlspecialchars(file_get_contents(__DIR__ . '/../docs/source-changes-1.1.30.md'), ENT_QUOTES, 'UTF-8'); ?></pre></details>
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
            <details><summary>Operations, expected profile and verification scope</summary><pre style="white-space:pre-wrap;overflow-wrap:anywhere"><?php echo htmlspecialchars(file_get_contents(__DIR__ . '/../docs/release-1.1.31.md'), ENT_QUOTES, 'UTF-8'); ?></pre></details>
            <details><summary>Exact source replacement and insertion guide</summary><pre style="white-space:pre-wrap;overflow-wrap:anywhere"><?php echo htmlspecialchars(file_get_contents(__DIR__ . '/../docs/source-changes-1.1.31.md'), ENT_QUOTES, 'UTF-8'); ?></pre></details>
            <details><summary>Measured resource allocation and current-host tests</summary><pre style="white-space:pre-wrap;overflow-wrap:anywhere"><?php echo htmlspecialchars(file_get_contents(__DIR__ . '/../docs/server-policy-report-1.1.31.md'), ENT_QUOTES, 'UTF-8'); ?></pre></details>
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
            <h4 class="uniselv-help-card-title">Runtime Operations, Exact Source Placement &amp; Validation Scope</h4>
            <div class="uniselv-help-card-desc">Release <?php echo $uniselvHelpEscape($uniselvHelpVersion); ?>. These technical guides describe already-applied changes; they are not additional post-install paste steps.</div>
            <details><summary>Operations, expected profile and verification scope</summary><pre style="white-space:pre-wrap;overflow-wrap:anywhere"><?php echo htmlspecialchars(file_get_contents(__DIR__ . '/../docs/release-1.1.31.md'), ENT_QUOTES, 'UTF-8'); ?></pre></details>
            <details><summary>Exact source replacement and insertion guide</summary><pre style="white-space:pre-wrap;overflow-wrap:anywhere"><?php echo htmlspecialchars(file_get_contents(__DIR__ . '/../docs/source-changes-1.1.31.md'), ENT_QUOTES, 'UTF-8'); ?></pre></details>
            <details><summary>Measured resource allocation and current-host tests</summary><pre style="white-space:pre-wrap;overflow-wrap:anywhere"><?php echo htmlspecialchars(file_get_contents(__DIR__ . '/../docs/server-policy-report-1.1.31.md'), ENT_QUOTES, 'UTF-8'); ?></pre></details>
        </div>

```
