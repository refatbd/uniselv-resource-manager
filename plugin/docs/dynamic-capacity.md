# Dynamic PHP capacity — 1.1.20

Demand-pressure sharing now yields genuinely idle reservations to eligible waiting peers without preempting active/queued requests. See [demand-sharing.md](demand-sharing.md); full physical and account boundaries remain authoritative.

New cold admissions subtract only verified clean inactive file cache from raw account memory when estimating the current working set. Active file cache, anonymous/kernel memory and dirty/writeback pages remain charged. Existing account/host lease reservations still count in full; native and aggregate hard limits and physical safety budgets are unchanged. Missing or invalid counters retain raw-current accounting. See [cache-aware-admission.md](cache-aware-admission.md) for scope, edit placement, source references and bounded test evidence.

The earlier matched deployment below remains historical evidence for its stated settings and workload. New public uncached capacity is recorded separately; earlier warm/cold cloud failures are retained.

## Matched 1.1.18 settings baseline

Current matched-profile deployment and evidence: [matched-capacity.md](matched-capacity.md) and [matched-capacity-validation.json](matched-capacity-validation.json). OPcache 256 MiB, SQL account connections 34, global FPM 8/64, measured RAM and source/profile drift checks supersede the earlier sizing example below. Other hardware is derived and requires validation.

## Historical 1.1.17 baseline — not the current deployed values


This release keeps native Webuzo PHP-FPM defaults global and adds an explicitly enabled automatic exception in **private managed runtime copies**. It does not create native per-user PHP-FPM overrides.

## Sharing behavior

The global ceiling derives from shared hardware inputs. Each managed pool ceiling is reduced to fit the account's effective Memory High, 90% of Memory Max, and Tasks Max. At cold start, the governor grants as many estimated workers as fit the remaining physical PHP budget and host reserve. It also checks combined leases and current memory for the same UID across PHP versions. Registered account count is not an input to allocation.

An inactive account has no PHP capacity lease. Ondemand workers exit when idle; the idle proxy then stops its private backend and releases its lease. Continuously busy pools retain their conservative grant until idle. This avoids reloading or killing live requests to reclaim a grant. It is not instantaneous fair redistribution, a guaranteed minimum per tenant, or a measured visitor capacity. Account and aggregate kernel CPU/RAM boundaries remain in effect.

The proxy uses fixed relay threads and a bounded socket queue. Queueing plus execution share a finite request budget: native timeout minus 5% delivery allowance. It never automatically replays a request after forwarding bytes. Real exhaustion or a deadline can still produce HTTP 503, now with a self-contained white/coral animated page, Retry-After and no-store headers. Motion respects reduced-motion preferences.

When the actual aggregate CPU cgroup already preserves at least 15% host CPU headroom, high load is reported without halving every account's CPU quota. Existing breaker quotas use the durable restoration journal. Without the valid aggregate guard, the legacy breaker remains available.

## Inspected panel workflow

Observed on Webuzo 4.8.4 / Ubuntu 24.04, 2026-10-20. These are observed server values, not vendor factory defaults.

**Webuzo Admin Panel > Apps > PHP FPM Settings**: leave **Username :-** at **Select User**, verify **Global PHP FPM Settings**, select the installed **PHP Version :-**. Existing PHP 8.4 values were Ondemand, Max Children 2, Max Spare Servers 2, Max Request 500, idle timeout 10 seconds, request timeout 120 seconds, File Limit 131072 and blank Listen Backlog. Run PHP-FPM as nobody was unchecked.

For the reviewed 4-vCPU/8-GB profile, generated Max Children is 8 and Listen Backlog is 64; Max Spare Servers follows 8 but is unused in Ondemand. Click **Submit**, wait for **Done / Settings saved successfully**, then **Ok**. Repeat for each installed version. Confirm native inheritance and managed runtime caps after reconciliation. Install and verify the updated account-aware governor before raising the native ceiling on an existing server. Keep traffic in maintenance during initial installation of an unprotected server.

**Webuzo Admin Panel > Apps > MySQL Configuration > Editor Mode**: heading **MariaDB 11.4 Configuration**; editor `mysql_data`, button **Save Raw Configuration**. The inspected configuration is `/etc/my.cnf`. The tested change replaces exactly one existing directive in `[mysqld]`. Preserve all other content and section headings.

Replacement location: AFTER the existing `slow_query_log=1` line and BEFORE the existing `max_statement_time=30` line. Replace `max_user_connections=6`; do not append a duplicate.

Copyable replacement code for this tested profile:

```ini
max_user_connections=18
```

Illustrative AFTER-edit context; do not paste this excerpt as an additional block:

```ini
[mysqld]

slow_query_log=1
max_user_connections=18
max_statement_time=30
```

Save with **Save Raw Configuration**, wait for **MySQL Configuration saved successfully**, and verify `SELECT @@GLOBAL.max_user_connections` equals the saved value. The planner derives this allowance from its shared PHP worker/version model; 18 is the reviewed profile value, not a universal plugin constant. This save retained the existing database buffer pool and total connection ceiling; no unmeasured RAM increase was applied.

## Program and policy placement

The release supplies complete program files. Do not paste individual Python methods into Webuzo fields or PHP configuration. For initial installation, the package creates each complete file. For reviewed maintenance, back up the existing whole file, replace from the beginning through the end of file, and preserve its executable permissions. Never append a second program. Existing adopted source mismatches remain blocked by the normal installer until reviewed; this release does not silently overwrite arbitrary adopted code.

| Complete replacement path | Package source | Placement |
|---|---|---|
| `/usr/local/sbin/webuzo-isolation.py` | `core/webuzo-isolation.py` | AFTER beginning of file, BEFORE end of file; replace entire content |
| `/usr/local/uniselv-resman/core/webuzo-isolation.py` | `core/webuzo-isolation.py` | Same complete program, no duplicate copy inside the file |
| `/usr/local/uniselv-resman/core/protection-lifecycle.py` | `core/protection-lifecycle.py` | Whole-file replacement |
| `/usr/local/uniselv-resman/agent/collector.py` | `agent/collector.py` | Whole-file replacement |
| `/usr/local/uniselv-resman/agent/ipc_server.py` | `agent/ipc_server.py` | Whole-file replacement |
| `/usr/local/webuzo/plugins/uniselv-resman/core/…` | Corresponding `core/…` | Keep bundle mirror identical |
| `/usr/local/webuzo/plugins/uniselv-resman/agent/…` | Corresponding `agent/…` | Keep bundle mirror identical |
| `/usr/local/webuzo/plugins/uniselv-resman/uniselv-resman.php` | `uniselv-resman.php` | Whole-file replacement |

The beginning/end context is the complete matching packaged file, from its first line through its final line. Check its SHA256 against the release; a partial excerpt is not a valid replacement. Runtime unit files and `/etc/webuzo-isolation/phpXX/ACCOUNT.conf` are generated by the coordinator; do not paste or manually maintain account settings there.

Policy path: `/etc/webuzo-isolation/policy.json`. Preserve the reviewed physical budgets and existing fields, setting `accountRuntimeCaps` to boolean `true`. For a full exported policy update, replace the complete JSON object from beginning to end, never append another object. Exact budget values come from the same Global Inputs or measured host policy. `maxActivePools` is retained for legacy compatibility; account-aware admission is governed by memory grants, not a fixed registered-user or fixed-full-pool count. `poolBudgetMiB` describes the full ceiling estimate, not preallocated RAM per registered user.

After saving reviewed program updates: compile Python, lint PHP, restart/reconcile the managed coordinators, restart `uniselv-resman-agent.service`, and run:

```sh
sudo python3 /usr/local/sbin/webuzo-isolation.py verify
```

Require `mechanicalChecksPass: true`, correct account cgroups, active sockets and health bridges. In **UNISELV Resources > Configured vs Effective Audit > Automatic PHP Runtime Capacity**, inspect native ceilings, managed caps, lease states and reserved MiB. The same data is available in the admin audit response. Verify website HTTP behavior separately. An inactive saved managed cap is a ceiling, not a live memory reservation.

## Evidence and limits

See `dynamic-capacity-audit.json`. Temporary comparisons identified queue rejection, a SQL connection bottleneck and quota feedback. Temporary runtime overrides were removed before saving permanent settings. The final installed-settings test uses read-only public product GETs without configuration changes. Every tested request passed through Cloudflare as DYNAMIC, so this measures the origin path.

Python protocol, fragmentation, queue, unavailable-backend, cap, shared-memory, cross-version accounting and circuit-breaker tests are separate from a real CMS burst. Planner tests cover hardware scaling and overselling independence. Neither constitutes a fresh-install/reboot/vendor-update certificate or sustained multi-tenant workload capacity. Shared SQL/Apache attribution, sustained mixed tenants and new lifecycle validation remain open. Host swap stays disabled; no new swap-boundary claim is made.

## Final installed-settings result

With the normal 280% account CPU quota and the unchanged 340% aggregate hosting cap, 16/16 product requests succeeded in 26.134 seconds and 32/32 succeeded in 38.907 seconds. No HTTP 503, database error or OOM kill occurred. Peak account memory was 1481.8 MiB; minimum host MemAvailable was 5230 MiB. The native PHP configuration hash remained unchanged during this final test. This is a bounded origin-path burst, not a maximum sustained visitor count.
