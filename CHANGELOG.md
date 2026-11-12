## 1.2.0 — 2026-11-12

- Add full Platform Operations & Zero-Terminal Application Services suite across Admin (**Platform & Laravel** tab) and Enduser (**App Services & Tools** tab):
  1. **OS Build Preflight & One-Click Toolchain/Composer Installer**: checks `gcc`, `g++`, `make`, `autoconf`, `pkg-config`, `libssl-dev`/`libcurl4-openssl-dev`/`zlib1g-dev`, and SHA-384 verified `composer` binary with background apt/dnf installation.
  2. **One-Click Managed Laravel Services**: automatic Laravel project discovery, plan-proportional worker budgets, and one-click Install/Enable/Disable/Start/Stop/Restart/Remove/Logs/Test for **Laravel Queue Workers** (`queue:work`), **Laravel Horizon** (`horizon`), **Laravel Reverb WebSocket** (`reverb:start`), and **Laravel Scheduler** (`schedule:work`) running inside `User=<account>` + `Slice=golden-<uid>.slice`, plus Admin live ephemeral worker self-test.
  3. **Node.js / Python / Manual Laravel Daemon Cgroup Containment & Budget Guard**: `/proc` detection and automatic `systemd-run`/`golden-<uid>.slice` containment with concurrency caps.
  4. **Per-Account Port Registry & Socket Isolation**: collision-free 10-port blocks (`20000–59990`) + `/run/uniselv-apps/<user>` + reverse-proxy snippet.
  5. **Per-Account Isolated Redis ACL Governance**: prefix-locked `u_<user>` ACLs (`~<user>:*` with dangerous admin commands disabled), persisted via `aclfile` + `ACL SAVE`, live cross-tenant `NOPERM` verification test, `.env` snippet, and opt-in `default` user lockdown.
  6. **Heavy Background Binary Concurrency & Timeout Guard**: enforces slice containment, max concurrency, and max runtime for `chromium`/`headless_shell`/`wkhtmltopdf`/`ffmpeg`/`libreoffice`.
  7. **App Log Bloat & Inode Watchdog**: monitors `/home` inodes and oversized tenant logs with symlink-safe tail truncation.
  8. **Server-to-Server Policy Migration Export / Import**: secret-free JSON bundle export, dry-run preview, transactional apply, and managed service re-provisioning.
  9. **Per-Account /run/uniselv-apps/<user>/ports.json Auto-Export**: atomic metadata emission (`0640` permissions, non-secret port allocations, socket dir, and Redis prefixes) with boot-time self-healing for zero-configuration client app detection (REVERB_PORT, OCTANE_PORT, HORIZON_METRICS_PORT).

## 1.1.43 — 2026-11-12

- Promote OpenSwoole Governance to a dedicated top-level **OpenSwoole** Admin tab with quick-jump links from System Health, live PHP/INI/toolchain readiness diagnostics (`openswoole_diagnostics`), one-click ephemeral loopback & cgroups v2 end-to-end self-test (`openswoole_selftest`), plan/account task-worker override controls, account-scoped Octane/OpenSwoole launch snippet generator, and an audit & enforcement event log table.

## 1.1.42 — 2026-11-12

- Add OpenSwoole Governance & Multi-PHP Automation: automatically discover and compile compatible PECL OpenSwoole releases inside isolated transient systemd units, copy `.so` into each PHP version's true `extension_dir`, auto-enable OpenSwoole on newly installed Webuzo PHP branches, enforce `golden-<uid>.slice` cgroups v2 containment and plan-proportional worker budgets, and expose full Admin and Enduser UI controls.

## 1.1.41 — 2026-11-10

- Bound concurrent history scans, share identical in-flight results and briefly cache successful history responses. Accept up to 24 Agent IPC clients and return a retryable response when history capacity is busy.

## 1.1.40 — 2026-11-10

- Speed up concurrent history reads by aggregating bounded ranges through the existing SQLite index instead of sorting raw samples by computed bucket.

## 1.1.39 — 2026-11-10

- Fix in-place upgrades on servers with an existing PHP isolation runtime. Use the generator profile when provisioning a new runtime and verify the running isolation, PAM and Golden Shield configuration during upgrades.

## 1.1.38 — 2026-11-10

- Reconcile Golden Shield checksums for account slices changed by the proportional CPUWeight migration. Back up the registry and preserve the drift guard for unrelated changes.
- Verify that a process has exited before reporting success. Report signal failures instead of recording a successful stop.
- Roll up telemetry by account and minute after 48 hours while preserving weighted averages, peaks and event counts. Protect the newest hour under storage pressure and compact SQLite after measuring reusable pages.
- Aggregate history in SQLite and limit charts to 300 points. Ignore stale responses when switching accounts or time ranges and display retry controls on read failures.
- Show host CPU usage separately from hosting allocation and timestamp the Top Resource Consumers samples. Add keyboard-operated sample inspection and time labels to history charts.
- Improve mobile navigation, Bengali locale handling, notification timestamps and status colors. Show scheduled reports as Generated and distinguish live telemetry from the last sample.

## 1.1.37 — 2026-11-05

- **Storage-Bounded SQLite Telemetry Engine (`collector.py`):**
  - Implement active database storage quota enforcement honoring `retention_max_storage_mib` (default 100 MiB).
  - Automatically downsample historical telemetry older than 48 hours to 1-minute averages (deleting 11 out of 12 raw 5s samples), reclaiming 91.6% storage while preserving smooth long-term chart visibility.
  - Progressive batch pruning of oldest excess samples coupled with transactional WAL checkpoint truncation and filesystem VACUUM whenever disk footprint exceeds configured safety thresholds.
- **Daemon Memory Safety & OOM Defense (`ipc_server.py`):**
  - Completely re-architect `action_enduser_history` to use SQL-level streaming aggregation and time-bucket grouping (`bucket_ts = (timestamp / step) * step`).
  - Eliminates dangerous Python heap allocation of 500,000+ dict objects during 7d/30d queries, slashing daemon RSS memory consumption from 700+ MiB to <2 MiB and guaranteeing `uniselv-resman-agent` never exceeds systemd `MemoryMax=128M`.
- **Dynamic Cgroups v2 Kernel Quota Discovery & Fair CPUWeight (`golden-shield.py` & `collector.py`):**
  - Integrate live cgroup v2 controller probing (`cpu.max`, `memory.max`, `pids.max`) to ensure live telemetry, thresholds, and circuit breakers immediately adapt to Webuzo plan updates without hardcoding.
  - Dynamically inject proportional cgroups v2 `CPUWeight = max(10, min(10000, CPUQuota))` into account slices (`golden-<uid>.slice`) for fair-share CPU scheduling during multi-tenant CPU contention.
- **Coordinator Startup Reconciliation Timeout (`webuzo-isolation.py`):**
  - Extend isolation coordinator supervisor timeout (`TimeoutStartSec=180`) to eliminate serial systemd reload stalls across high-density tenant pools.

## 1.1.36 — 2026-11-04

- Implement plan-proportional upward and downward PHP-FPM worker ceiling calculation (`account_worker_ceiling`) derived from cgroup RAM allowance and task limits, lifting the legacy 8-worker native ceiling for higher-tier accounts (Enterprise up to 21 workers, Turbo up to 15, Pro at 9, Starter at 6, Go at 3).
- Integrate dynamic cgroups v2 `CPUWeight` generation in Golden Shield proportional to plan `CPUQuota` (Enterprise=280, Pro=150, Starter=100) ensuring fair dynamic CPU scheduling during peak multi-tenant contention while preserving single-tenant burstability.
- Enforce strict Golden Shield root reservation for host OS and Webuzo Admin Panel (`system.slice` with `CPUWeight=1000` and guaranteed 1.4+ GB reserved physical RAM).
- Extend coordinator startup reconciliation timeout (`TimeoutStartSec=180`) across all PHP runtime managers and implement atomic slice pre-caching to eliminate serial systemd reload stalls across 25+ tenant pools.
- Patch `place_native_process` to verify PID existence and reset failed transient units, preventing systemd scope tracking exhaustion.
- Update `policy.json` with `maxActivePools: 10`, `workerRssMiB: 140`, and `accountMaxWorkers: 32`.

## 1.1.35 — 2026-11-01

- Optimize PAM Session Guard (`webuzo-session-guard.py`) by adding immediate fast-path bypass for non-interactive `cron` and `crond` sessions (`PAM_SERVICE in ('cron', 'crond')`). Eliminates concurrent subprocess storms and 500–700% CPU spikes during minute-boundary cron dispatch.
- Fast-path existing slice verification: skip redundant `golden-shield.py prepare-account` execution when the account slice is already active and bounded.
- Preserve interactive SSH session placement, cgroup isolation boundaries, and fail-safe error logging.

## 1.1.34 — 2026-10-30

- Add self-healing staging cleanup and PID-isolated temporary files to atomic writer, preventing zero-byte lock deadlock when disk space is exhausted.
- Enforce try/finally unlinking across isolation, Golden Shield and session guard staging paths to guarantee incomplete writes never block future service admission.
- Add explicit fsync and flush barriers prior to atomic replacement.
- Preserve global native defaults, physical/account safety boundaries, and existing runtime policy.

## 1.1.33 — 2026-10-27

- Preserve routing and charged leases on unchanged native graceful reload; keep explicit restart as a maintenance operation.
- Derive managed master control grace from the inherited finite request timeout, preserve longer native values, and verify every managed pool.
- Retain balanced native global settings after repeated worker, queue, Apache and database comparisons; synchronize the canonical generator source and asset versions.
- Record 184 isolated Linux tests, 24,363 accepted recorded requests without failures, 331 matching configured values, and automatic reboot recovery. Preserve failed/rejected attempts and workload boundaries in the dated report.

## 1.1.30 — 2026-10-25

- Repair and activate the checked native PHP service bridge when an already-managed PHP version is onboarded or repaired. Refuse a changed/custom native unit instead of overwriting it.
- Include native bridge activity in runtime governance health, repair admission and post-operation verification. A healthy coordinator and health master alone no longer hide an inactive compatibility bridge.
- Add regressions for automatic bridge recovery and failed post-repair verification.
- Preserve shared physical budgets, native global PHP-FPM defaults, per-account limits and retained history.
- Add optional owner-selected Shared Redis integration sized from the matching physical Global Inputs: one cache service, no per-user allocation. Verify restart readiness, cache/client/process limits and Golden placement; retain and restore native ownership/configuration transactionally.
- Add cache-only consent, hardware-drift refusal, idempotence and rollback regression coverage.
- Add a dated current-host readiness follow-up. Historical Redis guard and backup rotation evidence is distinguished from the actual current installation.

- Verify native Webuzo 4.8.6 to 4.8.7 update, subsequent automatic bridge recovery/reboot, four PHP versions, account provisioning and 25 native HTTP routes. No additional runtime code change was needed for that update.

## 1.1.29 — 2026-10-24

- Fix queue stalls during fair-share rebalancing when long-running/background PHP prevents backend-idle proof. A drain attempt now uses five percent of the native-derived proxy request timeout, rounded up to a whole second (minimum one second), never more than the timeout.
- On drain-budget expiry, retain the full charged worker grant and backend, resume queued requests, and keep the existing rebalancing cooldown. Do not terminate background work, release unproven memory, reset client deadlines or replay submitted requests.
- Add a real-socket regression proving an unproven background job cannot hold the live queue for the whole request timeout.
- Preserve physical admission budgets, account CPU/RAM limits, native global FPM defaults and the existing private-backend protections.
- Record successful bounded tests and retained failures separately; native maintenance is not a zero-downtime guarantee.

## 1.1.28 — 2026-10-24

- Fix a sustained partial-grant bottleneck: queued demand now requests unused peer capacity and grows the protected relay concurrency without restarting PHP/OPcache.
- Keep the private FPM ceiling tied to native account limits, with a root-only backend socket and PID/start-token protocol handshake before enabling relay enforcement. Older proxies retain bounded legacy FPM caps.
- Drain forwarded work and verify idle FPM children before fair-share reductions or legacy transitions; preserve queue deadlines and never replay requests. Unverifiable backends defer regrant rather than force a stop.
- Honor waiting peers on a fresh cold grant and avoid yielding a cold proxy that has no lease to reclaim.
- Expose private FPM ceiling, concurrent grant and enforcement separately in the audit UI; refresh canonical installer source/hashes and dated performance evidence.
- Hardware budgets and global native PHP defaults are unchanged. Bounded GET results do not certify checkout or a universal visitor count.

## 1.1.27 — 2026-10-24

- Use verified native plan transactions for temporary boost application, cancellation and expiry; never record failed restoration as success.
- Persist application intent before mutation and retry interrupted/failed restoration.
- Refuse overlapping unresolved boosts, UID reuse, independent plan drift and internal billing-mapping redirection.
- Expose pending/failed boost recovery counts in administrator health.
- Expand native lifecycle, security and failure-path evidence; preserve full-certification exclusions.
- Fail closed on full runtime removal before any service stop if a recovery launcher, registry or native bridge is invalid; reject removal while Golden Shield depends on it.
- Recover existing native unit enablement without redundant SysV synchronization; preserve/recompute custom/automatic warm retention correctly when PHP version overhead changes.
- Resolve canonical combined-installer admission policy through the shared configuration normalizer, including warm retention.
- Scope reseller audit account aliases, PHP runtime rows and totals to owned accounts.
- Count descendant-local kernel task refusal events without hierarchical double counting.
- Track the Apache foreground master directly in systemd; preserve native environment/file limits and remove PID-file-based boot ownership failure.
- Show telemetry-storage threshold warnings instead of a green normal badge when the configured warning size is exceeded; preserve unknown readings and clamp only bar geometry.
- Keep governance snapshots current when journal reads time out; bound the shared journal tail and expose missing event coverage.
- Refresh canonical generator embedded hashes, cache revision, exact source-change guides and dated readiness evidence.


## 1.1.26 — 2026-10-24

- Replace the competing native UID process mover through an owned systemd drop-in; preserve vendor source, managed FPM descendants and shared Apache placement. Adopt escaped legacy account sessions into valid cgroup v2 child scopes and reload account assignments dynamically.
- Keep warm master/OPcache state using a physical-budget-derived idle deadline; yield quiescent leases to eligible waiting peers or low host memory headroom. Global ondemand worker defaults and account/host hard limits remain unchanged.
- Sum disjoint native and managed account telemetry, retain historical memory charges, enumerate actual UID processes and prevent matching kernel settings from hiding escaped workers.
- Add administrator cgroup integrity evidence and update Help, the canonical generator, embedded installer source/checksums and matched profile.
- Validate bounded worker placement, legacy session recovery, OPcache reuse after the old idle cutoff, CPU throttling and cross-account PHP requests. Broader workload/lifecycle certification remains separate.

## 1.1.25 — 2026-10-24

- Correct circular/liquid card percentages, actual RAM boundary measurement and CPU allocation normalization.
- Preserve zero/unknown values; remove fake hardware fill, minimum liquid levels, load floor, RAM fallback and admin chart prehistory.
- Normalize SVG paths, align server-rendered initial fills, and document each card denominator.
- Server tuning and resource limits are unchanged; focused visual/arithmetic verification is separate from lifecycle/capacity certification.

## 1.1.24 — 2026-10-24

- Refresh searchable Help/About runtime guidance, dynamic compatibility details, diagnostic command authentication and metric explanations.

- Add guarded background PHP installation/vendor/binary-change reconciliation using reviewed global settings, stable observations, syntax checks, transaction rollback and bounded retries.
- Preserve intentional runtime retirement; expose re-enable, root-only recovery and asynchronous serialized administrator operations.
- Add shared-profile PHP/all-section drift views, bounded no-follow account INI audit, capacity event reasons/timeline/minute buckets and private configuration comparisons.
- Accept native generator JSON exports, resolve version-specific session templates and keep missing/invalid evidence visible.
- Escape notification text and use durable unique atomic staging for governance metadata.
- Prevent partial agent deployment when an unreviewed adopted runtime blocks activation; update health/help UI and canonical installer assets.
- Preserve global native PHP defaults, dynamic runtime caps, physical safety budgets, neutral animated 503 design and evidence-based readiness limitations.

## 1.1.23 — 2026-10-24

- Fail closed before retirement when native configuration, manifests, launcher ownership or restoration backups cannot be validated.
- Serialize PHP lifecycle operations; retain a durable recovery journal and restore prior files, registration and service states after failed onboarding. Interrupted operations recover before the next lifecycle action.
- Rebase approved native launcher restoration on vendor regeneration while preserving the previous baseline; remove forced SIGKILL during repair.
- Account for added PHP-version overhead inside the reviewed physical budget; release the additional reserve after retirement without inflating the baseline.
- Reject corrupt managed registries and never substitute physical discovery for explicit registration. Surface runtime reload failures in bulk plan-sync results.
- Add read-only PHP runtime registration/status in System & Agent Health; identify virtual CPUs correctly.
- Fix Bulk Sync response rendering for account counts, legacy plan arrays, partial errors and runtime reload failures; verify six UI response cases.
- Package with PHP ZipArchive, forward-slash paths, directory 0755/file 0644 permissions and verified source/asset closure.
- Separate current regression evidence from historical incomplete lifecycle claims. No new all-platform, fresh-OS or WordPress-capacity certification.

## 1.1.22 — 2026-10-22

- Modernize Admin Overview and Enduser Dashboard UI with illuminated neumorphic/glassmorphic gauge cards, dynamic liquid SVG circular fills (0%–100%), 7-bar undulating equalizers, animated sparkline telemetry curves, glowing live telemetry neon capsule badges, and instant zero-latency tab switching.
- Resolve syntax anomaly in frontend bundle and verify zero console errors/warnings in Chrome DevTools across all resolution viewports.
- Fix unmanaged PHP physical discovery breaking native plan save transactions and billing adapter synchronizations; isolate isolation reload loops strictly to explicitly managed PHP versions (`/var/lib/webuzo-isolation/installed.json`).
- Implement dynamic PHP onboarding (`webuzo-isolation.py onboard <version>`) and retirement (`webuzo-isolation.py retire <version>`) with automated compensating rollback and fail-closed checks against active tenant pools.
- Expose PHP lifecycle inspection and management through background daemon IPC with CSRF enforcement.
- Update configuration generator PHP version validator to dynamic regex pattern `/^php\d{2,3}$/`, supporting newly introduced PHP versions without validation failures.
- Transition automated test suites to dynamically provisioned, isolated disposable test fixtures (`disptest`) with comprehensive post-test cleanup, eliminating hardcoded historical account dependencies.
