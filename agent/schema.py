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

CREATE TABLE IF NOT EXISTS openswoole_plan_policies (
    plan_name TEXT PRIMARY KEY,
    allowed INTEGER NOT NULL DEFAULT 1,
    max_workers_override INTEGER NOT NULL DEFAULT 0,
    max_task_workers_override INTEGER NOT NULL DEFAULT -1,
    updated_at INTEGER NOT NULL,
    updated_by TEXT NOT NULL DEFAULT 'admin'
);

CREATE TABLE IF NOT EXISTS openswoole_account_policies (
    username TEXT PRIMARY KEY,
    allowed INTEGER NOT NULL DEFAULT -1,
    max_workers_override INTEGER NOT NULL DEFAULT 0,
    max_task_workers_override INTEGER NOT NULL DEFAULT -1,
    updated_at INTEGER NOT NULL,
    updated_by TEXT NOT NULL DEFAULT 'admin'
);

CREATE TABLE IF NOT EXISTS managed_app_services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    uid INTEGER NOT NULL,
    service_type TEXT NOT NULL,
    service_slug TEXT NOT NULL,
    app_path TEXT NOT NULL,
    php_branch TEXT DEFAULT 'php84',
    runtime_bin TEXT DEFAULT '',
    workers INTEGER NOT NULL DEFAULT 1,
    max_memory_mb INTEGER NOT NULL DEFAULT 256,
    queues TEXT DEFAULT 'default',
    port INTEGER DEFAULT 0,
    enabled INTEGER NOT NULL DEFAULT 1,
    unit_name TEXT NOT NULL,
    last_status TEXT DEFAULT 'stopped',
    last_error TEXT DEFAULT '',
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL,
    UNIQUE(username, service_slug)
);

CREATE INDEX IF NOT EXISTS idx_managed_services_user ON managed_app_services(username);

CREATE TABLE IF NOT EXISTS account_port_allocations (
    username TEXT PRIMARY KEY,
    uid INTEGER NOT NULL,
    base_port INTEGER UNIQUE NOT NULL,
    port_count INTEGER NOT NULL DEFAULT 10,
    socket_dir TEXT NOT NULL,
    updated_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS redis_acl_accounts (
    username TEXT PRIMARY KEY,
    redis_user TEXT NOT NULL,
    key_prefix TEXT NOT NULL,
    password_hash TEXT DEFAULT '',
    password_plain_enc TEXT DEFAULT '',
    enabled INTEGER NOT NULL DEFAULT 1,
    max_commands_policy TEXT DEFAULT 'tenant_safe',
    updated_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS app_log_findings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    log_path TEXT NOT NULL,
    size_bytes INTEGER NOT NULL DEFAULT 0,
    mtime INTEGER NOT NULL DEFAULT 0,
    scanned_at INTEGER NOT NULL,
    UNIQUE(username, log_path)
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
            ('sample_count', 'INTEGER NOT NULL DEFAULT 1'),
            ('cpu_peak', 'REAL'),
            ('mem_peak', 'INTEGER'),
            ('read_peak', 'REAL'),
            ('write_peak', 'REAL'),
            ('iops_peak', 'REAL'),
            ('tasks_peak', 'INTEGER'),
            ('limit_io_read_bps', 'INTEGER DEFAULT 0'),
            ('limit_io_write_bps', 'INTEGER DEFAULT 0'),
            ('limit_io_read_iops', 'INTEGER DEFAULT 0'),
            ('limit_io_write_iops', 'INTEGER DEFAULT 0'),
        ]
        for col_name, col_def in migration_cols:
            if col_name not in existing_cols:
                cur.execute(f"ALTER TABLE samples ADD COLUMN {col_name} {col_def}")

        system_columns = {row[1] for row in cur.execute("PRAGMA table_info(system_metrics)")}
        if 'sample_count' not in system_columns:
            cur.execute("ALTER TABLE system_metrics ADD COLUMN sample_count INTEGER NOT NULL DEFAULT 1")
        cur.execute("UPDATE scheduled_reports SET status = 'generated', dispatched_to = NULL WHERE status = 'dispatched'")

        import time
        now = int(time.time())
        # Billing mappings are operator configuration. Never reseed demo mappings
        # on startup: doing so resurrected deleted entries after agent restart.

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
            ('brand_name', 'UNISELV Resource Manager'),
            ('brand_locale', 'en'),
            ('openswoole_auto_install_new_php', '1'),
            ('openswoole_enforcement_mode', 'enforce'),
            ('openswoole_strict_cgroup', '1'),
            ('openswoole_worker_rss_mib', '128'),
            ('openswoole_global_max_workers', '4'),
            ('openswoole_enable_coroutine', '1'),
            ('openswoole_preemptive_scheduler', '0'),
            ('openswoole_unixsock_buffer_size', '8388608'),
            ('openswoole_disabled_versions', ''),
            ('platform_runtime_containment', '1'),
            ('platform_runtime_mode', 'enforce'),
            ('platform_max_node_workers', '2'),
            ('platform_max_python_workers', '2'),
            ('platform_heavy_binary_guard', '1'),
            ('platform_heavy_binary_max_concurrent', '2'),
            ('platform_heavy_binary_max_sec', '300'),
            ('platform_log_threshold_mib', '250'),
            ('platform_log_auto_truncate', '0'),
            ('platform_redis_lock_default', '0'),
            ('platform_laravel_max_workers_cap', '4')
        ])
        conn.commit()
    finally:
        conn.close()

if __name__ == '__main__':
    import sys
    db = sys.argv[1] if len(sys.argv) > 1 else '/tmp/test-resman.sqlite'
    init_db(db)
    print(f"Database initialized at {db}")
