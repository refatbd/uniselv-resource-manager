# UNISELV Resource Manager — Repository & Environment Audit

> Stage A Deliverable — Non-mutating Static & Environment Verification
> Date: 2026-11-16
> Auditor: Senior Staff AI Systems Engineer (Gemini Antigravity)

---

## 1. Executive Summary

This audit establishes the baseline evidence for the UNISELV Resource Manager redesign. The inspected codebase is a mission-critical Webuzo hosting infrastructure plugin managing Linux cgroups v2 resource limits, kernel-level telemetry, tenant isolation, and background daemons.

All version identifiers across the repository metadata, PHP plugin headers, package builders, and the live staging server were verified and found to be in **100% synchronization at v1.4.0**.

---

## 2. Git & Working Tree State

| Property | Value | Evidence / Verification |
|---|---|---|
| **Repository URL** | `https://github.com/refatbd/uniselv-resource-manager` | Cloned from upstream origin |
| **Active Branch** | `main` | Verified via `git branch --show-current` |
| **Commit SHA** | `a0fcfc3` | `docs: remove internal test harness references from public plugin documentation` |
| **Working Tree Status** | Clean | Verified via `git status --porcelain` |
| **Parent Commit** | `6576f0d` | `docs: add v1.4.0 changelog, update readme, admin and user guides for 8-services platform suite` |

---

## 3. Version & Package Alignment Audit

To prevent production regressions and deployment drift, all version identifiers were cross-compared across local and remote surfaces:

| Target File / Surface | Version Defined | Status | Notes |
|---|---|---|---|
| `plugin/info.json` | `1.4.0` | **MATCH** | `"version": "1.4.0"`, `"requires": "4.9.1"`, last updated `2026-11-14` |
| `plugin/uniselv-resman.php` (Header) | `1.4.0` | **MATCH** | `Version: 1.4.0` in plugin declaration block |
| `plugin/uniselv-resman.php` (Assets) | `1.4.0` | **MATCH** | Asset cache-busting query parameter: `-1.4.0` |
| `CHANGELOG.md` | `1.4.0` | **MATCH** | Detailed release notes for v1.4.0 present |
| `README.md` | `1.4.0` | **MATCH** | Documentation reflects v1.4.0 feature matrix |
| `package_plugin.php` | `1.4.0` | **MATCH** | Strict regex assertion enforcing version parity |
| **Staging Server Installed Plugin** | `1.4.0` | **MATCH** | Verified at `/usr/local/webuzo/enduser/plugins/uniselv-resman/info.json` |
| **Staging Service Runtime** | `1.4.0` | **MATCH** | `uniselv-resman-agent.service` active and verified |

**Conclusion:** Zero version discrepancy detected. The staging server actively runs the exact codebase represented by the current `main` branch.

---

## 4. Architectural Stack & Technical Topology

The plugin operates without third-party frameworks or external dependencies:

```
[ Webuzo Web Interface (Apache/Nginx/EMPS) ]
                     │
         PHP Plugin Hooks (admin_act / enduser_act)
                     │
          UNIX Domain Socket (/run/uniselv-resman/ipc.sock)
                     │  (JSON request/response protocol)
                     ▼
  [ Python 3 Daemon Agent (uniselv-resman-agent.service) ]
                     │
     ┌───────────────┼───────────────┬────────────────┐
     ▼               ▼               ▼                ▼
[ Linux Cgroups v2 ] [ SQLite DB ] [ Systemd Units ] [ FastCGI / PHP-FPM ]
(/sys/fs/cgroup)    (metrics.db)   (wpiso-*.service) (Socket routing)
```

- **Frontend Core:** Native Vanilla JavaScript (`plugin/assets/app.js`, 398 KB) and native CSS (`plugin/assets/style.css`, 61.5 KB). Inline SVG vector graphics for all telemetry gauges and historical trend charts. Zero CDN dependencies.
- **Backend Core:** PHP 8+ procedural controller (`plugin/uniselv-resman.php`, 248 KB) interfacing with Webuzo core globals and the `UniselvApiClient` wrapper (`plugin/api_client.php`).
- **Inter-Process Communication (IPC):** Bounded UNIX domain socket at `/run/uniselv-resman/ipc.sock` using length-delimited JSON payloads with strict RBAC enforcement based on peer credentials (`SO_PEERCRED`).
- **Agent Daemon:** Python 3 systemd background service (`/usr/local/uniselv-resman/agent/agent_daemon.py`) running with a memory limit of 128 MB and task limit of 64.
- **Telemetry Persistence:** SQLite 3 WAL-mode database at `/var/lib/uniselv-resource-manager/metrics.db` with automated rolling retention and vacuuming.

---

## 5. Staging Environment Diagnostics

A non-mutating SSH audit of the staging host (`51.79.144.93`) confirmed:
- **Operating System:** Ubuntu Linux (Kernel with native cgroups v2 enabled).
- **Webuzo Installation:** `/usr/local/webuzo` and `/var/webuzo`.
- **Active Service:** `uniselv-resman-agent.service` loaded, enabled, and active (running for over 20 days uptime).
- **Service Memory Usage:** ~68.8 MB (well below the 128 MB maximum cap).
- **Webuzo Ports:** Admin Panel on HTTPS port `2005`; Enduser Panel on HTTPS port `5507`.
