# Resource Manager 1.1.23 — deployment and PHP lifecycle

Use global Webuzo PHP-FPM/INI/OPcache defaults for each installed PHP version. Do not create manual native per-user FPM settings. Runtime worker caps remain automatic and account-scoped; idle workers do not reserve capacity.

## Version events

1. Install the PHP software using Webuzo. Configure the new version globally and verify the native layout/configuration. In the generator Advanced Global Inputs, add/select the actual PHP target and regenerate the profile. Adding a target in the browser does not install or register PHP.
2. During an appropriate maintenance window, run `sudo python3 /usr/local/sbin/webuzo-isolation.py onboard php83`, substituting the actual version. This also repairs a managed launcher replaced by a vendor update. It validates native pools before mutation, waits for graceful native stop, and does not force-kill remaining masters. Root-written launcher changes require administrator review before this explicit repair operation.
3. Verify System & Agent Health > PHP Runtime Registration, then check actual HTTP placement and `sudo python3 /usr/local/sbin/webuzo-isolation.py verify` before assigning customer traffic.
4. To remove a version, first move all domains away using Webuzo, reconcile and verify the native config/manifest contain no customer pools. Run `sudo python3 /usr/local/sbin/webuzo-isolation.py retire php83`. Only after successful retirement remove the software through Webuzo. Missing/malformed config, remaining pools, changed launcher or missing restoration backup blocks retirement.
5. Re-export the generator profile after the installed version set changes. Reviewed-profile parity checks intentionally reject stale version lists; there is no silent fallback to unreviewed physical discovery.

There is no unattended acceptance of unknown PHP layouts or vendor/admin modifications. New versions need an explicit lifecycle action after global configuration. Standard directory-name validation is not certification of all future PHP implementations.

## Failure and recovery

Lifecycle operations serialize through `/run/webuzo-isolation/php-lifecycle.lock`. Before mutation, root-only snapshots of version control files, registration, native restoration baseline, relevant units/links and prior active/enabled service states are recorded in `/var/lib/webuzo-isolation/lifecycle-pending.json`. Journal writes are synced before mutation. Exceptions restore prior routing/control state and retain an audit snapshot. After an interrupted process, the next onboard/retire operation attempts recovery of the pending journal first. Unsafe or conflicting staging files require manual review rather than blind deletion. Failed recovery retains the pending file and reports an error; do not delete it or force a new registration. Keep these snapshots private.

Vendor regeneration archives the previous native restoration baseline and records the current native launcher before wrapping it. Retirement restores that current baseline. Added version bookkeeping reserves 32 MiB (matching generator 16-MiB bookkeeping plus 16-MiB private health estimate), in addition to per-pool OPcache/worker lease charges. Retirement releases this additional reserve up to the original reviewed budget. External policy changes require a regenerated/reviewed accounting baseline; the plugin does not enlarge physical safety limits or kill live requests to make room.

A stopped coordinator with no pools is displayed as stopped, not silently labelled healthy. PHP registration status is read-only in the UI. Runtime reload failures now make bulk plan sync report failure rather than a false success.

## Packaging and exact source placement

Deploy the complete plugin package, not partial snippets. Its root directory is `uniselv-resman/`; source maps to `/usr/local/webuzo/plugins/uniselv-resman/`, agent code to `/usr/local/uniselv-resman/agent/`, and the reviewed runtime to `/usr/local/sbin/webuzo-isolation.py`. Existing files are replacements, not appended code. Do not duplicate classes/functions or append directives. New documentation/test/builder files start at their first line and end at their final line. `source-changes-1.1.23.json` records exact existing anchors, generated code and after-edit context for changed plugin files; save UTF-8 and verify syntax/tests after replacement. Keep ownership hashes and component restoration backups synchronized with deployed source.

Run `php package_plugin.php` (or the compatibility Python entry point). It uses native PHP ZipArchive, forward slashes, directory 0755/file 0644 modes, a root module directory, asset-version consistency and ZIP closure/source-hash verification. Installer-applied runtime execute permissions are separate from archive file permissions. Never use Compress-Archive for these packages.

## Evidence and limits

See `server-configuration-validation-20261024.json` in the canonical generator and `server-audit-20261024` in the workspace. Unit/failure tests, actual synthetic systemd/FPM lifecycle checks, configured-value parity and browser checks are distinct evidence scopes. A synthetic PHP fixture is not a real Webuzo software package install; the complete 92-case matrix, clean OS installation, protection uninstall/reinstall and every vendor/domain/account event are not certified. WordPress capacity, payments and swap remain outside this release's new validation.
