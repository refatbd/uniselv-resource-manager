# Product Design Brief — UNISELV Resource Manager

## 1. Product identity

**Product:** UNISELV Resource Manager  
**Category:** Webuzo hosting infrastructure resource monitoring and governance plugin  
**Primary environment:** Webuzo Admin and Enduser panels on Ubuntu Linux  
**Core technologies evidenced in the public repository:** PHP plugin integration, native JavaScript, CSS, inline/native SVG charts, Python background daemon, UNIX-domain-socket IPC, SQLite telemetry storage, systemd, and Linux cgroups v2.

The product extends Webuzo resource limits with kernel-level telemetry, account-level visibility, administrative governance, and operational tooling. It is not a generic analytics dashboard.

## 2. Product users

### A. Server administrator / platform operator

Needs to:
- Understand physical server capacity and current resource pressure.
- See account-level CPU, memory, I/O, task, throttling, and OOM information.
- Compare configured limits with effective kernel limits.
- Detect drift and understand the risk before synchronizing plans.
- Manage temporary resource overrides with clear expiry and audit history.
- Inspect daemon health, PHP runtimes, OpenSwoole, managed Laravel services, browser engine governance, and platform operations where those features exist.
- Review scheduled reports, audit events, permissions, package mappings, and billing integration status.

Design implication: Admin screens can be information-dense, but hierarchy must make risk, current state, and next action obvious.

### B. Hosting account enduser

Needs to:
- Understand their own resource usage and plan allowance.
- Distinguish core-equivalent CPU usage from percentage of plan allowance.
- Understand total memory, anonymous memory, file cache, and swap without misleading simplification.
- Review history, processes, snapshots, and notifications.
- Safely stop only their own eligible processes.
- Export a privacy-safe support report.
- View enabled platform/runtime capabilities and use permitted self-service controls.

Design implication: Enduser screens should be simpler and more explanatory than Admin screens. Never expose other tenants' data or administrative-only controls.

### C. Reseller or scoped operator

If the current repository and authorization model expose reseller-scoped views, make the scope visible:
- Show which accounts belong to the current reseller.
- Make the active scope/filter explicit.
- Do not imply that the reseller can see or control all server accounts.
- Preserve server-side ownership enforcement.

## 3. Primary product jobs

1. **Observe:** Show accurate, fresh resource telemetry.
2. **Diagnose:** Help an operator understand why a metric is elevated or unavailable.
3. **Govern:** Compare configured and effective limits and manage approved policies.
4. **Protect:** Make system headroom, safety reserves, and tenant isolation understandable.
5. **Act:** Provide safe, permission-aware controls with clear confirmation and feedback.
6. **Explain:** Communicate technical metrics in plain, precise language.

## 4. Visual thesis

### Precision Operations Console

The interface should use a coherent LIGHT + DARK visual system and feel like a professional infrastructure operations workbench:
- Calm, deliberate, and technical.
- Dense where the task requires density.
- Structured around real operational workflows.
- Precise with numbers, units, timestamps, thresholds, and status.
- Restrained in decoration.
- Consistent across Admin and Enduser surfaces without making both experiences identical.

The visual identity should come from typography, data hierarchy, navigation, grid rhythm, restrained materials, and excellent state design—not from decorative gradients or animation.

### Desired impression

- Trustworthy.
- Technically competent.
- Operationally clear.
- Fast to scan.
- Suitable for extended daily use.
- Distinctive without being theatrical.

## 5. Product-specific design rules

- Treat telemetry as evidence, not decoration.
- Show units beside values.
- Distinguish measured values, configured limits, derived percentages, stale samples, and unavailable values.
- Do not show invented sample metrics, fake trend lines, fake alerts, fake customer names, or illustrative values in production UI.
- Never use colour as the only indicator of status.
- Give destructive or privileged actions clear scope, consequence, and confirmation.
- Make the last sample time and telemetry freshness visible where relevant.
- Explain CPU semantics consistently: 100% core-equivalent usage represents one fully utilized physical CPU core; account allowance percentage is a separate normalized metric.
- Preserve the distinction between total cgroup memory, anonymous memory, file/page cache, and swap.
- Do not collapse technically different measurements into a single generic “performance” score.

## 6. Scope boundaries

The redesign is a presentation and interaction redesign of existing product surfaces.

Do not:
- Turn the plugin into a standalone SaaS application.
- Replace Webuzo navigation or global chrome.
- Add a marketing homepage unless one exists in the checked-out repository and is explicitly in scope.
- Rewrite the daemon, IPC, cgroups, storage, or authorization layers for visual convenience.
- Remove advanced features because they are difficult to design.
- Hide operational controls behind decorative cards or unexplained menus.
- Change the meaning, precision, units, or refresh behavior of metrics.

## 7. Theme requirement — Light + Dark switcher

- Provide two user-selectable modes: Light and Dark.
- Light is the default for first-time users.
- Include an accessible theme switcher in the plugin-owned UI for both Admin and Enduser experiences.
- Persist the selected theme across page visits and sessions using a namespaced preference key, with a safe fallback if browser storage is unavailable.
- Do not add an automatic System mode; the user's explicit selection controls the plugin theme.
- Do not change Webuzo's global chrome or other plugins when switching the UNISELV theme.
- Apply the selected theme to every plugin-owned surface, including charts, dialogs, dropdowns, popovers, toasts, forms, and dynamically injected content.
- If the host Webuzo panel uses a different theme, keep the plugin-owned content internally consistent with the user's UNISELV theme choice.
- Audit any existing theme implementation before replacing or consolidating it.

## 8. Design decisions to record

Create a design decision log during the audit and implementation. Each significant decision must record:
- Decision.
- Product/user reason.
- Screens affected.
- Accessibility implications.
- Technical constraints.
- Alternatives rejected.
- Verification method.
