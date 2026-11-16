# UNISELV Resource Manager — Antigravity Project Instructions

> Read this file before inspecting, editing, testing, or deploying this repository.
> This is the top-level operating contract for Gemini Antigravity.

## Mission

Redesign the existing UNISELV Resource Manager interface into one distinctive, coherent, production-grade **Precision Operations Console**.

The redesign must feel purpose-built for server resource monitoring, infrastructure operations, tenant governance, and hosting-account self-service. It must not look like a generic AI-generated SaaS dashboard.

The redesign covers the actual UI surfaces present in this Webuzo plugin:
- Webuzo Admin panel integration.
- Webuzo Enduser panel integration.
- Existing operational, telemetry, governance, reports, and settings views.
- Shared components, responsive behavior, and a user-controlled Light/Dark theme switcher (Light default).

Do not invent a public marketing website, a new product module, or a new backend architecture unless the repository audit proves that such a surface already exists or the owner explicitly requests it.

## Mandatory reading order

Read all of these documents before proposing implementation:

1. `docs/antigravity/01-PRODUCT-DESIGN-BRIEF.md`
2. `docs/antigravity/02-RESEARCH-AND-REFERENCE-REPOS.md`
3. `docs/antigravity/03-DESIGN-SYSTEM.md`
4. `docs/antigravity/04-UI-SURFACE-INVENTORY.md`
5. `docs/antigravity/05-EXECUTION-PLAN.md`
6. `docs/antigravity/06-SERVER-ACCESS-SAFETY.md`
7. `docs/antigravity/07-QA-TEST-PLAN.md`
8. `docs/antigravity/08-ACCEPTANCE-CHECKLIST.md`

## Non-negotiable engineering constraints

This repository is a Webuzo plugin, not a standalone React/Vue/Next.js application.

Preserve the existing architecture unless a separately approved engineering change is necessary:
- PHP plugin integration and Webuzo hooks.
- Existing admin and enduser entry points.
- PHP-to-daemon UNIX-domain-socket IPC.
- Python daemon and its authorization model.
- Cgroups v2 resource enforcement and telemetry calculations.
- Existing API action names, request/response contracts, CSRF checks, authorization checks, and tenant boundaries.
- Existing JavaScript behavior, chart data semantics, forms, and operational actions.
- Existing install, activation, deactivation, uninstall, backup, and recovery behavior.

Do not introduce React, Vue, a CSS framework, a charting dependency, a remote icon library, or a CDN merely to achieve the redesign. Prefer the existing native PHP, CSS, JavaScript, and SVG implementation.

Before changing markup, map all IDs, classes, data attributes, inline event handlers, global objects, and selectors used by JavaScript. Preserve them or update every dependent reference and test.

Do not change backend behavior as a side effect of visual work.

## Required workflow: audit first, implement second

### Stage A — read-only repository and environment audit

Do not edit files in this stage.

1. Confirm the checked-out repository, branch, commit SHA, working tree status, and installed plugin version.
2. Inspect the full repository tree and all repository-specific instructions.
3. Verify the current README as updated by the owner, then compare changelog, package metadata, PHP plugin header, packaged archive metadata, and the version installed on the staging server. Do not repeat any previously observed README/version discrepancy without rechecking the current commit.
4. Inventory every Admin and Enduser screen, tab, nested view, modal, form, table, chart, and action.
5. Trace UI-to-JavaScript-to-PHP-to-daemon flows for critical actions.
6. Identify CSS duplication, hard-coded values, inline styles, global selectors, conflicting overrides, and existing responsive rules.
7. Identify existing accessibility behavior, keyboard handling, focus management, reduced-motion support, and any existing plugin-owned theme controls or dark-theme rules. The target design supports LIGHT and DARK themes with a user-controlled switcher; LIGHT is the default.
8. Capture baseline screenshots using test accounts and non-sensitive test data.
9. Run only non-mutating checks on the server. Follow `06-SERVER-ACCESS-SAFETY.md`.
10. Produce the audit deliverables listed below.

### Stage B — design proposal

Before changing production UI code, prepare:
- Current UI findings ranked by user impact.
- Complete screen/component inventory.
- Existing behavior and DOM-hook compatibility map.
- Proposed information architecture.
- One coherent visual direction based on `03-DESIGN-SYSTEM.md`.
- Light and Dark theme previews, with Light as the default and an explicit user-controlled switcher.
- Desktop, tablet, and mobile previews for representative Admin and Enduser screens.
- Risk register and proposed rollback plan.

Do not produce several unrelated visual styles. The project needs one consistent design language.

### Stage C — implementation after explicit approval

After the owner approves the design proposal:

1. Work on a dedicated feature branch.
2. Make a clean baseline commit before implementation.
3. Implement shared Light/Dark design tokens and primitives first, with Light as the default.
4. Migrate one representative Admin screen and one Enduser screen.
5. Verify the result before applying the shared patterns to the remaining screens.
6. Work in small, reviewable commits.
7. Preserve functionality and data semantics.
8. Run the relevant tests after every meaningful implementation slice.
9. Do not deploy to production without explicit owner approval.

## Required audit deliverables

Create these files during Stage A, using actual repository evidence:

- `docs/antigravity/audit/REPOSITORY-AUDIT.md`
- `docs/antigravity/audit/SCREEN-INVENTORY.md`
- `docs/antigravity/audit/DOM-AND-JS-CONTRACT.md`
- `docs/antigravity/audit/CURRENT-DESIGN-FINDINGS.md`
- `docs/antigravity/audit/SECURITY-AND-DEPLOYMENT-RISKS.md`
- `docs/antigravity/audit/BASELINE-TEST-REPORT.md`

The `audit/` folder can be created if it does not exist. Do not overwrite existing owner-authored documents without approval.

## Stop and ask the owner if

- The only available target is the production server.
- You cannot distinguish staging from production.
- You find a repository/server version mismatch that could make the deployment unsafe.
- A proposed UI change requires changing authorization, CSRF, IPC, daemon, cgroup, billing, or lifecycle behavior.
- A command could restart services, terminate processes, change resource limits, alter plans, delete data, or change system configuration.
- You cannot establish a safe rollback.
- The required browser test account would have real destructive privileges.
- The current behavior is unclear or undocumented.

## Definition of success

The finished product must be visually coherent, responsive, accessible, data-accurate, and operationally safe. A beautiful screenshot is not sufficient. Every visible control must work, every displayed metric must be real and correctly labelled, and existing security and backend behavior must remain intact.

Use `08-ACCEPTANCE-CHECKLIST.md` as the final release gate.
