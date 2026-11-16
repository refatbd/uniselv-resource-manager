# UNISELV Resource Manager — DOM & JavaScript Compatibility Contract

> Stage A Deliverable — Comprehensive DOM Hooks, Global Variables & API Contract Mapping
> Purpose: Guarantee that UI redesign does not break any existing JavaScript behavior, event listeners, or daemon IPC calls.

---

## 1. Critical Preservation Principle

The UI redesign must **strictly preserve or safely alias** every DOM ID, CSS selector, data attribute, and window-scoped global that `plugin/assets/app.js` relies upon. Any modification to markup that deletes or renames these identifiers will cause runtime JavaScript exceptions and silent operational failures.

---

## 2. Global Window Variables & Namespace

| Identifier | Defined In | Consumed By | Semantics |
|---|---|---|---|
| `window.UNISELV_LOCALE` | `uniselv-resman.php` | `app.js` | Active ISO locale code (`"en"` or `"bn"`). |
| `window.UNISELV_TRANSLATIONS` | `uniselv-resman.php` | `app.js` | Key-value translation dictionary for active locale. |
| `window.UniselvResMan` | `app.js` | PHP views & inline handlers | Main controller singleton handling polling, charts, tabs, modals, and API calls. |
| `window.UniselvToast` | `app.js` | `UniselvResMan` & error handlers | Toast notification controller. |

---

## 3. Mandatory DOM IDs Inventory

### 3.1 Shell & Navigation Controls
- `#uniselv-toast-container`: Root container for dynamic toasts.
- `#uniselv-mobile-section`: Dynamically injected `<select>` for mobile viewports.
- `#uniselv-more-sections`: Dynamically injected `<select>` for Admin tab overflow.
- `#uniselv-locale-selector`: Language selection dropdown.
- `#uniselv-account-search`: Real-time text filter for All Accounts table.
- `#admin-user-selector`: Tenant filter in Analytics view.
- `#uniselv-usage-timeframe`: Historical telemetry interval selector.
- `#uniselv-export-btn`: Support report trigger button.

### 3.2 Telemetry & State Badges
- `#admin-telemetry-freshness`: Admin freshness status badge.
- `#uniselv-telemetry-freshness`: Enduser freshness status badge.
- `#uniselv-active-boosts-banner`: Container for active Golden Shield override warnings.
- `#uniselv-snaps-count-badge`: Enduser snapshots count pill.
- `#uniselv-notif-count-badge`: Enduser notifications count pill.

### 3.3 Metric Value Elements (Must Preserve)
| Metric Domain | Value Element ID | Secondary / Subtitle ID | Gauge Arc ID | Thumb Rotation ID | Wave Graphic ID |
|---|---|---|---|---|---|
| **CPU** | `#uniselv-val-cpu` | `#uniselv-sub-cpu` / `#uniselv-core-cpu` | `#uniselv-arc-cpu` | `#uniselv-thumb-rot-cpu` | `#uniselv-wave-cpu` |
| **Memory** | `#uniselv-val-mem` | `#uniselv-sub-mem` | `#uniselv-arc-mem` | `#uniselv-thumb-rot-mem` | `#uniselv-wave-mem` |
| **I/O** | `#uniselv-val-io` | `#uniselv-sub-io` | `#uniselv-arc-io` | `#uniselv-thumb-rot-io` | `#uniselv-wave-io` |
| **Tasks** | `#uniselv-val-tasks` | `#uniselv-sub-tasks` | `#uniselv-arc-tasks` | `#uniselv-thumb-rot-tasks` | `#uniselv-wave-tasks` |

### 3.4 Container & View Panels
- Admin Tab Panels: `#tab-overview`, `#tab-accounts`, `#tab-analytics`, `#tab-audit`, `#tab-goldenshield`, `#tab-capacity`, `#tab-reports`, `#tab-integrations`, `#tab-auditlog`, `#tab-openswoole`, `#tab-platform`, `#tab-health`, `#tab-help`.
- Enduser Tab Panels: `#tab-dashboard`, `#tab-processes`, `#tab-history`, `#tab-snapshots`, `#tab-notifications`, `#tab-services`, `#tab-help`.

---

## 4. API Actions & IPC Client Contract

All asynchronous UI interactions communicate through Webuzo's dispatcher via `index.php?act=uniselv-resman&action=<action>`, which invokes `UniselvApiClient::call($action, $params, $user, $isAdmin)`.

| Action Name | Invoked By (`app.js`) | Payload Parameters | Response Semantics |
|---|---|---|---|
| `get_admin_overview` | `loadAdminOverview()` | `{}` | Host hardware specs, load averages, aggregate telemetry, Golden Shield policy. |
| `get_admin_accounts` | `loadAdminAccounts()` | `{search, page, limit}` | Array of tenant accounts with plan limits, live consumption, drift flags. |
| `get_admin_audit_limits` | `loadAdminAudit()` | `{}` | Side-by-side array of configured vs effective cgroups kernel limits. |
| `sync_account_limits` | `syncAccount(user)` | `{target_user}` | Re-applies Webuzo plan limits directly to `/sys/fs/cgroup/`. |
| `get_user_analytics` | `loadUserAnalytics(user)` | `{user, timeframe}` | Historical time-series metrics array for SVG chart rendering. |
| `get_agent_health` | `loadSystemHealth()` | `{}` | Daemon PID, memory, socket latency, SQLite file size and status. |
| `get_golden_shield_status` | `loadGoldenShield()` | `{}` | Safety reserve calculations and cgroup weights. |
| `get_platform_services_status` | `loadPlatformServices()` | `{}` | 8 platform services status (Redis ACL, Horizon, Reverb, etc.). |
| `get_enduser_dashboard` | `loadEnduserDashboard()` | `{}` | Authenticated tenant's current usage vs assigned quota. |
| `get_enduser_processes` | `loadEnduserProcesses()` | `{}` | Redacted active process table for authenticated user. |
| `kill_enduser_process` | `terminateProcess(pid)` | `{pid}` | Strictly terminates tenant's own process; rejects foreign PIDs. |
| `get_enduser_snapshots` | `loadEnduserSnapshots()` | `{limit}` | Historical high-pressure telemetry snapshots. |
| `get_enduser_notifications` | `loadEnduserNotifications()` | `{}` | Alert events with severity and timestamp. |
| `export_support_report` | `exportReport()` | `{}` | Anonymized JSON/text diagnostic bundle for support tickets. |

---

## 5. JavaScript DOM Event Handlers

The following functions are wired to interactive elements via event listeners or inline triggers:
- `UniselvResMan.switchTab(tabId)`
- `UniselvResMan.setLocale(localeCode)`
- `UniselvResMan.openHelpTopic(topicSlug)`
- `UniselvResMan.loadAdminOverview()`
- `UniselvResMan.exportReport()`
- `UniselvResMan.filterAccounts(query)`
- `UniselvResMan.syncAccount(username)`
- `UniselvResMan.promptKillProcess(pid, commandSummary)`

**Compatibility Requirement:** In Phase 3 and Phase 4, the new theme switcher control will be added to the header as an accessible button invoking `UniselvResMan.toggleTheme()` without altering or disturbing any existing action triggers.
