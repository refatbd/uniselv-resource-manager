# Elastic runtime correction — 1.1.28

The sustained partial-grant bottleneck is fixed on the current server. Native CPU/RAM/task limits, global PHP defaults and the 3127-MiB shared PHP budget were not increased. Native global FPM settings remain shared across installed versions.

The old one-worker private cap queued requests with unused CPU/RAM. New protected proxies charge and enforce a concurrent relay grant separately from the account-derived FPM ceiling. Queued demand advertises pressure and can grow the charged grant in place, retaining the PHP master/OPcache. Waiting peers can reclaim genuinely unused warm reservations. Reductions preserve bounded queues, drain forwarded requests and verify backend idleness before re-admission. Root-only backend sockets and a PID/start-token/cgroup handshake prevent bypass and preserve compatibility with old proxies.

## Measured results

Anonymous origin GET browsing with 5–10 second think time. All marked responses confirmed application cache BYPASS; no cache hits. No website code/configuration, carts, orders or payments changed.

| Run | Simulated shoppers | Requests | Failures | Median | p95 |
|---|---:|---:|---:|---:|---:|
| Before correction | 5 | 18 | 0 | 5.318 s | 18.772 s |
| First corrected | 5 | 24 | 0 | 2.037 s | 2.616 s |
| First corrected | 10 | 36 | 0 | 4.133 s | 10.834 s |
| First corrected | 20 | 55 | 0 | 10.378 s | 17.709 s |
| Final after reboot | 5 | 24 | 0 | 2.257 s | 2.935 s |
| Final after reboot | 10 | 42 | 0 | 2.331 s | 5.883 s |

The final run had 69 successful requests including warm-up, up to eight PHP workers, sampled account CPU up to 275.9 percent, minimum host available RAM 5517.8 MiB and no account OOM kills. A grant changed from four to eight with its lease start preserved. The first corrected heavier run reached the configured 280-percent CPU allowance and added throttled periods. This establishes removal of artificial one-worker serialization; it does not eliminate application CPU cost or certify 40–80 shoppers. Stage percentiles are separate; different runs are not one combined percentile.

## Verification and limits

140 isolated regression tests passed, including growth, peer fairness, physical/account bounds, legacy compatibility, PID reuse, protected sockets, active/queued transport, no-replay drain, disconnected background-job detection, uncertain backend deferral and failed restart handling. Syntax checks covered 13 Python, 10 PHP and 64 JavaScript files. Eight hardware/overselling generator cases and embedded source checksums passed.

The final Apache/isolation/agent code was rebooted. After native PHP reconciliation settled, all core services, 25-account placement, boost recovery and 331 generated/live configuration checks passed with zero mismatches. Protected files and account inventory survived reboot. New private backends were root:root 0600, and a real hosting UID was denied direct connection. Source/ownership receipts were backed up together; complete package source parity and ZIP integrity are checked separately.

A transient early-boot reconciliation observation is preserved. One background ConnectionResetError predates the marked final load window and is retained as background evidence. There is no claim that all traffic was error-free. No temporary WordPress diagnostic files, cron jobs or hosting accounts were created for this correction; test curl/monitor processes exited.

Prior 1.1.27 provisioning/native-version/quota/lifecycle evidence remains historical. Clean-OS/full reset requires another VPS, which is unavailable; future vendor/hardware, active swap, per-account SQL CPU/RAM isolation, arbitrary launchers, mail/backup and CSF are not certified by this bounded test. Unsupported proc/kernel visibility defers a regrant until idle can be proven rather than force-stopping a job. The owner deferred website audit/fixes.

See release-1.1.28.md and source-changes-1.1.28.md/.json for the full behavior, exact file replacements and anchors, save/verification and safe rollback requirements. The canonical generator is uniselv.win/webuzo-planner/. Readiness metadata was refreshed after boot while keeping all generated physical/global settings identical.
