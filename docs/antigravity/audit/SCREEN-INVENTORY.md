# UNISELV Resource Manager — Complete Screen & Surface Inventory

> Stage A Deliverable — Comprehensive UI Surface & Interaction Inventory
> Verified against repository source files (`plugin/uniselv-resman.php`, `assets/app.js`, `views/`) and live Webuzo staging panels.

---

## 1. Webuzo Admin Panel Surfaces (`act=uniselv-resman`)

Accessed by Server Administrators and Platform Operators. Entry hook: `uniselv_resman_admin()`.

### 1.1 Shell & Global Header
- **Brand Header:** Plugin icon/logo, Product title (`UNISELV Resource Manager`), Subtitle (`Server telemetry and resource limits`).
- **Telemetry Freshness Indicator:** Badge `#admin-telemetry-freshness` (`Live telemetry`, `Waiting for telemetry`, `Stale telemetry`, `Telemetry offline`).
- **Tools Menu:** Language selector (`#uniselv-locale-selector`: English / Bengali), Documentation deep-link, Help & About modal trigger.
- **Refresh Action:** Immediate manual telemetry refresh button (`UniselvResMan.loadAdminOverview()`).

### 1.2 Administrative Tabs
| Tab Identifier | Tab Label | Primary Purpose | Key Components & DOM Hooks |
|---|---|---|---|
| `tab-overview` | **Server Overview** | Real-time physical host capacity and system headroom | Host CPU gauge (`#uniselv-arc-cpu`), RAM gauge (`#uniselv-arc-mem`), I/O gauge (`#uniselv-arc-io`), Task threads gauge (`#uniselv-arc-tasks`), Hardware spec chips, 1m/5m/15m load averages, Golden Shield allocation ceiling, Safety reserves banner (`#uniselv-active-boosts-banner`). |
| `tab-accounts` | **All Accounts** | Tenant resource consumption inventory & drift management | Account search bar (`#uniselv-account-search`), Tenant inventory table (Username, Plan, CPU core-eq %, Allowance %, RAM used/limit, Tasks, Throttling, OOM score, FastCGI status, Actions), Temporary boost modal trigger, Sync drift action. |
| `tab-analytics` | **User Analytics & Snapshots** | Deep-dive telemetry inspection and incident analysis | Tenant selector dropdown (`#admin-user-selector`), Historical charts (CPU, RAM, EP, I/O, Faults), Timeframe selector (today, 24h, 7d, 30d), Incident snapshots timeline, Incident details viewer. |
| `tab-audit` | **Configured vs Effective Audit** | Drift detection between Webuzo database plans and Linux kernel cgroups | Drift comparison table, Status pills (`Synchronized`, `Drift Detected`), Bulk drift reconciliation action, Individual account sync trigger. |
| `tab-goldenshield` | **Golden Shield Governance** | System-wide kernel protection and resource reservation | Customer allocation ceiling cards, Reserved capacity meters, Cgroups v2 weight distribution controls, Auto-mitigation status. |
| `tab-capacity` | **Capacity Planning & Oversell** | Hosting server density and capacity modeling | Oversell ratio calculation cards, Memory headroom forecast, High-watermark trends, Recommended allocation caps. |
| `tab-reports` | **Scheduled Reports** | Automated operational report delivery | Report schedule configurations, Recipient email lists, Format selectors (PDF / HTML / JSON), Historical report archive list. |
| `tab-integrations` | **Branding & Localization** | Reseller/Enterprise white-label settings | Brand name input, Logo URL, Accent primary color picker, Support URL, Default locale selector, Documentation URL override. |
| `tab-auditlog` | **Audit Log** | Immutable administrator action ledger | Filterable event table (Timestamp, Actor, Target tenant, Action type, Old/New state payload, Status). |
| `tab-openswoole` | **OpenSwoole Governance** | Multi-PHP daemon & asynchronous worker supervision | Multi-PHP runtime status table, OpenSwoole worker supervisors, FastCGI admission status, Graceful reload actions. |
| `tab-platform` | **Platform Operations & Laravel Suite** | Enterprise runtime suites (8 managed services) | Redis ACL tenant isolation, Laravel Horizon supervisors, Reverb WebSocket daemons, Cron task schedulers, Headless Chrome engine sandbox, FastCGI admission queues. |
| `tab-health` | **System Health** | Daemon agent status and database integrity | `uniselv-resman-agent.service` status pill, SQLite database size and WAL status, UNIX socket response latency, Diagnostic run trigger. |
| `tab-help` | **Help & Documentation** | Embedded knowledge base & operational guide | Filterable guide topics (`quickstart`, `cgroups`, `openswoole`, `troubleshooting`), Markdown view container. |

---

## 2. Webuzo Enduser Panel Surfaces (`act=uniselv-resman`)

Accessed by Individual Hosting Tenants and Scoped Resellers. Entry hook: `uniselv_resman_enduser()`.

### 2.1 Shell & Header
- **Brand Header:** Customized brand logo, Brand name, Authenticated tenant identification (`Account: <username> (<domain>) • Assigned Plan: <plan>`).
- **Telemetry Freshness Badge:** `#uniselv-telemetry-freshness`.
- **Tenant Actions:** Support ticket link, Embedded Help guide trigger, Support report export button (`#uniselv-export-btn`).

### 2.2 Enduser Tabs
| Tab Identifier | Tab Label | Primary Purpose | Key Components & DOM Hooks |
|---|---|---|---|
| `tab-dashboard` | **Dashboard** | Personal resource consumption vs plan quotas | 4 Resource Gauge Cards (CPU Core Usage vs Plan Allowance %, RAM Breakdown [Total cgroup, Anon, Cache, Swap], Disk I/O Throughput, Active Tasks & Thread limits), Recent resource events feed, FastCGI worker admission status. |
| `tab-processes` | **Current Usage & Processes** | Active process inspection and self-service process control | Process inventory table (PID, CPU %, Memory, Execution duration, Redacted command-line), Safe process kill button with confirmation modal. |
| `tab-history` | **Historical Charts** | Historical consumption trends over customizable intervals | Native SVG line charts (CPU core-equivalent, Plan allowance, Memory usage, Virtual memory [RAM+Swap], Disk I/O throughput, Entry processes [EP], Faults/throttles), Time window selectors (1h, 6h, 24h, 7d). |
| `tab-snapshots` | **Snapshots** | High-pressure incident telemetry capture | Incident event list (Timestamp, Trigger reason, Peak CPU/RAM, Process count), Detailed snapshot inspect modal (`#uniselv-snaps-count-badge`). |
| `tab-notifications` | **Notifications & Events** | Tenant-facing alerts and resource warnings | Notification list with severity tags (`warning`, `critical`, `info`), Mark-as-read/acknowledge action buttons (`#uniselv-notif-count-badge`). |
| `tab-services` | **App Services & Tools** | Permitted tenant runtime services | Tenant-scoped Laravel worker status, Redis database isolate status, Cron scheduler overview, Chrome headless sandbox permissions. |
| `tab-help` | **Help Guide** | Self-service troubleshooting and documentation | Account resource guide, cgroup limit explanations, Support contact links. |

---

## 3. Shared Overlays, Modals & Dynamic UI States

- **Global Toast Container:** `#uniselv-toast-container` (Supports `success`, `error`, `warning`, `info` notification banners with auto-dismiss).
- **Process Termination Confirmation Modal:** Modal dialog with backdrop, target process details, danger alert, and explicit confirmation/cancellation buttons.
- **Temporary Resource Override Modal:** Admin modal to assign temporary CPU/RAM boosts with mandatory reason, duration, and auto-expiry timestamp.
- **Snapshot Detail Modal:** Displays frozen process state, memory metrics, and system load at the time of an alert trigger.
- **Mobile Navigation Dropdown:** `#uniselv-mobile-section` (Compact section selector on viewports `< 768px`).
- **Administrative Overflow Menu:** `#uniselv-more-sections` (Collapsible dropdown handling administrative tabs that exceed horizontal viewport space).
