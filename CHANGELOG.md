# UNISELV Resource Manager — Changelog

All notable changes to the UNISELV Resource Manager for Webuzo are documented in this file.

---

## [1.1.16] - 2026-10-20

- Fix Webuzo panel deactivation lifecycle by dispatching root deactivation directly via Webuzo's privileged `root_bg_exec()`, avoiding unprivileged panel worker execution during PHP tracker restoration.
- Guard `deactivate.php` and `uninstall.php` with root CLI preflight checks to reject unprivileged execution.
- Fix directory traversal permissions on `/usr/local/uniselv-resman` and `/core` to ensure `fpm_worker_tracker.php` is accessible across tenant PHP processes.

## [1.1.15] - 2026-10-20

- Fix Webuzo panel activation lifecycle by dispatching root installation directly via Webuzo's privileged `root_bg_exec()`, avoiding inactive-plugin CLI hook dependency.
- Guard `install.php` with a root CLI preflight check to reject unprivileged panel worker execution before file deployment.
- Add missing `listen.backlog` fallback in PHP-FPM pool parser for pools omitting explicit directive (defaults to Linux standard 511).
- Normalize bundled and deployment scripts with strict LF line endings.

## [1.1.14] - 2026-10-18

- Use the native theme-colored chart icon and a shorter Admin menu label, "UNISELV Resources", to keep sidebar navigation compact. Preserve the full product name in the link tooltip and plugin metadata.

## [1.1.13] - 2026-10-18

- Reduce read-only dashboard polling to ten seconds, coordinate matching authenticated tabs, cache fresh samples for five seconds, and apply bounded timeout/backoff.
- Preserve mutation authorization and uncached writes; display source freshness and reuse stable asset cache keys.
- Document native Webuzo comparison, 29 regression checks and bounded live CPU observations.

## [1.1.12] - 2026-10-18

- Harden installer, deactivation and uninstall with checked deployment, ownership journals, retained recovery assets and verified panel reload.
- Bootstrap bundled protection dependencies, preserve adopted integrations, fix state-aware native/Golden routing and deleted-account reconciliation.
- Serialize policy and managed-file transactions; enforce physical Manual limits and bounded, truthful rollback behavior.
- Restrict reseller scope and report/audit partial plan synchronization errors.
- Validate existing-host lifecycle, new accounts/plans, agent failure, cron, regeneration, reboot and bounded aggregate saturation. See `plugin/docs/LIFECYCLE-REVIEW-1.1.12.md` for measured results and excluded fresh OS/physical-resize scope.

## [1.1.11] - 2026-10-18

- Fix real-record history failure, aggregate RAM/storage contracts, retention saving and actual agent memory reporting.
- Replace fixed plan choices and fabricated hardware/coverage values with native settings and observed state.
- Harden package/audit rendering, branding validation and missing-session CSRF behavior.
- Add measured sparklines, stale-data visibility, keyboard dialog behavior and compact mobile navigation.
- Stop resurrecting deleted demo billing mappings. Preserve existing operator configuration.
- See `plugin/docs/PREPUBLICATION-REVIEW-1.1.11.md` for evidence, test scope and remaining environment notes.

## [1.1.10] - 2026-10-18

- Installer returns failure when every PHP configuration mutation fails; final manifest failures also block continuation or enter rollback.
- Packages an owned Apache FastCGI retry integration with syntax/include verification, graceful reload, checked removal and rollback. Existing unowned configuration is never overwritten.
- Removes dependency on the validation VPS's old per-domain retry override. Global integration applies to native Apache FastCGI workers, including subsequently created vhosts.
- Validation now fails closed on unsuccessful pre-stage dynamic recovery and preserves failed-operation details. Release evidence is in docs/RELEASE-VALIDATION-1.1.10.md.
- Fixes FastCGI admission proxy task exhaustion: warm requests do not spawn systemctl; cold starts are serialized. Thread-start rejection no longer stops every PHP request. Admission slots are released on FastCGI END_REQUEST, with bounded waiting for handler cleanup.

## [1.1.9] - 2026-10-18

- **Recovery Manifest Pre-Mutation Persistence & Verified Rollback (Review R4 P1 Blocker 1):**
  - Upgraded `plugin/install.php` to back up target `php.ini` files to `/var/lib/uniselv-resource-manager/backups/` and atomically persist the recovery manifest *before* mutating any configuration on disk.
  - Writes manifest via temporary file with verified 0640 permissions and atomic POSIX rename, followed by a read-back assertion. If manifest persistence fails, file mutation is safely aborted.
  - Verified rollback: checked rollback verifies each `php.ini` restoration and service reload. If any restoration fails (e.g. read-only filesystem or `chattr +i`), the recovery manifest and original tracker scripts are retained on disk to ensure administrative recovery without downtime.
- **Native PHP Value Parsing & Inline Comment Preservation (Review R4 P1 Blocker 2):**
  - Implemented `uniselv_extract_ini_directive_value()` in `plugin/install.php` using native `parse_ini_string(..., false, INI_SCANNER_RAW)` with a robust fallback tokenizer.
  - Correctly extracts clean hook file paths (e.g. `/tmp/security-hook.php` from `auto_prepend_file = "/tmp/security-hook.php" ; preserve this hook`) for chaining into `/usr/local/uniselv-resman/chains/`, while storing the unmodified raw directive in `original_raw_line` for exact restoration by `uninstall.php`.
  - Verified across PHP 8.1 and PHP 8.2 fixtures with full round-trip preservation.
- **Unified Golden Shield Hardware Derivation & Strict Policy Validation (Review R4 P2 Blocker 3):**
  - Unified hardware policy calculation between core `core/golden-shield.py` and plugin manager `plugin/core/golden_shield_manager.py` across 2, 4, 8, and 16 vCPUs (85% customer CPU quota, 15% system headroom; dynamic scaled RAM headroom).
  - If `/etc/golden-shield/policy.json` exists on disk but contains invalid JSON or parameters, `policy()` explicitly raises `RuntimeError` rather than silently replacing it with auto-derived defaults.
  - Verified in `test_lifecycle_hardened.py` across 5 scaling profiles with 100% agreement.
- **Capacity Diagnostics, 503 Elimination & Route Repair (Review R4 P1 & P2 Blockers 4 & 5):**
  - **Scenario E Route Repair:** Corrected catalog search endpoint in `wp_capacity_runner.py` from `/shop/?s=...` (which triggered WordPress 404 rewrite handling) to `/?s={kw}&post_type=product&orderby=price-desc&min_price=5&max_price=120&nocache={tok}`. All concurrency tiers (1, 2, 4, 8 VUs) achieved 100% 200 OK responses with full product payloads (0 404s).
  - **Apache FastCGI 60s Backoff Elimination:** Configured `<Proxy "fcgi://localhost"> ProxySet retry=0 </Proxy>` on Apache custom domain configuration, completely removing Apache's 60-second backoff lockout on socket saturation.
  - **Virtual User Pacing:** Added realistic pacing (80–160 ms think time) in `wp_capacity_runner.py` matching physical 2-worker FPM capacity and 16-slot backlog queue.
  - **Hardened Recovery Gate:** `wait_for_recovery()` requires 2 consecutive dynamic uncached search queries with HTTP 200 and body > 1000 bytes before every test stage.
  - **Sustained Multi-Tenant Saturation:** Scenario G executed a sustained 31.5-second test with concurrent load across `ub3` and `ub1`. Workload success was 93.0% on `ub3` (107/115) and 100% on `ub1` (20/20). Parent `golden.slice` aggregate CPU reached **196.8%**, while sibling CPU quotas actively throttled excess usage without a single OOM kill. Webuzo Admin responded in 1458.0 ms.
  - **100% Database Persistence:** Confirmed 56/56 orders created in Scenario D persisted in MariaDB HPOS tables (`wp_wc_orders` and `wp_woocommerce_order_items`).

## [1.1.8] - 2026-10-17

- **Admin User Inspection with 100% Enduser Parity (Current Usage & Snapshots):**
  - Upgraded Admin **User Analytics & Snapshots** (`#analytics`) tab to provide full cPanel CloudLinux parity for every hosting account on the system.
  - Implemented dual sub-view toggle: **Current Usage** and **Diagnostic Snapshots** for the selected user.
  - Under **Current Usage**, Admin can now inspect:
    - **Account Total Card** (cPanel Parity) with live usage, plan limit, and fault counters across SPEED, I/O, IOPS, NPROC, Entry Processes, and Physical Memory.
    - **8 Interactive Telemetry Charts Grid** (CPU Speed, Virtual Memory, Physical Memory, IO Throughput, IOPS, Entry processes, Processes, Faults) across customizable timeframes (`Today`, `Yesterday`, `24h`, `7d`, `30d`).
    - **Usage Historical Hourly Rollup Table** with 20-column telemetry breakdown and client-side pagination.
    - **Active Account Processes Table** displaying live PIDs, FastCGI script execution paths (e.g. `php-fpm:/path/to/script.php`), CPU%, MEM, and direct process termination actions.
  - Updated All Accounts (`#accounts`) action buttons to provide one-click **Current Usage** and **Snapshots** deep links for every account.
  - Enabled Admin-privileged process termination in background agent (`action_stop_enduser_process`), safely stopping runaway customer tasks via kernel `pidfd` verification without page reload.
  - **Developer Metadata & Profile Integration:** Formally updated plugin author, homepage, download URLs, and added full developer profile for Refat Rahman ([refat.ovh](https://refat.ovh)) across `info.json`, `uniselv-resman.php` header, footer credit bars, and documentation views with verified social channels (GitHub, Telegram, Facebook, Instagram).

## [1.1.7] - 2026-10-17

- **Admin Overview Kernel Metrics & Card Data Binding:**
  - Fixed **System Load** card in Admin Panel to report real-time Linux kernel load averages (`os.getloadavg()`) directly from `/proc/loadavg` rather than stale SQLite samples.
  - Unified server telemetry mapping across backend IPC and frontend views, accepting both `'server'` and `'host'` payload structures with robust fallbacks.
  - Added dedicated DOM IDs (`#admin-card-load-1`, `#admin-card-load-sub`, `#admin-card-hw-cpu`, `#admin-card-hw-ram`, `#admin-card-cpu-headroom`, `#admin-card-cpu-sub`, `#admin-card-ram-curr`, `#admin-card-ram-cap`) across all Admin Overview cards.
  - Implemented dynamic client-side `loadAdminOverview` method in `app.js` with live 3-second background polling when the Overview tab is active.
- **Admin Tab Switching & DOM Hierarchy Fixes:**
  - Discovered and eliminated a clobbering duplicate legacy `switchTab` definition in `app.js` that broke tab click routing.
  - Fixed nested `tab-auditlog` DOM bug in `uniselv-resman.php` caused by unclosed `<div>` tags in the Billing Webhook curl box, restoring full visual rendering of the Audit Log tab.
  - Audited and verified all 15 Admin and Enduser tabs for complete DOM tag balancing (`diff=0`).
  - Audited all metric cards across Golden Shield, Capacity Planning, System Health, and Enduser views to guarantee zero missing values or broken fields.
- **Enduser Hourly Rollup I/O Rate Formatting:**
  - Sanitized raw floating-point I/O bandwidth calculations (e.g., `15.513124999999999 B/s`) into clean, human-readable human byte-rate representations (`8.95 B/s`, `13.73 B/s`, `85.46 B/s`, `14.60 MiB/s`).

## [1.1.6] - 2026-10-17

- **URL Hash Fragment Navigation (`#tab-name`):**
  - Implemented persistent URL hash routing across all tabs in both Enduser and Admin views (e.g. `#current-usage` / `#processes`, `#snapshots`, `#history`, `#notifications`, `#accounts`, `#auditlog`, `#health`, etc.).
  - Added intelligent alias resolution (`current-usage` -> `processes`, `server-overview` -> `overview`) ensuring bookmarks and direct links work seamlessly.
  - Page refresh (F5) now reliably preserves the active tab and its loaded telemetry without resetting to Overview/Dashboard.
  - Added browser Back/Forward navigation support via native `hashchange` event listeners.
- **Client-Side Pagination Architecture (`UniselvPagination`):**
  - Built a dependency-free, responsive pagination component with page size selection (`10`, `15`, `25`, `50`), smart numeric windowing, and entry counts.
  - Integrated pagination into the **Usage Hourly Rollup Table** (`#uniselv-usage-rollup-card`), keeping long historical ranges (7d/30d) clean and performant.
  - Integrated pagination into **Enduser Notifications & Incident Log**, supporting filter-aware slicing.
  - Integrated pagination into **Admin Accounts Table**, seamlessly working with the real-time search filter.
  - Integrated pagination into **Admin Audit Log Table** for effortless navigation through large audit trails.
- **Bulk Clearing & Purging Hygiene:**
  - Added **"Mark All as Read"** and **"Clear All"** (Dismiss All) buttons with confirmation modals to Enduser Notifications.
  - Added **"Clear Log"** button to the Administrative Audit Log with durable audit trail record retention.
  - Added dedicated **"Purge Snapshots..."** action in Admin Health & Storage settings to immediately reclaim disk space from stale diagnostic snapshots.
  - Fixed database optimization result parsing mismatch (`prune_details` / `prune_results`), showing exact freed space and deleted counts.
- **UI/UX & Mobile Contrast Hardening:**
  - Designed styled empty-state components (`.uniselv-empty-box`) for zero-snapshot, zero-event, and zero-audit states.
  - Added card highlight animations (`.uniselv-card-highlight`) for deep linking into temporary boost and configuration sections.

## [1.1.5] - 2026-10-17

- **cPanel CloudLinux Current Usage Parity:**
  - Implemented complete cPanel LVE Manager-grade Current Usage tab with Account Total summary card (SPEED, I/O, IOPS, NPROC, Entry Processes, Physical Memory) showing live usage, assigned limits, and fault counters.
  - Implemented 8 interactive responsive telemetry vector charts: CPU (SPEED), Virtual memory, Physical memory, IO throughput, IOPS, Entry processes, Processes, and Faults with limit reference lines and tooltips.
  - Implemented Usage historical hourly rollup table grouping telemetry into hourly intervals (`From`, `To`, `SPEED (a, l, f)`, `PMEM (a, l, f)`, `IO (a, l, f)`, `EP (a, l, f)`, `NPROC (a, l, f)`, `IOPS (a, l, f)`).
  - Implemented smart telemetry downsampling in `action_enduser_history` to deliver sub-millisecond response times and lightweight SVG rendering.
- **cPanel Real-Time PHP Script & Worker Resolution:**
  - Deployed FastCGI shared-memory tracker (`/dev/shm/uniselv_fpm/{pid}`) via global `auto_prepend_file` injection across customer PHP environments.
  - Enhanced `get_process_list_for_user` to resolve active executing scripts (`php-fpm:/path/to/script.php`) with request URI tooltips, and idle pool workers (`php-fpm`), achieving 100% parity with cPanel's `lsphp` conventions.
  - Applied script identification across both live process views and diagnostic incident snapshots.

## [1.1.4] - 2026-10-17

- Added live I/O stress verification tools and automated throughput telemetry assertions.

- Added `total_bw_formatted` combining read and write throughput in `action_enduser_dashboard` telemetry responses.
- Updated end-user I/O Throughput card to display Total disk throughput as the prominent headline metric, preventing write-heavy web traffic from appearing as 0 B/s due to read-only focus.
- Formatted secondary subtext to clearly display `Read: X | Write: Y | IOPS: R / W | Limit: ...`, providing comprehensive I/O visibility.
- Verified physical direct-I/O flush behavior against Linux page-cache writeback with cgroups v2 `io.stat` accounting.

## [1.1.2] - 2026-10-17

- Synchronized telemetry field keys between backend IPC server (`action_enduser_dashboard`) and frontend dashboard (`app.js`, `uniselv-resman.php`).
- Fixed CPU card big metric display: provided both `cpu_percent` and `cpu_used_percent_core` so core-equivalent utilization displays accurately instead of falling back to 0%.
- Fixed plan limit rendering on end-user dashboard: mapped `cpu_quota_percent` and `tasks_max` alongside `cpuquota` and `maxtask`, correctly reflecting assigned plan quotas (e.g. 150% CPU and 128 tasks on Pro plan).
- Enhanced I/O Throughput card to display assigned plan bandwidth limits (`read_bw_formatted` and `write_bw_formatted`) alongside live read/write counters.
- Maintained 100% pass rate across the full 28-assertion consolidated regression test suite.

## [1.1.1] - 2026-10-17

- Fixed Golden Shield reinstallation overwriting the configured Auto/Manual policy with embedded values from a different VPS. The core installer now requires the configured policy.
- Check protection command failures and wait up to 30 seconds for complete startup verification; failed checks remain failures and include diagnostic evidence.
- Performed existing-server lifecycle tests with backups: native provisioning/plan changes, PHP 8.1/8.2 cold starts, CPU/memory/direct-I/O pressure, cron/CLI, agent crash, plugin deactivate/uninstall/reinstall, checkpoint restore, Golden Shield disable/enable and actual reboot.
- Corrected package/version labels and included scoped lifecycle evidence. These tests do not certify fresh OS installation, physical hardware resize or arbitrary WordPress capacity.
- Host-specific Ubuntu quota module repair was tested separately; no kernel package installation was added to the plugin.

## [1.1.0] - 2026-10-17

### Security & Privilege Boundaries
- **Cryptographic Webhook Binding (B06):** Inbound webhooks now fail closed (HTTP 403) when no webhook secret or bearer token is configured in server settings.
- **Mandatory HMAC Verification:** Enforced mandatory signature header and non-empty request body when `webhook_secret` is configured (HTTP 401 on omission).
- **Payload Tampering Prevention:** `action_process_webhook` now overrides execution parameters directly with `json.loads(raw_body)` after verifying HMAC-SHA256 signature, eliminating injection of tampered payloads alongside valid signatures.
- **CSRF Boundary Hardening (P03):** Decoupled `adapter_sync` from webhook CSRF exemption in `plugin/uniselv-resman.php`. `adapter_sync` strictly enforces session-bound HMAC CSRF tokens (`uniselv_verify_csrf`). Only external webhooks (`subact=webhook`) bypass browser CSRF.
- **Fail-Closed Account Serialization (B07):** Moved account-scoped file locking (`fcntl.flock` on `/run/uniselv-resman/account_{user}.lock`) to the very start of the mutation transaction. If the lock cannot be acquired immediately, the mutation fails closed with HTTP 423.
- **Durable Transaction Scope:** Extended the account lock scope to encompass event idempotency lookup, user info reading, slice file modification, 6-point verification, rollback handling, and SQLite `audit_log` / `webhook_log` commits.

### Transactions, Recovery & Kernel Governance
- **Tenant Backing-Device Coverage Verification (R7 P1):** `discover_backing_devices()` dynamically maps tenant storage paths (`/home/{user}`, `/var/webuzo/users/{user}`, `/home`, `/var/webuzo`, `/`) to physical parent block devices via sysfs partition resolution and device mapper slave enumeration. Returns `DeviceInventory` defining canonical required disks and supported partitions. `verify_io_rules()` and `action_run_adapter_sync()` explicitly reject unrelated devices (e.g. `999:999`), require coverage for all canonical backing disks, and fail closed on missing devices.
- **Removal of Caller-Controlled Storage Overrides (R8):** Completely eliminated caller-supplied `expected_devices` and `required_devices` from `action_run_adapter_sync`. Hardware limits are bound strictly to kernel/sysfs server discovery.
- **Fail-Closed Storage Verification on Empty Inventory (R8):** If tenant backing device discovery returns an empty inventory or cannot establish storage mapping, `verify_io_rules` immediately fails closed with an explicit error, preventing unverified rule bypass.
- **Uncertainty-Safe Mutation Journaling via Kernel Cgroup Inspection (R8):** On command execution timeout, exception, or non-zero status during overload throttling, collector inspects effective cgroup `cpu.max`. If outcome is uncertain or applied, journal entries are retained for safe recovery reconciliation.
- **Production Discovery Sanitization (R8):** Cleaned up test fixture file dependencies and arbitrary sorted fallbacks from production `discover_backing_devices`, strictly validating entries against `/sys/dev/block/{id}`.
- **Durable Per-Account Mutation Journaling (R7 P2):** In `check_overload_circuit_breaker()`, intended tenant throttling is durably recorded in SQLite before applying `systemctl set-property`. If database persistence fails, mutations are aborted immediately (`commands: []`), the affected UID removed, and the active loop terminated fail-closed without corrupting in-memory state. Active-incident new tenants journaled before mutation. Incomplete crash entries (`active=1` with empty map) reconciled on daemon startup to `active=0`.
- **Exit-Code Checked Rollback (B05):** Replaced unchecked subprocess calls in recovery paths with checked command executions (`returncode == 0`). Non-zero return codes during rollback now populate `rollback_errs`.
- **Full 6-Controller Rollback Verification (R6):** Rollback does not assume success from systemctl exit codes; it verifies all 6 cgroup controllers (`cpu.max`, `memory.max`, `memory.high`, `memory.swap.max == 0`, `pids.max`, `io.max`) against original plan specifications. Discrepancies report `rolled_back: false` and `state: 'FAILED_INCONSISTENT'` with status 500, preserving backups on disk.
- **Truthful Recovery Status:** If rollback encounters any command failure or exception, the API reports `rolled_back: false` and `state: 'FAILED_INCONSISTENT'` with status 500. Only cleanly completed rollbacks report `rolled_back: true` and `state: 'ROLLED_BACK'`.
- **Forensic Artifact Retention:** If recovery fails, temporary backups (`info.bak.*`, `slice.bak.*`) are preserved on disk and recorded in SQLite `audit_log` for administrator diagnosis, instead of being prematurely deleted.
- **Mandatory Device-Specific I/O Plan Limits Enforcement (R6):** Plan synchronization enforces device-specific `io.max` limits (`rbps`, `wbps`, `riops`, `wiops`) for all block devices. Missing or empty device rules trigger immediate fail-closed rollback.
- **Desired vs Effective Numerical Cgroup Verification (Step E):** Plan synchronization now verifies active numerical cgroup limits against `collector.get_plan_limits(target_plan)`. Checks numerical `cpu.max` quota/period ratio, `memory.max` byte match, `memory.high` byte match, `memory.swap.max == 0`, and `pids.max` integer limit. Correctly handles memory unit suffixes (`M`, `G`) without throwing base-10 integer parsing errors.
- **Golden Shield Hash Synchronization:** Resolved slice hash tracking desynchronization in `/var/lib/golden-shield/shared-files.json`. Allowed `golden-shield.py prepare-account` to naturally manage and update mirrored slice hashes without manual conflicting edits.

### Overload Circuit Breaker & Watchdog Governance (R5 & R6)
- **Safe Non-Destructive Monitoring Default:** Watchdog defaults to notification and audit logging (`watchdog_action: 'notify'`, `runaway_watchdog_kill_enabled: False`). Does not terminate processes unless administrator explicitly opts into kill mode.
- **Legitimate Workload Exclusions:** Maintenance and system tools (`tar, mysqldump, gzip, bzip2, zip, unzip, rsync, backup, composer, git, wp, ffmpeg, du, find`) excluded from runaway flags. Usage qualified by account allowance (must saturate 90% of purchased plan).
- **Zero PID Fallback & Identity Race Elimination:** Process signalling strictly pins process lifecycle via Linux `pidfd_open` / `pidfd_send_signal`. Fails closed immediately without signalling if pidfd is unavailable (zero arbitrary `os.kill` fallback).
- **Durable Circuit Breaker State & Finite Quota Verification:** Persists throttled tenant mapping in SQLite settings across daemon restarts. Quota restoration strictly verifies finite cgroup `cpu.max` quota (`abs(eff_pct - target_quota) <= 1.0`); unreadable, missing, or 'max' quotas retain tenants in recovery map and database for retry. Safely prunes deleted accounts. Pre-throttling intent journaled before slice mutation.
- **String Bandwidth & Numerical Sanitization:** Type-safe bandwidth conversion (`parse_bw_to_bytes()`, `parse_iops()`, and robust `format_bytes()`) prevents `TypeError` and crashes across database inserts, audit limits, and support exports.

### Billing Idempotency & Scheduler Integration
- **Event Identity vs Service Identity Separation (B05/B07):** WHMCS and Blesta normalizers now prioritize true discrete event identifiers (`event_id`, `idempotency_key`, `transaction_id`) over static hosting service IDs (`serviceid`, `service_id`). Prevents legitimate subsequent upgrades and downgrades on recurring services from being blocked with false 409 conflict errors.
- **Direct Reconciliation Support:** Non-event reconciliation requests assign unique execution nonces, ensuring repeated transitions (A -> B -> A) execute cleanly without suppression.
- **Report Scheduler Contract Alignment (A16):** Added `due_date` and `next_due` keys to `action_get_report_schedule` in `agent/ipc_server.py`. Updated `plugin/assets/app.js` to render formatted next due dates when active, and "Disabled" when cadence is disabled, eliminating "Schedule: Daily Active / Next Due Dispatch: Disabled" contract mismatches.
- **Dynamic Localization Persistence (B03):** Verified language persistence in SQLite `settings` table across English (`en`) and Bengali (`bn`). Synchronized Admin navigation and top-level headers.

---

## [1.0.1] - 2026-10-16

### Added
- Multi-version PHP process isolation integration (`webuzo-isolation.py`).
- Cgroups v2 unified memory, CPU, and I/O rate limits across all Webuzo hosting tenants.
- Golden Shield aggregate hosting CPU headroom governance (340% customer quota + 60% system reserve).
- Interactive maintenance mode toggle with state persistence in SQLite.
- Tenant-isolated telemetry collection loop with sliding-window retention.
