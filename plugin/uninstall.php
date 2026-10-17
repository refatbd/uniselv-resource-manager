<?php
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

// 1. Stop and disable systemd service
echo "[UNISELV] Stopping uniselv-resman-agent.service...\n";
exec('systemctl stop uniselv-resman-agent.service 2>/dev/null');
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
                @unlink($fpath);
            } else {
                echo "[UNISELV] Preserving externally adopted core script: {$fname}...\n";
            }
        }
    }
}

// 4. Remove Nginx configs and web links
echo "[UNISELV] Removing Webuzo EMPS Nginx configs...\n";
@unlink($base_path . '/conf/webuzo/emps/admin_locations_uniselv-resman.conf');
@unlink($base_path . '/conf/webuzo/emps/enduser_locations_uniselv-resman.conf');
@unlink($web_enduser . '/uniselv-resman');
@exec('rm -rf ' . escapeshellarg($web_admin . '/uniselv-resman'));

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
exec('service webuzo restart');

echo "[UNISELV] Uninstall complete.\n";
