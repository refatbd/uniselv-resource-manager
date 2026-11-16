# UNISELV Resource Manager — Universal Deep Audit Matrix & Defect Tracker

This document serves as the single source of truth for the recursive, loop-driven visual, layout, and theme audit across all pages, subpages, nested subtabs, hidden conditional states, and modals for both **Light** and **Dark** themes.

**Audit Verification Standards:**
1. **Light Mode Parity:** Clean white/off-white surfaces, crisp slate borders, readable slate typography (WCAG AA/AAA).
2. **Dark Mode Immunization:** Zero rogue white/light backgrounds (e.g. `#ecfdf5`, `#ffffff`), deep slate surfaces, readable mint/slate typography (WCAG AAA).
3. **Typography & Word-Wrapping:** No mid-word breaks (`word-break: normal`), proper column `min-width`, zero text overflowing card boundaries.
4. **Alignment & Dimensions:** Standardized 34px-38px control heights (`.uniselv-cpanel-btn`, `.uniselv-cpanel-select`, `.uniselv-btn`), flexbox centering, no awkward white space or collapsed grid columns.
5. **Dynamic / Hidden States:** Dropdown changes, ajax test results, modal overlays, empty vs populated states.

---

## 1. Admin Panel Audit Surface Matrix

| ID | Screen / Component / State | Trigger / Conditions | Light Mode | Dark Mode | Typography & Wrap | Alignment & Sizing | Verification Status |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **A01-1** | `#overview` — Telemetry Header | Default Load | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **A01-2** | `#overview` — 4 Circular Gauges | Default Load & SVG Waves | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **A01-3** | `#overview` — Top Consumers Table | Default Load (Active vs Empty) | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **A01-4** | `#overview` — Grant Boost Action | Click `Grant Boost` button | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **A02-1** | `#accounts` — Account Search Filter | Input text & Empty Match | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **A02-2** | `#accounts` — 25 Tenant Accounts Table | Table listing & badges | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **A02-3** | `#accounts` — Table Pagination | Page 1, 2, Next, Prev | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **A02-4** | `#accounts` — Boost Modal (`uniselv-override-modal`) | Click `Boost` button | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **A02-5** | `#accounts` — Bottom Cards (Boost Form & Bulk Sync) | Bottom of `#accounts` | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **A03-1** | `#analytics` — Subtab 1: Current Usage (Header & Selectors) | Timeframe select & Refresh | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **A03-2** | `#analytics` — Subtab 1: Account Total & 8 Charts | 8 SVG charts & hover tooltips | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **A03-3** | `#analytics` — Subtab 1: Hourly Usage Breakdown Table | Pagination & Sort | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **A03-4** | `#analytics` — Subtab 1: Active Processes Card | Populated vs Empty State | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **A03-5** | `#analytics` — Subtab 2: Snapshots Toolbar | Date & Snapshot ID Selectors | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **A03-6** | `#analytics` — Subtab 2 -> Sub-subtab: Process list | Default active view | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **A03-7** | `#analytics` — Subtab 2 -> Sub-subtab: Database Queries | Click `Database Queries` | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **A03-8** | `#analytics` — Subtab 2 -> Sub-subtab: HTTP Queries | Click `HTTP Queries` | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **A04-1** | `#audit` — Configured vs Effective Limits Table | Default Load | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **A04-2** | `#audit` — Automatic PHP Runtime Capacity Table | Leased & Idle Grants | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **A05-1** | `#goldenshield` — Governor Status & 4 Metric Cards | Default Load | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **A05-2** | `#goldenshield` — Escaped Process Audit Alert | Alert Banner | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **A05-3** | `#goldenshield` — Modal 1 (`uniselv-golden-modal`) Default | Click `Reconfigure` | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **A05-4** | `#goldenshield` — Modal 1 Hidden State (`#golden-manual-fields-modal`) | Select `Advanced Manual Mode` | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **A05-5** | `#goldenshield` — Modal 2 (`uniselv-restore-modal`) | Click `Restore Backup` | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **A05-6** | `#goldenshield` — Bottom Policy Checkpoint Card | Select Checkpoint row | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **A06-1** | `#capacity` — 4 Risk Level & Commit Ratio Cards | Default Load | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **A06-2** | `#capacity` — Observed 24h Peak Telemetry Cards | Historical Maxima | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **A07-1** | `#reports` — Schedule Configuration & Cadence | Dropdown & Save Settings | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **A07-2** | `#reports` — Generate Report Now Dynamic State | Click `Generate Report Now` | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **A07-3** | `#reports` — Reports History Table & View Summary | Row actions & badges | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **A08-1** | `#integrations` — Branding & Localization Settings Card | Left Column Form Inputs | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **A08-2** | `#integrations` — Billing Package Mappings Card | Table & Add/Update Form | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **A08-3** | `#integrations` — Webhook Integration Endpoint Card | Code Info Snippet | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **A08-4** | `#integrations` — Role-Level Baselines Table (B04) | Word Wrap & Column Widths | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **A08-5** | `#integrations` — Granular Account Overrides Table (B04) | Word Wrap, Badges & Spacing | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **A09-1** | `#auditlog` — Search, Action Filter & Clear Log | Controls Toolbar | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **A09-2** | `#auditlog` — Audit History Table & Badges | 20 rows & pagination | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **A09-3** | `#auditlog` — View Details Triggered State | Click `View Details` | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **A10-1** | `#openswoole` — Section 1: Automation & Isolation Directives | Checkboxes & Inputs | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **A10-2** | `#openswoole` — Section 2: Verification Console & Account Select | Dropdowns & Launch Snippet | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **A10-3** | `#openswoole` — Section 2: Dynamic Readiness Check Card | Click `Check PHP Readiness` | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **A10-4** | `#openswoole` — Section 2: Live Self-Test Dynamic Console | Click `Run Live Self-Test` | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **A10-5** | `#openswoole` — Section 3: Installed PHP Extensions Table | Disable & Rebuild Buttons | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **A10-6** | `#openswoole` — Section 4: Plan-Level Resource Budgets Table | Worker Limits & Apply | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **A10-7** | `#openswoole` — Section 5: Account Enforcement & Activity Table | Overrides & Test/Cmd | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **A10-8** | `#openswoole` — Section 6 & 7: Live Processes & Audit Events | Table logs & empty states | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **A11-1** | `#platform` — Section 1: OS Build & Toolchain Preflight | Status pills & build buttons | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **A11-2** | `#platform` — Section 1B: Chrome Browser Engine Governance | Toggle, Smoke Test, Table | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **A11-3** | `#platform` — Section 2: Laravel Stack & Supervisor | Deactivate/Restart/Test | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **A11-4** | `#platform` — Section 3: Redis ACL & Dedicated Port Registry | Port Registry & ACL actions | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **A11-5** | `#platform` — Section 4: Node/Python/Watchdog Containment | Limit inputs & save button | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **A11-6** | `#platform` — Section 5: App Log Bloat & Inode Watchdog | Log table & Trim actions | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **A11-7** | `#platform` — Section 6: Policy Migration (Export/Import) | JSON textarea & Preview | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **A12-1** | `#health` — PHP Runtime Registration Card | Table & Refresh button | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **A12-2** | `#health` — Runtime Governance Evidence & Lifecycle Table | Retire Runtime actions | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **A12-3** | `#health` — Governance Accordions (Drift, Coverage, Recovery) | Click to Expand Details | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **A12-4** | `#health` — System Settings & Feature Governance | Toggles & Save button | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **A12-5** | `#health` — Telemetry Storage & Retention Policy | Inputs, Bar, Prune/Purge | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **A12-6** | `#health` — Background Daemon Health & Maintenance Mode | Status metrics & Toggle | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **A13-1** | `#help` — Documentation Header & Search | Search input & cards | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **A13-2** | `#help` — 8 Category Filter Pills | Click each pill to filter | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **A13-3** | `#help` — Code Blocks & Copy Command Buttons | Code snippets & Copy | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **A13-4** | `#help` — Architecture Table & Author Profile Card | Bottom cards & links | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |

---

## 2. Enduser Panel Audit Surface Matrix

| ID | Screen / Component / State | Trigger / Conditions | Light Mode | Dark Mode | Typography & Wrap | Alignment & Sizing | Verification Status |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **E01-1** | `#dashboard` — Header Telemetry Bar & Controls | Theme Switcher & Export | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **E01-2** | `#dashboard` — 4 Circular Telemetry Gauges | Gauge arcs & wave animation | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **E01-3** | `#dashboard` — 8 Modern Application Service Cards | 8 cards & action buttons | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **E01-4** | `#dashboard` — Config Modal (`uniselv-service-config-modal`) | Click `Config & Fields` | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **E01-5** | `#dashboard` — Bottom Cards (PHP Workers, Chrome Hub) | Bottom of `#dashboard` | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **E02-1** | `#processes` — Timeframe Toolbar & Refresh | Presets & 34px buttons | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **E02-2** | `#processes` — Account Total & 8 Resource Charts | Charts & legends | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **E02-3** | `#processes` — Hourly Usage Table & Pagination | Rows, badges, pagination | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **E02-4** | `#processes` — Active Processes Table & Kill Tasks Button | Process list & Stop buttons | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **E02-5** | `#processes` — OpenSwoole Budget Card & Copy Command | Octane command & refresh | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **E03-1** | `#history` — Historical Time Range Presets | Last Hour, Today, 7d, 30d | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **E03-2** | `#history` — 4 Telemetry Sparkline Charts | CPU, RAM, Tasks, Disk | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **E03-3** | `#history` — Interactive Range Sliders | Drag slider & timestamp | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **E03-4** | `#history` — Historical Samples Table & Pagination | Rows & pagination | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **E04-1** | `#snapshots` — Process list Subtab | PID, CMD, CPU, MEM | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **E04-2** | `#snapshots` — Database Queries Subtab | Empty state & slow queries | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **E04-3** | `#snapshots` — HTTP Queries Subtab | Log console & word-wrap | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **E04-4** | `#snapshots` — Snapshots Date & ID Selectors | 34px controls & Prev/Next | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **E05-1** | `#notifications` — Filters & Mark All Read | Dropdown & buttons | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **E05-2** | `#notifications` — Events & Incident Log Table | Rows, icons, timestamps | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **E05-3** | `#notifications` — UNREAD & WARNING Badges | High contrast dark badges | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **E06-1** | `#services` — 8 Dedicated Services & Ports | Supervisor, Octane, Redis | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **E06-2** | `#services` — Redis ACL Isolation Card | Rotate password & Test | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **E06-3** | `#services` — Chrome Hub & Live Smoke Test | Dynamic test card | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **E07-1** | `#help` — 8 Architecture Cards & Guides | Guides & copy snippets | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **E07-2** | `#help` — Category Filter Pills | Pill buttons | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |
| **E07-3** | `#help` — Author & Developer Profile Card | Social links & icons | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS | VERIFIED_PASS |

---

## 3. Modals & Dynamic Standalone Systems

| ID | Modal / Dynamic System | Mount Element | Light Mode | Dark Mode | Action / Test Evidence | Status |
| :--- | :--- | :--- | :---: | :---: | :--- | :---: |
| **M01** | `UniselvModal.confirm` Confirmation Dialog | `document.body` | VERIFIED_PASS | VERIFIED_PASS | `.uniselv-modal-confirm` text contrast `#101714` on `#72BDAA` (8.5:1 ratio) | VERIFIED_PASS |
| **M02** | `UniselvNotify` Toast System | `document.body` | VERIFIED_PASS | VERIFIED_PASS | Synchronized theme attribute, `#17211D` dark card, `#E8EFEB` text, emerald/crimson icons | VERIFIED_PASS |
| **M03** | Service Config Modal (`#uniselv-service-config-modal`) | DOM Container | VERIFIED_PASS | VERIFIED_PASS | Form controls, input backgrounds, and copy triggers | VERIFIED_PASS |
| **M04** | Override / Boost Modal (`#uniselv-override-modal`) | DOM Container | VERIFIED_PASS | VERIFIED_PASS | Dropdown inputs, memory slider, submit button | VERIFIED_PASS |
| **M05** | Golden Shield Reconfig Modal (`#uniselv-golden-modal`) | DOM Container | VERIFIED_PASS | VERIFIED_PASS | Advanced mode dynamic fields, range inputs, submit | VERIFIED_PASS |
| **M06** | Audit Details JSON Viewer | Modal Backdrop | VERIFIED_PASS | VERIFIED_PASS | `#0f172a` monospace code container, copy button | VERIFIED_PASS |
