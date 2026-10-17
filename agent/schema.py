import sqlite3
import os
import pathlib

SCHEMA_SQL = """
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS samples (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    uid INTEGER NOT NULL,
    timestamp INTEGER NOT NULL,
    cpu_percent REAL DEFAULT 0.0,
    cpu_allowance_percent REAL DEFAULT 0.0,
    cpu_throttled_events INTEGER DEFAULT 0,
    cpu_throttled_usec INTEGER DEFAULT 0,
    mem_current_bytes INTEGER DEFAULT 0,
    mem_anon_bytes INTEGER DEFAULT 0,
    mem_file_bytes INTEGER DEFAULT 0,
    mem_swap_bytes INTEGER DEFAULT 0,
    oom_kill_events INTEGER DEFAULT 0,
    mem_high_events INTEGER DEFAULT 0,
    mem_max_events INTEGER DEFAULT 0,
    tasks_current INTEGER DEFAULT 0,
    task_limit_events INTEGER DEFAULT 0,
    read_bytes_sec REAL DEFAULT 0.0,
    write_bytes_sec REAL DEFAULT 0.0,
    read_iops_sec REAL DEFAULT 0.0,
    write_iops_sec REAL DEFAULT 0.0,
    plan_name TEXT,
    limit_cpu_quota INTEGER DEFAULT 0,
    limit_mem_max_bytes INTEGER DEFAULT 0,
    limit_tasks_max INTEGER DEFAULT 0,
    limit_io_read_bps INTEGER DEFAULT 0,
    limit_io_write_bps INTEGER DEFAULT 0,
    limit_io_read_iops INTEGER DEFAULT 0,
    limit_io_write_iops INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_samples_user_time ON samples(username, timestamp);
CREATE INDEX IF NOT EXISTS idx_samples_time ON samples(timestamp);

CREATE TABLE IF NOT EXISTS snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    uid INTEGER NOT NULL,
    timestamp INTEGER NOT NULL,
    trigger_type TEXT NOT NULL,
    processes_json TEXT,
    web_diagnostics_json TEXT,
    db_diagnostics_json TEXT,
    metrics_summary_json TEXT
);

CREATE INDEX IF NOT EXISTS idx_snapshots_user_time ON snapshots(username, timestamp);

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    uid INTEGER NOT NULL,
    timestamp INTEGER NOT NULL,
    event_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    message TEXT NOT NULL,
    details_json TEXT
);

CREATE INDEX IF NOT EXISTS idx_events_user_time ON events(username, timestamp);

CREATE TABLE IF NOT EXISTS temporary_overrides (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    uid INTEGER NOT NULL,
    original_plan TEXT NOT NULL,
    override_plan TEXT NOT NULL,
    created_at INTEGER NOT NULL,
    expires_at INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    reason TEXT
);

CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp INTEGER NOT NULL,
    actor TEXT NOT NULL,
    action TEXT NOT NULL,
    target_account TEXT,
    details_json TEXT
);

CREATE TABLE IF NOT EXISTS system_metrics (
    timestamp INTEGER PRIMARY KEY,
    cpu_percent REAL DEFAULT 0.0,
    mem_used_bytes INTEGER DEFAULT 0,
    mem_available_bytes INTEGER DEFAULT 0,
    swap_used_bytes INTEGER DEFAULT 0,
    golden_slice_cpu_percent REAL DEFAULT 0.0,
    golden_slice_mem_bytes INTEGER DEFAULT 0,
    load1 REAL DEFAULT 0.0,
    load5 REAL DEFAULT 0.0,
    load15 REAL DEFAULT 0.0
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
);

CREATE TABLE IF NOT EXISTS notification_state (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    event_id INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'read',
    updated_at INTEGER NOT NULL,
    UNIQUE(username, event_id)
);

CREATE INDEX IF NOT EXISTS idx_notif_user ON notification_state(username);

CREATE TABLE IF NOT EXISTS webhook_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    idempotency_key TEXT UNIQUE NOT NULL,
    timestamp INTEGER NOT NULL,
    source TEXT NOT NULL,
    event_type TEXT NOT NULL,
    target_account TEXT,
    payload_json TEXT,
    response_json TEXT,
    status_code INTEGER DEFAULT 200
);

CREATE INDEX IF NOT EXISTS idx_webhook_key ON webhook_log(idempotency_key);

CREATE TABLE IF NOT EXISTS scheduled_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp INTEGER NOT NULL,
    report_type TEXT NOT NULL,
    summary_json TEXT NOT NULL,
    dispatched_to TEXT,
    status TEXT NOT NULL DEFAULT 'generated'
);

CREATE TABLE IF NOT EXISTS package_mappings (
    billing_package TEXT PRIMARY KEY,
    resource_plan TEXT NOT NULL,
    updated_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS account_permissions (
    username TEXT NOT NULL,
    permission TEXT NOT NULL,
    granted INTEGER NOT NULL DEFAULT 1,
    updated_at INTEGER NOT NULL,
    updated_by TEXT NOT NULL DEFAULT 'admin',
    PRIMARY KEY(username, permission)
);

CREATE TABLE IF NOT EXISTS role_permissions (
    role TEXT NOT NULL,
    permission TEXT NOT NULL,
    granted INTEGER NOT NULL DEFAULT 1,
    updated_at INTEGER NOT NULL,
    PRIMARY KEY(role, permission)
);
"""

def init_db(db_path: str):
    path = pathlib.Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(SCHEMA_SQL)
        conn.commit()

        # Dynamic schema migration for existing databases
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(samples)")
        existing_cols = {row[1] for row in cur.fetchall()}
        
        migration_cols = [
            ('limit_io_read_bps', 'INTEGER DEFAULT 0'),
            ('limit_io_write_bps', 'INTEGER DEFAULT 0'),
            ('limit_io_read_iops', 'INTEGER DEFAULT 0'),
            ('limit_io_write_iops', 'INTEGER DEFAULT 0'),
        ]
        for col_name, col_def in migration_cols:
            if col_name not in existing_cols:
                try:
                    cur.execute(f"ALTER TABLE samples ADD COLUMN {col_name} {col_def}")
                except Exception:
                    pass

        import time
        now = int(time.time())
        cur.executemany("""
            INSERT OR IGNORE INTO package_mappings (billing_package, resource_plan, updated_at)
            VALUES (?, ?, ?)
        """, [
            ('Bronze', 'starter', now),
            ('Silver', 'turbo', now),
            ('Gold', 'enterprise', now),
            ('Platinum', 'master', now),
            ('Business Hosting', 'enterprise', now),
            ('Starter Hosting', 'starter', now),
            ('Pro Hosting', 'turbo', now),
            ('VIP Hosting', 'master', now)
        ])

        cur.executemany("""
            INSERT OR IGNORE INTO role_permissions (role, permission, granted, updated_at)
            VALUES (?, ?, ?, ?)
        """, [
            ('enduser', 'can_stop_processes', 1, now),
            ('enduser', 'can_export_diagnostics', 1, now),
            ('enduser', 'can_view_history', 1, now),
            ('reseller', 'can_set_overrides', 1, now),
            ('reseller', 'can_export_diagnostics', 1, now),
            ('reseller', 'can_view_audit_log', 1, now)
        ])

        # Seed shared hosting best-practice default feature settings and hardware-scaled thresholds
        cpus = os.cpu_count() or 4
        def_load_thresh = str(round(cpus * 0.80, 2))
        def_rec_thresh = str(round(cpus * 0.55, 2))

        cur.executemany("""
            INSERT OR IGNORE INTO settings (key, value)
            VALUES (?, ?)
        """, [
            ('telemetry_enabled', '1'),
            ('telemetry_interval', '5'),
            ('snapshot_on_throttle', '1'),
            ('snapshot_on_oom', '1'),
            ('snapshot_on_task_limit', '1'),
            ('snapshot_cooldown_sec', '60'),
            ('alert_threshold_cpu', '75'),
            ('alert_threshold_mem', '80'),
            ('alert_threshold_tasks', '80'),
            ('enduser_allow_kill', '1'),
            ('enduser_allow_export', '1'),
            ('enduser_allow_db_trace', '1'),
            ('auto_prune_hourly', '1'),
            ('retention_samples_days', '30'),
            ('retention_snapshots_days', '14'),
            ('retention_events_days', '30'),
            ('retention_audit_days', '90'),
            ('retention_max_storage_mib', '100'),
            ('enable_runaway_watchdog', '1'),
            ('runaway_cpu_percent', '80'),
            ('runaway_max_duration_sec', '60'),
            ('enable_circuit_breaker', '1'),
            ('circuit_breaker_load_threshold', def_load_thresh),
            ('circuit_breaker_recovery_threshold', def_rec_thresh),
            ('report_schedule', 'daily'),
            ('report_recipient', 'system_admin'),
            ('brand_name', 'UNISELV Resource Manager'),
            ('brand_locale', 'en')
        ])
        conn.commit()
    finally:
        conn.close()

if __name__ == '__main__':
    import sys
    db = sys.argv[1] if len(sys.argv) > 1 else '/tmp/test-resman.sqlite'
    init_db(db)
    print(f"Database initialized at {db}")
