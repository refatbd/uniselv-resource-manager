# Exact source changes — 1.1.32

Already-applied release source changes relative to 1.1.31; not extra post-install paste steps. Prefer the reviewed complete package.

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
CAPACITY_MODEL_VERSION='account-demand-v6-idle-compaction'
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
CAPACITY_MODEL_VERSION='account-demand-v7-stable-sharing'
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
PROXY='/usr/lib/systemd/systemd-socket-proxyd'
MARKER='# WEBUZO-ISOLATION MANAGED LAUNCHER'
CAPACITY_MODEL_VERSION='account-demand-v7-stable-sharing'
NATIVE_CGROUP_USERS=pathlib.Path('/var/webuzo/conf/cgroupusers')
NATIVE_CGROUP_DROPIN=UNITS/'cgroup.service.d/90-uniselv-resman.conf'
```

### Block 2 — insert

Existing anchor AFTER which:
```text
    return free<required


```

Existing anchor BEFORE which:
```text
def compact_idle_lease(unit, limits):
    """Release excess worker reservation only after native children have exited.
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
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


```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text


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
```

### Block 3 — replace

Existing anchor AFTER which:
```text

def compact_idle_lease(unit, limits):
```

Existing anchor BEFORE which:
```text

    The master retains one fully charged worker plus opcode/relay overhead.
```

Existing content to replace/remove (not copied):
```text
    """Release excess worker reservation only after native children have exited.
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
    """Release excess reservation after surplus native children have exited.
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text

def compact_idle_lease(unit, limits):
    """Release excess reservation after surplus native children have exited.

    The master retains one fully charged worker plus opcode/relay overhead.
```

### Block 4 — replace

Existing anchor AFTER which:
```text
    The master retains one fully charged worker plus opcode/relay overhead.
    The caller holds its dispatch mutex with an empty request queue throughout.
```

Existing anchor BEFORE which:
```text
    """
    match=re.fullmatch(r'wpiso-fpm-(php\d{2,3})-([a-z_][a-z0-9_-]*)\.service',unit)
    if not match:return False
```

Existing content to replace/remove (not copied):
```text
    Unknown proc state or charged memory never earns a smaller reservation.
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
    A sole remaining child must be proven idle on the private listener. Unknown
    proc state or excessive charged memory never earns a smaller reservation.
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
    The master retains one fully charged worker plus opcode/relay overhead.
    The caller holds its dispatch mutex with an empty request queue throughout.
    A sole remaining child must be proven idle on the private listener. Unknown
    proc state or excessive charged memory never earns a smaller reservation.
    """
    match=re.fullmatch(r'wpiso-fpm-(php\d{2,3})-([a-z_][a-z0-9_-]*)\.service',unit)
```

### Block 5 — replace

Existing anchor AFTER which:
```text
        if (proc/'cgroup').read_text().strip()!='0::'+expected:return False
        if not re.search(r'^Uid:\s+0\b',(proc/'status').read_text(),re.M):return False
```

Existing anchor BEFORE which:
```text
        cost=p['workerRssMiB']+48+p['opcacheMiB']+limits['memoryMiB']
        charged=int((pathlib.Path('/sys/fs/cgroup'+expected)/'memory.current').read_text())
```

Existing content to replace/remove (not copied):
```text
        if (proc/'task'/str(pid)/'children').read_text().strip():return False
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
        children=(proc/'task'/str(pid)/'children').read_text().split()
        if len(children)>1:return False
        if children and not backend_drained(unit,RUN/(match[1]+'-'+match[2]+'.sock')):return False
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
        if (proc/'cgroup').read_text().strip()!='0::'+expected:return False
        if not re.search(r'^Uid:\s+0\b',(proc/'status').read_text(),re.M):return False
        children=(proc/'task'/str(pid)/'children').read_text().split()
        if len(children)>1:return False
        if children and not backend_drained(unit,RUN/(match[1]+'-'+match[2]+'.sock')):return False
        cost=p['workerRssMiB']+48+p['opcacheMiB']+limits['memoryMiB']
        charged=int((pathlib.Path('/sys/fs/cgroup'+expected)/'memory.current').read_text())
```

### Block 6 — insert

Existing anchor AFTER which:
```text
        if not 1<=current<=native<=128:raise ValueError('Invalid elastic worker lease')
        ceiling=runtime_ceiling(uid,native,p,limits['queue'],limits['timeout'])
```

Existing anchor BEFORE which:
```text
        peers=waiting_units(unit)
        leases={path.name:json.loads(path.read_text()) for path in (RUN/'slots').glob('*.service')}
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
        publish_runtime_demand(unit,uid,ceiling,demand,p['workerRssMiB']+48+p['opcacheMiB']+limits['memoryMiB'])
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
        if not 1<=current<=native<=128:raise ValueError('Invalid elastic worker lease')
        ceiling=runtime_ceiling(uid,native,p,limits['queue'],limits['timeout'])
        publish_runtime_demand(unit,uid,ceiling,demand,p['workerRssMiB']+48+p['opcacheMiB']+limits['memoryMiB'])
        peers=waiting_units(unit)
        leases={path.name:json.loads(path.read_text()) for path in (RUN/'slots').glob('*.service')}
```

### Block 7 — replace

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
        pressure=peer_budget_pressure(leases,peers,p)
        target=min(ceiling,contention_ceiling(ceiling,limits['memoryMiB'],p,len(set(leases)|peers))) if pressure else ceiling
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
        target=fair_demand_ceiling(unit,ceiling,demand,leases,peers,p)
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
        peers=waiting_units(unit)
        leases={path.name:json.loads(path.read_text()) for path in (RUN/'slots').glob('*.service')}
        target=fair_demand_ceiling(unit,ceiling,demand,leases,peers,p)
        waiting=RUN/'waiting';waiting.mkdir(mode=0o700,exist_ok=True);ticket=waiting/unit
        def request(cap):
```

### Block 8 — replace

Existing anchor AFTER which:
```text
                clear_elastic_demand(unit);return None
            request(target)
```

Existing anchor BEFORE which:
```text
            clear_elastic_demand(unit);return None
        group=pathlib.Path('/sys/fs/cgroup'+account_cgroup(uid))
```

Existing content to replace/remove (not copied):
```text
            return {'ceiling':target,'previous':current,'reasonDetail':'peer_fair_share' if peers else 'account_boundary'}
        if demand<=current or current>=target:
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
            return {'ceiling':target,'previous':current,'reasonDetail':'peer_fair_share' if target<ceiling else 'account_boundary'}
        if demand<=current or current>=ceiling:
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                clear_elastic_demand(unit);return None
            request(target)
            return {'ceiling':target,'previous':current,'reasonDetail':'peer_fair_share' if target<ceiling else 'account_boundary'}
        if demand<=current or current>=ceiling:
            clear_elastic_demand(unit);return None
        if current>=target:
```

### Block 9 — insert

Existing anchor AFTER which:
```text
        if demand<=current or current>=target:
            clear_elastic_demand(unit);return None
```

Existing anchor BEFORE which:
```text
        group=pathlib.Path('/sys/fs/cgroup'+account_cgroup(uid))
        boundary=int((group/'memory.max').read_text())*.9/1048576
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
        if current>=target:
            request(target);return None  # Let idle reservations yield without destabilizing busy peers.
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
        if demand<=current or current>=ceiling:
            clear_elastic_demand(unit);return None
        if current>=target:
            request(target);return None  # Let idle reservations yield without destabilizing busy peers.
        group=pathlib.Path('/sys/fs/cgroup'+account_cgroup(uid))
        boundary=int((group/'memory.max').read_text())*.9/1048576
```

### Block 10 — replace

Existing anchor AFTER which:
```text
    pending=queue.Queue(maxsize=limits['queue']);lock=threading.Lock();start_lock=threading.Lock()
    stopping=threading.Event();activity={'last':time.monotonic(),'active':0,'forwarded':0}
```

Existing anchor BEFORE which:
```text
    old_signals={}
    if threading.current_thread() is threading.main_thread():
```

Existing content to replace/remove (not copied):
```text
    dispatch=threading.Condition(lock);draining=False;regrant=None;rebalance_after=0;drain_deadline=0;dispatch_limit=1 if stop_backend else limits['workers']
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
    dispatch=threading.Condition(lock);draining=False;regrant=None;rebalance_after=0;shrink_after=0;drain_deadline=0;dispatch_limit=1 if stop_backend else limits['workers']
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
    pending=queue.Queue(maxsize=limits['queue']);lock=threading.Lock();start_lock=threading.Lock()
    stopping=threading.Event();activity={'last':time.monotonic(),'active':0,'forwarded':0}
    dispatch=threading.Condition(lock);draining=False;regrant=None;rebalance_after=0;shrink_after=0;drain_deadline=0;dispatch_limit=1 if stop_backend else limits['workers']
    old_signals={}
    if threading.current_thread() is threading.main_thread():
```

### Block 11 — replace

Existing anchor AFTER which:
```text
                    limit=runtime_dispatch_limit(unit,limits['workers'])
                    with dispatch:dispatch_limit=limit;dispatch.notify_all()
```

Existing anchor BEFORE which:
```text
                    plan=elastic_regrant_plan(unit,limits,demand)
                    if plan:
```

Existing content to replace/remove (not copied):
```text
                    with lock:demand=activity['forwarded']+pending.qsize()
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                    with lock:demand=activity['active']+pending.qsize()
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                    limit=runtime_dispatch_limit(unit,limits['workers'])
                    with dispatch:dispatch_limit=limit;dispatch.notify_all()
                    with lock:demand=activity['active']+pending.qsize()
                    plan=elastic_regrant_plan(unit,limits,demand)
                    if plan:
```

### Block 12 — replace

Existing anchor AFTER which:
```text
                            with dispatch:dispatch_limit=runtime_dispatch_limit(unit,limits['workers']);dispatch.notify_all()
                            diagnostic('runtime_grant_grown',**plan)
```

Existing anchor BEFORE which:
```text
                            # Rebalancing must not consume a whole client deadline while
                            # an unforwarded/background PHP job prevents idle proof.
```

Existing content to replace/remove (not copied):
```text
                        else:
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                        elif time.monotonic()>=shrink_after:
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                            with dispatch:dispatch_limit=runtime_dispatch_limit(unit,limits['workers']);dispatch.notify_all()
                            diagnostic('runtime_grant_grown',**plan)
                        elif time.monotonic()>=shrink_after:
                            # Rebalancing must not consume a whole client deadline while
                            # an unforwarded/background PHP job prevents idle proof.
```

### Block 13 — insert

Existing anchor AFTER which:
```text
                    rebalance_after=time.monotonic()+max(2,min(15,limits['timeout']/4))
            if draining:
```

Existing anchor BEFORE which:
```text
                with lock:drained=activity['active']==0
                if drained and not backend_drained(unit,backend):drained=False
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                refresh_draining_demand(unit)
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                    rebalance_after=time.monotonic()+max(2,min(15,limits['timeout']/4))
            if draining:
                refresh_draining_demand(unit)
                with lock:drained=activity['active']==0
                if drained and not backend_drained(unit,backend):drained=False
```

### Block 14 — insert

Existing anchor AFTER which:
```text
                    with dispatch:draining=False;regrant=None;dispatch.notify_all()
                    rebalance_after=time.monotonic()+max(2,min(15,limits['timeout']/4))
```

Existing anchor BEFORE which:
```text
                    diagnostic('runtime_regrant_deferred',reasonDetail='backend_not_proven_idle')
                if drained:
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                    shrink_after=rebalance_after
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                    with dispatch:draining=False;regrant=None;dispatch.notify_all()
                    rebalance_after=time.monotonic()+max(2,min(15,limits['timeout']/4))
                    shrink_after=rebalance_after
                    diagnostic('runtime_regrant_deferred',reasonDetail='backend_not_proven_idle')
                if drained:
```

### Block 15 — replace

Existing anchor AFTER which:
```text
            if stop_backend and quiescent and not draining:
                try:
```

Existing anchor BEFORE which:
```text
                    with dispatch:
                        if activity['active']==0 and pending.unfinished_tasks==0 and elapsed>=policy()['idleSeconds']:
```

Existing content to replace/remove (not copied):
```text
                    # Wait at least the native worker-idle interval before reclaiming
                    # reservations, and never compete with a dequeued request.
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                    # Native surplus children must have exited; a sole remaining
                    # child must be proven accepting. Do not add another arbitrary
                    # idle delay or compete with a dequeued request.
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
            if stop_backend and quiescent and not draining:
                try:
                    # Native surplus children must have exited; a sole remaining
                    # child must be proven accepting. Do not add another arbitrary
                    # idle delay or compete with a dequeued request.
                    with dispatch:
                        if activity['active']==0 and pending.unfinished_tasks==0:
```

### Block 16 — replace

Existing anchor AFTER which:
```text
                    # reservations, and never compete with a dequeued request.
                    with dispatch:
```

Existing anchor BEFORE which:
```text
                            compacted=compact_idle_lease(unit,limits)
                            if compacted:
```

Existing content to replace/remove (not copied):
```text
                        if activity['active']==0 and pending.unfinished_tasks==0 and elapsed>=policy()['idleSeconds']:
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                        if activity['active']==0 and pending.unfinished_tasks==0:
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                    # idle delay or compete with a dequeued request.
                    with dispatch:
                        if activity['active']==0 and pending.unfinished_tasks==0:
                            compacted=compact_idle_lease(unit,limits)
                            if compacted:
```

### Block 17 — insert

Existing anchor AFTER which:
```text
                    # Allocation still passes the same locked budget checks.
                    if stop_backend and activity['active']+pending.qsize()>dispatch_limit:
```

Existing anchor BEFORE which:
```text
                        rebalance_after=0
                    dispatch.notify_all()
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                        # Wake live growth immediately, but never erase the
                        # separate cooldown of a deferred background-job drain.
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                    # Allocation still passes the same locked budget checks.
                    if stop_backend and activity['active']+pending.qsize()>dispatch_limit:
                        # Wake live growth immediately, but never erase the
                        # separate cooldown of a deferred background-job drain.
                        rebalance_after=0
                    dispatch.notify_all()
```

### Block 18 — insert

Existing anchor AFTER which:
```text
            try:clear_elastic_demand(unit)
            except (OSError,ValueError,TypeError):pass
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
            try:clear_runtime_demand(unit)
            except OSError:pass  # Expiry still bounds a failed cleanup; finish shutdown.
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
            try:clear_elastic_demand(unit)
            except (OSError,ValueError,TypeError):pass
            try:clear_runtime_demand(unit)
            except OSError:pass  # Expiry still bounds a failed cleanup; finish shutdown.
        while True:
            try:client,_,_=pending.get_nowait()
```

### Block 19 — replace

Existing anchor AFTER which:
```text
def release(unit):
    if not re.fullmatch(r'wpiso-fpm-php\d{2,3}-[a-z_][a-z0-9_-]*\.service',unit):raise ValueError('Invalid release unit')
```

Existing anchor BEFORE which:
```text

def is_managed(version):
```

Existing content to replace/remove (not copied):
```text
    with lock('admission'):(RUN/'slots'/unit).unlink(missing_ok=True)
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
    with lock('admission'):
        (RUN/'slots'/unit).unlink(missing_ok=True)
        # The proxy may still own queued work during a drained regrant.
        # Proxy shutdown clears demand; a crashed proxy expires automatically.
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
def release(unit):
    if not re.fullmatch(r'wpiso-fpm-php\d{2,3}-[a-z_][a-z0-9_-]*\.service',unit):raise ValueError('Invalid release unit')
    with lock('admission'):
        (RUN/'slots'/unit).unlink(missing_ok=True)
        # The proxy may still own queued work during a drained regrant.
        # Proxy shutdown clears demand; a crashed proxy expires automatically.

def is_managed(version):
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
  "version": "1.1.31",
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
  "version": "1.1.32",
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
  "name": "UNISELV Resource Manager",
  "slug": "uniselv-resman",
  "version": "1.1.32",
  "author": "<a href=\"https://refat.ovh\" target=\"_blank\">Refat Rahman</a>",
  "developer": {
```

### Block 2 — replace

Existing anchor AFTER which:
```text
  "download_url": "https://refat.ovh/plugins/uniselv-resman/",
  "download_link": "https://refat.ovh/plugins/uniselv-resman/uniselv-resman.zip",
```

Existing anchor BEFORE which:
```text
  "homepage": "https://refat.ovh"
}
```

Existing content to replace/remove (not copied):
```text
  "last_updated": "2026-10-25",
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
  "last_updated": "2026-10-26",
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
  "download_url": "https://refat.ovh/plugins/uniselv-resman/",
  "download_link": "https://refat.ovh/plugins/uniselv-resman/uniselv-resman.zip",
  "last_updated": "2026-10-26",
  "homepage": "https://refat.ovh"
}
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
Version: 1.1.31
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
Version: 1.1.32
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
/*
Plugin Name: UNISELV Resource Manager
Version: 1.1.32
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
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '-1.1.31r1' . '"></script>';

    echo '<div class="uniselv-container">';
    
```

Existing content to replace/remove (not copied):
```text
    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '-1.1.31r1' . '">';
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '-1.1.32r1' . '">';
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
    $i18n_dict = uniselv_get_i18n_dict();

    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '-1.1.32r1' . '">';
    echo '<style>:root { --uniselv-primary: ' . $brand_color . '; --primary-color: ' . $brand_color . '; }</style>';
    echo '<script>
```

### Block 3 — replace

Existing anchor AFTER which:
```text
    if (rtrim($brand_docs, '/') === 'https://docs.uniselv.com') $brand_docs = ''; // Historical placeholder; use bundled local Help.

    $panel_url = !empty($globals['panel_url']) ? rtrim($globals['panel_url'], '/') : '';
    $i18n_dict = uniselv_get_i18n_dict();

    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '-1.1.31r1' . '">';
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
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '-1.1.31r1' . '"></script>';
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '-1.1.32r1' . '"></script>';
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
window.UNISELV_TRANSLATIONS = ' . json_encode($i18n_dict[$locale] ?? $i18n_dict['en']) . ';
</script>';
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '-1.1.32r1' . '"></script>';

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
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '-1.1.31r1' . '"></script>';

    echo '<div class="uniselv-container">';

    // Header
```

Existing content to replace/remove (not copied):
```text
    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '-1.1.31r1' . '">';
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '-1.1.32r1' . '">';
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
    $i18n_dict = uniselv_get_i18n_dict();

    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '-1.1.32r1' . '">';
    echo '<style>:root { --uniselv-primary: ' . $brand_color . '; --primary-color: ' . $brand_color . '; }</style>';
    echo '<script>
```

### Block 5 — replace

Existing anchor AFTER which:
```text
    $limits = isset($dash['limits']) ? $dash['limits'] : [];

    $panel_url = !empty($globals['panel_url']) ? rtrim($globals['panel_url'], '/') : '';
    $i18n_dict = uniselv_get_i18n_dict();

    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '-1.1.31r1' . '">';
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
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '-1.1.31r1' . '"></script>';
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '-1.1.32r1' . '"></script>';
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
window.UNISELV_TRANSLATIONS = ' . json_encode($i18n_dict[$locale] ?? $i18n_dict['en']) . ';
</script>';
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '-1.1.32r1' . '"></script>';

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
                Native PHP-FPM defaults remain global; automatic account runtime caps borrow available shared capacity rather than reserving workers for idle accounts. Tuning values come from the reviewed generator profile, not this help page. Configured vs Effective Audit separates the private FPM ceiling from the current concurrent relay grant. A partial grant advertises queued demand and can grow in place without a PHP/OPcache restart. Fair-share reductions hold new work in the bounded queue and wait for forwarded work and verified backend idleness before re-admission. Root-only backend sockets and a PID/start-token proxy handshake prevent bypass and preserve compatibility with older running proxies. Warm masters retain OPcache while headroom permits, with a hardware-derived maximum idle duration; eligible peer demand or low host reserve can reclaim a quiescent lease early. Ondemand workers still retire using inherited global defaults. The native cgroup service uses a plugin-owned coexistence drop-in, preserving the vendor script and managed service descendants.
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                Native PHP-FPM defaults remain global; automatic account runtime caps borrow available shared capacity rather than reserving workers for idle accounts. Tuning values come from the reviewed generator profile, not this help page. Configured vs Effective Audit separates the private FPM ceiling from the current concurrent relay grant. A partial grant advertises queued demand and can grow in place without a PHP/OPcache restart. Active peers publish short-lived demand heartbeats separately from waiting tickets. Deterministic sharing charges idle reservations in full and lets lightly used peers leave worker capacity available to busier peers. A missing waiting ticket alone no longer means an account is idle. Queued demand is retained and refreshed across a drained backend restart. New arrivals can trigger immediate growth without erasing the separate cooldown after a deferred shrink. Fair-share reductions hold new work in the bounded queue and wait for forwarded work and verified backend idleness before re-admission. Root-only backend sockets and a PID/start-token proxy handshake prevent bypass and preserve compatibility with older running proxies. Warm masters retain OPcache while headroom permits, with a hardware-derived maximum idle duration; eligible peer demand or low host reserve can reclaim a quiescent lease early. Ondemand workers still retire using inherited global defaults. The native cgroup service uses a plugin-owned coexistence drop-in, preserving the vendor script and managed service descendants.
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                    <li><strong>Recover or export:</strong> Use <strong>Recover Pending Operation</strong> for an interrupted lifecycle transaction, or <strong>Prepare &amp; Download Comparison</strong> for private diagnostics. Failed recovery retains its journal. Exports contain account paths; share privately.</li>
                </ol>
                Native PHP-FPM defaults remain global; automatic account runtime caps borrow available shared capacity rather than reserving workers for idle accounts. Tuning values come from the reviewed generator profile, not this help page. Configured vs Effective Audit separates the private FPM ceiling from the current concurrent relay grant. A partial grant advertises queued demand and can grow in place without a PHP/OPcache restart. Active peers publish short-lived demand heartbeats separately from waiting tickets. Deterministic sharing charges idle reservations in full and lets lightly used peers leave worker capacity available to busier peers. A missing waiting ticket alone no longer means an account is idle. Queued demand is retained and refreshed across a drained backend restart. New arrivals can trigger immediate growth without erasing the separate cooldown after a deferred shrink. Fair-share reductions hold new work in the bounded queue and wait for forwarded work and verified backend idleness before re-admission. Root-only backend sockets and a PID/start-token proxy handshake prevent bypass and preserve compatibility with older running proxies. Warm masters retain OPcache while headroom permits, with a hardware-derived maximum idle duration; eligible peer demand or low host reserve can reclaim a quiescent lease early. Ondemand workers still retire using inherited global defaults. The native cgroup service uses a plugin-owned coexistence drop-in, preserving the vendor script and managed service descendants.
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
            <details><summary>Operations, expected profile and verification scope</summary><pre style="white-space:pre-wrap;overflow-wrap:anywhere"><?php echo htmlspecialchars(file_get_contents(__DIR__ . '/../docs/release-1.1.31.md'), ENT_QUOTES, 'UTF-8'); ?></pre></details>
            <details><summary>Exact source replacement and insertion guide</summary><pre style="white-space:pre-wrap;overflow-wrap:anywhere"><?php echo htmlspecialchars(file_get_contents(__DIR__ . '/../docs/source-changes-1.1.31.md'), ENT_QUOTES, 'UTF-8'); ?></pre></details>
            <details><summary>Measured resource allocation and current-host tests</summary><pre style="white-space:pre-wrap;overflow-wrap:anywhere"><?php echo htmlspecialchars(file_get_contents(__DIR__ . '/../docs/server-policy-report-1.1.31.md'), ENT_QUOTES, 'UTF-8'); ?></pre></details>
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
            <details><summary>Operations, expected profile and verification scope</summary><pre style="white-space:pre-wrap;overflow-wrap:anywhere"><?php echo htmlspecialchars(file_get_contents(__DIR__ . '/../docs/release-1.1.32.md'), ENT_QUOTES, 'UTF-8'); ?></pre></details>
            <details><summary>Exact source replacement and insertion guide</summary><pre style="white-space:pre-wrap;overflow-wrap:anywhere"><?php echo htmlspecialchars(file_get_contents(__DIR__ . '/../docs/source-changes-1.1.32.md'), ENT_QUOTES, 'UTF-8'); ?></pre></details>
            <details><summary>Measured resource allocation and current-host tests</summary><pre style="white-space:pre-wrap;overflow-wrap:anywhere"><?php echo htmlspecialchars(file_get_contents(__DIR__ . '/../docs/server-policy-report-1.1.32.md'), ENT_QUOTES, 'UTF-8'); ?></pre></details>
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
            <h4 class="uniselv-help-card-title">Runtime Operations, Exact Source Placement &amp; Validation Scope</h4>
            <div class="uniselv-help-card-desc">Release <?php echo $uniselvHelpEscape($uniselvHelpVersion); ?>. These technical guides describe already-applied changes; they are not additional post-install paste steps.</div>
            <details><summary>Operations, expected profile and verification scope</summary><pre style="white-space:pre-wrap;overflow-wrap:anywhere"><?php echo htmlspecialchars(file_get_contents(__DIR__ . '/../docs/release-1.1.32.md'), ENT_QUOTES, 'UTF-8'); ?></pre></details>
            <details><summary>Exact source replacement and insertion guide</summary><pre style="white-space:pre-wrap;overflow-wrap:anywhere"><?php echo htmlspecialchars(file_get_contents(__DIR__ . '/../docs/source-changes-1.1.32.md'), ENT_QUOTES, 'UTF-8'); ?></pre></details>
            <details><summary>Measured resource allocation and current-host tests</summary><pre style="white-space:pre-wrap;overflow-wrap:anywhere"><?php echo htmlspecialchars(file_get_contents(__DIR__ . '/../docs/server-policy-report-1.1.32.md'), ENT_QUOTES, 'UTF-8'); ?></pre></details>
        </div>

```
