# Clean inactive file cache and automatic PHP admission — introduced in 1.1.19, retained in 1.1.20

Runtime 1.1.20 also adds demand-pressure idle lease yield; see `demand-sharing.md`. Read `uncached-capacity-validation.json` for current bounded tests and the still-open WordPress/lifecycle gates.

The previous governor subtracted the account's entire `memory.current` from its admission allowance. An idle account can retain file cache after all PHP workers exit. On the inspected host, approximately 1.2 GiB of clean inactive file cache remained while anonymous memory was zero. Treating that cache as permanently occupied application RAM reduced subsequent private grants from the native eight-worker ceiling to five or six.

New admission uses a conservative working-set estimate:

```text
clean_inactive = max(0, min(memory.current, file, inactive_file) - file_dirty - file_writeback)
estimated_working_set = memory.current - clean_inactive
account_available = account_boundary - max(existing_account_lease_reservations, estimated_working_set)
```

All counters are bytes from the account's cgroup v2 files. Missing, negative, duplicate, malformed or inconsistent required counters retain the original raw-current calculation. Dirty/writeback pages, active file cache, anonymous memory and kernel memory are not credited as free capacity. No cache is flushed and no account count enters the formula. This is an admission estimate: raw kernel accounting and enforcement remain authoritative, and page reclamation is not a guaranteed latency-free operation.

The following boundaries remain unchanged: 90% of native account Memory Max, effective Memory High, Tasks Max, native global `pm.max_children`, full existing account/host lease reservations, the shared physical PHP budget, host RAM reserve, aggregate hosting CPU/RAM limits and swap prohibition. Multiple PHP versions cannot spend the same account reservation twice. Busy pools still retain their current grant until idle; this is not instantaneous resizing or a minimum entitlement.

Each new lease records `accountMemoryMiB`, `accountCleanInactiveFileMiB`, `accountWorkingSetMiB` and `accountMemoryAccounting`. These diagnostic fields do not replace `memory.current` in the UI or kernel.

## Source placement and safe update

The supported update is the complete reviewed plugin installation, which manages native integration ownership and bundled sources. Do not hand-edit native per-user PHP-FPM settings.

For source review, `/usr/local/sbin/webuzo-isolation.py`, `/usr/local/uniselv-resman/core/webuzo-isolation.py` and the panel plugin's `core/webuzo-isolation.py` contain the same complete program. This is an existing-file replacement, not an appended directive. Replace the complete source AFTER the start-of-file boundary and BEFORE EOF, including the existing `#!/usr/bin/python3` first line and the final `sys.exit(1)` exception-handler line. Retain original private backups, permissions and the ownership manifest. Do not append another program below the old one.

The new `account_memory_usage()` helper is AFTER the existing `demand_grant()` function's return and BEFORE `def write_pool(version,row,p):`. The `admit()` function replaces the old two-line raw-current subtraction. The 1.1.19 correction changed `CAPACITY_MODEL_VERSION` from `account-demand-v2` to `account-demand-v3`; current 1.1.20 uses `account-demand-v4` AFTER `MARKER='# WEBUZO-ISOLATION MANAGED LAUNCHER'` and BEFORE the self-contained fallback-page comment. Full replacement source is bundled; these anchors are review context, not extra paste blocks.

Illustrative AFTER-edit excerpt only:

```python
                current=int((group/'memory.current').read_text())
                try:stat_text=(group/'memory.stat').read_text()
                except OSError:stat_text=''
                current,reclaimable,working=account_memory_usage(current,stat_text)
                account_available=boundary-max(account_reserved,working/1048576)
```

Save as one complete program, run `python3 -m py_compile`, verify ownership and source hashes, reconcile during maintenance, check all installed-version health/coordinator services, and run the mechanical and native HTTP tests. Do not bypass an ownership/source-drift rejection. Existing native global values and the reviewed measured profile are preserved.

## Evidence and limits

Regression tests cover inactive-cache admission, retained dirty/active/anonymous charges, malformed counters, source replacement and unchanged shared reservations. Dated site-specific uncached workload results are recorded separately. The workload also required a site-level SuperRocket optimization patch; those results are not a universal visitor count for this plugin or server size. Full changed-profile reboot/vendor-regeneration, sustained mixed tenants, shared-service attribution and payment capacity remain separate gates.

References: [Linux cgroup v2 memory controller](https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html), [Docker's distinction between raw usage and inactive file cache](https://docs.docker.com/reference/cli/docker/container/stats/), [PHP-FPM concurrency settings](https://www.php.net/manual/en/install.fpm.configuration.php).
