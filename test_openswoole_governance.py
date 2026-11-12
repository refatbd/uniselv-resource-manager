"""Unit & security tests for OpenSwoole multi-PHP automation and resource enforcement."""
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
            _stub.flock = lambda *a, **k: None
            _stub.LOCK_EX = 2
            _stub.LOCK_NB = 4
            _stub.LOCK_UN = 8
            sys.modules[_mod_name] = _stub

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'agent'))

import openswoole_manager as om
import schema
from ipc_server import IpcRequestHandler


class _FakeCollector:
    def __init__(self, db_path, users=None, limits_by_uid=None):
        self.db_path = db_path
        self.users = users or {
            'starter1': {'uid': 1001, 'plan_name': 'starter', 'domain': 'starter.example.com'},
            'ent1': {'uid': 1002, 'plan_name': 'enterprise', 'domain': 'ent.example.com'},
        }
        self.limits_by_uid = limits_by_uid or {
            1001: {'cpuquota': 100, 'mem_max': 1024 * 1024 * 1024, 'maxtask': 64},
            1002: {'cpuquota': 400, 'mem_max': 4096 * 1024 * 1024, 'maxtask': 256},
        }
        self.events = []
        self.settings = {}

    def get_webuzo_users(self):
        return dict(self.users)

    def get_plan_limits(self, plan_name):
        if plan_name == 'enterprise':
            return {'cpuquota': 400, 'mem_max': 4096 * 1024 * 1024, 'maxtask': 256}
        return {'cpuquota': 100, 'mem_max': 1024 * 1024 * 1024, 'maxtask': 64}

    def get_user_limits(self, uid, plan_name):
        return self.limits_by_uid.get(uid, self.get_plan_limits(plan_name))

    def record_event(self, uname, uid, event_type, severity, message, details):
        self.events.append({
            'username': uname,
            'uid': uid,
            'event_type': event_type,
            'severity': severity,
            'message': message,
            'details': details,
        })


class OpenSwooleGovernanceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = pathlib.Path(self.tmp.name)
        self.db_path = str(self.base / 'resman.sqlite')
        schema.init_db(self.db_path)
        self.old_store = om.STORE_DIR
        self.old_state = om.STATE_FILE
        self.old_job = om.JOB_FILE
        self.old_policy = om.POLICY_EXPORT_FILE
        self.old_lock = om.LOCK_FILE
        om.STORE_DIR = self.base / 'openswoole'
        om.STATE_FILE = om.STORE_DIR / 'state.json'
        om.JOB_FILE = om.STORE_DIR / 'job.json'
        om.POLICY_EXPORT_FILE = om.STORE_DIR / 'policy.json'
        om.LOCK_FILE = om.STORE_DIR / 'build.lock'

    def tearDown(self):
        om.STORE_DIR = self.old_store
        om.STATE_FILE = self.old_state
        om.JOB_FILE = self.old_job
        om.POLICY_EXPORT_FILE = self.old_policy
        om.LOCK_FILE = self.old_lock
        self.tmp.cleanup()

    def test_php_compatibility_matrix(self):
        self.assertEqual(om.compatible_openswoole_candidates(70433), ['4.12.1'])
        self.assertEqual(om.compatible_openswoole_candidates(80134), ['22.1.2'])
        self.assertEqual(om.compatible_openswoole_candidates(80235), ['25.2.0', '22.1.2'])
        self.assertEqual(om.compatible_openswoole_candidates(80427), ['25.2.0', '26.2.0'])
        self.assertEqual(om.compatible_openswoole_candidates(80501), ['26.2.0', '25.2.0'])
        self.assertEqual(om.compatible_openswoole_candidates(70300), [])

    def test_compute_account_policy_scales_strictly_with_assigned_resources(self):
        settings = dict(om.OPENSWOOLE_DEFAULTS)
        starter = om.compute_account_policy(
            'u_start', 1001, 'starter',
            {'cpuquota': 100, 'mem_max': 1024 * 1024 * 1024, 'maxtask': 64},
            settings,
        )
        self.assertTrue(starter['allowed'])
        self.assertEqual(starter['max_workers'], 1)
        self.assertEqual(starter['max_task_workers'], 0)

        ent = om.compute_account_policy(
            'u_ent', 1002, 'enterprise',
            {'cpuquota': 400, 'mem_max': 4096 * 1024 * 1024, 'maxtask': 256},
            settings,
        )
        self.assertEqual(ent['max_workers'], 4)
        self.assertEqual(ent['max_task_workers'], 2)

        # Operator override cannot bypass hard physical 64 MiB/worker account memory limit
        over = om.compute_account_policy(
            'u_tiny', 1003, 'tiny',
            {'cpuquota': 100, 'mem_max': 256 * 1024 * 1024, 'maxtask': 32},
            settings,
            account_policy={'allowed': 1, 'max_workers_override': 32, 'max_task_workers_override': -1},
        )
        self.assertEqual(over['max_workers'], 4)

        # Plan deny inherited, account force allow overrides plan deny
        plan_denied = om.compute_account_policy(
            'u_a', 1004, 'starter',
            {'cpuquota': 100, 'mem_max': 1024 * 1024 * 1024, 'maxtask': 64},
            settings,
            plan_policy={'allowed': 0, 'max_workers_override': 0, 'max_task_workers_override': -1},
        )
        self.assertFalse(plan_denied['allowed'])
        self.assertEqual(plan_denied['max_workers'], 0)

        acc_allowed = om.compute_account_policy(
            'u_a', 1004, 'starter',
            {'cpuquota': 100, 'mem_max': 1024 * 1024 * 1024, 'maxtask': 64},
            settings,
            plan_policy={'allowed': 0, 'max_workers_override': 0, 'max_task_workers_override': -1},
            account_policy={'allowed': 1, 'max_workers_override': 2, 'max_task_workers_override': -1},
        )
        self.assertTrue(acc_allowed['allowed'])
        self.assertEqual(acc_allowed['max_workers'], 2)

    def test_reconcile_waits_for_stability_then_provisions_new_php(self):
        fake_versions = {
            'php84': {
                'version': 'php84', 'php_version': '8.4.27', 'php_version_id': 80427,
                'extension_dir': '/usr/local/apps/php84/ext', 'php_config_ext_dir': '',
                'ini_file': str(self.base / 'php84.ini'), 'ini_exists': True,
                'phpize': '/usr/local/apps/php84/bin/phpize', 'php_config': '/usr/local/apps/php84/bin/php-config',
                'so_exists': True, 'loaded': True, 'openswoole_version': '25.2.0',
                'compatible_versions': ['25.2.0', '26.2.0'], 'recommended_release': '25.2.0',
                'manually_disabled': False, 'status': 'active', 'last_error': '', 'last_build_at': 0,
            },
            'php85': {
                'version': 'php85', 'php_version': '8.5.1', 'php_version_id': 80501,
                'extension_dir': '/usr/local/apps/php85/ext', 'php_config_ext_dir': '',
                'ini_file': str(self.base / 'php85.ini'), 'ini_exists': False,
                'phpize': '/usr/local/apps/php85/bin/phpize', 'php_config': '/usr/local/apps/php85/bin/php-config',
                'so_exists': False, 'loaded': False, 'openswoole_version': '',
                'compatible_versions': ['26.2.0', '25.2.0'], 'recommended_release': '26.2.0',
                'manually_disabled': False, 'status': 'not_installed', 'last_error': '', 'last_build_at': 0,
            },
        }
        with mock.patch.object(om, 'discover_php_versions', return_value=fake_versions), \
             mock.patch.object(om, 'build_and_enable_php_version', return_value={'success': True, 'version': 'php85', 'action': 'compiled_and_enabled'}) as build_mock:
            first = om.reconcile_new_php_versions(self.db_path, automatic=True, force_all=False)
            self.assertEqual(build_mock.call_count, 0)
            self.assertEqual(first['skipped'][0]['reason'], 'waiting_install_stability')

            second = om.reconcile_new_php_versions(self.db_path, automatic=True, force_all=False)
            self.assertEqual(build_mock.call_count, 1)
            self.assertEqual(len(second['provisioned']), 1)
            self.assertEqual(second['provisioned'][0]['version'], 'php85')

    def test_enforce_runtime_policies_contains_escaped_and_caps_workers(self):
        collector = _FakeCollector(self.db_path)
        fake_procs = [
            {'pid': 5001, 'ppid': 1, 'uid': 1001, 'username': 'starter1', 'comm': 'php', 'cmdline': 'swoole: master', 'exe': '/usr/local/apps/php84/bin/php', 'php_version': 'php84', 'role': 'master', 'rss_bytes': 40 * 1024 * 1024, 'threads': 2, 'start_ticks': 100, 'current_cgroup': '0::/user.slice', 'expected_cgroup': '/golden.slice/golden-1001.slice', 'contained': False},
            {'pid': 5002, 'ppid': 5001, 'uid': 1001, 'username': 'starter1', 'comm': 'php', 'cmdline': 'swoole: worker #0', 'exe': '/usr/local/apps/php84/bin/php', 'php_version': 'php84', 'role': 'worker', 'rss_bytes': 50 * 1024 * 1024, 'threads': 1, 'start_ticks': 101, 'current_cgroup': '0::/golden.slice/golden-1001.slice', 'expected_cgroup': '/golden.slice/golden-1001.slice', 'contained': True},
            {'pid': 5003, 'ppid': 5001, 'uid': 1001, 'username': 'starter1', 'comm': 'php', 'cmdline': 'swoole: worker #1', 'exe': '/usr/local/apps/php84/bin/php', 'php_version': 'php84', 'role': 'worker', 'rss_bytes': 50 * 1024 * 1024, 'threads': 1, 'start_ticks': 102, 'current_cgroup': '0::/golden.slice/golden-1001.slice', 'expected_cgroup': '/golden.slice/golden-1001.slice', 'contained': True},
            {'pid': 5004, 'ppid': 5001, 'uid': 1001, 'username': 'starter1', 'comm': 'php', 'cmdline': 'swoole: worker #2', 'exe': '/usr/local/apps/php84/bin/php', 'php_version': 'php84', 'role': 'worker', 'rss_bytes': 50 * 1024 * 1024, 'threads': 1, 'start_ticks': 103, 'current_cgroup': '0::/golden.slice/golden-1001.slice', 'expected_cgroup': '/golden.slice/golden-1001.slice', 'contained': True},
        ]
        stopped = []
        with mock.patch.object(om, 'scan_openswoole_processes', return_value=fake_procs), \
             mock.patch.object(om, 'contain_process_in_account_slice', return_value=(True, 'Contained')) as contain_mock, \
             mock.patch.object(om, '_safe_stop_pid', side_effect=lambda u, p, s: stopped.append(p) or True):
            res = om.enforce_runtime_policies(collector, self.db_path)

        contain_mock.assert_called_once_with(1001, 5001)
        self.assertEqual(res['contained_moves'], 1)
        # starter1 allows max_workers=1, so 2 excess highest worker PIDs (5004, 5003) must be stopped
        self.assertEqual(stopped, [5004, 5003])
        self.assertEqual(len(res['violations']), 1)

    def test_ipc_authorization_isolates_admin_and_enduser(self):
        collector = _FakeCollector(self.db_path)
        if sys.platform == 'win32':
            import ipc_server as ipc_mod
            with mock.patch.object(ipc_mod.GoldenShieldManager, 'ensure_systemd_slice_persistence', return_value=None):
                handler = IpcRequestHandler(db_path=self.db_path, collector=collector)
        else:
            handler = IpcRequestHandler(db_path=self.db_path, collector=collector)

        # Enduser cannot modify openswoole settings or run PHP builds
        denied1 = handler.handle_request({'action': 'save_openswoole_settings', 'auth': {'user': 'starter1', 'is_admin': False}, 'params': {'openswoole_auto_install_new_php': '0'}})
        self.assertIn('Forbidden', denied1.get('error', ''))
        denied2 = handler.handle_request({'action': 'openswoole_php_action', 'auth': {'user': 'starter1', 'is_admin': False}, 'params': {'operation': 'sync_all'}})
        self.assertIn('Forbidden', denied2.get('error', ''))

        # Reseller cannot change global openswoole settings
        collector.users['res1'] = {'uid': 1010, 'plan_name': 'pro', 'reseller': True}
        denied3 = handler.handle_request({'action': 'save_openswoole_settings', 'auth': {'user': 'res1', 'is_admin': True}, 'params': {'openswoole_auto_install_new_php': '0'}})
        self.assertIn('Forbidden', denied3.get('error', ''))

        # Enduser CAN inspect their own assigned OpenSwoole budget
        with mock.patch.object(om, 'discover_php_versions', return_value={}), \
             mock.patch.object(om, 'scan_openswoole_processes', return_value=[]):
            eu = handler.handle_request({'action': 'get_enduser_openswoole', 'auth': {'user': 'starter1', 'is_admin': False}, 'params': {}})
        self.assertTrue(eu['success'])
        self.assertEqual(eu['policy']['max_workers'], 1)
        self.assertIn('--workers=1', eu['guidance']['recommended_octane_command'])

        # Root Admin CAN update account policy
        saved = handler.handle_request({'action': 'save_openswoole_policy', 'auth': {'user': 'root', 'is_admin': True}, 'params': {'scope': 'account', 'target': 'starter1', 'allowed': '0'}})
        self.assertTrue(saved['success'])
        with mock.patch.object(om, 'discover_php_versions', return_value={}), \
             mock.patch.object(om, 'scan_openswoole_processes', return_value=[]):
            eu2 = handler.handle_request({'action': 'get_enduser_openswoole', 'auth': {'user': 'starter1', 'is_admin': False}, 'params': {}})
        self.assertFalse(eu2['policy']['allowed'])
        self.assertEqual(eu2['policy']['max_workers'], 0)

    def test_tree_role_inference_allows_compliant_and_stops_overbudget_master(self):
        collector = _FakeCollector(self.db_path)
        compliant_tree = om._infer_tree_roles([
            {'pid': 6001, 'ppid': 1, 'uid': 1001, 'username': 'starter1', 'comm': 'php', 'cmdline': '/usr/local/apps/php84/bin/php srv.php', 'exe': '/usr/local/apps/php84/bin/php', 'php_version': 'php84', 'role': 'app', 'rss_bytes': 20 * 1024 * 1024, 'threads': 2, 'start_ticks': 100, 'current_cgroup': '0::/golden.slice/golden-1001.slice', 'expected_cgroup': '/golden.slice/golden-1001.slice', 'contained': True},
            {'pid': 6002, 'ppid': 6001, 'uid': 1001, 'username': 'starter1', 'comm': 'php', 'cmdline': '/usr/local/apps/php84/bin/php srv.php', 'exe': '/usr/local/apps/php84/bin/php', 'php_version': 'php84', 'role': 'app', 'rss_bytes': 15 * 1024 * 1024, 'threads': 1, 'start_ticks': 101, 'current_cgroup': '0::/golden.slice/golden-1001.slice', 'expected_cgroup': '/golden.slice/golden-1001.slice', 'contained': True},
            {'pid': 6003, 'ppid': 6002, 'uid': 1001, 'username': 'starter1', 'comm': 'php', 'cmdline': '/usr/local/apps/php84/bin/php srv.php', 'exe': '/usr/local/apps/php84/bin/php', 'php_version': 'php84', 'role': 'app', 'rss_bytes': 25 * 1024 * 1024, 'threads': 1, 'start_ticks': 102, 'current_cgroup': '0::/golden.slice/golden-1001.slice', 'expected_cgroup': '/golden.slice/golden-1001.slice', 'contained': True},
        ])
        self.assertEqual([p['role'] for p in compliant_tree], ['master', 'manager', 'worker'])
        stopped_compliant = []
        with mock.patch.object(om, 'scan_openswoole_processes', return_value=compliant_tree), \
             mock.patch.object(om, '_safe_stop_pid', side_effect=lambda u, p, s: stopped_compliant.append(p) or True):
            res_ok = om.enforce_runtime_policies(collector, self.db_path)
        self.assertEqual(res_ok['violations'], [])
        self.assertEqual(stopped_compliant, [])

        overbudget_tree = om._infer_tree_roles([
            {'pid': 7001, 'ppid': 1, 'uid': 1001, 'username': 'starter1', 'comm': 'php', 'cmdline': 'php srv.php', 'exe': '/usr/local/apps/php84/bin/php', 'php_version': 'php84', 'role': 'app', 'rss_bytes': 20 * 1024 * 1024, 'threads': 2, 'start_ticks': 100, 'current_cgroup': '0::/golden.slice/golden-1001.slice', 'expected_cgroup': '/golden.slice/golden-1001.slice', 'contained': True},
            {'pid': 7002, 'ppid': 7001, 'uid': 1001, 'username': 'starter1', 'comm': 'php', 'cmdline': 'php srv.php', 'exe': '/usr/local/apps/php84/bin/php', 'php_version': 'php84', 'role': 'app', 'rss_bytes': 15 * 1024 * 1024, 'threads': 1, 'start_ticks': 101, 'current_cgroup': '0::/golden.slice/golden-1001.slice', 'expected_cgroup': '/golden.slice/golden-1001.slice', 'contained': True},
            {'pid': 7003, 'ppid': 7002, 'uid': 1001, 'username': 'starter1', 'comm': 'php', 'cmdline': 'php srv.php', 'exe': '/usr/local/apps/php84/bin/php', 'php_version': 'php84', 'role': 'app', 'rss_bytes': 25 * 1024 * 1024, 'threads': 1, 'start_ticks': 102, 'current_cgroup': '0::/golden.slice/golden-1001.slice', 'expected_cgroup': '/golden.slice/golden-1001.slice', 'contained': True},
            {'pid': 7004, 'ppid': 7002, 'uid': 1001, 'username': 'starter1', 'comm': 'php', 'cmdline': 'php srv.php', 'exe': '/usr/local/apps/php84/bin/php', 'php_version': 'php84', 'role': 'app', 'rss_bytes': 25 * 1024 * 1024, 'threads': 1, 'start_ticks': 103, 'current_cgroup': '0::/golden.slice/golden-1001.slice', 'expected_cgroup': '/golden.slice/golden-1001.slice', 'contained': True},
        ])
        stopped_over = []
        with mock.patch.object(om, 'scan_openswoole_processes', return_value=overbudget_tree), \
             mock.patch.object(om, '_safe_stop_pid', side_effect=lambda u, p, s: stopped_over.append(p) or True):
            res_over = om.enforce_runtime_policies(collector, self.db_path)
        self.assertEqual(res_over['violations'][0]['active_workers'], 2)
        self.assertEqual(stopped_over, [7001])

    def test_ordinary_php_cli_cron_never_misclassified_without_listen_socket(self):
        # Even though php.d/openswoole.ini loads openswoole.so globally, an ordinary cron CLI without
        # a listening socket or swoole/octane cmdline must NOT trigger OpenSwoole enforcement.
        with mock.patch.object(om, '_pid_holds_listening_socket', return_value=False), \
             mock.patch.object(om, '_pid_loads_openswoole', return_value=True):
            self.assertFalse(
                om._is_openswoole_process(
                    '/usr/local/apps/php84/bin/php artisan ims:sync-products --all',
                    'php',
                    '/usr/local/apps/php84/bin/php',
                    12345,
                    listening_inodes={'99999'},
                )
            )
        with mock.patch.object(om, '_pid_holds_listening_socket', return_value=True), \
             mock.patch.object(om, '_pid_loads_openswoole', return_value=True):
            self.assertTrue(
                om._is_openswoole_process(
                    '/usr/local/apps/php84/bin/php /home/u/app.php',
                    'php',
                    '/usr/local/apps/php84/bin/php',
                    12346,
                    listening_inodes={'99999'},
                )
            )

    def test_diagnostics_selftest_auth_and_audit_and_task_override(self):
        collector = _FakeCollector(self.db_path)
        if sys.platform == 'win32':
            import ipc_server as ipc_mod
            with mock.patch.object(ipc_mod.GoldenShieldManager, 'ensure_systemd_slice_persistence', return_value=None):
                handler = IpcRequestHandler(db_path=self.db_path, collector=collector)
        else:
            handler = IpcRequestHandler(db_path=self.db_path, collector=collector)

        collector.users['res1'] = {'uid': 1010, 'plan_name': 'pro', 'reseller': True}
        for act in ('openswoole_diagnostics', 'openswoole_selftest'):
            d_eu = handler.handle_request({'action': act, 'auth': {'user': 'starter1', 'is_admin': False}, 'params': {}})
            self.assertIn('Forbidden', d_eu.get('error', ''))
            d_res = handler.handle_request({'action': act, 'auth': {'user': 'res1', 'is_admin': True}, 'params': {}})
            self.assertIn('Forbidden', d_res.get('error', ''))

        # Save task-worker override and confirm effective policy updates via enduser payload
        saved_task = handler.handle_request({
            'action': 'save_openswoole_policy',
            'auth': {'user': 'root', 'is_admin': True},
            'params': {'scope': 'account', 'target': 'starter1', 'allowed': '1', 'max_workers_override': '2', 'max_task_workers_override': '3'},
        })
        self.assertTrue(saved_task['success'])
        with mock.patch.object(om, 'discover_php_versions', return_value={}), \
             mock.patch.object(om, 'scan_openswoole_processes', return_value=[]):
            eu_task = handler.handle_request({'action': 'get_enduser_openswoole', 'auth': {'user': 'starter1', 'is_admin': False}, 'params': {}})
        self.assertEqual(eu_task['policy']['max_workers'], 2)
        self.assertEqual(eu_task['policy']['max_task_workers'], 3)

        # Readiness check returns clean per-PHP structured report
        fake_ini = self.base / 'openswoole.ini'
        fake_ini.write_text(om.render_openswoole_ini(om.load_openswoole_settings(self.db_path)), encoding='utf-8')
        fake_matrix = {
            'php84': {
                'version': 'php84',
                'php_bin': '/usr/local/apps/php84/bin/php',
                'php_version': '8.4.1',
                'extension_dir': '/usr/local/apps/php84/ext/',
                'ini_file': str(fake_ini),
                'so_exists': True,
                'ini_exists': True,
                'loaded': True,
                'status': 'active',
                'openswoole_version': '25.2.0',
                'compatible_versions': ['25.2.0'],
                'last_error': '',
            }
        }
        fake_proc = mock.Mock(returncode=0, stdout='1\n', stderr='')
        with mock.patch.object(om, 'discover_php_versions', return_value=fake_matrix), \
             mock.patch.object(om.shutil, 'which', side_effect=lambda b: f'/usr/bin/{b}'), \
             mock.patch.object(om.subprocess, 'run', return_value=fake_proc):
            diag = om.run_openswoole_readiness_check(self.db_path)
        self.assertTrue(diag['success'])
        self.assertTrue(diag['all_passed'])
        self.assertEqual(diag['php_checks'][0]['openswoole_version'], '25.2.0')

        # Admin diagnostics & selftest IPC routes dispatch properly
        with mock.patch.object(om, 'run_openswoole_readiness_check', return_value={'success': True, 'all_passed': True, 'php_checks': [], 'toolchain': {}}):
            r_diag = handler.handle_request({'action': 'openswoole_diagnostics', 'auth': {'user': 'root', 'is_admin': True}, 'params': {}})
        self.assertTrue(r_diag['all_passed'])

        with mock.patch.object(om, 'run_openswoole_self_test', return_value={'success': True, 'all_passed': True, 'username': 'starter1', 'steps': []}):
            r_self = handler.handle_request({'action': 'openswoole_selftest', 'auth': {'user': 'root', 'is_admin': True}, 'params': {'username': 'starter1', 'php_version': 'php84'}})
        self.assertTrue(r_self['all_passed'])

        audit_rows = om.recent_openswoole_audit(self.db_path, limit=10)
        self.assertTrue(len(audit_rows) >= 1)


if __name__ == '__main__':
    unittest.main()
