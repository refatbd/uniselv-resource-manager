# UNISELV Resource Manager — Precision Operations Console Design Proposal

> Stage B Deliverable — Unified Visual Direction, Token Specification & Rollout Plan
> Visual Thesis: **Precision Operations Console** (Warm quiet light / Graphite ink dark)

---

## 1. Information Architecture Proposal

### 1.1 Webuzo Admin Panel IA Restructuring
To resolve the flat 13-tab visual crowding issue, Admin surfaces are structured into 4 logical operational clusters with a streamlined segmented navigation bar:

1. **Monitoring & Fleet Telemetry:**
   - Server Overview (`tab-overview`): Lead with Host Physical Headroom & Safety Reserve.
   - All Accounts (`tab-accounts`): Tenant table with inline drift indicators, live CPU/RAM usage, and instant boost actions.
   - User Analytics (`tab-analytics`): Single-tenant historical SVG charts & deep telemetry inspection.
2. **Kernel Governance & Capacity:**
   - Drift Audit (`tab-audit`): Configured vs Effective cgroup comparison & bulk synchronization.
   - Golden Shield (`tab-goldenshield`): Hardware safety ceiling & system reserve allocations.
   - Capacity Planning (`tab-capacity`): Oversell modeling & density forecasting.
3. **Platform Services & Multi-PHP:**
   - Platform & Laravel Suite (`tab-platform`): 8-services dashboard (Redis ACL, Horizon, Reverb, Cron Schedulers, Chrome Headless).
   - OpenSwoole Governance (`tab-openswoole`): Multi-PHP runtime isolation & asynchronous worker supervision.
   - System & Agent Health (`tab-health`): `uniselv-resman-agent.service` metrics, SQLite storage health, and socket diagnostics.
4. **Administration & Help:**
   - Scheduled Reports (`tab-reports`)
   - Branding & Localization (`tab-integrations`)
   - Audit Log (`tab-auditlog`)
   - Help Guide (`tab-help`)

### 1.2 Webuzo Enduser Panel IA
Preserves the focused 7-tab personal workflow:
1. **Dashboard (`tab-dashboard`):** 4 high-precision resource meters (CPU Core vs Plan Allowance %, RAM Breakdown [Total cgroup, Anon, Cache, Swap], Disk I/O Throughput, Task threads).
2. **Current Usage & Processes (`tab-processes`):** Active process tree with privacy redactions & safe stop controls.
3. **Historical Charts (`tab-history`):** High-density SVG telemetry trendlines.
4. **Snapshots (`tab-snapshots`):** Incident capture timeline.
5. **Notifications (`tab-notifications`):** Alert history.
6. **App Services (`tab-services`):** Tenant-authorized self-service tools.
7. **Help Guide (`tab-help`):** Local knowledge base.

---

## 2. Design Tokens: Light & Dark Modes

```css
/* ==========================================================================
   UNISELV Precision Operations Console Tokens
   ========================================================================== */
:root,
.uniselv-container[data-theme="light"] {
    --ur-bg: #F3F5F2;              /* Soft parchment canvas */
    --ur-surface: #FFFFFF;         /* Primary panel card */
    --ur-surface-2: #EAEFEB;       /* Inset telemetry container */
    --ur-surface-3: #E1E8E3;       /* Hover / active control surface */
    --ur-text: #18231F;            /* Deep forest ink (High contrast) */
    --ur-text-muted: #63716A;      /* Secondary metadata */
    --ur-text-subtle: #7D8983;     /* Tertiary unit / timestamp labels */
    --ur-border: #D7E0DA;          /* Crisp hairline divider */
    --ur-border-strong: #B8C6BE;   /* Emphasized component boundary */
    --ur-accent: #176B5B;          /* Precision deep teal */
    --ur-accent-hover: #125447;
    --ur-accent-soft: #E1F0EB;
    --ur-focus: #A94F32;           /* Visible burnt-orange keyboard ring */
    --ur-radius: 6px;
    --ur-font-mono: ui-monospace, "SFMono-Regular", Consolas, "Liberation Mono", monospace;
    --ur-font-sans: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

.uniselv-container[data-theme="dark"] {
    --ur-bg: #101714;              /* Deep graphite canvas */
    --ur-surface: #17211D;         /* Dark ink panel */
    --ur-surface-2: #1D2924;       /* Inset telemetry container */
    --ur-surface-3: #26352E;       /* Hover / active surface */
    --ur-text: #E8EFEB;            /* High-legibility crisp text */
    --ur-text-muted: #A5B2AA;
    --ur-text-subtle: #87968D;
    --ur-border: #304139;
    --ur-border-strong: #46594F;
    --ur-accent: #72BDAA;          /* Minted sage accent */
    --ur-accent-hover: #91D0BF;
    --ur-accent-soft: #1D3B32;
    --ur-focus: #E0A080;
    --ur-radius: 6px;
}
```

---

## 3. Light/Dark Theme Switcher Specification

- **Placement:** Placed prominently in the plugin header bar adjacent to the Language selector (`#uniselv-locale-selector`) in both Admin and Enduser panels.
- **Default:** Always `light` for first-time visitors (`localStorage.getItem('uniselv_theme') || 'light'`).
- **No Automatic System Mode:** In accordance with instructions, there is no `prefers-color-scheme` override that silently flips the theme; user choice is sovereign and explicit.
- **Persistence:** Stored in browser `localStorage` under `uniselv_theme`. Evaluated immediately in the `<head>` or header markup before rendering to eliminate theme flash (FOUC).
- **Scope Containment:** The theme attribute is strictly scoped to `.uniselv-container[data-theme="..."]`, guaranteeing that Webuzo's host header, sidebar, and other plugins remain completely untouched.

---

## 4. Key Component Redesigns

1. **Host Infrastructure Anchor Banner:** Replaces the generic card row with a high-density status banner presenting:
   - Physical CPU Model & Total Cores
   - Physical Memory & Kernel Golden Shield Safety Reserve
   - Real-time Load Averages (1m, 5m, 15m) with threshold-aware status pills.
2. **Circular Telemetry Gauge:**
   - Stripped of all wave and particle artifacts.
   - Clean 240° track arc with precision tick marks at 25%, 50%, 75%, and 100%.
   - Tabular numerals (`font-variant-numeric: tabular-nums`) displaying exact percentage alongside core-equivalent units.
3. **Accessible Data Tables:**
   - Fixed header with subtle inset background (`--ur-surface-2`).
   - Monospace font for PIDs, IP addresses, memory byte strings, and usernames.
   - Status indicators pairing geometric SVG shapes with text (never color alone).
