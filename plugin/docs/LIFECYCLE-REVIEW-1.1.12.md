# UNISELV Resource Manager 1.1.12 — lifecycle and safety validation

Date: 2026-10-18. This report supersedes earlier readiness statements for the changed components; older reports retain their original scope.

## Validated scope

Existing Ubuntu VPS, 4 vCPU / 8-GB-class hardware, Webuzo 4.8.4, cgroups v2, installed PHP 8.1 and 8.2. The test preserves the seven original hosting accounts. No physical VPS resize or fresh OS installation was performed in this run. A new server must pass installer compatibility and effective-protection checks; existing-host results are not evidence for every vendor image or workload.

## Changes

- Checked file deployment, atomic ownership manifests, required command exit codes, service readiness and panel Nginx validation/reload. Installation no longer silently ignores failed dependency activation.
- Added a journaled bootstrap for missing bundled isolation, Golden Shield and PAM dependencies. Plugin-owned components are distinguished from adopted external integrations; uninstall preserves adopted ones. Unsupported or changed implementations stop activation rather than being silently overwritten.
- Fixed the bundled isolation/Golden Shield bootstrap mismatch. Routing supports native account slices when Golden Shield is removed, and Golden account slices while it is installed. An interrupted core uninstall retains its installation marker and recovery state until restoration finishes.
- Added cross-process locking for managed-file recovery records. Six concurrent processes performing 120 writes retained all file records and hashes.
- Fixed deleted-account reconciliation: a removed username no longer prevents processing the regenerated native pool configuration. Healthy status returns after reconciliation.
- Installer/uninstaller reload native PHP service bridges, not each internal coordinator, proxy and health unit. This avoids competing restarts and interrupted checks. A syntax-only PHP process terminated with SIGTERM receives up to three attempts; real syntax errors fail immediately.
- Uninstall works without the PHP cURL extension, using checked system cURL verification. Tenant verification allows bounded native reload recovery; wrong identity/payload still fails. Maintenance reloads can briefly interrupt requests; zero-downtime maintenance is not claimed.
- Failed tracker restoration blocks deactivate/uninstall cleanup and retains recovery assets. Unknown web integration files are preserved. Panel reload uses validated graceful Nginx reload.
- Manual CPU/RAM overrides cannot consume the hardware-scaled Auto reserve. Invalid modes, non-integer values and oversized restore checkpoints are rejected before mutation. Restore failure makes at most one rollback attempt and reports an inconsistent state if that attempt fails. Backup IDs are unique and policy mutations are serialized.
- Tightened actual reseller authentication, owned-account inventory, audit filtering and permission revocation. Server-wide policy actions remain root-admin only. Native plan save reports and audits partial synchronization failure instead of swallowing it.
- Golden Shield disable retains its cap when core restoration fails and no longer reports a false successful disable. Help explains ownership, maintenance, bounded recovery and Manual-mode downgrade precautions.

## Live results

`RESMAN-1112-ACCOUNTS.json`: 29 passing assertions, including new native reseller/child account creation, first HTTP and subsecond CLI entry containment, cold PHP 8.1/8.2 first instruction, native resource-plan creation/assignment/edit with kernel CPU confirmation, actual reseller ownership boundaries, agent stop, forced agent crash/restart, native vhost regeneration, both PHP reloads, actual account cron entry, checkpoint restore and disposable account/plan cleanup. PHP 8.1 used an existing eligible native pool; the new account used its native PHP 8.2 pool. No unconfigured per-version pool was assumed.

`RESMAN-1112-LIFECYCLE.json`: 14 passing assertions in the final install → deactivate → activate → uninstall → install cycle, with HTTP containment and panel availability checks after actions and preserved adopted dependency ownership.

`RESMAN-1112-REBOOT.json`: boot ID changed; Webuzo, agent, Golden Shield, managed Apache and both PHP coordinators became active; first customer HTTP execution was contained; effective protection verification passed. Initial SSH reconnection attempts failed during restart, then recovered without provider-console action. The OS reported approximately 21.6 seconds of kernel/userspace startup; this does not equate to the external reconnection delay.

`RESMAN-1112-LOAD.json`: eight bounded CPU workers in the Master account, with Circuit Breaker temporarily paused through the plugin API to isolate Golden Shield. Aggregate cap was **340000 / 100000**, measured mean **300.84% CPU** over **27.48 seconds**, with **170 additional quota-throttled periods**. All **24 HTTP requests** succeeded (12 panel, 12 WordPress homepage). Circuit Breaker was restored to its original enabled setting. An earlier enabled-Circuit-Breaker run reduced the Master runtime allowance to 170%; this intentional additional throttle is not a failed aggregate cap. These are bounded availability/enforcement checks, not an unlimited WordPress capacity guarantee.

## Failure and regression tests

- 26 safety, ownership/bootstrap composition, policy/rollback, reseller permission and syntax-interruption unit tests.
- 9 backend regressions and 8 frontend regressions retained from the prepublication fixes.
- 11 private mount-namespace PHP lifecycle cases: full manifest filesystem, invalid deployment target, foreign isolation, read-only INI, third-party tracker chaining, read-only restoration, corrupt recovery manifest, plugin-owned cleanup, adopted preservation and failed deactivation cleanup. Service operations are stubbed in these namespace cases; they prove filesystem/error-handling behavior, not a clean-host kernel deployment.
- Six-process/120-write real Linux managed-registry concurrency check.

Missing-component bootstrap/owned-removal orchestration is tested with controlled composition fixtures. The actual live lifecycle uses the existing adopted protection stack. No full removal/reinstallation of every adopted protection component or fresh OS deployment is claimed for 1.1.12. Prior WordPress/cart/capacity evidence remains tied to its original release and workload.

## Recovery and remaining boundaries

Private consistent database/configuration/integration backups were taken before mutation. Recovery was exercised during failed trials; stale adopted PAM recovery metadata was reconstructed only when current hooks and saved originals matched archived hashes. Reviewed orphan test-slice metadata was quarantined/reconciled without changing original account plans. Disposable users, plan, cron, probes and test timers are cleaned after verification. CSF configuration is unchanged.

Real VPS hardware resize remains excluded at the owner's request. 2/4/8/32-vCPU sizing models are tested; they are not live resize evidence. Before a downgrade in Manual mode, reduce overrides to fit the smaller physical capacity and reserve. New PHP/vendor layouts, destructive clean OS installation and arbitrary production application mixes require their own compatibility/capacity evidence. The previously observed optional vendor memcached library dependency is separate from this plugin and has not been repaired by masking the extension.
