# Server Access and Safety Policy for Gemini Antigravity

## 1. Default rule

**Do not give an AI coding agent unrestricted root access to a production Webuzo server.**

The plugin contains privileged infrastructure controls, including resource governance, process termination, PHP runtime operations, systemd integration, cgroups v2, and platform services. A visual redesign does not justify unrestricted production access.

## 2. Preferred environment order

1. Local repository checkout.
2. Dedicated staging VPS that mirrors the production software versions.
3. Sanitized test accounts and non-sensitive test data.
4. Read-only production observation only if a specific verification cannot be reproduced in staging.
5. Production change only after owner review and explicit approval.

## 3. Credentials

- Never paste passwords, private keys, API tokens, webhook secrets, database credentials, or session cookies into repository Markdown.
- Never commit credentials to Git.
- Never place secrets in screenshots, browser console logs, terminal transcripts, or audit reports.
- Use a separate, revocable, time-limited account for the agent.
- Use an SSH key restricted to the staging host and the minimum required account.
- Do not reuse the owner's personal SSH key.
- Do not expose production secrets in `.env`, PHP config, shell history, or copied diagnostics.
- Redact credentials and tenant-identifying data from all reports.

## 4. Access levels

### Initial audit
- Read-only repository access.
- Read-only staging SSH access.
- Read-only browser access with a test account.
- No ability to restart services, kill processes, change plans, alter cgroups, or modify system configuration.

### Implementation
- Local or staging working tree only.
- Write access to a dedicated feature branch.
- No direct write access to production plugin files.
- No unrestricted `sudo`.
- No production database or daemon mutation.

### System-level verification
If a test genuinely requires privileged access:
1. Antigravity explains the test and exact commands.
2. The owner reviews the commands and expected effects.
3. The owner executes them manually or grants a narrowly scoped, temporary permission.
4. The result is recorded with sensitive output redacted.

Do not create a generic root shell or unrestricted command-execution endpoint for the agent.

## 5. Actions requiring explicit approval

Never execute any of the following on production without explicit owner approval and a verified rollback plan:

- Restart, stop, reload, or enable/disable systemd services.
- Kill or terminate processes.
- Change cgroup CPU, memory, I/O, or task limits.
- Apply, cancel, or synchronize resource plans or overrides.
- Reconfigure Golden Shield or system headroom.
- Install, uninstall, enable, or disable plugin components.
- Change PHP versions, extensions, FPM pools, or runtime configuration.
- Change Redis, OpenSwoole, Laravel workers, Horizon, Reverb, scheduler, or Chrome engine services.
- Modify Webuzo, Apache, Nginx, systemd, cron, PAM, firewall, or kernel configuration.
- Prune, vacuum, truncate, delete, restore, or migrate databases.
- Delete snapshots, audit logs, backups, or recovery manifests.
- Execute package-manager upgrades or OS updates.
- Change user permissions, ownership, or file modes recursively.
- Trigger billing webhooks or external account changes.
- Run an automated test whose effects on a live server are not known.

## 6. Safe audit behavior

Allowed during the initial read-only audit, subject to the staging account's permissions:
- Inspect repository files and metadata.
- Inspect installed plugin version and file checksums.
- Read service status and logs.
- Inspect browser output and screenshots.
- Read non-sensitive configuration metadata.
- Run syntax checks that do not modify system state.
- Run read-only diagnostic commands whose effects are understood.

If uncertain whether a command mutates state, do not run it. Explain the uncertainty and ask the owner.

## 7. Backups and rollback

Before any approved staging or production change:
- Record the current Git commit and working tree.
- Back up the current plugin directory.
- Preserve the current packaged plugin archive and checksum.
- Back up relevant configuration files.
- Back up the SQLite telemetry database using an application-safe method.
- Record ownership and permissions.
- Record the active service state.
- Define exact rollback steps.
- Verify that the backup is readable before relying on it.

Do not delete existing recovery manifests or backups to force an installation.

## 8. Browser automation safety

- Use a dedicated staging Admin account with minimum permissions.
- Use a dedicated Enduser account with synthetic test data.
- Do not test process termination against real customer processes.
- Do not click privileged controls on production.
- Do not trigger billing, webhook, account suspension, plan migration, or destructive maintenance flows in production.
- Confirm the active hostname and environment before every test session.
- Keep screenshots free of passwords, tokens, private customer information, and internal secrets.

## 9. Network and data handling

- Do not upload full production logs or database files to an external AI service.
- Use sanitized samples.
- Do not expose account paths, domains, usernames, command-line arguments, or IP addresses unless strictly necessary.
- Preserve existing command-line and diagnostic redaction.
- Do not add external telemetry or third-party analytics as part of the redesign.

## 10. Stop conditions

Stop and contact the owner if:
- The environment appears to be production.
- Credentials are broader than the approved scope.
- A command's side effects are uncertain.
- A test could affect customer accounts or server availability.
- A backup or rollback cannot be verified.
- The requested visual change appears to require changing security boundaries.
