<?php
/**
 * UNISELV Resource Manager IPC Client
 * Connects securely to the local privileged background agent over UNIX domain socket.
 */

class UniselvApiClient {
    private static $socket_path = '/run/uniselv-resman/agent.sock';
    private static $token_path  = '/run/uniselv-resman/broker.token';

    public static function call($action, $params = [], $auth_user = '', $is_admin = false, $timeout = 15) {
        if (!file_exists(self::$socket_path)) {
            return [
                'error' => 'UNISELV Resource Manager agent is not running. Service uniselv-resman-agent is inactive.'
            ];
        }

        $broker_token = '';
        if (file_exists(self::$token_path)) {
            $broker_token = trim(@file_get_contents(self::$token_path));
        }

        $payload = [
            'action' => $action,
            'broker_token' => $broker_token,
            'auth' => [
                'user' => (string)$auth_user,
                'is_admin' => (bool)$is_admin
            ],
            'params' => (array)$params
        ];

        $json_data = json_encode($payload) . "\n";

        $socket = @fsockopen('unix://' . self::$socket_path, -1, $errno, $errstr, 5.0);
        if (!$socket) {
            return [
                'error' => "Failed to connect to agent socket ($errno): $errstr"
            ];
        }

        $stream_timeout = max(5, min(120, intval($timeout)));
        stream_set_timeout($socket, $stream_timeout);
        fwrite($socket, $json_data);

        $response = '';
        $timed_out = false;
        while (!feof($socket)) {
            $chunk = fgets($socket, 8192);
            if ($chunk === false) {
                $meta = stream_get_meta_data($socket);
                if (!empty($meta['timed_out'])) {
                    $timed_out = true;
                }
                break;
            }
            $response .= $chunk;
            if (strpos($chunk, "\n") !== false) break;
        }
        fclose($socket);

        if ($timed_out) {
            return [
                'error' => "Background agent request timed out after {$stream_timeout}s ({$action})",
                'timed_out' => true,
                'raw' => $response
            ];
        }

        $decoded = json_decode(trim($response), true);
        if ($decoded === null) {
            return [
                'error' => 'Invalid JSON received from background agent',
                'raw' => $response
            ];
        }

        return $decoded;
    }
}
