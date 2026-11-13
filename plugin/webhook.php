<?php
require_once __DIR__ . '/api_client.php';

header('Content-Type: application/json');
header('Cache-Control: no-store');
if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
    header('Allow: POST');
    http_response_code(405);
    echo json_encode(['error' => 'Webhook requires POST']);
    exit;
}

$body = file_get_contents('php://input', false, null, 0, 24577);
if ($body === false || strlen($body) > 24576) {
    http_response_code(413);
    echo json_encode(['error' => 'Webhook body is too large']);
    exit;
}

$authorization = $_SERVER['HTTP_AUTHORIZATION'] ?? '';
$token = preg_match('/^Bearer\s+(\S+)$/iD', $authorization, $match) ? $match[1] : '';
$response = UniselvApiClient::call('process_webhook', [
    'raw_body' => $body,
    'bearer_token' => $token,
    'x_uniselv_signature' => $_SERVER['HTTP_X_UNISELV_SIGNATURE'] ?? '',
], '', false, 60);

$status = (int)($response['status_code'] ?? (!empty($response['success']) ? 200 : 502));
http_response_code($status >= 200 && $status <= 599 ? $status : 502);
echo json_encode($response);
