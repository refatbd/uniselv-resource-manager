# UNISELV Resource Manager - Enduser Guide

Welcome to the **UNISELV Resource Manager** for Webuzo. This guide explains how to monitor, diagnose, and optimize your hosting account's resource usage from the Webuzo Enduser Panel.

---

## Accessing the Interface

1. Log in to your Webuzo Enduser Panel (`https://your-domain.com:2003/`).
2. In the navigation menu, search for **Resource Manager** or navigate to `index.php?act=uniselv-resman`.

---

## 1. Dashboard Tab

The **Dashboard** gives you a real-time, high-level overview of your account's health and resource consumption with live animated telemetry.

### Modern Visual Dashboard & Wave Sparklines
- **Card Icon Badges:** Circular colored badge icons (CPU microchip in blue, Memory stack in purple, I/O drive in teal, Tasks cog in amber) provide instant visual differentiation.
- **Wave Sparklines:** Each resource card includes an SVG wave sparkline with vertical gradient fills displaying recent throughput dynamics.
- **Modern Non-Blocking Alerts & Modals:**
  - Traditional blocking browser alert dialogs are replaced with modern, non-blocking toast notifications (`UniselvNotify`) featuring progress timers, auto-dismiss, and icon badges.
  - Dangerous actions (such as terminating runaway processes) trigger centered confirmation modals (`UniselvModal.confirm`) with backdrop blur and distinct action styling.

### Live Animated Telemetry (3-Second Polling)
- **Real-Time Auto-Refresh:** The dashboard continuously polls live telemetry every 3 seconds in the background without requiring manual browser page refreshes.
- **Pulsating Live Badge:** A green pulsating indicator (`LIVE AUTO-REFRESH (3s)`) signals an active, healthy telemetry stream.
- **Smooth Bezier Transitions:** Resource gauge progress bars dynamically animate their width and color using cubic-bezier curves (`0.6s ease-out`).
- **Dynamic Status Badges:**
  - **NORMAL (Green):** Resource consumption is well within account quota bounds.
  - **LIMIT EXCEEDED (Red):** Resource consumption has reached or exceeded 100% of the assigned plan limit, prompting immediate visual awareness.
  - **Card Highlight Pulse:** Whenever an elevated usage sample arrives, the affected resource card briefly pulses to highlight the change.

### Resource Gauges
- **CPU Usage:**
  - **Core Semantics:** In UNISELV Resource Manager, **100% CPU represents one full physical CPU core**.
  - **Dual Display:** The gauge displays both your **Core-Equivalent Usage** and your **Percentage of Plan Allowance**.
  - *Example:* If your plan allocates 50% CPU (0.5 core) and your current scripts are consuming 50.22%, your Core-Equivalent Usage is **50.22% (0.5 Core)** and your Allowance Utilization is **100.4%** (`50.22 / 50.0 * 100`).
- **Memory (RAM & Cache):**
  - Displays your total accounted cgroup memory (`memory.current`) against your plan limit (e.g. 1024 MiB).
  - **Memory Composition:**
    - **Anonymous RAM (`anon`):** Active process heap, PHP variables, script allocations. This memory cannot be discarded without swapping.
    - **Page Cache (`file`):** Disk files cached in memory by Linux for fast read access. The operating system will automatically free pagecache if your scripts need more anonymous RAM.
    - **Swap Memory:** Secondary memory used if RAM is under pressure.
- **I/O Throughput & IOPS:**
  - Real-time disk read and write throughput in KB/s or MB/s.
  - Active I/O operations per second (IOPS).
- **Task & Thread Usage:**
  - Number of active processes and threads currently running under your account vs your plan's `TasksMax` limit.


---

## 2. Current Usage & Process Inspector Tab

The **Current Usage** tab allows you to inspect active workloads running under your user account and take controlled action against runaway scripts.

### Process List
- Displays all PHP-FPM worker processes, scheduled cron tasks, and CLI commands executing as your user.
- Shows individual process PID, CPU percentage, memory consumption, execution runtime, and command name.
- **Privacy & Security Redaction:** Command arguments containing database passwords, API tokens, or secrets are automatically redacted with `[REDACTED]`.

### Controlled Process Stop
If a PHP script or cron job is stuck in an infinite loop or consuming excessive resources, you can terminate it safely:
1. Locate the process in the table.
2. Click the **Stop Process** button.
3. Confirm the termination prompt.

> [!IMPORTANT]
> **PID Reuse Protection:** The system automatically verifies both your user ownership and the process's exact start-time timestamp (`/proc/<pid>/stat`). If a process finishes and the operating system recycles that PID to a different process before your request arrives, the system will securely refuse the termination to prevent accidental kills.

---

## 3. History Tab

The **History** tab provides interactive historical telemetry to understand trends over time.

### Available Time Ranges
- **Last 1 Hour:** High-resolution 10-second data points.
- **Today:** Rolling data since midnight.
- **Last 24 Hours:** Day-long utilization profile.
- **Last 7 Days:** Weekly trend analysis.
- **Last 30 Days:** Monthly capacity profile.

### Interactive SVG Charts
- Rendered natively in your browser with zero external dependencies.
- **Historical Limit Line:** A dashed red reference line illustrates your plan's limit over time, making it easy to identify when temporary boosts were active.
- **Average vs Peak:** Distinguishes smooth average resource load from sudden instantaneous spikes.

---

## 4. Snapshots & Diagnostics Tab

When an account experiences significant resource pressure (such as CPU throttling or near-memory exhaustion), the background agent automatically captures a **Diagnostic Snapshot**.

### What a Snapshot Contains
- **System Watermark:** Exact timestamp and resource metrics at the time of the event.
- **Process Hierarchy:** The top processes active at that exact moment.
- **Sanitized HTTP Traces:** The latest incoming web requests to your domain (URL paths, HTTP status codes, execution times).
- **Database Query Traces:** Slow queries executing under your database user.

> [!NOTE]
> Diagnostic snapshots are diagnostic aids. Shared database activity and HTTP traffic are correlated based on account mapping and timing, rather than direct kernel cgroup attribution.

---

## 5. Notifications & Upgrade Recommendations

### Automated Event Alerts
The system highlights key resource events:
- **CPU Throttling:** Indicates your processes demanded more CPU cycles than your plan quota permitted during a scheduling window.
- **Memory Pressure & OOM Events:** Alerts you if Linux terminated a process due to exceeding memory limits (`Out Of Memory`).
- **Task Limit Exceeded:** Alerts you if your cron jobs or PHP processes hit the maximum concurrency limit.

### Optimization & Upgrade Guidance
- **Sustained Load vs Transient Spikes:** The system will never recommend a plan upgrade based on a single brief spike. Recommendations are only issued if your account experiences sustained pressure over multiple days.
- **Actionable Optimization Advice:** Practical tips for caching, database index optimization, and background worker queue scheduling.

---

## 6. Privacy-Safe Support Export

If you need help from your hosting provider:
1. Navigate to the **Support Export** section.
2. Click **Generate Privacy-Safe Export**.
3. Download the resulting JSON summary.

All user passwords, sensitive configuration keys, session tokens, and file system paths are completely scrubbed before the file is generated, ensuring your private data remains secure.

---

## 7. Interactive Help & About Guide (Enduser Tab 6)

The **Help & About** tab provides an integrated guide directly within the Enduser Panel:
- **Instant Search:** Type questions or search terms like `slow`, `503`, `memory`, `tasks`, or `cpu` into the search box to filter topics in real time.
- **Category Filter Pills:** Switch between *Getting Started*, *Features & Tools*, *Understanding Metrics*, *Practical Guides*, *FAQ & Diagnostics*, and *About*.
- **Direct Contextual Links:** Click the **Help Guide** pill in the top header to jump straight to practical guides and instructions on interpreting your real-time meters.

