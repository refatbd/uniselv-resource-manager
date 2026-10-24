# Current-host readiness follow-up — 1.1.30

The current-host core protection and selected Shared Redis checks passed. The owner selected one shared cache service without per-user allocation. Shared Redis is not tenant-isolated. These results are not universal production certification.

## Fixed issue

After complete 1.1.29 removal/reinstall, reboot left the native PHP84 compatibility bridge inactive while its isolated coordinator and health master were running. Origin HTTPS still returned 200, but mechanical verification correctly failed. Managed PHP repair now validates/activates the native bridge. Governance checks it before declaring health and verifies it after repair.

## Verified results

- 151 isolated Linux regressions passed, including inactive-bridge recovery and failed post-repair verification.
- Complete current-host 1.1.30 plugin-owned protection removal/reinstall passed during controlled maintenance; account history, 25 accounts, JSON policy values and native global FPM defaults were retained. Native Shared Redis settings were restored on removal and selected shared limits were reapplied on reinstall, with matching file ownership. See JSON for exact elapsed seconds.
- Actual 1.1.30 governance repaired the inactive PHP84 bridge; final-release reboot returned all four coordinators and four native bridges automatically. They remained stable for 45 seconds before audit; no manual post-boot service start was used.
- Final audit: 331 checks, zero mismatches; account placement and override recovery passed. All 25 temporary native HTTP placement probes passed and were removed.
- Native disposable full-account archive opened correctly; an intentionally corrupted marker was restored with matching content hash and UID. A second full native account restore also restored an intentionally corrupted 1,000-row database from its included SQL archive. Separate MariaDB logical backup restored 1,000 rows exactly and disposable databases/accounts were removed.
- Private current rollback archive verified 1,108 regular files. An earlier pre-maintenance off-host control copy matched its SHA-256. Rollback was exercised during safety-aborted test attempts. This is not bare-metal disaster recovery.
- One authorized outbound test email was accepted by Gmail over TLS; the owner confirmed receipt. In-app report generation/storage passed separately.
- ClamAV accepted the clean fixture and detected EICAR; fixtures removed and daemon enablement preserved. Public TLS verification passed; actual renewal was not due.

## Owner-selected Shared Redis

One shared loopback cache is retained. No per-user instances, calculations or reserved account allocations are required. Shared access is the selected trust model; it is not account isolation. Private pressure tests exercised eviction and connection refusal without pressuring customer keys.

## Remaining concrete gaps

### Backup schedule and disaster recovery

No scheduled jobs configured at current inspection. A disposable native full-account archive restored an intentionally corrupted file and 1,000-row database. Separate MariaDB logical restore also passed. Current scheduled retention, complete disaster restore and off-host recovery are not implied.

### Automatic mail/scanner/alert integrations

Manual transport, report storage and scanner fixtures passed only. The report API stores reports in-app; it does not implement SMTP delivery. ClamAV daemons retained disabled state. The EICAR fixture does not attest a scheduled scan, signature updater, mail routing on detection, or unattended completion.

### Actual certificate renewal

Not due; native Renew controls disabled. Current public certificates passed validation. No forced production reissuance or future-CA success is claimed.

### External environments

Separate environment/access required. No disposable clean VPS is available. Actual provider hardware resize, clean-OS installation, full bare-metal disaster restore and unavailable future vendor releases cannot be proven on this current host.

### Application workload capacity

Website audit deferred by owner. No WordPress fixes, orders, payments or new maximum-shopper claim. Prior bounded sustained/runtime and website-latency evidence remains dated 1.1.29.

## Scope and cleanup

CPU/RAM safety, account resource limits, native global FPM/OPcache values and proxy/admission behavior were not increased. CSF remains owner-managed. Maintenance rule removed, cron restored, rollback timer disarmed, and customer website data unchanged. Private recovery data is excluded from the downloadable plugin/generator packages.

Exact code replacements, verified anchors and context are in source-changes-1.1.30.md/.json and generator-source-changes-1.1.30.md/.json. Prefer the complete reviewed archives; these guides are not extra post-install commands.
