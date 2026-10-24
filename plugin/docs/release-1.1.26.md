# Resource Manager 1.1.26 — server runtime correction

## What changed

The native Webuzo cgroup mover previously relocated managed PHP workers outside the Golden account parent. The collector could then select a resident but mostly idle proxy group and miss the active native PHP group. A 20-second whole-master idle deadline also discarded OPcache too quickly.

The corrected integration uses an owned systemd drop-in while Golden is active, reloads the privileged native assignment registry, preserves managed descendants, and adopts legacy account CLI processes into proper child scopes. Shared Apache workers remain an aggregate-owned service. Vendor cgroup.sh is not rewritten. Native-only mode/rollback restores the vendor command. Old scanner-file ownership receipts are archived and relinquished explicitly; vendor updates are not overwritten on later rollback.

Warm masters retain OPcache while headroom permits. The maximum deadline is derived from physical PHP memory budget and master/OPcache footprint: one minute per affordable footprint, bounded to 60–900 seconds. The recorded profile generates 600 seconds. This is an operational planner policy, not measured visitor capacity. Eligible waiting peers and low host memory reserve can reclaim a quiescent lease earlier. Busy/queued requests are not evicted by this idle rule. Conservative complete lease reservations remain charged until release. Registered inactive accounts do not receive permanent workers.

Global native PHP-FPM defaults are unchanged. Ondemand workers still retire independently using inherited global settings. `idleSeconds` remains a legacy compatibility field; new generated proxy units use `warmIdleSeconds` for the whole master. OPcache remains 256 MiB on the recorded profile, with no per-user native tuning form.

Account telemetry sums disjoint native and managed roots, including retained historical page-cache charges, without adding descendants twice or summing limits. Process inventory enumerates the real UID. Configured-versus-effective audit no longer reports complete synchronization when customer processes are observed outside their boundary. The administrator health page exposes placement and native coexistence guard status.

## Actual UI navigation

Webuzo Admin > Plugins > UNISELV Resources > System & Agent Health > Account cgroup placement. Observed fields: status, Accounts checked, Native coexistence guard. The result is a page-load audit; refresh the page after maintenance. PASS means the implemented current checks passed, not a universal deployment certificate. Global Inputs remains the only generator input area; CPU, RAM, Disk Type and Overselling remain the default minimal flow. No section-local input form was added.

## Verification recorded on the current Ubuntu/Webuzo host

- 92 Linux regression cases and 8 hardware/overselling generator cases passed.
- 331 configuration comparisons matched; account kernel audit mismatches: 0; checked accounts: 25; outside customer processes: 0.
- A PHP request stayed in its account service group at entry and after seven seconds; a deliberately outside legacy CLI fixture was adopted into a child scope.
- OPcache start identity survived a 25-second idle interval. After final coordinator refresh, real uncached product requests also returned 200 before and after 30 seconds idle.
- Eight CPU-heavy PHP requests measured 276.56% account CPU against a 280% quota, with 54 throttled periods.
- Four bounded CPU actors across two accounts measured 325.63% aggregate CPU against 340%, with 37 throttled periods. These were CPU fixtures, not four shoppers.
- Another account's private PHP request succeeded in its own boundary; no permanent entitlement or workload-capacity guarantee follows.
- Native vendor scanner checksum remained unchanged. Private test files and temporary CPU units were removed/stopped.

The most recent cloud visitor-capacity test predates these changes. WordPress remains expensive and unchanged. These results do not certify checkout, carts, payments, all future vendor releases, a fresh OS, a complete protection reset/reinstall or reboot for this release. The all-section readiness export retains its unverified sections. Host swap was not enabled.

## Installation / maintenance ownership

The current server was upgraded through a reviewed privileged workflow with private backups and ownership/recovery receipt rebasing. An existing installation whose adopted runtime hash differs must not be updated by blindly copying a ZIP over active runtime files: the installer deliberately refuses that mismatch. Preserve backups, ownership manifests, Golden recovery receipts and the generator profile together. A fresh installation uses the bundled components in their reviewed dependency order. Do not uninstall working protection just to force an update.

Prefer the complete reviewed package. The exact relative-to-1.1.25 source replacement/insertion appendix is `source-changes-1.1.26.md` and `.json`; it includes file paths, existing anchors, generated code, AFTER-edit context and verification steps. It documents already-applied changes, not mandatory extra post-install edits.

## Generated managed files — placement reference, not additional paste steps

The core creates the following new owned drop-in. AFTER: beginning of a new file. BEFORE: end of that same file. Do not modify or append code to `/usr/local/webuzo/bin/cgroup.sh`.

Path: `/etc/systemd/system/cgroup.service.d/90-uniselv-resman.conf`

Generated complete content:

```ini
# UNISELV-RESMAN native cgroup coexistence; vendor source preserved
[Service]
ExecStart=
ExecStart=/usr/bin/python3 /usr/local/sbin/webuzo-isolation.py native-cgroup-guard
Restart=on-failure
RestartSec=2
```

Illustrative AFTER-edit excerpt (context only; do not paste a second copy):

```ini
# UNISELV-RESMAN native cgroup coexistence; vendor source preserved
[Service]
ExecStart=
ExecStart=/usr/bin/python3 /usr/local/sbin/webuzo-isolation.py native-cgroup-guard
Restart=on-failure
RestartSec=2
```

Exactly one owned file is used. The empty ExecStart resets the inherited command; the next ExecStart supplies the replacement. Unknown changes stop management instead of being overwritten. Save through the reviewed installer, reload systemd, and verify the actual service command plus customer process placement.

Policy path: `/etc/webuzo-isolation/policy.json`. Replace the complete prior JSON object, AFTER file start and BEFORE file end. Never append a second object. The following is the recorded 4-vCPU/visible-7751-MiB profile example; use generated values from your own Global Inputs on another host.

Generated complete policy:

```json
{
  "accountRuntimeCaps": true,
  "maxActivePools": 4,
  "hostReserveMiB": 1280,
  "poolBudgetMiB": 2649,
  "phpBudgetMiB": 3127,
  "workerRssMiB": 288,
  "opcacheMiB": 256,
  "idleSeconds": 20,
  "requestTimeoutSeconds": 120,
  "warmIdleSeconds": 600
}
```

Illustrative AFTER-edit excerpt (context only):

```json
{
  "accountRuntimeCaps": true,
  "maxActivePools": 4,
  "hostReserveMiB": 1280,
  "poolBudgetMiB": 2649,
  "phpBudgetMiB": 3127,
  "workerRssMiB": 288,
  "opcacheMiB": 256,
  "idleSeconds": 20,
  "requestTimeoutSeconds": 120,
  "warmIdleSeconds": 600
}
```

Apply through reviewed maintenance and regenerate/reconcile managed units so their warm-idle argument matches the policy. Do not manually edit individual customer FPM copies. Verify with:

```sh
sudo systemctl show cgroup.service -p ActiveState -p ExecStart
sudo python3 /usr/local/sbin/webuzo-isolation.py verify
sudo python3 /usr/local/sbin/golden-shield.py check
```

Run bounded private PHP checks across multiple five-second native mover sweeps, inspect actual `/proc/PID/cgroup`, compare OPcache before/after the old idle deadline, and verify real HTTP content. Repeat native provisioning, plan/global-PHP changes and reboot as separate lifecycle gates when those are in scope. Matching configured numbers alone is insufficient.
