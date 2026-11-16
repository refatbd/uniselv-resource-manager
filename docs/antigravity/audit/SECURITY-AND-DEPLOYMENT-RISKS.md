# UNISELV Resource Manager — Security & Deployment Risk Register

> Stage A Deliverable — Production Safety, Tenant Boundary & Deployment Risk Assessment
> Policy Alignment: Adheres strictly to `docs/antigravity/06-SERVER-ACCESS-SAFETY.md`.

---

## 1. Security & Operational Risk Matrix

| Risk ID | Risk Category | Severity | Probability | Risk Description | Mitigation & Engineering Controls |
|---|---|---|---|---|---|
| **SEC-01** | **Tenant Isolation** | Critical | Low | Accidental exposure of other tenants' process data or metrics in Enduser panel. | Strict backend enforcement: `auth['user']` is validated in `ipc_server.py`. Enduser requests for foreign usernames are rejected or forced to their own username. Redesign touches only UI markup/presentation. |
| **SEC-02** | **CSRF Protection** | High | Low | UI forms or action triggers omitting Webuzo session CSRF token. | All POST and asynchronous requests verify `uniselv_verify_csrf($user)` prior to dispatching daemon commands. No token handling is altered. |
| **SEC-03** | **Privilege Escalation** | High | Very Low | Client-side attempts to invoke root actions (e.g. killing system processes, altering cgroups). | The daemon socket validates `SO_PEERCRED` on Linux. The Enduser cannot call `sync_account_limits` or administrative endpoints. UI will never render admin controls in enduser view. |
| **SEC-04** | **Third-Party CDN Leakage** | Medium | Low | Accidental injection of external font, script, or stylesheet CDNs (e.g. Google Fonts, cdnjs). | Zero external dependencies. All fonts use standard system UI stacks; all icons are native inline SVG; all scripts/styles are bundled locally. |
| **OPS-01** | **Production Drift** | High | Low | Staging changes overwriting uncommitted production hotfixes. | Full file integrity and version cross-check confirmed matching SHA at v1.4.0. Clean baseline git commit required before changes. |
| **OPS-02** | **Asset Cache Invalidation** | Medium | Medium | Webuzo panel serving stale `style.css` or `app.js` from browser cache after upgrade. | Retain and update the query string version suffix (e.g. `?v=<filemtime>-1.4.1`) in `uniselv-resman.php` to guarantee instant client cache refresh. |
| **OPS-03** | **Package Archive Mismatch** | High | Low | Generated ZIP archive missing correct Linux file permissions (0755 for dirs, 0644 for files). | Packaging script `package_plugin.php` automatically asserts Unix permissions and SHA-256 manifests on every build. |

---

## 2. Server Safety Boundary Protocols

In strict accordance with `06-SERVER-ACCESS-SAFETY.md`:
1. **No Destructive Server Commands:** The agent will never execute unverified commands that restart services, terminate processes, modify firewall rules, or mutate `/sys/fs/cgroup/`.
2. **Read-Only Audit Phase:** All audit investigations are strictly non-mutating (`git status`, `systemctl status`, read-only file queries, non-privileged browser inspection).
3. **Dedicated Feature Branching:** All redesign implementation work will occur on an isolated feature branch (`ui/precision-operations-console`).
4. **Verified Rollback Mechanism:** Before any deployment to staging or production, a full backup of `/usr/local/webuzo/plugins/uniselv-resman` and current archive state is verified.

---

## 3. Rollback Procedure

In the event of an unexpected regression during testing:
1. **Git Level:** Revert the feature branch commit: `git revert <commit-sha>` and rebuild the package.
2. **Server Level:** 
   - Stored backup at `/var/webuzo/backup/uniselv-resman.bak.<timestamp>` can be restored within 10 seconds.
   - Run `/usr/bin/php /usr/local/webuzo/plugins/uniselv-resman/install.php` to restore verified plugin state.
   - Reload Webuzo panel service: `systemctl restart webuzo.service`.
