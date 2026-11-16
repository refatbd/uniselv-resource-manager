# Gemini Antigravity — First Prompt

Copy this prompt into Gemini Antigravity after opening the repository workspace and adding the documentation pack.

---

You are working on the existing **UNISELV Resource Manager** repository.

First read:
- `ANTIGRAVITY.md`
- Every Markdown document in `docs/antigravity/`

Your mission is to redesign the complete existing plugin UI as a distinctive **Precision Operations Console**, with consistent Admin and Enduser experiences and a user-controlled Light/Dark theme switcher. Light is the default; do not add an automatic System mode.

## Important: do not start coding yet

For your first task, perform a READ-ONLY audit only.

Do not edit source files.
Do not change the server.
Do not run privileged or destructive commands.
Do not deploy.
Do not restart services.
Do not change cgroups, resource limits, PHP runtimes, Redis, OpenSwoole, Laravel services, Chrome, billing, or Webuzo configuration.

## Audit tasks

1. Inspect the complete repository and identify the actual stack, current branch, commit SHA, and working tree state.
2. Compare the README, changelog, plugin metadata, PHP plugin header, package archive metadata, and installed staging version. Report any version mismatch.
3. Inventory every Admin and Enduser screen, tab, nested view, modal, form, table, chart, and action.
4. Map the full interaction contract: PHP hooks, API actions, DOM IDs, CSS classes, data attributes, JavaScript selectors, global functions, and daemon IPC actions.
5. Identify repeated/overridden CSS, hard-coded colours, inline styles, global selectors, inconsistent components, and responsive problems.
6. Inspect any existing plugin-owned theme controls and theme rules. The target is a user-controlled Light/Dark switcher with Light as the default and no automatic System mode.
7. Capture baseline screenshots for representative Admin and Enduser screens on the staging environment, if safely available.
8. Identify all loading, empty, error, success, stale, offline, and permission-denied states.
9. Identify accessibility issues and test keyboard behavior without triggering privileged actions.
10. Review public design references in `02-RESEARCH-AND-REFERENCE-REPOS.md` and extract only the principles that fit this product.
11. Create all audit reports required by `ANTIGRAVITY.md`.
12. Prepare a single coherent visual proposal following `03-DESIGN-SYSTEM.md`.

## Required output before implementation

Return:
- Repository and version findings.
- Complete screen inventory.
- Current design problems ranked by impact.
- Existing DOM/JavaScript compatibility map.
- Security and deployment risk register.
- Proposed information architecture.
- Proposed design tokens and component rules.
- Admin and Enduser concept screenshots.
- Light/Dark switcher behavior, persistence, and Light as the default.
- Desktop, tablet, and mobile examples.
- Test plan and rollback plan.
- A list of questions that genuinely block safe implementation.

## Preserve these constraints

This is a Webuzo plugin using the existing PHP, native JavaScript, CSS, SVG, Python daemon, UNIX socket IPC, SQLite, systemd, and cgroups v2 architecture.

Do not migrate it to React, Vue, Next.js, or a new backend.
Do not break Webuzo hooks, existing API contracts, CSRF checks, authorization, tenant isolation, or daemon behavior.
Do not remove functionality to simplify the design.
Do not create fake metrics, fake trends, or fake operational states.
Do not load remote fonts, icon libraries, or CSS frameworks from a CDN.

The initial audit must be read-only. After presenting the findings and design proposal, STOP and wait for my explicit approval before modifying source code.

When implementation is approved, work on a feature branch, use small commits, test each vertical slice, and follow the acceptance checklist.

---
