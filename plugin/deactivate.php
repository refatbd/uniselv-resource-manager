<?php
global $globals;

$taskID = null;
if (function_exists('task_get_current')) {
    $taskID = task_get_current();
}
if (empty($taskID) && function_exists('task_create')) {
    $label = function_exists('__') ? __('Deactivating UNISELV Resource Manager') : 'Deactivating UNISELV Resource Manager';
    $taskID = task_create('deactivating_uniselv_resman', $label);
    if (function_exists('task_start')) {
        task_start($taskID);
    }
}

$base_path = !empty($globals['path']) ? $globals['path'] : '/usr/local/webuzo';
$web_admin = $base_path . '/web/admin';
$web_enduser = $base_path . '/web/enduser';
$lib_dir = '/var/lib/uniselv-resource-manager';

require_once __DIR__ . '/lifecycle_helpers.php';
// Fixture mode limits the child to tracker restoration + real CLI/FPM verification.
uniselv_checked_command('UNISELV_FIXTURE_MODE=1 ' . escapeshellarg(is_executable('/usr/local/emps/bin/php') ? '/usr/local/emps/bin/php' : '/usr/local/bin/php') . ' ' . escapeshellarg(__DIR__ . '/uninstall.php'));

if ($taskID && function_exists('task_update')) {
    task_update($taskID, 'Removing Webuzo Nginx locations', 20);
}

// Delete the conf files we created
uniselv_remove_web_integration($base_path, $web_admin, $web_enduser, __DIR__);

if ($taskID && function_exists('task_update')) {
    task_update($taskID, 'Stopping background collection service', 50);
}

// Stop the agent service
uniselv_checked_command('systemctl stop uniselv-resman-agent.service');

if ($taskID && function_exists('task_update')) {
    task_update($taskID, 'Cleaning web assets cache', 80);
}

// Owned web links were removed above; unrelated files are retained.

if ($taskID && function_exists('task_update')) {
    task_update($taskID, 'Restarting Webuzo service', 90);
}

uniselv_reload_panel();

if ($taskID && function_exists('task_update')) {
    task_update($taskID, 'Deactivation Completed', 100);
}
