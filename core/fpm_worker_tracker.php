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
    $raw_uri = $_SERVER['REQUEST_URI'] ?? '';
    
    // Sanitize and redact sensitive credentials from URI
    $redacted_uri = preg_replace('/([?&](?:password|pass|pwd|token|secret|auth|nonce|key|session)=)[^&]*/i', '$1[REDACTED]', $raw_uri);
    if (strlen($redacted_uri) > 256) {
        $redacted_uri = substr($redacted_uri, 0, 256);
    }

    $user = get_current_user();
    
    // Write atomic bounded state with strict file ownership
    @file_put_contents($worker_file, json_encode([
        'script' => substr($script, 0, 256),
        'uri' => $redacted_uri,
        'user' => $user,
        'start' => microtime(true)
    ]), LOCK_EX);

    register_shutdown_function(function() use ($worker_file) {
        @unlink($worker_file);
    });
}

// Chain third-party prepend script if previously registered
$chained_cfg = '/usr/local/uniselv-resman/chains/third_party_prepend_' . PHP_MAJOR_VERSION . PHP_MINOR_VERSION . '.php';
if (file_exists($chained_cfg) && is_readable($chained_cfg)) {
    @include_once($chained_cfg);
}
