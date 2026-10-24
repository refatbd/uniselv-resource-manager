# Resource Manager 1.1.27 — current-host test results

Current-host bounded lifecycle passed. This is not a universal production certificate. Website audit/fixes remain deferred by the owner.

119 isolated tests, four adversarial suites, eight generator cases and 331 configured/runtime value checks passed. Configuration mismatches: zero. Original 25 hosting accounts remain; temporary fixtures and PHP 8.3 were removed.

| Test | Result | Exact scope |
|---|---|---|
| Generated/live configuration parity | PASS-live | 331 allowlisted checks, zero mismatches; all-section coverage distinguishes sections without checks. |
| Native provisioning and plan transition | PASS-live-bounded | Create/delete; PHP 7.4/8.1/8.2/8.4 assignment/global inheritance; Go/Pro kernel limits. No manual per-user FPM setting. |
| Temporary boost transaction lifecycle | PASS-live-and-isolated | Apply, overlap refusal, cancellation, expiry and interrupted-application recovery; UID/plan/billing/rollback failure paths isolated. |
| Native PHP 8.3 lifecycle | PASS-live | Vendor native install; global profile inherited; automatic onboarding; real contained HTTP; in-use retirement refusal; switch away; retirement/remove. Restored original global FPM defaults. |
| Native vhost regeneration and suspension | PASS-live | Non-destructive --rebuild_vhost preserved probe content; suspension stopped probe execution and unsuspension restored routing. --rebuild-user separately observed resetting disposable content. |
| RAM hard limit | PASS-live-bounded | Actual disposable account MemoryMax hard OOM verified; temporary MemoryHigh adjustment restored. First high-backpressure observation is retained separately. |
| Task boundary and event reporting | PASS-live-and-isolated | Actual TasksMax 64 refused the next fork; descendant-local kernel events read correctly, plus three aggregation regressions. |
| Disk and inode quota boundaries | PASS-live-bounded | Disposable native quota rejected byte writes and inode creation with EDQUOT; data removed. |
| I/O | PASS-live-smoke | 64-MiB direct I/O under native device rule; this run does not recertify all plan throughput/IOPS ceilings. Older multi-plan measurements remain dated evidence. |
| Native cron and PAM session startup | PASS-live-bounded | Real disposable native cron and runuser initial instruction in correct account cgroup. Earlier real SSH entry remains historical. |
| IPC, file, process and reseller authorization | PASS-live-and-isolated | Private root controls denied to tenant; token spoof/foreign PID/stale PID rejected; own process controlled; reseller aliases/runtime totals scoped in regression. |
| Database and agent shared-service recovery | PASS-live-bounded | Dedicated SQL probe read/mixed transaction/invariant and cache, controlled MariaDB restart, agent SIGKILL automatic recovery. Post-reboot SQL/cache also passed. No WordPress DB changes. |
| Apache boot ownership | PASS-live-after-fix | First reboot failed initial forking/PID-file startup. Foreground tracked master fixed; native status/reload/restart passed. Second boot started Apache immediately without timeout/restart retry. |
| Second boot and retained state | PASS-live-bounded | New boot ID; protected files/accounts preserved; all core units active; native boot PHP reconciliation briefly pending then completed; no pending journal; private HTTP contained. |
| Uninstall preflight, vendor replacement and recovery failure | PASS-isolated-and-targeted-live | 117 then 119 isolated tests; actual existing-stack installer rerun; full isolation removal refused while Golden depends on it; actual pending PHP84 recovery tested. Full protection removal not attempted on live accounts. |
| Governance journal delay | PASS-live-after-fix | Unit-glob journal read timed out and prevented snapshot refresh. Bounded shared tail now finishes; unavailable journal reads produce explicit partial-coverage evidence while current runtime/config snapshot is retained. Two new regressions. |
| Adversarial handlers | PASS-isolated | Four suites passed; R6 38 assertions, R7 31 assertions. Synthetic policy fixtures are not a live overload certificate. |
| Hardware and overselling derivation | PASS-generated | Eight cases: 2/4/8/16 vCPU, 4/8/16/32 GiB, 100/300 percent overselling. Physical safety budgets unchanged by sales overselling; embedded source hashes verified. |
| Cleanup | PASS-live | Original 25 accounts; disposable account/home/pool/probe gone; PHP83 removed; temporary cron/scripts/IO/quota fixture data removed. All 25 account placement and boost recovery PASS. |

## External, unavailable and owner-excluded cases

- **Clean-OS install / complete protection uninstall-reinstall / disaster restore — NOT-RUN-external-environment:** No disposable VPS available; owner explicitly requested current-host tests only.
- **Native PHP patch update — NOT-AVAILABLE-vendor:** No PHP patch update in the current native catalogue. Actual PHP83 install/remove and isolated vendor replacement are separate.
- **Physical hardware resize / future vendor and OS versions — NOT-RUN-external-environment:** Generated matrix and current supported installation do not certify an actual resize or future release.
- **RAM plus active host swap — NOT-RUN-host-swap-off:** Host swap intentionally remains disabled; do not infer active swap enforcement from memory.max.
- **WordPress audit / shopper capacity — DEFERRED-owner:** Website work explicitly last. No new maximum-shopper claim from these server fixtures.
- **CSF / lfd — EXCLUDED-owner-managed:** lfd.service observed failed after reboot; owner requested no CSF changes.
- **Optional unrelated services and full commercial features — SEPARATE-PENDING:** Mail delivery, TLS renewal, Redis tenancy, Backuply restore, malware/alerts, filesystem jail and per-account SQL CPU/RAM isolation are not certified by this core lifecycle run.

## Corrections found in this pass

Verified boost restoration and interrupted intent; lifecycle removal preflight and native enablement recovery; canonical policy warm retention; reseller audit data scoping; descendant task-event counting; Apache boot ownership; and bounded journal diagnostics were corrected. Exact code, anchors and save/verification steps are in source-changes-1.1.27.md/.json. Old failures and corrected test-fixture assumptions remain in the local evidence rather than being relabelled successful.

The second reboot tested the released Apache/isolation core. Subsequent journal diagnostic and storage-warning UI refinements were verified by agent restart, live fresh scan, regression and browser refresh; there was no third whole-host reboot for those refinements.
