# Resman 1.1.31: measured server allocation and configuration validation

Date: 2026-10-25. Canonical generator: `M:\Codenew\FFFFFF\uniselv.win\webuzo-planner`. Runtime SHA-256: `2cd322cbf73ad12dfea3dbd8c394c1145237698ba8f6e22bccf4db8527647a24`.

## Outcome and meaning

The current configuration passes 331 saved-value comparisons, mechanical runtime checks, Golden Shield checks, 25-account placement checks and override recovery checks. The allocation changes below were deployed with rollback copies and checked on the current server. This establishes stronger evidence than matching a saved profile: controlled requests reached approximately 277.2% of the account's 280% CPU allowance, while physical/account budget checks remained active.

This is a measured, functioning policy for the tested hardware/workloads, not a mathematical proof that no future workload can benefit from retuning. More workers cannot manufacture CPU time. The configuration should be revisited when hardware, application cost or account activity materially changes.

## Problems fixed

| Before | Now | Verification |
|---|---|---|
| One cold request could reserve an entire worker allowance. | A verified relay starts with one fully charged worker; queued/forwarded demand grows the grant within account, host and shared PHP budgets. | Cold grant, native ceiling, private socket and budget regressions. |
| Warm idle pools could retain large worker reservations until warm TTL/eviction. | After the configured idle interval, no native children, verified root master/cgroup and a fitting actual memory charge allow compaction to one worker without restarting the master. | Controlled grant 8→1, reservation 2649→633 MiB; same master PID and OPcache start. This frees ledger reservations, not literal RAM allocations. |
| Any valid peer ticket could cause fair-share restart or idle eviction even if its next worker fitted. | Fair-share pressure uses the real unfunded next worker; each cold peer publishes its own full minimum footprint across PHP/relay versions. Unknown legacy minima stay conservative. | Funded peer retained the target OPcache in controlled live testing; different-relay and unknown-minimum regressions. |
| Zero-demand/post-response pools could enter master restart; relay completion could be mistaken for finished PHP work. | Zero-demand pools use idle reclamation; idle retirement also requires native backend-idle proof. | A seven-second job after FastCGI END_REQUEST completed while a cold peer queued; master/OPcache remained intact. |
| A new burst could wait for the periodic regrant tick. | Queue arrival triggers another locked allocation check without replaying or interrupting submitted requests. | Regression freezes the periodic clock until arrival-driven growth occurs; native bursts below. |
| Child FPM syntax checks inherited the supervisor's systemd readiness/watchdog endpoint and produced rejected notification messages. | Child environment omits those endpoints; the supervisor's own environment is unchanged. | Environment regression and current managed-service verification. |
| The 16-MiB interned-string pool filled completely. | The generator derives 4–32 MiB from one eighth of total OPcache; the current profile uses 32 MiB inside the unchanged 256-MiB total. | 16/32/16 comparison: 32 MiB stored about 26 MiB with spare space. CPU benefit was small/noisy. |

Global native PHP-FPM settings remain common across installed PHP versions. No manual per-user native settings were introduced. Automatic private runtime limits remain tied to account boundaries and actual shared demand. Shared Redis remains shared; overselling does not increase physical safety limits.

## Why the worker ceiling was not blindly doubled

The host exposes four logical CPUs and about 7.57 GiB kernel RAM. The target account is limited to 280% CPU and about 4.17 GiB RAM; those are different from whole-host capacity. Golden hosting services share a 340% aggregate CPU boundary with 60% headroom.

The current conservative worker allowance is 288 MiB, based on a 256-MiB script limit plus native allowance. Sixteen workers would require at least `16 × 288 + 48 + 256 + 41 = 4,953 MiB`, exceeding the shared 3,127-MiB PHP budget before considering peers. Assuming every worker always stays at 120 MiB is not a safety proof. The common native ceiling of eight can be reduced dynamically; it does not reserve eight live processes for every registered account.

Controlled native requests each consumed 200 ms of PHP CPU:

| Concurrent requests | Requests | Throughput | Account CPU |
|---:|---:|---:|---:|
| 1 | 16 | 4.90/s | 99.6% |
| 2 | 16 | 8.54/s | 175.1% |
| 4 | 16 | 13.38/s | 272.4% |
| 8 | 16 | 13.52/s | 277.2% |

The payload-only theoretical limit at 280% is about 14 requests/s. The eight-request test delivered 13.52/s, about 96.6% of that ideal before protocol/measurement overhead. Four-request concurrency already used 272.4% CPU. Eight retains room for I/O concurrency; increasing the worker count alone has no demonstrated large CPU throughput gain.

HTTP was intentionally paused, existing PHP/background jobs were drained, and only private owner-authorized FastCGI fixtures ran in this controlled test. Fixtures were removed and HTTP was restored. An earlier uncontrolled peer test encountered genuine competing pool reservations and an OPcache eviction; that failed assumption is retained in `live-runtime-regressions-uncontrolled.json`, not counted as a passing cache-preservation proof. True resource pressure may still require a drained restart or cache eviction.

## Standalone origin fixture results

All 420 fixture requests completed with zero failures and zero OOM kills. The existing dedicated test database's integrity invariant passed before and after; customer databases were not modified. These are short origin-component tests using local curl clients, not real-browser shoppers. Very short stage CPU percentages include measurement overhead and must not be used to size CPU.

| Workload | Concurrent requests | Requests | Throughput | P95 |
|---|---:|---:|---:|---:|
| db-read-high-16 | 16 | 32 | 84.51/s | 0.082 s |
| db-cached-40 | 40 | 80 | 107.47/s | 0.196 s |
| cpu-low-40 | 40 | 80 | 51.42/s | 0.727 s |
| cpu-high-40 | 40 | 80 | 3.33/s | 12.644 s |
| static-40 | 40 | 80 | 143.10/s | 0.049 s |

The heavy CPU fixture consumed roughly 0.8 CPU-seconds per request; about 3.3 requests/s is consistent with a 2.8-core allowance. Forty queued requests completing successfully does not mean forty continuously CPU-running workers or forty WooCommerce shoppers with a low latency guarantee.

## OPcache comparison

Three product URLs, three warmup requests plus six measured requests per stage; temporary signed instrumentation was removed. Values are request CPU from the same profiler, not whole-worker post-response CPU. Server-wide global values were restored between stages before adopting the measured 32-MiB working-set fit.

| Stage | Median request CPU | Median request wall | Interned buffer used/free |
|---|---:|---:|---:|
| interned16-a | 1222.8 ms | 1350.7 ms | 16.00 / 0.00 MiB |
| interned32-b | 1211.8 ms | 1332.6 ms | 25.71 / 6.29 MiB |
| interned16-c | 1270.7 ms | 1397.7 ms | 16.00 / 0.00 MiB |

The CPU delta is smaller than the variation between the two 16-MiB runs, so no large causal speedup is claimed. The confirmed capacity improvement is that repeated strings now fit. Total OPcache remains 256 MiB, so the shared reservation budget did not increase. The canonical generator and all installed PHP version global INI values now agree at 256/32 MiB. Eight hardware/overselling cases check buffer scaling and rejection behavior; undersized hardware profiles still report their resource-plan validation errors.

## Website verification without WordPress changes

Three product URLs were requested through Cloudflare with a unique diagnostic query and a bypass cookie. Every measured response had SuperRocket BYPASS and no Cloudflare HIT. Three warmup requests preceded the final 34-request run. No cart, checkout, payment or maximum-shopper claim is made.

| Policy run | 8-concurrent throughput | 8-concurrent P95 | Verified uncached failures |
|---|---:|---:|---:|
| A: original runtime, online baseline | 1.62/s | 8.08 s | 0 |
| B: early candidate, online | 1.74/s | 6.28 s | 0 |
| C: final runtime + 32-MiB strings, online | 1.68/s | 5.83 s | 0 |

These online runs have different cold/warm/background conditions and are not a randomized causal A/B experiment. They verify successful uncached serving; they do not establish a universal maximum or prove every response improvement was caused by Resman. Website CPU cost remains substantial. Server fixtures demonstrate that admission can use the CPU allowance; identifying/reducing WordPress/theme/plugin cost is the next, separate phase.

## Readiness, deployment and remaining scope

- 126 Linux root regressions passed in disposable mocked fixtures. This count is separate from the live lifecycle tests from earlier releases.
- 331 current saved-value checks matched; runtime mechanical, Golden Shield, 25-account placement and temporary override recovery checks passed. All checked service units were active; no pending lifecycle journal remained.
- Native PHP versions checked: 7.4, 8.1, 8.2 and 8.4. Actual website load used PHP 8.4. Other versions were not claimed to run the WooCommerce workload.
- Runtime copies and canonical embedded installer source have identical normalized SHA-256. Release metadata, Help runbook, changelog, exact source anchors, JSON exports and native ZIP checks are included. Generator readiness uses the exact dated profile; five hardware/workload/override changes correctly lose the current-profile verification claim, while object key order does not affect matching. The INI page and English exports now link the current 256/32-MiB evidence instead of reporting an obsolete pending rollout.
- Runtime upgrades retained rollback copies of runtime and ownership/restoration manifests. Native Webuzo monitoring can replace a systemd restart job; deployment now uses the existing checked coordinator restart workflow rather than treating a canceled job alone as success or failure.
- WordPress plugin/theme code and currency settings were not permanently changed. Default USD, Bangladesh geolocation to BDT and no loading mask are user-confirmed requirements; any checkout/currency concern needs a separate later reproduction.
- Shared Redis mode and CSF ownership remain unchanged. SSL, backup and unrelated hosting features are outside this resource-allocation task.
- Clean-OS installation, unknown future vendor releases, hardware resizing and unmeasured application/resource mixes are outside this validation. RSS is an admission estimate; cgroup limits remain the enforced boundary. No zero-OOM, never-retune or universal-optimum guarantee is asserted.

See `server-policy-validation.json` for machine-readable evidence and `source-changes-1.1.31.md` / `.json` for exact file paths, verified content anchors, generated replacement code, after-edit context, duplicate handling and verification steps. Use complete reviewed packages instead of appending individual functions to an existing installation.
