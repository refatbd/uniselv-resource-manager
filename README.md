> Current release: **1.1.16**, 2026-10-20. Privileged Webuzo panel activation and deactivation dispatchers, root CLI preflight guards, and PHP-FPM listen.backlog fallback. Previous release records below are historical.

> Current release: **1.1.12**. Installable artifact: `uniselv-resman-1.1.12.zip`. Current scope and evidence: `plugin/docs/LIFECYCLE-REVIEW-1.1.12.md`.

# UNISELV Resource Manager for Webuzo

A resource management and telemetry extension for Webuzo Hosting Panel on Ubuntu Linux (cgroups v2). Release validation and its boundaries are recorded in `plugin/docs/RELEASE-VALIDATION-1.1.10.md`.

UNISELV Resource Manager bridges native Webuzo Resource Limits (`/var/webuzo/cgroups/` and `/bin/webuzo --api act=resource_limits`) with kernel-level cgroups v2 telemetry, hardware-scaled aggregate safety headroom (Golden Shield integration), diagnostic snapshots, and administrative governance.

---

## Architecture Overview

```
+-----------------------------------------------------------------------------------+
|                                Browser Clients                                    |
|         Admin Panel (`act=uniselv-resman`)     Enduser Panel (`act=uniselv-resman`)|
+-----------------------------------------------------------------------------------+
                                        | (HTTPS / EMPS FastCGI)
                                        v
+-----------------------------------------------------------------------------------+
|                        Webuzo Plugin Layer (PHP 8.1+)                             |
|  - `uniselv-resman.php`: Admin & Enduser Theme Controllers                       |
|  - `api_client.php`: Strictly Isolated UNIX Domain Socket IPC Client             |
|  - `assets/`: Native Responsive UI, SVG Line Charts, Tabbed Views                 |
+-----------------------------------------------------------------------------------+
                                        | UNIX Socket (`/run/uniselv-resman/agent.sock`)
                                        v
+-----------------------------------------------------------------------------------+
|                Privileged Background Daemon (`uniselv-resman-agent`)              |
|  - Systemd Service: MemoryMax=64M, TasksMax=32, AmbientCapabilities=CAP_KILL      |
|  - `collector.py`: High-resolution cgroups v2 delta accounting (10s interval)     |
|  - `ipc_server.py`: Request router with caller authorization & IDOR isolation     |
|  - `schema.py`: SQLite WAL bounded storage (`/var/lib/uniselv-resource-manager/`) |
+-----------------------------------------------------------------------------------+
           |                                                      |
           v                                                      v
+-----------------------+                            +------------------------------+
|   Kernel Cgroups v2   |                            | Native Webuzo & Systemd      |
| `/sys/fs/cgroup/`     |                            | `/var/webuzo/cgroups/<plan>` |
| `<uid>.slice`         |                            | `/bin/webuzo --api`          |
| `golden-<uid>.slice`  |                            | `/etc/systemd/system/*.slice`|
+-----------------------+                            +------------------------------+
```

---

## Key Features

### 1. Enduser Capabilities (`act=uniselv-resman`)
- **Dashboard & Gauge Widgets:** Real-time CPU, memory, read/write I/O throughput, IOPS, and task/thread counts.
- **Accurate CPU Semantics:**
  - 100% CPU strictly represents one full physical CPU core.
  - Dual metrics: Core-equivalent usage and Account Allowance Percentage (`used / quota * 100`).
- **Memory Transparency:**
  - True cgroup v2 kernel accounting (`memory.current`).
  - Clear separation between active anonymous RAM (`memory.stat` `anon`), pagecache (`file`), and swap memory (`memory.swap.current`).
  - Process RSS is never falsely equated to total cgroup memory.
- **Historical Analysis:**
  - 1 Hour, Today, 24 Hours, 7 Days, and 30 Days historical telemetry.
  - Native SVG line charts rendering averages, sampled peaks, and historical limit thresholds without external CDN dependencies.
- **Resource Events:** Plain-language alerts for CPU throttling events, memory pressure, OOM terminations, and task limit exhaustion with exact timestamps.
- **Live Process Inspection & Controlled Stop:**
  - Authenticated view of the customer's PHP workers, cron jobs, and CLI scripts.
  - Redaction of sensitive command-line parameters (passwords, tokens, database credentials).
  - Secure process termination guarded against PID reuse race conditions via `/proc/<pid>/stat` process start-time verification.
- **Diagnostic Snapshots:**
  - Automated event-triggered and periodic high-watermark snapshots.
  - Associated sanitized HTTP request logs and MariaDB query traces.
- **Privacy-Safe Support Export:** One-click export of resource history and diagnostic events with all credentials, session tokens, and passwords scrubbed.

### 2. Admin Governance Capabilities (`act=uniselv-resman`)
- **Server Overview & Golden Shield Headroom:**
  - Aggregated server CPU, RAM, swap, and I/O pressure.
  - Shared aggregate headroom policy: 4 vCPU scales to 340% managed hosting allocation + 60% dedicated system/admin reserve; 1280 MiB RAM physical safety reserve.
  - Protection of system services without assigning a rigid dedicated single core.
- **All-Accounts Inventory:** Real-time table covering all hosting accounts (`ub1` through `ub7`), active plans, kernel CPU/RAM utilization, and synchronization health.
- **Native Plan Synchronization & Audit:**
  - Audits Webuzo plan definitions against live systemd slices and cgroup kernel limits.
  - Direct integration with `/bin/webuzo --api act=resource_limits` to eliminate policy drift.
- **Expiring Temporary Overrides:**
  - Grant temporary plan boosts (e.g. 60 minutes) to resolve urgent spikes.
  - Background daemon automatically reverts to the original native plan upon expiration.
- **External Billing Adapters (WHMCS / Blesta):**
  - Webhook ingestion for plan upgrades/downgrades.
  - Built-in idempotency key deduplication to prevent duplicate execution during billing system retries.
- **Telemetry Storage & Retention Policy UI:**
  - Configurable sliding-window thresholds: Telemetry Samples (default 30d), Diagnostic Snapshots (14d), Resource Throttling Events (30d), Audit Trail Logs (90d).
  - Storage quota monitor: Live progress bar showing exact SQLite database footprint against a 100 MiB safety threshold with table row counts.
  - On-Demand Optimization: One-click "Prune & Optimize Database Now" action triggering WAL checkpoint truncation and filesystem VACUUM.
  - Continuous tracking of daemon RSS memory (bounded by `MemoryMax=64M`).

---

## Directory Structure

```
uniselv-resource-manager/
├── agent/
│   ├── agent_daemon.py             # Main background daemon entry point
│   ├── collector.py                # Cgroup v2 delta telemetry collector
│   ├── ipc_server.py               # UNIX socket server & authorization logic
│   ├── schema.py                   # SQLite database schema & retention engine
│   └── uniselv-resman-agent.service# Systemd service definition
├── plugin/
│   ├── info.json                   # Webuzo plugin metadata
│   ├── index.php                   # Plugin bootstrapper & location installer
│   ├── uniselv-resman.php          # Main hook registrations & view controllers
│   ├── api_client.php              # PHP UNIX domain socket client
│   ├── install.php                 # Lifecycle activation script
│   ├── deactivate.php              # Lifecycle deactivation script
│   ├── uninstall.php               # Complete purge & cleanup script
│   ├── admin_locations_uniselv-resman.conf # Nginx route for Webuzo Admin
│   ├── enduser_locations_uniselv-resman.conf # Nginx route for Webuzo Enduser
│   ├── assets/
│   │   ├── style.css               # Accessible styling (contrast & explicit labels)
│   │   └── app.js                  # Frontend controllers & SVG chart renderers
│   └── images/
│       └── logo.png                # Plugin brand asset
├── uniselv-resman.zip              # Packaged deployable archive
├── uniselv-resman.zip.sha256       # Cryptographic checksum
├── IMPLEMENTATION-MATRIX.md        # Technical feature & constraint matrix
├── ARCHITECTURE.md                 # In-depth architectural design
├── USER-GUIDE.md                   # Enduser operational guide
├── ADMIN-GUIDE.md                  # Administrator governance guide
└── REVIEW-HANDOFF.md               # Senior engineering audit & verification handoff
```

---

## Installation & Deployment

### Quick Install via Webuzo Admin Panel
1. Download `uniselv-resman.zip`.
2. Navigate to **Webuzo Admin Panel** -> **Plugins** -> **Add New Plugin**.
3. Upload `uniselv-resman.zip` and click **Install**.
4. Click **Activate** to register lifecycle hooks and start the background daemon.

### CLI Deployment (Automation / Root)
```bash
# 1. Extract package to Webuzo plugins directory
unzip -o uniselv-resman.zip -d /usr/local/webuzo/plugins/uniselv-resman

# 2. Run activation hook via Webuzo CLI
/usr/local/emps/bin/php /usr/local/webuzo/cli.php activate-plugin=uniselv-resman/uniselv-resman.php

# 3. Verify daemon health
systemctl status uniselv-resman-agent.service
```

---

## Verification & Testing

Execute the comprehensive automated test suite on the live host:
```bash
python3 test_suite.py
```
Test results and verification metrics are recorded in `TEST-REPORT.json`.

---

## Security & Isolation Principles

1. **Least Privilege IPC:** Webuzo frontend PHP code executes within the unprivileged `webuzo` user context. Commands and queries communicate exclusively over `/run/uniselv-resman/agent.sock` with strict identity verification.
2. **IDOR & Session Defense:** User identity is enforced at the PHP hook level using `$user['username']`. An unprivileged user cannot forge requests to inspect or stop processes belonging to other accounts.
3. **No Direct Root Shells:** The agent daemon exposes strictly parameter-validated action endpoints; arbitrary shell commands cannot be injected over IPC.
4. **Credential Redaction:** Process lists, command arguments, and export dumps scrub all database passwords, authentication tokens, and user credentials.

---

## Developer & Author

- **Name:** Refat Rahman
- **Website:** [refat.ovh](https://refat.ovh)
- **GitHub:** [@refatbd](https://github.com/refatbd)
- **Telegram:** [@refatbd](https://t.me/refatbd)
- **Facebook:** [rjrefat](https://www.facebook.com/rjrefat/)
- **Instagram:** [@refat_official](https://www.instagram.com/refat_official)

