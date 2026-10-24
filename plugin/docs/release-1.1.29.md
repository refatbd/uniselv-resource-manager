# Resource Manager 1.1.29 — bounded rebalance drain

## Corrected behavior

A long/background PHP task can continue after the FastCGI response has ended. In 1.1.28 a fair-share rebalance paused new dispatch while waiting for proof that every backend worker was idle. That pause could consume the full proxy request timeout. A sustained native test retained 16 client timeouts, with no hosting OOM or physical budget violation.

1.1.29 limits each drain attempt to five percent of the proxy request timeout, rounded up to a whole second (minimum one second), and never beyond the request timeout. With the measured native request timeout of 120 seconds, the proxy budget is 114 seconds and one drain attempt is 6 seconds. Other valid native timeouts derive their own window.

If idle proof is unavailable by that deadline, the proxy resumes its queue using the unchanged charged grant. The backend and its background work stay alive. The existing cooldown prevents continuous rebalance attempts. Only proven-idle backends can be stopped and have their reservation released; original client deadlines remain unchanged and submitted work is never replayed.

No CPU/RAM cap, physical PHP budget, worker estimate, global PHP-FPM default or OPcache size was increased. All PHP versions use the same implementation. The canonical generator bundles the same corrected source and checksum.

## Upgrade and verification

Install the complete reviewed module. Exact already-applied file replacements, verified BEFORE/AFTER anchors, separate generated blocks, preserved surrounding context, duplicate handling and save/verification instructions are in source-changes-1.1.29.md and source-changes-1.1.29.json. Do not paste old replacement snippets into an updated installation. Back up ownership and Golden restoration manifests together with the runtime before any manual change.

Native Webuzo provisioning/rebuild/restart is a maintenance operation and can interrupt connections. A native API acknowledgement or socket file does not prove that all asynchronous jobs have settled. The recorded steady-load tests wait until all native managers are active with no pending systemd job and unchanged identity for 45 seconds. This is a test-readiness barrier, not an extra user input or permanent server setting.

## Evidence

The final evidence ledger is stability-validation-1.1.29.json and the results guide is stability-results-1.1.29.md. Keep retained failed runs and dated prior evidence separate. Current-host bounded tests do not certify a fresh OS, complete reset/disaster restore, future vendor releases or any number of real WooCommerce checkout users. CSF remains owner-managed and WordPress audit/fixes remain deferred.
