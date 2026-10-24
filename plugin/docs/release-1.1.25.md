# Gauge correction — 1.1.25

The circular arc and liquid level now use the same clamped 0–100 percentage, with no artificial minimum fill. 0% is empty, 50% half and 100% full; values above 100% cap the visual fill while retaining the actual metric in text/tooltip. Missing/non-finite data has a neutral unknown state, not a fabricated usage value. SVG pathLength normalizes each ring to 100 units; surface wave decoration no longer scales through the full liquid depth.

Admin Hardware Detection is inventory, not a usage metric; its fixed 60% fill is removed. Shared CPU Headroom shows configured hosting allocation divided by visible vCPU capacity: 340% on four vCPUs is 85% of 400%, not 100% usage. RAM uses actual golden.slice memory.current / memory.max. System Load is load1 / vCPU count, not CPU utilization. Zero RAM/load stays zero; fixed 45%/minimum 5% fallbacks are removed. Initial server-rendered fills match these semantics, including enduser tasks. Admin trend lines start with real timestamped samples, with no fabricated prehistory. No server resource limits were changed.

Focused validation: 18 gauge input cases plus CPU/RAM/load normalization and PHP initial-fill assertions, visual 0/25/50/75/100/unknown fixtures and live card/API verification. Historical lifecycle/configuration evidence remains separate; no new whole-server readiness certificate is asserted.

# Resource Manager 1.1.25 — accurate card gauges

## Where to find it

Webuzo > Plugins > UNISELV Resources > System & Agent Health > Runtime Governance & Configuration Evidence.

Observed controls, in order: Refresh Evidence; Reconcile PHP Changes; Recover Pending Operation; Prepare & Download Comparison. PHP Lifecycle Automation contains Retire Runtime, or Enable Runtime for an intentionally retired version. These are operational actions, not independent configuration forms. Defaults, overrides and hardware planning remain in the generator Global Inputs.

## PHP lifecycle automation

The background agent checks once per minute, outside telemetry collection. Maintenance Mode pauses background governance. An installation must remain unchanged across two scans at least 60 seconds apart. PHP INI and native global FPM values must match the root-owned reviewed generator profile. Pool parsing uses validation-only mode. Native FPM syntax is checked before mutation; an unused PHP version is tested using a temporary private validation pool, without starting a workload or editing native configuration.

The existing journaled lifecycle transaction then onboards or repairs the version, preserving aggregate physical RAM/CPU boundaries and accounting for additional version overhead. Registration, launcher and coordinator/health states are verified afterward. Binary changes remain pending until a stable observation and successful reconciliation. Failed attempts have a five-minute cooldown and three-attempt ceiling for the same fingerprint. Reconcile PHP Changes clears that retry history, but does not bypass stability, global setting, syntax or lifecycle guards. Native PHP global settings are still applied manually per installed version; automation never invents their values or creates manual per-user FPM overrides.

To uninstall: move all domains to another registered version using Webuzo; verify HTTP behavior and that no native/managed pools remain; choose Retire Runtime and confirm; verify retired status; only then uninstall PHP in Webuzo. Retirement persists through scans. Enable Runtime explicitly permits registration again. If software was removed first, missing installation files block automatic destructive cleanup: restore the installation for reviewed recovery/retirement. Registry entries are never blindly deleted.

## Expected configuration source

The root-owned file is `/etc/webuzo-isolation/generator-profile.json`, mode 0600 recommended. Both a native Global Inputs JSON export and the historical `{ "configuration": ... }` wrapper are accepted. The native combined Golden Shield export is normalized to the reviewed Golden/isolation policies; no settings are applied during normalization. Generator validation errors block automation. Missing/unreadable profiles are reported, not replaced with hardcoded tuning.

For an updated expected profile, export the configuration from the canonical generator Global Inputs after reviewing the actual hardware, versions and overrides. Transfer it privately to the server. Replace the complete profile file from its opening `{` through its final `}`; there are no surrounding directives or insertion anchors. Do not append a second JSON object. Keep a root-private backup, install the reviewed file with root ownership and restrictive permissions, then choose Reconcile PHP Changes. A JSON export does not apply PHP, Apache, SQL or resource-plan settings to the server.

## Configuration drift and account exceptions

Global Settings Drift lists PHP version, section, directive, expected and actual values. The all-section server comparison uses the same allowlisted configuration audit, normally cached for five minutes; explicit reconciliation and export refresh it. It compares configured values/service/kernel checks, not application throughput. Configuration Audit Coverage lists every generator section and distinguishes configured-value checks from sections not checked by this audit; zero mismatches is not whole-server certification. A drift/error is not silently repaired by changing tuning values; apply the shared generator values in the correct global panel, then recheck.

Account Inheritance Exceptions scans `/home/*/public_html`: all root INI files first, then nested directories breadth-first. It never follows a tenant symlink when reading INI content; each path component is opened with no-follow descriptor access. Reads, elapsed time, filesystem entries and result count are bounded to protect the agent. Coverage, unreadable paths and bounded-stop reason are retained in exports. A large first site cannot hide another account's root override. Alternate domain document roots, `.htaccess`, per-pool administrative INI and application `ini_set` are outside this scanner; an incomplete scan is explicitly labelled. It does not remove user overrides.

## Capacity diagnostics

Capacity Events shows a bounded last-hour journal sample; Recent Capacity Event Timeline shows time, unit and reason. Reasons include host reserve, shared PHP budget, account memory, active-pool ceiling, account memory/task constraints, proxy queue full/deadline, backend unavailable, request deadline and relay I/O failure. Admission diagnostics include available/reserved/account memory where known. Event timestamps enable minute buckets in JSON exports. These are diagnostic events, not unique visitors or exact failed-request totals: an admission failure and a proxy failure can concern the same request. Journal rate limiting/retention and the sample cap apply. Customer-facing 503 responses retain the neutral white/red animated design, no-store and Retry-After behavior.

## Recovery and export

Recover Pending Operation attempts to restore the recorded pre-operation files, registration and service state. The journal's owned file/unit paths are validated before restoration. It does not blindly delete conflicting staging files; failed recovery keeps the journal and actionable status. Lifecycle Recovery History exposes metadata only, not private file snapshots.

Long operations run asynchronously with a job identifier, protected against overlap. Browser polling does not cancel the server operation. Agent restarts mark unfinished jobs interrupted; background scans cannot overwrite the last administrator job. Mutations require the existing root-only IPC boundary and browser CSRF validation. Resellers/endusers cannot read or operate server-wide governance. Administrative operations and actual background repairs are audited; unchanged periodic scans do not flood the audit table.

Prepare & Download Comparison produces an administrator-only JSON report with expected/actual rows, override coverage, bounded event summaries, lifecycle metadata and readiness scope. No credentials, raw logs, private journal snapshots or application content are exported. Account paths are included; share privately with administrators.

## Release installation and source placement

The live reviewed maintenance upgrade has already been applied with root-private backups and ownership/Golden restoration hashes updated together. Plugin installation checks compatibility with an existing adopted isolation runtime before deploying agent files. An unknown/different adopted implementation blocks activation; it is not silently overwritten. Fresh installs deploy the bundled runtime. Upgrading another protected server requires the same reviewed maintenance procedure before activation.

Install the complete `uniselv-resman/` package. Plugin files map to `/usr/local/webuzo/plugins/uniselv-resman/`; agent/core deployment copies map to `/usr/local/uniselv-resman/`; the isolation launcher implementation additionally maps to `/usr/local/sbin/webuzo-isolation.py`. Existing files are full replacements, never appended. New files begin at their first line and end at their last line. `source-changes-1.1.25.json` and `.md` provide exact replacement/insertion anchors, generated code separately from illustrative after-edit context, duplicate guidance, save and verification steps. Save UTF-8/LF; preserve ownership and installer-applied execution permissions. Run syntax checks, regression suite, actual service/API/HTTP verification and archive closure checks after applying a reviewed release.

## Evidence boundaries

See runtime-governance-validation-1.1.24.json for the dated checks. Synthetic unused PHP fixtures exercise actual systemd/FPM and rollback without customer pools; they are not a Webuzo package-manager installation certificate. Historical 1.1.23 reboot/native provisioning evidence remains historical. This release does not certify clean OS deployment, every vendor event, full protection uninstall/reinstall, every account/domain combination, alternate-root override coverage, host swap boundaries or WordPress shopping capacity. CSF is outside this task. There is no bug-free or universal production-readiness guarantee.
