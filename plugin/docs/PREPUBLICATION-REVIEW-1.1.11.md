# Prepublication review — UNISELV Resource Manager 1.1.11

Date: 2026-10-18. Environment: Ubuntu 24.04, Webuzo 4.8.4, 4 vCPU, approximately 7.57 GiB visible RAM. Review covers deployed Admin/Enduser workflows, desktop and 390px browser layouts, backend contracts and regression tests. This report supersedes earlier UI/readiness claims for this release.

## Findings corrected

| Finding before review | Correction and effect |
|---|---|
| Current Usage/history failed with real records: `sqlite3.Row has no attribute get` | History rows are converted to dictionaries. Real account charts, totals and hourly records load. A nonempty SQLite regression reproduces the old failure. |
| Overview RAM always displayed zero because it summed nonexistent `samples.mem_bytes` | Read aggregate `golden.slice/memory.current`, including shared services. Missing data is Unavailable. Live reading was approximately 412 MiB. |
| Overview could show an Auto recommendation instead of applied Manual policy; absent hardware became 4 CPU/8 GB | Display configured policy. Remove fixed hardware and capacity fallback values. Actual zero commitment remains zero. |
| Storage UI expected a nested API envelope while the backend returned flat settings | Return measured DB/WAL/SHM footprint, actual row counts and nested settings. Live DB approximately 20.8 MiB, over 175,000 samples. |
| Retention Save dereferenced a nonexistent input; submitted values were not bounded before SQL | Add Storage Warning Threshold field and validate the entire batch before mutation. Actual browser Save succeeded with unchanged settings. Label threshold as an indicator, not an enforced disk quota. |
| Agent RSS used the wrong response key and UI claimed a static 64M constraint | Read RSS and actual service memory.max. This VPS reports 128 MiB. |
| Top consumers were the first alphabetical accounts | Rank by sampled CPU, then memory; explicitly label the table as the latest sample at page load. |
| Boost/mapping choices were hard-coded to selected named plans and old RAM values | Read verified native plan files; show actual CPU/RAM labels. All installed native plans remain selectable. Invalid mappings display a Missing native plan warning. |
| Database initialization silently resurrected deleted demo billing mappings | Stop automatic demo mapping seeding. Preserve existing operator mappings and role defaults. Restart regression verifies persistence without reseeding. |
| Package names, confirmation text and audit detail JSON could be interpreted as HTML or break inline handlers | Escape data, use event listeners for dynamic details/delete actions, and render JSON as text. A literal HTML/quote package was created, inspected and removed through the actual UI. |
| Branding accepted executable links or arbitrary CSS values | Validate HTTP(S) URLs, disallow embedded credentials, validate #RRGGBB and locale before SQL writes. Render-time validation protects legacy settings too. |
| CSRF had a predictable shared fallback when session identity was absent | Require Webuzo session identity or its authenticated session path; otherwise fail closed. Missing-token refusal and real browser saves tested. |
| Admin live polling was never started; failed/stale customer polling still said LIVE | Start polling in both roles. Show sample age, unavailable state and connection failure while retaining last values. |
| Four dashboard waves were static illustrations presented as live trends | Draw distinct measured samples since the page opened, retain up to five minutes, suppress until two samples arrive, and expire old samples. Real ten-sample idle trends verified. |
| Mobile header/grids overflowed, navigation consumed many rows, history range buttons overflowed | Wrap content, contain tables, provide an accessible Section selector using every existing navigation item, and wrap range buttons. Admin/customer sections fit a 390px viewport. |
| Confirmation dialogs had no Escape/focus handling; many fields lacked accessible names | Add dialog semantics, focus trap, Escape cancellation and focus restoration; name fields and add visible focus/reduced-motion handling. |
| Hardcoded 100% Active/Contained labels and Help promised full CloudLinux/isolation parity | Derive synchronized account counts; describe observed process coverage as a point-in-time check. Correct tasks versus requests, shared-resource limits, stop-process risks and actual menu/button names. |
| Documentation link pointed at a historical placeholder; units/version metadata were inconsistent | Placeholder Docs opens bundled local Help. Align release version, use MiB/KiB for binary charts, label plotted averages and unknown historical combined RAM+swap limits honestly. |

## Verification completed

- Nine backend regression tests and eight frontend regression tests passed (17 total).
- PHP syntax lint passed; PHP checks verified session-bound CSRF, missing-token refusal and safe legacy link rendering.
- Actual Admin browser: overview, account directory, analytics, audit, Golden Shield, capacity, reports, billing/permissions, logs, health and Help navigation inspected. Retention Save, literal package create/delete, confirmation Escape/focus restoration tested.
- Actual customer browser: dashboard, Current Usage, Historical Charts, snapshots, notifications and searchable role-specific Help inspected. Current Usage renders eight resource cards, including explicitly unavailable Entry Processes; historical swap ceiling is labelled unavailable rather than invented.
- 390px Admin checks: overview, accounts, Golden Shield, health, branding and Help. Customer checks: all six sections. Final document width never exceeded the viewport in these checks; tables scroll within their containers. Desktop visual screenshot preserved.
- Live privileged broker checks: customer requesting ub4 receives only ub3; customer admin-overview access refused; nonempty ub3 history succeeds; storage and real memory cap verified. These are authorization checks, not a substitute for penetration testing.
- Webuzo, agent and Golden Shield services remained active. Source/deployed files compared by SHA-256; final package sync manifest preserved.
- Review mapping fixture deleted; no native plans or quotas changed. Backup: `/root/webuzo-validation/prepublish-1.1.11`.

## Scope and remaining environment notes

- Existing VPS contains a legacy Bronze -> default billing mapping with no matching verified native plan. The UI now warns. Existing operator mappings were preserved; new installations no longer receive demo mappings. Review the mapping before connecting billing.
- PHP 8.2 CLI (when loading its normal INI) emits a missing `libsasl2.so.3` dependency warning for `memcached.so`. The plugin does not require memcached. Its extension/package repair is a separate server configuration task; syntax lint used `-n` and is not evidence of extension health.
- An unattended external WHMCS/Blesta Webuzo HTTP route is not certified by this release. Correct the integration route/authentication and validate it with a dedicated account before using automated billing synchronization; an unauthenticated customer-port curl example was removed.
- No fresh OS, reboot, uninstall/reinstall, renewed overload benchmark or hardware-resize lifecycle was rerun for 1.1.11. Enforcement code is unchanged from the bounded 1.1.10 validation. Earlier lifecycle/capacity reports retain their original environment and scope.
- This is a tested prepublication UI/logic maintenance release. It does not certify universal workload capacity or CloudLinux equivalence.

## Evidence

Local files in `vps-validation`: `RESMAN-1111-LIVE.json`, `RESMAN-1111-UI.json`, `RESMAN-1111-UNIT-TESTS.txt`, `RESMAN-1111-PHP-CHECKS.txt`, `RESMAN-1111-SYNC.json`, `RESMAN-1111-DESKTOP.png`, `RESMAN-1111-MOBILE.png`.
