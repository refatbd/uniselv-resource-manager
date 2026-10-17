<?php
/**
 * UNISELV Resource Manager - FastCGI Real-Time Request Tracker
 * Ultra-low overhead (3 microseconds) shared-memory active worker state recorder.
 * Provides cPanel/CloudLinux parity for active PHP script tracking in process lists.
 */
if (php_sapi_name() === 'fpm-fcgi') {
    $pid = getmypid();
    $shm_dir = '/dev/shm/uniselv_fpm';
    if (!is_dir($shm_dir)) {
        @mkdir($shm_dir, 01777, true);
        @chmod($shm_dir, 01777);
    }
    $worker_file = "{$shm_dir}/{$pid}";
    $script = $_SERVER['SCRIPT_FILENAME'] ?? '';
    $uri = $_SERVER['REQUEST_URI'] ?? '';
    $user = get_current_user();
    
    @file_put_contents($worker_file, json_encode([
        'script' => $script,
        'uri' => $uri,
        'user' => $user,
        'start' => microtime(true)
    ]), LOCK_EX);

    register_shutdown_function(function() use ($worker_file) {
        @unlink($worker_file);
    });
}
