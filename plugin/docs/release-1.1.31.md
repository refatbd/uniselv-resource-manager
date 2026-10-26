# Release 1.1.31 — demand-sized grants and warm idle reservation reclamation

Cold pools with a verified private relay now reserve one worker and grow only to measured forwarded plus queued demand, subject to the existing account, host and aggregate PHP memory boundaries. Unverified/legacy relays retain their conservative full native enforcement path. Native global PHP-FPM defaults are unchanged.

New queued bursts trigger a fresh locked allocation check immediately instead of waiting for the periodic regrant tick. A regression freezes the periodic clock to verify arrival-driven growth while the first request remains in flight.

When a proxy is quiescent for the configured native idle interval, it may reduce an elastic grant to one fully charged worker only after the root FPM master identity/cgroup is verified, every native child has exited and charged backend memory fits the new reservation. The master, private socket, native configuration and OPcache remain intact. This releases reservations, not allocated memory promises or physical safety limits. No registration-count split or permanent per-account reservation is introduced.

A valid peer ticket no longer causes fair-share shrink or idle eviction when the next peer worker already fits the shared PHP budget. A pool with zero forwarded/queued demand uses the idle reclamation path instead of a fair-share master restart. Actual unfunded concurrent demand can still require a drained rebalance. Warm TTL and host-pressure eviction remain supported; idle retirement now also requires native backend-idle proof so FastCGI END_REQUEST does not interrupt post-response jobs.

Cold tickets publish the originating pool's complete minimum footprint; different PHP versions or relay sizes are not inferred from the current pool. Unknown legacy minima stay conservative. Child commands no longer inherit the supervisor's systemd notification/watchdog endpoint; the supervisor retains its own readiness channel.

The generator derives the interned-string buffer from one eighth of total OPcache, rounded down to a power of two and bounded to 4–32 MiB. The current matched 256-MiB OPcache profile uses 32 MiB inside that unchanged total. A 16/32/16 comparison found that 16 MiB was full while 32 MiB stored about 26 MiB of strings. CPU differences were small and noisy, not a large speedup. Native global INI values are applied consistently across installed versions; per-user native FPM forms remain untouched.

This does not guarantee an optimal worker count for every application, unchanged future hardware or all future vendor updates. Idle cache retention consumes a fully charged minimum grant; true memory pressure may legitimately evict a warm master. Worker RSS remains a conservative estimate, while cgroup limits provide kernel enforcement. Shared Redis remains shared and CSF remains owner-managed.

Validation: see server-policy-validation.json and the dated server policy report. Syntax/unit tests, bounded live placement/allocation tests and website capacity are separate evidence levels. The website and currency plugins were not modified. USD default with geolocated BDT is recorded as intended application behavior; currency review is deferred.

Install the complete package through the supported installer/update workflow, keeping ownership and restoration manifests with runtime files. Do not manually append these functions after installation. Exact before/after source anchors, replacement blocks and verification instructions are in source-changes-1.1.31.md and .json. Rollback must restore the runtime and its ownership/shared-file manifests together, then restart managed coordinators in a drained maintenance window.
