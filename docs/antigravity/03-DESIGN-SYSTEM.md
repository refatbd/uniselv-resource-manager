# UNISELV Design System — Precision Operations Console

> Canonical visual and interaction specification for all redesigned Admin and Enduser surfaces.
> Values below are proposed starting tokens. Validate them against the existing logo, Webuzo host theme, contrast tests, and rendered screenshots before finalizing.

## 1. Design principles

1. **Operational clarity:** the most important state and action must be immediately visible.
2. **Data integrity:** never distort or decorate measured values.
3. **Hierarchy over ornament:** typography, alignment, spacing, and contrast create structure.
4. **Controlled density:** show useful information without visual clutter.
5. **Consistency:** the same component has the same meaning and behavior everywhere.
6. **Progressive disclosure:** advanced controls are available without overwhelming routine tasks.
7. **Accessible by default:** keyboard, contrast, focus, semantics, and reduced motion are built in.

## 2. Visual direction

Name: **Precision Operations Console**

Material language:
- Warm, quiet light surfaces.
- Graphite/ink dark surfaces.
- Fine borders and clear surface layers.
- Restrained deep-teal primary action colour.
- Copper used sparingly for emphasis or selected highlights, not as a second competing primary.
- Semantic status colours reserved for actual operational states.

Do not add decorative blobs, neon glows, glassmorphism, gradient text, floating particles, or animated card lifts.

## 3. Proposed colour tokens

These are initial values, not permission to override existing brand assets. First inspect the actual logo and any documented brand requirements. If the logo has a meaningful established colour, adapt the accent while preserving the system's semantic roles.

### Light theme

| Token | Proposed value | Use |
|---|---|---|
| `--ur-bg` | `#F3F5F2` | Main canvas |
| `--ur-surface` | `#FFFFFF` | Primary panels |
| `--ur-surface-2` | `#EAEFEB` | Subtle inset surfaces |
| `--ur-surface-3` | `#E1E8E3` | Selected/hovered structural surfaces |
| `--ur-text` | `#18231F` | Primary text |
| `--ur-text-muted` | `#63716A` | Secondary text |
| `--ur-text-subtle` | `#7D8983` | Tertiary metadata |
| `--ur-border` | `#D7E0DA` | Standard divider/border |
| `--ur-border-strong` | `#B8C6BE` | Emphasized border |
| `--ur-accent` | `#176B5B` | Primary action/link |
| `--ur-accent-hover` | `#125447` | Hover/active |
| `--ur-accent-soft` | `#E1F0EB` | Subtle selected surface |
| `--ur-focus` | `#A94F32` | Visible keyboard focus |

### Dark theme

| Token | Proposed value | Use |
|---|---|---|
| `--ur-bg` | `#101714` | Main canvas |
| `--ur-surface` | `#17211D` | Primary panels |
| `--ur-surface-2` | `#1D2924` | Inset surfaces |
| `--ur-surface-3` | `#26352E` | Selected/hovered structural surfaces |
| `--ur-text` | `#E8EFEB` | Primary text |
| `--ur-text-muted` | `#A5B2AA` | Secondary text |
| `--ur-text-subtle` | `#87968D` | Tertiary metadata |
| `--ur-border` | `#304139` | Standard divider/border |
| `--ur-border-strong` | `#46594F` | Emphasized border |
| `--ur-accent` | `#72BDAA` | Primary action/link |
| `--ur-accent-hover` | `#91D0BF` | Hover/active |
| `--ur-accent-soft` | `#1D3B32` | Subtle selected surface |
| `--ur-focus` | `#E0A080` | Visible keyboard focus |

### Semantic status tokens

| Semantic | Light | Dark | Meaning |
|---|---|---|---|
| Success | `#18794E` | `#63C69A` | Healthy, completed, within policy |
| Warning | `#94600A` | `#E6B65E` | Approaching threshold, needs attention |
| Critical | `#B93832` | `#F07870` | OOM, failure, dangerous pressure |
| Info | `#286A9B` | `#79B8E4` | Informational state |
| Neutral | `#59665F` | `#A7B1AB` | Unknown, inactive, not applicable |

Status colours must not be the only status indicator. Pair them with text, icons, or shapes.

## 4. Typography

Use a deliberate hierarchy. Do not rely on huge headings to make an operational interface feel premium.

Preferred approach:
- UI text: system UI sans-serif stack for compatibility and zero external font dependency.
- Technical values, IDs, timestamps, and code-like content: system monospace stack.
- Numeric metrics: `font-variant-numeric: tabular-nums`.
- Use sentence case for labels. Avoid unnecessary all-caps micro-labels.
- Keep long explanatory copy readable and concise.

Suggested CSS stacks:

```css
font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
font-family: ui-monospace, "SFMono-Regular", Consolas, "Liberation Mono", monospace;
```

Do not load fonts from a third-party CDN. If a bundled font is proposed, document its license, size, fallback, and performance impact first.

Suggested scale:
- Page title: 24–28px, weight 650–700.
- Section heading: 16–18px, weight 600–650.
- Body: 14–15px, line-height 1.45–1.6.
- Table/body metadata: 13–14px, never too small for routine reading.
- Metric value: 24–32px depending on context.
- Technical metadata: 12–13px with adequate contrast.

## 5. Spacing and layout

Use a consistent 4px base scale:
- 4px: icon/text micro-gap.
- 8px: compact control gap.
- 12px: compact component padding.
- 16px: standard component padding.
- 24px: section spacing.
- 32px: major group separation.
- 40px: page-level separation where needed.

Use a restrained radius scale:
- Small controls: 5–6px.
- Buttons and inputs: 6px.
- Tables/panels: 8–10px.
- Dialogs: 10–12px.
- Pills: fully rounded only when the pill shape communicates a status or compact selection.

Do not wrap every element in a card. Use page canvas, section headings, tables, dividers, and grouped controls to create hierarchy.

Prefer borders and surface contrast over large shadows. Elevation is reserved for overlays, menus, and dialogs.

## 6. Navigation and shell

- Preserve Webuzo's global Admin and Enduser shell.
- Redesign only the plugin's owned surface.
- Use one coherent internal navigation pattern across the plugin.
- Group large Admin navigation into meaningful operational categories if the existing number of tabs makes scanning difficult.
- Keep Enduser navigation simpler.
- The active section must be unmistakable without relying on colour alone.
- On small screens, use a compact, accessible navigation control with clear current-section text.
- Do not introduce a second competing global sidebar inside the Webuzo sidebar unless the available viewport and usability tests justify it.

## 7. Component rules

### Buttons
- Primary: one clear primary action per local workflow.
- Secondary: neutral outline or quiet surface.
- Destructive: explicit danger treatment and confirmation.
- Disabled: visibly disabled and not misleading.
- Loading: show progress and prevent accidental duplicate submissions.
- Keep labels action-oriented: “Refresh telemetry”, “Review changes”, “Apply override”.

### Panels and cards
- Use panels for related information, not as a default wrapper.
- Avoid nested cards.
- Keep panel padding consistent.
- Do not use hover elevation on every panel.
- Use a clear header, optional supporting text, and meaningful actions.

### Tables
- Use semantic table markup and clear column labels.
- Align numeric values consistently.
- Use tabular numerals.
- Include units in headings or values.
- Provide useful sorting/filtering states only where implemented.
- Make row actions discoverable without crowding every cell.
- On mobile, provide a deliberate responsive table strategy; do not silently clip important data.
- Preserve pagination, search, filters, and account scope.

### Forms
- Use persistent labels, not placeholder-only labels.
- Explain units, allowed ranges, and operational consequences.
- Group related fields.
- Show field-level validation and an overall submission result.
- Confirm privileged or destructive operations with exact target and consequence.

### Status indicators
- Use text plus a semantic colour/icon.
- Distinguish live, stale, offline, waiting, unavailable, and unknown states.
- Display last successful sample time when relevant.
- Do not animate a live dot continuously unless it communicates an actual live state and reduced-motion is respected.

### Notifications and dialogs
- Toasts must be concise and accessible.
- Errors must explain what failed and what the user can do next.
- Dialogs need correct focus management, Escape handling where safe, keyboard access, and focus restoration.
- Destructive dialogs must name the affected account/resource and operation.

## 8. Telemetry and charts

- Preserve the meaning and precision of all current telemetry.
- Always show units and time range.
- Distinguish current, average, peak, configured limit, effective limit, and normalized allowance.
- Do not use a gauge for every metric. Use a chart, bar, value, or table according to the question being answered.
- Do not add decorative sparkline trends without real samples.
- No data must render as an explicit empty/unavailable state, not zero.
- Stale data must be visibly labelled.
- Tooltips must be keyboard-accessible or have equivalent textual data.
- Use a consistent chart palette across Admin and Enduser.
- Keep thresholds and limits legible in both themes.

Product-specific semantics to preserve:
- CPU core-equivalent usage and account allowance percentage are separate.
- Total cgroup memory is not the same as process RSS.
- Anonymous memory, file/page cache, and swap must remain distinguishable.
- I/O throughput, IOPS, task/thread count, throttling, and OOM events must retain their existing definitions.

## 9. Light / Dark theme switcher

The UNISELV plugin supports two user-selectable themes: LIGHT and DARK. LIGHT is the default.

Rules:
1. Provide a clear, accessible Light/Dark theme switcher in both Admin and Enduser plugin experiences.
2. Do not add a third System/Auto mode. The user's explicit selection controls the plugin theme.
3. Persist the selected theme using a namespaced preference key such as `uniselv.theme.v1`, with a safe fallback if browser storage is unavailable.
4. Apply the selected theme consistently to Admin and Enduser plugin surfaces.
5. Ensure dialogs, dropdowns, tooltips, toast containers, SVG charts, form controls, and dynamically injected content use the selected theme.
6. Use semantic CSS variables. Do not create separate unrelated stylesheets for every screen.
7. Set `color-scheme` appropriately on the plugin root so native controls match the selected theme.
8. Test both themes while the OS/browser preference is Light and while it is Dark. An explicit UNISELV selection must not unexpectedly flip when the OS preference changes.
9. Do not change Webuzo's global theme or other plugins' appearance.
10. If an existing plugin theme selector or dark stylesheet exists, inventory it first and consolidate it carefully rather than creating conflicting parallel implementations.
11. Theme switching must not reload the page unless the existing architecture makes that unavoidable; prefer a safe, immediate update without disrupting active forms or navigation.
12. Ensure the switcher has an accessible name, visible focus, keyboard operation, and a clear selected state.

A possible implementation is a namespaced data attribute on the plugin root plus explicit theme propagation to overlay roots. Choose the final mechanism only after auditing how the current DOM and overlays are mounted.

## 10. Motion

- Motion is functional, brief, and restrained.
- Use transitions for state changes, not decoration.
- No floating particles, perpetual decorative motion, exaggerated spring effects, or card lift on hover.
- Respect `prefers-reduced-motion: reduce`.
- Never animate numeric values in a way that makes the measurement ambiguous.

## 11. Responsive behavior

Test at minimum:
- 1440 × 900 desktop.
- 1280 × 800 laptop.
- 1024 × 768 compact desktop/tablet landscape.
- 768 × 1024 tablet portrait.
- 390 × 844 mobile.
- 360 × 800 narrow mobile.

Requirements:
- No horizontal page overflow.
- No clipped buttons or modal actions.
- Tables remain usable.
- Navigation remains understandable.
- Charts resize without hiding axes or labels.
- Touch targets are comfortable.
- Long account names, domains, paths, and command strings wrap safely.

## 12. Accessibility

Target WCAG 2.2 AA where applicable:
- Contrast checked in both themes.
- Keyboard access for all interactive controls.
- Visible focus states.
- Semantic headings, buttons, labels, tables, and dialogs.
- Correct ARIA only where native semantics are insufficient.
- Status is not communicated by colour alone.
- Reduced-motion support.
- Accessible validation and async status announcements.
- No keyboard traps.
- Focus is restored after dialogs close.

## 13. CSS architecture

- Establish one canonical token layer.
- Replace repeated hard-coded colours with semantic variables.
- Remove obsolete duplicate overrides after confirming they are unused.
- Scope plugin styles to plugin-owned roots.
- Avoid global selectors that can leak into Webuzo.
- Avoid new inline styles; use reusable classes.
- Avoid unexplained `!important`.
- Keep responsive rules grouped and documented.
- Keep Admin and Enduser components visually related without forcing identical density.
- Do not rename JavaScript hooks or IDs without updating all consumers and tests.
