# Resource Manager 1.1.29 — stability results

The current-host bounded core tests passed after correcting a real queue stall. This is not a universal production or zero-downtime certificate. WordPress was not modified.

## Issue found and fixed

1.1.28 could pause foreground dispatch while waiting for backend-idle proof during fair-share rebalancing. A longer saturation run produced 16 client timeouts despite free host RAM. The stalled drain observed in the retained diagnostic evidence lasted about 46 seconds.

1.1.29 gives a drain attempt a native-timeout-derived budget: 6 seconds for the measured 114-second proxy timeout. If idle proof is still unavailable, it retains the full charged grant/backend and resumes the queue with the existing cooldown. No background task is force-killed, no unproven memory is released, original client deadlines do not reset and submitted work is not replayed. CPU/RAM/native FPM values were not increased.

## New-code tests

| Scenario | Requests | Failures | Median | p95 |
|---|---:|---:|---:|---:|
| sustained-cpu-quota | 2979 | 0 | 2.311 s | 3.971 s |
| three-account-contention | 441 | 0 | 0.319 s | 1.044 s |

The saturation phase lasted **600 seconds**, with 16 actors, a measured 500-ms CPU target, 32-MiB allocation and 0.5–1 second think times. Mean sampled account CPU was 261.9%; short sampled peak 283.6%. This is a synthetic PHP workload, not 16 full WooCommerce shoppers.

Controlled post-response background work lasted 20 seconds. Foreground completed in 6.058 seconds while background work was still running; the cold peer completed in 24.810 seconds. The background job finished naturally. The live drain-deferred event occurred after approximately 6.323 seconds against its 6-second budget; scheduler/poll overhead is reported explicitly.

Maximum sampled PHP reservation was 3108 MiB against 3127 MiB. Minimum available host RAM was 5584.9 MiB against the 1280-MiB reserve. No new hosting OOM kill was observed. Temporary probe files were removed.

## Enforcement and lifecycle

- Linux: 141 isolated regressions passed. Python/PHP/JavaScript syntax: 13/10/64 files. Eight generated hardware/overselling cases passed; embedded runtime source/checksum matches the release.
- Three-account sharing and intentional client-disconnect recovery passed on the new code. PHP81/82/84 competition and disposable worker/proxy SIGKILL/restart recovery also passed in the separately dated pre-correction suite.
- Direct disk tests in an unchanged native account measured write/read IOPS near 1761/2641 against 1764/2647 limits; repeated 1-GiB sequential direct write/read measured 132.31/221.90 MB/s against 132/220 MB/s limits. A 64-MiB physical file was reused and removed. Small finite-window variation is not an enlarged configured limit.
- Final-code reboot confirmed a new boot ID and preserved protected files/accounts. All core units active, all 25 account placements PASS, boost recovery PASS, no pending lifecycle recovery. Final generated/runtime audit: 331 checks, zero mismatches.
- Prior native PHP install/remove, provisioning/plan/boost, memory/task/quota, cron/PAM, vhost/suspension and shared-service tests remain dated evidence, not newly claimed exhaustive repetitions.

## Real website check after reboot

| Uncached browsing actors | Requests | Failures | Median | p95 |
|---|---:|---:|---:|---:|
| 10-shoppers | 59 | 0 | 2.953 s | 9.271 s |
| 15-shoppers | 63 | 0 | 8.987 s | 15.943 s |

All origin requests including warm-up succeeded and reported cache BYPASS. Higher load stages stopped when p95 exceeded the 15-second test target. Product/home GETs with 5–10 second think times do not cover browser assets, carts, checkout or payment. Website latency remains a separate application investigation.

## Retained failures and maintenance behavior

- First provisioning probe and two cross-version requests ran while asynchronous native PHP rebuild was still stopping/restarting coordinators. Those failed runs remain archived; steady tests were repeated after a 45-second stable-manager/no-jobs barrier.
- A native disposable deletion left empty FTP JSON metadata after passwd/home/native-list removal. Exact empty fixture-only residue was verified before removal. Original 25 account directories were restored.
- Initial post-reboot check observed PHP84 activating and configuration audit unavailable during boot. The settled post-reboot snapshot separately passed all 331 checks.
- The failed 1.1.28 long-load result is retained; it is not relabelled successful.

## Separate or unavailable scope

- Native provisioning, PHP restarts and host reboot can interrupt connections; zero-downtime maintenance is not certified.
- No disposable VPS is available: current-release clean-OS install, full protection uninstall/reinstall and disaster restore are not executed. Owner requested current-host tests only.
- No native vendor PHP patch update was available. Future software layouts/releases and actual physical hardware resize are separate tests.
- Host swap stays off. MemorySwapMax=0 is not an active RAM-plus-swap workload certificate.
- CSF/lfd remains owner-managed. Mail/TLS renewal, Redis tenancy, backup restore, scanners, alert delivery, filesystem jails and per-account SQL CPU/RAM isolation are separate service/architecture scope.
- Optimal native worker-cap alternatives on the real WordPress application were not benchmarked in this pass; global ceiling remains 8 with dynamic account/shared grants. No manual per-user FPM setting was introduced.
- WordPress profiling/fixes, real browser assets, carts, checkout/payment and a maximum shopper certificate remain separate. Finite synthetic success does not establish universal uptime or leak freedom.

## Source and deployment

Exact already-applied module replacements and BEFORE/AFTER anchors: source-changes-1.1.29.md/.json. The canonical generator contains the same runtime in free-shield-assets.json with its matching SHA256. Generator replacements are described in generator-source-changes-1.1.29.md/.json. Replace complete reviewed files; never append duplicate definitions or directives. Keep ownership/restoration manifests and source backups together.
