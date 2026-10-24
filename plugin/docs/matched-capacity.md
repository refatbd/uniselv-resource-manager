# Matched capacity deployment — 20 October 2026 / 1.1.18

This dated deployment is for an existing Ubuntu 24.04 / Webuzo 4.8.4 server, 4 vCPU and 7751 MiB measured RAM. It is a bounded verification record, not a universal sizing recommendation or full deployment certificate. All sections continue to derive from Global Inputs. Other hardware must be recalculated and tested.

## Applied changes and measurements

| Setting | Previous | Applied and checked |
|---|---|---|
| RAM planning | 7490 MiB estimate | 7751 measured, 1280 reserve, 6471 hosting |
| Hosting CPU | 340% aggregate | 340% retained; 60% host headroom |
| Customer OPcache / strings | 128 / 8 MiB | 256 / 16 MiB; warm HTTP usage 164.13 MiB, 4910 scripts |
| Private health OPcache / strings | inherited incompatible strings | explicit 16 / 4 MiB for all four versions |
| Native global FPM | 2 children, backlog blank | 8 ceiling, 64 backlog, Ondemand, idle 10 s, timeout 120 s |
| PHP admission | earlier calculated profile | 3127 MiB shared budget, 2649 MiB full-ceiling estimate; no idle-account reservation |
| SQL account connections | original 6; earlier reviewed 18 | 34; total 64, InnoDB 1024 MiB |
| Apache | existing Prefork / mod_ruid2 | retained, 20 workers; TLS 1.2 + 1.3 confirmed in native selected preset |
| Native plans | old RAM ceilings | all six regenerated; 25 account limits reconciled |

Installed versions are PHP 7.4, 8.1, 8.2 and 8.4. PHP 7.4 exports omit unsupported JIT directives. Native FPM defaults remain global. Explicitly approved private runtime caps derive from account RAM and Tasks limits. Continuously busy private pools retain their conservative startup grant until idle; a second account waited 22–44 seconds in bounded sharing probes. This is not instantaneous fair redistribution or a guaranteed minimum share.

Global PHP memory is 256M. A site's old .user.ini overrode eleven global values, including memory 512M, execution 300, input 600 and a PHP 8.2 session path while running PHP 8.4. Commenting those overrides restored inheritance; all 30 effective PHP 8.4 HTTP values now match. Recheck after a future account PHP INI Editor save.

## Read-only checks and bounded loads

326 saved/configuration checks, 30 effective HTTP INI values and 25 native account limits matched. Four private health/coordinator pairs were active; 14 deployed release source files matched the bundle. Three account FastCGI probes passed UID/cgroup checks and their temporary probes were removed.

Final direct-origin TLS product bursts: 16/16 in 21.647 s, 32/32 in 29.655 s and 64/64 in 59.424 s. Operator-network public Cloudflare compressed GETs: 16/16 in 28.377 s, 32/32 in 53.628 s. No curl failure, capacity 503, database error, critical page error or OOM occurred in these final runs. Normal account CPU 280% and aggregate 340% were retained. Cloudflare HTML responses were DYNAMIC, not cache hits.

Earlier 8-second test-client connection deadlines failed; those failures remain in the JSON record. TLS connection queuing reached 42.123491 seconds. Final test-client connect/total deadlines were 90/100 seconds; no server deadline increase was made for that correction. This tests queued completion, not a low-latency guarantee or 100–200 sustained visitors.

All-section readiness remains visible in the generator and JSON exports. Fresh install, provisioning, reboot/vendor regeneration, sustained mixed CMS, payment flows and shared SQL tenant isolation remain open for this changed profile. Host swap remains off.

## Complete file placement and duplicate handling

Use the planner's per-block code placement guide for native INI, Apache and SQL changes; do not replace an entire vendor configuration with an isolated snippet. Panel-only resource plans use the native Save and account reconciliation workflow, not invented raw edits.

The profile file is `/etc/webuzo-isolation/generator-profile.json`. Back up any existing file. This is a complete new JSON document: copy `matched-server-profile.json` from its first `{` through its final `}`, AFTER the beginning of file and BEFORE EOF. There are no surrounding content anchors for a new file. Replace an existing document completely, never append another object or merge duplicate keys. Owner root, mode 0600. Import the same profile at **Global Inputs > Advanced mode > Import measured server profile**; importing does not deploy it.

The new audit program is `/usr/local/uniselv-resman/core/configuration-audit.py`, with the identical plugin mirror under `/usr/local/webuzo/plugins/uniselv-resman/core/configuration-audit.py`. Copy the entire matching package file from `#!/usr/bin/python3` through EOF; new file starts empty, existing file is a complete replacement. No duplicate methods or appended program. Preserve root ownership and verify against the release SHA256.

Other changed complete programs are `core/webuzo-isolation.py`, `core/protection-lifecycle.py`, `core/golden-shield.py` and `agent/golden_shield_manager.py`, under the corresponding `/usr/local/uniselv-resman/` and plugin mirror paths. The two sbin entry points are `/usr/local/sbin/webuzo-isolation.py` and `/usr/local/sbin/golden-shield.py`. Back up each whole file, replace beginning through EOF using the matching package source, and preserve permissions. The contextual AFTER-edit example is exactly the complete packaged file, with its original first and last lines; no partial program fragment is valid. Adopted-source ownership still requires a reviewed matching predecessor; unknown source drift remains blocked.

After a reviewed save, compile Python, lint PHP, reconcile all installed-version coordinators and the agent, then run:

```sh
python3 /usr/local/uniselv-resman/core/configuration-audit.py
python3 /usr/local/sbin/webuzo-isolation.py verify
python3 /usr/local/sbin/golden-shield.py check
```

Require zero audit mismatches, no unintended inheritance exceptions and passing mechanical/Golden checks. Confirm HTTP values and representative workloads separately; syntax checks do not certify capacity. The profile guard rejects measured hardware, installed-version or native budget drift rather than overwriting adopted policy silently.

## MySQL native checkbox representation

Observed path: **Webuzo Admin Panel > Apps > MySQL Configuration**, heading **MariaDB 11.4 Configuration**, **Basic Mode / Editor Mode**. The Basic Mode button is **Save**; the Editor Mode action is **Save Raw Configuration**. The companion observation JSON records exact ordered fields, units/placeholders and applied values, not factory defaults.

File `/etc/my.cnf`, existing `[mysqld]` section. This is replacement of exactly one existing line `skip-networking=0`, AFTER `default_storage_engine=InnoDB` and BEFORE `wait_timeout=60`. Replace, do not append a duplicate. If absent on another server, enabled TCP requires no directive; do not invent these anchors for another layout.

Copyable replacement code:

```ini
# skip-networking omitted: local TCP remains enabled
```

Illustrative AFTER-edit context, not a second paste block:

```ini
default_storage_engine=InnoDB
# skip-networking omitted: local TCP remains enabled
wait_timeout=60
```

Save, parse with the installed MariaDB binary and confirm `SELECT @@skip_networking` returns 0. Reload the native panel: Skip Networking must be unchecked. The native UI treated an active `skip-networking=0` as checked even while MariaDB reported OFF. Commenting this false flag corrected the panel roundtrip hazard without changing the running database or requiring a restart. Keep loopback binding.

## Response page and rollback

The release contains the self-contained, neutral white/coral animated capacity page with reduced-motion support, HTTP 503, Retry-After and no-store. Actual deadline/exhaustion can still return it; the change does not conceal a failed request as HTTP 200 and never replays forwarded requests.

The deployment retained a root-only configuration backup and an independent rollback timer during changes. Disarm the timer only after final parity, source, service and workload checks. Keep the backup for manual recovery. Do not publish private server journals or authenticated URLs.
