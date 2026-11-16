# UI, Functional, Accessibility, and Release QA Plan

## 1. Test environments

Use:
- Local checkout for static and syntax checks.
- Staging Webuzo server for integration and browser testing.
- Dedicated Admin, Enduser, and reseller test accounts where applicable.
- Sanitized, deterministic test data.

Never run destructive UI tests against real customer accounts.

## 2. Repository and static checks

First inspect which scripts and test files actually exist. Do not assume a command in an old README is still valid.

Potential checks, only when the relevant runtime and files are present:
- PHP syntax checks for changed PHP files.
- JavaScript syntax check for changed JS files.
- Python compile checks for changed Python files.
- Existing repository test suite.
- CSS lint or formatting checks if already configured.
- Package/archive integrity and checksum validation if packaging is changed.

The public repository lists test files related to native reload, OpenSwoole governance, platform manager, and telemetry history. Verify their current names, dependencies, and whether they are safe for staging before running them.

Do not run an unverified test suite on production.

## 3. Browser and visual matrix

Minimum viewports:
- 1440 × 900.
- 1280 × 800.
- 1024 × 768.
- 768 × 1024.
- 390 × 844.
- 360 × 800.

Minimum theme/environment matrix:
- Light theme selected while OS/browser preference is Light.
- Light theme selected while OS/browser preference is Dark.
- Dark theme selected while OS/browser preference is Light.
- Dark theme selected while OS/browser preference is Dark.
- Change OS/browser preference after an explicit UNISELV selection and verify the selected theme remains unchanged.
- Verify the Light/Dark switcher is available and works in Admin and Enduser.
- Verify dialogs, dropdowns, charts, form controls, and dynamically injected content follow the selected theme.

Minimum role matrix:
- Admin.
- Enduser.
- Reseller/scoped role if implemented.

Capture screenshots for:
- Admin Overview.
- Admin All Accounts.
- Admin audit/governance view.
- Admin system/platform operations view.
- Enduser Dashboard/Current Usage.
- Enduser Processes.
- Enduser History.
- At least one modal/dialog.
- At least one loading, empty, error, and success state.

Use the same viewport, role, theme, and test data for before/after comparisons.

## 4. Functional regression matrix

Verify all applicable existing behaviors:
- Navigation and tab switching.
- Direct links/deep links.
- Search and filters.
- Pagination.
- Refresh and telemetry polling.
- Time-range selection.
- Chart tooltips and data inspection.
- Modal open/close and focus restoration.
- Form validation and submission.
- Confirmation dialogs.
- Toast success/error states.
- Notification acknowledgement.
- Snapshot browsing and export.
- Permission-based visibility.
- Theme selection and persistence.
- Responsive mobile navigation.
- Keyboard navigation.

For every mutation:
- Verify the correct target.
- Verify authorization is enforced server-side.
- Verify CSRF protection remains active.
- Verify the UI prevents accidental duplicate submissions.
- Verify the result and failure state are truthful.

## 5. Telemetry correctness

Confirm the redesign has not changed or obscured:
- CPU core-equivalent usage.
- Account CPU allowance percentage.
- Configured CPU quota.
- Effective CPU limit.
- Total cgroup memory.
- Anonymous memory.
- File/page cache.
- Swap usage.
- I/O throughput and IOPS.
- Task/thread count.
- Throttling and OOM events.
- Telemetry sample timestamp and freshness.

Check:
- No data is not displayed as zero.
- Stale data is not presented as live.
- No synthetic trends appear while waiting for real samples.
- Chart units and time windows are visible.
- Thresholds and limits are correctly identified.
- Rounding does not materially change interpretation.

## 6. Accessibility

Target WCAG 2.2 AA where applicable.

Check:
- Contrast for normal and large text in both Light and Dark themes.
- Focus visible on all interactive elements.
- Logical keyboard order.
- Keyboard operation of tabs, menus, dialogs, and controls.
- Correct labels for inputs.
- Semantic headings and tables.
- Dialog role, name, focus trap, Escape behavior where safe, and focus restoration.
- Async status announcements.
- Error identification and instructions.
- Reduced-motion behavior.
- Touch target size and spacing.
- Status not communicated by colour alone.

## 7. Browser and server diagnostics

Inspect:
- Browser console errors and warnings.
- Failed network requests.
- Missing assets.
- PHP errors in staging logs.
- JavaScript exceptions.
- CSS overflow and layout shifts.
- Slow or repeated requests introduced by the UI.
- Theme flash or incorrect overlay theme.
- Unexpected calls to privileged actions.

Do not copy sensitive log lines into the report. Redact secrets, usernames, domains, paths, IP addresses, and customer data.

## 8. Performance and compatibility

- Do not add heavy dependencies for cosmetic improvements.
- Do not add remote CDN dependencies.
- Avoid excessive DOM updates during telemetry refresh.
- Keep charts responsive and efficient.
- Avoid layout shifts when async data loads.
- Preserve compatibility with the supported Webuzo/PHP/browser environment discovered during audit.
- Test with the actual browser versions supported by the target hosting panel.

## 9. Required QA report

Create `docs/antigravity/qa/REDESIGN-QA-REPORT.md` with:
- Commit SHA and build/package version.
- Test environment and browser version.
- Test accounts/roles (non-sensitive labels only).
- Viewports and themes tested.
- Screens tested.
- Functional tests passed/failed/not run.
- Accessibility findings.
- Visual comparison evidence.
- Console/network/server errors.
- Telemetry correctness findings.
- Security and permission regression findings.
- Known limitations.
- Remaining risks.
- Final recommendation: PASS, PASS WITH WARNINGS, or FAIL.

Never claim a test passed unless it was actually executed and its result inspected.
