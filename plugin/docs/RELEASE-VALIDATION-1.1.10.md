# Release validation — UNISELV Resource Manager 1.1.10

Date: 2026-10-18. Environment: existing Ubuntu 24.04 Webuzo VPS, 4 vCPU, approximately 8 GB RAM, native Apache/FastCGI, PHP 8.1 and 8.2. This release addresses the remaining installer status, reproducible Apache integration, and bounded application/CPU-pressure findings.

## Changes and verified behavior

- Required PHP configuration failures now return nonzero even if every mutation failed. An isolated execution of the deployed configuration block with an unwritable manifest path returned exit 1 and left the original ini unchanged.
- Apache retry configuration is shipped and installed automatically. Real install -> uninstall -> install -> repeated install -> check passed. The old per-domain test override was backed up and replaced by a comment before final load testing; results no longer depend on it. Five isolated ownership/rollback tests passed.
- Diagnosing the original failures found kernel task-controller rejection in the FastCGI proxy: per-request systemctl subprocesses exhausted TasksMax=12, killing the proxy and cutting off PHP requests. Warm connections now use no subprocess; cold starts serialize; thread-start rejection retains the proxy; FastCGI END_REQUEST promptly releases admission slots. Account limits and proxy TasksMax were not increased. Four Linux socket/concurrency tests passed, including fragmented response headers and a backend keeping its socket open after END_REQUEST.
- Six recovery/statistics tests passed. The read-only search/catalog load runner may retry a disconnected persistent GET connection once and records that initial failure. It does not retry HTTP status errors, timeouts, cart mutations or checkout. This benchmark behavior is not installed into customer applications and does not eliminate every possible network interruption.

## Repeated application observations

Each stage used 8 virtual users, 3 seconds warmup and 45 seconds measurement. Final operation counts include drain; window throughput uses only completions within the window.

| Run | Workload | Final successful / attempted operations | Recovered transport interruptions | Window operations/sec | p95 ms |
|---|---|---|---|---|---|
| 1 | heavy | 169 / 169 | 0 | 3.58 | 3891.99 |
| 1 | dynamic | 255 / 255 | 0 | 5.51 | 1914.77 |
| 2 | heavy | 127 / 127 | 4 | 2.64 | 4761.17 |
| 2 | dynamic | 179 / 179 | 0 | 3.8 | 3415.95 |

No final HTTP 503 responses occurred in these repeated stages. Initial transport interruptions remain visible in the raw evidence; successful logical operations are not a claim of zero failed first transmission attempts. Failed pre-fix runs are preserved separately.

## Parent CPU budget protection

The actual parent kernel limit was `cpu.max = 340000 100000`: 340% hosting ceiling on the 4-vCPU host. A bounded unprivileged synthetic load unit was placed directly beneath golden.slice to test that parent budget, with normal PHP application requests concurrently remaining in their account slice. This is a parent-budget component test, not a simulation of twenty real customer WordPress accounts. No native plans or physical safety budgets were changed.

| Repeat | Sample window seconds | Mean hosting CPU % | Parent throttled periods in window | Authenticated admin successes / probes | Concurrent application successes / attempts |
|---|---|---|---|---|---|
| 1 | 58.95 | 324.3 | 419 | 6 / 6 | 131 / 131 |
| 2 | 59.65 | 323.1 | 425 | 6 / 6 | 143 / 143 |

Admin probes were approximately ten seconds apart in the ceiling-focused test. The management-heavy diagnostic also preserved availability: 60/60 authenticated probes and 270/270 concurrent application requests succeeded, with the parent quota engaging hundreds of times, while average hosting CPU was lower because management itself consumed host CPU.

CPU means above are recomputed from the saved first/last sustained kernel samples, excluding SSH launch and drain. Original elapsed-time-denominator results and all samples are retained. Per-interval scheduling bursts are not startup escapes or proof of exceeding a sustained quota. A CPU ceiling is a maximum, not a guaranteed allocation or a dedicated physical core.

## Stateful PHP and cleanup

Cart regression: 29/29 journeys. Checkout regression: 22/22 checkouts; 22 corresponding database orders verified with status, positive amount, test email and line items. These are synthetic transactions on the test site.

PHP 8.1 and 8.2 cold/warm HTTP probes confirmed effective user identity and kernel placement inside each corresponding golden account slice. Probe files were removed. The old public CPU-stress endpoint was backed up outside the web root and removed. No load units remained. Webuzo, agent and Golden Shield were active; the parent had zero OOM kills and the active PHP proxy reported zero task-limit rejections after the fix.

## Scope, installation and artifacts

Activate through the normal Webuzo plugin workflow. Apache integration requires the native supported Apache layout; see apache-fcgi-integration.md for exact owned paths and reviewed check/rollback commands. Existing externally adopted isolation implementations must match this release or activation stops for a reviewed maintenance upgrade. Backups of the validation VPS's replaced code/configuration were retained in /root/webuzo-validation/codex-1.1.10.

This run did not reinstall the OS, reboot the VPS, or repeat the full plugin uninstall/reinstall matrix. Historical lifecycle evidence describes its own earlier build. No guarantee is made for unlimited traffic, arbitrary WordPress plugins/catalog sizes, all operating systems/web-server layouts, upstream network failure, or every VPS provider. These are bounded successful checks of the changed components, not unconditional production certification.

Evidence included beside this document: release-validation-1.1.10.json, release-cart-checkout-1.1.10.json, release-health-1.1.10.json. Workspace diagnostic and unit-test sources remain in vps-validation. Release ZIP checksums are published in the separate .sha256 files to avoid self-referential archive checksums.
