# Redesign Acceptance Checklist

A redesign is complete only when all applicable items are verified.

## A. Product and design
- [ ] The design clearly fits a server resource monitoring and infrastructure governance product.
- [ ] The design is not a generic AI SaaS template.
- [ ] Admin and Enduser surfaces share one visual language.
- [ ] Admin remains operationally dense where needed.
- [ ] Enduser remains simpler and focused on personal account usage.
- [ ] Existing brand assets are respected.
- [ ] No unrequested public marketing surface or product feature was invented.
- [ ] All design decisions have documented rationale.

## B. Design system
- [ ] Semantic colour tokens are used.
- [ ] Light theme is complete across Admin and Enduser.
- [ ] Dark theme is complete across Admin and Enduser.
- [ ] Light is the default for first-time users.
- [ ] An accessible Light/Dark switcher is available in Admin and Enduser.
- [ ] Selected theme persists across page visits and sessions.
- [ ] No automatic System/Auto mode overrides the user's selection.
- [ ] Dialogs, toasts, dropdowns, charts, form controls, and dynamic content follow the selected theme.
- [ ] Webuzo global chrome and other plugins are not modified.
- [ ] Typography and numeric alignment are consistent.
- [ ] Spacing, radii, borders, and component states are consistent.
- [ ] No unnecessary card nesting or decorative effects remain.
- [ ] CSS is scoped and duplicate rules are addressed.

## C. Functional integrity
- [ ] Webuzo Admin integration still works.
- [ ] Webuzo Enduser integration still works.
- [ ] Existing hooks and entry points are preserved.
- [ ] Existing API action names and contracts are preserved.
- [ ] Existing JavaScript selectors and DOM hooks are preserved or comprehensively migrated.
- [ ] Search, filters, pagination, refresh, charts, forms, dialogs, and exports work.
- [ ] Permission-based visibility remains correct.
- [ ] Tenant isolation remains correct.
- [ ] CSRF protections remain correct.
- [ ] No backend business logic was changed unintentionally.
- [ ] No existing feature was silently removed.

## D. Data and telemetry
- [ ] All displayed metrics come from real data.
- [ ] No fake values or fake trends are present.
- [ ] Units are visible.
- [ ] CPU usage and account allowance remain distinct.
- [ ] Memory breakdown remains accurate.
- [ ] Stale/offline/waiting/unavailable states are explicit.
- [ ] Chart time ranges and thresholds are clear.
- [ ] Numeric precision and rounding are appropriate.

## E. Responsive quality
- [ ] 1440 × 900 tested.
- [ ] 1280 × 800 tested.
- [ ] 1024 × 768 tested.
- [ ] 768 × 1024 tested.
- [ ] 390 × 844 tested.
- [ ] 360 × 800 tested.
- [ ] No horizontal page overflow.
- [ ] Tables remain usable.
- [ ] Charts remain readable.
- [ ] Navigation and dialogs remain usable.
- [ ] Long values and technical strings do not break layout.

## F. Accessibility
- [ ] Keyboard-only navigation tested.
- [ ] Focus visibility tested.
- [ ] Contrast tested in both Light and Dark themes.
- [ ] Forms have persistent labels.
- [ ] Dialog keyboard behavior tested.
- [ ] Async status and error announcements tested.
- [ ] Reduced-motion preference respected.
- [ ] Status is not communicated by colour alone.

## G. Engineering and security
- [ ] Work was performed on a feature branch.
- [ ] No unrestricted production root access was used.
- [ ] No secrets were committed or copied into reports.
- [ ] No destructive production command was run without explicit approval.
- [ ] Relevant syntax and repository tests passed.
- [ ] Browser console and network checks completed.
- [ ] No unexpected PHP/server errors remain.
- [ ] Existing security boundaries are preserved.
- [ ] Backup and rollback plan is documented.
- [ ] Package contents and checksum verified if packaging changed.

## H. Evidence and handoff
- [ ] Repository audit report completed.
- [ ] Screen inventory completed.
- [ ] DOM/JavaScript contract map completed.
- [ ] Design decisions recorded.
- [ ] Before/after screenshots supplied.
- [ ] QA report completed.
- [ ] Changed files and commits summarized.
- [ ] Known limitations documented.
- [ ] Deployment steps reviewed.
- [ ] Owner explicitly approved production deployment.

## Final status

Choose one:
- **PASS:** all critical requirements are verified; no unresolved high-severity issue.
- **PASS WITH WARNINGS:** no critical regression, but documented non-blocking issues remain.
- **FAIL:** a critical behavior, security, accessibility, data-integrity, or rollback requirement is not met.

A screenshot-only review can never receive PASS.
