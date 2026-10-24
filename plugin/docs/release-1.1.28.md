# Resource Manager 1.1.28 — elastic runtime concurrency

## Problem and resulting behavior

A real account with an eight-worker native/account ceiling was stuck on a one-worker private FPM cap. Other warm leases held shared admission reservations. The old partial grant returned successfully without advertising unmet demand, and the pool had no growth path. CPU peaked near 95 percent of a 280-percent account allowance while more than 5.8 GiB of host RAM remained available. Lifecycle/configuration parity alone did not detect this performance defect.

New proxies enforce the live concurrency grant themselves. The private FPM configuration retains the account-derived ceiling, while the relay dispatches only as many requests as the charged grant permits. Queued demand can acquire unreserved physical budget and increase dispatch immediately without restarting PHP or discarding OPcache. Partial grants publish expiring demand tickets so quiescent warm peers can release unused reservations. Fresh admissions honor existing waiting peers.

A reduction in fair share, or migration from a legacy pool, holds new requests in the existing bounded queue, drains forwarded work and verifies backend idleness before stopping/re-admitting that backend. A disconnected browser does not prove PHP finished: children must be gone or verifiably waiting to accept on that exact private listener. Unknown proc/kernel visibility defers the transition instead of force-stopping a job. Queue deadlines remain bounded; requests are never replayed. Re-admission rechecks current physical/account limits rather than promising a previously calculated grant.

## Enforcement and compatibility

The actual FPM backend socket is root:root 0600. Apache retains the native nobody-owned front socket; only the root proxy reaches the backend. Non-empty native listener ACL overrides are unsupported and block this mode. A root-only PID/start-token/cgroup/command handshake proves a new proxy is running before admission permits a private FPM ceiling larger than the concurrent grant. Old running proxies keep the older bounded FPM-cap method. Native Webuzo global PHP defaults remain shared; no manual native per-user PHP-FPM override is created. Existing CPU, RAM, task, global PHP budgets and safety reserves are unchanged.

Webuzo Admin > Plugins > UNISELV Resources > Configured vs Effective Audit > Automatic PHP Runtime Capacity now separates Native ceiling, Private FPM ceiling, Concurrent grant and Enforcement. A warm reservation is a reclaimable planning amount, not measured physical RAM and not proof of a human visitor. System & Agent Health continues to report mechanics and placement separately from application capacity.

## First corrected live experiment

Origin anonymous GET browsing, deterministic home/product mix and 5–10 second think time. Cloudflare was bypassed by direct TLS origin resolution; every successful measured response reported application cache BYPASS, with zero cache hits. No cart, checkout, payment or WordPress code/configuration changes.

| Stage | Requests | HTTP failures | Median | p95 |
|---|---:|---:|---:|---:|
| Before: 5 shoppers | 18 | 0 | 5.318 s | 18.772 s |
| Corrected: 5 shoppers | 24 | 0 | 2.037 s | 2.616 s |
| Corrected: 10 shoppers | 36 | 0 | 4.133 s | 10.834 s |
| Corrected: 20 shoppers | 55 | 0 | 10.378 s | 17.709 s |

The corrected run observed concurrency grants 4 and 8, up to eight PHP workers, account CPU approximately 281 percent over sampled intervals and 472 additional throttled periods at the configured 280-percent allowance. Minimum available RAM was 5378 MiB. This establishes that the artificial one-worker bottleneck was removed; the 20-shopper stage still exceeded the 15-second latency target. Forty to eighty WooCommerce shoppers, full browser assets and payment flows are not certified. Automated work on another account was observed despite the assumption that other sites had no human visitors; its secret URL was not retained in this report.

The earlier report belongs to 1.1.27 and is preserved. It is not relabelled as a pass. Current-run source changes, final bounded tests and startup checks are listed in elastic-validation-1.1.28.json. Prior native PHP install/remove, account/quota, shared-service and reboot tests are dated 1.1.27 evidence rather than universal certification of this release. Clean-OS/full reset requires a separate disposable VPS, which is unavailable. CSF remains owner-managed.

## Apply, verify and rollback

Prefer the complete reviewed plugin package and its privileged runtime upgrade workflow. Uploading source alone cannot replace code already loaded by a running Python proxy. Observe the Enforcement column and current leases after a safe controlled refresh or restart. Never stop an active pool merely to change its display. This live deployment keeps root-owned backups and matching ownership receipts.

Verify syntax, the isolated regression/drain tests, configured/live parity, account placement, protected root-only backend socket, proxy handshake and before/after HTTP results. Review growth/drain journal events without exporting unrelated cron commands or secrets. On rollback, drain and stop affected managed backends before returning to an old proxy/core; old code must re-admit and regenerate a real FPM cap before serving requests. Restore source and ownership/recovery receipts together. Do not run an old ungated proxy against a newer high-ceiling FPM pool with a smaller charged grant.

Exact already-applied replacements, verified anchors, copied code versus context and save/verification steps are in source-changes-1.1.28.md/.json. Do not append their code to an updated installation. Canonical generator: uniselv.win/webuzo-planner/. Embedded source hashes and eight hardware/overselling cases are checked; no physical safety budget was increased to obtain the improvement.

Final post-reboot validation passed: 140 regression tests, eight generator cases, 331 live value checks with zero mismatches, protected private sockets and 25-account placement. The post-reboot 5/10-shopper p95 values were 2.935/5.883 seconds, with all 69 requests including warm-up successful. The first corrected 20-shopper p95 remains 17.709 seconds; it was not rerun as a new maximum visitor certificate. See elastic-results-1.1.28.md and elastic-validation-1.1.28.json for dated scope, background event and boot-settling qualifications.
