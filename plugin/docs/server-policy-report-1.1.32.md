# Resman 1.1.32: repeated configuration and allocation comparisons

## What was actually established

The six requested comparison categories were exercised on the current host: fixed workloads, controlled setting changes, saturation/arrival ramps, multiple accounts, sustained load/recovery, and repeated balanced trials. The outcome is a measured default among tested candidates for this hardware and workload, not a proof over every possible workload or future software version.

No WordPress source, theme, currency or third-party plugin code was modified. Native per-version PHP-FPM settings remain global. Temporary private runtime/service views were removed and database runtime settings restored. Physical safety limits and shared Redis mode are unchanged.

## Defect found and corrected

The previous runtime cleared a granted peer's waiting ticket. Another proxy could mistake that still-busy peer for inactivity, grow greedily, and then shrink/restart again when demand reappeared. A lightly used third account reproduced the cycle. The failed initial online run also exceeded the 15-second website latency gate; it was stopped and restored, not counted as a successful test.

Root-owned short-lived busy-demand records now survive waiting-ticket clearance. Deterministic water-filling charges every idle reservation in full, gives genuinely demanded capacity to active accounts and retains unfunded tickets so safe idle reclamation can occur. A sole native child can be compacted only after listener-idleness, cgroup/master identity and charged-memory checks. In-flight/background jobs are never considered safely drained merely because a FastCGI response ended.

Two earlier balanced old/new 45-second trials reproduced **41 old-runtime fair-share restarts**. Two fresh final-code 45-second trials required 2 initial fair-share adjustments; initial growth is included. A further startup-boundary defect was found in the intermediate candidate during sustained load, corrected by preserving/refreshing demand through backend release and counting valid unleased demand. Intermediate candidates are excluded from final-code rankings. Repeats are bounded rather than a statistical confidence interval.

| Trial | Requests/s | P95 seconds | Account CPU % | Fair restarts |
|---|---:|---:|---:|---:|
| ab-r1-old31-target | 14.31 | 1.294 | 163.0 | 6 |
| ab-r1-old31-peer | 8.47 | 1.115 | 99.0 | 6 |
| ab-r2-old31-peer | 3.18 | 3.597 | 53.1 | 14 |
| ab-r2-old31-target | 6.82 | 2.463 | 92.9 | 15 |
| ab-r1-new32-target | 14.44 | 0.764 | 156.3 | 0 |
| ab-r1-new32-peer | 12.55 | 0.435 | 136.7 | 1 |
| ab-r2-new32-target | 14.23 | 0.736 | 155.4 | 1 |
| ab-r2-new32-peer | 13.08 | 0.409 | 141.0 | 0 |

## Repeated worker screening

Three balanced repeats per candidate. Payload CPU time is measured inside PHP; wait-heavy requests intentionally free the CPU while waiting.

| Worker ceiling | Workload | Median requests/s | Median P95 seconds | Median account CPU % |
|---:|---|---:|---:|---:|
| 2 | cpu | 9.68 | 2.473 | 199.4 |
| 2 | io | 12.24 | 1.965 | 18.9 |
| 2 | mixed | 11.05 | 2.172 | 118.8 |
| 4 | cpu | 13.39 | 1.830 | 277.2 |
| 4 | io | 24.17 | 0.994 | 35.9 |
| 4 | mixed | 20.28 | 1.209 | 217.6 |
| 6 | cpu | 13.01 | 2.005 | 270.7 |
| 6 | io | 35.45 | 0.675 | 51.2 |
| 6 | mixed | 23.06 | 1.083 | 247.1 |
| 8 | cpu | 13.54 | 2.093 | 279.5 |
| 8 | io | 46.34 | 0.508 | 65.3 |
| 8 | mixed | 25.13 | 1.001 | 268.7 |

Eight is retained as the common native ceiling, not a permanent eight-worker reservation per account. CPU-bound payloads plateau near the 280% CPU allowance; waiting workloads benefit from more concurrent workers. Sixteen workers at the conservative 288-MiB allowance exceed the shared PHP budget. Lower ceilings would sacrifice waiting-workload concurrency without creating more CPU time.

## Real uncached product requests

Three existing product URLs, HTML GET only, same origin-to-edge path, six concurrent clients, eighteen measured requests plus three warmups per trial, balanced ceiling order 8/4/4/8/8/4. Every measured response must be HTTP 200, SuperRocket BYPASS and not Cloudflare HIT. No cart, checkout, full browser rendering or maximum-shopper certification is implied.

| Trial | Ceiling | Requests/s | P95 seconds | Failures |
|---:|---:|---:|---:|---:|
| 1 | 8 | 1.776 | 4.335 | 0 |
| 2 | 4 | 1.583 | 5.492 | 0 |
| 3 | 4 | 1.865 | 4.046 | 0 |
| 4 | 8 | 1.807 | 4.188 | 0 |
| 5 | 8 | 1.761 | 3.912 | 0 |
| 6 | 4 | 1.865 | 3.980 | 0 |

## Apache and database candidates

Apache 12/20/24 workers and database 512/768/1024-MiB buffer pools were compared three times in balanced order. Apache changes existed only in a private service mount; database resize was runtime-only. Service budget figures are planning allowances, not individual Apache/MariaDB MemoryMax promises: those services remain constrained by their aggregate parent. The observed database working set is smaller than every tested buffer candidate, so this test cannot establish which is best for a much larger future database. Retain 20 Apache workers and 1024 MiB DB buffer as the existing balanced defaults unless repeated measurements show a material benefit worth the memory tradeoff.

| Trial | Requests/s | P95 seconds | Failures |
|---|---:|---:|---:|
| apache-r1-workers20-static | 839.107 | 0.038 | 0 |
| apache-r1-workers20-php | 3.149 | 10.104 | 0 |
| apache-r1-workers12-static | 783.278 | 0.041 | 0 |
| apache-r1-workers12-php | 3.342 | 9.446 | 0 |
| apache-r1-workers24-static | 888.589 | 0.037 | 0 |
| apache-r1-workers24-php | 3.404 | 9.134 | 0 |
| apache-r2-workers24-static | 982.226 | 0.029 | 0 |
| apache-r2-workers24-php | 2.575 | 12.135 | 0 |
| apache-r2-workers20-static | 1149.044 | 0.029 | 0 |
| apache-r2-workers20-php | 3.330 | 9.405 | 0 |
| apache-r2-workers12-static | 870.785 | 0.035 | 0 |
| apache-r2-workers12-php | 3.250 | 9.801 | 0 |
| apache-r3-workers12-static | 865.205 | 0.038 | 0 |
| apache-r3-workers12-php | 3.335 | 9.564 | 0 |
| apache-r3-workers24-static | 840.366 | 0.040 | 0 |
| apache-r3-workers24-php | 3.382 | 9.421 | 0 |
| apache-r3-workers20-static | 409.482 | 0.086 | 0 |
| apache-r3-workers20-php | 2.683 | 11.749 | 0 |
| database-r1-pool1024-read | 281.180 | 0.064 | 0 |
| database-r1-pool1024-wordpress | 1.839 | 2.380 | 0 |
| database-r1-pool512-read | 400.417 | 0.043 | 0 |
| database-r1-pool512-wordpress | 1.882 | 2.337 | 0 |
| database-r1-pool768-read | 368.585 | 0.047 | 0 |
| database-r1-pool768-wordpress | 1.802 | 2.547 | 0 |
| database-r2-pool768-read | 242.704 | 0.082 | 0 |
| database-r2-pool768-wordpress | 0.871 | 7.748 | 0 |
| database-r2-pool1024-read | 1.932 | 12.713 | 0 |
| database-r2-pool1024-wordpress | 1.910 | 2.285 | 0 |
| database-r2-pool512-read | 381.731 | 0.044 | 0 |
| database-r2-pool512-wordpress | 0.919 | 8.551 | 0 |
| database-r3-pool512-read | 348.964 | 0.057 | 0 |
| database-r3-pool512-wordpress | 0.774 | 12.180 | 0 |
| database-r3-pool768-read | 283.916 | 0.064 | 0 |
| database-r3-pool768-wordpress | 1.775 | 2.376 | 0 |
| database-r3-pool1024-read | 296.581 | 0.066 | 0 |
| database-r3-pool1024-wordpress | 1.812 | 2.462 | 0 |

## Offered arrivals, sustained sharing and recovery

Fixed offered arrivals start latency at the intended schedule, including executor delay; this avoids reporting only closed-loop client capacity. Twenty seconds at each 6/12/18-RPS input, two balanced repeats. Overload may complete later instead of failing; that is not sustainable capacity. Five minutes of concurrent account load plus sixty seconds of recovery are recorded in the machine-readable stage ledger.

| Repeat | Offered RPS | Completion RPS | P95 scheduled seconds | Maximum pending tasks | Failures |
|---:|---:|---:|---:|---:|---:|
| 1 | 6 | 5.99 | 0.220 | 2 | 0 |
| 1 | 12 | 11.93 | 0.215 | 3 | 0 |
| 1 | 18 | 13.05 | 7.464 | 104 | 0 |
| 2 | 18 | 13.48 | 6.556 | 96 | 0 |
| 2 | 12 | 11.93 | 0.770 | 11 | 0 |
| 2 | 6 | 5.99 | 0.214 | 2 | 0 |

## Final correction discovered during service screening

The screening journal exposed repeated 6-second deferred drains while native post-response work prevented idle proof. New arrivals reset the scheduling timestamp and erased the intended retry delay. This is a Resman queue-control defect, not evidence that changing the SQL buffer caused the recorded 7–12-second outliers. Those pre-fix service timings are retained and are unsuitable for claiming a unique optimal SQL buffer size.

The final runtime `ee49bbb6e3b9219a9476ddcc3f10e662f6f2e47900dfc49350809e1dfd138e01` separates immediate growth scheduling from deferred shrink cooldown. Configuration-comparison runtime: `486f372f45a698c250f1e37ca26e3b014918a27fd7176d8a8a14a40b7e6aef5f`. Numeric settings are unchanged. Comparisons were not silently relabeled as final-code runs: the delta was checked with 135 Linux regressions, a native 20-second post-response job under continuous arrivals and temporary peer demand, 420 standalone origin requests and 34 fresh uncached product requests.

The native job completed. Drain attempts were separated by 21.21 seconds, rather than restarting every six seconds. Foreground requests continued during the cooldown; full charged reservations were retained. The final origin fixture series had zero failures/OOM and the dedicated SQL-data invariant passed before and after. Exact final website stages are in the JSON ledger. Warmup/readiness failures from earlier maintenance transitions are recorded separately, not folded into successful steady-state trials.

## Restoration and remaining scope

Final 331-value, mechanical runtime, Golden Shield, account placement and override-recovery checks passed. Agent/Apache/coordinators are active. Temporary scripts, service views and database settings were restored; source hashes match the release. Unit suite: 135 Linux tests. Exact JSON profiles and raw stage evidence remain with the dated audit.

Earlier warm TTL 30/120/600, queue 16/32/64, 4–64-client burst ramp and post-response-job tests are dated evidence; fresh-OS installation and unknown future vendor behavior are not simulated by matching a saved profile. A previously discarded contaminated warm-lease trial and the interrupted two-account-only rehearsal are excluded from rankings. A prior CPU outlier coincided with host activity outside the hosting slice; no specific culprit was proven, so it is not attributed to WordPress or any named service. Native regeneration interrupted a later old-runtime rehearsal; its HTTP failures are retained as invalidated comparison evidence, not used as throughput rankings.

Changes in application CPU cost, RSS, data size, account activity or hardware may justify retuning. Website CPU profiling remains the next separate task.
