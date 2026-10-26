# Demand-pressure PHP sharing — Resource Manager 1.1.20

This governor follows physical hardware and live demand. It has no fixed visitor target, and registered idle accounts reserve no PHP workers, OPcache or pool lease. Native global PHP-FPM defaults remain identical across installed PHP versions. Private runtime grants remain bounded by each account's native RAM/Tasks limits, current working memory, full existing leases, MemAvailable and the shared physical budget.

## What changed

Previously, a cold pool could borrow the entire available burst allowance and keep that complete reservation until its ordinary idle timeout. A different account could wait even after the first pool finished its requests. Version 1.1.20 publishes short-lived root-only demand tickets only when the waiting account can fit its own minimum footprint but the shared allowance is exhausted. A backend with no active request and no unfinished queued request then yields its lease promptly. Active/queued requests drain; they are not killed, replayed or migrated.

The waiting cold grant receives a soft memory share based on live leases and current waiting demand. Native limits and final full reservation checks still apply. There is no division by the number of registered accounts, no per-user native FPM form, and no multiplication of physical limits by overselling. Isolated accounts with insufficient own RAM do not force unrelated idle pools to recycle.

```text
pool_overhead = 48 MiB + generated OPcache + generated relay allowance
soft_workers = min(native/account ceiling,
                   max(1, floor((physical PHP budget / live demanders - pool_overhead)
                                / generated worker RSS)))
final grant = existing shared/account/host admission checks applied to soft_workers
```

The soft share is considered after an admission attempt is blocked. A solitary pool can still borrow its full safe burst. On the reviewed 3127-MiB PHP budget, eight global workers and 288-MiB worker estimate, two pressured pools have a four-worker soft example, three have two, and four have one. These are memory-envelope examples, not entitlements or preallocated shares. Exact grants depend on arrival order, native account boundaries and remaining full leases. A busy reduced grant does not grow in place; later cold admission can borrow unused capacity again. Fully busy pools are not forcibly preempted. Sustained fairness under every workload remains a separate gate.

Tickets live only under `/run/webuzo-isolation/waiting/`, mode 0700. Expired, malformed and nonfinite entries are ignored; the producer removes its ticket when its bounded attempt exits. Existing request/queue timeouts remain in effect. The idle decision uses unfinished queue tasks, covering the dequeue-before-active-counter race.

## Exact source placement and update

Existing files: `/usr/local/sbin/webuzo-isolation.py`, `/usr/local/uniselv-resman/core/webuzo-isolation.py`, `/usr/local/webuzo/plugins/uniselv-resman/core/webuzo-isolation.py`.

Use the complete reviewed program from the release, replacing the existing complete program AFTER the start-of-file boundary and BEFORE EOF. Its first line is `#!/usr/bin/python3`; its final exception-handler line ends with `sys.exit(1)`. Never append a second program. Preserve original backups, owner/mode and the ownership manifest. The supported installer/update path must reject unknown adopted-source drift; do not bypass that rejection.

Review anchors: `waiting_units()` and `contention_ceiling()` are AFTER `demand_grant()` and BEFORE `account_memory_usage()`. The changed `admit()` block is AFTER the existing `slots=RUN/'slots'...` initialization and BEFORE `def connect_backend(...)`. The changed proxy idle decision is AFTER `diagnostic('started',**limits)` and BEFORE the existing `listener.accept()`. These identify the complete-source changes; they are not separate paste commands.

Illustrative AFTER-edit excerpt only, not a fragment to paste into an old program:

```python
diagnostic('started',**limits)
while not stopping.is_set():
    with lock:quiescent=not activity['active'] and pending.unfinished_tasks==0
    if quiescent and waiting_units(unit):
        diagnostic('idle_lease_yield',reasonDetail='waiting_peer_admission')
        return
    try:client,_=listener.accept()
```

The unchanged native/global configuration is separate from `/etc/webuzo-isolation/phpXX/ACCOUNT.conf`, the private managed runtime copy. Do not hand-edit native per-user defaults. The release's policy is one complete JSON object; replace from its first `{` through its final `}`, never append duplicate objects or keys. All hardware-dependent values still originate in Global Inputs.

Save/verification: validate Python syntax and recognized source hashes; retain a task-scoped rollback backup; reconcile installed versions in maintenance; verify ownership, coordinator/private-health services and native placement. Run request-drain, pressure-sharing, idle-release and bounded workload tests before committing the update. Check the final rollback state. English/JSON generator exports carry this behavior and its limits.

## Recorded evidence and limits

22 targeted Resource Manager checks passed, including real-socket active/queued drain, malformed/expired demand tickets, own-account-shortage isolation and conservative full-budget arithmetic. The reviewed VPS passed a finite 50-actor, 300-ms-CPU/32-MiB-allocation PHP fixture: 377 requests, zero failures, p95 1.6985 s. Native requests stayed in their assigned account cgroups. Two peer accounts started in 1.590 and 1.797 s after idle lease yield. Observed concurrent grants were 3/2/2, reserving 3051 MiB against 3127 MiB. Idle reservations returned to zero; test files were removed; no OOM occurred.

This fixture bypasses WordPress, SQL, browser assets and cache layers. The separate current WooCommerce cloud baseline reached 40 total VUs but failed its 15-second latency gate; it is not certified by the fixture. Read `uncached-capacity-validation.json` for exact versions, workloads and open gates. Real site repairs, heavy mixed tenants, payment paths and changed-profile reboot/vendor regeneration remain separate.
