<?php
require_once __DIR__ . '/lifecycle_helpers.php';
// Reject an unprivileged panel include before deploying or changing any files.
if (PHP_SAPI !== 'cli' || !function_exists('posix_geteuid') || posix_geteuid() !== 0) {
    uniselv_lifecycle_fail('Installer requires root CLI execution; activate through the privileged Webuzo dispatcher');
}

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

@mkdir($agent_dir, 0755, true);
@chmod($agent_dir, 0755);
@mkdir($agent_dir . '/agent', 0755, true);
@mkdir($lib_dir, 0750, true);
@mkdir($run_dir, 0750, true);
foreach ([$agent_dir . '/agent', $lib_dir, $run_dir] as $dir) {
    if (!is_dir($dir) || is_link($dir)) uniselv_lifecycle_fail('Unsafe or unwritable directory ' . $dir);
}

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
        if (is_file($src_agent . '/' . $f)) {
            uniselv_checked_copy($src_agent . '/' . $f, $agent_dir . '/agent/' . $f, 0755);
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
    if (!is_array($manifest_data)) uniselv_lifecycle_fail('Invalid ownership manifest');
    $manifest = $manifest_data;
}

$core_scripts = [
    'golden-shield.py' => '/usr/local/sbin/golden-shield.py',
    'webuzo-isolation.py' => '/usr/local/sbin/webuzo-isolation.py',
    'webuzo-session-guard.py' => '/usr/local/sbin/webuzo-session-guard.py',
    'webuzo-session-guard-manager.py' => '/usr/local/sbin/webuzo-session-guard-manager.py',
    'apache-fcgi-guard.py' => $agent_dir . '/core/apache-fcgi-guard.py',
    'protection-lifecycle.py' => $agent_dir . '/core/protection-lifecycle.py',
    'fpm_worker_tracker.php' => $agent_dir . '/core/fpm_worker_tracker.php'
];

if (is_dir($src_core)) {
    foreach ($core_scripts as $fname => $dest_path) {
        $src_file = $src_core . '/' . $fname;
        if (file_exists($src_file)) {
            uniselv_checked_copy($src_file, $agent_dir . '/core/' . $fname, ($fname === 'fpm_worker_tracker.php') ? 0755 : 0750);
            
            if (!in_array($fname, ['fpm_worker_tracker.php', 'apache-fcgi-guard.py', 'protection-lifecycle.py'])) {
                if (!file_exists($dest_path)) {
                    uniselv_checked_copy($src_file, $dest_path, 0750);
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
    uniselv_checked_json($manifest_file, $manifest);
}

// Do not report this release's proxy fixes active while preserving an older
// externally adopted implementation. Fresh installs copy the bundled code above.
$installed_isolation = '/usr/local/sbin/webuzo-isolation.py';
$bundled_isolation = $agent_dir . '/core/webuzo-isolation.py';
if (file_exists($installed_isolation) && file_exists($bundled_isolation) &&
    hash_file('sha256', $installed_isolation) !== hash_file('sha256', $bundled_isolation)) {
    echo "[UNISELV] INSTALLATION BLOCKED: Existing isolation implementation differs from this release. Preserve its backup and perform a reviewed maintenance upgrade before activation; adopted scripts are not silently overwritten.\n";
    exit(1);
}

// Global PHP-FPM Request Tracker Injection (cPanel CloudLinux Parity) with Reversible Manifest
$tracker_script = $agent_dir . '/core/fpm_worker_tracker.php';
$env_tracker = getenv('UNISELV_TRACKER_SCRIPT');
if ($env_tracker !== false && trim($env_tracker) !== '') {
    $tracker_script = trim($env_tracker);
}
$tracker_manifest_file = $lib_dir . '/php_tracker_manifest.json';
$env_manifest = getenv('UNISELV_MANIFEST_FILE');
if ($env_manifest !== false && trim($env_manifest) !== '') {
    $tracker_manifest_file = trim($env_manifest);
}
$tracker_manifest = [];
if (file_exists($tracker_manifest_file)) {
    $tracker_manifest = @json_decode(file_get_contents($tracker_manifest_file), true) ?: [];
}

function uniselv_extract_ini_directive_value($directive_line) {
    $parsed = @parse_ini_string($directive_line, false, INI_SCANNER_RAW);
    if ($parsed !== false && array_key_exists('auto_prepend_file', $parsed)) {
        $val = $parsed['auto_prepend_file'];
        if ($val === null || $val === false) {
            return '';
        }
        return trim($val, " \t\n\r\0\x0B\"'");
    }
    if (preg_match('/^[ \t]*auto_prepend_file[ \t]*=[ \t]*(?:"([^"]*)"|\'([^\']*)\'|([^;\r\n]*))/i', $directive_line, $m)) {
        if (isset($m[1]) && $m[1] !== '') {
            return $m[1];
        }
        if (isset($m[2]) && $m[2] !== '') {
            return $m[2];
        }
        if (isset($m[3])) {
            return trim($m[3], " \t\n\r\0\x0B\"'");
        }
    }
    return '';
}

function uniselv_atomic_persist_manifest($manifest_file, $manifest_data) {
    $dir = dirname($manifest_file);
    if (!is_dir($dir)) {
        @mkdir($dir, 0750, true);
    }
    $tmp_file = $manifest_file . '.tmp.' . uniqid() . '_' . getmypid();
    $payload = json_encode($manifest_data, JSON_PRETTY_PRINT);
    if ($payload === false) {
        return false;
    }
    $written = @file_put_contents($tmp_file, $payload);
    if ($written === false || $written < 5) {
        @unlink($tmp_file);
        return false;
    }
    @chmod($tmp_file, 0640);
    if (!@rename($tmp_file, $manifest_file)) {
        @unlink($tmp_file);
        return false;
    }
    $check = @file_get_contents($manifest_file);
    if ($check === false) {
        return false;
    }
    $decoded = @json_decode($check, true);
    return is_array($decoded);
}

if (file_exists($tracker_script)) {
    @chmod($tracker_script, 0755);
    @mkdir('/dev/shm/uniselv_fpm', 01777, true);
    @chmod('/dev/shm/uniselv_fpm', 01777);
    
    $chain_dir = '/usr/local/uniselv-resman/chains';
    if (!is_dir($chain_dir)) {
        @mkdir($chain_dir, 0755, true);
        @chmod($chain_dir, 0755);
    }

    $env_ini = getenv('UNISELV_INI_FILES');
    if ($env_ini !== false && trim($env_ini) !== '') {
        $php_inies = array_map('trim', explode(',', $env_ini));
    } else {
        $php_inies = array_unique(array_merge(
            glob('/usr/local/apps/php*/etc/php.ini') ?: [],
            glob('/etc/php/*/fpm/php.ini') ?: []
        ));
    }
    $reloaded_fpm = false;
    if (getenv('UNISELV_SKIP_FPM_RELOAD') === '1') {
        $reloaded_fpm = false;
    }
    $install_errors = [];

    foreach ($php_inies as $pini) {
        $ini_content = @file_get_contents($pini);
        if ($ini_content === false) continue;
        
        $pini_owner = @fileowner($pini);
        $pini_perms = @substr(sprintf('%o', fileperms($pini)), -4);

        if (strpos($ini_content, $tracker_script) === false) {
            $orig_raw = '';
            $orig_val = '';
            $third_party = null;
            $has_active = false;

            // Find all auto_prepend_file lines using PHP ini parsing semantics
            preg_match_all('/^[ \t]*(;?)[ \t]*auto_prepend_file[ \t]*=[ \t]*([^\r\n]*)/m', $ini_content, $matches, PREG_SET_ORDER | PREG_OFFSET_CAPTURE);

            $last_active_match = null;
            $first_commented_match = null;

            foreach ($matches as $m) {
                $is_comment = ($m[1][0] === ';');
                if (!$is_comment) {
                    $last_active_match = $m;
                } else if ($first_commented_match === null) {
                    $first_commented_match = $m;
                }
            }

            if ($last_active_match !== null) {
                // Active directive exists! Preserve it and chain it
                $has_active = true;
                $orig_raw = trim($last_active_match[0][0]);
                $val = uniselv_extract_ini_directive_value($last_active_match[0][0]);
                $orig_val = $val;

                if (!empty($val) && $val !== 'none' && $val !== 'off' && $val !== $tracker_script) {
                    $third_party = $val;
                    if (preg_match('/php(\d+)/', $pini, $pm)) {
                        $chain_file = $chain_dir . '/third_party_prepend_' . $pm[1] . '.php';
                        $safe_val = addslashes($val);
                        @file_put_contents($chain_file, "<?php\n// Chained third-party prepend registered by UNISELV Resource Manager\nif (file_exists('{$safe_val}') && is_readable('{$safe_val}')) {\n    require_once '{$safe_val}';\n}\n");
                        @chmod($chain_file, 0644);
                    }
                }

                // Replace ONLY the effective active directive; keep commented example lines intact!
                $offset = $last_active_match[0][1];
                $len = strlen($last_active_match[0][0]);
                $new_ini = substr($ini_content, 0, $offset) . "auto_prepend_file = {$tracker_script}" . substr($ini_content, $offset + $len);
            } else if ($first_commented_match !== null) {
                // Only commented directive exists; replace it
                $orig_raw = trim($first_commented_match[0][0]);
                $orig_val = '';
                $offset = $first_commented_match[0][1];
                $len = strlen($first_commented_match[0][0]);
                $new_ini = substr($ini_content, 0, $offset) . "auto_prepend_file = {$tracker_script}" . substr($ini_content, $offset + $len);
            } else {
                $orig_raw = ';auto_prepend_file =';
                $orig_val = '';
                $new_ini = $ini_content . "\n; UNISELV Resource Manager FastCGI Tracker\nauto_prepend_file = {$tracker_script}\n";
            }

            // Create durable backup of original ini before mutation
            $backup_dir = $lib_dir . '/backups';
            if (!is_dir($backup_dir)) {
                @mkdir($backup_dir, 0700, true);
            }
            $backup_path = $backup_dir . '/ini_' . md5($pini) . '_' . time() . '.bak';
            @copy($pini, $backup_path);

            // Record in manifest BEFORE writing mutated ini file to disk
            $tracker_manifest[$pini] = [
                'original_raw_line' => $orig_raw,
                'original_val' => $orig_val,
                'is_active' => $has_active,
                'third_party' => $third_party,
                'backup_path' => file_exists($backup_path) ? $backup_path : null,
                'installed_at' => time(),
                'owner_uid' => $pini_owner,
                'perms' => $pini_perms
            ];

            // CRITICAL: Atomic pre-mutation manifest persistence verification
            if (!uniselv_atomic_persist_manifest($tracker_manifest_file, $tracker_manifest)) {
                $install_errors[] = "Pre-mutation manifest persistence failed for {$pini}; mutation aborted";
                continue;
            }

            // Atomic transactional write via temporary file
            $tmp_ini = $pini . '.uniselv_tmp_' . uniqid();
            $written = @file_put_contents($tmp_ini, $new_ini);
            if ($written === false) {
                $install_errors[] = "Failed to write temp ini: {$tmp_ini}";
                continue;
            }
            if ($pini_perms) {
                @chmod($tmp_ini, octdec($pini_perms));
            }
            if ($pini_owner !== false) {
                @chown($tmp_ini, $pini_owner);
            }
            if (!@rename($tmp_ini, $pini)) {
                @unlink($tmp_ini);
                $install_errors[] = "Atomic rename failed for {$pini}";
                continue;
            }
            $reloaded_fpm = true;
        }
    }

    // Fail even when every mutation failed, so no reload/health-check branch was entered.
    if (!$reloaded_fpm && !empty($install_errors)) {
        foreach ($install_errors as $err) echo "[UNISELV] INSTALLATION BLOCKED: {$err}\n";
        exit(1);
    }
    // A failed final persistence check must also enter verified rollback after partial mutation.
    if (!uniselv_atomic_persist_manifest($tracker_manifest_file, $tracker_manifest)) {
        $install_errors[] = 'Final recovery manifest persistence failed';
        if (!$reloaded_fpm) {
            echo "[UNISELV] INSTALLATION BLOCKED: Final recovery manifest persistence failed\n";
            exit(1);
        }
    }

    if ($reloaded_fpm) {
        // Dynamic discovery of installed and active PHP-FPM services
        $reload_services = [];
        exec("systemctl list-unit-files --no-legend --type=service 'php*-fpm*.service' 'php-fpm*.service' 2>/dev/null", $unit_files);
        foreach ($unit_files as $line) {
            $parts = preg_split('/\s+/', trim($line));
            if (!empty($parts[0])) {
                $svc_name = $parts[0];
                exec("systemctl is-active " . escapeshellarg($svc_name) . " 2>/dev/null", $st_out, $st_code);
                if ($st_code === 0) {
                    $reload_services[] = $svc_name;
                }
            }
        }
        $reload_services = array_unique($reload_services);
        foreach ($reload_services as $svc) {
            $rc_out = [];
            $rc_code = 0;
            exec("systemctl reload " . escapeshellarg($svc) . " 2>&1", $rc_out, $rc_code);
            if ($rc_code !== 0) {
                exec("systemctl restart " . escapeshellarg($svc) . " 2>&1", $rc_out, $rc_code);
                if ($rc_code !== 0) {
                    $install_errors[] = "Failed reloading/restarting service {$svc}: " . implode(' ', $rc_out);
                }
            }
        }
        
        // Safety verification: execute a real script file on disk across all installed PHP versions (NOT -r)
        $tmp_cli = '/tmp/uniselv_install_health_' . uniqid() . '.php';
        @file_put_contents($tmp_cli, "<?php echo 'CLI_OK';\n");
        @chmod($tmp_cli, 0644);

        $php_bins = array_unique(array_merge(
            glob('/usr/local/apps/php*/bin/php') ?: [],
            ['/usr/bin/php']
        ));

        foreach ($php_bins as $bin) {
            if (file_exists($bin) && is_executable($bin)) {
                $vout = [];
                $vcode = 0;
                exec(escapeshellcmd($bin) . ' ' . escapeshellarg($tmp_cli) . ' 2>&1', $vout, $vcode);
                $vstr = implode("\n", $vout);
                if ($vcode !== 0 || strpos($vstr, 'CLI_OK') === false) {
                    $install_errors[] = "PHP binary {$bin} failed executing script (exit code {$vcode}): {$vstr}";
                }
            }
        }
        @unlink($tmp_cli);

        // Immediate verified rollback if any verification check fails
        if (!empty($install_errors)) {
            echo "[UNISELV] INSTALLATION BLOCKED: Post-configuration health check failed:\n";
            foreach ($install_errors as $err) {
                echo "  - {$err}\n";
            }
            echo "[UNISELV] Executing automatic rollback of all php.ini files...\n";
            $rollback_failed = false;
            foreach ($tracker_manifest as $pini => $meta) {
                if (file_exists($pini)) {
                    $cur = @file_get_contents($pini);
                    if ($cur !== false) {
                        $orig_line = $meta['original_raw_line'] ?? ';auto_prepend_file =';
                        $restored = preg_replace('/^[ \t]*auto_prepend_file[ \t]*=[ \t]*[' . chr(39) . chr(34) . ']?[ \t]*' . preg_quote($tracker_script, '/') . '[ \t]*[' . chr(39) . chr(34) . ']?[^\r\n]*/m', $orig_line, $cur);
                        $w = @file_put_contents($pini, $restored);
                        if ($w === false) {
                            $rollback_failed = true;
                            echo "[UNISELV] Rollback ERROR: Unwritable configuration on {$pini}\n";
                        } else {
                            $persisted = @file_get_contents($pini);
                            if ($persisted === false || strpos($persisted, $tracker_script) !== false) {
                                $rollback_failed = true;
                                echo "[UNISELV] Rollback ERROR: Verification failed for {$pini}\n";
                            }
                        }
                    }
                }
            }
            foreach ($reload_services as $svc) {
                $rc_out = [];
                $rc_code = 0;
                exec("systemctl reload " . escapeshellarg($svc) . " 2>&1 || systemctl restart " . escapeshellarg($svc) . " 2>&1", $rc_out, $rc_code);
                if ($rc_code !== 0) {
                    $rollback_failed = true;
                    echo "[UNISELV] Rollback ERROR: Failed reloading {$svc}: " . implode(' ', $rc_out) . "\n";
                }
            }
            if ($rollback_failed) {
                echo "[UNISELV] CRITICAL: Automatic rollback encountered errors! Recovery manifest and backups retained at {$tracker_manifest_file} for manual recovery.\n";
            } else {
                @unlink($tracker_manifest_file);
                if (is_dir($chain_dir)) {
                    @exec('rm -rf ' . escapeshellarg($chain_dir));
                }
                echo "[UNISELV] Rollback verified successfully. Installation aborted.\n";
            }
            exit(1);
        }
    }
}

$is_fixture_mode = (getenv('UNISELV_INI_FILES') !== false || getenv('UNISELV_FIXTURE_MODE') === '1');
if ($is_fixture_mode) {
    echo "[UNISELV] Notice: UNISELV fixture isolation mode active; skipping host daemon installation.\n";
    exit(0);
}

// Ship the same reversible Apache integration used by the application validation.
$apache_guard = $agent_dir . '/core/apache-fcgi-guard.py';
$apache_out = [];
exec('/usr/bin/python3 ' . escapeshellarg($apache_guard) . ' install 2>&1', $apache_out, $apache_rc);
if ($apache_rc !== 0) {
    echo "[UNISELV] INSTALLATION BLOCKED: Apache FastCGI integration failed: " . implode("\n", $apache_out) . "\n";
    exit(1);
}

if ($taskID && function_exists('task_update')) {
    task_update($taskID, 'Installing systemd service', 50);
}

// Copy systemd service unit
if (file_exists($agent_dir . '/agent/uniselv-resman-agent.service')) {
    uniselv_checked_copy($agent_dir . '/agent/uniselv-resman-agent.service', '/etc/systemd/system/uniselv-resman-agent.service', 0644);
    uniselv_checked_command('systemctl daemon-reload');
    uniselv_checked_command('systemctl enable uniselv-resman-agent.service');
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
    raise
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
uniselv_checked_command("python3 -c " . escapeshellarg($init_script));
@chmod($db_file, 0660);
@chown($db_file, 'root');
@chgrp($db_file, 'webuzo');

// Verify/install missing dependencies from the bundle; never invoke nonexistent CLI actions.
uniselv_checked_command('/usr/bin/python3 ' . escapeshellarg($agent_dir . '/core/protection-lifecycle.py') . ' install');
uniselv_checked_command('systemctl restart uniselv-resman-agent.service');
uniselv_checked_command('systemctl is-active --quiet uniselv-resman-agent.service');

if ($taskID && function_exists('task_update')) {
    task_update($taskID, 'Configuring Webuzo Nginx integration', 75);
}

// Refuse to overwrite unrelated files or links.
uniselv_checked_link(__DIR__ . '/admin_locations_uniselv-resman.conf', $base_path . '/conf/webuzo/emps/admin_locations_uniselv-resman.conf');
uniselv_checked_link(__DIR__ . '/enduser_locations_uniselv-resman.conf', $base_path . '/conf/webuzo/emps/enduser_locations_uniselv-resman.conf');
$web_admin_resman = $web_admin . '/uniselv-resman';
$web_enduser_resman = $web_enduser . '/uniselv-resman';
@mkdir($web_admin_resman, 0755, true);
if (!is_dir($web_admin_resman) || is_link($web_admin_resman)) uniselv_lifecycle_fail('Unsafe asset directory');
uniselv_checked_link(__DIR__ . '/images', $web_admin_resman . '/images');
uniselv_checked_link(__DIR__ . '/assets', $web_admin_resman . '/assets');
uniselv_checked_link($web_admin_resman, $web_enduser_resman);

if ($taskID && function_exists('task_update')) {
    task_update($taskID, 'Restarting Webuzo services', 90);
}

uniselv_reload_panel();

if ($taskID && function_exists('task_update')) {
    task_update($taskID, 'Activation Complete', 100);
}
