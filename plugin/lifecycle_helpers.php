<?php
// Fail closed and retain recovery artifacts when any lifecycle stage fails.
function uniselv_lifecycle_fail($message) {
    echo "[UNISELV] LIFECYCLE FAILED: " . $message . ". Recovery files retained; review before retry.\n";
    exit(1);
}
function uniselv_checked_copy($source, $dest, $mode = 0755) {
    if (!is_file($source) || is_link($dest) || is_dir($dest)) uniselv_lifecycle_fail('Unsafe or missing deployment file: ' . $dest);
    $tmp = $dest . '.resman-stage-' . getmypid();
    if (!@copy($source, $tmp) || !@chmod($tmp, $mode) || hash_file('sha256', $source) !== @hash_file('sha256', $tmp) || !@rename($tmp, $dest)) {
        @unlink($tmp); uniselv_lifecycle_fail('Cannot deploy ' . $dest);
    }
}
function uniselv_checked_command($command) {
    $output = []; exec($command . ' 2>&1', $output, $rc);
    if ($rc !== 0) uniselv_lifecycle_fail('Command exit ' . $rc . ': ' . implode("\n", $output));
}
function uniselv_checked_json($path, $data) {
    $temp = $path . '.resman-stage-' . getmypid();
    $json = json_encode($data, JSON_PRETTY_PRINT);
    if ($json === false || @file_put_contents($temp, $json) !== strlen($json) || !@chmod($temp, 0640) || !@rename($temp, $path)) {
        @unlink($temp); uniselv_lifecycle_fail('Cannot persist recovery/ownership manifest ' . $path);
    }
    if (@file_get_contents($path) !== $json) uniselv_lifecycle_fail('Manifest verification failed ' . $path);
}
function uniselv_checked_link($target, $dest) {
    if (is_link($dest)) {
        if (readlink($dest) === $target) return;
        uniselv_lifecycle_fail('Existing unowned integration link: ' . $dest);
    }
    if (file_exists($dest) || !@symlink($target, $dest)) uniselv_lifecycle_fail('Cannot create owned integration link ' . $dest);
}
function uniselv_reload_panel() {
    $nginx = '/usr/local/emps/sbin/nginx';
    if (!is_executable($nginx)) uniselv_lifecycle_fail('Supported Webuzo EMPS nginx was not found');
    uniselv_checked_command(escapeshellarg($nginx) . ' -t');
    uniselv_checked_command(escapeshellarg($nginx) . ' -s reload');
}

function uniselv_remove_owned_link($target, $dest) {
    if (!file_exists($dest) && !is_link($dest)) return;
    if (!is_link($dest) || readlink($dest) !== $target) uniselv_lifecycle_fail('Refusing unowned integration path ' . $dest);
    if (!@unlink($dest)) uniselv_lifecycle_fail('Cannot remove owned integration link ' . $dest);
}
function uniselv_remove_web_integration($base, $admin, $enduser, $source) {
    uniselv_remove_owned_link($source . '/admin_locations_uniselv-resman.conf', $base . '/conf/webuzo/emps/admin_locations_uniselv-resman.conf');
    uniselv_remove_owned_link($source . '/enduser_locations_uniselv-resman.conf', $base . '/conf/webuzo/emps/enduser_locations_uniselv-resman.conf');
    $assets = $admin . '/uniselv-resman';
    uniselv_remove_owned_link($assets, $enduser . '/uniselv-resman');
    uniselv_remove_owned_link($source . '/images', $assets . '/images');
    uniselv_remove_owned_link($source . '/assets', $assets . '/assets');
    if (is_dir($assets) && !@rmdir($assets)) uniselv_lifecycle_fail('Unexpected files remain in plugin web folder; preserved for review');
}

function uniselv_sync_default_php_symlinks(): array {
    global $globals;
    $default_ver = null;
    if (!empty($globals['WU_DEFAULT_PHP']) && preg_match('/^php\d{2,3}$/', $globals['WU_DEFAULT_PHP'])) {
        $default_ver = $globals['WU_DEFAULT_PHP'];
    }
    if (!$default_ver && file_exists('/usr/local/webuzo/universal.php')) {
        $c = @file_get_contents('/usr/local/webuzo/universal.php');
        if ($c && preg_match("/\\\$globals\['WU_DEFAULT_PHP'\]\s*=\s*['\"](php\d{2,3})['\"];/", $c, $m)) {
            $default_ver = $m[1];
        }
    }
    if (!$default_ver) {
        $installed = glob('/usr/local/apps/php*/bin/php') ?: [];
        rsort($installed);
        if (!empty($installed) && preg_match('#/usr/local/apps/(php\d{2,3})/bin/php#', $installed[0], $m)) {
            $default_ver = $m[1];
        }
    }
    if (!$default_ver) {
        return ['success' => false, 'error' => 'No default PHP version found'];
    }

    $source_dir = "/usr/local/apps/{$default_ver}/bin";
    $bin_dirs = ['/usr/local/bin', '/usr/bin'];
    $binaries = ['php', 'php-cgi', 'phar', 'phar.phar', 'phpize', 'php-config'];
    $synced = [];

    foreach ($binaries as $bin) {
        $source_file = "{$source_dir}/{$bin}";
        if (!is_file($source_file) || !is_executable($source_file)) {
            continue;
        }
        foreach ($bin_dirs as $dest_dir) {
            if (!is_dir($dest_dir)) {
                @mkdir($dest_dir, 0755, true);
            }
            $dest_file = "{$dest_dir}/{$bin}";
            if (is_link($dest_file) && @readlink($dest_file) === $source_file) {
                $synced[] = $dest_file;
                continue;
            }
            $tmp = "{$dest_dir}/{$bin}.uniselv-tmp." . getmypid();
            @unlink($tmp);
            if (@symlink($source_file, $tmp)) {
                if (!@rename($tmp, $dest_file)) {
                    @unlink($dest_file);
                    @symlink($source_file, $dest_file);
                }
                @unlink($tmp);
                $synced[] = $dest_file;
            } else {
                @unlink($dest_file);
                if (@symlink($source_file, $dest_file)) {
                    $synced[] = $dest_file;
                }
            }
        }
    }
    return ['success' => true, 'version' => $default_ver, 'synced' => $synced];
}
