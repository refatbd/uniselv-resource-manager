# UNISELV Resource Manager - Architecture & Technical Design

This document details the internal architecture, security boundary model, telemetry calculation mechanisms, and lifecycle integration of the UNISELV Resource Manager for Webuzo.

---

## 1. System Architecture & Component Interaction

The solution is partitioned into three distinct tiers to uphold the principle of least privilege:

```
+-----------------------------------------------------------------------------------------+
|                                    Presentation Tier                                    |
|                                                                                         |
|   Webuzo Admin UI (`act=uniselv-resman`)           Webuzo Enduser UI (`act=uniselv-resman`) |
|   - Server aggregate overview                      - Live resource gauges               |
|   - 7-Account inventory                            - Core-equivalent CPU & Allowance    |
|   - Plan audit & synchronization                   - Memory breakdown (anon/cache/swap) |
|   - Expiring temporary overrides                   - Process inspector & safe stop      |
|   - Billing adapters (WHMCS/Blesta)                - Sanitized diagnostic export        |
+-----------------------------------------------------------------------------------------+
                                             |
                                             v
+-----------------------------------------------------------------------------------------+
|                                  Plugin Controller Tier                                 |
|                                                                                         |
|   Webuzo PHP Hook Environment (`/usr/local/webuzo/plugins/uniselv-resman/`)            |
|   - Runs under unprivileged `webuzo` user via EMPS FastCGI                              |
|   - `uniselv-resman.php`: Registers `admin_act` and `enduser_act` hooks                 |
|   - `api_client.php`: Communicates strictly over local UNIX Domain Socket               |
|   - Enforces calling context: extracts authenticated `$user['username']` from session  |
+-----------------------------------------------------------------------------------------+
                                             |
                          UNIX Domain Socket: `/run/uniselv-resman/agent.sock`
                          JSON Request / Response (Non-blocking, Timeout 10s)
                                             v
+-----------------------------------------------------------------------------------------+
|                               Privileged Daemon Tier                                    |
|                                                                                         |
|   Systemd Service: `uniselv-resman-agent.service` (Isolated Cgroup)                     |
|   - Execution Context: Root with bounded capabilities (MemoryMax=64M, TasksMax=32)      |
|   - `collector.py`: High-resolution cgroups v2 delta accounting (10s interval)          |
|   - `ipc_server.py`: Request router with caller authorization & IDOR isolation          |
|   - `schema.py`: SQLite WAL bounded storage (`/var/lib/uniselv-resource-manager/`)      |
+-----------------------------------------------------------------------------------------+
                         |                                           |
                         v                                           v
+---------------------------------------------------+  +----------------------------------+
|               Kernel Cgroups v2                   |  |      Native Webuzo / Systemd     |
|  - `/sys/fs/cgroup/<uid>.slice`                   |  |  - `/var/webuzo/cgroups/<plan>`  |
|  - `/sys/fs/cgroup/golden.slice/golden-<uid>.slice|  |  - `/bin/webuzo --api`           |
|  - `cpu.stat`, `memory.current`, `memory.stat`    |  |  - `/etc/systemd/system/*.slice` |
|  - `io.stat`, `pids.current`                      |  |  - `systemctl daemon-reload`     |
+---------------------------------------------------+  +----------------------------------+
```

---

## 2. Privilege Separation & Security Model

### 2.1 Threat Model & Boundary Enforcement
Web interfaces are exposed to external inputs and customer interactions. Running all telemetry and control logic within PHP FastCGI would either require granting the Webuzo web server direct root capabilities (violating least privilege) or running arbitrary `sudo` commands (creating shell injection vectors).

**Our Defensive Architecture:**
1. **Isolated Daemon:** A standalone Python daemon (`uniselv-resman-agent.service`) runs with constrained systemd parameters.
2. **UNIX Socket IPC:** Communication occurs via `/run/uniselv-resman/agent.sock` owned by `root:webuzo` with `0660` permissions. Untrusted network clients cannot access this socket.
3. **No Shell Execution over IPC:** The daemon exposes strictly typed actions (`get_enduser_dashboard`, `stop_enduser_process`, `set_temporary_override`, etc.). There is no generic "exec" or "shell" method.
4. **Mandatory Identity Injection:** The PHP client derives caller identity from Webuzo internal authentication globals (`$user['username']` for endusers, `admin` flag for administrators). Endusers cannot impersonate other accounts or query administrative metrics.

### 2.2 PID Reuse & Process Termination Defense
Allowing users to stop their own runaway scripts is essential for self-service, but naive `kill(pid)` introduces a critical security vulnerability: PID recycling. If a user's process dies and the kernel reassigns that PID to an unprivileged process owned by another user or a system daemon, an unvalidated termination could kill arbitrary processes.

**Protection Algorithm:**
1. When the enduser views the process table, the collector records both `pid` and `start_time` (ticks after system boot from `/proc/<pid>/stat` field 22).
2. When a stop request is issued:
   - The agent reads `/proc/<pid>/status` and verifies `Uid:` matches the target user's UID.
   - The agent reads field 22 of `/proc/<pid>/stat` and verifies it matches the exact `start_time` provided in the request.
   - If `start_time` differs by even 1 tick, the agent rejects the operation with `Security Refusal: Process start time mismatch (PID was recycled)`.
   - Only upon passing both checks is `SIGTERM` (followed by bounded `SIGKILL` if unresponsive) delivered.

---

## 3. Linux Cgroup v2 Telemetry Engine

### 3.1 Kernel Cgroup Discovery
Webuzo generates cgroup slices under `/sys/fs/cgroup/<uid>.slice`. Concurrently, Golden Shield provides isolation via `/sys/fs/cgroup/golden.slice/golden-<uid>.slice`.
To avoid duplicate counting or monitoring dormant slices, `collector.py` implements an active-slice detection algorithm:
- Checks candidate slice paths in order.
- Prioritizes the slice exhibiting active tasks (`pids.current > 0`) or active memory (`memory.current > 0`).

### 3.2 CPU Core-Equivalent & Allowance Normalization
In Linux cgroup v2, CPU usage is tracked via cumulative microseconds in `cpu.stat`:
- `usage_usec`: Total CPU time consumed.
- `user_usec`: User-space execution time.
- `system_usec`: Kernel execution time.
- `nr_periods`: Total scheduling periods elapsed.
- `nr_throttled`: Periods in which tasks were throttled due to quota exhaustion.
- `throttled_usec`: Aggregate duration tasks spent waiting for quota replenishment.

**Mathematical Conversion:**
```
delta_cpu_usec = current_usage_usec - previous_usage_usec
delta_wall_sec = current_timestamp - previous_timestamp

cpu_percent = (delta_cpu_usec / (delta_wall_sec * 1,000,000)) * 100.0
```
- **Semantics:** 100.0% equals exactly 1 full CPU core saturated.
- **Allowance Normalization:**
```
cpu_allowance_percent = (cpu_percent / configured_quota_percent) * 100.0
```
*Example:* An account on the `go` plan has a quota of 50% (0.5 vCPU). If it consumes 35% of a physical core, `cpu_percent` is 35.0% and `cpu_allowance_percent` is `(35 / 50) * 100 = 70.0%`.

### 3.3 Memory Breakdown & Cache Distinction
Process RSS does not represent true account memory impact because it ignores pagecache, shared kernel allocations, and memory under active reclaim.
The collector parses `memory.stat` directly from the account cgroup:
- `mem_current`: Total memory charged to the cgroup (`memory.current`).
- `mem_anon`: Active anonymous memory (heap, stack, private dirty allocations).
- `mem_file`: Memory mapped to disk files (pagecache). Reclaimable under memory pressure.
- `mem_swap`: Account swap usage (`memory.swap.current`).

---

## 4. Golden Shield Headroom & Governance Model

To prevent hosting tenants from exhausting node resources and crashing system daemons (MariaDB, Apache/Nginx, SSH, Cron), UNISELV Resource Manager incorporates the Golden Shield shared aggregate headroom model.

### 4.1 Headroom Scaling Principles
- **No Rigid Single-Core Pinning:** Dedicating a specific core (e.g., Core 0) exclusively to the system leaves system resources underutilized during low load and throttles multi-threaded database bursts.
- **Shared Aggregate Headroom:**
  - For a 4 vCPU server (400% total core capacity):
    - **Customer Hosting Aggregate:** 340% (85% of total capacity).
    - **System & Administration Reserve:** 60% (15% of total capacity).
  - Physical RAM Headroom: 1280 MiB strictly reserved for system stability; customer allocation caps scale accordingly.
  - Overselling hosting packages is permitted administratively, but overselling **never inflates physical safety thresholds**.

---

## 5. Storage & Retention Architecture

Telemetry data is maintained in a local SQLite database with Write-Ahead Logging (WAL) enabled:
- **Location:** `/var/lib/uniselv-resource-manager/resman.sqlite`
- **Tables:**
  - `samples`: 10-second interval telemetry for each active hosting user.
  - `system_metrics`: Node-wide aggregate metrics.
  - `events`: Throttling, OOM terminations, high memory pressure incidents.
  - `snapshots`: High-watermark diagnostic captures with sanitized process trees.
  - `temporary_overrides`: Active and historical plan boosts.
  - `audit_log`: Administrative actions and webhook events.
- **Bounded Retention:**
  - Samples older than 30 days are purged hourly via `DELETE FROM samples WHERE timestamp < ?`.
  - Snapshots older than 14 days are purged hourly.
  - Automated `PRAGMA wal_checkpoint(PASSIVE)` ensures WAL logs do not grow unbounded. Total DB footprint remains strictly under 50 MiB.

---

## 6. External Billing Integration (WHMCS / Blesta)

The agent implements an idempotent webhook ingestion pipeline for external billing platforms:
- **Payload:**
  ```json
  {
    "event": "package_change",
    "account": "ub1",
    "package": "turbo",
    "idempotency_key": "whmcs-inv-94821-step-2"
  }
  ```
- **Deduplication Engine:**
  - Incoming requests verify the `idempotency_key` against `audit_log`.
  - If a matching key was processed within the last 24 hours, the agent skips execution and returns the original cached success response.
  - Eliminates duplicate plan migrations caused by network timeouts or billing gateway retries.
