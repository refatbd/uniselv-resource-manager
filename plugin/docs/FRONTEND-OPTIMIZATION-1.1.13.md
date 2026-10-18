# Frontend optimization review - 1.1.13

Date: 2026-10-18. Scope: existing Ubuntu/Webuzo installation; read-only telemetry transport and asset caching. Protection implementation and enforcement policies are unchanged from 1.1.12.

## Changes

- Admin Overview and Enduser Dashboard poll every 10 seconds instead of 3 seconds. Non-visible/inactive views skip polling when browser visibility is available.
- Read-only responses can be reused for 5 seconds. Same-tab requests are single-flight. BroadcastChannel and Web Locks coordinate compatible browsers across tabs of the same authenticated context.
- Coordination names use a SHA-256 digest of endpoint, account, role and session CSRF identity. No tokens or metrics are persisted in browser storage; different contexts do not share a channel. Unsupported optional browser APIs fall back to per-tab caching and single-flight requests.
- Mutations and other feature actions bypass this telemetry cache. Their existing authorization and CSRF checks remain in force.
- Telemetry requests have a 15-second client timeout. Failed polling backs off from 10 to 60 seconds; available peers share the failure cooldown. Long-running mutations have no new automatic timeout.
- The one-second freshness label uses the actual source timestamp and makes no network requests. Older samples cannot replace newer samples. Clock reversal expires the local cache.
- CSS/JS cache keys use file modification time rather than the current time on every render. Help documents the refresh behavior.

## Verification

12 targeted polling tests, 8 existing UI regression tests and 9 backend regression tests passed. Tests include account/role/session/endpoint separation, duplicate suppression, unsupported APIs, late responses, failure cooldown, clock reversal, visibility, BFCache and timeout separation.

Two Overview tabs and one existing integration tab were retained during the normal-traffic observations below. These were sequential windows, not a controlled workload benchmark.

| Observation | Duration | Direct plugin/protection CPU, one-core equivalent | Share of 4-vCPU capacity | Memory |
|---|---:|---:|---:|---:|
| 1.1.12 baseline | 180.77 s | 7.495% | 1.874% | mean 110.9 MiB; peak 112.77 MiB |
| 1.1.13 preliminary, 10 s reuse window | 180.62 s | 5.040% | 1.260% | mean 117.11 MiB; peak 118.17 MiB |
| Final 1.1.13, 5 s reuse window | 60.20 s | 5.341% | 1.335% | mean 117.27 MiB; peak 117.49 MiB |

The final observation recorded six Overview requests across both Overview tabs in 60 seconds. Direct service CPU was about 29% lower than baseline. Its memory did not decrease; it remained stable during the observation, with no OOM kills or automatic service restarts. The agent had been deliberately restarted once for version metadata before observation.

Final direct CPU components, one-core equivalent: agent 1.447%, Golden Shield 3.530%, and remaining compatibility services approximately 0.364%. Golden Shield includes ongoing protection work, so its cost is not dashboard-rendering cost.

Webuzo's shared service CPU was 44.783% of one core in the final window. This includes native panel activity and cannot all be attributed to this plugin. Whole-host CPU averaged 15.46% of total capacity. No claim of zero monitoring overhead or sustained workload capacity follows from these windows.

## Native Webuzo comparison

The deployed Webuzo 4.8.4 Admin panel was inspected at Home > Server Utilities > CPU / Ram. The readable vendor themes `web/admin/themes/default/cpu_theme.php` and `ram_theme.php` call their authenticated `act=cpu&ajax=true` and `act=ram&ajax=true` routes every 5000 ms. Their AJAX branches output Used/Free values and return before the full theme header/render. The browser redraws the existing chart. The vendor backend collectors are encoded; their internal sampling/caching and CPU cost have not been verified.

Those views show host totals; they do not replace per-account cgroup metrics, history, snapshots or protection enforcement. The plugin also uses AJAX; its current dashboard optimization reduces repeated reads while retaining those functions. Vendor source files were not modified.

## Boundaries and recovery

No kernel, PAM, native resource policy, firewall, PHP-FPM manager or Golden Shield configuration was changed for this optimization. Previous existing-host lifecycle evidence remains in `LIFECYCLE-REVIEW-1.1.12.md`; this is not a new fresh-OS, physical-resize or heavy WordPress capacity certification. Backend protection still runs when browser tabs close.

Rollback: restore the six changed plugin files and the runtime agent version file from the private deployment backup, then restart only the agent to reload its version string. Do not publish private backups. Release-specific test evidence and monitoring JSON are kept with the local validation records.
