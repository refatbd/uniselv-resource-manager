<?php
global $globals;

// Get task ID for Webuzo task progress tracking
$taskID = null;
if (function_exists('task_get_current')) {
    $taskID = task_get_current();
}
if (empty($taskID) && function_exists('task_create')) {
    $label = function_exists('__') ? __('Activating UNISELV Resource Manager') : 'Activating UNISELV Resource Manager';
    $taskID = task_create('activating_uniselv_resman', $label);
    if (function_exists('task_start')) {
        task_start($taskID);
    }
}

if ($taskID && function_exists('task_update')) {
    task_update($taskID, 'Creating system directories', 10);
}

$base_path = !empty($globals['path']) ? $globals['path'] : '/usr/local/webuzo';
$web_admin = $base_path . '/web/admin';
$web_enduser = $base_path . '/web/enduser';

$agent_dir = '/usr/local/uniselv-resman';
$lib_dir = '/var/lib/uniselv-resource-manager';
$run_dir = '/run/uniselv-resman';

@mkdir($agent_dir . '/agent', 0755, true);
@mkdir($lib_dir, 0750, true);
@mkdir($run_dir, 0750, true);

// Set ownership
@chown($lib_dir, 'root');
@chgrp($lib_dir, 'webuzo');
@chown($run_dir, 'root');
@chgrp($run_dir, 'webuzo');

if ($taskID && function_exists('task_update')) {
    task_update($taskID, 'Deploying background agent files', 25);
}

// Copy agent files from plugin or bundled dir
$src_agent = __DIR__ . '/agent';
if (!is_dir($src_agent)) {
    $src_agent = dirname(__DIR__) . '/agent';
}

if (is_dir($src_agent)) {
    $files = scandir($src_agent);
    foreach ($files as $f) {
        if ($f !== '.' && $f !== '..') {
            copy($src_agent . '/' . $f, $agent_dir . '/agent/' . $f);
            chmod($agent_dir . '/agent/' . $f, 0755);
        }
    }
}

// Deploy bundled core protection scripts and establish ownership manifest
@mkdir($agent_dir . '/core', 0755, true);
@chmod($agent_dir . '/core', 0755);
$src_core = __DIR__ . '/core';
if (!is_dir($src_core)) {
    $src_core = dirname(__DIR__) . '/core';
}

$manifest_file = $lib_dir . '/ownership_manifest.json';
$manifest = [];
if (file_exists($manifest_file)) {
    $manifest_data = @json_decode(file_get_contents($manifest_file), true);
    if (is_array($manifest_data)) {
        $manifest = $manifest_data;
    }
}

$core_scripts = [
    'golden-shield.py' => '/usr/local/sbin/golden-shield.py',
    'webuzo-isolation.py' => '/usr/local/sbin/webuzo-isolation.py',
    'webuzo-session-guard.py' => '/usr/local/sbin/webuzo-session-guard.py',
    'webuzo-session-guard-manager.py' => '/usr/local/sbin/webuzo-session-guard-manager.py',
    'fpm_worker_tracker.php' => $agent_dir . '/core/fpm_worker_tracker.php'
];

if (is_dir($src_core)) {
    foreach ($core_scripts as $fname => $dest_path) {
        $src_file = $src_core . '/' . $fname;
        if (file_exists($src_file)) {
            copy($src_file, $agent_dir . '/core/' . $fname);
            chmod($agent_dir . '/core/' . $fname, ($fname === 'fpm_worker_tracker.php') ? 0755 : 0750);
            
            if ($fname !== 'fpm_worker_tracker.php') {
                if (!file_exists($dest_path)) {
                    copy($src_file, $dest_path);
                    chmod($dest_path, 0750);
                    chown($dest_path, 'root');
                    chgrp($dest_path, 'root');
                    $manifest[$fname] = [
                        'ownership' => 'plugin_installed',
                        'installed_at' => time(),
                        'sha256' => hash_file('sha256', $dest_path)
                    ];
                } else {
                    if (!isset($manifest[$fname])) {
                        $manifest[$fname] = [
                            'ownership' => 'adopted_external',
                            'adopted_at' => time(),
                            'sha256' => hash_file('sha256', $dest_path)
                        ];
                    }
                }
            }
        }
    }
    @file_put_contents($manifest_file, json_encode($manifest, JSON_PRETTY_PRINT));
    @chmod($manifest_file, 0640);
}

// Global PHP-FPM Request Tracker Injection (cPanel CloudLinux Parity)
$tracker_script = $agent_dir . '/core/fpm_worker_tracker.php';
if (file_exists($tracker_script)) {
    @chmod($tracker_script, 0755);
    @mkdir('/dev/shm/uniselv_fpm', 01777, true);
    @chmod('/dev/shm/uniselv_fpm', 01777);
    
    $php_inies = glob('/usr/local/apps/php*/etc/php.ini');
    $reloaded_fpm = false;
    foreach ($php_inies as $pini) {
        $ini_content = @file_get_contents($pini);
        if ($ini_content !== false && strpos($ini_content, $tracker_script) === false) {
            if (preg_match('/^(\s*;?\s*auto_prepend_file\s*=\s*)(.*)$/m', $ini_content, $m)) {
                $existing_val = trim($m[2]);
                if (empty($existing_val)) {
                    $new_ini = preg_replace('/^(\s*;?\s*auto_prepend_file\s*=\s*).*$/m', "auto_prepend_file = {$tracker_script}", $ini_content);
                    @file_put_contents($pini, $new_ini);
                    $reloaded_fpm = true;
                }
            } else {
                $ini_content .= "\n; UNISELV Resource Manager FastCGI Tracker\nauto_prepend_file = {$tracker_script}\n";
                @file_put_contents($pini, $ini_content);
                $reloaded_fpm = true;
            }
        }
    }
    if ($reloaded_fpm) {
        exec('systemctl reload wpiso-fpm-*.service 2>/dev/null || true');
        exec('systemctl reload php-fpm81.service php-fpm82.service 2>/dev/null || true');
    }
}

if ($taskID && function_exists('task_update')) {
    task_update($taskID, 'Installing systemd service', 50);
}

// Copy systemd service unit
if (file_exists($agent_dir . '/agent/uniselv-resman-agent.service')) {
    copy($agent_dir . '/agent/uniselv-resman-agent.service', '/etc/systemd/system/uniselv-resman-agent.service');
    chmod('/etc/systemd/system/uniselv-resman-agent.service', 0644);
    exec('systemctl daemon-reload');
    exec('systemctl enable uniselv-resman-agent.service');
    exec('systemctl restart uniselv-resman-agent.service');
}

if ($taskID && function_exists('task_update')) {
    task_update($taskID, 'Activating Golden Shield & Best-Practice Policies', 65);
}

// Initialize SQLite schema and seed best-practice defaults
$db_file = $lib_dir . '/resman.sqlite';
$init_script = "import sys, sqlite3
sys.path.insert(0, '$agent_dir/agent')
try:
    import schema
    schema.init_db('$db_file')
except Exception:
    pass
conn = sqlite3.connect('$db_file')
cur = conn.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)')

import os
cpus = os.cpu_count() or 4
def_load_thresh = str(round(cpus * 0.80, 2))
def_rec_thresh = str(round(cpus * 0.55, 2))

defaults = [
    ('telemetry_enabled', '1'),
    ('telemetry_interval', '5'),
    ('auto_prune_hourly', '1'),
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
    ('retention_samples_days', '30'),
    ('retention_snapshots_days', '14'),
    ('retention_events_days', '30'),
    ('retention_audit_days', '90'),
    ('retention_max_storage_mib', '100'),
    ('enable_runaway_watchdog', '1'),
    ('runaway_cpu_percent', '80'),
    ('runaway_max_duration_sec', '60'),
    ('watchdog_action', 'notify'),
    ('runaway_watchdog_kill_enabled', '0'),
    ('watchdog_require_account_saturation', '1'),
    ('watchdog_excluded_commands', 'mysqldump,tar,gzip,backup,composer,wp,ffmpeg'),
    ('enable_circuit_breaker', '1'),
    ('circuit_breaker_load_threshold', def_load_thresh),
    ('circuit_breaker_recovery_threshold', def_rec_thresh),
    ('report_schedule', 'daily'),
    ('report_recipient', 'system_admin'),
    ('brand_name', 'UNISELV Resource Manager'),
    ('brand_locale', 'en')
]
for k, v in defaults:
    cur.execute('INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)', (k, v))
conn.commit()
conn.close()
";
@exec("python3 -c " . escapeshellarg($init_script));
@chmod($db_file, 0660);
@chown($db_file, 'root');
@chgrp($db_file, 'webuzo');

// Automatically calculate and apply Golden Shield kernel limits & systemd drop-in
if (file_exists('/usr/local/sbin/golden-shield.py')) {
    @exec('python3 /usr/local/sbin/golden-shield.py apply 2>&1');
    @exec('python3 /usr/local/sbin/golden-shield.py write-systemd-dropin 2>&1');
    @exec('systemctl daemon-reload');
}

// Prepare cgroups for all existing Webuzo accounts
$users_dir = '/var/webuzo/users';
if (is_dir($users_dir) && file_exists('/usr/local/sbin/golden-shield.py')) {
    $u_entries = scandir($users_dir);
    foreach ($u_entries as $u) {
        if ($u !== '.' && $u !== '..') {
            $pw = @posix_getpwnam($u);
            if ($pw && isset($pw['uid'])) {
                @exec('python3 /usr/local/sbin/golden-shield.py prepare-account ' . intval($pw['uid']) . ' 2>&1');
            }
        }
    }
}

if ($taskID && function_exists('task_update')) {
    task_update($taskID, 'Configuring Webuzo Nginx integration', 75);
}

// Symlink Nginx location configs
@unlink($base_path . '/conf/webuzo/emps/admin_locations_uniselv-resman.conf');
@unlink($base_path . '/conf/webuzo/emps/enduser_locations_uniselv-resman.conf');
symlink(__DIR__ . '/admin_locations_uniselv-resman.conf', $base_path . '/conf/webuzo/emps/admin_locations_uniselv-resman.conf');
symlink(__DIR__ . '/enduser_locations_uniselv-resman.conf', $base_path . '/conf/webuzo/emps/enduser_locations_uniselv-resman.conf');

// Create web assets folders in /usr/local/webuzo/web/admin/uniselv-resman
$web_admin_resman = $web_admin . '/uniselv-resman';
$web_enduser_resman = $web_enduser . '/uniselv-resman';

@mkdir($web_admin_resman, 0755, true);
@unlink($web_admin_resman . '/images');
@unlink($web_admin_resman . '/assets');
@symlink(__DIR__ . '/images', $web_admin_resman . '/images');
@symlink(__DIR__ . '/assets', $web_admin_resman . '/assets');

@chown($web_admin_resman . '/images', 'webuzo');
@chgrp($web_admin_resman . '/images', 'webuzo');

@unlink($web_enduser_resman);
@symlink($web_admin_resman, $web_enduser_resman);

if ($taskID && function_exists('task_update')) {
    task_update($taskID, 'Restarting Webuzo services', 90);
}

if (function_exists('root_bg_exec')) {
    root_bg_exec('service webuzo restart');
} else {
    exec('service webuzo restart 2>/dev/null');
}

if ($taskID && function_exists('task_update')) {
    task_update($taskID, 'Activation Complete', 100);
}
