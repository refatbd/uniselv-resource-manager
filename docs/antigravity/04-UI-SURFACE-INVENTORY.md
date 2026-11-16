# UI Surface Inventory and UX Requirements

> This is a starting inventory derived from the public repository README and source files. It is not a substitute for a complete local checkout audit. Antigravity must verify every item against the actual checked-out commit and add missing screens.

## 1. Admin panel — known surfaces

The public source exposes an Admin integration through the Webuzo `admin_act` hook. The UI includes a tabbed operational console.

### A. Monitoring
- Server Overview.
- All Accounts.
- User Analytics and Snapshots.
- Current account usage and resource charts.
- Resource event and telemetry freshness views.

### B. Governance
- Configured vs Effective Audit.
- Golden Shield Governance.
- Capacity and Oversell.
- Temporary resource overrides.
- Role and Account Permissions.
- Package Mappings.

### C. Platform operations
- System and Agent Health.
- PHP Runtime Registration and lifecycle governance.
- OpenSwoole Governance and Multi-PHP Automation.
- Platform Operations and Managed Laravel Services.
- Redis ACL tenant isolation and related platform controls where present.
- Chrome Browser Engine governance, permissions, and diagnostics where present.

### D. Reporting and configuration
- Scheduled Reports.
- Branding and Billing.
- Audit Log.
- Telemetry/storage retention settings.
- Help and About.
- Support report/export tools.

### Admin UX requirements

Server Overview:
- Lead with physical host capacity, resource headroom, and telemetry freshness.
- Make current load and safety reserve easy to interpret.
- Show source/time context and unavailable states.
- Avoid a wall of equally weighted metric cards.

All Accounts:
- Prioritize account identity, plan, CPU, allowance, memory, tasks, throttling, OOM, and relevant actions.
- Keep search, filters, pagination, and row actions usable.
- Make account scope explicit.
- Provide clear empty and no-match states.

Configured vs Effective Audit:
- Show configured and effective values side by side.
- Make drift easy to scan.
- Clearly separate read-only inspection from mutation.
- Explain the scope of bulk synchronization before confirmation.

Golden Shield and Capacity:
- Explain customer allocation ceiling and system reserve.
- Visualize capacity in a way that preserves exact values and units.
- Distinguish policy configuration from current observed utilization.
- Do not imply that an oversold allocation is the same as physical capacity.

Temporary Overrides:
- Show target account, original plan, temporary plan, reason, start time, and expiry.
- Make automatic restoration visible.
- Make manual cancellation a deliberate, confirmed action.
- Preserve auditability.

System/Agent Health:
- Separate service state, telemetry freshness, runtime health, and last diagnostic result.
- Distinguish warning from failure.
- Make remediation guidance specific and non-destructive.

OpenSwoole / Platform / Chrome:
- Group advanced tools by operational task.
- Separate read-only diagnostics from state-changing actions.
- Show progress and final results for long-running jobs.
- Keep destructive or privileged controls visually distinct.
- Preserve permission-aware visibility.

Audit Log:
- Prioritize timestamp, actor, target, action, outcome, and reason.
- Provide useful filters.
- Do not truncate critical audit context without a way to inspect it.

## 2. Enduser panel — known surfaces

The public source exposes an Enduser integration through the Webuzo `enduser_act` hook.

Known areas include:
- Dashboard.
- Current Usage.
- Processes.
- History.
- Snapshots and snapshot details.
- Notifications and Events.
- Support Report Export.
- OpenSwoole assigned resource budget/runtime.
- Platform services and self-service controls where enabled.
- Application logs, worker/scheduler/Reverb-related views, and Chrome checks where enabled and authorized.

### Enduser UX requirements

Dashboard / Current Usage:
- Explain usage against the user's own plan.
- Separate CPU core-equivalent usage from allowance percentage.
- Present memory breakdown accurately.
- Show last sample and freshness.
- Keep the most relevant next action visible.

Processes:
- Show only the authenticated user's eligible processes.
- Make command-line redaction understandable.
- Make termination scope explicit.
- Require confirmation before stopping a process.
- Never imply that a process can be stopped if the server-side action is unavailable.

History:
- Make time ranges clear.
- Show actual samples only.
- Distinguish gaps, stale samples, and missing telemetry.
- Keep axes, units, and thresholds legible.

Snapshots:
- Explain capture time and trigger.
- Make sensitive diagnostic information privacy-aware.
- Make support export scope clear.

Notifications:
- Distinguish unread/read and severity.
- Make acknowledgement behavior clear.
- Do not use colour alone.

Platform services:
- Show only services and actions available to the authenticated account.
- Explain service status, assigned budget, and safe controls.
- Never expose server-wide administrative information.

## 3. Shared UI components to inventory

Antigravity must locate all actual instances and dependencies for:
- Plugin header/brand area.
- Navigation tabs and mobile navigation.
- Page titles and section headers.
- Metric panels and metric values.
- Gauge/usage visualization.
- SVG charts and chart tooltips.
- Tables, filters, search, pagination.
- Status badges and freshness indicators.
- Buttons and icon buttons.
- Form controls and validation.
- Confirmation dialogs and other modals.
- Toast notifications.
- Loading skeletons/spinners.
- Empty states.
- Error states.
- Help tooltips and documentation links.
- Theme selector.
- Responsive table wrappers.
- Any dynamically injected panels or async results.

## 4. Required screen inventory fields

For every screen or nested view, record:

| Field | Required detail |
|---|---|
| Screen name | Actual UI label |
| Role | Admin, Enduser, reseller/scoped role |
| Entry point | Tab, modal, deep link, or action |
| Primary user task | What the user is trying to do |
| Data source | Existing API action or server-rendered data |
| Key DOM hooks | IDs, classes, data attributes, JS selectors |
| Main interactions | Search, filter, submit, refresh, confirm, etc. |
| States | Loading, empty, success, warning, error, stale, offline |
| Responsive behavior | Desktop, tablet, mobile |
| Risk | Read-only, privileged, destructive |
| Theme support | Light and Dark; Light default; persistent user-controlled switcher |
| Test evidence | Screenshot, test, or browser observation |

## 5. Interaction and state requirements

Every interactive screen must define:
- Initial state.
- Loading state.
- Empty state.
- No-results state.
- Validation state.
- Success state.
- Failure state.
- Stale/offline state if telemetry-dependent.
- Permission-denied state if role-dependent.
- Disabled state where an action is unavailable.

Do not redesign only the default successful state.

## 6. Navigation consistency

Use consistent naming, ordering, icon style, active state, and keyboard behavior.

Do not:
- Add duplicate navigation destinations.
- Hide a frequently used operation in an unexplained overflow menu.
- Use different tab styles on Admin and Enduser without a clear density reason.
- Make mobile navigation a tiny row of icon-only buttons.
- Change deep links or tab identifiers without updating routing and tests.

## 7. Theme consistency requirement

All Admin and Enduser plugin-owned surfaces must support the same Light and Dark design system. Light is the default; users can switch explicitly between Light and Dark. Do not add an automatic System mode. Persist the selection and apply it to charts, dialogs, popovers, native form controls, and dynamically injected UI. Do not alter Webuzo's global shell.

## 8. Copy and terminology

Use precise infrastructure terminology:
- CPU core-equivalent.
- Account CPU allowance.
- Total cgroup memory.
- Anonymous memory.
- File/page cache.
- Swap.
- Disk throughput / IOPS.
- Active tasks / threads.
- Throttling.
- OOM termination.
- Configured limit.
- Effective limit.
- Telemetry freshness.

Avoid vague labels such as:
- “Performance score”.
- “AI insights”.
- “Smart optimization”.
- “Powerful analytics”.
- “Everything is fine”.

Use plain-language explanations when a technical term may be unfamiliar, without changing the metric's meaning.
