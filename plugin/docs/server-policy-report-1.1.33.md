# Resman 1.1.33 — current-host configuration selection and validation

Date: 2026-10-27. Runtime SHA-256: `dac8d288f8ec00c794dffb61f451ef4bfd61a35a10216d4c9623f5a35074beaf`.

**Resource-scope acceptance: PASSED after real reboot verification.**

The selected configuration is the best balanced retained choice among the candidates tested on this host and workload. The evidence supports current-host resource readiness and normal resource use. It does not establish unique optimality over every conceivable workload or a permanent never-retune guarantee. SSL, mail, backup and WordPress feature remediation were not added as unrelated acceptance gates.

## Two confirmed corrections

1. Native reload previously forced a complete routing/pool restart, even for unchanged account definitions. Reload now validates/reconciles changed definitions selectively and uses graceful native master reload for surviving pools. Public socket/proxy units and charged leases remain in place; PHP INI/extension reload still occurs. Explicit restart retains its restart semantics.
2. The native `process_control_timeout = 10s` escalation cut off a genuinely timed post-response job. Managed global copies now derive a minimum control grace from the inherited finite request timeout and preserve longer operator values. Malformed or duplicate controls fail closed. Mechanical verification checks every managed pool. Native panel defaults remain global; no manual per-user panel settings or new independent inputs were created.

The accepted native reload case recorded **823 foreground requests, zero failures**, preserved the public socket and proxy PID, and completed a **30.008-second** post-response job. A private harmless INI change was read back after reload; the actual global INI file stayed unchanged. Maximum queued request wait was **20.80 seconds** during reload, so this is not a zero-latency maintenance claim. An earlier sleep-only fixture returned early on a signal; rejected tests were replaced with an elapsed-time-checked loop.

Native signal reference: [PHP 8.4 FPM manual source](https://github.com/php/php-src/blob/PHP-8.4/sapi/fpm/php-fpm.8.in). Global control directive reference: [PHP FPM configuration](https://www.php.net/manual/en/install.fpm.configuration.php).

## Selected values

| Setting | Retained value |
|---|---:|
| Native global worker ceiling | 8 |
| Native backlog | 64 |
| Maximum warm idle lifetime | 600 s |
| Apache MaxRequestWorkers | 20 |
| InnoDB buffer pool | 1024 MiB |
| OPcache / interned strings | 256 / 32 MiB |

The account CPU ceiling remains 280%; aggregate hosting CPU remains 340% on four visible logical CPUs. Physical/account memory, swap and task boundaries are retained. Warm pools receive demand-driven grants; eight is a ceiling, not eight reserved workers for every registered account. Global Inputs, packaged source and canonical `uniselv.win/` embedded runtime remain consistent.

## Repeated worker comparisons

Three balanced repeats per candidate, same payload and client topology. CPU payloads consume about 200 ms of measured PHP CPU; waiting payloads intentionally spend time off-CPU.

| Ceiling | Workload | Median requests/s | Median P95 seconds |
|---:|---|---:|---:|
| 2 | cpu | 9.70 | 2.473 |
| 2 | io | 12.13 | 1.985 |
| 2 | mixed | 11.01 | 2.177 |
| 4 | cpu | 13.46 | 1.813 |
| 4 | io | 23.97 | 1.010 |
| 4 | mixed | 20.31 | 1.208 |
| 6 | cpu | 13.41 | 1.992 |
| 6 | io | 35.36 | 0.680 |
| 6 | mixed | 24.83 | 0.990 |
| 8 | cpu | 12.09 | 2.254 |
| 8 | io | 44.93 | 0.547 |
| 8 | mixed | 24.85 | 1.045 |

Four or six workers are competitive for CPU-bound payloads; eight retains greater wait-heavy throughput and essentially the same mixed-workload throughput as six. Real BDT-cookie HTML comparisons did not establish a material throughput gain from lowering the ceiling to four. These are tradeoffs, not a claim that eight wins every metric. Controlled CPU payloads used roughly 97% of the measured hosting-account CPU time; this excludes root/system/shared-service CPU and is not a WordPress optimization percentage.

## Apache and SQL confirmation

Apache 12/20/24 workers and SQL 512/768/1024-MiB buffer pools each received three balanced repeats. Retaining Apache 20 avoids the lower PHP/static results at 12; 24 did not establish a material overall improvement. The initial small SQL samples favored 512 MiB in some cases, so a larger SQL-only confirmation followed, with preload-only locks held and 48 measured BDT-cookie product requests per trial. Other WordPress behavior remained unchanged.

| SQL buffer | Median requests/s | Median P95 seconds | Median account CPU ms/request |
|---:|---:|---:|---:|
| 1024 MiB | 1.428 | 3.969 | 1817.6 |
| 512 MiB | 1.454 | 3.300 | 1811.6 |

The larger confirmation left only a **1.8%** median throughput difference, with the winner reversing and tail-latency outliers occurring with both sizes. This did not meet the predeclared consistent material improvement criterion. The balanced 1-GiB shared cache is retained. No larger-future-database optimum is implied. SQL runtime values and preload locks were restored.

## Sustained load, sharing and recovery

All 67 controlled fixture stages passed: worker and queue screening, 4–64-client bursts, natural warm retention, two five-minute sustained stages, simultaneous accounts and recovery. Queue candidates were 16/32/64. Real offered-arrival tests included 6/12/18 requests/s, two balanced orders; latency starts at intended arrival time, including executor lag. The 18-RPS input exceeded sustainable CPU-payload throughput and accumulated waiting work; eventual zero-error completion is not a sustainable 18-RPS rating.

A separate **601.1-second** saturation test completed **7183 requests**, zero failures and zero OOM kills. Average account CPU was 261.5%; peak account memory was 1625.6 MiB and minimum host available memory 4609 MiB. Apache remained online, so normal host/customer background work was not presented as an idle dedicated CPU reservation. A subsequent low-cost recovery stage passed. The native 20-second post-response/rebalance case also passed with a real elapsed-time guard; deferred drains retained reservations and did not restart every six seconds.

## Public cold start and rejected readiness attempts

Six first public requests after proven natural proxy/backend retirement succeeded with HTTP 200, actual product variation forms, SuperRocket BYPASS and Cloudflare DYNAMIC. No private FastCGI request prewarmed PHP before those measurements; only static HTTP service readiness was checked. The accelerated idle lifetime exercised the same normal retirement/startup path without force-stopping unfinished background work. Cold page durations were approximately 6.4–8.2 seconds; this is not the warm response-time claim.

The long matrix ended after a public warmup assertion following a deliberate service transition. All 67 fixture stages passed, but its entire website comparison was not accepted. Its first 18-request website stage is excluded from paired ranking. Six separate fully logged paired trials completed 108 measured requests with zero failures. The original failed warmup lacked enough recorded transport detail to assign an exact cause; it was not silently relabeled as a successful test or a proven configuration defect.

## Verification and release scope

184 isolated Linux tests passed against shipping source. The final configured-value audit reports 331 checks with zero mismatches; runtime placement, Golden Shield and managed reload-grace checks passed. Eight hardware/overselling generator cases verify physical safety-budget behavior, including explicit rejection where the proposed small profile cannot meet native plan minima. Rejected profiles are not claimed as successful deployments.

The accepted recorded trial total is **24363 requests, zero recorded failures and zero fixture OOM kills**. This count includes measured stage records, not every warmup/diagnostic call and not rejected baselines. All temporary files/views were removed, SQL settings restored and public uncached postchecks passed.

Actual reboot verification passed without manually starting services; see the boot-ID and automatic-service record in the JSON ledger.

This accepts the current-host Resman/resource configuration scope. Clean-OS installation, unknown future vendor releases or different hardware/data/workload require separate evidence. Shared SQL/Redis retain their disclosed shared trust model. No checkout, orders, payments, SMS, tracking submissions or WordPress feature fixes were used as test actions. The website still spends substantial CPU building dynamic pages; a higher shopper count requires its own feature-preserving application work and matched capacity test.

Exact replacements and verified anchors: `source-changes-1.1.33.md/.json`. Private raw evidence remains outside the distributed module; summaries and source hashes are supplied with the release.
