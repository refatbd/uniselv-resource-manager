import sqlite3
import sys
import tempfile
import time
import types
import unittest
from contextlib import closing
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent / 'agent'))

from collector import MetricsCollector
from schema import init_db

# Only the SQLite handlers are exercised here. Windows lacks these Linux modules.
linux_modules = {name: types.ModuleType(name) for name in ('pwd', 'grp', 'fcntl')}
if sys.platform == 'win32':
    with patch.dict(sys.modules, linux_modules):
        from ipc_server import IpcRequestHandler
else:
    from ipc_server import IpcRequestHandler


class TelemetryHistoryTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.db_path = str(Path(directory.name) / 'telemetry.db')
        init_db(self.db_path)
        self.collector = MetricsCollector.__new__(MetricsCollector)
        self.collector.db_path = self.db_path
        self.collector.get_retention_settings = lambda: {
            'samples_days': 30, 'snapshots_days': 14, 'events_days': 30,
            'audit_days': 90, 'max_storage_mib': 10,
        }
        self.handler = IpcRequestHandler.__new__(IpcRequestHandler)
        self.handler.db_path = self.db_path
        self.handler._history_ttl = 0

    def history(self, username):
        return self.handler.action_enduser_history(username, {'range': '7d'})

    def test_minute_rollup_keeps_each_account_and_host_metrics(self):
        minute = (int(time.time()) - 3 * 86400) // 60 * 60
        accounts = ('first', 'second', 'third')
        with closing(sqlite3.connect(self.db_path)) as conn, conn:
            for index in range(12):
                stamp = minute + 1 + 5 * index
                conn.execute('INSERT INTO system_metrics(timestamp, cpu_percent) VALUES (?, ?)',
                             (stamp, index))
                conn.executemany('''
                    INSERT INTO samples(username, uid, timestamp, cpu_percent, cpu_throttled_events)
                    VALUES (?, ?, ?, ?, 1)
                ''', [(name, uid, stamp, index) for uid, name in enumerate(accounts, 1)])
        before = {name: self.history(name) for name in accounts}

        self.collector.prune_retention()
        self.collector.prune_retention()

        for name in accounts:
            with self.subTest(name=name):
                after = self.history(name)
                self.assertEqual(after['total_samples'], 12)
                self.assertEqual(after['points_count'], 1)
                self.assertEqual(after['summary'], before[name]['summary'])
                self.assertEqual(after['summary']['cpu_peak'], 11)
                self.assertEqual(after['account_total'][0]['fault'], 12)
        with closing(sqlite3.connect(self.db_path)) as conn:
            self.assertEqual(conn.execute('SELECT cpu_percent, sample_count FROM system_metrics').fetchall(),
                             [(5.5, 12)])

    def test_storage_target_protects_newest_hour(self):
        with closing(sqlite3.connect(self.db_path)) as conn, conn:
            recent = int(time.time()) - 300
            conn.executemany('INSERT INTO samples(username, uid, timestamp, plan_name) VALUES (?, 1, ?, ?)',
                             [('account', recent, 'x' * 1024)] * 12000)

        result = self.collector.prune_retention()

        self.assertTrue(result['over_budget'])
        self.assertEqual(result['deleted_samples'], 0)
        self.assertEqual(self.history('account')['total_samples'], 12000)

    def test_storage_pruning_stops_once_freed_pages_meet_the_target(self):
        with closing(sqlite3.connect(self.db_path)) as conn, conn:
            stamp = int(time.time()) - 7200
            conn.executemany('INSERT INTO samples(username, uid, timestamp, plan_name) VALUES (?, 1, ?, ?)',
                             [('account', stamp, 'x' * 1024)] * 12000)

        result = self.collector.prune_retention()

        self.assertFalse(result['over_budget'])
        self.assertGreater(result['deleted_samples'], 0)
        self.assertLess(result['deleted_samples'], 12000)

    def test_history_uses_no_more_than_300_chart_points(self):
        with closing(sqlite3.connect(self.db_path)) as conn, conn:
            start = int(time.time()) - 1000 * 60
            conn.executemany('INSERT INTO samples(username, uid, timestamp) VALUES (?, 1, ?)',
                             [('account', start + index * 60) for index in range(1000)])

        result = self.history('account')

        self.assertEqual(result['total_samples'], 1000)
        self.assertLessEqual(result['points_count'], 300)
        self.assertEqual(self.history('missing')['account_total'], [])


if __name__ == '__main__':
    unittest.main()
