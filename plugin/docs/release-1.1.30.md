# Release 1.1.30 - native bridge recovery and optional Shared Redis

Managed PHP repair now validates and activates the native compatibility bridge; governance checks it before reporting healthy and after repair. Foreign/custom bridge units are refused by the existing checked installer. Physical hosting budgets, account resource plans and global native FPM/OPcache defaults are unchanged.

The owner-selected optional Shared Redis integration uses one shared service, sized from the common physical Global Inputs. It does not create per-user instances or divide RAM by account count. Cache dataset, process RAM and connection ceilings are checked after restart and the service runs inside Golden aggregate protection. Overselling does not increase these physical ceilings. Shared local access remains a shared trust scope, not tenant isolation.

The first application requires explicit --cache-only consent and a matching root-owned profile. Current inspected Redis keys were all attributed to rebuildable SuperRocket object cache; PHP sessions use files. Persistence, authentication, application endpoint and binding are preserved. Review future durable Redis consumers before reusing eviction settings.

Native configuration ownership is retained. Failed application restores configuration, policy and registry state. Reviewed uninstall restores native Redis settings and service placement; reinstall reapplies retained shared policy. See readiness-followup.json for actual completed lifecycle/reboot results and bounded private-fixture tests.

Use the complete reviewed package. Exact source paths, replacement anchors, copied code and contextual examples are in source-changes-1.1.30.md/.json. These are not extra post-install commands. Clean-OS installation, unavailable future vendor updates and bare-metal disaster recovery remain separate. CSF is owner-managed; website audit is deferred.
