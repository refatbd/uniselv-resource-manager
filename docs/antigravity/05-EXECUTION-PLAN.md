# Redesign Execution Plan

## Overview

Redesign in controlled vertical slices. Do not replace the entire stylesheet or rewrite all PHP markup in one operation.

## Phase 0 — Safety and baseline

1. Confirm repository path, branch, commit SHA, working tree, and package version.
2. Confirm staging host identity and that it is not production.
3. Create a feature branch.
4. Capture baseline screenshots for representative Admin and Enduser screens.
5. Record existing tests and exact commands that are present in the checkout.
6. Make a clean baseline commit.
7. Confirm a rollback method.

Exit gate: safe staging environment and reproducible baseline exist.

## Phase 1 — Read-only product and code audit

1. Read repository instructions and all relevant documentation.
2. Inspect the PHP hook registration and controller functions.
3. Inspect CSS, JavaScript, PHP markup, SVG charts, and dynamic rendering.
4. Map all UI-to-JS-to-PHP-to-daemon interactions.
5. Map every DOM ID, selector, data attribute, inline event handler, and global function used by JavaScript.
6. Inventory Admin and Enduser surfaces.
7. Identify hard-coded colours, duplicate CSS, inline styles, global style leakage, and responsive overrides.
8. Identify current theme behavior and overlay mounting.
9. Inspect existing accessibility and keyboard behavior.
10. Produce the audit reports required by `ANTIGRAVITY.md`.

Exit gate: the owner can understand the current UI, behavior, risks, and proposed direction before implementation.

## Phase 2 — Design proposal and visual baseline

1. Confirm the Precision Operations Console direction.
2. Inspect the actual product logo and host theme.
3. Validate proposed colour tokens and contrast.
4. Create one representative Admin screen concept.
5. Create one representative Enduser screen concept.
6. Show both Light and Dark designs across Admin and Enduser, with Light as the default and a persistent user-controlled switcher.
7. Show desktop and mobile layouts.
8. Document navigation, table, metric, chart, form, dialog, and status patterns.
9. Compare screenshots and explain why the new layout improves the task.
10. Obtain owner approval.

Exit gate: one approved visual direction and design token set.

## Phase 3 — Design foundation

Implement:
- Semantic CSS custom properties for Light and Dark themes.
- A persistent, accessible Light/Dark switcher with Light as the default and no automatic System mode.
- Typography and numeric styles.
- Spacing and radius scale.
- Focus, hover, active, disabled, loading, and error states.
- Buttons, inputs, status indicators, panels, tables, dialogs, and toast foundations.
- Chart theme variables.
- Scoped plugin styles.

Do not change backend behavior.

Exit gate: shared primitives work in both Admin and Enduser without style leakage into Webuzo.

## Phase 4 — Representative vertical slice

1. Redesign one Admin screen with real data and all relevant states.
2. Redesign one Enduser screen with real data and all relevant states.
3. Preserve existing DOM hooks and JavaScript contracts.
4. Test all interactions.
5. Test both Light and Dark themes at all target viewports, including when the OS/browser preference differs from the selected UNISELV theme.
6. Review screenshots with the owner.
7. Refine the design system based on evidence.

Exit gate: approved patterns are reusable and behavior remains intact.

## Phase 5 — Admin rollout

Migrate the remaining Admin surfaces in logical groups:
- Monitoring.
- Account inventory and analytics.
- Governance and capacity.
- System/runtime/platform operations.
- Reports, billing, permissions, audit, and help.

For each group:
- Reuse approved components.
- Preserve all actions and permission checks.
- Test loading, empty, error, and success states.
- Capture before/after screenshots.
- Run relevant regression tests.

Exit gate: all Admin surfaces follow the design system and pass the relevant checks.

## Phase 6 — Enduser rollout

Migrate:
- Dashboard/current usage.
- Processes.
- History.
- Snapshots.
- Notifications.
- Support export.
- Runtime and platform self-service views.

Keep the Enduser experience simpler than Admin. Preserve strict tenant isolation.

Exit gate: all Enduser surfaces are consistent, role-safe, and tested.

## Phase 7 — Responsive, accessibility, and visual regression

1. Test all required viewport sizes.
2. Test keyboard-only navigation.
3. Test screen-reader labels and async announcements where applicable.
4. Test contrast in light and dark.
5. Test reduced motion.
6. Test tables, charts, dialogs, and overflow.
7. Compare baseline and redesigned screenshots.
8. Check browser console, failed requests, and server logs.

Exit gate: QA report has no unresolved critical/high issues.

## Phase 8 — Release preparation

1. Review changed files and diff.
2. Run all relevant repository tests.
3. Validate PHP and JavaScript syntax.
4. Validate package contents and checksum generation if applicable.
5. Verify install/upgrade/rollback assumptions without applying destructive actions to production.
6. Prepare release notes and rollback steps.
7. Present evidence to the owner.
8. Deploy only after explicit approval.

## Commit strategy

Use small commits such as:
- `docs: add antigravity redesign brief`
- `ui: introduce semantic design tokens`
- `ui: add theme preference support`
- `ui: redesign shared navigation and controls`
- `ui: redesign admin monitoring surfaces`
- `ui: redesign enduser resource views`
- `test: add visual and responsive regression evidence`

Use commit names that describe actual changes. Do not claim tests passed unless they were run and their output was inspected.
