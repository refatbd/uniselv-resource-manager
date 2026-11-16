# UNISELV Resource Manager — Current Design Findings & Gap Analysis

> Stage A Deliverable — Expert Usability, Visual Hierarchy & Accessibility Findings
> Based on direct inspection of rendered staging screenshots and stylesheet rules.

---

## 1. Problem Ranking Overview

| Rank | Finding Identifier | Severity | Core Issue | User Impact |
|---|---|---|---|---|
| **1** | `GAP-THEME-NO-DARK` | **HIGH** | Complete absence of Dark Theme & Theme Switcher | Server administrators and developers working in low-light environments experience visual fatigue; violates project design mandate. |
| **2** | `GAP-AI-SLOP-DECORATION` | **HIGH** | Gimmicky animations, waves, particles & gradients | Decreases operational trustworthiness; gives the impression of a generic demo rather than a mission-critical infrastructure tool. |
| **3** | `GAP-CONTRAST-A11Y` | **MEDIUM** | Low contrast text on tinted pastel badge backgrounds | Fails WCAG 2.2 AA contrast standards (< 4.5:1 ratio), making critical status unreadable in varied ambient lighting. |
| **4** | `GAP-NAV-CROWDING` | **MEDIUM** | Flat 13-tab horizontal row in Admin Panel | Causes severe visual crowding and awkward wrapping on standard viewports (1280px–1440px). |
| **5** | `GAP-HIERARCHY-CARDS` | **MEDIUM** | Uniform card grid lacking operational priority | Host hardware safety headroom and physical capacity receive identical visual weight as transient metrics. |
| **6** | `GAP-TYPO-NUMERICS` | **LOW** | Missing consistent tabular numerals for metrics | Metric numbers jitter slightly during polling updates; inconsistent hierarchy across headings. |

---

## 2. Detailed Findings & Engineering Evidence

### 2.1 Missing Dark Mode & Theme Switcher (`GAP-THEME-NO-DARK`)
- **Evidence:** `plugin/assets/style.css` contains solely light-mode CSS variables (`--uniselv-bg-body: #f8fafc; --uniselv-bg-card: #ffffff;`). There are zero dark theme overrides or `[data-theme="dark"]` rules.
- **Root Cause:** The initial v1.0–v1.4 development focused on kernel isolation and backend features, leaving styling on a single hardcoded light theme.
- **Remediation:** Introduce semantic CSS tokens mapping to `--ur-bg`, `--ur-surface`, `--ur-text`, `--ur-border`, and `--ur-accent`, controlled via a persistent data attribute (`data-theme="light"` / `data-theme="dark"`) with Light default and an accessible toggle in the header.

### 2.2 Artificial "AI-Slop" Decorative Gimmicks (`GAP-AI-SLOP-DECORATION`)
- **Evidence:** In `style.css` (lines 1754–1780), CSS classes `.wave-front`, `.wave-back`, and `.particle` inject animated SVG wave masks and floating particle dots behind telemetry gauges. Cards use an excessive `16px` border-radius and multi-layer drop shadows (`0 4px 20px -2px rgba(15, 23, 42, 0.04)`).
- **Usability Impact:** Server telemetry is operational evidence, not animated entertainment. The waves distort gauge needle readings and consume unnecessary client CPU rendering cycles.
- **Remediation:** Strip wave and particle decorative overlays completely. Replace with crisp, high-precision SVG circular gauges with distinct track, indicator, and calibrated threshold tick-marks following `03-DESIGN-SYSTEM.md`.

### 2.3 Color Contrast & Status Signaling (`GAP-CONTRAST-A11Y`)
- **Evidence:** The live freshness badge uses `#ecfdf5` background with `#047857` text, and host CPU cards use `#eff6ff` with `#3b82f6`. Under standard display calibration, the contrast ratio is ~3.2:1 (violating the minimum 4.5:1 WCAG requirement).
- **Accessibility Risk:** Color is frequently used as the sole conveyor of status (e.g., green dot for live, amber dot for elevated).
- **Remediation:** Enforce semantic status tokens pairing high-contrast foregrounds with clear textual labels and distinct geometric icon shapes (check, triangle alert, circle).

### 2.4 Administrative Navigation Overcrowding (`GAP-NAV-CROWDING`)
- **Evidence:** The Admin header presents 13 individual navigation buttons in a single flex row: *Overview, Accounts, Analytics, Audit, Golden Shield, Capacity, Reports, Branding, Audit Log, OpenSwoole, Platform, Health, Help*.
- **Screen Evidence:** On viewports below 1440px width, tabs break into two staggered lines or trigger the crude browser-native select fallback (`#uniselv-more-sections`), breaking visual continuity.
- **Remediation:** Organize Admin tabs into clean, cohesive operational clusters (e.g. *Monitoring, Governance, Platform Operations, Administration*) or use a structured segmented control with clear active state styling.

### 2.5 Visual Hierarchy & Operational Density (`GAP-HIERARCHY-CARDS`)
- **Evidence:** In `tab-overview` and `tab-dashboard`, all 4 primary metric cards share identical dimensions, typography, and card containers. Host physical capacity and kernel headroom do not visually anchor the page.
- **Remediation:** Re-structure the layout to lead with an authoritative Host Infrastructure Banner (displaying physical cores, total RAM, and active Golden Shield safety reserve), followed by an operational grid of high-density telemetry gauges.
