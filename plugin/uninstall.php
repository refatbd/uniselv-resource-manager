<?php
require_once __DIR__ . '/lifecycle_helpers.php';
/**
 * UNISELV Resource Manager Uninstall & Reset
 * Supports clean removal, native settings restoration, and safe data handling.
 */

global $globals;

$purge_data = isset($argv) && in_array('--purge-data', $argv);
$base_path = !empty($globals['path']) ? $globals['path'] : '/usr/local/webuzo';
$web_admin = $base_path . '/web/admin';
$web_enduser = $base_path . '/web/enduser';

echo "[UNISELV] Initiating plugin uninstall...\n";

// Refuse changed plugin-owned implementations before touching PHP or services.
if (getenv('UNISELV_INI_FILES') === false && getenv('UNISELV_FIXTURE_MODE') !== '1') {
    $ownership_path = '/var/lib/uniselv-resource-manager/ownership_manifest.json';
    if (is_file($ownership_path)) {
        $ownership = json_decode(file_get_contents($ownership_path), true);
        if (!is_array($ownership)) uniselv_lifecycle_fail('Invalid ownership manifest; removal blocked');
        foreach ($ownership as $name => $meta) {
            if (($meta['ownership'] ?? '') !== 'plugin_installed') continue;
            if (!in_array($name, ['golden-shield.py', 'webuzo-isolation.py', 'webuzo-session-guard.py', 'webuzo-session-guard-manager.py'])) uniselv_lifecycle_fail('Unknown owned implementation ' . $name);
            $owned_file = '/usr/local/sbin/' . $name;
            if (is_file($owned_file) && hash_file('sha256', $owned_file) !== ($meta['sha256'] ?? '')) uniselv_lifecycle_fail('Owned implementation changed: ' . $name);
        }
    }
}

// 0. Cleanly restore PHP auto_prepend_file directives across installed PHP versions BEFORE removing files
echo "[UNISELV] Restoring PHP auto_prepend_file configuration across installed PHP versions...\n";
$lib_dir = '/var/lib/uniselv-resource-manager';

$env_manifest = getenv('UNISELV_MANIFEST_FILE');
$tracker_manifest_file = ($env_manifest !== false && trim($env_manifest) !== '') ? trim($env_manifest) : ($lib_dir . '/php_tracker_manifest.json');

$env_tracker = getenv('UNISELV_TRACKER_SCRIPT');
$tracker_script = ($env_tracker !== false && trim($env_tracker) !== '') ? trim($env_tracker) : '/usr/local/uniselv-resman/core/fpm_worker_tracker.php';

$env_inies = getenv('UNISELV_INI_FILES');
if ($env_inies !== false && trim($env_inies) !== '') {
    $all_inies = array_filter(array_map('trim', explode(',', $env_inies)));
} else {
    $all_inies = array_unique(array_merge(
        glob('/usr/local/apps/php*/etc/php.ini') ?: [],
        glob('/etc/php/*/fpm/php.ini') ?: [],
        glob('/etc/php/*/cli/php.ini') ?: []
    ));
}

$qc = chr(39) . chr(34);
$tracker_regex = '/^[ \t]*auto_prepend_file[ \t]*=[ \t]*[' . $qc . ']?[ \t]*' . preg_quote($tracker_script, '/') . '[ \t]*[' . $qc . ']?[^\r\n]*/m';

$restore_errors = [];
$reloaded_fpm = false;

// 1. Process manifest if present
if (file_exists($tracker_manifest_file)) {
    $raw_manifest = @file_get_contents($tracker_manifest_file);
    $tracker_manifest = @json_decode($raw_manifest, true);
    if (!is_array($tracker_manifest)) $restore_errors[] = 'Recovery manifest is invalid; implementation and backups must be retained for reviewed recovery';
    if (is_array($tracker_manifest)) {
        foreach ($tracker_manifest as $pini => $meta) {
            if (file_exists($pini)) {
                $cur = @file_get_contents($pini);
                if ($cur === false) {
                    $restore_errors[] = "Cannot read ini file: {$pini}";
                    continue;
                }
                if (preg_match($tracker_regex, $cur)) {
                    $orig_raw = trim($meta['original_raw_line'] ?? '');
                    if (empty($orig_raw) || strpos($orig_raw, $tracker_script) !== false) {
                        $orig_raw = ';auto_prepend_file =';
                    }
                    $restored = preg_replace($tracker_regex, $orig_raw, $cur);
                    if ($restored === null) {
                        $restore_errors[] = "Regex error restoring {$pini}";
                        continue;
                    }
                    $bytes = @file_put_contents($pini, $restored);
                    if ($bytes === false) {
                        $restore_errors[] = "Unwritable configuration: failed writing restored content to {$pini}";
                        continue;
                    }
                    // Verify persisted content
                    $persisted = @file_get_contents($pini);
                    if ($persisted === false || preg_match($tracker_regex, $persisted)) {
                        $restore_errors[] = "Verification failed: {$pini} still references tracker after write";
                        continue;
                    }
                    $reloaded_fpm = true;
                    echo "[UNISELV] Restored {$pini} to original directive: {$orig_raw}\n";
                }
            }
        }
    } else {
        echo "[UNISELV] Warning: tracker manifest was invalid JSON, using fallback scanner.\n";
    }
}

// 2. Global fallback scan: find ANY ini referencing tracker script (quoted or unquoted)
foreach ($all_inies as $pini) {
    if (!file_exists($pini)) continue;
    $cur = @file_get_contents($pini);
    if ($cur !== false && preg_match($tracker_regex, $cur)) {
        $restored = preg_replace($tracker_regex, ';auto_prepend_file =', $cur);
        if ($restored === null) {
            $restore_errors[] = "Regex error in fallback on {$pini}";
            continue;
        }
        $bytes = @file_put_contents($pini, $restored);
        if ($bytes === false) {
            $restore_errors[] = "Unwritable configuration in fallback: {$pini}";
            continue;
        }
        $persisted = @file_get_contents($pini);
        if ($persisted === false || preg_match($tracker_regex, $persisted)) {
            $restore_errors[] = "Fallback verification failed: {$pini} still contains tracker reference";
            continue;
        }
        $reloaded_fpm = true;
        echo "[UNISELV] Fallback: Reverted {$pini} auto_prepend_file to disabled.\n";
    }
}

// 3. Absolute assertion: Assert NO active php.ini on the entire system still references tracker
foreach ($all_inies as $pini) {
    if (!file_exists($pini)) continue;
    $chk = @file_get_contents($pini);
    if ($chk !== false && preg_match($tracker_regex, $chk)) {
        $restore_errors[] = "Unresolved tracker reference detected in {$pini}";
    }
}

// 4. Checked reload of FPM services
if ($reloaded_fpm) {
    if (getenv('UNISELV_SKIP_FPM_RELOAD') === '1') {
        echo "[UNISELV] Notice: UNISELV_SKIP_FPM_RELOAD set. Skipping service reload for fixture testing.\n";
    } else {
        echo "[UNISELV] Dynamically discovering and reloading active PHP-FPM pools...\n";
        // Reload native PHP bridges only; restarting internal coordinators/proxies
        // concurrently can kill syntax/admission checks and interrupt tenant traffic.
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
                    $restore_errors[] = "Failed reloading/restarting service {$svc} (exit code {$rc_code}): " . implode(' ', $rc_out);
                }
            }
        }
    }
}

// 5. Verification: Real script file execution across all installed PHP versions (NOT -r)
$tmp_test = '/tmp/uniselv_cli_health_' . uniqid() . '.php';
@file_put_contents($tmp_test, "<?php echo 'CLI_OK';\n");
@chmod($tmp_test, 0644);

$php_bins = array_unique(array_merge(
    glob('/usr/local/apps/php*/bin/php') ?: [],
    ['/usr/bin/php']
));

foreach ($php_bins as $bin) {
    if (file_exists($bin) && is_executable($bin)) {
        $vout = [];
        $vcode = 0;
        exec(escapeshellcmd($bin) . ' ' . escapeshellarg($tmp_test) . ' 2>&1', $vout, $vcode);
        $vstr = implode("\n", $vout);
        if ($vcode !== 0 || strpos($vstr, 'CLI_OK') === false) {
            $restore_errors[] = "PHP CLI binary {$bin} failed executing script file (exit code {$vcode}): {$vstr}";
        } else {
            echo "[UNISELV] Verified PHP CLI {$bin} executes script cleanly (exit code 0).\n";
        }
    }
}
@unlink($tmp_test);

// 6. Verification: Real tenant FPM execution with effective process identity
if (getenv('UNISELV_SKIP_TENANT_PROBE') === '1') {
    echo "[UNISELV] Notice: UNISELV_SKIP_TENANT_PROBE set. Skipping tenant FPM probe for fixture testing.\n";
} else {
    // Dynamic tenant pool discovery
    $targets = [];
    $env_probe_hosts = getenv('UNISELV_PROBE_HOSTS');
    if ($env_probe_hosts !== false && trim($env_probe_hosts) !== '') {
        foreach (explode(',', $env_probe_hosts) as $item) {
            $parts = explode(':', trim($item));
            if (count($parts) >= 3) {
                $targets[] = [
                    'host' => trim($parts[0]),
                    'docroot' => trim($parts[1]),
                    'uid' => intval(trim($parts[2]))
                ];
            }
        }
    } else {
        $vhost_files = array_unique(array_merge(
            glob('/usr/local/apps/apache*/etc/conf.d/*.conf') ?: [],
            glob('/etc/apache2/sites-enabled/*.conf') ?: [],
            glob('/etc/httpd/conf.d/*.conf') ?: [],
            glob('/etc/nginx/sites-enabled/*') ?: []
        ));

        foreach ($vhost_files as $vf) {
            $content = @file_get_contents($vf);
            if ($content === false) continue;
            
            if (preg_match_all('/<VirtualHost[^>]*>(.*?)<\/VirtualHost>/s', $content, $blocks)) {
                foreach ($blocks[1] as $blk) {
                    if (preg_match('/ServerName\s+([a-zA-Z0-9\.\-]+)/', $blk, $sn) &&
                        preg_match('/DocumentRoot\s+([^\s\r\n]+)/', $blk, $dr)) {
                        $domain = trim($sn[1]);
                        $docroot = trim($dr[1]);
                        if (is_dir($docroot) && is_writable($docroot)) {
                            $uid = @fileowner($docroot);
                            if ($uid !== false && $uid >= 1000) {
                                $targets[$domain] = [
                                    'host' => $domain,
                                    'docroot' => $docroot,
                                    'uid' => $uid
                                ];
                            }
                        }
                    }
                }
            }
        }
        $targets = array_values($targets);
    }

    if (empty($targets)) {
        echo "[UNISELV] Notice: No customer tenant pools/vhosts detected on this host. Skipping tenant probe.\n";
    } else {
        $server_ip_raw = exec("hostname -I 2>/dev/null");
        $server_ips = preg_split('/\s+/', trim($server_ip_raw));
        $server_ip = !empty($server_ips[0]) ? $server_ips[0] : '127.0.0.1';

        $tested_uids = [];
        foreach ($targets as $target) {
            if (in_array($target['uid'], $tested_uids)) continue;
            $tested_uids[] = $target['uid'];

            $token = bin2hex(random_bytes(16));
            $probe_name = 'uniselv_probe_' . uniqid() . '.php';
            $probe_file = $target['docroot'] . '/' . $probe_name;

            $probe_code = "<?php\nheader('Content-Type: application/json');\necho json_encode([\n    'status' => 'OK',\n    'token' => '{$token}',\n    'euid' => posix_geteuid(),\n    'uid' => getmyuid(),\n    'php_version' => PHP_VERSION\n]);\n";
            $written = @file_put_contents($probe_file, $probe_code);
            if ($written === false) {
                $restore_errors[] = "Failed to write tenant probe file to {$probe_file}";
                continue;
            }
            @chmod($probe_file, 0644);
            @chown($probe_file, $target['uid']);

            // A native PHP reload can briefly replace its listening socket. Await
            // bounded recovery; identity/payload mismatches still fail verification.
            for ($probe_attempt = 1; $probe_attempt <= 5; $probe_attempt++) {
                if (function_exists('curl_init')) {
                    $ch = curl_init("http://{$server_ip}/{$probe_name}");
                    curl_setopt($ch, CURLOPT_HTTPHEADER, ["Host: {$target['host']}"]);
                    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
                    curl_setopt($ch, CURLOPT_TIMEOUT, 6);
                    $raw_resp = curl_exec($ch);
                    $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
                    $curl_err = curl_error($ch);
                    curl_close($ch);
                } else {
                    // Lifecycle must also work with PHP -n or a missing PHP cURL module.
                    $response_file = tempnam(sys_get_temp_dir(), 'resman-http-');
                    $error_file = tempnam(sys_get_temp_dir(), 'resman-http-');
                    $http_code = 0; $raw_resp = ''; $curl_err = 'Cannot allocate HTTP verification files';
                    if ($response_file !== false && $error_file !== false) {
                        $out = []; $rc = 1;
                        exec('/usr/bin/curl --max-time 6 -sS -o ' . escapeshellarg($response_file) . ' -w ' . escapeshellarg('%{http_code}') . ' -H ' . escapeshellarg('Host: ' . $target['host']) . ' ' . escapeshellarg("http://{$server_ip}/{$probe_name}") . ' 2>' . escapeshellarg($error_file), $out, $rc);
                        $http_code = intval(implode('', $out));
                        $raw_resp = file_get_contents($response_file);
                        $curl_err = $rc === 0 ? '' : ('curl exit ' . $rc . ': ' . file_get_contents($error_file));
                    }
                    if ($response_file !== false) @unlink($response_file);
                    if ($error_file !== false) @unlink($error_file);
                }
                if (empty($curl_err) && !in_array($http_code, [0, 502, 503, 504], true)) break;
                if ($probe_attempt < 5) usleep(500000);
            }
            if ($probe_attempt > 1) echo "[UNISELV] Notice: Tenant HTTP verification awaited reload recovery ({$probe_attempt} attempts).\n";
            @unlink($probe_file);

            if (!empty($curl_err)) {
                $restore_errors[] = "Tenant FPM probe transport failure for {$target['host']}: {$curl_err}";
            } else if ($http_code !== 200) {
                $restore_errors[] = "Tenant FPM probe for {$target['host']} returned HTTP {$http_code} (expected 200)";
            } else {
                $parsed = @json_decode($raw_resp, true);
                if (!is_array($parsed) || ($parsed['status'] ?? '') !== 'OK' || ($parsed['token'] ?? '') !== $token) {
                    $restore_errors[] = "Tenant FPM probe for {$target['host']} returned unexpected payload: " . substr($raw_resp, 0, 200);
                } else if (intval($parsed['euid'] ?? -1) !== intval($target['uid'])) {
                    $restore_errors[] = "Tenant FPM probe for {$target['host']} effective UID mismatch: expected {$target['uid']}, got " . ($parsed['euid'] ?? 'null');
                } else {
                    echo "[UNISELV] Verified tenant FPM probe for {$target['host']} (PHP {$parsed['php_version']}, EUID {$parsed['euid']}) returned HTTP 200 OK.\n";
                }
            }

            if (count($tested_uids) >= 2) break;
        }
    }
}

// 7. CRITICAL GATE: Halt deletion if ANY errors occurred!
if (!empty($restore_errors)) {
    echo "[UNISELV] CRITICAL: Pre-deletion verification failed! Halting tracker deletion to prevent server downtime:\n";
    foreach ($restore_errors as $err) {
        echo "  - {$err}\n";
    }
    echo "[UNISELV] Recovery assets in {$tracker_script} and manifest are preserved.\n";
    exit(1);
}

echo "[UNISELV] All pre-deletion verifications passed. Proceeding with file cleanup.\n";

$is_fixture_mode = (getenv('UNISELV_INI_FILES') !== false || getenv('UNISELV_FIXTURE_MODE') === '1');
if ($is_fixture_mode) {
    echo "[UNISELV] Notice: UNISELV fixture isolation mode active; skipping destructive host systemd/service cleanup.\n";
    exit(0);
}

// Remove chains directory if present
$protection_lifecycle = '/usr/local/uniselv-resman/core/protection-lifecycle.py';
if (is_file($protection_lifecycle)) uniselv_checked_command('/usr/bin/python3 ' . escapeshellarg($protection_lifecycle) . ' uninstall');

$apache_guard = '/usr/local/uniselv-resman/core/apache-fcgi-guard.py';
if (file_exists($apache_guard)) {
    $apache_out = [];
    exec('/usr/bin/python3 ' . escapeshellarg($apache_guard) . ' uninstall 2>&1', $apache_out, $apache_rc);
    if ($apache_rc !== 0) {
        echo "[UNISELV] Removal blocked: Apache recovery failed: " . implode("\n", $apache_out) . "\n";
        exit(1);
    }
}
if (is_dir('/usr/local/uniselv-resman/chains')) {
    @exec('rm -rf /usr/local/uniselv-resman/chains');
}

// Clean /dev/shm tracker directory
@exec('rm -rf /dev/shm/uniselv_fpm');

// 1. Stop and disable systemd service
echo "[UNISELV] Stopping uniselv-resman-agent.service...\n";
uniselv_checked_command('systemctl stop uniselv-resman-agent.service');
exec('systemctl disable uniselv-resman-agent.service 2>/dev/null');

if (file_exists('/etc/systemd/system/uniselv-resman-agent.service')) {
    @unlink('/etc/systemd/system/uniselv-resman-agent.service');
    exec('systemctl daemon-reload');
}

// 2. Remove systemd drop-in override for golden.slice if managed by UNISELV
$dropin_file = '/etc/systemd/system/golden.slice.d/50-uniselv-limits.conf';
if (file_exists($dropin_file)) {
    echo "[UNISELV] Removing systemd drop-in override...\n";
    @unlink($dropin_file);
    @rmdir('/etc/systemd/system/golden.slice.d');
    exec('systemctl daemon-reload');
}

// 3. Process ownership manifest for /usr/local/sbin scripts
$lib_dir = '/var/lib/uniselv-resource-manager';
$manifest_file = $lib_dir . '/ownership_manifest.json';
if (file_exists($manifest_file)) {
    $manifest = @json_decode(file_get_contents($manifest_file), true);
    if (is_array($manifest)) {
        foreach ($manifest as $fname => $meta) {
            $fpath = '/usr/local/sbin/' . $fname;
            if (isset($meta['ownership']) && $meta['ownership'] === 'plugin_installed') {
                echo "[UNISELV] Removing plugin-installed core script: {$fname}...\n";
                if (is_file($fpath) && hash_file('sha256', $fpath) !== ($meta['sha256'] ?? '')) uniselv_lifecycle_fail('Owned implementation changed; refusing removal: ' . $fpath);
                if (file_exists($fpath) && !@unlink($fpath)) uniselv_lifecycle_fail('Cannot remove owned implementation ' . $fpath);
            } else {
                echo "[UNISELV] Preserving externally adopted core script: {$fname}...\n";
            }
        }
    }
}

// 4. Remove Nginx configs and web links
echo "[UNISELV] Removing Webuzo EMPS Nginx configs...\n";
uniselv_remove_web_integration($base_path, $web_admin, $web_enduser, __DIR__);

// 5. Remove agent directory
echo "[UNISELV] Removing agent binary directory...\n";
@exec('rm -rf /usr/local/uniselv-resman');

// 6. Data handling
if ($purge_data) {
    echo "[UNISELV] Purging historical database and manifests...\n";
    @exec('rm -rf /var/lib/uniselv-resource-manager');
    @unlink('/etc/golden-shield/mode.json');
} else {
    echo "[UNISELV] Preserving historical database in /var/lib/uniselv-resource-manager\n";
}

// 7. Clean runtime sockets
@unlink('/run/uniselv-resman/agent.sock');
@rmdir('/run/uniselv-resman');

// 6. Restart Webuzo
echo "[UNISELV] Restarting Webuzo...\n";
uniselv_reload_panel();

echo "[UNISELV] Uninstall complete.\n";
