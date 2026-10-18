# Existing-server lifecycle validation — 1.1.1

Date: 2026-10-17. Environment: Ubuntu 24.04, kernel 6.8.0-147-generic, Webuzo 4.8.4, 4 vCPU, approximately 7.57 GiB visible RAM; PHP 8.1 and 8.2. This is an existing-server adoption/upgrade test, not a fresh OS installation certificate.

## Evidence-backed results

- Private configuration archive and consistent SQLite backup captured before mutation; recovery archive downloaded locally. Recovery was exercised successfully after failed Golden Shield cycles.
- Created a disposable native Webuzo account; assigned Starter, Pro and Go and compared effective CPU quotas. Created, edited and deleted a disposable native resource plan through the plugin.
- First successful PHP instruction ran inside its account slice on PHP 8.1 and 8.2 after cold pool stops. CLI, child-process and actual cron execution were contained.
- Kernel enforcement survived an agent stop; killing the agent's main process triggered automatic restart.
- Four concurrent tenant CPU workloads averaged approximately 305% CPU under the 340% aggregate allowance, with throttling recorded. Panel HTTPS responses remained approximately 0.13–0.17 seconds; the authenticated root IPC overview completed in approximately 0.17 seconds. HTTPS 302 to login is a healthy response, not an outage.
- Disposable-account memory pressure produced a real account OOM kill with account swap blocked. Only that account's MemoryHigh was temporarily raised to its hard cap to avoid a prolonged reclaim stall; the prior value was restored. Host swap was disabled, so this is not a host-swap-enabled escape test.
- Bounded process admission stopped at 62 children with EAGAIN. The sampled parent pids.events counter did not change, so this observation alone does not attribute the rejection exclusively to that particular cgroup counter.
- Direct I/O measured approximately 41.5 MB/s write against a 44 MB/s cap and 68.1 MB/s read against a 73 MB/s cap. Temporary test data was removed.
- Plugin deactivate/reactivate and uninstall/reinstall recovered the agent, broker socket and panel. Uninstall preserved the adopted external core scripts and existing database. This does not test removal of plugin-owned protection on an otherwise clean server.
- Golden Shield checkpoint restore and disable/re-enable were exercised. Re-enable initially failed; the confirmed policy-overwrite defect was fixed and the final real cycle passed, including HTTP containment.
- Native virtual-host configuration regeneration passed. An exploratory native --rebuild-user operation removed the disposable probe; it is not treated as successful data-preserving regeneration and is not recommended as a routine plugin recovery command.
- Actual VPS reboot was verified through a changed kernel boot ID; SSH, Webuzo, Golden Shield and the plugin agent returned automatically, along with HTTP containment and finite resource limits.
- A second actual reboot confirmed native user quota enabled automatically. Final checks found no failed system services, only the original seven hosting accounts, correct HTTP containment and no remaining test probes.

## Fixes made during validation

1. The bundled Golden Shield installer embedded a previous VPS policy (6210 MiB) and overwrote the plugin's calculated policy (6471 MiB). It now requires and uses the configured policy. No previous-server hardware defaults are substituted during install.
2. Protection command exit failures are checked. Startup verification can wait up to 30 seconds for asynchronous services; the verification predicate is unchanged and failure evidence is returned.
3. This Ubuntu host lacked quota_v2 for its running kernel. Installed the matching official linux-modules-extra package, loaded the module and restarted native quotaon. An 8 MiB disposable-user quota rejected excess writes. This is a host repair, not a new kernel-package installer inside the plugin.

Regression reruns: 38 R6 assertions, 31 R7 assertions and four startup/policy-sizing unit tests passed. Syntax compilation passed. Assertion totals describe these suites only, not all product features.

## Historical failures and test corrections

Raw lifecycle evidence retains failed attempts. Initial requests to 127.0.0.1 hit the default vhost; corrected tests used the public-IP-bound tenant vhost. An initial load-test assertion incorrectly required HTTP 200 and rejected healthy 302 login redirects. A cleanup assertion attempted to delete an account already removed. These fixture errors are not counted as unexplained product failures.

The first newly provisioned account request returned 50X before isolation configuration settled; a later successful request was contained. Do not promise zero provisioning warm-up or uninterrupted availability while rebuilding/restarting services. Configuration snapshot restoration during diagnostic recovery also restored PHP configuration from before the disposable account existed; its resulting 50X is not evidence of normal stable-state operation.

## Remaining boundaries

Fresh OS install, physical hardware resize, host-swap-enabled pressure, arbitrary multi-device/LVM layouts, exhaustive browser workflows for every role and every feature, and heavy WordPress/database capacity were not certified here. Hardware sizing formulas were tested using supplied 2/4/8-vCPU profiles; this is not a real VPS resize.

No CSF/firewall settings were changed. Original hosting accounts were preserved; test accounts, probes and data were removed. Private backup archives and credentials must not be distributed in the plugin ZIP.

Raw evidence and final server checks are retained under the workspace vps-validation directory. The final second-reboot quota/service result is in lifecycle-finalcheck-20261017.txt and RESMAN-LIFECYCLE-EVIDENCE-20261017.json.
