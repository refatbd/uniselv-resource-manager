# Dynamic demand sharing — Resource Manager 1.1.32

Native PHP-FPM defaults remain global across installed PHP versions. Private runtime caps are automatic account RAM/Tasks boundaries, not manual native per-user settings. Registered accounts that have never requested PHP hold no lease. The algorithm does not split capacity by registration count or multiply physical safety limits by overselling.

## Cold requests, live growth and fair sharing

A verified relay starts with a fully charged one-worker reservation. Queued plus active connection demand can grow that reservation in place without restarting PHP or OPcache. Growth must pass account working-memory, Memory High/90% Memory Max, Tasks, actual host headroom and aggregate PHP-budget checks. Legacy or unverified relays retain conservative native enforcement.

Waiting tickets and busy-demand records have different meanings. A waiting ticket requests an unfunded grant; a busy-demand heartbeat says a proxy still has work even after its waiting ticket clears. Both directories are root-only under `/run/webuzo-isolation/`. Demand expires automatically after a crashed proxy. Queued demand is retained and refreshed across a drained backend restart; a temporarily missing backend lease does not erase a still-live proxy's claim. Proxy shutdown clears its demand record.

When active demand cannot fit simultaneously, a deterministic worker distribution subtracts fully charged idle leases and per-pool overhead, then distributes the remaining worker allowance up to each active claimant's actual demand and native ceiling. A lightly used account leaves its unused share available. Targets do not release reservations: actual admission and drained regrant checks still charge the complete footprint.

An oversized busy grant holds new work in the bounded queue and waits for submitted work plus native backend-idle proof before restarting at a smaller grant. This can require one initial fair-share adjustment when a new peer becomes busy. A granted peer clearing its waiting ticket must not cause continuing grow/shrink restarts. A bounded drain that cannot prove idleness is deferred while retaining its full charged reservation. In-flight work is neither replayed nor forcibly migrated.

## Idle workers and OPcache

Ondemand workers inherit global native idle settings. Once surplus children have exited, a quiescent proxy may compact the reservation to one fully charged worker without restarting the root master or OPcache. Zero children is eligible; a sole child must be proven accepting on the private listener. The master's UID/cgroup and actual charged memory must fit. Multiple children, unknown proc visibility or post-response background work keep the conservative reservation.

The generated warm-master timeout is a maximum under available headroom, not a permanent resource lock. Unfunded eligible peer demand or low host reserve may reclaim a proven idle backend earlier. Native backend-idle proof is required even after FastCGI END_REQUEST so post-response jobs are not mistaken for completed PHP work.

## Source placement and verification

Replace the complete reviewed program at `/usr/local/sbin/webuzo-isolation.py`, `/usr/local/uniselv-resman/core/webuzo-isolation.py` and `/usr/local/webuzo/plugins/uniselv-resman/core/webuzo-isolation.py`, AFTER start of file and BEFORE EOF. Prefer the supported complete-package update; never append duplicate functions or a second program. Keep the runtime and ownership/restoration manifests together for rollback.

The exact changed blocks, verified AFTER/BEFORE anchors, copied code separately from illustrative context, permissions and save/verification steps are in `source-changes-1.1.32.md` and `.json`. The generator's embedded program and digest must match the package; its exact complete-file replacements are in `generator-source-changes-1.1.32.md` and `.json`. Managed runtime copies are not an instruction to create manual native per-user FPM settings.

Read `server-policy-validation.json` and `server-policy-report-1.1.32.md` for the actual repeated worker, multi-account, sustained/recovery, Apache, database and offered-arrival comparisons. Syntax/unit checks, bounded current-host behavior and application capacity are separate evidence levels. The previous `demand-sharing-1.1.20.md` is historical behavior and must not override this description.

Worker RSS is a planning estimate; kernel account/aggregate cgroups enforce actual boundaries. This does not guarantee a minimum service rate for every account, arbitrary script costs, clean-OS installation, unknown future vendor releases or an unlimited shopper count. Hardware, workload, RSS, account activity or database growth may justify renewed measurements.
