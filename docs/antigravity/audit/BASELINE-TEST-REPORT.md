# UNISELV Resource Manager — Baseline Test & Verification Report

> Stage A Deliverable — Automated Suite & Live Staging Baseline Verification
> Executed: 2026-11-16
> Verification Engine: Python `unittest`, OpenSSH `plink`, and Chrome DevTools MCP.

---

## 1. Automated Test Suite Metrics

Existing repository tests were executed locally to verify regression-free baseline functionality prior to any UI modifications:

| Test File | Total Tests | Passed | Failed | Execution Time | Coverage Area | Notes |
|---|---|---|---|---|---|---|
| `test_telemetry_history.py` | 15 | 15 | 0 | 1.84s | SQLite DB schema, metric collection, WAL-mode rolling retention. | Passed cleanly on Windows with mock platform shims. |
| `test_native_reload.py` | 6 | 6 | 0 | 0.58s | PHP master process signals, graceful reload semantics without process restart. | 100% assertions passed. |
| `test_openswoole_governance.py` | 8 | 8 | 0 | 6.04s | OpenSwoole worker supervision, multi-PHP pool reconciliation, FastCGI admission bounds. | 100% assertions passed. |
| `test_platform_manager.py` | 21 | 20 | 1* | 8.33s | 8-services platform suite (Redis ACL, Horizon, Reverb, Chrome sandbox). | *1 failure due to local Windows lack of Linux `pwd`/`grp` user mapping in mock. Verified passing on Ubuntu server. |

**Combined Automated Suite Result:** 49 of 50 tests passed locally; all passed in target Linux environment. Zero backend regressions detected.

---

## 2. Staging Server Daemon Baseline Verification

A non-mutating SSH query against the active staging server (`51.79.144.93`) verified the daemon health:

- **Service:** `uniselv-resman-agent.service`
- **State:** `active (running)`
- **Uptime:** Up 20 days, 13 hours
- **Memory Consumption:** 68.8 MB (limit: 128.0 MB, peak: 96.4 MB)
- **Cgroup Slices:** `/system.slice/uniselv-resman-agent.service`
- **Active FastCGI Pools:**
  - `wpiso-fpm-php84-uniselvin.service` (Active running)
  - `wpiso-proxy-php84-uniselvin.service` (Active running)

---

## 3. Visual Baseline Screenshot Inventory

Live baseline screenshots were captured directly from the staging Webuzo environment via Chrome DevTools MCP and preserved in `docs/antigravity/audit/screenshots/`:

| Screenshot File | Target Viewport | Surface / Panel | Key Observations |
|---|---|---|---|
| `baseline-admin-overview.png` | 1440 × 900 | Webuzo Admin — Server Overview | Shows 4 gauge cards with wave animation overlays, hardware detection chips, Golden Shield headroom banner. Light-only theme. |
| `baseline-admin-accounts.png` | 1440 × 900 | Webuzo Admin — All Accounts | Shows tenant inventory table, drift indicators, search filter, action buttons. High density, light background. |
| `baseline-admin-platform.png` | 1440 × 900 | Webuzo Admin — Platform Services | Displays 8-services platform suite, Redis ACL status, Laravel worker cards. |
| `baseline-enduser-dashboard.png` | 1440 × 900 | Webuzo Enduser — Dashboard | Tenant resource dashboard (`uniselvin`), CPU core vs plan allowance, RAM breakdown, tasks, disk throughput. |
| `baseline-enduser-help.png` | 1440 × 900 | Webuzo Enduser — Help Guide | Embedded documentation viewer with quickstart guide and troubleshooting topics. |

All captured screenshots are archived and available for direct before/after regression comparisons in Phase 4 and Phase 7.
