# Webuzo 4.8.6 to 4.8.7 - Resman compatibility verification

Started: 2026-10-24; completed: 2026-10-25 (Asia/Dhaka). Resource Manager: 1.1.30. Result: PASS in the current tested environment.

The native Webuzo update was submitted from Updates > Webuzo Update > Update Webuzo. Completion was established by signature-verified native upgrade log status and panel readback of Current Version 4.8.7 / Latest Version 4.8.7. A background-submission message alone was not treated as completion.

Before the update, a private control snapshot and approximately 3 GB vendor-file archive were created and read back. These contain private information and are excluded from distributables; they are not a bare-metal or SQL disaster-recovery certificate.

## Verified after the actual update

- 331 configuration checks, zero mismatches; mechanical runtime and Golden checks passed.
- Resman source/policy hashes, native global FPM settings and the original 25 accounts were preserved.
- A disposable native account passed creation, PHP 7.4/8.1/8.2/8.4 assignment and global PHP/OPcache inheritance, native/private restarts, vhost regeneration, suspension and unsuspension. The account, managed manifests and test file were removed. Version assignment is a maintenance operation: transient old-version responses and 503 responses occurred before convergence; zero downtime is not claimed.
- All 25 native HTTP placement probes passed and were removed. A four-request, three-second CPU smoke stayed below the account ceiling; no throttle event occurred. This is not proof of the saturation ceiling or maximum shopper capacity.
- 151 isolated Linux regression tests passed.
- A subsequent real reboot returned all four coordinators and native bridges automatically; service identity/activity remained stable for 45 seconds before audit. Policies/source hashes and account list matched the pre-update baseline. No manual post-update or post-boot repair was applied.
- Shared Redis retained loopback operation, 128 MiB maxmemory, 128 clients, allkeys-lru, Golden placement, 512 MiB process ceiling and zero service swap. A direct origin uncached request returned HTTP 200.

During reboot, the native PHP 8.4 bridge was initially inactive. Existing Resman governance automatically onboarded/repaired it after its stability observation, and it became active without a manual service start.

No Resman logic or resource configuration change was necessary for this tested update. No WordPress fixes, customer database edits or CSF changes were made. This attests Webuzo 4.8.7 in this environment, not untested future vendor releases. Native provisioning/restarts/reboot can interrupt requests.

Machine-readable details: webuzo-update-validation.json. Private backup contents and credentials are not included.
