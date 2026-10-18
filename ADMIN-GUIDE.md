# UNISELV Resource Manager - Administrator Guide

A comprehensive guide for system administrators managing server resources, tenant limits, and governance using the **UNISELV Resource Manager** within Webuzo Admin.

---

## Release 1.1.10 installation and recovery

Activation installs the Apache FastCGI retry integration automatically and validates the native Apache configuration before reload. See bundled `docs/apache-fcgi-integration.md` for ownership, supported layout, verification and rollback. Do not paste a duplicate per-domain rule.

An installer configuration error now returns failure even when no PHP ini could be changed. Read the activation error, correct the reported prerequisite or file permission, and retry activation. Keep recovery manifests and backups; do not delete them to force activation. Full plugin installation is not an atomic OS snapshot.

On an existing server, activation also checks that an adopted `/usr/local/sbin/webuzo-isolation.py` matches the bundled implementation. If it differs, activation stops for a reviewed maintenance upgrade rather than silently preserving an old proxy bug or overwriting an administrator's integration. This release was applied and verified on the validation VPS with backups; that is not a generic migration of every third-party isolation integration.

The isolation proxy now serializes cold starts, avoids spawning management commands on warm requests and releases slots at FastCGI END_REQUEST. Its concurrency and account resource ceilings remain finite. Over-capacity requests may still be refused; the plugin does not promise unlimited heavy WordPress capacity.

## 1. Access & Navigation

1. Log in to your **Webuzo Admin Panel** (`https://your-server-ip:2005/`).
2. Navigate to **Plugins** -> **UNISELV Resource Manager**, or visit `index.php?act=uniselv-resman`.
3. The interface requires administrative privileges. All requests verify the Webuzo admin session.

---

## 2. Server Aggregate Overview & Golden Shield Headroom

The Overview tab presents a unified picture of physical host capacity and shared service safety.

### The Golden Shield Shared Headroom Policy
Traditional setups either dedicate an entire rigid physical core to system daemons (wasting CPU during quiet periods) or allow hosting customers to consume 100% of host capacity (risking kernel lockups and database crashes).

UNISELV Resource Manager implements the **Golden Shield Shared Aggregate Headroom Model**:
- **Hardware-Scaled CPU Headroom:**
  - On our 4 vCPU server (400% maximum capacity):
    - **Customer Hosting Ceiling:** **340%** (85% of total capacity shared across all customer accounts).
    - **System & Management Reserve:** **60%** (15% of total capacity strictly reserved for system daemons: MariaDB, Webuzo EMPS, Apache/Nginx, SSH, Cron, and Mail).
- **Physical RAM Safety Budget:**
  - **1280 MiB** of physical RAM is strictly protected as host headroom.
  - **Overselling Policy:** While administrators may oversell allocated hosting plan limits across accounts, **overselling never inflates physical safety thresholds**. If customer demand nears the 340% aggregate CPU or physical RAM safety boundary, Golden Shield enforcement protects node stability.

---

## 3. All-Accounts Inventory & Live Monitoring

The **All Accounts** tab displays a consolidated table of all hosting tenants (`ub1` through `ub7`):

| Column | Description |
| :--- | :--- |
| **User** | Linux hosting username. |
| **UID** | POSIX User ID associated with the account cgroup slice. |
| **Current Plan** | Active native Webuzo plan (e.g. `go`, `starter`, `pro`, `turbo`). |
| **CPU Usage** | Current core-equivalent CPU utilization (100% = 1 full core). |
| **CPU Allowance** | Percentage of the account's plan quota currently consumed. |
| **Memory** | Total cgroup memory (`memory.current`) vs configured limit. |
| **Sync Status** | Cgroup v2 kernel synchronization badge (**Synchronized** or **Drift Detected**). |
| **Actions** | Quick links to view user details, inspect processes, or apply temporary overrides. |

---

## 4. Native Plan Synchronization & Effective Cgroup Audit

UNISELV Resource Manager is designed to **extend, not replace**, native Webuzo Resource Limits:
- **Native Definitions:** Plans are stored in `/var/webuzo/cgroups/<plan>`.
- **Systemd Slices:** Generated under `/etc/systemd/system/<uid>.slice`.
- **Kernel Enforcement:** Monitored under `/sys/fs/cgroup/<uid>.slice` and `/sys/fs/cgroup/golden.slice/golden-<uid>.slice`.

### Performing an Audit
1. Open the **Audit Limits** view in the Admin panel.
2. The system compares the Webuzo plan definitions against the live `cpu.max` and `memory.max` kernel values.
3. If drift is detected (for example, if a manual edit bypassed Webuzo), click **Bulk Sync All Plans**.
4. The system presents an elegant, modern confirmation dialog (`UniselvModal.confirm`) explaining the synchronization scope.
5. Upon confirmation, the agent invokes the native Webuzo CLI (`/bin/webuzo --api act=resource_limits`) and reloads systemd to eliminate discrepancies safely. A modern floating toast notification (`UniselvNotify.success`) provides instant non-blocking feedback.

---

## 5. Expiring Temporary Overrides

When a customer experiences a legitimate traffic spike (e.g. product launch, viral campaign) and needs a short-term capacity boost:
1. In the All-Accounts table, select the target user.
2. Click **Apply Temporary Override**.
3. Select an elevated target plan (e.g. upgrade `ub1` from `go` to `turbo`).
4. Set the duration (e.g. 15 minutes, 1 hour, 4 hours, 24 hours, or custom minutes) and record an administrative reason.
5. Click **Apply Override**.

### Automatic Restoration
- The privileged daemon updates the user's slice and logs the override expiration timestamp in `/var/lib/uniselv-resource-manager/resman.sqlite`.
- The background daemon evaluates active overrides every 30 seconds.
- Upon expiration, the daemon automatically reverts the account to its original native plan and issues a system audit log. No manual administrator intervention is required.
- Overrides can also be manually cancelled at any time via the Admin UI.

---

## 6. External Billing Adapters (WHMCS & Blesta)

UNISELV Resource Manager includes built-in adapters for external hosting automation:
- **Webhook Endpoint:** Internal IPC action `run_adapter_sync`.
- **Supported Events:**
  - `package_change`: Automatically updates user plan assignments upon invoice payment or plan upgrade in WHMCS/Blesta.
  - `account_suspend`: Restricts limits or freezes workloads.
  - `account_unsuspend`: Restores standard tier limits.

### Idempotency Protection
To prevent duplicate package transitions or race conditions caused by network retries:
- Every webhook payload accepts an `idempotency_key` (e.g. `whmcs-trans-98214`).
- If an event with the same idempotency key is received within 24 hours, the agent returns the cached success response without re-executing plan mutations.

---

## 7. Telemetry Storage & Retention Policy

To prevent unbounded SQLite disk growth across months of high-resolution metric collection, UNISELV Resource Manager features an active storage governance engine:

### Configurable Retention Thresholds (Admin Tab 5)
Administrators can fine-tune sliding-window retention days directly from the Admin Panel:
- **Telemetry Samples Retention (Days):** Sliding window for 10-second CPU, memory, task, and I/O records (Default: 30 days).
- **Diagnostic Snapshots Retention (Days):** Sliding window for full process hierarchies, HTTP traces, and SQL queries (Default: 14 days).
- **Resource Events & Throttling Incidents (Days):** Sliding window for CPU throttling, task limits, and OOM terminations (Default: 30 days).
- **Audit Trail Logs Retention (Days):** Audit log records of administrative mutations and overrides (Default: 90 days).

### Automated Hourly Maintenance & Storage Quota
- **Background Daemon Hook:** Every 3600 seconds (1 hour), the collector daemon automatically executes a sliding-window prune based on the configured thresholds.
- **Quota Safeguard:** A 100 MiB safety threshold is monitored. The UI renders a live storage utilization progress bar showing exact database footprint (e.g. `568.0 KiB of 100 MiB Quota [0.6%]`) along with individual table row counts.

### On-Demand Pruning & VACUUM Optimization
- Administrators can trigger an immediate manual purge and disk compaction by clicking **Prune & Optimize Database Now**.
- This executes:
  1. Instant timestamp-based cutoff deletions across `samples`, `snapshots`, `events`, `system_metrics`, and `audit_log`.
  2. `PRAGMA wal_checkpoint(TRUNCATE)` to flush and truncate Write-Ahead Logging logs.
  3. `VACUUM` to release free pages back to the Linux filesystem.
  4. Returns before/after byte counts and formatted disk space reclaimed.

---

## 9. Golden Shield Kernel Governor Tab (Admin Tab 4)

The **Golden Shield Kernel Governor** tab gives administrators complete visibility and runtime control over node-level CPU quota and memory protection:

### Governor States
- **Active:** Golden Shield service is running, cgroup `golden.slice` is active with hardware-scaled limits, and all customer workloads are contained.
- **Degraded:** Slices exist but configured policy diverges from live kernel attributes or outside processes exist.
- **Disabled:** Governor limits removed from kernel. Customer slices operate without aggregate ceiling.
- **Not Installed / Unsupported:** Golden Shield binaries or cgroups v2 controller unavailable.

### 4-Tier Governance Comparison Grid
1. **Detected Hardware:** Real-time kernel hardware probe (vCPU count, physical RAM in GiB, available swap, and hardware fingerprint hash).
2. **Calculated Policy (Auto):** Dynamic formula results (85% customer hosting CPU, 15% system daemon headroom across all cores, dynamic RAM headroom).
3. **Configured Policy:** Current configuration in `/etc/golden-shield/policy.json`.
4. **Active Kernel Limits:** Live values from `/sys/fs/cgroup/golden.slice/cpu.max` and `memory.max`.

### Escaped Process Audit & Coverage
- Continuously audits whether any tenant processes (Apache web workers, PHP workers, MariaDB) execute outside `golden.slice`.
- Displays green badge **"100% Contained"** when all workloads are strictly isolated within their assigned boundaries.

### Reconfiguring the Governor
1. Click **Reconfigure** to open the modal dialog.
2. Select **Governance Mode**:
   - **Auto Mode (Recommended):** Dynamically scales hosting pool CPU quota (85%) and reserves (15%) to match the physical CPU core count, preventing server lockups even as instances are resized.
   - **Manual Mode:** Allows explicit numeric overrides for `customerCpuPercent` and `hostingMemoryMaxMiB`.
3. Click **Save & Apply**. Limits are dynamically applied to the kernel without service restart or customer downtime.

### Safe Verification & Disabling
- Click **Run Verification** to execute an on-demand audit comparing live cgroups attributes against the policy file.
- Click **Disable** (with two-stage modal confirmation) to safely dismantle aggregate cgroup ceilings in emergency troubleshooting scenarios.

---

## 10. Configuration Backup Checkpoints & Transactional Restoration

Before every policy modification or reconfiguration, UNISELV Resource Manager automatically captures a timestamped backup checkpoint in `/var/lib/uniselv-resource-manager/golden-backups/`.

### Restoring a Backup Checkpoint
1. Navigate to the **Golden Shield & Capacity** tab (Admin Tab 4).
2. Click **Restore Backup** in the header banner.
3. The Restore Modal queries the background agent and displays all available configuration checkpoints with timestamps, governance modes, CPU quotas, memory caps, and headroom numbers.
4. Select the desired checkpoint and click **Restore Selected Backup**.
5. The system performs a transactional restoration:
   - Validates the backup ID format against path-traversal attacks.
   - Verifies the policy schema integrity.
   - Captures a pre-restore checkpoint.
   - Atomically updates `/etc/golden-shield/policy.json` and `/etc/golden-shield/mode.json`.
   - Writes the persistent systemd drop-in override `/etc/systemd/system/golden.slice.d/50-uniselv-limits.conf`.
   - Applies memory caps and CPU quotas to the running kernel.
   - Executes live kernel verification. If verification fails, the system automatically rolls back to the pre-restore state.

---

## 11. Hardware Change Reconciliation & Persistent Modes

When a cloud VPS is resized (e.g. CPU core or RAM upgrades), UNISELV Resource Manager ensures hosting boundaries adapt safely without manual recalculation:
- **Governance Modes:** Stored persistently in `/etc/golden-shield/mode.json` and SQLite `settings`.
- **Auto Mode:** Upon detecting CPU changes or a RAM delta > 5%, the agent computes the new 85% hosting quota and RAM safety headroom, writes persistent drop-in configs, and applies limits immediately.
- **Manual Mode:** If custom administrator overrides are active, the reconciler preserves your manual limits and logs an administrative warning, allowing you to review capacity at your convenience.
- **Zero Fabricated Fallbacks:** Hardware detection reads `/proc/cpuinfo` and `/proc/meminfo` directly and fails closed if metrics cannot be ascertained.

---

## 12. Reboot Resilience with Systemd Drop-in Overrides

Setting runtime limits with `systemctl set-property --runtime` is volatile across reboots. UNISELV Resource Manager maintains persistent drop-in overrides at:
`/etc/systemd/system/golden.slice.d/50-uniselv-limits.conf`

```ini
# Automatically managed by UNISELV Resource Manager
[Slice]
CPUQuota=340%
MemoryMax=6786383872
MemorySwapMax=0
```

This guarantees that whenever the server reboots or systemd reloads, kernel cgroup quotas and zero-swap enforcement are restored instantly before services start.

---

## 13. Interactive Help & About Tab (Admin Tab 6)

The **Help & About** tab provides an integrated administrative runbook accessible directly inside Webuzo:
- **Real-Time Topic Search:** Search bar filters topics, commands, and scenarios in real time.
- **Category Navigation Pills:** Filter by *Quick Start*, *Feature Guide*, *Resource Metrics*, *Golden Shield*, *Practical Scenarios*, *Troubleshooting*, or *About*.
- **One-Click Command Copy:** All terminal verification commands (`systemctl status`, `journalctl`, `golden-shield.py check`, `cgroup cat`) include one-click **Copy** buttons with visual confirmation.
- **Contextual Help:** Header pills on tabs (such as the *Documentation* pill next to Bulk Sync) link directly to relevant topics in the Help section.


