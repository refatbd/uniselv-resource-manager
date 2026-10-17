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

if ($taskID && function_exists('task_update')) {
    task_update($taskID, 'Removing Webuzo Nginx locations', 20);
}

// Delete the conf files we created
@unlink($base_path . '/conf/webuzo/emps/admin_locations_uniselv-resman.conf');
@unlink($base_path . '/conf/webuzo/emps/enduser_locations_uniselv-resman.conf');
@unlink($web_enduser . '/uniselv-resman');

if ($taskID && function_exists('task_update')) {
    task_update($taskID, 'Stopping background collection service', 50);
}

// Stop the agent service
exec('systemctl stop uniselv-resman-agent.service 2>/dev/null');

if ($taskID && function_exists('task_update')) {
    task_update($taskID, 'Cleaning web assets cache', 80);
}

@exec('rm -rf ' . escapeshellarg($web_admin . '/uniselv-resman'));

if ($taskID && function_exists('task_update')) {
    task_update($taskID, 'Restarting Webuzo service', 90);
}

if (function_exists('root_bg_exec')) {
    root_bg_exec('service webuzo restart');
} else {
    exec('service webuzo restart 2>/dev/null');
}

if ($taskID && function_exists('task_update')) {
    task_update($taskID, 'Deactivation Completed', 100);
}
