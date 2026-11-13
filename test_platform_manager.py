"""Unit & security tests for v1.2.0 Platform Operations & Managed Laravel Services."""
import json
import os
import pathlib
import sqlite3
import sys
import tempfile
import types
import unittest
from unittest import mock

if sys.platform == 'win32':
    for _mod_name in ('pwd', 'grp', 'fcntl'):
        if _mod_name not in sys.modules:
            _stub = types.ModuleType(_mod_name)
            _stub.getpwnam = lambda name: None
            _stub.getpwuid = lambda uid: None
            _stub.getgrnam = lambda name: None
            _stub.getgrgid = lambda gid: None
            _stub.flock = lambda *a, **k: None
            _stub.LOCK_EX = 2
            _stub.LOCK_NB = 4
            _stub.LOCK_UN = 8
            sys.modules[_mod_name] = _stub

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'agent'))

import ipc_server as ipc_mod
import openswoole_manager as om
import platform_manager as pm
import schema
from ipc_server import IpcRequestHandler


class _FakeCollector:
    def __init__(self, db_path, users=None, limits_by_uid=None):
        self.db_path = db_path
        self.users = users or {
            'starter1': {'uid': 1001, 'plan_name': 'starter', 'domain': 'starter.example.com', 'owner': 'root'},
            'pro1': {'uid': 1002, 'plan_name': 'pro', 'domain': 'pro.example.com', 'owner': 'res1'},
            'res1': {'uid': 1010, 'plan_name': 'pro', 'domain': 'res.example.com', 'reseller': True, 'owner': 'root'},
        }
        self.limits_by_uid = limits_by_uid or {
            1001: {'cpuquota': 100, 'mem_max': 512 * 1024 * 1024, 'maxtask': 64},
            1002: {'cpuquota': 400, 'mem_max': 2048 * 1024 * 1024, 'maxtask': 256},
            1010: {'cpuquota': 200, 'mem_max': 1024 * 1024 * 1024, 'maxtask': 128},
        }
        self.events = []

    def get_webuzo_users(self):
        return dict(self.users)

    def get_user_limits(self, uid, plan_name=''):
        return dict(self.limits_by_uid.get(uid, {'cpuquota': 100, 'mem_max': 512 * 1024 * 1024, 'maxtask': 64}))


class PlatformManagerTestCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.base = pathlib.Path(self._tmp.name)
        self.db_path = str(self.base / 'test_platform.db')
        schema.init_db(self.db_path)
        self.collector = _FakeCollector(self.db_path)

    def tearDown(self):
        self._tmp.cleanup()

    def test_os_preflight_status_structure(self):
        res = pm.get_os_preflight_status()
        self.assertTrue(res['success'])
        for key in ('distro', 'binaries', 'headers', 'missing_tools', 'missing_headers', 'ready_for_openswoole_build', 'install_command_preview'):
            self.assertIn(key, res)
        self.assertIn('openssl_dev', res['headers'])
        self.assertIn('libcurl_dev', res['headers'])

    def test_collision_free_port_allocations(self):
        with mock.patch.object(pm, 'APP_SOCKET_ROOT', self.base / 'run_apps'), \
             mock.patch.object(pm, '_is_port_open', return_value=False):
            a1 = pm.ensure_account_port_allocation(self.collector, self.db_path, 'starter1')
            a2 = pm.ensure_account_port_allocation(self.collector, self.db_path, 'pro1')
            a1_again = pm.ensure_account_port_allocation(self.collector, self.db_path, 'starter1')

        self.assertTrue(a1['success'])
        self.assertTrue(a2['success'])
        self.assertEqual(a1['ports'], a1_again['ports'])
        self.assertNotEqual(a1['base_port'], a2['base_port'])
        self.assertGreaterEqual(abs(a1['base_port'] - a2['base_port']), 10)
        s1 = set(a1['ports'].values())
        s2 = set(a2['ports'].values())
        self.assertEqual(len(s1 & s2), 0)
        self.assertIn('ProxyPass', a1['reverb_proxy_snippet'])

        # Auto-exported ports.json must exist and expose non-secret ports/prefixes
        pf = self.base / 'run_apps' / 'starter1' / 'ports.json'
        self.assertTrue(pf.is_file())
        pdata = json.loads(pf.read_text(encoding='utf-8'))
        self.assertEqual(pdata['reverb_port'], a1['ports']['reverb_port'])
        self.assertEqual(pdata['octane_port'], a1['ports']['octane_port'])
        self.assertEqual(pdata['horizon_metrics_port'], a1['ports']['horizon_metrics_port'])
        self.assertEqual(pdata['redis_prefix'], 'starter1:')
        self.assertEqual(pdata['horizon_prefix'], 'starter1:horizon:')

    def test_laravel_discovery_zero_secret_leak_and_traversal_block(self):
        home_dir = self.base / 'home_starter1'
        app_dir = home_dir / 'public_html'
        app_dir.mkdir(parents=True)
        (app_dir / 'artisan').write_text('#!/usr/bin/env php\n', encoding='utf-8')
        (app_dir / 'composer.json').write_text(json.dumps({
            'require': {
                'laravel/framework': '^11.0',
                'laravel/horizon': '^5.29',
                'laravel/reverb': '^1.4',
            }
        }), encoding='utf-8')
        (app_dir / '.env').write_text(
            'APP_KEY=base64:ULTRA_SECRET_DO_NOT_LEAK\n'
            'DB_PASSWORD=SUPER_SECRET_DB_PASS\n'
            'QUEUE_CONNECTION=redis\n'
            'CACHE_STORE=redis\n'
            'BROADCAST_CONNECTION=reverb\n',
            encoding='utf-8',
        )

        discovered = pm.discover_laravel_apps('starter1', home_override=str(home_dir))
        self.assertEqual(len(discovered), 1)
        item = discovered[0]
        self.assertTrue(item['declared_horizon'])
        self.assertTrue(item['declared_reverb'])
        self.assertEqual(item['env']['queue_connection'], 'redis')
        serialized = json.dumps(item)
        self.assertNotIn('ULTRA_SECRET_DO_NOT_LEAK', serialized)
        self.assertNotIn('SUPER_SECRET_DB_PASS', serialized)

        # Path traversal rejection
        self.assertIsNone(pm._safe_home_subpath('starter1', '/etc/passwd', home_override=str(home_dir)))
        self.assertIsNone(pm._safe_home_subpath('starter1', '../../etc/passwd', home_override=str(home_dir)))
        self.assertEqual(
            pm._safe_home_subpath('starter1', 'public_html', home_override=str(home_dir)),
            pathlib.Path(os.path.realpath(str(app_dir))),
        )

    def test_laravel_unit_render_and_worker_budget_caps(self):
        budget = pm.compute_laravel_service_budget(self.collector, 'starter1', self.db_path)
        self.assertEqual(budget['expected_slice'], 'golden-1001.slice')
        self.assertEqual(budget['max_queue_workers'], 1)
        self.assertTrue(budget['horizon_allowed'])

        pro_budget = pm.compute_laravel_service_budget(self.collector, 'pro1', self.db_path)
        self.assertEqual(pro_budget['max_queue_workers'], 4)

        exec_cmd = pm._build_laravel_exec_command('reverb', '/usr/local/apps/php84/bin/php', 'default', 1, 256, 20011)
        self.assertIn('reverb:start --host=127.0.0.1 --port=20011', exec_cmd)
        unit = pm._render_laravel_systemd_unit(
            'pro1', 'pro1', 1002, 'queue', 'queue-public-html',
            '/home/pro1/public_html', exec_cmd, '/home/pro1/.uniselv-logs/queue.log'
        )
        self.assertIn('User=pro1', unit)
        self.assertIn('Slice=golden-1002.slice', unit)
        self.assertIn('NoNewPrivileges=yes', unit)

        # Install & control flow via mocked filesystem/systemd
        home_pro = self.base / 'home_pro1'
        app_pro = home_pro / 'public_html'
        app_pro.mkdir(parents=True)
        (app_pro / 'artisan').write_text('#!/usr/bin/env php\n', encoding='utf-8')
        with mock.patch.object(pm, '_resolve_user_ids', return_value=(1002, 1002, str(home_pro))), \
             mock.patch.object(pm, '_query_systemd_unit', return_value={'unit_name': 'u', 'active_state': 'active', 'sub_state': 'running', 'main_pid': 4321, 'slice': 'golden-1002.slice', 'enabled': 'enabled'}), \
             mock.patch.object(pm, '_is_port_open', return_value=False), \
             mock.patch.object(pm, '_service_unit_path', side_effect=lambda uname: self.base / uname), \
             mock.patch.object(pm, 'APP_SOCKET_ROOT', self.base / 'run_apps'), \
             mock.patch.object(pm.subprocess, 'run', return_value=types.SimpleNamespace(returncode=0, stdout='', stderr='')), \
             mock.patch('os.chown', create=True):
            res = pm.save_and_install_laravel_service(self.collector, self.db_path, 'pro1', {
                'username': 'pro1',
                'service_type': 'queue',
                'app_path': str(app_pro),
                'php_branch': 'php84',
                'workers': '99',
                'queues': 'emails,default',
            })
        self.assertTrue(res['success'])
        conn = sqlite3.connect(self.db_path)
        row = conn.execute('SELECT workers, service_type, unit_name FROM managed_app_services WHERE username = ?', ('pro1',)).fetchone()
        conn.close()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], 4)  # Capped at pro1 budget max_queue_workers=4
        self.assertEqual(row[1], 'queue')

    def test_redis_acl_provision_test_and_revoke(self):
        calls = []
        kv_store = {}

        def fake_redis(args, auth_user='', auth_pass='', timeout=5.0, **kwargs):
            calls.append((args, auth_user))
            cmd = args[0] if args else ''
            if cmd == 'PING':
                return 0, 'PONG', ''
            if cmd == 'INFO':
                return 0, 'redis_version:8.2.2\n', ''
            if cmd == 'ACL' and len(args) >= 2 and args[1] == 'GETUSER':
                return 0, 'flags\non\nnopass', ''
            if cmd == 'ACL' and args[1] == 'DELUSER':
                return 0, '1', ''
            if cmd == 'ACL' and args[1] in ('SETUSER', 'SAVE'):
                return 0, 'OK', ''
            if cmd == 'ACL' and args[1] == 'DRYRUN':
                allowed = args[3] == 'SET' and args[4].startswith('starter1:')
                return (0, 'OK', '') if allowed else (1, '', 'User has no permissions to run this command')
            if cmd == 'SET' and args[1].startswith('starter1:'):
                kv_store[args[1]] = args[2]
                return 0, 'OK', ''
            if cmd == 'GET' and args[1].startswith('starter1:'):
                return 0, kv_store.get(args[1], ''), ''
            if cmd == 'DEL' and args[1].startswith('starter1:'):
                kv_store.pop(args[1], None)
                return 0, '1', ''
            if cmd == 'SET' and args[1].startswith('__other_tenant'):
                return 1, '', 'NOPERM this user has no permissions to access one of the keys'
            if cmd in ('CONFIG', 'FLUSHALL', 'FLUSHDB', 'SHUTDOWN'):
                return 1, '', f"NOPERM User u_starter1 has no permissions to run the '{cmd.lower()}' command"
            return 0, 'OK', ''

        conf_path = self.base / 'redis.conf'
        conf_path.write_text('port 6379\nbind 127.0.0.1\n', encoding='utf-8')
        with mock.patch.object(pm, '_find_redis_cli', return_value='/usr/bin/redis-cli'), \
             mock.patch.object(pm, '_find_redis_conf', return_value=conf_path), \
             mock.patch.object(pm, '_run_redis', side_effect=fake_redis):
            prov = pm.provision_redis_acl(self.db_path, 'starter1', actor='admin')
            self.assertTrue(prov['success'])
            self.assertEqual(prov['redis_user'], 'u_starter1')
            self.assertEqual(prov['key_prefix'], 'starter1:')
            self.assertIn((['ACL', 'SAVE'], ''), calls)

            test_res = pm.test_redis_acl_isolation(self.db_path, 'starter1')
            self.assertTrue(test_res['success'])
            self.assertTrue(test_res['all_passed'])
            self.assertEqual(len(test_res['steps']), 4)
            self.assertFalse(any(args[0] == 'FLUSHALL' for args, _ in calls))

            st_scoped = pm.get_redis_isolation_status(self.collector, self.db_path, scoped_user='starter1')
            st_admin = pm.get_redis_isolation_status(self.collector, self.db_path, scoped_user=None)
            self.assertNotIn('password', st_scoped['accounts'][0])
            self.assertNotIn('password', st_admin['accounts'][0])

            rev = pm.revoke_redis_acl(self.db_path, 'starter1', actor='admin')
            self.assertTrue(rev['success'])

    def test_heavy_binary_and_runtime_containment_enforcement(self):
        fake_procs = [
            {'pid': 2001, 'uid': 1001, 'username': 'starter1', 'kind': 'node', 'comm': 'node', 'cmdline': 'node server.js', 'rss_mib': 80.0, 'age_sec': 120, 'current_cgroup': 'user.slice', 'expected_slice': 'golden-1001.slice', 'contained': False},
            {'pid': 2002, 'uid': 1001, 'username': 'starter1', 'kind': 'heavy_binary', 'comm': 'chromium', 'cmdline': 'chromium --headless', 'rss_mib': 300.0, 'age_sec': 600, 'current_cgroup': 'golden-1001.slice', 'expected_slice': 'golden-1001.slice', 'contained': True},
        ]
        with mock.patch.object(pm, 'scan_tenant_runtimes_and_binaries', return_value={'success': True, 'processes': fake_procs}), \
             mock.patch.object(om, 'contain_process_in_account_slice', return_value=True) as contain_mock, \
             mock.patch.object(om, '_safe_stop_pid', return_value=True) as stop_mock:
            res = pm.enforce_platform_tick(self.collector, self.db_path)

        self.assertEqual(res['contained'], 1)
        self.assertEqual(res['terminated'], 1)
        contain_mock.assert_called_once_with(1001, 2001)
        stop_mock.assert_called_once_with(1001, 2002, 0)

    def test_log_tail_truncation_and_symlink_rejection(self):
        home_dir = self.base / 'home_s1'
        log_dir = home_dir / 'storage' / 'logs'
        log_dir.mkdir(parents=True)
        log_file = log_dir / 'laravel.log'
        log_file.write_text('\n'.join(f'line-{i}' for i in range(2500)) + '\n', encoding='utf-8')

        res = pm.truncate_app_log(self.db_path, 'starter1', 'starter1', 'storage/logs/laravel.log', keep_lines=100, is_admin=False, home_override=str(home_dir))
        self.assertTrue(res['success'])
        self.assertGreater(res['freed_bytes'], 1000)
        remaining = log_file.read_text(encoding='utf-8').splitlines()
        self.assertEqual(len(remaining), 100)
        self.assertEqual(remaining[0], 'line-2400')
        self.assertEqual(remaining[-1], 'line-2499')

        # Cross-tenant unauthorized truncation denied
        denied = pm.truncate_app_log(self.db_path, 'other_user', 'starter1', 'storage/logs/laravel.log', keep_lines=50, is_admin=False, home_override=str(home_dir))
        self.assertEqual(denied.get('status_code'), 403)

    def test_policy_export_strips_secrets_and_import_dryrun_apply(self):
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("INSERT OR REPLACE INTO package_mappings (billing_package, resource_plan, updated_at) VALUES ('starter_pkg', 'starter', 1)")
            conn.execute("INSERT OR REPLACE INTO openswoole_plan_policies (plan_name, allowed, max_workers_override, max_task_workers_override, updated_at, updated_by) VALUES ('starter', 1, 2, 1, 1, 'root')")
            conn.execute("INSERT OR REPLACE INTO redis_acl_accounts (username, redis_user, key_prefix, password_hash, password_plain_enc, enabled, updated_at) VALUES ('starter1', 'u_starter1', 'starter1:', 'h1', 'TOP_SECRET_REDIS_TOKEN_123', 1, 1)")
            conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('webhook_secret', 'local-webhook-secret')")
            conn.commit()
        finally:
            conn.close()

        exp = pm.export_policy_bundle(self.db_path)
        self.assertTrue(exp['success'])
        raw_json = json.dumps(exp['bundle'])
        self.assertNotIn('TOP_SECRET_REDIS_TOKEN_123', raw_json)
        self.assertNotIn('password_plain_enc', raw_json)
        self.assertNotIn('webhook_secret', exp['bundle']['settings'])

        # Modify bundle and test dry-run vs real apply
        bundle = exp['bundle']
        bundle['settings']['platform_log_threshold_mib'] = '500'
        bundle['settings']['webhook_secret'] = 'foreign-webhook-secret'
        dry = pm.import_policy_bundle(self.collector, self.db_path, 'root', bundle, dry_run=True)
        self.assertTrue(dry['success'])
        self.assertTrue(dry['dry_run'])
        self.assertEqual(pm.load_platform_settings(self.db_path)['platform_log_threshold_mib'], '250')

        applied = pm.import_policy_bundle(self.collector, self.db_path, 'root', bundle, dry_run=False)
        self.assertTrue(applied['success'])
        self.assertFalse(applied['dry_run'])
        self.assertEqual(pm.load_platform_settings(self.db_path)['platform_log_threshold_mib'], '500')
        conn = sqlite3.connect(self.db_path)
        try:
            self.assertEqual(conn.execute("SELECT value FROM settings WHERE key = 'webhook_secret'").fetchone(),
                             ('local-webhook-secret',))
        finally:
            conn.close()
        invalid = pm.import_policy_bundle(self.collector, self.db_path, 'root',
                                          {'schema_version': 1, 'package_mappings': ['invalid']}, dry_run=True)
        self.assertFalse(invalid['success'])

    def test_ipc_rbac_platform_guards(self):
        if sys.platform == 'win32':
            with mock.patch.object(ipc_mod.GoldenShieldManager, 'ensure_systemd_slice_persistence', return_value=None):
                handler = IpcRequestHandler(db_path=self.db_path, collector=self.collector)
        else:
            handler = IpcRequestHandler(db_path=self.db_path, collector=self.collector)

        # Server-wide admin actions must block both Enduser and Reseller
        for act in ('get_platform_status', 'get_platform_dep_status', 'save_platform_settings', 'platform_install_deps', 'platform_selftest_laravel', 'platform_redis_action', 'platform_export_policy', 'platform_import_policy'):
            r_eu = handler.handle_request({'action': act, 'auth': {'user': 'starter1', 'is_admin': False}, 'params': {}})
            self.assertIn('Forbidden', r_eu.get('error', ''), msg=f'Enduser should be forbidden from {act}')
            r_res = handler.handle_request({'action': act, 'auth': {'user': 'res1', 'is_admin': True}, 'params': {}})
            self.assertIn('Forbidden', r_res.get('error', ''), msg=f'Reseller should be forbidden from {act}')

        # Enduser cannot view or tamper with another account via get_enduser_platform_services
        with mock.patch.object(pm, 'list_laravel_services', return_value={'success': True, 'services': [], 'discovered_apps': []}), \
             mock.patch.object(pm, 'get_redis_isolation_status', return_value={'success': True, 'accounts': []}), \
             mock.patch.object(pm, 'ensure_account_port_allocation', return_value={'success': True, 'ports': {}}), \
             mock.patch.object(pm, 'scan_app_logs_and_inodes', return_value={'success': True, 'findings': []}), \
             mock.patch.object(pm, 'scan_tenant_runtimes_and_binaries', return_value={'success': True, 'processes': []}):
            r_self = handler.handle_request({'action': 'get_enduser_platform_services', 'auth': {'user': 'starter1', 'is_admin': False}, 'params': {'username': 'pro1'}})
        self.assertEqual(r_self.get('username'), 'starter1')  # Forced back to starter1!

        # Reseller cannot operate on unowned starter1
        r_unowned = handler.handle_request({'action': 'get_enduser_platform_services', 'auth': {'user': 'res1', 'is_admin': True}, 'params': {'username': 'starter1'}})
        self.assertIn('Forbidden', r_unowned.get('error', ''))

    def test_dep_installer_uses_systemd_run_and_fast_php_scan(self):
        seen_cmds = []

        class _InlineThread:
            def __init__(self, target=None, daemon=None):
                self._target = target
            def start(self):
                if self._target:
                    self._target()

        def fake_run(cmd, **kwargs):
            seen_cmds.append(list(cmd))
            return mock.Mock(returncode=0, stdout='ok', stderr='')

        with mock.patch.object(pm.os, 'name', 'posix'), \
             mock.patch.object(pm.shutil, 'which', side_effect=lambda b: '/usr/bin/systemd-run' if b == 'systemd-run' else None), \
             mock.patch.object(pm, '_detect_distro', return_value={'family': 'debian', 'pkg_manager': 'apt-get', 'id': 'ubuntu', 'pretty': 'Ubuntu 24.04'}), \
             mock.patch.object(pm, '_install_composer_verified', return_value=(True, 'Installed Composer')), \
             mock.patch.object(pm.subprocess, 'run', side_effect=fake_run), \
             mock.patch.object(pm.threading, 'Thread', _InlineThread):
            res = pm.start_install_build_dependencies(self.db_path, 'root', 'all')

        self.assertTrue(res['success'])
        self.assertEqual(len(seen_cmds), 2)
        for cmd in seen_cmds:
            self.assertEqual(cmd[0], 'systemd-run')
            self.assertIn('--wait', cmd)
            self.assertIn('--collect', cmd)
            self.assertIn('MemoryMax=1G', cmd)
            self.assertIn('APT::Update::Post-Invoke-Success=', cmd)
        job = pm._read_json_safe(pm.DEP_JOB_FILE, {})
        self.assertEqual(job.get('state'), 'completed')

        # list_laravel_services must NOT spawn openswoole discover_php_versions subprocesses
        import openswoole_manager as osw_mgr
        with mock.patch.object(osw_mgr, 'discover_php_versions', side_effect=AssertionError('must not scan php binaries via subprocess')), \
             mock.patch.object(pm, 'discover_laravel_apps', return_value=[]):
            svc_res = pm.list_laravel_services(self.collector, self.db_path)
        self.assertTrue(svc_res['success'])
        self.assertIn('php_branches', svc_res)
        self.assertIn('php84', svc_res['php_branches'])

        # _install_composer_verified must inject HOME & COMPOSER_HOME even when systemd unit lacks them
        captured_envs = []
        class _FakeResp:
            def __init__(self, payload: bytes):
                self._payload = payload
            def read(self):
                return self._payload
            def __enter__(self):
                return self
            def __exit__(self, *a):
                return False

        import hashlib as _hl
        import urllib.request as _ur
        installer_bytes = b'<?php echo "composer"; ?>'
        sig_bytes = _hl.sha384(installer_bytes).hexdigest().encode('utf-8')
        comp_dest = pathlib.Path(self._tmp.name) / 'composer_bin' / 'composer'

        def fake_urlopen(req, timeout=15):
            return _FakeResp(sig_bytes if 'installer.sig' in req.full_url else installer_bytes)

        def fake_comp_run(cmd, env=None, **kwargs):
            captured_envs.append(env or {})
            comp_dest.parent.mkdir(parents=True, exist_ok=True)
            comp_dest.write_text('#!/usr/bin/env php\n', encoding='utf-8')
            return mock.Mock(returncode=0, stdout='', stderr='')

        clean_env = {k: v for k, v in os.environ.items() if k not in ('HOME', 'COMPOSER_HOME')}
        with mock.patch.dict(pm.os.environ, clean_env, clear=True), \
             mock.patch.object(pm, 'SYSTEM_COMPOSER_BIN', comp_dest), \
             mock.patch.object(pm.shutil, 'which', return_value='/usr/bin/php'), \
             mock.patch.object(_ur, 'urlopen', side_effect=fake_urlopen), \
             mock.patch.object(pm.subprocess, 'run', side_effect=fake_comp_run):
            ok_c, msg_c = pm._install_composer_verified()
        self.assertTrue(ok_c, msg=msg_c)
        self.assertTrue(captured_envs and captured_envs[0].get('HOME'))
        self.assertTrue(captured_envs[0].get('COMPOSER_HOME'))

    def test_global_feature_toggles_plan_ram_gate_and_octane_port(self):
        # Include a <512 MiB plan account to test horizon/reverb RAM gating
        users = dict(self.collector.users)
        users['micro1'] = {'uid': 1003, 'plan_name': 'micro', 'domain': 'micro.example.com', 'owner': 'root'}
        limits = dict(self.collector.limits_by_uid)
        limits[1003] = {'cpuquota': 50, 'mem_max': 256 * 1024 * 1024, 'maxtask': 32}
        micro_col = _FakeCollector(self.db_path, users=users, limits_by_uid=limits)

        budget_micro = pm.compute_laravel_service_budget(micro_col, 'micro1', self.db_path)
        self.assertTrue(budget_micro['services_globally_enabled'])
        self.assertTrue(budget_micro['queue_allowed'])
        self.assertTrue(budget_micro['scheduler_allowed'])
        self.assertFalse(budget_micro['horizon_allowed'])
        self.assertFalse(budget_micro['reverb_allowed'])

        # 256 MiB account must be rejected when installing horizon or reverb even if globally enabled
        home_micro = self.base / 'home_micro1'
        app_micro = home_micro / 'public_html'
        app_micro.mkdir(parents=True)
        (app_micro / 'artisan').write_text('#!/usr/bin/env php\n', encoding='utf-8')
        denied_hor = pm.save_and_install_laravel_service(micro_col, self.db_path, 'micro1', {
            'username': 'micro1',
            'app_path': str(app_micro),
            'service_type': 'horizon',
            'php_branch': 'php84',
        })
        self.assertFalse(denied_hor['success'])
        self.assertIn('512 MiB', denied_hor.get('error', ''))

        if sys.platform == 'win32':
            with mock.patch.object(ipc_mod.GoldenShieldManager, 'ensure_systemd_slice_persistence', return_value=None):
                handler = IpcRequestHandler(db_path=self.db_path, collector=micro_col)
        else:
            handler = IpcRequestHandler(db_path=self.db_path, collector=micro_col)

        # Partial save_platform_settings must preserve unrelated existing settings
        r_save = handler.handle_request({
            'action': 'save_platform_settings',
            'auth': {'user': 'root', 'is_admin': True},
            'params': {
                'platform_laravel_services_enabled': '0',
                'platform_laravel_allowed_types': 'queue,scheduler',
                'platform_redis_acl_enabled': '0',
                'platform_log_watchdog_enabled': '0',
            },
        })
        self.assertTrue(r_save['success'], msg=r_save)
        saved = r_save['settings']
        self.assertEqual(saved['platform_laravel_services_enabled'], '0')
        self.assertEqual(saved['platform_laravel_allowed_types'], 'queue,scheduler')
        self.assertEqual(saved['platform_redis_acl_enabled'], '0')
        self.assertEqual(saved['platform_log_watchdog_enabled'], '0')
        self.assertEqual(saved['platform_log_threshold_mib'], '250')  # untouched default preserved

        # Globally disabled Managed Laravel Services blocks enduser queue install
        home_s1 = self.base / 'home_starter1_gate'
        app_s1 = home_s1 / 'public_html'
        app_s1.mkdir(parents=True)
        (app_s1 / 'artisan').write_text('#!/usr/bin/env php\n', encoding='utf-8')
        r_srv_off = pm.save_and_install_laravel_service(micro_col, self.db_path, 'starter1', {
            'username': 'starter1',
            'app_path': str(app_s1),
            'service_type': 'queue',
            'php_branch': 'php84',
        })
        self.assertFalse(r_srv_off['success'])
        self.assertIn('disabled', r_srv_off.get('error', '').lower())

        # Re-enable global services but keep only queue,scheduler in allowed types
        handler.handle_request({
            'action': 'save_platform_settings',
            'auth': {'user': 'root', 'is_admin': True},
            'params': {
                'platform_laravel_services_enabled': '1',
                'platform_laravel_allowed_types': 'queue,scheduler',
            },
        })
        r_type_off = pm.save_and_install_laravel_service(micro_col, self.db_path, 'starter1', {
            'username': 'starter1',
            'app_path': str(app_s1),
            'service_type': 'reverb',
            'php_branch': 'php84',
        })
        self.assertFalse(r_type_off['success'])
        self.assertIn('disabled', r_type_off.get('error', '').lower())

        # Enduser Redis ACL provision/test blocked when platform_redis_acl_enabled == '0'
        r_red_off = handler.handle_request({
            'action': 'enduser_redis_action',
            'auth': {'user': 'starter1', 'is_admin': False},
            'params': {'operation': 'provision'},
        })
        self.assertFalse(r_red_off.get('success', True))
        self.assertIn('disabled', r_red_off.get('error', '').lower())

        # Enduser Log Watchdog truncate blocked when platform_log_watchdog_enabled == '0'
        r_log_off = handler.handle_request({
            'action': 'truncate_app_log',
            'auth': {'user': 'starter1', 'is_admin': False},
            'params': {'log_path': str(app_s1 / 'storage' / 'logs' / 'laravel.log')},
        })
        self.assertFalse(r_log_off.get('success', True))
        self.assertIn('disabled', r_log_off.get('error', '').lower())

        # Enduser OpenSwoole injects assigned --port=<octane_port>
        with mock.patch.object(pm, 'APP_SOCKET_ROOT', self.base / 'run_apps_oct'), \
             mock.patch.object(pm, '_is_port_open', return_value=False), \
             mock.patch.object(om, 'get_enduser_status_payload', return_value={
                 'success': True,
                 'guidance': {'recommended_octane_command': 'php artisan octane:start --workers=2 --task-workers=1'},
             }):
            r_oct = handler.handle_request({
                'action': 'get_enduser_openswoole',
                'auth': {'user': 'starter1', 'is_admin': False},
                'params': {},
            })
        self.assertTrue(r_oct['success'])
        port_assigned = r_oct['guidance'].get('assigned_octane_port')
        self.assertIsInstance(port_assigned, int)
        self.assertIn(f'--port={port_assigned}', r_oct['guidance'].get('recommended_octane_command', ''))

    def test_smart_php_queue_discovery_redis_url_and_strict_service_test(self):
        home_dir = self.base / 'home_smart'
        app_dir = home_dir / 'clone.example.com'
        (app_dir / 'config').mkdir(parents=True)
        (app_dir / 'vendor').mkdir(parents=True)
        (app_dir / 'vendor' / 'autoload.php').write_text('<?php\n', encoding='utf-8')
        (app_dir / 'artisan').write_text('#!/usr/bin/env php\n', encoding='utf-8')
        (app_dir / 'composer.json').write_text(json.dumps({
            'require': {'php': '^8.2', 'laravel/framework': '^12.0', 'laravel/horizon': '^5.40'},
        }), encoding='utf-8')
        (app_dir / 'config' / 'horizon.php').write_text(
            "<?php return ['defaults' => ['s1' => ['queue' => ['webhook_responses']], 's2' => ['queue' => ['telegram', 'default']], 's3' => ['queue' => ['low_priority']]]];\n",
            encoding='utf-8',
        )

        apps = pm.discover_laravel_apps('starter1', home_override=str(home_dir), available_php=['php74', 'php81', 'php82', 'php84'])
        self.assertEqual(len(apps), 1)
        self.assertEqual(apps[0]['php_constraint'], '^8.2')
        self.assertEqual(apps[0]['recommended_php'], 'php84')
        self.assertEqual(apps[0]['recommended_queues'], 'webhook_responses,telegram,default,low_priority')
        self.assertFalse(apps[0]['env']['has_env'])

        # REDIS_URL snippet must expose url with username & secret for scoped enduser and mask for admin overview
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute(
                "INSERT OR REPLACE INTO redis_acl_accounts (username, redis_user, key_prefix, password_hash, password_plain_enc, enabled, updated_at) VALUES ('starter1', 'u_starter1', 'starter1:', 'h1', 'SecrEtUrl99', 1, 1)"
            )
            conn.commit()
        finally:
            conn.close()
        with mock.patch.object(pm, '_find_redis_cli', return_value=None):
            eu_red = pm.get_redis_isolation_status(self.collector, self.db_path, scoped_user='starter1')
            ad_red = pm.get_redis_isolation_status(self.collector, self.db_path, scoped_user=None)
        self.assertNotIn('env_snippet', eu_red['accounts'][0])
        self.assertNotIn('SecrEtUrl99', str(eu_red))
        self.assertNotIn('env_snippet', ad_red['accounts'][0])

        # Strict control_laravel_service test must FAIL if .env is missing or unit is inactive
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute(
                """INSERT INTO managed_app_services (username, uid, service_type, service_slug, app_path, php_branch, runtime_bin, workers, max_memory_mb, queues, port, enabled, unit_name, last_status, last_error, created_at, updated_at)
                   VALUES ('starter1', 1001, 'queue', 'q-clone', ?, 'php84', '/nonexistent/php', 1, 256, 'default', 0, 1, 'uniselv-lrv-1001-q-clone.service', 'inactive', '', 1, 1)""",
                (str(app_dir),),
            )
            svc_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
            conn.commit()
        finally:
            conn.close()

        with mock.patch.object(pm, '_query_systemd_unit', return_value={'active_state': 'inactive', 'sub_state': 'dead', 'main_pid': 0, 'slice': '', 'enabled': True}):
            res_fail = pm.control_laravel_service(self.db_path, 'starter1', 'starter1', svc_id, 'test', is_admin=False)
        self.assertFalse(res_fail['all_passed'])
        step_map = {s['name']: s['passed'] for s in res_fail['steps']}
        self.assertFalse(step_map['env_exists'])
        self.assertFalse(step_map['systemd_slice'])

        (app_dir / '.env').write_text('APP_ENV=production\n', encoding='utf-8')
        with mock.patch.object(pm, '_query_systemd_unit', return_value={'active_state': 'active', 'sub_state': 'running', 'main_pid': 4242, 'slice': 'golden-1001.slice', 'enabled': True}):
            res_pass = pm.control_laravel_service(self.db_path, 'starter1', 'starter1', svc_id, 'test', is_admin=False)
        self.assertTrue(res_pass['all_passed'])

    def test_per_user_permissions_enforcement_and_supervisor_sanitization(self):
        # Default permission policy: Laravel types allowed, Supervisor opt-in False
        perms0 = pm.get_user_platform_permissions(self.db_path, 'starter1')
        self.assertTrue(perms0['platform_laravel_queue'])
        self.assertFalse(perms0['platform_supervisor'])

        # Grant Supervisor & revoke Scheduler for starter1
        res_perm = pm.set_user_platform_permissions(
            self.collector, self.db_path, 'root', 'starter1',
            {'platform_supervisor': 1, 'platform_laravel_scheduler': 0},
        )
        self.assertTrue(res_perm['success'])
        self.assertTrue(res_perm['permissions']['platform_supervisor'])
        self.assertFalse(res_perm['permissions']['platform_laravel_scheduler'])

        budget = pm.compute_laravel_service_budget(self.collector, 'starter1', self.db_path)
        self.assertTrue(budget['supervisor_allowed'])
        self.assertFalse(budget['scheduler_allowed'])
        self.assertTrue(budget['queue_allowed'])

        # Attempting to install a Scheduler unit for starter1 must fail when permission is disabled
        home_dir = self.base / 'home_sup'
        app_dir = home_dir / 'app1'
        (app_dir / 'storage' / 'logs').mkdir(parents=True)
        (app_dir / 'artisan').write_text('#!/usr/bin/env php\n', encoding='utf-8')
        with mock.patch.object(pm, '_resolve_user_ids', return_value=(1001, 1001, str(home_dir))):
            sch_fail = pm.save_and_install_laravel_service(
                self.collector, self.db_path, 'starter1',
                {'username': 'starter1', 'service_type': 'scheduler', 'app_path': str(app_dir), 'php_branch': 'php84'},
            )
        self.assertFalse(sch_fail['success'])
        self.assertIn('permission is disabled', sch_fail['error'].lower())

        # Sanitizer must strip user=root / shell injection from drop-in conf and force user=starter1
        bad_conf = home_dir / '.uniselv-supervisor' / 'conf.d' / 'laravel-worker.conf'
        bad_conf.parent.mkdir(parents=True, exist_ok=True)
        bad_conf.write_text(
            f"[program:laravel-worker]\n"
            f"user=root\n"
            f"directory={app_dir}\n"
            f"command=/usr/local/apps/php84/bin/php {app_dir}/artisan queue:work --sleep=3\n"
            f"numprocs=99\n"
            f"[program:evil]\n"
            f"user=root\n"
            f"command=/bin/sh -c 'id; whoami'\n",
            encoding='utf-8',
        )
        with mock.patch.object(pm, '_resolve_user_ids', return_value=(1001, 1001, str(home_dir))):
            parsed = pm._parse_user_supervisor_dropin(bad_conf, 'starter1', str(home_dir), max_workers=2)
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0]['slug'], 'laravel-worker')
        self.assertEqual(parsed[0]['numprocs'], 2)
        prog_name, rendered = pm._render_supervisor_program_conf(1001, 'starter1', parsed[0])
        self.assertEqual(prog_name, 'uniselv-1001-laravel-worker')
        self.assertIn('user=starter1', rendered)
        self.assertNotIn('user=root', rendered)

        # Register enabled queue service, then revoke queue permission -> enforcement disables it
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute(
                """INSERT INTO managed_app_services (username, uid, service_type, service_slug, app_path, php_branch, runtime_bin, workers, max_memory_mb, queues, port, enabled, unit_name, last_status, last_error, created_at, updated_at)
                   VALUES ('starter1', 1001, 'queue', 'q-sup', ?, 'php84', '/usr/local/apps/php84/bin/php', 1, 256, 'default', 0, 1, 'uniselv-lrv-1001-q-sup.service', 'active', '', 1, 1)""",
                (str(app_dir),),
            )
            conn.commit()
        finally:
            conn.close()
        rev = pm.set_user_platform_permissions(self.collector, self.db_path, 'root', 'starter1', {'platform_laravel_queue': 0})
        self.assertIn('uniselv-lrv-1001-q-sup.service', rev['enforcement']['stopped_units'])

    def test_stack_readiness_and_project_dropin_discovery_control(self):
        # 1. Readiness matrix includes all 5 capabilities and reflects global policy toggles
        with mock.patch.object(pm, '_detect_php_cli_extensions', return_value=('/usr/local/apps/php84/bin/php', {'pcntl', 'posix', 'redis', 'sockets', 'curl'})), \
             mock.patch.object(pm, 'get_supervisor_status', return_value={'installed': True, 'runtime_active': True, 'unit_name': 'supervisor.service', 'sync_bin_installed': True}), \
             mock.patch.object(pm, '_find_redis_cli', return_value='/usr/bin/redis-cli'), \
             mock.patch.object(pm.shutil, 'which', side_effect=lambda cmd: '/usr/sbin/cron' if cmd == 'cron' else None):
            r_all = pm.get_laravel_stack_readiness(self.db_path)
            self.assertEqual(set(r_all.keys()), {'supervisor', 'queue', 'horizon', 'reverb', 'scheduler'})
            self.assertTrue(r_all['horizon']['installed'])
            self.assertTrue(r_all['scheduler']['global_enabled'])

            conn = sqlite3.connect(self.db_path)
            try:
                conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('platform_laravel_allowed_types', 'queue,horizon,reverb')")
                conn.commit()
            finally:
                conn.close()
            r_no_sch = pm.get_laravel_stack_readiness(self.db_path)
            self.assertFalse(r_no_sch['scheduler']['global_enabled'])
            self.assertTrue(r_no_sch['queue']['global_enabled'])

        # 2. Auto-discovery & control of project drop-ins without any manual DB registration
        home_dir = self.base / 'home_dropin'
        app_dir = home_dir / 'clone.example.com'
        (app_dir / 'storage' / 'logs').mkdir(parents=True)
        (app_dir / 'artisan').write_text('#!/usr/bin/env php\n', encoding='utf-8')
        (app_dir / '.env').write_text('APP_ENV=production\n', encoding='utf-8')
        log_file = app_dir / 'storage' / 'logs' / 'worker.log'
        log_file.write_text('worker started ok\n', encoding='utf-8')
        dropin = home_dir / '.uniselv-supervisor' / 'conf.d' / 'laravel-worker.conf'
        dropin.parent.mkdir(parents=True, exist_ok=True)
        dropin.write_text(
            f"[program:laravel-worker]\n"
            f"directory={app_dir}\n"
            f"command=/usr/local/apps/php84/bin/php {app_dir}/artisan queue:work\n"
            f"numprocs=2\n"
            f"stdout_logfile={log_file}\n",
            encoding='utf-8',
        )

        with mock.patch.object(pm, '_resolve_user_ids', return_value=(1001, 1001, str(home_dir))), \
             mock.patch.object(pm, '_query_supervisor_program', return_value={'managed': True, 'program_name': 'uniselv-1001-laravel-worker', 'active_state': 'active', 'sub_state': 'RUNNING', 'main_pid': 7711, 'slice': 'golden-1001.slice (supervisor)'}):
            listed = pm.list_laravel_services(self.collector, self.db_path, target_user='starter1')
            drop_svcs = [s for s in listed['services'] if s.get('source') == 'project_dropin']
            self.assertEqual(len(drop_svcs), 1)
            self.assertEqual(drop_svcs[0]['id'], 'dropin:starter1:laravel-worker')
            self.assertTrue(drop_svcs[0]['runtime_active'])

            t_res = pm.control_laravel_service(self.db_path, 'starter1', 'starter1', 'dropin:starter1:laravel-worker', 'test', is_admin=False)
            self.assertTrue(t_res['all_passed'])
            l_res = pm.control_laravel_service(self.db_path, 'starter1', 'starter1', 'dropin:starter1:laravel-worker', 'logs', is_admin=False)
            self.assertTrue(l_res['success'])
            self.assertIn('worker started ok', '\n'.join(l_res['lines']))
            deny = pm.control_laravel_service(self.db_path, 'otheruser', 'otheruser', 'dropin:starter1:laravel-worker', 'logs', is_admin=False)
            self.assertEqual(deny.get('status_code'), 403)

    def test_orphaned_dropin_detection_and_removal(self):
        home_dir = self.base / 'home_orphan'
        app_dir = home_dir / 'deleted.example.com'  # Directory does not exist on disk!
        dropin = home_dir / '.uniselv-supervisor' / 'conf.d' / 'dead-worker.conf'
        dropin.parent.mkdir(parents=True, exist_ok=True)
        dropin.write_text(
            f"[program:dead-worker]\n"
            f"directory={app_dir}\n"
            f"command=/usr/local/apps/php84/bin/php {app_dir}/artisan queue:work\n"
            f"numprocs=1\n",
            encoding='utf-8',
        )

        with mock.patch.object(pm, '_resolve_user_ids', return_value=(1001, 1001, str(home_dir))), \
             mock.patch.object(pm, '_query_supervisor_program', return_value={'managed': True, 'program_name': 'uniselv-1001-dead-worker', 'active_state': 'failed', 'sub_state': 'FATAL', 'main_pid': 0, 'slice': 'golden-1001.slice (supervisor)'}):
            # 1. Detection: Must be identified as orphaned
            listed = pm.list_laravel_services(self.collector, self.db_path, target_user='starter1')
            drop_svcs = [s for s in listed['services'] if s.get('id') == 'dropin:starter1:dead-worker']
            self.assertEqual(len(drop_svcs), 1)
            svc = drop_svcs[0]
            self.assertTrue(svc.get('orphaned'))
            self.assertEqual(svc.get('active_state'), 'orphaned')
            self.assertEqual(svc.get('sub_state'), 'missing project')
            self.assertFalse(svc.get('runtime_active'))
            self.assertEqual(svc.get('conf_file'), str(dropin))

            # 2. Removal: Calling uninstall must remove the .conf file and reload supervisorctl
            sup_calls = []
            def _fake_run_sup(args, **kwargs):
                sup_calls.append(args)
                return mock.MagicMock(returncode=0, stdout='ok\n', stderr='')

            with mock.patch.object(pm, '_run_supervisorctl', side_effect=_fake_run_sup):
                uninst = pm.control_laravel_service(self.db_path, 'starter1', 'starter1', 'dropin:starter1:dead-worker', 'uninstall', is_admin=False)
                self.assertTrue(uninst['success'])
                self.assertTrue(uninst['uninstalled'])
                self.assertFalse(dropin.exists())
                # Verify supervisor stop and reread/update were triggered
                ops_found = [args[0] for args in sup_calls]
                self.assertIn('stop', ops_found)
                self.assertIn('reread', ops_found)
                self.assertIn('update', ops_found)

    def test_sync_and_reconcile_laravel_workers(self):
        home_dir = self.base / 'home_sync'
        active_app = home_dir / 'live.example.com'
        (active_app / 'storage' / 'logs').mkdir(parents=True)
        (active_app / 'artisan').write_text('#!/usr/bin/env php\n', encoding='utf-8')
        (active_app / 'composer.json').write_text('{"name": "test/live-app"}\n', encoding='utf-8')
        (active_app / '.env').write_text('APP_ENV=production\n', encoding='utf-8')

        conf_dir = home_dir / '.uniselv-supervisor' / 'conf.d'
        conf_dir.mkdir(parents=True, exist_ok=True)

        # Active worker drop-in
        live_dropin = conf_dir / 'live-worker.conf'
        live_dropin.write_text(
            f"[program:live-worker]\n"
            f"directory={active_app}\n"
            f"command=/usr/local/apps/php84/bin/php {active_app}/artisan queue:work\n",
            encoding='utf-8',
        )

        # Dead/orphaned worker drop-in pointing to missing directory
        dead_app = home_dir / 'deleted.example.com'
        dead_dropin = conf_dir / 'dead-worker.conf'
        dead_dropin.write_text(
            f"[program:dead-worker]\n"
            f"directory={dead_app}\n"
            f"command=/usr/local/apps/php84/bin/php {dead_app}/artisan queue:work\n",
            encoding='utf-8',
        )

        sup_calls = []
        def _fake_run_sup(args, **kwargs):
            sup_calls.append(args)
            return mock.MagicMock(returncode=0, stdout='reloaded\n', stderr='')

        with mock.patch.object(pm, '_resolve_user_ids', return_value=(1001, 1001, str(home_dir))), \
             mock.patch.object(pm, '_run_supervisorctl', side_effect=_fake_run_sup):
            res = pm.sync_and_reconcile_laravel_workers(self.collector, self.db_path, 'starter1', 'starter1', auto_prune=True, is_admin=False)
            self.assertTrue(res['success'])
            self.assertEqual(res['pruned_count'], 1)
            self.assertIn('dead-worker', [p['slug'] for p in res['pruned']])
            self.assertFalse(dead_dropin.exists())
            self.assertTrue(live_dropin.exists())
            self.assertGreaterEqual(res['synced_count'], 1)
            ops_found = [args[0] for args in sup_calls]
            self.assertIn('stop', ops_found)
            self.assertIn('reread', ops_found)
            self.assertIn('update', ops_found)

    def test_manage_laravel_scheduler_cron(self):
        home_dir = self.base / 'home_starter1_cron'
        app_dir = home_dir / 'myproject'
        app_dir.mkdir(parents=True)
        (app_dir / 'artisan').write_text('#!/usr/bin/env php\n', encoding='utf-8')

        crontab_content = ["# Existing cron jobs\n0 0 * * * /backup.sh\n"]

        def _fake_read_cron(u):
            return [line for line in crontab_content[0].splitlines() if line.strip()]

        def _fake_write_cron(u, text):
            crontab_content[0] = text
            return True, ''

        with mock.patch.object(pm, '_resolve_user_ids', return_value=(1001, 1001, str(home_dir))), \
             mock.patch.object(pm, '_read_crontab_lines', side_effect=_fake_read_cron), \
             mock.patch.object(pm, '_write_crontab_lines', side_effect=_fake_write_cron):
            # 1. Status: Not installed initially
            st = pm.manage_laravel_scheduler_cron(self.collector, self.db_path, 'starter1', 'starter1', app_path=str(app_dir), php_branch='php84', operation='status')
            self.assertTrue(st['success'])
            self.assertFalse(st['is_installed'])

            # 2. Install
            inst = pm.manage_laravel_scheduler_cron(self.collector, self.db_path, 'starter1', 'starter1', app_path=str(app_dir), php_branch='php84', operation='install')
            self.assertTrue(inst['success'])
            self.assertTrue(inst['is_installed'])
            self.assertIn('BEGIN UNISELV SCHEDULER', crontab_content[0])
            self.assertIn('schedule:run', crontab_content[0])

            # 3. Status: Now installed
            st2 = pm.manage_laravel_scheduler_cron(self.collector, self.db_path, 'starter1', 'starter1', app_path=str(app_dir), php_branch='php84', operation='status')
            self.assertTrue(st2['success'])
            self.assertTrue(st2['is_installed'])

            # 4. Remove
            rem = pm.manage_laravel_scheduler_cron(self.collector, self.db_path, 'starter1', 'starter1', app_path=str(app_dir), php_branch='php84', operation='remove')
            self.assertTrue(rem['success'])
            self.assertFalse(rem['is_installed'])
            self.assertNotIn('BEGIN UNISELV SCHEDULER', crontab_content[0])
            self.assertIn('/backup.sh', crontab_content[0])

    def test_manage_reverb_vhost_proxy(self):
        conf_d = self.base / 'apache_conf_d'
        conf_d.mkdir(parents=True)

        def _fake_run(cmd, **kwargs):
            return mock.MagicMock(returncode=0, stdout='Syntax OK\n', stderr='')

        apachectl = conf_d / 'apachectl'
        apachectl.touch()
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("INSERT INTO managed_app_services (username, uid, service_type, service_slug, app_path, port, unit_name, created_at, updated_at) VALUES ('starter1', 1001, 'reverb', 'reverb', '/home/starter1/app', 22241, 'reverb.service', 1, 1)")
            conn.commit()
        finally:
            conn.close()
        with mock.patch.object(pm, 'APACHE_CONF_DIR', conf_d), \
             mock.patch.object(pm, 'APACHECTL', apachectl), \
             mock.patch.object(pm, '_owns_webuzo_domain', side_effect=lambda user, domain: domain == 'example.com'), \
             mock.patch('subprocess.run', side_effect=_fake_run):
            self.assertEqual(pm.manage_reverb_vhost_proxy(self.collector, self.db_path, 'starter1', 'starter1', 'foreign.example', 22241)['status_code'], 403)
            self.assertEqual(pm.manage_reverb_vhost_proxy(self.collector, self.db_path, 'starter1', 'starter1', 'example.com', 6379)['status_code'], 403)
            # 1. Status: initially not installed
            st = pm.manage_reverb_vhost_proxy(self.collector, self.db_path, 'root', 'starter1', 'example.com', 22241, 'status', is_admin=True)
            self.assertTrue(st['success'])
            self.assertFalse(st['is_installed'])

            # 2. Install
            inst = pm.manage_reverb_vhost_proxy(self.collector, self.db_path, 'root', 'starter1', 'example.com', 22241, 'install', is_admin=True)
            self.assertTrue(inst['success'])
            self.assertTrue(inst['is_installed'])
            target_conf = conf_d / 'example.com.conf'
            self.assertTrue(target_conf.exists())
            conf_text = target_conf.read_text(encoding='utf-8')
            self.assertIn('ws://127.0.0.1:22241/app', conf_text)

            # 3. Remove
            rem = pm.manage_reverb_vhost_proxy(self.collector, self.db_path, 'root', 'starter1', 'example.com', 22241, 'remove', is_admin=True)
            self.assertTrue(rem['success'])
            self.assertFalse(rem['is_installed'])
            self.assertFalse(target_conf.exists())

    def test_get_active_resource_boosts(self):
        import time
        conn = sqlite3.connect(self.db_path)
        now = time.time()
        try:
            conn.execute("""
                INSERT INTO temporary_overrides (username, uid, original_plan, override_plan, created_at, expires_at, reason, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, ('starter1', 1001, 'starter', 'turbo', now - 100, now + 1800, 'Flash sale promo', 'active'))
            conn.commit()
        finally:
            conn.close()

        boosts_res = pm.get_active_resource_boosts(self.collector, self.db_path)
        self.assertTrue(boosts_res['success'])
        self.assertEqual(boosts_res['count'], 1)
        b = boosts_res['boosts'][0]
        self.assertEqual(b['username'], 'starter1')
        self.assertEqual(b['target_plan'], 'turbo')
        self.assertGreater(b['remaining_seconds'], 1500)
        self.assertGreaterEqual(b['remaining_minutes'], 25)

    def test_kill_stuck_cli_processes(self):
        home_dir = self.base / 'home_starter1_proc'
        home_dir.mkdir(parents=True)

        proc_dir_artisan = self.base / '10001'
        proc_dir_artisan.mkdir(parents=True)
        (proc_dir_artisan / 'cmdline').write_bytes(b'/usr/local/apps/php84/bin/php\x00/home/starter1/artisan\x00queue:work\x00')

        proc_dir_fpm = self.base / '10002'
        proc_dir_fpm.mkdir(parents=True)
        (proc_dir_fpm / 'cmdline').write_bytes(b'php-fpm:\x00pool\x00starter1\x00')

        fake_stat_user = mock.MagicMock(st_uid=1001)

        killed_signals = []
        def _fake_kill(pid, sig):
            killed_signals.append((pid, sig))

        def _fake_stat(path):
            return fake_stat_user

        with mock.patch.object(pm, '_resolve_user_ids', return_value=(1001, 1001, str(home_dir))), \
             mock.patch.object(pm.os, 'name', 'posix'), \
             mock.patch('glob.glob', return_value=[str(proc_dir_artisan), str(proc_dir_fpm)]), \
             mock.patch('os.stat', side_effect=_fake_stat), \
             mock.patch('os.kill', side_effect=_fake_kill):
            res = pm.kill_stuck_cli_processes(self.collector, self.db_path, 'starter1', 'starter1', is_admin=False)
            self.assertTrue(res['success'])
            self.assertEqual(res['killed_count'], 1)
            pids = [k['pid'] for k in res['killed']]
            self.assertIn(10001, pids)
            self.assertNotIn(10002, pids)  # php-fpm strictly protected


if __name__ == '__main__':
    unittest.main()
