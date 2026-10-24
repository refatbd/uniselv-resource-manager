# Exact source changes — 1.1.27

Already-applied release source changes relative to 1.1.26; not extra post-install paste steps. Prefer the reviewed complete package.

- Back up existing files and ownership/restoration manifests together.
- Use UTF-8/LF. Replace existing files; do not append duplicate imports, functions or directives. New files start at their first line and end at their final line.
- Install through the reviewed privileged deployment workflow. Restore root ownership and installer execution modes.
- Run Python/PHP/JavaScript syntax, regression, service/API/HTTP and ZIP closure checks. Configuration values and full workload/lifecycle readiness remain distinct.

## uniselv-resman/agent/agent_daemon.py

Installed paths: /usr/local/webuzo/plugins/uniselv-resman/agent/agent_daemon.py; ALSO /usr/local/uniselv-resman/agent/agent_daemon.py

Replace the full file; never append duplicate functions/directives. New files run from first through final line.

### Block 1 — replace

Existing anchor AFTER which:
```text

    def check_expired_overrides(self):
```

Existing anchor BEFORE which:
```text
            for row in expired:
                target_user = row['username']
```

Existing content to replace/remove (not copied):
```text
        """Revert temporary plan overrides whose expiration time has passed with verified API calls."""
        now = int(time.time())
        conn = self.handler.get_db()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM temporary_overrides WHERE status = 'active' AND expires_at <= ?", (now,))
            expired = cur.fetchall()
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
        """Serialize boost recovery and only finish after effective restoration."""
        with self.handler._override_lock:
            conn = self.handler.get_db()
            try:
                expired = conn.execute("SELECT * FROM temporary_overrides WHERE (status IN ('applying','active','failed_restoration') AND expires_at <= ?) OR status = 'applying'", (int(time.time()),)).fetchall()
            finally:
                conn.close()
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text

    def check_expired_overrides(self):
        """Serialize boost recovery and only finish after effective restoration."""
        with self.handler._override_lock:
            conn = self.handler.get_db()
            try:
                expired = conn.execute("SELECT * FROM temporary_overrides WHERE (status IN ('applying','active','failed_restoration') AND expires_at <= ?) OR status = 'applying'", (int(time.time()),)).fetchall()
            finally:
                conn.close()
            for row in expired:
                try:
```

### Block 2 — replace

Existing anchor AFTER which:
```text
            expired = cur.fetchall()
            for row in expired:
```

Existing anchor BEFORE which:
```text
                    conn.commit()
                    
```

Existing content to replace/remove (not copied):
```text
                target_user = row['username']
                original_plan = row['original_plan']
                row_id = row['id']

                user_info_path = f"/var/webuzo/users/{target_user}/info"
                success = False
                err_msg = ""
                if os.path.exists(user_info_path):
                    try:
                        with open(user_info_path, 'r', encoding='utf-8') as f:
                            u_info = json.load(f)
                        u_info['resource_limit'] = original_plan
                        tmp_path = f"{user_info_path}.tmp.{os.getpid()}"
                        with open(tmp_path, 'w', encoding='utf-8') as f:
                            json.dump(u_info, f, indent=4)
                        os.replace(tmp_path, user_info_path)
                        success = True
                    except Exception as e:
                        err_msg = str(e)
                else:
                    err_msg = f"User info file {user_info_path} does not exist"

                if success:
                    cur.execute("UPDATE temporary_overrides SET status = 'expired' WHERE id = ?", (row_id,))
                    cur.execute("""
                        INSERT INTO audit_log (timestamp, actor, action, target_account, details_json)
                        VALUES (?, 'system', 'override_expired', ?, ?)
                    """, (now, target_user, json.dumps({'restored_plan': original_plan, 'status': 'success'})))
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                try:
                    result = self.handler.restore_temporary_override(row, 'system')
                except Exception as error:
                    result = {'error': str(error)}
                success = result.get('success') is True
                status = 'expired' if success else 'failed_restoration'
                conn = self.handler.get_db()
                try:
                    changed = conn.execute("UPDATE temporary_overrides SET status = ? WHERE id = ? AND status IN ('applying','active','failed_restoration')", (status, row['id'])).rowcount
                    if changed and (success or row['status'] != status):
                        conn.execute("INSERT INTO audit_log (timestamp, actor, action, target_account, details_json) VALUES (?, 'system', ?, ?, ?)",
                            (int(time.time()), 'override_expired' if success else 'override_restoration_failed', row['username'], json.dumps({'override_id': row['id'], 'restored_plan': row['original_plan'], 'result': result})))
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                conn.close()
            for row in expired:
                try:
                    result = self.handler.restore_temporary_override(row, 'system')
                except Exception as error:
                    result = {'error': str(error)}
                success = result.get('success') is True
                status = 'expired' if success else 'failed_restoration'
                conn = self.handler.get_db()
                try:
                    changed = conn.execute("UPDATE temporary_overrides SET status = ? WHERE id = ? AND status IN ('applying','active','failed_restoration')", (status, row['id'])).rowcount
                    if changed and (success or row['status'] != status):
                        conn.execute("INSERT INTO audit_log (timestamp, actor, action, target_account, details_json) VALUES (?, 'system', ?, ?, ?)",
                            (int(time.time()), 'override_expired' if success else 'override_restoration_failed', row['username'], json.dumps({'override_id': row['id'], 'restored_plan': row['original_plan'], 'result': result})))
                    conn.commit()
                finally:
```

### Block 3 — replace

Existing anchor AFTER which:
```text
                    """, (now, target_user, json.dumps({'restored_plan': original_plan, 'status': 'success'})))
                    conn.commit()
```

Existing anchor BEFORE which:
```text

    def ensure_startup_enforcement_boundaries(self):
```

Existing content to replace/remove (not copied):
```text
                    
                    # Ensure native slice and golden mirror slice reflect restored plan
                    users = self.collector.get_webuzo_users()
                    if target_user in users:
                        uid = users[target_user]['uid']
                        try:
                            self.handler._write_native_slice(uid, original_plan)
                            subprocess.run(['python3', '/usr/local/sbin/golden-shield.py', 'prepare-account', str(uid)], capture_output=True, timeout=20)
                        except Exception as prep_err:
                            print(f"[Agent Override Prepare-Account Error] {prep_err}", file=sys.stderr)
                else:
                    # Mark restoration failed so it remains visible and retryable
                    cur.execute("UPDATE temporary_overrides SET status = 'failed_restoration' WHERE id = ?", (row_id,))
                    cur.execute("""
                        INSERT INTO audit_log (timestamp, actor, action, target_account, details_json)
                        VALUES (?, 'system', 'override_restoration_failed', ?, ?)
                    """, (now, target_user, json.dumps({'attempted_plan': original_plan, 'error': err_msg})))
                    conn.commit()
        except Exception as e:
            print(f"[Agent Override Error] {e}", file=sys.stderr)
        finally:
            conn.close()
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                finally:
                    conn.close()
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                            (int(time.time()), 'override_expired' if success else 'override_restoration_failed', row['username'], json.dumps({'override_id': row['id'], 'restored_plan': row['original_plan'], 'result': result})))
                    conn.commit()
                finally:
                    conn.close()

    def ensure_startup_enforcement_boundaries(self):
```

## uniselv-resman/agent/collector.py

Installed paths: /usr/local/webuzo/plugins/uniselv-resman/agent/collector.py; ALSO /usr/local/uniselv-resman/agent/collector.py

Replace the full file; never append duplicate functions/directives. New files run from first through final line.

### Block 1 — insert

Existing anchor AFTER which:
```text
        redacted = re.sub(pat, rep, redacted, flags=re.IGNORECASE)
    return redacted
```

Existing anchor BEFORE which:
```text

class MetricsCollector:
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text

def read_pids_events_tree(root):
    """Sum local fork-failure counters without adding modern hierarchy totals twice.

    Older kernels expose local pids.events only; newer kernels provide an
    explicit pids.events.local file alongside the hierarchical counter.
    """
    filename = 'pids.events.local' if os.path.exists(os.path.join(root, 'pids.events.local')) else 'pids.events'
    total = 0
    for directory, _, files in os.walk(root, followlinks=False):
        if filename in files:
            total += int(parse_key_value_file(os.path.join(directory, filename)).get('max', 0))
    return total

```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
        redacted = re.sub(pat, rep, redacted, flags=re.IGNORECASE)
    return redacted

def read_pids_events_tree(root):
    """Sum local fork-failure counters without adding modern hierarchy totals twice.

    Older kernels expose local pids.events only; newer kernels provide an
    explicit pids.events.local file alongside the hierarchical counter.
    """
    filename = 'pids.events.local' if os.path.exists(os.path.join(root, 'pids.events.local')) else 'pids.events'
    total = 0
    for directory, _, files in os.walk(root, followlinks=False):
        if filename in files:
            total += int(parse_key_value_file(os.path.join(directory, filename)).get('max', 0))
    return total


class MetricsCollector:
```

### Block 2 — replace

Existing anchor AFTER which:
```text
            for dst,key in [('oom_kill','oom_kill'),('mem_high_events','high'),('mem_max_events','max')]:
                stats[dst] += int(events.get(key, 0))
```

Existing anchor BEFORE which:
```text
            io = parse_io_stat(os.path.join(source, 'io.stat'))
            for key in stats['io']: stats['io'][key] += io.get(key, 0)
```

Existing content to replace/remove (not copied):
```text
            stats['task_limit_events'] += int(parse_key_value_file(os.path.join(source, 'pids.events')).get('max', 0))
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
            stats['task_limit_events'] += read_pids_events_tree(source)
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
            for dst,key in [('oom_kill','oom_kill'),('mem_high_events','high'),('mem_max_events','max')]:
                stats[dst] += int(events.get(key, 0))
            stats['task_limit_events'] += read_pids_events_tree(source)
            io = parse_io_stat(os.path.join(source, 'io.stat'))
            for key in stats['io']: stats['io'][key] += io.get(key, 0)
```

## uniselv-resman/agent/ipc_server.py

Installed paths: /usr/local/webuzo/plugins/uniselv-resman/agent/ipc_server.py; ALSO /usr/local/uniselv-resman/agent/ipc_server.py

Replace the full file; never append duplicate functions/directives. New files run from first through final line.

### Block 1 — insert

Existing anchor AFTER which:
```text

class IpcRequestHandler:
```

Existing anchor BEFORE which:
```text
    def __init__(self, db_path: str, collector):
        self.db_path = db_path
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
    _override_lock = threading.RLock()

```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text

class IpcRequestHandler:
    _override_lock = threading.RLock()

    def __init__(self, db_path: str, collector):
        self.db_path = db_path
```

### Block 2 — replace

Existing anchor AFTER which:
```text
                if action in {'get_admin_audit_limits', 'audit_limits'}:
                    result = self.action_admin_audit_limits()
```

Existing anchor BEFORE which:
```text
                if action == 'get_enduser_support_export' and not self.is_permission_granted(user, 'reseller', 'can_export_diagnostics'):
                    return {'error': 'Forbidden: Reseller export permission denied', 'status_code': 403}
```

Existing content to replace/remove (not copied):
```text
                    result['audit'] = [row for row in result.get('audit', []) if row.get('username') in owned]
                    return result
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                    rows = [row for row in result.get('accounts', result.get('audit', [])) if row.get('username') in owned]
                    return {'success': result.get('success', False), 'accounts': rows, 'audit': rows,
                        'total_accounts': len(rows), 'mismatch_count': sum(not row.get('is_synchronized', False) for row in rows),
                        'php_runtime': [row for row in result.get('php_runtime', []) if row.get('user') in owned],
                        'php_runtime_error': 'Scoped runtime details unavailable; ask the server administrator.' if result.get('php_runtime_error') else None}
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                if action in {'get_admin_audit_limits', 'audit_limits'}:
                    result = self.action_admin_audit_limits()
                    rows = [row for row in result.get('accounts', result.get('audit', [])) if row.get('username') in owned]
                    return {'success': result.get('success', False), 'accounts': rows, 'audit': rows,
                        'total_accounts': len(rows), 'mismatch_count': sum(not row.get('is_synchronized', False) for row in rows),
                        'php_runtime': [row for row in result.get('php_runtime', []) if row.get('user') in owned],
                        'php_runtime_error': 'Scoped runtime details unavailable; ask the server administrator.' if result.get('php_runtime_error') else None}
                if action == 'get_enduser_support_export' and not self.is_permission_granted(user, 'reseller', 'can_export_diagnostics'):
                    return {'error': 'Forbidden: Reseller export permission denied', 'status_code': 403}
```

### Block 3 — replace

Existing anchor AFTER which:
```text

    def action_set_temporary_override(self, admin_user: str, params: Dict[str, Any], is_reseller: bool = False) -> Dict[str, Any]:
```

Existing anchor BEFORE which:
```text

        if not target_user or not override_plan:
```

Existing content to replace/remove (not copied):
```text
        target_user = params.get('username')
        override_plan = params.get('override_plan') or params.get('plan')
        duration_minutes = int(params.get('duration_minutes') or params.get('duration') or 60)
        reason = params.get('reason', 'Admin temporary boost')
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
        with self._override_lock:
            return self._set_temporary_override(admin_user, params, is_reseller)
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text

    def action_set_temporary_override(self, admin_user: str, params: Dict[str, Any], is_reseller: bool = False) -> Dict[str, Any]:
        with self._override_lock:
            return self._set_temporary_override(admin_user, params, is_reseller)

    def _set_temporary_override(self, admin_user: str, params: Dict[str, Any], is_reseller: bool = False) -> Dict[str, Any]:
```

### Block 4 — replace

Existing anchor AFTER which:
```text
        reason = params.get('reason', 'Admin temporary boost')

```

Existing anchor BEFORE which:
```text
            return {'error': 'User not found', 'status_code': 404}

```

Existing content to replace/remove (not copied):
```text
        if not target_user or not override_plan:
            return {'error': 'Username and override_plan are required', 'status_code': 400}

        target_user = str(target_user).strip()
        override_plan = str(override_plan).strip()

        if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9_.-]{0,63}$', target_user) or '..' in target_user or '/' in target_user or '\\' in target_user:
            return {'error': f"Security Refusal: Invalid target username format '{target_user}'", 'status_code': 400}

        if not re.match(r'^[a-zA-Z0-9_.-]{1,64}$', override_plan) or '..' in override_plan or '/' in override_plan or '\\' in override_plan:
            return {'error': f"Security Refusal: Invalid override plan format '{override_plan}'", 'status_code': 400}

        users = self.collector.get_webuzo_users()
        if target_user not in users:
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
    def _set_temporary_override(self, admin_user: str, params: Dict[str, Any], is_reseller: bool = False) -> Dict[str, Any]:
        target = str(params.get('username') or '').strip()
        plan = str(params.get('override_plan') or params.get('plan') or '').strip()
        try:
            minutes = int(params.get('duration_minutes', params.get('duration', 60)))
            if minutes < 1: raise ValueError()
        except (TypeError, ValueError):
            return {'error': 'Duration must be a positive number of minutes', 'status_code': 400}
        if not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9_.-]{0,63}', target) or '..' in target:
            return {'error': 'Security Refusal: Invalid target username format', 'status_code': 400}
        if not re.fullmatch(r'[a-zA-Z0-9_.-]{1,64}', plan) or '..' in plan:
            return {'error': 'Security Refusal: Invalid override plan format', 'status_code': 400}
        account = self.collector.get_webuzo_users().get(target)
        if not account:
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
            return self._set_temporary_override(admin_user, params, is_reseller)

    def _set_temporary_override(self, admin_user: str, params: Dict[str, Any], is_reseller: bool = False) -> Dict[str, Any]:
        target = str(params.get('username') or '').strip()
        plan = str(params.get('override_plan') or params.get('plan') or '').strip()
        try:
            minutes = int(params.get('duration_minutes', params.get('duration', 60)))
            if minutes < 1: raise ValueError()
        except (TypeError, ValueError):
            return {'error': 'Duration must be a positive number of minutes', 'status_code': 400}
        if not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9_.-]{0,63}', target) or '..' in target:
            return {'error': 'Security Refusal: Invalid target username format', 'status_code': 400}
        if not re.fullmatch(r'[a-zA-Z0-9_.-]{1,64}', plan) or '..' in plan:
            return {'error': 'Security Refusal: Invalid override plan format', 'status_code': 400}
        account = self.collector.get_webuzo_users().get(target)
        if not account:
            return {'error': 'User not found', 'status_code': 404}
        if is_reseller and admin_user != 'root' and account.get('owner') != admin_user and target != admin_user:
```

### Block 5 — replace

Existing anchor AFTER which:
```text
        if target_user not in users:
            return {'error': 'User not found', 'status_code': 404}
```

Existing anchor BEFORE which:
```text
        now = int(time.time())
        expires_at = now + (duration_minutes * 60)
```

Existing content to replace/remove (not copied):
```text

        # B01: Reseller ownership enforcement
        if is_reseller and admin_user != 'root':
            target_data = users.get(target_user, {})
            if target_data.get('owner') != admin_user and target_user != admin_user:
                return {
                    'error': f"Forbidden: Reseller '{admin_user}' is not authorized to apply overrides to account '{target_user}'",
                    'status_code': 403
                }

        original_plan = users[target_user]['plan_name']
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
        if is_reseller and admin_user != 'root' and account.get('owner') != admin_user and target != admin_user:
            return {'error': 'Forbidden: Reseller cannot boost this account', 'status_code': 403}
        original = account['plan_name']
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
        if not account:
            return {'error': 'User not found', 'status_code': 404}
        if is_reseller and admin_user != 'root' and account.get('owner') != admin_user and target != admin_user:
            return {'error': 'Forbidden: Reseller cannot boost this account', 'status_code': 403}
        original = account['plan_name']
        now = int(time.time())
        conn = self.get_db()
```

### Block 6 — remove

Existing anchor AFTER which:
```text
        original_plan = users[target_user]['plan_name']
        now = int(time.time())
```

Existing anchor BEFORE which:
```text
        conn = self.get_db()
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO temporary_overrides (username, uid, original_plan, override_plan, created_at, expires_at, status, reason)
```

Existing content to replace/remove (not copied):
```text
        expires_at = now + (duration_minutes * 60)

        # Validate target plan exists in Webuzo cgroups
        plan_file = f"/var/webuzo/cgroups/{override_plan}"
        if not os.path.exists(plan_file):
            return {'error': f"Target override plan '{override_plan}' does not exist in /var/webuzo/cgroups/", 'status_code': 422}

        # Transactional update: update Webuzo user info
        user_info_path = f"/var/webuzo/users/{target_user}/info"
        if os.path.exists(user_info_path):
            try:
                with open(user_info_path, 'r', encoding='utf-8') as f:
                    u_info = json.load(f)
                u_info['resource_limit'] = override_plan
                tmp_path = f"{user_info_path}.tmp.{os.getpid()}"
                with open(tmp_path, 'w', encoding='utf-8') as f:
                    json.dump(u_info, f, indent=4)
                os.replace(tmp_path, user_info_path)
            except Exception as e:
                return {'error': f"Failed to update Webuzo user info: {e}"}

        # Sync native slice definition so golden-shield mirror reads active boost plan
        uid = users[target_user]['uid']
        self._write_native_slice(uid, override_plan)

        # Apply slice limits immediately
        prep_res = subprocess.run(['python3', '/usr/local/sbin/golden-shield.py', 'prepare-account', str(uid)], capture_output=True, text=True, timeout=15)
        if prep_res.returncode != 0:
            # Revert info file and native slice
            try:
                with open(user_info_path, 'r', encoding='utf-8') as f:
                    u_info = json.load(f)
                u_info['resource_limit'] = original_plan
                with open(user_info_path, 'w', encoding='utf-8') as f:
                    json.dump(u_info, f, indent=4)
                self._write_native_slice(uid, original_plan)
                subprocess.run(['python3', '/usr/local/sbin/golden-shield.py', 'prepare-account', str(uid)], capture_output=True, timeout=15)
            except Exception:
                pass
            return {'error': f"Failed to apply slice limits for override: {prep_res.stderr or prep_res.stdout}"}

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text

```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
        original = account['plan_name']
        now = int(time.time())
        conn = self.get_db()
        try:
```

### Block 7 — replace

Existing anchor AFTER which:
```text
            return {'error': f"Failed to apply slice limits for override: {prep_res.stderr or prep_res.stdout}"}

        conn = self.get_db()
        try:
```

Existing anchor BEFORE which:
```text
            conn.commit()
        finally:
            conn.close()

        return {
            'success': True,
            'override_id': new_id,
```

Existing content to replace/remove (not copied):
```text
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO temporary_overrides (username, uid, original_plan, override_plan, created_at, expires_at, status, reason)
                VALUES (?, ?, ?, ?, ?, ?, 'active', ?)
            """, (target_user, uid, original_plan, override_plan, now, expires_at, reason))
            new_id = cur.lastrowid

            conn.execute("""
                INSERT INTO audit_log (timestamp, actor, action, target_account, details_json)
                VALUES (?, ?, 'set_override', ?, ?)
            """, (now, admin_user, target_user, json.dumps({'override_id': new_id, 'from': original_plan, 'to': override_plan, 'expires_at': expires_at})))
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
            if conn.execute("SELECT 1 FROM temporary_overrides WHERE username = ? AND status IN ('applying','active','failed_restoration') LIMIT 1", (target,)).fetchone():
                return {'error': 'An active or unresolved boost already exists for this account', 'status_code': 409}
            cur = conn.execute("INSERT INTO temporary_overrides (username,uid,original_plan,override_plan,created_at,expires_at,status,reason) VALUES (?,?,?,?,?,?,'applying',?)",
                (target, account['uid'], original, plan, now, now + minutes * 60, str(params.get('reason') or 'Admin temporary boost')))
            override_id = cur.lastrowid
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
        conn = self.get_db()
        try:
            if conn.execute("SELECT 1 FROM temporary_overrides WHERE username = ? AND status IN ('applying','active','failed_restoration') LIMIT 1", (target,)).fetchone():
                return {'error': 'An active or unresolved boost already exists for this account', 'status_code': 409}
            cur = conn.execute("INSERT INTO temporary_overrides (username,uid,original_plan,override_plan,created_at,expires_at,status,reason) VALUES (?,?,?,?,?,?,'applying',?)",
                (target, account['uid'], original, plan, now, now + minutes * 60, str(params.get('reason') or 'Admin temporary boost')))
            override_id = cur.lastrowid
            conn.commit()
        finally:
```

### Block 8 — replace

Existing anchor AFTER which:
```text
            """, (now, admin_user, target_user, json.dumps({'override_id': new_id, 'from': original_plan, 'to': override_plan, 'expires_at': expires_at})))
            conn.commit()
        finally:
            conn.close()
```

Existing anchor BEFORE which:
```text
        conn = self.get_db()
        try:
            cur = conn.cursor()
            if override_id > 0:
```

Existing content to replace/remove (not copied):
```text

        return {
            'success': True,
            'override_id': new_id,
            'active_plan': override_plan,
            'original_plan': original_plan,
            'expires_at': expires_at,
            'message': f'Temporary override applied: {target_user} boosted to {override_plan} for {duration_minutes} minutes'
        }

    def action_cancel_temporary_override(self, admin_user: str, params: Dict[str, Any], is_reseller: bool = False) -> Dict[str, Any]:
        override_id = int(params.get('id') or params.get('override_id') or 0)
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
        # Persist intent before mutation, so an agent restart can restore an interrupted boost.
        try:
            result = self.action_run_adapter_sync(admin_user, {'adapter': 'temporary_override', 'payload': {'username': target, 'plan': plan},
                '_expected_native_plan': plan, '_expected_uid': account['uid'], '_expected_current_plans': [original]})
        except Exception as error:
            result = {'error': str(error)}
        success = result.get('success') is True
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
        finally:
            conn.close()
        # Persist intent before mutation, so an agent restart can restore an interrupted boost.
        try:
            result = self.action_run_adapter_sync(admin_user, {'adapter': 'temporary_override', 'payload': {'username': target, 'plan': plan},
                '_expected_native_plan': plan, '_expected_uid': account['uid'], '_expected_current_plans': [original]})
        except Exception as error:
            result = {'error': str(error)}
        success = result.get('success') is True
        conn = self.get_db()
        try:
```

### Block 9 — replace

Existing anchor AFTER which:
```text
        override_id = int(params.get('id') or params.get('override_id') or 0)
        conn = self.get_db()
        try:
```

Existing anchor BEFORE which:
```text
            conn.commit()
        finally:
            conn.close()

        return {
            'success': True,
            'override_id': actual_id,
```

Existing content to replace/remove (not copied):
```text
            cur = conn.cursor()
            if override_id > 0:
                cur.execute("SELECT * FROM temporary_overrides WHERE id = ? AND status = 'active'", (override_id,))
            elif 'username' in params:
                cur.execute("SELECT * FROM temporary_overrides WHERE username = ? AND status = 'active' ORDER BY id DESC LIMIT 1", (params['username'],))
            else:
                return {'error': 'Missing override id or username'}
            row = cur.fetchone()
            if not row:
                return {'error': 'Active override not found'}

            target_user = row['username']
            if is_reseller and admin_user != 'root':
                users = self.collector.get_webuzo_users()
                target_data = users.get(target_user, {})
                if target_data.get('owner') != admin_user and target_user != admin_user:
                    return {
                        'error': f"Forbidden: Reseller '{admin_user}' is not authorized to cancel overrides for account '{target_user}'",
                        'status_code': 403
                    }

            original_plan = row['original_plan']
            actual_id = row['id']

            # Restore Webuzo user info
            user_info_path = f"/var/webuzo/users/{target_user}/info"
            if os.path.exists(user_info_path):
                try:
                    with open(user_info_path, 'r', encoding='utf-8') as f:
                        u_info = json.load(f)
                    u_info['resource_limit'] = original_plan
                    tmp_path = f"{user_info_path}.tmp.{os.getpid()}"
                    with open(tmp_path, 'w', encoding='utf-8') as f:
                        json.dump(u_info, f, indent=4)
                    os.replace(tmp_path, user_info_path)
                except Exception as e:
                    return {'error': f"Failed to restore Webuzo user info: {e}"}

            users = self.collector.get_webuzo_users()
            if target_user in users:
                uid = users[target_user]['uid']
                self._write_native_slice(uid, original_plan)
                subprocess.run(['python3', '/usr/local/sbin/golden-shield.py', 'prepare-account', str(uid)], capture_output=True, timeout=15)

            cur.execute("UPDATE temporary_overrides SET status = 'cancelled' WHERE id = ?", (actual_id,))
            cur.execute("""
                INSERT INTO audit_log (timestamp, actor, action, target_account, details_json)
                VALUES (?, ?, 'cancel_override', ?, ?)
            """, (int(time.time()), admin_user, target_user, json.dumps({'override_id': actual_id, 'restored_to': original_plan})))
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
            conn.execute("UPDATE temporary_overrides SET status = ?, expires_at = ? WHERE id = ?", ('active' if success else 'failed_restoration', now + minutes * 60 if success else now, override_id))
            conn.execute("INSERT INTO audit_log(timestamp,actor,action,target_account,details_json) VALUES(?,?,?,?,?)",
                (now, admin_user, 'set_override' if success else 'override_apply_failed', target, json.dumps({'override_id': override_id, 'from': original, 'to': plan, 'result': result})))
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
        conn = self.get_db()
        try:
            conn.execute("UPDATE temporary_overrides SET status = ?, expires_at = ? WHERE id = ?", ('active' if success else 'failed_restoration', now + minutes * 60 if success else now, override_id))
            conn.execute("INSERT INTO audit_log(timestamp,actor,action,target_account,details_json) VALUES(?,?,?,?,?)",
                (now, admin_user, 'set_override' if success else 'override_apply_failed', target, json.dumps({'override_id': override_id, 'from': original, 'to': plan, 'result': result})))
            conn.commit()
        finally:
```

### Block 10 — insert

Existing anchor AFTER which:
```text
            """, (int(time.time()), admin_user, target_user, json.dumps({'override_id': actual_id, 'restored_to': original_plan})))
            conn.commit()
        finally:
            conn.close()
```

Existing anchor BEFORE which:
```text

        return {
            'success': True,
            'override_id': actual_id,
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
        if not success:
            return {'error': 'Temporary boost was not verified; restoration remains tracked', 'status_code': 500, 'override_id': override_id, 'apply_result': result}
        return {'success': True, 'override_id': override_id, 'active_plan': plan, 'original_plan': original, 'expires_at': now + minutes * 60, 'message': 'Temporary boost applied and limits verified'}
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
        finally:
            conn.close()
        if not success:
            return {'error': 'Temporary boost was not verified; restoration remains tracked', 'status_code': 500, 'override_id': override_id, 'apply_result': result}
        return {'success': True, 'override_id': override_id, 'active_plan': plan, 'original_plan': original, 'expires_at': now + minutes * 60, 'message': 'Temporary boost applied and limits verified'}

    def restore_temporary_override(self, row, actor: str) -> Dict[str, Any]:
```

### Block 11 — replace

Existing anchor AFTER which:
```text
            """, (int(time.time()), admin_user, target_user, json.dumps({'override_id': actual_id, 'restored_to': original_plan})))
            conn.commit()
        finally:
            conn.close()

```

Existing anchor BEFORE which:
```text

    def action_sync_native_plans(self, admin_user: str) -> Dict[str, Any]:
```

Existing content to replace/remove (not copied):
```text
        return {
            'success': True,
            'override_id': actual_id,
            'username': target_user,
            'restored_plan': original_plan,
            'message': f'Override cancelled. Restored {target_user} to {original_plan}'
        }
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
    def restore_temporary_override(self, row, actor: str) -> Dict[str, Any]:
        """Use the normal verified plan transaction; reject UID reuse/manual drift."""
        target = str(row['username'])
        original = str(row['original_plan'])
        if not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9_.-]{0,63}', target) or '..' in target:
            return {'error': 'Invalid stored override account', 'status_code': 400}
        if not re.fullmatch(r'[a-zA-Z0-9_.-]{1,64}', original) or '..' in original:
            return {'error': 'Invalid stored original plan', 'status_code': 400}
        account = self.collector.get_webuzo_users().get(target)
        if not account or int(account['uid']) != int(row['uid']):
            return {'error': 'Override account is missing or UID changed; restoration refused', 'status_code': 409}
        if account['plan_name'] not in (row['override_plan'], original):
            return {'error': 'Account plan changed outside this boost; restoration requires review', 'status_code': 409}
        return self.action_run_adapter_sync(actor, {'adapter': 'temporary_override',
            'payload': {'username': target, 'plan': original}, '_expected_native_plan': original,
            '_expected_uid': row['uid'], '_expected_current_plans': [row['override_plan'], original]})

    def action_cancel_temporary_override(self, admin_user: str, params: Dict[str, Any], is_reseller: bool = False) -> Dict[str, Any]:
        with self._override_lock:
            return self._cancel_temporary_override(admin_user, params, is_reseller)

    def _cancel_temporary_override(self, admin_user: str, params: Dict[str, Any], is_reseller: bool = False) -> Dict[str, Any]:
        try:
            override_id = int(params.get('id') or params.get('override_id') or 0)
        except (ValueError, TypeError):
            return {'error': 'Invalid override id', 'status_code': 400}
        conn = self.get_db()
        try:
            if override_id > 0:
                row = conn.execute("SELECT * FROM temporary_overrides WHERE id = ? AND status IN ('applying','active','failed_restoration')", (override_id,)).fetchone()
            elif 'username' in params:
                row = conn.execute("SELECT * FROM temporary_overrides WHERE username = ? AND status IN ('applying','active','failed_restoration') ORDER BY id DESC LIMIT 1", (params['username'],)).fetchone()
            else:
                return {'error': 'Missing override id or username'}
        finally:
            conn.close()
        if not row:
            return {'error': 'Active override not found'}
        if is_reseller and admin_user != 'root':
            account = self.collector.get_webuzo_users().get(row['username'], {})
            if account.get('owner') != admin_user and row['username'] != admin_user:
                return {'error': 'Forbidden: Reseller cannot cancel this account override', 'status_code': 403}
        result = self.restore_temporary_override(row, admin_user)
        if result.get('success') is not True:
            return {'error': 'Override restoration failed', 'status_code': 500, 'restore_result': result, 'override_id': row['id']}
        conn = self.get_db()
        try:
            conn.execute("UPDATE temporary_overrides SET status = 'cancelled' WHERE id = ? AND status IN ('applying','active','failed_restoration')", (row['id'],))
            conn.execute("INSERT INTO audit_log (timestamp, actor, action, target_account, details_json) VALUES (?, ?, 'cancel_override', ?, ?)",
                (int(time.time()), admin_user, row['username'], json.dumps({'override_id': row['id'], 'restored_to': row['original_plan']})))
            conn.commit()
        finally:
            conn.close()
        return {'success': True, 'override_id': row['id'], 'username': row['username'], 'restored_plan': row['original_plan'], 'message': 'Override cancelled and original limits verified'}
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
        return {'success': True, 'override_id': override_id, 'active_plan': plan, 'original_plan': original, 'expires_at': now + minutes * 60, 'message': 'Temporary boost applied and limits verified'}

    def restore_temporary_override(self, row, actor: str) -> Dict[str, Any]:
        """Use the normal verified plan transaction; reject UID reuse/manual drift."""
        target = str(row['username'])
        original = str(row['original_plan'])
        if not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9_.-]{0,63}', target) or '..' in target:
            return {'error': 'Invalid stored override account', 'status_code': 400}
        if not re.fullmatch(r'[a-zA-Z0-9_.-]{1,64}', original) or '..' in original:
            return {'error': 'Invalid stored original plan', 'status_code': 400}
        account = self.collector.get_webuzo_users().get(target)
        if not account or int(account['uid']) != int(row['uid']):
            return {'error': 'Override account is missing or UID changed; restoration refused', 'status_code': 409}
        if account['plan_name'] not in (row['override_plan'], original):
            return {'error': 'Account plan changed outside this boost; restoration requires review', 'status_code': 409}
        return self.action_run_adapter_sync(actor, {'adapter': 'temporary_override',
            'payload': {'username': target, 'plan': original}, '_expected_native_plan': original,
            '_expected_uid': row['uid'], '_expected_current_plans': [row['override_plan'], original]})

    def action_cancel_temporary_override(self, admin_user: str, params: Dict[str, Any], is_reseller: bool = False) -> Dict[str, Any]:
        with self._override_lock:
            return self._cancel_temporary_override(admin_user, params, is_reseller)

    def _cancel_temporary_override(self, admin_user: str, params: Dict[str, Any], is_reseller: bool = False) -> Dict[str, Any]:
        try:
            override_id = int(params.get('id') or params.get('override_id') or 0)
        except (ValueError, TypeError):
            return {'error': 'Invalid override id', 'status_code': 400}
        conn = self.get_db()
        try:
            if override_id > 0:
                row = conn.execute("SELECT * FROM temporary_overrides WHERE id = ? AND status IN ('applying','active','failed_restoration')", (override_id,)).fetchone()
            elif 'username' in params:
                row = conn.execute("SELECT * FROM temporary_overrides WHERE username = ? AND status IN ('applying','active','failed_restoration') ORDER BY id DESC LIMIT 1", (params['username'],)).fetchone()
            else:
                return {'error': 'Missing override id or username'}
        finally:
            conn.close()
        if not row:
            return {'error': 'Active override not found'}
        if is_reseller and admin_user != 'root':
            account = self.collector.get_webuzo_users().get(row['username'], {})
            if account.get('owner') != admin_user and row['username'] != admin_user:
                return {'error': 'Forbidden: Reseller cannot cancel this account override', 'status_code': 403}
        result = self.restore_temporary_override(row, admin_user)
        if result.get('success') is not True:
            return {'error': 'Override restoration failed', 'status_code': 500, 'restore_result': result, 'override_id': row['id']}
        conn = self.get_db()
        try:
            conn.execute("UPDATE temporary_overrides SET status = 'cancelled' WHERE id = ? AND status IN ('applying','active','failed_restoration')", (row['id'],))
            conn.execute("INSERT INTO audit_log (timestamp, actor, action, target_account, details_json) VALUES (?, ?, 'cancel_override', ?, ?)",
                (int(time.time()), admin_user, row['username'], json.dumps({'override_id': row['id'], 'restored_to': row['original_plan']})))
            conn.commit()
        finally:
            conn.close()
        return {'success': True, 'override_id': row['id'], 'username': row['username'], 'restored_plan': row['original_plan'], 'message': 'Override cancelled and original limits verified'}

    def action_sync_native_plans(self, admin_user: str) -> Dict[str, Any]:
```

### Block 12 — insert

Existing anchor AFTER which:
```text
        except (OSError, ValueError, subprocess.SubprocessError, AttributeError):
            pass
```

Existing anchor BEFORE which:
```text
        return {
            'cgroup_integrity': placement,
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
        override_recovery = {'status': 'UNAVAILABLE', 'pending': None, 'failed': None}
        try:
            conn = self.get_db()
            try:
                rows = conn.execute("SELECT status, COUNT(*) AS n FROM temporary_overrides WHERE status IN ('applying','failed_restoration') OR (status = 'active' AND expires_at <= ?) GROUP BY status", (int(time.time()),)).fetchall()
                counts = {r['status']: int(r['n']) for r in rows}
                failed = counts.get('failed_restoration', 0)
                pending = counts.get('applying', 0) + counts.get('active', 0)
                override_recovery = {'status': 'ATTENTION' if failed else ('PENDING' if pending else 'PASS'), 'pending': pending, 'failed': failed}
            finally:
                conn.close()
        except sqlite3.Error:
            pass
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
        except (OSError, ValueError, subprocess.SubprocessError, AttributeError):
            pass
        override_recovery = {'status': 'UNAVAILABLE', 'pending': None, 'failed': None}
        try:
            conn = self.get_db()
            try:
                rows = conn.execute("SELECT status, COUNT(*) AS n FROM temporary_overrides WHERE status IN ('applying','failed_restoration') OR (status = 'active' AND expires_at <= ?) GROUP BY status", (int(time.time()),)).fetchall()
                counts = {r['status']: int(r['n']) for r in rows}
                failed = counts.get('failed_restoration', 0)
                pending = counts.get('applying', 0) + counts.get('active', 0)
                override_recovery = {'status': 'ATTENTION' if failed else ('PENDING' if pending else 'PASS'), 'pending': pending, 'failed': failed}
            finally:
                conn.close()
        except sqlite3.Error:
            pass
        return {
            'override_recovery': override_recovery,
```

### Block 13 — insert

Existing anchor AFTER which:
```text
            pass
        return {
```

Existing anchor BEFORE which:
```text
            'cgroup_integrity': placement,
            'memory_cap_formatted': cap_display,
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
            'override_recovery': override_recovery,
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
            pass
        return {
            'override_recovery': override_recovery,
            'cgroup_integrity': placement,
            'memory_cap_formatted': cap_display,
```

### Block 14 — insert

Existing anchor AFTER which:
```text
                map_row = cur.fetchone()
                target_plan = map_row['resource_plan'] if map_row else billing_plan
```

Existing anchor BEFORE which:
```text
            finally:
                conn.close()

            # 5. Validate target user exists
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                if params.get('_expected_native_plan') is not None and target_plan != params['_expected_native_plan']:
                    return {'error': 'Internal plan restoration mapping mismatch; no limits changed', 'status_code': 409}
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                map_row = cur.fetchone()
                target_plan = map_row['resource_plan'] if map_row else billing_plan
                if params.get('_expected_native_plan') is not None and target_plan != params['_expected_native_plan']:
                    return {'error': 'Internal plan restoration mapping mismatch; no limits changed', 'status_code': 409}
            finally:
                conn.close()
```

### Block 15 — insert

Existing anchor AFTER which:
```text
            # 5. Validate target user exists
            users = self.collector.get_webuzo_users()
```

Existing anchor BEFORE which:
```text
            if target_user not in users:
                return {'error': f"User '{target_user}' does not exist on this Webuzo server", 'status_code': 404}
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
            # Internal boost transactions must not follow UID reuse or overwrite a newer plan.
            expected_uid = params.get('_expected_uid')
            if expected_uid is not None and (target_user not in users or int(users[target_user]['uid']) != int(expected_uid)):
                return {'error': 'Account identity changed before plan transaction', 'status_code': 409}
            expected_plans = params.get('_expected_current_plans')
            if expected_plans is not None and users.get(target_user, {}).get('plan_name') not in expected_plans:
                return {'error': 'Account plan changed before plan transaction', 'status_code': 409}
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
            # 5. Validate target user exists
            users = self.collector.get_webuzo_users()
            # Internal boost transactions must not follow UID reuse or overwrite a newer plan.
            expected_uid = params.get('_expected_uid')
            if expected_uid is not None and (target_user not in users or int(users[target_user]['uid']) != int(expected_uid)):
                return {'error': 'Account identity changed before plan transaction', 'status_code': 409}
            expected_plans = params.get('_expected_current_plans')
            if expected_plans is not None and users.get(target_user, {}).get('plan_name') not in expected_plans:
                return {'error': 'Account plan changed before plan transaction', 'status_code': 409}
            if target_user not in users:
                return {'error': f"User '{target_user}' does not exist on this Webuzo server", 'status_code': 404}
```

## uniselv-resman/agent/runtime_governance.py

Installed paths: /usr/local/webuzo/plugins/uniselv-resman/agent/runtime_governance.py; ALSO /usr/local/uniselv-resman/agent/runtime_governance.py

Replace the full file; never append duplicate functions/directives. New files run from first through final line.

### Block 1 — replace

Existing anchor AFTER which:
```text

def diagnostics():
```

Existing anchor BEFORE which:
```text
    counts, buckets, recent = collections.Counter(), {}, []
    for line in text.splitlines():
```

Existing content to replace/remove (not copied):
```text
    rc, text = command(['journalctl', '--since=-1h', '--no-pager', '-o', 'cat', '-n', str(MAX_JOURNAL_ROWS),
                        '-u', 'wpiso-proxy-*.service', '-u', 'wpiso-fpm-*.service'])
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
    # Expanding systemd unit globs can scan the entire journal before applying -n.
    # Bound the shared tail first, then allowlist capacity records below.
    unavailable = ''
    try:
        rc, text = command(['journalctl', '--since=-1h', '--no-pager', '-o', 'cat', '-n', str(MAX_JOURNAL_ROWS)])
        if rc: unavailable = 'Journal command failed; capacity event coverage is unavailable.'
    except (subprocess.TimeoutExpired, OSError):
        rc, text = 1, ''
        unavailable = 'Journal read timed out or was unavailable; capacity event coverage is unavailable.'
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text

def diagnostics():
    # Expanding systemd unit globs can scan the entire journal before applying -n.
    # Bound the shared tail first, then allowlist capacity records below.
    unavailable = ''
    try:
        rc, text = command(['journalctl', '--since=-1h', '--no-pager', '-o', 'cat', '-n', str(MAX_JOURNAL_ROWS)])
        if rc: unavailable = 'Journal command failed; capacity event coverage is unavailable.'
    except (subprocess.TimeoutExpired, OSError):
        rc, text = 1, ''
        unavailable = 'Journal read timed out or was unavailable; capacity event coverage is unavailable.'
    counts, buckets, recent = collections.Counter(), {}, []
    for line in text.splitlines():
```

### Block 2 — replace

Existing anchor AFTER which:
```text
    return {'available': rc == 0, 'windowSeconds': 3600, 'maxJournalRows': MAX_JOURNAL_ROWS,
            'counts': dict(counts), 'minuteBuckets': buckets, 'recent': recent[-30:],
```

Existing anchor BEFORE which:
```text


def fpm_preflight(version, has_pools):
```

Existing content to replace/remove (not copied):
```text
            'scope': 'Bounded journal sample. Admission attempts and proxy failures are separate events, not unique failed visitors. No events does not prove no overload; journal retention/rate limiting applies.'}
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
            'error': unavailable,
            'scope': (unavailable+' ' if unavailable else '')+'Bounded last-'+str(MAX_JOURNAL_ROWS)+' all-service journal sample within one hour. Admission attempts and proxy failures are separate events, not unique failed visitors. Empty counts do not prove no overload; unrelated traffic, journal retention/rate limiting and unavailable reads can omit events.'}
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
    return {'available': rc == 0, 'windowSeconds': 3600, 'maxJournalRows': MAX_JOURNAL_ROWS,
            'counts': dict(counts), 'minuteBuckets': buckets, 'recent': recent[-30:],
            'error': unavailable,
            'scope': (unavailable+' ' if unavailable else '')+'Bounded last-'+str(MAX_JOURNAL_ROWS)+' all-service journal sample within one hour. Admission attempts and proxy failures are separate events, not unique failed visitors. Empty counts do not prove no overload; unrelated traffic, journal retention/rate limiting and unavailable reads can omit events.'}


```

## uniselv-resman/assets/app.js

Installed paths: /usr/local/webuzo/plugins/uniselv-resman/assets/app.js

Replace the full file; never append duplicate functions/directives. New files run from first through final line.

### Block 1 — replace

Existing anchor AFTER which:
```text
            if (document.getElementById('storage-total-display')) document.getElementById('storage-total-display').innerText = st.total_formatted ?? 'Unavailable';
            if (document.getElementById('storage-limit-display')) document.getElementById('storage-limit-display').innerText = (s.max_storage_mib || 100) + ' MiB';
```

Existing anchor BEFORE which:
```text
            if (document.getElementById('storage-samples-count')) document.getElementById('storage-samples-count').innerText = st.samples_count || 0;
            if (document.getElementById('storage-snapshots-count')) document.getElementById('storage-snapshots-count').innerText = st.snapshots_count || 0;
```

Existing content to replace/remove (not copied):
```text
            if (document.getElementById('storage-bar-fill')) document.getElementById('storage-bar-fill').style.width = Math.min(100, st.used_percent || 0) + '%';
            if (document.getElementById('storage-used-pct')) document.getElementById('storage-used-pct').innerText = (st.used_percent || 0) + '%';
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
            const storagePct = Number(st.used_percent);
            const storageKnown = st.used_percent != null && Number.isFinite(storagePct) && storagePct >= 0;
            const storageWarning = storageKnown && storagePct >= 100;
            const storageFill = document.getElementById('storage-bar-fill');
            if (storageFill) {
                storageFill.style.width = (storageKnown ? Math.min(100, storagePct) : 0) + '%';
                storageFill.style.background = storageWarning ? '#f59e0b' : '';
            }
            const storageBadge = document.getElementById('storage-used-pct');
            if (storageBadge) {
                storageBadge.textContent = storageKnown ? storagePct + '%' : 'Unavailable';
                storageBadge.className = 'uniselv-badge ' + (storageWarning ? 'badge-warning' : 'badge-normal');
            }
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
            if (document.getElementById('storage-total-display')) document.getElementById('storage-total-display').innerText = st.total_formatted ?? 'Unavailable';
            if (document.getElementById('storage-limit-display')) document.getElementById('storage-limit-display').innerText = (s.max_storage_mib || 100) + ' MiB';
            const storagePct = Number(st.used_percent);
            const storageKnown = st.used_percent != null && Number.isFinite(storagePct) && storagePct >= 0;
            const storageWarning = storageKnown && storagePct >= 100;
            const storageFill = document.getElementById('storage-bar-fill');
            if (storageFill) {
                storageFill.style.width = (storageKnown ? Math.min(100, storagePct) : 0) + '%';
                storageFill.style.background = storageWarning ? '#f59e0b' : '';
            }
            const storageBadge = document.getElementById('storage-used-pct');
            if (storageBadge) {
                storageBadge.textContent = storageKnown ? storagePct + '%' : 'Unavailable';
                storageBadge.className = 'uniselv-badge ' + (storageWarning ? 'badge-warning' : 'badge-normal');
            }
            if (document.getElementById('storage-samples-count')) document.getElementById('storage-samples-count').innerText = st.samples_count || 0;
            if (document.getElementById('storage-snapshots-count')) document.getElementById('storage-snapshots-count').innerText = st.snapshots_count || 0;
```

## uniselv-resman/core/golden-shield.py

Installed paths: /usr/local/webuzo/plugins/uniselv-resman/core/golden-shield.py; ALSO /usr/local/uniselv-resman/core/golden-shield.py; ALSO /usr/local/sbin/golden-shield.py

Replace the full file; never append duplicate functions/directives. New files run from first through final line.

### Block 1 — insert

Existing anchor AFTER which:
```text
 managed(UNITS/(unit+'.d')/'90-golden-shield.conf','[Slice]\n'+'\n'.join(k+'='+v for k,v in settings.items())+'\n' if unit.endswith('.slice') else '[Service]\n'+'\n'.join(k+'='+v for k,v in settings.items())+'\n')
 command(['systemctl','set-property','--runtime',unit]+[k+'='+v for k,v in settings.items()])
```

Existing anchor BEFORE which:
```text
def apache_integration():
 # Preserve both native control entry points. The managed unit executes the saved original, avoiding recursion.
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
def apache_launcher(original):
 return '#!/bin/sh\n# Golden Shield shared Apache launcher\ncase "${1:-}" in\n start|stop|restart|reload) exec /bin/systemctl "$1" golden-apache.service ;;\n graceful) exec /bin/systemctl reload golden-apache.service ;;\n graceful-stop) exec /bin/systemctl stop golden-apache.service ;;\n status) if /bin/systemctl is-active --quiet golden-apache.service; then echo "httpd is running"; else echo "httpd is stopped"; exit 1; fi ;;\n *) exec '+shlex.quote(str(original))+' "$@" ;;\nesac\n'

def apache_service_unit():
 # Track the foreground master directly; native boot cleanup may remove a PID file.
 # Type=simple remains compatible with older supported systemd implementations.
 return '[Unit]\nDescription=Golden Shield shared hosting Apache\nWants=httpd.service\nAfter=network.target\n[Service]\nType=simple\nSlice=golden.slice\nExecStartPre=/usr/local/apps/apache2/bin/httpd -t\nExecStart=/bin/sh -c \'if [ -f /usr/local/apps/apache2/bin/envvars ]; then . /usr/local/apps/apache2/bin/envvars; fi; ulimit -S -n "$$(ulimit -H -n)"; exec /usr/local/apps/apache2/bin/httpd -DFOREGROUND\'\nExecReload=/usr/local/apps/apache2/bin/httpd -t\nExecReload=/bin/kill -USR1 $MAINPID\nKillSignal=SIGWINCH\nKillMode=mixed\nTimeoutStartSec=30\nTimeoutStopSec=30\nRestart=on-failure\nRestartSec=2\n[Install]\nWantedBy=multi-user.target\n'

```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
 managed(UNITS/(unit+'.d')/'90-golden-shield.conf','[Slice]\n'+'\n'.join(k+'='+v for k,v in settings.items())+'\n' if unit.endswith('.slice') else '[Service]\n'+'\n'.join(k+'='+v for k,v in settings.items())+'\n')
 command(['systemctl','set-property','--runtime',unit]+[k+'='+v for k,v in settings.items()])
def apache_launcher(original):
 return '#!/bin/sh\n# Golden Shield shared Apache launcher\ncase "${1:-}" in\n start|stop|restart|reload) exec /bin/systemctl "$1" golden-apache.service ;;\n graceful) exec /bin/systemctl reload golden-apache.service ;;\n graceful-stop) exec /bin/systemctl stop golden-apache.service ;;\n status) if /bin/systemctl is-active --quiet golden-apache.service; then echo "httpd is running"; else echo "httpd is stopped"; exit 1; fi ;;\n *) exec '+shlex.quote(str(original))+' "$@" ;;\nesac\n'

def apache_service_unit():
 # Track the foreground master directly; native boot cleanup may remove a PID file.
 # Type=simple remains compatible with older supported systemd implementations.
 return '[Unit]\nDescription=Golden Shield shared hosting Apache\nWants=httpd.service\nAfter=network.target\n[Service]\nType=simple\nSlice=golden.slice\nExecStartPre=/usr/local/apps/apache2/bin/httpd -t\nExecStart=/bin/sh -c \'if [ -f /usr/local/apps/apache2/bin/envvars ]; then . /usr/local/apps/apache2/bin/envvars; fi; ulimit -S -n "$$(ulimit -H -n)"; exec /usr/local/apps/apache2/bin/httpd -DFOREGROUND\'\nExecReload=/usr/local/apps/apache2/bin/httpd -t\nExecReload=/bin/kill -USR1 $MAINPID\nKillSignal=SIGWINCH\nKillMode=mixed\nTimeoutStartSec=30\nTimeoutStopSec=30\nRestart=on-failure\nRestartSec=2\n[Install]\nWantedBy=multi-user.target\n'

def apache_integration():
 # Preserve both native control entry points. The managed unit tracks the foreground binary; other commands use the saved original.
```

### Block 2 — replace

Existing anchor AFTER which:
```text
 command(['systemctl','set-property','--runtime',unit]+[k+'='+v for k,v in settings.items()])
def apache_integration():
```

Existing anchor BEFORE which:
```text
 if INIT.is_symlink() and INIT.resolve()!=APACHE.resolve():raise RuntimeError('Unsupported Apache init symlink target.')
 original=STATE/'apachectl.original'
```

Existing content to replace/remove (not copied):
```text
 # Preserve both native control entry points. The managed unit executes the saved original, avoiding recursion.
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
 # Preserve both native control entry points. The managed unit tracks the foreground binary; other commands use the saved original.
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text

def apache_integration():
 # Preserve both native control entry points. The managed unit tracks the foreground binary; other commands use the saved original.
 if INIT.is_symlink() and INIT.resolve()!=APACHE.resolve():raise RuntimeError('Unsupported Apache init symlink target.')
 original=STATE/'apachectl.original'
```

### Block 3 — replace

Existing anchor AFTER which:
```text
 original=STATE/'apachectl.original'
 atomic(original,APACHE.read_text(),0o755)
```

Existing anchor BEFORE which:
```text
 command([str(APACHE),'configtest'])
 pidfile=pathlib.Path('/usr/local/apps/apache2/logs/httpd.pid')
```

Existing content to replace/remove (not copied):
```text
 wrapper='#!/bin/sh\n# Golden Shield shared Apache launcher\ncase "${1:-}" in\n start|stop|restart|reload) exec /bin/systemctl "$1" golden-apache.service ;;\n graceful) exec /bin/systemctl reload golden-apache.service ;;\n graceful-stop) exec /bin/systemctl stop golden-apache.service ;;\n *) exec '+shlex.quote(str(original))+' "$@" ;;\nesac\n'
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
 wrapper=apache_launcher(original)
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
 original=STATE/'apachectl.original'
 atomic(original,APACHE.read_text(),0o755)
 wrapper=apache_launcher(original)
 command([str(APACHE),'configtest'])
 pidfile=pathlib.Path('/usr/local/apps/apache2/logs/httpd.pid')
```

### Block 4 — replace

Existing anchor AFTER which:
```text
  if time.monotonic()>deadline:raise RuntimeError('Old Apache master has not stopped; review before retrying.')
  time.sleep(.2)
```

Existing anchor BEFORE which:
```text
 managed(UNITS/'golden-apache.service',unit);managed(APACHE,wrapper,0o755)
 if not INIT.is_symlink():managed(INIT,wrapper,0o755)
```

Existing content to replace/remove (not copied):
```text
 unit='[Unit]\nDescription=Golden Shield shared hosting Apache\nAfter=network.target\n[Service]\nType=forking\nSlice=golden.slice\nPIDFile=/usr/local/apps/apache2/logs/httpd.pid\nExecStart='+str(original)+' start\nExecStop='+str(original)+' graceful-stop\nExecReload='+str(original)+' graceful\nTimeoutStopSec=30\n[Install]\nWantedBy=multi-user.target\n'
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
 unit=apache_service_unit()
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
  if time.monotonic()>deadline:raise RuntimeError('Old Apache master has not stopped; review before retrying.')
  time.sleep(.2)
 unit=apache_service_unit()
 managed(UNITS/'golden-apache.service',unit);managed(APACHE,wrapper,0o755)
 if not INIT.is_symlink():managed(INIT,wrapper,0o755)
```

### Block 5 — insert

Existing anchor AFTER which:
```text
 command(['systemctl','daemon-reload']);command(['systemctl','enable','--now','golden-apache.service'])
def repair_native_ownership():
```

Existing anchor BEFORE which:
```text
 # Do not let SysV PID guessing adopt the managed Apache master twice.
 bridge='[Unit]\nDescription=Webuzo Apache control bridge to Golden Shield\nWants=golden-apache.service\nAfter=golden-apache.service\n[Service]\nType=oneshot\nRemainAfterExit=yes\nExecStart=/bin/systemctl start golden-apache.service\nExecStop=/bin/systemctl stop golden-apache.service\nExecReload=/bin/systemctl reload golden-apache.service\n[Install]\nWantedBy=multi-user.target\n'
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
 apache_unit=UNITS/'golden-apache.service';desired=apache_service_unit()
 changed=apache_unit.read_text()!=desired
 command(['/usr/local/apps/apache2/bin/httpd','-t'])
 managed(apache_unit,desired,0o644)
 wrapper=apache_launcher(STATE/'apachectl.original');managed(APACHE,wrapper,0o755)
 if not INIT.is_symlink():managed(INIT,wrapper,0o755)
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
 command(['systemctl','daemon-reload']);command(['systemctl','enable','--now','golden-apache.service'])
def repair_native_ownership():
 apache_unit=UNITS/'golden-apache.service';desired=apache_service_unit()
 changed=apache_unit.read_text()!=desired
 command(['/usr/local/apps/apache2/bin/httpd','-t'])
 managed(apache_unit,desired,0o644)
 wrapper=apache_launcher(STATE/'apachectl.original');managed(APACHE,wrapper,0o755)
 if not INIT.is_symlink():managed(INIT,wrapper,0o755)
 # Do not let SysV PID guessing adopt the managed Apache master twice.
 bridge='[Unit]\nDescription=Webuzo Apache control bridge to Golden Shield\nWants=golden-apache.service\nAfter=golden-apache.service\n[Service]\nType=oneshot\nRemainAfterExit=yes\nExecStart=/bin/systemctl start golden-apache.service\nExecStop=/bin/systemctl stop golden-apache.service\nExecReload=/bin/systemctl reload golden-apache.service\n[Install]\nWantedBy=multi-user.target\n'
```

### Block 6 — remove

Existing anchor AFTER which:
```text
 managed(UNITS/'httpd.service',bridge,0o644)
 managed(UNITS/'webuzo-onboot.service.d'/'60-golden-ownership.conf','[Service]\nType=oneshot\nRemainAfterExit=yes\n',0o644)
```

Existing anchor BEFORE which:
```text
 command(['systemctl','daemon-reload'])
 command(['systemctl','reset-failed','httpd.service','webuzo-onboot.service'],False)
```

Existing content to replace/remove (not copied):
```text
 apache_unit=UNITS/'golden-apache.service'
 apache_text=apache_unit.read_text()
 if 'Wants=httpd.service\n' not in apache_text:
  managed(apache_unit,apache_text.replace('[Unit]\n','[Unit]\nWants=httpd.service\n',1))
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text

```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
 managed(UNITS/'httpd.service',bridge,0o644)
 managed(UNITS/'webuzo-onboot.service.d'/'60-golden-ownership.conf','[Service]\nType=oneshot\nRemainAfterExit=yes\n',0o644)
 command(['systemctl','daemon-reload'])
 if changed:command(['systemctl','restart','golden-apache.service'])
```

### Block 7 — insert

Existing anchor AFTER which:
```text
  managed(apache_unit,apache_text.replace('[Unit]\n','[Unit]\nWants=httpd.service\n',1))
 command(['systemctl','daemon-reload'])
```

Existing anchor BEFORE which:
```text
 command(['systemctl','reset-failed','httpd.service','webuzo-onboot.service'],False)
 command(['systemctl','start','httpd.service'])
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
 if changed:command(['systemctl','restart','golden-apache.service'])
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
 managed(UNITS/'webuzo-onboot.service.d'/'60-golden-ownership.conf','[Service]\nType=oneshot\nRemainAfterExit=yes\n',0o644)
 command(['systemctl','daemon-reload'])
 if changed:command(['systemctl','restart','golden-apache.service'])
 command(['systemctl','reset-failed','httpd.service','webuzo-onboot.service'],False)
 command(['systemctl','start','httpd.service'])
```

## uniselv-resman/core/protection-lifecycle.py

Installed paths: /usr/local/webuzo/plugins/uniselv-resman/core/protection-lifecycle.py; ALSO /usr/local/uniselv-resman/core/protection-lifecycle.py

Replace the full file; never append duplicate functions/directives. New files run from first through final line.

### Block 1 — replace

Existing anchor AFTER which:
```text
#!/usr/bin/python3
"""Checked installation/removal of plugin-owned protection dependencies."""
```

Existing anchor BEFORE which:
```text
sys.path.insert(0, '/usr/local/uniselv-resman/agent')
ROOT = pathlib.Path('/var/lib/uniselv-resource-manager')
```

Existing content to replace/remove (not copied):
```text
import json, os, pathlib, subprocess, sys, hashlib, time, re, math
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
import json, os, pathlib, subprocess, sys, hashlib, time, re, math, importlib.util
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
#!/usr/bin/python3
"""Checked installation/removal of plugin-owned protection dependencies."""
import json, os, pathlib, subprocess, sys, hashlib, time, re, math, importlib.util
sys.path.insert(0, '/usr/local/uniselv-resman/agent')
ROOT = pathlib.Path('/var/lib/uniselv-resource-manager')
```

### Block 2 — replace

Existing anchor AFTER which:
```text
    return {'accountRuntimeCaps':True,'maxActivePools':min(64,php_budget//minimum),'hostReserveMiB':reserve,
        'poolBudgetMiB':pool_cost,'phpBudgetMiB':php_budget,'workerRssMiB':max(rss_values),
```

Existing anchor BEFORE which:
```text


def reviewed_admission_policy(hw):
```

Existing content to replace/remove (not copied):
```text
        'opcacheMiB':max(cache_values),'idleSeconds':20,'requestTimeoutSeconds':max(timeouts or [120])}
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
        'opcacheMiB':max(cache_values),'idleSeconds':20,'requestTimeoutSeconds':max(timeouts or [120]),
        'warmIdleSeconds':max(60,min(900,(php_budget//(48+max(cache_values)))*60))}
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
    return {'accountRuntimeCaps':True,'maxActivePools':min(64,php_budget//minimum),'hostReserveMiB':reserve,
        'poolBudgetMiB':pool_cost,'phpBudgetMiB':php_budget,'workerRssMiB':max(rss_values),
        'opcacheMiB':max(cache_values),'idleSeconds':20,'requestTimeoutSeconds':max(timeouts or [120]),
        'warmIdleSeconds':max(60,min(900,(php_budget//(48+max(cache_values)))*60))}


```

### Block 3 — replace

Existing anchor AFTER which:
```text
    if path.is_symlink() or stat.st_uid!=0 or stat.st_mode & 0o022:
        raise RuntimeError('Generator profile must be a root-owned, non-writable regular file')
```

Existing anchor BEFORE which:
```text
    if config.get('validationErrors'):
        raise RuntimeError('Generator export contains validation errors')
```

Existing content to replace/remove (not copied):
```text
    data=json.loads(path.read_text());config=data['configuration'];hardware=config['globalInputs']['hardware']
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
    spec=importlib.util.spec_from_file_location('resman_install_profile',pathlib.Path(__file__).with_name('configuration-audit.py'))
    normalizer=importlib.util.module_from_spec(spec);spec.loader.exec_module(normalizer)
    config=normalizer.normalize_profile(json.loads(path.read_text()))['configuration'];hardware=config['globalInputs']['hardware']
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
    if path.is_symlink() or stat.st_uid!=0 or stat.st_mode & 0o022:
        raise RuntimeError('Generator profile must be a root-owned, non-writable regular file')
    spec=importlib.util.spec_from_file_location('resman_install_profile',pathlib.Path(__file__).with_name('configuration-audit.py'))
    normalizer=importlib.util.module_from_spec(spec);spec.loader.exec_module(normalizer)
    config=normalizer.normalize_profile(json.loads(path.read_text()))['configuration'];hardware=config['globalInputs']['hardware']
    if config.get('validationErrors'):
        raise RuntimeError('Generator export contains validation errors')
```

## uniselv-resman/core/webuzo-isolation.py

Installed paths: /usr/local/webuzo/plugins/uniselv-resman/core/webuzo-isolation.py; ALSO /usr/local/uniselv-resman/core/webuzo-isolation.py; ALSO /usr/local/sbin/webuzo-isolation.py

Replace the full file; never append duplicate functions/directives. New files run from first through final line.

### Block 1 — replace

Existing anchor AFTER which:
```text
    for unit in lifecycle_units(version):execute(['systemctl','reset-failed',unit],False)
    for unit,state in journal['units'].items():
```

Existing anchor BEFORE which:
```text
    for unit,state in journal['units'].items():
        if state['active']:execute(['systemctl','start',unit],timeout=90)
```

Existing content to replace/remove (not copied):
```text
        if state['enabled']=='enabled':execute(['systemctl','enable',unit])
        elif state['enabled']=='disabled':execute(['systemctl','disable',unit])
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
        if state['enabled'] in ('enabled','disabled'):
            # Restored owned symlinks already express enablement. Re-running enable
            # unnecessarily invokes Webuzo's SysV shim, which can lack runlevels.
            actual=execute(['systemctl','is-enabled',unit],False).stdout.strip()
            if actual!=state['enabled']:
                execute(['systemctl','enable' if state['enabled']=='enabled' else 'disable',unit])
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
    for unit in lifecycle_units(version):execute(['systemctl','reset-failed',unit],False)
    for unit,state in journal['units'].items():
        if state['enabled'] in ('enabled','disabled'):
            # Restored owned symlinks already express enablement. Re-running enable
            # unnecessarily invokes Webuzo's SysV shim, which can lack runlevels.
            actual=execute(['systemctl','is-enabled',unit],False).stdout.strip()
            if actual!=state['enabled']:
                execute(['systemctl','enable' if state['enabled']=='enabled' else 'disable',unit])
    for unit,state in journal['units'].items():
        if state['active']:execute(['systemctl','start',unit],timeout=90)
```

### Block 2 — insert

Existing anchor AFTER which:
```text
                reserved+=int(json.loads(lease.read_text())['costMiB'])
            if reserved>budget:raise RuntimeError('Wait for PHP leases to quiesce before adding version overhead')
```

Existing anchor BEFORE which:
```text
            current['phpBudgetMiB']=budget
            atomic(BASE/'policy.json',json.dumps(current,indent=2))
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
            automatic_warm=current.get('warmIdleSeconds',warm_idle_seconds(current))==warm_idle_seconds(current)
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                reserved+=int(json.loads(lease.read_text())['costMiB'])
            if reserved>budget:raise RuntimeError('Wait for PHP leases to quiesce before adding version overhead')
            automatic_warm=current.get('warmIdleSeconds',warm_idle_seconds(current))==warm_idle_seconds(current)
            current['phpBudgetMiB']=budget
            if automatic_warm:current['warmIdleSeconds']=warm_idle_seconds(current)
```

### Block 3 — insert

Existing anchor AFTER which:
```text
            if reserved>budget:raise RuntimeError('Wait for PHP leases to quiesce before adding version overhead')
            current['phpBudgetMiB']=budget
```

Existing anchor BEFORE which:
```text
            atomic(BASE/'policy.json',json.dumps(current,indent=2))
    base['appliedBudgetMiB']=budget
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
            if automatic_warm:current['warmIdleSeconds']=warm_idle_seconds(current)
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
            automatic_warm=current.get('warmIdleSeconds',warm_idle_seconds(current))==warm_idle_seconds(current)
            current['phpBudgetMiB']=budget
            if automatic_warm:current['warmIdleSeconds']=warm_idle_seconds(current)
            atomic(BASE/'policy.json',json.dumps(current,indent=2))
    base['appliedBudgetMiB']=budget
```

### Block 4 — insert

Existing anchor AFTER which:
```text

def uninstall():
```

Existing anchor BEFORE which:
```text
    data=json.loads((STATE/'installed.json').read_text())
    for version in data['versions']:execute(['systemctl','disable','--now','wpiso-manager-'+version+'.service'],False,timeout=90)
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
    if pathlib.Path('/var/lib/golden-shield/installed.json').exists():
        raise RuntimeError('Remove Golden Shield through the reviewed dependency workflow before PHP isolation.')
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text

def uninstall():
    if pathlib.Path('/var/lib/golden-shield/installed.json').exists():
        raise RuntimeError('Remove Golden Shield through the reviewed dependency workflow before PHP isolation.')
    data=json.loads((STATE/'installed.json').read_text())
    versions=data.get('versions')
```

### Block 5 — insert

Existing anchor AFTER which:
```text
def uninstall():
    data=json.loads((STATE/'installed.json').read_text())
```

Existing anchor BEFORE which:
```text
    for version in data['versions']:execute(['systemctl','disable','--now','wpiso-manager-'+version+'.service'],False,timeout=90)
    for version in data['versions']:
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
    versions=data.get('versions')
    if not isinstance(versions,list) or any(not isinstance(v,str) or not re.fullmatch(r'php\d{2,3}',v) for v in versions):
        raise ValueError('Invalid managed PHP registry; no services changed')
    # Validate the entire restore set before stopping the first coordinator.
    for version in versions:
        ctl=paths(version)/'bin/fpmctl';original=STATE/'original-launchers'/version
        if ctl.is_symlink() or original.is_symlink() or not ctl.is_file() or not original.is_file():
            raise RuntimeError('Unsafe or missing launcher recovery files: '+version)
        if ctl.read_text()!=wrapper(version) and ctl.read_bytes()!=original.read_bytes():
            raise RuntimeError('Launcher changed: manually review saved original before restoring '+version)
        native=UNITS/('php-fpm'+version[3:]+'.service')
        if native.is_symlink() or (native.exists() and native.read_text()!=bridge(version)):
            raise RuntimeError('Native service bridge changed; review before removal: '+version)
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
        raise RuntimeError('Remove Golden Shield through the reviewed dependency workflow before PHP isolation.')
    data=json.loads((STATE/'installed.json').read_text())
    versions=data.get('versions')
    if not isinstance(versions,list) or any(not isinstance(v,str) or not re.fullmatch(r'php\d{2,3}',v) for v in versions):
        raise ValueError('Invalid managed PHP registry; no services changed')
    # Validate the entire restore set before stopping the first coordinator.
    for version in versions:
        ctl=paths(version)/'bin/fpmctl';original=STATE/'original-launchers'/version
        if ctl.is_symlink() or original.is_symlink() or not ctl.is_file() or not original.is_file():
            raise RuntimeError('Unsafe or missing launcher recovery files: '+version)
        if ctl.read_text()!=wrapper(version) and ctl.read_bytes()!=original.read_bytes():
            raise RuntimeError('Launcher changed: manually review saved original before restoring '+version)
        native=UNITS/('php-fpm'+version[3:]+'.service')
        if native.is_symlink() or (native.exists() and native.read_text()!=bridge(version)):
            raise RuntimeError('Native service bridge changed; review before removal: '+version)
    for version in data['versions']:execute(['systemctl','disable','--now','wpiso-manager-'+version+'.service'],False,timeout=90)
    for version in data['versions']:
```

## uniselv-resman/info.json

Installed paths: /usr/local/webuzo/plugins/uniselv-resman/info.json

Replace the full file; never append duplicate functions/directives. New files run from first through final line.

### Block 1 — replace

Existing anchor AFTER which:
```text
  "name": "UNISELV Resource Manager",
  "slug": "uniselv-resman",
```

Existing anchor BEFORE which:
```text
  "author": "<a href=\"https://refat.ovh\" target=\"_blank\">Refat Rahman</a>",
  "developer": {
```

Existing content to replace/remove (not copied):
```text
  "version": "1.1.26",
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
  "version": "1.1.27",
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
  "name": "UNISELV Resource Manager",
  "slug": "uniselv-resman",
  "version": "1.1.27",
  "author": "<a href=\"https://refat.ovh\" target=\"_blank\">Refat Rahman</a>",
  "developer": {
```

## uniselv-resman/uniselv-resman.php

Installed paths: /usr/local/webuzo/plugins/uniselv-resman/uniselv-resman.php

Replace the full file; never append duplicate functions/directives. New files run from first through final line.

### Block 1 — replace

Existing anchor AFTER which:
```text
/*
Plugin Name: UNISELV Resource Manager
```

Existing anchor BEFORE which:
```text
Description: Enterprise Resource Management, Cgroups v2 Isolation, Real-Time Monitoring & Telemetry for Webuzo.
Author: Refat Rahman
```

Existing content to replace/remove (not copied):
```text
Version: 1.1.26
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
Version: 1.1.27
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
/*
Plugin Name: UNISELV Resource Manager
Version: 1.1.27
Description: Enterprise Resource Management, Cgroups v2 Isolation, Real-Time Monitoring & Telemetry for Webuzo.
Author: Refat Rahman
```

### Block 2 — replace

Existing anchor AFTER which:
```text
    if (rtrim($brand_docs, '/') === 'https://docs.uniselv.com') $brand_docs = ''; // Historical placeholder; use bundled local Help.

    $panel_url = !empty($globals['panel_url']) ? rtrim($globals['panel_url'], '/') : '';
    $i18n_dict = uniselv_get_i18n_dict();

```

Existing anchor BEFORE which:
```text
    echo '<style>:root { --uniselv-primary: ' . $brand_color . '; --primary-color: ' . $brand_color . '; }</style>';
    echo '<script>
window.UNISELV_LOCALE = ' . json_encode($locale) . ';
window.UNISELV_TRANSLATIONS = ' . json_encode($i18n_dict[$locale] ?? $i18n_dict['en']) . ';
</script>';
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '-1.1.26r2' . '"></script>';

    echo '<div class="uniselv-container">';
    
```

Existing content to replace/remove (not copied):
```text
    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '-1.1.26r2' . '">';
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '-1.1.27r3' . '">';
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
    $i18n_dict = uniselv_get_i18n_dict();

    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '-1.1.27r3' . '">';
    echo '<style>:root { --uniselv-primary: ' . $brand_color . '; --primary-color: ' . $brand_color . '; }</style>';
    echo '<script>
```

### Block 3 — replace

Existing anchor AFTER which:
```text
    if (rtrim($brand_docs, '/') === 'https://docs.uniselv.com') $brand_docs = ''; // Historical placeholder; use bundled local Help.

    $panel_url = !empty($globals['panel_url']) ? rtrim($globals['panel_url'], '/') : '';
    $i18n_dict = uniselv_get_i18n_dict();

    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '-1.1.26r2' . '">';
    echo '<style>:root { --uniselv-primary: ' . $brand_color . '; --primary-color: ' . $brand_color . '; }</style>';
    echo '<script>
window.UNISELV_LOCALE = ' . json_encode($locale) . ';
window.UNISELV_TRANSLATIONS = ' . json_encode($i18n_dict[$locale] ?? $i18n_dict['en']) . ';
</script>';
```

Existing anchor BEFORE which:
```text

    echo '<div class="uniselv-container">';
    
```

Existing content to replace/remove (not copied):
```text
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '-1.1.26r2' . '"></script>';
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '-1.1.27r3' . '"></script>';
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
window.UNISELV_TRANSLATIONS = ' . json_encode($i18n_dict[$locale] ?? $i18n_dict['en']) . ';
</script>';
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '-1.1.27r3' . '"></script>';

    echo '<div class="uniselv-container">';
```

### Block 4 — replace

Existing anchor AFTER which:
```text
                    </div>
                    <div class="uniselv-storage-bar-bg">
```

Existing anchor BEFORE which:
```text
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-top: 14px; font-size: 0.82rem; color: #475569;">
```

Existing content to replace/remove (not copied):
```text
                        <div id="storage-bar-fill" class="uniselv-storage-bar-fill" style="width: 1%;"></div>
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                        <div id="storage-bar-fill" class="uniselv-storage-bar-fill" style="width: 0%;"></div>
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                    </div>
                    <div class="uniselv-storage-bar-bg">
                        <div id="storage-bar-fill" class="uniselv-storage-bar-fill" style="width: 0%;"></div>
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-top: 14px; font-size: 0.82rem; color: #475569;">
```

### Block 5 — insert

Existing anchor AFTER which:
```text
                    <small>Page-load audit. Usage combines disjoint native and managed account groups. A DRIFT result requires investigation; it is not a healthy isolation certificate.</small>
                    <div>' . htmlspecialchars(implode(', ', $health['cgroup_integrity']['drift_accounts'] ?? [])) . '</div>
```

Existing anchor BEFORE which:
```text
                </div>

                <div style="display: flex; gap: 14px; align-items: center; flex-wrap: wrap; margin-top: 20px;">
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                    <div style="margin-top:8px;"><strong>Temporary boost recovery: ' . htmlspecialchars($health['override_recovery']['status'] ?? 'UNAVAILABLE') . '</strong> · Pending: ' . htmlspecialchars(strval($health['override_recovery']['pending'] ?? 'Unavailable')) . ' · Failed restorations: ' . htmlspecialchars(strval($health['override_recovery']['failed'] ?? 'Unavailable')) . '</div>
                    <small>Failed restorations remain visible and retryable; inspect Audit Log before changing a conflicting account plan.</small>
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                    <small>Page-load audit. Usage combines disjoint native and managed account groups. A DRIFT result requires investigation; it is not a healthy isolation certificate.</small>
                    <div>' . htmlspecialchars(implode(', ', $health['cgroup_integrity']['drift_accounts'] ?? [])) . '</div>
                    <div style="margin-top:8px;"><strong>Temporary boost recovery: ' . htmlspecialchars($health['override_recovery']['status'] ?? 'UNAVAILABLE') . '</strong> · Pending: ' . htmlspecialchars(strval($health['override_recovery']['pending'] ?? 'Unavailable')) . ' · Failed restorations: ' . htmlspecialchars(strval($health['override_recovery']['failed'] ?? 'Unavailable')) . '</div>
                    <small>Failed restorations remain visible and retryable; inspect Audit Log before changing a conflicting account plan.</small>
                </div>

```

### Block 6 — replace

Existing anchor AFTER which:
```text
    $limits = isset($dash['limits']) ? $dash['limits'] : [];

    $panel_url = !empty($globals['panel_url']) ? rtrim($globals['panel_url'], '/') : '';
    $i18n_dict = uniselv_get_i18n_dict();

```

Existing anchor BEFORE which:
```text
    echo '<style>:root { --uniselv-primary: ' . $brand_color . '; --primary-color: ' . $brand_color . '; }</style>';
    echo '<script>
window.UNISELV_LOCALE = ' . json_encode($locale) . ';
window.UNISELV_TRANSLATIONS = ' . json_encode($i18n_dict[$locale] ?? $i18n_dict['en']) . ';
</script>';
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '-1.1.26r2' . '"></script>';

    echo '<div class="uniselv-container">';

    // Header
```

Existing content to replace/remove (not copied):
```text
    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '-1.1.26r2' . '">';
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '-1.1.27r3' . '">';
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
    $i18n_dict = uniselv_get_i18n_dict();

    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '-1.1.27r3' . '">';
    echo '<style>:root { --uniselv-primary: ' . $brand_color . '; --primary-color: ' . $brand_color . '; }</style>';
    echo '<script>
```

### Block 7 — replace

Existing anchor AFTER which:
```text
    $limits = isset($dash['limits']) ? $dash['limits'] : [];

    $panel_url = !empty($globals['panel_url']) ? rtrim($globals['panel_url'], '/') : '';
    $i18n_dict = uniselv_get_i18n_dict();

    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '-1.1.26r2' . '">';
    echo '<style>:root { --uniselv-primary: ' . $brand_color . '; --primary-color: ' . $brand_color . '; }</style>';
    echo '<script>
window.UNISELV_LOCALE = ' . json_encode($locale) . ';
window.UNISELV_TRANSLATIONS = ' . json_encode($i18n_dict[$locale] ?? $i18n_dict['en']) . ';
</script>';
```

Existing anchor BEFORE which:
```text

    echo '<div class="uniselv-container">';

    // Header
```

Existing content to replace/remove (not copied):
```text
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '-1.1.26r2' . '"></script>';
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '-1.1.27r3' . '"></script>';
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
window.UNISELV_TRANSLATIONS = ' . json_encode($i18n_dict[$locale] ?? $i18n_dict['en']) . ';
</script>';
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '-1.1.27r3' . '"></script>';

    echo '<div class="uniselv-container">';
```

## uniselv-resman/views/admin_help.php

Installed paths: /usr/local/webuzo/plugins/uniselv-resman/views/admin_help.php

Replace the full file; never append duplicate functions/directives. New files run from first through final line.

### Block 1 — replace

Existing anchor AFTER which:
```text
            <h4 class="uniselv-help-card-title">Runtime Operations, Exact Source Placement &amp; Validation Scope</h4>
            <div class="uniselv-help-card-desc">Release <?php echo $uniselvHelpEscape($uniselvHelpVersion); ?>. These technical guides describe already-applied changes; they are not additional post-install paste steps.</div>
```

Existing anchor BEFORE which:
```text
        </div>


        <!-- 1. QUICK START -->
```

Existing content to replace/remove (not copied):
```text
            <details><summary>Operations, expected profile and verification scope</summary><pre style="white-space:pre-wrap;overflow-wrap:anywhere"><?php echo htmlspecialchars(file_get_contents(__DIR__ . '/../docs/release-1.1.26.md'), ENT_QUOTES, 'UTF-8'); ?></pre></details>
            <details><summary>Exact source replacement and insertion guide</summary><pre style="white-space:pre-wrap;overflow-wrap:anywhere"><?php echo htmlspecialchars(file_get_contents(__DIR__ . '/../docs/source-changes-1.1.26.md'), ENT_QUOTES, 'UTF-8'); ?></pre></details>
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
            <details><summary>Operations, expected profile and verification scope</summary><pre style="white-space:pre-wrap;overflow-wrap:anywhere"><?php echo htmlspecialchars(file_get_contents(__DIR__ . '/../docs/release-1.1.27.md'), ENT_QUOTES, 'UTF-8'); ?></pre></details>
            <details><summary>Exact source replacement and insertion guide</summary><pre style="white-space:pre-wrap;overflow-wrap:anywhere"><?php echo htmlspecialchars(file_get_contents(__DIR__ . '/../docs/source-changes-1.1.27.md'), ENT_QUOTES, 'UTF-8'); ?></pre></details>
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
            <h4 class="uniselv-help-card-title">Runtime Operations, Exact Source Placement &amp; Validation Scope</h4>
            <div class="uniselv-help-card-desc">Release <?php echo $uniselvHelpEscape($uniselvHelpVersion); ?>. These technical guides describe already-applied changes; they are not additional post-install paste steps.</div>
            <details><summary>Operations, expected profile and verification scope</summary><pre style="white-space:pre-wrap;overflow-wrap:anywhere"><?php echo htmlspecialchars(file_get_contents(__DIR__ . '/../docs/release-1.1.27.md'), ENT_QUOTES, 'UTF-8'); ?></pre></details>
            <details><summary>Exact source replacement and insertion guide</summary><pre style="white-space:pre-wrap;overflow-wrap:anywhere"><?php echo htmlspecialchars(file_get_contents(__DIR__ . '/../docs/source-changes-1.1.27.md'), ENT_QUOTES, 'UTF-8'); ?></pre></details>
        </div>

```

### Block 2 — insert

Existing anchor AFTER which:
```text
                    <li>Review <em>System &amp; Agent Health &gt; Runtime Governance &amp; Configuration Evidence</em> for admission/queue reasons. Grant a suitable temporary boost only when account limits and aggregate headroom justify it; investigate slow application/database work separately.</li>
                </ol>
```

Existing anchor BEFORE which:
```text
                <strong>Scenario 2: Investigating Rogue Process Outside Boundary:</strong>
                <ol style="margin:6px 0 10px 20px; padding:0;">
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                <p><strong>Temporary boost recovery:</strong> Application, cancellation and expiry use verified plan transactions. An unresolved boost blocks overlapping boosts. A failed restore remains retryable and appears under <em>System &amp; Agent Health &gt; Temporary boost recovery</em> and <em>Audit Log</em>. UID reuse or a separately changed account plan requires administrator review; the previous boost does not overwrite that new identity or plan.</p>
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                    <li>Review <em>System &amp; Agent Health &gt; Runtime Governance &amp; Configuration Evidence</em> for admission/queue reasons. Grant a suitable temporary boost only when account limits and aggregate headroom justify it; investigate slow application/database work separately.</li>
                </ol>
                <p><strong>Temporary boost recovery:</strong> Application, cancellation and expiry use verified plan transactions. An unresolved boost blocks overlapping boosts. A failed restore remains retryable and appears under <em>System &amp; Agent Health &gt; Temporary boost recovery</em> and <em>Audit Log</em>. UID reuse or a separately changed account plan requires administrator review; the previous boost does not overwrite that new identity or plan.</p>
                <strong>Scenario 2: Investigating Rogue Process Outside Boundary:</strong>
                <ol style="margin:6px 0 10px 20px; padding:0;">
```
