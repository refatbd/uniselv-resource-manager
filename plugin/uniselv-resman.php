<?php
/*
Plugin Name: UNISELV Resource Manager
Version: 1.1.16
Description: Enterprise Resource Management, Cgroups v2 Isolation, Real-Time Monitoring & Telemetry for Webuzo.
Author: Refat Rahman
Author URI: https://refat.ovh
*/

if (!defined('SOFTACULOUS')) {
    // Prevent direct execution outside framework
}

require_once(__DIR__ . '/api_client.php');

function uniselv_get_i18n_dict() {
    return [
        'en' => [
            'brand_title' => 'UNISELV Resource Manager',
            'brand_subtitle' => 'Server-Wide Telemetry, Cgroups v2 & Golden Shield Governance',
            'server_overview' => 'Server Overview',
            'all_accounts' => 'All Accounts',
            'user_analytics' => 'User Analytics & Snapshots',
            'audit' => 'Configured vs Effective Audit',
            'golden_shield' => 'Golden Shield Governance',
            'system_health' => 'System & Agent Health',
            'capacity_planning' => 'Capacity & Oversell',
            'scheduled_reports' => 'Scheduled Reports',
            'branding_locale' => 'Branding & Billing',
            'package_mappings' => 'Package Mappings',
            'permissions_governance' => 'Role & Account Permissions',
            'audit_log' => 'Audit Log',
            'help_about' => 'Help & About',
            'documentation' => 'Docs',
            'bulk_sync' => 'Bulk Sync All Plans',
            'save_changes' => 'Save Changes',
            'status' => 'Status',
            'active' => 'Active',
            'disabled' => 'Disabled',
            'apply_boost' => 'Apply Boost',
            'cancel' => 'Cancel',
            'restore' => 'Restore',
            'refresh' => 'Refresh',
            'reconfigure_golden' => 'Reconfigure Golden Shield',
            'restore_backup' => 'Restore Backup',
            'verify_limits' => 'Verify Limits',
            'auto_prune' => 'Prune Database Now',
            'maintenance_mode' => 'Maintenance Mode',
            'enable_maintenance' => 'Enable Maintenance Mode',
            'disable_maintenance' => 'Disable Maintenance Mode',
            'schedule_automation' => 'Automated Schedule Configuration & Recurrence (A16)',
            'export_report' => 'Export Support Report',
            'quick_stats' => 'Quick Telemetry',
            'cpu_usage' => 'CPU Quota & Usage',
            'memory_usage' => 'RAM Memory Usage',
            'tasks_usage' => 'Process & Task Count',
            'io_usage' => 'Disk I/O Bandwidth',
            'php_pools' => 'PHP-FPM Engine Pools',
            'kill_process' => 'Terminate Process',
            'confirm_kill' => 'Are you sure you want to terminate this process?',
            'confirm_maintenance_enable' => 'Are you sure you want to enable Maintenance Mode? This will restrict non-admin interactions.',
            'confirm_maintenance_disable' => 'Are you sure you want to disable Maintenance Mode and restore normal operations?',
            'success_saved' => 'Settings saved successfully.',
            'operation_failed' => 'Operation failed:',
            'loading' => 'Loading...',
            'no_data' => 'No data available.',
            'account_detail' => 'Account Telemetry Detail',
            'upgrade_recommendations' => 'Upgrade Recommendations',
            'optimization_tips' => 'Optimization Guidance',
            'audit_trail' => 'Administrative Audit Trail',
            'reseller_scope' => 'Reseller Scope',
            'all_owners' => 'All Owners',
            'filter_by_reseller' => 'Filter by Reseller',
            'role_permissions' => 'Role Baseline Permissions',
            'account_permissions' => 'Granular Account Overrides',
            'permission_name' => 'Permission Name',
            'granted' => 'Granted / Allowed',
            'restricted' => 'Restricted / Denied',
            'action' => 'Action',
            'save_permission' => 'Save Permission'
        ],
        'bn' => [
            'brand_title' => 'ইউনিসেলভ রিসোর্স ম্যানেজার',
            'brand_subtitle' => 'সার্ভার টেলিমেট্রি, সিগ্রুপস ভি২ ও গোল্ডেন শিল্ড গভর্নেন্স',
            'server_overview' => 'সার্ভার ওভারভিউ',
            'all_accounts' => 'সকল একাউন্ট',
            'user_analytics' => 'ইউজার অ্যানালিটিক্স ও স্ন্যাপশট',
            'audit' => 'কনফিগারড বনাম কার্যকর অডিট',
            'golden_shield' => 'গোল্ডেন শিল্ড গভর্নেন্স',
            'system_health' => 'সিস্টেম ও এজেন্ট স্বাস্থ্য',
            'capacity_planning' => 'ক্যাপাসিটি ও ওভারসেল',
            'scheduled_reports' => 'শিডিউলড রিপোর্ট',
            'branding_locale' => 'ব্র্যান্ডিং ও বিলিং',
            'package_mappings' => 'প্যাকেজ ম্যাপিং',
            'permissions_governance' => 'রোল ও একাউন্ট পারমিশন',
            'audit_log' => 'অডিট লগ',
            'help_about' => 'সহায়তা ও পরিচিতি',
            'documentation' => 'ডকুমেন্টেশন',
            'bulk_sync' => 'সকল প্ল্যান সিঙ্ক করুন',
            'save_changes' => 'পরিবর্তন সংরক্ষণ করুন',
            'status' => 'স্ট্যাটাস',
            'active' => 'সক্রিয়',
            'disabled' => 'নিষ্ক্রিয়',
            'apply_boost' => 'বুস্ট প্রয়োগ করুন',
            'cancel' => 'বাতিল',
            'restore' => 'রিস্টোর করুন',
            'refresh' => 'রিফ্রেশ',
            'reconfigure_golden' => 'গোল্ডেন শিল্ড পুনঃকনফিগার',
            'restore_backup' => 'ব্যাকআপ রিস্টোর',
            'verify_limits' => 'লিমিট যাচাই করুন',
            'auto_prune' => 'ডাটাবেজ প্রুন করুন',
            'maintenance_mode' => 'রক্ষণাবেক্ষণ মোড',
            'enable_maintenance' => 'রক্ষণাবেক্ষণ মোড সক্রিয় করুন',
            'disable_maintenance' => 'রক্ষণাবেক্ষণ মোড নিষ্ক্রিয় করুন',
            'schedule_automation' => 'স্বয়ংক্রিয় শিডিউল কনফিগারেশন ও পুনরাবৃত্তি (A16)',
            'export_report' => 'সাপোর্ট রিপোর্ট এক্সপোর্ট',
            'quick_stats' => 'কুইক টেলিমেট্রি',
            'cpu_usage' => 'সিপিইউ ব্যবহার ও কোটা',
            'memory_usage' => 'র‍্যাম মেমরি ব্যবহার',
            'tasks_usage' => 'প্রসেস ও টাস্ক সংখ্যা',
            'io_usage' => 'ডিস্ক আই/ও ব্যান্ডউইডথ',
            'php_pools' => 'পিএইচপি-এফপিএম ইঞ্জিন পুল',
            'kill_process' => 'প্রসেস বন্ধ করুন',
            'confirm_kill' => 'আপনি কি নিশ্চিতভাবে এই প্রসেসটি বন্ধ করতে চান?',
            'confirm_maintenance_enable' => 'আপনি কি নিশ্চিতভাবে রক্ষণাবেক্ষণ মোড সক্রিয় করতে চান? এটি নন-অ্যাডমিন কার্যকলাপ সীমাবদ্ধ করবে।',
            'confirm_maintenance_disable' => 'আপনি কি নিশ্চিতভাবে রক্ষণাবেক্ষণ মোড নিষ্ক্রিয় করতে চান এবং সাধারণ কার্যক্রম চালু করতে চান?',
            'success_saved' => 'সেটিংস সফলভাবে সংরক্ষিত হয়েছে।',
            'operation_failed' => 'অপারেশন ব্যর্থ হয়েছে:',
            'loading' => 'লোড হচ্ছে...',
            'no_data' => 'কোনো ডাটা পাওয়া যায়নি।',
            'account_detail' => 'একাউন্ট টেলিমেট্রি বিস্তারিত',
            'upgrade_recommendations' => 'আপগ্রেড সুপারিশ',
            'optimization_tips' => 'অপটিমাইজেশন পরামর্শ',
            'audit_trail' => 'অ্যাডমিনিস্ট্রেটিভ অডিট ট্রেইল',
            'reseller_scope' => 'রিসেলার আওতাভুক্ত',
            'all_owners' => 'সকল ওনার',
            'filter_by_reseller' => 'রিসেলার অনুযায়ী ফিল্টার',
            'role_permissions' => 'রোল বেসলাইন পারমিশন',
            'account_permissions' => 'গ্র্যানুলার একাউন্ট ওভাররাইড',
            'permission_name' => 'পারমিশনের নাম',
            'granted' => 'অনুমোদিত',
            'restricted' => 'সীমাবদ্ধ / অননুমোদিত',
            'action' => 'অ্যাকশন',
            'save_permission' => 'পারমিশন সংরক্ষণ করুন'
        ]
    ];
}

function __u($key, $locale = 'en') {
    $dict = uniselv_get_i18n_dict();
    if (isset($dict[$locale][$key])) {
        return $dict[$locale][$key];
    }
    if (isset($dict['en'][$key])) {
        return $dict['en'][$key];
    }
    return $key;
}

// ==================== LIFECYCLE HOOKS ====================

if (function_exists('register_activation_hook')) {
    register_activation_hook(__FILE__, 'uniselv_resman_activation');
}
function uniselv_resman_activation() {
    global $error;

    // Direct execution is supported only from an already privileged CLI.
    if (PHP_SAPI === 'cli' && function_exists('posix_geteuid') && posix_geteuid() === 0) {
        include_once(__DIR__ . '/install.php');
        return true;
    }

    // Use Webuzo's privileged background dispatcher. Invoke the real installer
    // directly: the inactive plugin's cli_end hook may not yet be available.
    // Dispatch is not proof of completed installation.
    if (function_exists('root_bg_exec')) {
        $log = '/root/resman-panel-activation.log';
        $script = 'umask 077; printf "UNISELV_PANEL_INSTALL_STARTED\\n" > ' . escapeshellarg($log) .
            '; /usr/local/emps/bin/php ' . escapeshellarg(__DIR__ . '/install.php') .
            ' >> ' . escapeshellarg($log) . ' 2>&1; uniselv_rc=$?; ' .
            'printf "\\nUNISELV_PANEL_INSTALL_EXIT=%s\\n" "$uniselv_rc" >> ' . escapeshellarg($log) .
            '; exit "$uniselv_rc"';
        $command = '/bin/sh -c ' . escapeshellarg($script);
        if (root_bg_exec($command) !== false) return true;
        $error['uniselv_activation'] = 'UNISELV root installation dispatch failed. Existing services were retained.';
        return false;
    }

    $error['uniselv_activation'] = 'UNISELV activation requires Webuzo root_bg_exec. Installer was not run in the panel worker; existing services were retained.';
    return false;
}

if (function_exists('register_deactivation_hook')) {
    register_deactivation_hook(__FILE__, 'uniselv_resman_deactivation');
}
function uniselv_resman_deactivation() {
    global $error;

    // Direct execution is supported only from an already privileged CLI.
    if (PHP_SAPI === 'cli' && function_exists('posix_geteuid') && posix_geteuid() === 0) {
        include_once(__DIR__ . '/deactivate.php');
        return true;
    }

    // Use Webuzo's privileged background dispatcher. Invoke the real deactivator
    // directly as root, avoiding unprivileged panel worker execution.
    if (function_exists('root_bg_exec')) {
        $log = '/root/resman-panel-deactivation.log';
        $script = 'umask 077; printf "UNISELV_PANEL_DEACTIVATE_STARTED\n" > ' . escapeshellarg($log) .
            '; /usr/local/emps/bin/php ' . escapeshellarg(__DIR__ . '/deactivate.php') .
            ' >> ' . escapeshellarg($log) . ' 2>&1; uniselv_rc=$?; ' .
            'printf "\nUNISELV_PANEL_DEACTIVATE_EXIT=%s\n" "$uniselv_rc" >> ' . escapeshellarg($log) .
            '; exit "$uniselv_rc"';
        $command = '/bin/sh -c ' . escapeshellarg($script);
        if (root_bg_exec($command) !== false) return true;
        $error['uniselv_deactivation'] = 'UNISELV root deactivation dispatch failed.';
        return false;
    }

    $error['uniselv_deactivation'] = 'UNISELV deactivation requires Webuzo root_bg_exec. Deactivator was not run in the panel worker; existing services were retained.';
    return false;
}

// CLI Hook
if (function_exists('add_filter')) {
    add_filter('cli_end', 'uniselv_resman_cli');
}
function uniselv_resman_cli($args) {
    global $globals;

    if (isset($args['uniselv-resman-install'])) {
        include_once(__DIR__ . '/install.php');
        exit(0);
    }

    if (isset($args['uniselv-resman-deactivate'])) {
        include_once(__DIR__ . '/deactivate.php');
        exit(0);
    }

    if (isset($args['uniselv-resman-uninstall'])) {
        include_once(__DIR__ . '/uninstall.php');
        exit(0);
    }
}

function uniselv_render_developer_footer() {
    return '<div class="uniselv-developer-footer" style="margin-top: 36px; padding: 18px 24px; background: #ffffff; border: 1px solid var(--uniselv-border, #e2e8f0); border-radius: 12px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
        <div style="display: flex; align-items: center; gap: 12px;">
            <div style="width: 38px; height: 38px; border-radius: 50%; background: linear-gradient(135deg, #2563eb, #1d4ed8); display: flex; align-items: center; justify-content: center; color: #ffffff; font-weight: 700; font-size: 0.95rem; box-shadow: 0 2px 6px rgba(37,99,235,0.25); letter-spacing: 0.5px;">RR</div>
            <div>
                <div style="font-weight: 700; font-size: 0.95rem; color: #1e293b;">
                    Developed by <a href="https://refat.ovh" target="_blank" style="color: var(--uniselv-primary, #2563eb); text-decoration: none; font-weight: 700;">Refat Rahman</a>
                </div>
                <div style="font-size: 0.8rem; color: #64748b; margin-top: 2px;">
                    Systems Architect & Full-Stack Engineer • <a href="https://refat.ovh" target="_blank" style="color: #64748b; text-decoration: underline;">refat.ovh</a>
                </div>
            </div>
        </div>
        <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
            <a href="https://github.com/refatbd" target="_blank" class="uniselv-social-btn" title="GitHub: refatbd" style="display: inline-flex; align-items: center; gap: 6px; padding: 6px 12px; border-radius: 8px; background: #f8fafc; border: 1px solid #e2e8f0; color: #1e293b; font-size: 0.82rem; font-weight: 600; text-decoration: none; transition: all 0.2s ease;">
                <svg width="15" height="15" fill="currentColor" viewBox="0 0 24 24"><path fill-rule="evenodd" clip-rule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"/></svg> GitHub
            </a>
            <a href="https://t.me/refatbd" target="_blank" class="uniselv-social-btn" title="Telegram: @refatbd" style="display: inline-flex; align-items: center; gap: 6px; padding: 6px 12px; border-radius: 8px; background: #f8fafc; border: 1px solid #e2e8f0; color: #0284c7; font-size: 0.82rem; font-weight: 600; text-decoration: none; transition: all 0.2s ease;">
                <svg width="15" height="15" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm4.64 6.8c-.15 1.58-.8 5.42-1.13 7.19-.14.75-.42 1-.68 1.03-.58.05-1.02-.38-1.58-.75-.88-.58-1.38-.94-2.23-1.5-.99-.65-.35-1.01.22-1.59.15-.15 2.71-2.48 2.76-2.69a.2.2 0 00-.05-.18c-.06-.05-.14-.03-.21-.02-.09.02-1.49.95-4.22 2.79-.4.27-.76.41-1.08.4-.36-.01-1.04-.2-1.55-.37-.63-.2-1.12-.31-1.08-.66.02-.18.27-.36.75-.55 2.92-1.27 4.86-2.11 5.83-2.51 2.78-1.16 3.35-1.36 3.73-1.36.08 0 .27.02.39.12.1.08.13.19.14.27-.01.06.01.24 0 .37z"/></svg> Telegram
            </a>
            <a href="https://www.facebook.com/rjrefat/" target="_blank" class="uniselv-social-btn" title="Facebook: rjrefat" style="display: inline-flex; align-items: center; gap: 6px; padding: 6px 12px; border-radius: 8px; background: #f8fafc; border: 1px solid #e2e8f0; color: #1877f2; font-size: 0.82rem; font-weight: 600; text-decoration: none; transition: all 0.2s ease;">
                <svg width="15" height="15" fill="currentColor" viewBox="0 0 24 24"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg> Facebook
            </a>
            <a href="https://www.instagram.com/refat_official" target="_blank" class="uniselv-social-btn" title="Instagram: @refat_official" style="display: inline-flex; align-items: center; gap: 6px; padding: 6px 12px; border-radius: 8px; background: #f8fafc; border: 1px solid #e2e8f0; color: #e1306c; font-size: 0.82rem; font-weight: 600; text-decoration: none; transition: all 0.2s ease;">
                <svg width="15" height="15" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/></svg> Instagram
            </a>
        </div>
    </div>';
}

// ==================== ADMIN PANEL INTEGRATION ====================

if (function_exists('add_filter')) {
    add_filter('admin_menu', 'uniselv_resman_admin_menu', 10, 1);
}
function uniselv_resman_admin_menu($menu) {
    global $globals;
    $menu['uniselv-resman'] = [
        'name' => 'UNISELV Resources',
        'href' => $globals['ind'] . 'act=uniselv-resman',
        'icon' => 'fas fa-chart-line',
        'attr' => 'title="UNISELV Resource Manager"'
    ];
    return $menu;
}

function uniselv_safe_brand_url($value) {
    $value = trim((string)$value);
    $scheme = strtolower((string)parse_url($value, PHP_URL_SCHEME));
    if (!filter_var($value, FILTER_VALIDATE_URL) || !in_array($scheme, ['http', 'https']) ||
        parse_url($value, PHP_URL_USER) !== null || parse_url($value, PHP_URL_PASS) !== null) return '';
    return htmlspecialchars($value, ENT_QUOTES, 'UTF-8');
}

function uniselv_csrf_token($user) {
    global $SESS;
    $sess_key = isset($SESS['self_sess_key']) ? (string)$SESS['self_sess_key'] : '';
    if ($sess_key === '' && preg_match('~/((?:sess)[A-Za-z0-9]{8,})/~', $_SERVER['REQUEST_URI'] ?? '', $match)) $sess_key = $match[1];
    if ($sess_key === '') return ''; // Never issue a predictable shared fallback token.
    return hash_hmac('sha256', $user . ':' . $sess_key, 'uniselv_resman_secret_salt_2026');
}

function uniselv_verify_csrf($user) {
    $token = isset($_POST['csrf_token']) ? $_POST['csrf_token'] : (isset($_SERVER['HTTP_X_CSRF_TOKEN']) ? $_SERVER['HTTP_X_CSRF_TOKEN'] : '');
    $expected = uniselv_csrf_token($user);
    if (empty($token) || !hash_equals($expected, $token)) {
        header('Content-Type: application/json', true, 403);
        echo json_encode(['error' => 'Security Refusal: Invalid or missing CSRF token']);
        exit(0);
    }
}

if (function_exists('admin_act')) {
    admin_act('uniselv-resman', 'uniselv_resman_admin');
}
function uniselv_resman_admin() {
    global $globals, $SESS;

    if (isset($_REQUEST['api']) && $_REQUEST['api'] === 'json') {
        header('Content-Type: application/json');
        $subact = isset($_REQUEST['subact']) ? $_REQUEST['subact'] : '';
        $params = $_POST;
        $current_user = isset($SESS['user']) ? $SESS['user'] : 'root';

        $is_webhook = ($subact === 'webhook');
        if ($is_webhook) {
            $raw_input = file_get_contents('php://input');
            if (!empty($raw_input)) {
                $decoded = json_decode($raw_input, true);
                if (is_array($decoded)) {
                    $params = array_merge($params, $decoded);
                }
                $params['raw_body'] = $raw_input;
            }
            if (!empty($_SERVER['HTTP_AUTHORIZATION'])) {
                $params['bearer_token'] = preg_replace('/^Bearer\s+/i', '', $_SERVER['HTTP_AUTHORIZATION']);
            }
            if (!empty($_SERVER['HTTP_X_UNISELV_SIGNATURE'])) {
                $params['x_uniselv_signature'] = $_SERVER['HTTP_X_UNISELV_SIGNATURE'];
            }
        }

        $mutation_actions = [
            'set_override', 'cancel_override', 'sync_plans', 'save_plan',
            'set_maintenance', 'save_storage_settings', 'prune_database',
            'golden_reconfigure', 'golden_disable', 'golden_restore', 'golden_enable',
            'save_feature_settings', 'adapter_sync', 'delete_plan', 'dispatch_report',
            'save_report_schedule', 'branding_save', 'mark_notification',
            'save_package_mapping', 'delete_package_mapping', 'webhook',
            'save_account_permission', 'save_role_permission',
            'clear_audit_logs', 'purge_snapshots'
        ];
        
        if (in_array($subact, $mutation_actions)) {
            // Strictly enforce CSRF for all browser mutation actions including adapter_sync.
            // Only external webhook requests (subact === 'webhook') are exempt from browser session CSRF,
            // as they are cryptographically authenticated via HMAC-SHA256 / Bearer token in process_webhook.
            if (!$is_webhook) {
                uniselv_verify_csrf($current_user);
            }
        }

        $action_map = [
            'overview' => 'get_admin_overview',
            'accounts' => 'get_admin_accounts',
            'account_detail' => 'get_admin_account_detail',
            'audit' => 'get_admin_audit_limits',
            'out_of_bounds' => 'get_admin_out_of_boundary',
            'set_override' => 'set_temporary_override',
            'cancel_override' => 'cancel_temporary_override',
            'sync_plans' => 'sync_native_plans',
            'save_plan' => 'save_native_plan',
            'delete_plan' => 'delete_native_plan',
            'capacity' => 'get_capacity_planning',
            'scheduled_reports' => 'get_scheduled_reports',
            'dispatch_report' => 'dispatch_scheduled_report',
            'get_report_schedule' => 'get_report_schedule',
            'save_report_schedule' => 'save_report_schedule',
            'package_mappings' => 'get_package_mappings',
            'save_package_mapping' => 'save_package_mapping',
            'delete_package_mapping' => 'delete_package_mapping',
            'get_permissions' => 'get_permissions',
            'save_account_permission' => 'save_account_permission',
            'save_role_permission' => 'save_role_permission',
            'branding_get' => 'get_branding_settings',
            'branding_save' => 'save_branding_settings',
            'audit_log' => 'get_audit_log',
            'clear_audit_logs' => 'clear_audit_logs',
            'purge_snapshots' => 'purge_snapshots',
            'mark_notification' => 'mark_notification',
            'set_maintenance' => 'set_maintenance_mode',
            'agent_health' => 'get_agent_health',
            'get_feature_settings' => 'get_feature_settings',
            'save_feature_settings' => 'save_feature_settings',
            'get_storage_settings' => 'get_storage_settings',
            'save_storage_settings' => 'save_storage_settings',
            'prune_database' => 'prune_database_now',
            'adapter_sync' => 'run_adapter_sync',
            'webhook' => 'process_webhook',
            'history' => 'get_enduser_history',
            'dashboard' => 'get_enduser_dashboard',
            'processes' => 'get_enduser_processes',
            'stop_process' => 'stop_enduser_process',
            'golden_status' => 'get_golden_shield_status',
            'golden_enable' => 'enable_golden_shield',
            'golden_reconfigure' => 'reconfigure_golden_shield',
            'golden_verify' => 'verify_golden_shield',
            'golden_disable' => 'disable_golden_shield',
            'golden_restore' => 'restore_golden_shield_config',
            'golden_list_backups' => 'list_golden_shield_backups',
            'snapshots_index' => 'get_snapshots_index',
            'snapshot_detail' => 'get_snapshot_detail'
        ];

        if (isset($action_map[$subact])) {
            $resp = UniselvApiClient::call($action_map[$subact], $params, $current_user, true);
            echo json_encode($resp);
        } else {
            echo json_encode(['error' => 'Unknown admin subaction']);
        }
        exit(0);
    }

    if (function_exists('theme_for_act')) {
        theme_for_act('uniselv_resman_admin_theme', 'uniselv-resman');
    }
}

function uniselv_resman_admin_theme() {
    global $globals, $SESS;

    $overview = UniselvApiClient::call('get_admin_overview', [], $SESS['user'], true);
    $native_plan_data = UniselvApiClient::call('get_package_mappings', [], $SESS['user'], true);
    $native_plan_options = '';
    foreach (($native_plan_data['native_plans'] ?? []) as $native_plan) {
        $native_plan_options .= '<option value="' . htmlspecialchars($native_plan['name'], ENT_QUOTES, 'UTF-8') . '">' . htmlspecialchars($native_plan['label'], ENT_QUOTES, 'UTF-8') . '</option>';
    }
    if (!$native_plan_options) $native_plan_options = '<option value="">No verified native plans available</option>';

    $accounts = UniselvApiClient::call('get_admin_accounts', [], $SESS['user'], true);
    $audit = UniselvApiClient::call('get_admin_audit_limits', [], $SESS['user'], true);
    $sync_rows = $audit['audit'] ?? [];
    $sync_count = count(array_filter($sync_rows, function($row) { return !empty($row['is_synchronized']); }));
    $sync_summary = $sync_rows ? $sync_count . ' / ' . count($sync_rows) . ' verified at page load' : 'Unavailable';
    $health = UniselvApiClient::call('get_agent_health', [], $SESS['user'], true);
    $golden = UniselvApiClient::call('get_golden_shield_status', [], $SESS['user'], true);

    $branding = UniselvApiClient::call('get_branding_settings', [], $SESS['user'], true);
    $locale = !empty($branding['locale']) ? $branding['locale'] : 'en';
    $brand_name = !empty($branding['brand_name']) ? htmlspecialchars($branding['brand_name']) : __u('brand_title', $locale);
    $brand_logo = !empty($branding['brand_logo_url']) ? uniselv_safe_brand_url($branding['brand_logo_url']) : '';
    $brand_color = !empty($branding['brand_primary_color']) && preg_match('/^#[0-9a-fA-F]{6}$/', $branding['brand_primary_color']) ? $branding['brand_primary_color'] : '#2563eb';
    $brand_support = !empty($branding['brand_support_url']) ? uniselv_safe_brand_url($branding['brand_support_url']) : 'https://uniselv.com/support';
    $brand_docs = !empty($branding['brand_docs_url']) ? uniselv_safe_brand_url($branding['brand_docs_url']) : '';
    if (rtrim($brand_docs, '/') === 'https://docs.uniselv.com') $brand_docs = ''; // Historical placeholder; use bundled local Help.

    $panel_url = !empty($globals['panel_url']) ? rtrim($globals['panel_url'], '/') : '';
    $i18n_dict = uniselv_get_i18n_dict();

    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '">';
    echo '<style>:root { --uniselv-primary: ' . $brand_color . '; --primary-color: ' . $brand_color . '; }</style>';
    echo '<script>
window.UNISELV_LOCALE = ' . json_encode($locale) . ';
window.UNISELV_TRANSLATIONS = ' . json_encode($i18n_dict[$locale] ?? $i18n_dict['en']) . ';
</script>';
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '"></script>';

    echo '<div class="uniselv-container">';
    
    // Header
    echo '<div class="uniselv-header">
        <div class="uniselv-brand">
            <div class="uniselv-logo-icon">
                ' . (!empty($brand_logo) ? '<img src="' . $brand_logo . '" alt="' . $brand_name . '" style="max-height: 38px; max-width: 38px; object-fit: contain;">' : '<svg width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 4a2 2 0 114 0v1a1 1 0 001 1h3a1 1 0 011 1v3a1 1 0 01-1 1h-1a2 2 0 100 4h1a1 1 0 011 1v3a1 1 0 01-1 1h-3a1 1 0 01-1-1v-1a2 2 0 10-4 0v1a1 1 0 01-1 1H7a1 1 0 01-1-1v-3a1 1 0 00-1-1H4a2 2 0 110-4h1a1 1 0 001-1V7a1 1 0 011-1h3a1 1 0 001-1V4z"/></svg>') . '
            </div>
            <div>
                <h2 class="uniselv-brand-title">' . $brand_name . '</h2>
                <p class="uniselv-brand-subtitle">' . __u('brand_subtitle', $locale) . '</p>
            </div>
        </div>
        <div style="display: flex; gap: 10px; align-items: center; flex-wrap: wrap;">
            <select id="uniselv-locale-selector" class="uniselv-select" style="padding: 4px 8px; font-size: 0.82rem; border-radius: 6px; background: #fff; border: 1px solid var(--uniselv-border);" onchange="UniselvResMan.setLocale(this.value)">
                <option value="en"' . ($locale === 'en' ? ' selected' : '') . '>English (US)</option>
                <option value="bn"' . ($locale === 'bn' ? ' selected' : '') . '>বাংলা (Bengali)</option>
            </select>
            <a href="' . ($brand_docs ?: '#help') . '" ' . ($brand_docs ? 'target="_blank" rel="noopener noreferrer"' : 'onclick="UniselvResMan.openHelpTopic(&quot;quickstart&quot;); return false;"') . ' class="uniselv-help-pill" style="text-decoration: none;">
                <svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/></svg> ' . __u('documentation', $locale) . '
            </a>
            <button class="uniselv-help-pill" onclick="UniselvResMan.openHelpTopic(\'quickstart\')">
                <svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg> ' . __u('help_about', $locale) . '
            </button>
            <button class="uniselv-btn btn-primary" onclick="UniselvResMan.syncNativePlans()">
                <svg width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg> ' . __u('bulk_sync', $locale) . '
            </button>
        </div>
    </div>';

    // Tabs
    echo '<div class="uniselv-tabs">
        <button class="uniselv-tab-btn active" data-tab="overview">
            <svg class="uniselv-tab-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg> ' . __u('server_overview', $locale) . '
        </button>
        <button class="uniselv-tab-btn" data-tab="accounts">
            <svg class="uniselv-tab-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"/></svg> ' . __u('all_accounts', $locale) . ' (' . (isset($accounts['count']) ? $accounts['count'] : 0) . ')
        </button>
        <button class="uniselv-tab-btn" data-tab="analytics">
            <svg class="uniselv-tab-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 8v8m-4-5v5m-4-2v2m-2 4h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg> ' . __u('user_analytics', $locale) . '
        </button>
        <button class="uniselv-tab-btn" data-tab="audit">
            <svg class="uniselv-tab-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg> ' . __u('audit', $locale) . '
        </button>
        <button class="uniselv-tab-btn" data-tab="goldenshield">
            <svg class="uniselv-tab-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/></svg> ' . __u('golden_shield', $locale) . '
        </button>
        <button class="uniselv-tab-btn" data-tab="capacity">
            <svg class="uniselv-tab-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"/></svg> ' . __u('capacity_planning', $locale) . '
        </button>
        <button class="uniselv-tab-btn" data-tab="reports">
            <svg class="uniselv-tab-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg> ' . __u('scheduled_reports', $locale) . '
        </button>
        <button class="uniselv-tab-btn" data-tab="integrations">
            <svg class="uniselv-tab-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 4a2 2 0 114 0v1a1 1 0 001 1h3a1 1 0 011 1v3a1 1 0 01-1 1h-1a2 2 0 100 4h1a1 1 0 011 1v3a1 1 0 01-1 1h-3a1 1 0 01-1-1v-1a2 2 0 10-4 0v1a1 1 0 01-1 1H7a1 1 0 01-1-1v-3a1 1 0 00-1-1H4a2 2 0 110-4h1a1 1 0 001-1V7a1 1 0 011-1h3a1 1 0 001-1V4z"/></svg> ' . __u('branding_locale', $locale) . '
        </button>
        <button class="uniselv-tab-btn" data-tab="auditlog">
            <svg class="uniselv-tab-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg> ' . __u('audit_log', $locale) . '
        </button>
        <button class="uniselv-tab-btn" data-tab="health">
            <svg class="uniselv-tab-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/></svg> ' . __u('system_health', $locale) . '
        </button>
        <button class="uniselv-tab-btn" data-tab="help">
            <svg class="uniselv-tab-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg> ' . __u('help_about', $locale) . '
        </button>
    </div>';

    // TAB 1: SERVER OVERVIEW
    $host = !empty($overview['host']) ? $overview['host'] : (!empty($overview['server']) ? $overview['server'] : []);
    $shield = !empty($overview['golden_shield']) ? $overview['golden_shield'] : [];
    $calc_policy = !empty($shield['configured_policy']) ? $shield['configured_policy'] : [];

    $cpu_cores = isset($host['cpu_cores']) ? $host['cpu_cores'] : (isset($host['cpu_count']) ? $host['cpu_count'] : 'Unavailable');
    $total_ram = isset($host['total_ram_formatted']) ? $host['total_ram_formatted'] : (isset($host['mem_total_formatted']) ? $host['mem_total_formatted'] : 'Unavailable');
    $customer_cpu = isset($shield['customer_cpu_percent']) ? $shield['customer_cpu_percent'] : (isset($calc_policy['customerCpuPercent']) ? $calc_policy['customerCpuPercent'] : 'Unavailable');
    $reserved_cpu = isset($shield['reserved_cpu_percent']) ? $shield['reserved_cpu_percent'] : (isset($calc_policy['reservedCpuPercent']) ? $calc_policy['reservedCpuPercent'] : 'Unavailable');

    $golden_mem_cur = isset($shield['golden_mem_current_formatted']) ? $shield['golden_mem_current_formatted'] : 'Unavailable';
    $golden_mem_cap = isset($shield['golden_mem_max_formatted']) ? $shield['golden_mem_max_formatted'] : (isset($calc_policy['hostingMemoryMaxMiB']) ? round($calc_policy['hostingMemoryMaxMiB']/1024, 2) . ' GiB' : 'Unavailable');
    $headroom_mib = isset($shield['headroom_mib']) ? $shield['headroom_mib'] : (isset($calc_policy['headroomMiB']) ? $calc_policy['headroomMiB'] : 'Unavailable');

    $l1 = isset($host['load1']) ? number_format((float)$host['load1'], 2) : '0.00';
    $l5 = isset($host['load5']) ? number_format((float)$host['load5'], 2) : '0.00';
    $l15 = isset($host['load15']) ? number_format((float)$host['load15'], 2) : '0.00';

    echo '<div id="tab-overview" class="uniselv-tab-content active"><p id="admin-telemetry-freshness" style="font-size:0.85rem; margin:0 0 12px;">Reading latest telemetry sample...</p>';
    echo '<div class="uniselv-grid">
        <div class="uniselv-card">
            <div class="uniselv-card-header"><span class="uniselv-card-title">Hardware Detection</span></div>
            <div class="uniselv-card-value" id="admin-card-hw-cpu">' . $cpu_cores . ' vCPUs</div>
            <div class="uniselv-card-sub" id="admin-card-hw-ram">Physical RAM: ' . $total_ram . '</div>
        </div>
        <div class="uniselv-card">
            <div class="uniselv-card-header"><span class="uniselv-card-title">Shared CPU Headroom</span></div>
            <div class="uniselv-card-value" id="admin-card-cpu-headroom">' . $customer_cpu . '% Hosting</div>
            <div class="uniselv-card-sub" id="admin-card-cpu-sub">' . $reserved_cpu . '% System Headroom (No fixed core dedicated)</div>
        </div>
        <div class="uniselv-card">
            <div class="uniselv-card-header"><span class="uniselv-card-title">RAM Safety Budget</span></div>
            <div class="uniselv-card-value" id="admin-card-ram-curr">' . $golden_mem_cur . '</div>
            <div class="uniselv-card-sub" id="admin-card-ram-cap">Hosting Cap: ' . $golden_mem_cap . ' (Reserve: ' . $headroom_mib . ' MiB)</div>
        </div>
        <div class="uniselv-card">
            <div class="uniselv-card-header"><span class="uniselv-card-title">System Load</span></div>
            <div class="uniselv-card-value" id="admin-card-load-1">' . $l1 . '</div>
            <div class="uniselv-card-sub" id="admin-card-load-sub">5m: ' . $l5 . ' | 15m: ' . $l15 . '</div>
        </div>
    </div>';

    // Top consumers
    echo '<div class="uniselv-card mb-4">
        <h5 style="margin-bottom: 14px; font-weight: 700;">Top Resource Consumers (Latest Sample at Page Load)</h5>
        <div class="uniselv-table-wrap">
            <table class="uniselv-table">
                <thead>
                    <tr>
                        <th>Account</th>
                        <th>Plan</th>
                        <th>CPU % (Core Eq.)</th>
                        <th>Allowance Used</th>
                        <th>Memory Used</th>
                        <th>Active Tasks</th>
                        <th>Throttling Events</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>';
    if (!empty($accounts['accounts'])) {
        $consumers = $accounts['accounts'];
        usort($consumers, function($a, $b) { return ($b['cpu_percent'] <=> $a['cpu_percent']) ?: ($b['mem_used_bytes'] <=> $a['mem_used_bytes']); });
        foreach (array_slice($consumers, 0, 5) as $acc) {
            $badge = ($acc['cpu_allowance_percent'] > 90) ? 'badge-critical' : (($acc['cpu_allowance_percent'] > 60) ? 'badge-warning' : 'badge-normal');
            $status_txt = ($acc['cpu_allowance_percent'] > 90) ? 'CRITICAL' : (($acc['cpu_allowance_percent'] > 60) ? 'ELEVATED' : 'NORMAL');
            echo '<tr>
                <td><strong>' . htmlspecialchars($acc['username']) . '</strong><br><small style="color:#64748b;">' . htmlspecialchars($acc['domain']) . '</small></td>
                <td><span class="uniselv-badge badge-normal">' . htmlspecialchars(strtoupper($acc['plan_name'])) . '</span></td>
                <td>' . $acc['cpu_percent'] . '%</td>
                <td><span class="uniselv-badge ' . $badge . '">' . $acc['cpu_allowance_percent'] . '% (' . $status_txt . ')</span></td>
                <td>' . $acc['mem_formatted'] . '</td>
                <td>' . $acc['tasks_current'] . ' / ' . $acc['tasks_max'] . '</td>
                <td>' . $acc['throttled_events'] . '</td>
                <td>
                    <button class="uniselv-btn btn-outline btn-sm" onclick="UniselvResMan.openOverrideModal(\'' . htmlspecialchars($acc['username']) . '\', \'' . htmlspecialchars($acc['plan_name']) . '\')">Grant Boost</button>
                </td>
            </tr>';
        }
    }
    echo '      </tbody>
            </table>
        </div>
    </div>';
    echo '</div>'; // End Tab 1

    // TAB 2: ALL ACCOUNTS
    echo '<div id="tab-accounts" class="uniselv-tab-content">
        <div style="margin-bottom: 16px; display: flex; gap: 12px; align-items: center;">
            <input type="text" id="uniselv-account-search" placeholder="Search accounts by username or domain..." style="padding: 10px 14px; border: 1px solid var(--uniselv-border); border-radius: 6px; width: 340px; font-size: 0.9rem;">
        </div>
        <div class="uniselv-table-wrap">
            <table class="uniselv-table">
                <thead>
                    <tr>
                        <th>User</th>
                        <th>Domain</th>
                        <th>Plan</th>
                        <th>CPU %</th>
                        <th>Allowance %</th>
                        <th>Memory Used</th>
                        <th>Tasks</th>
                        <th>Throttling</th>
                        <th>OOM Kills</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>';
    if (!empty($accounts['accounts'])) {
        foreach ($accounts['accounts'] as $acc) {
            $badge = ($acc['cpu_allowance_percent'] > 90) ? 'badge-critical' : (($acc['cpu_allowance_percent'] > 60) ? 'badge-warning' : 'badge-normal');
            echo '<tr class="uniselv-account-row" data-user="' . htmlspecialchars($acc['username']) . '" data-domain="' . htmlspecialchars($acc['domain']) . '">
                <td><strong>' . htmlspecialchars($acc['username']) . '</strong></td>
                <td>' . htmlspecialchars($acc['domain']) . '</td>
                <td><span class="uniselv-badge badge-normal">' . htmlspecialchars(strtoupper($acc['plan_name'])) . '</span></td>
                <td>' . $acc['cpu_percent'] . '%</td>
                <td><span class="uniselv-badge ' . $badge . '">' . $acc['cpu_allowance_percent'] . '%</span></td>
                <td>' . $acc['mem_formatted'] . '</td>
                <td>' . $acc['tasks_current'] . '</td>
                <td>' . $acc['throttled_events'] . '</td>
                <td>' . ($acc['oom_events'] > 0 ? '<span class="uniselv-badge badge-critical">' . $acc['oom_events'] . ' OOM</span>' : '0') . '</td>
                <td>
                    <button class="uniselv-btn btn-outline btn-sm" onclick="UniselvResMan.openOverrideModal(\'' . htmlspecialchars($acc['username']) . '\', \'' . htmlspecialchars($acc['plan_name']) . '\')">Boost</button>
                    <button class="uniselv-btn btn-outline btn-sm" style="margin-left: 4px;" onclick="UniselvResMan.inspectUserUsage(\'' . htmlspecialchars($acc['username']) . '\')" title="Inspect Current Usage & 8 Resource Charts">Current Usage</button>
                    <button class="uniselv-btn btn-outline btn-sm" style="margin-left: 4px;" onclick="UniselvResMan.inspectUserSnapshots(\'' . htmlspecialchars($acc['username']) . '\')" title="Browse Point-in-time Forensic Snapshots">Snapshots</button>
                </td>
            </tr>';
        }
    }
    echo '      </tbody>
            </table>
        </div>
        <div id="uniselv-accounts-pagination" class="uniselv-pagination-wrap"></div>

        <!-- Side-by-Side Management Grid in All Accounts -->
        <div class="uniselv-grid" style="grid-template-columns: repeat(auto-fit, minmax(420px, 1fr)); gap: 20px; margin-top: 24px;">
            <!-- Column 1: Grant Temporary Resource Boost -->
            <div class="uniselv-card" id="card-temporary-boost">
                <div class="uniselv-card-header" style="margin-bottom: 12px;">
                    <h5 style="margin: 0; font-weight: 700; display: flex; align-items: center; gap: 8px;">
                        <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="color: var(--uniselv-primary);"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
                        Grant Temporary Resource Boost
                    </h5>
                </div>
                <p style="font-size: 0.86rem; color: #64748b; margin-bottom: 14px;">Temporarily elevate an account limits for high-traffic events. The boost automatically expires and cleanly restores the original plan.</p>
                
                <div class="uniselv-form-group" style="margin-bottom: 12px;">
                    <label class="uniselv-form-label">Target Account</label>
                    <select id="quick-override-username" class="uniselv-form-input" style="width: 100%;">
                        <option value="">-- Select an account --</option>';
    if (!empty($accounts['accounts'])) {
        foreach ($accounts['accounts'] as $acc) {
            echo '<option value="' . htmlspecialchars($acc['username']) . '">' . htmlspecialchars($acc['username']) . ' (' . htmlspecialchars($acc['domain']) . ' - ' . htmlspecialchars(strtoupper($acc['plan_name'])) . ')</option>';
        }
    }
    echo '          </select>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px;">
                    <div>
                        <label class="uniselv-form-label">Boosted Plan</label>
                        <select id="quick-override-plan" class="uniselv-form-input" style="width: 100%;">' . $native_plan_options . '</select>
                    </div>
                    <div>
                        <label class="uniselv-form-label">Duration (Minutes)</label>
                        <input type="number" id="quick-override-duration" value="60" min="5" max="1440" class="uniselv-form-input" style="width: 100%;">
                    </div>
                </div>
                <div class="uniselv-form-group" style="margin-bottom: 16px;">
                    <label class="uniselv-form-label">Reason</label>
                    <input type="text" id="quick-override-reason" value="Temporary high-traffic event" class="uniselv-form-input" style="width: 100%;">
                </div>
                <button class="uniselv-btn btn-primary" onclick="UniselvResMan.submitQuickOverride()">
                    <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg> Apply Temporary Boost
                </button>
            </div>

            <!-- Column 2: Bulk Plan Synchronization & Governance Actions -->
            <div class="uniselv-card">
                <div class="uniselv-card-header" style="margin-bottom: 12px;">
                    <h5 style="margin: 0; font-weight: 700; display: flex; align-items: center; gap: 8px;">
                        <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="color: #10b981;"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
                        Bulk Plan Synchronization & Governance
                    </h5>
                </div>
                <p style="font-size: 0.86rem; color: #64748b; margin-bottom: 14px;">Reapply Webuzo plan limits across all hosting accounts and reconcile systemd slice drop-ins with zero kernel drift.</p>
                <div style="background: var(--uniselv-bg-subtle); border: 1px solid var(--uniselv-border); border-radius: 8px; padding: 14px; margin-bottom: 16px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 0.85rem;">
                        <span style="color: #64748b;">Total Provisioned Accounts:</span>
                        <strong>' . count(isset($accounts['accounts']) ? $accounts['accounts'] : []) . '</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 0.85rem;">
                        <span style="color: #64748b;">Synchronized Kernel Slices:</span>
                        <strong>' . htmlspecialchars($sync_summary) . '</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.85rem;">
                        <span style="color: #64748b;">Active Overrides:</span>
                        <strong id="quick-overrides-count">0</strong>
                    </div>
                </div>
                <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                    <button class="uniselv-btn btn-outline" onclick="UniselvResMan.syncNativePlans()">
                        <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg> Bulk Sync All Plans
                    </button>
                    <button class="uniselv-btn btn-outline" onclick="UniselvResMan.switchTab(\'audit\')">
                        <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg> Audit Effective Limits
                    </button>
                </div>
            </div>
        </div>
    </div>';

    // TAB: USER HISTORICAL ANALYTICS & SNAPSHOTS
    echo '<div id="tab-analytics" class="uniselv-tab-content">
        <div class="uniselv-card mb-4" style="background: linear-gradient(to right, #f8fafc, #ffffff); border-left: 4px solid var(--uniselv-primary);">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 14px;">
                <div>
                    <h5 style="margin: 0 0 4px 0; font-weight: 700; color: #1e293b;">User Telemetry & Point-in-Time Snapshots</h5>
                    <p style="margin: 0; font-size: 0.88rem; color: #64748b;">Inspect individual hosting accounts using native Webuzo and Linux measurements: account totals, 8 telemetry charts, hourly rollups, live processes, and forensic snapshots.</p>
                </div>
                <div style="display: flex; gap: 10px; align-items: center;">
                    <label style="font-weight: 600; font-size: 0.88rem; color: #475569;">Select Account:</label>
                    <select id="admin-user-selector" class="uniselv-form-select" style="min-width: 260px; font-weight: 600; padding: 8px 12px; border-radius: 6px;" onchange="UniselvResMan.onAdminUserSelected(this.value)">';
    if (!empty($accounts['accounts'])) {
        foreach ($accounts['accounts'] as $acc) {
            echo '<option value="' . htmlspecialchars($acc['username']) . '">' . htmlspecialchars($acc['username']) . ' (' . htmlspecialchars($acc['domain']) . ' - ' . htmlspecialchars(strtoupper($acc['plan_name'])) . ')</option>';
        }
    }
    echo '          </select>
                </div>
            </div>
        </div>

        <!-- Sub-navigation: Current Usage vs Diagnostic Snapshots -->
        <div class="uniselv-cpanel-subtabs mb-4" style="border-bottom: 2px solid var(--uniselv-border); margin-bottom: 20px;">
            <button class="uniselv-cpanel-subtab active" id="admin-subtab-usage" onclick="UniselvResMan.switchAdminUserSubtab(\'usage\')">
                <svg width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="vertical-align: middle; margin-right: 4px;"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg> Current Usage
            </button>
            <button class="uniselv-cpanel-subtab" id="admin-subtab-snapshots" onclick="UniselvResMan.switchAdminUserSubtab(\'snapshots\')">
                <svg width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="vertical-align: middle; margin-right: 4px;"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"/></svg> Diagnostic Snapshots
            </button>
        </div>

        <!-- VIEW 1: CURRENT USAGE FOR SELECTED USER -->
        <div id="admin-view-usage">
            <!-- Top Toolbar: Timeframe & Time unit -->
            <div class="uniselv-cpanel-header" style="margin-bottom: 20px;">
                <div style="display: flex; align-items: center; gap: 14px; flex-wrap: wrap;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <label style="font-size: 0.88rem; font-weight: 600; color: #475569;">Timeframe:</label>
                        <select id="admin-usage-timeframe" class="uniselv-cpanel-select" onchange="UniselvResMan.loadAdminUserUsage(this.value)">
                            <option value="today" selected>Today</option>
                            <option value="yesterday">Yesterday</option>
                            <option value="24h">Last 24 Hours</option>
                            <option value="7d">Last 7 Days</option>
                            <option value="30d">Last 30 Days</option>
                        </select>
                    </div>
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <label style="font-size: 0.88rem; font-weight: 600; color: #475569;">Time unit:</label>
                        <select id="admin-usage-timeunit" class="uniselv-cpanel-select">
                            <option value="hour" selected>Hour</option>
                            <option value="minute">Minute</option>
                        </select>
                    </div>
                    <button class="uniselv-cpanel-btn" onclick="UniselvResMan.refreshAdminUserUsage()" title="Refresh Telemetry">
                        <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="vertical-align: middle; margin-right: 4px;"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg> Refresh
                    </button>
                    <span style="font-size: 0.88rem; color: #64748b; font-weight: 600;">Account: <span id="admin-usage-selected-user" style="color: var(--uniselv-primary);">--</span></span>
                </div>
                <div style="font-size: 0.84rem; color: #64748b;">
                    Server Time: <strong>' . date('Y-m-d H:i') . '</strong>
                </div>
            </div>

            <!-- 1. Account Total Card -->
            <div class="uniselv-card mb-4" id="admin-account-total-card">
                <h5 style="margin-bottom: 12px; font-weight: 700; font-size: 1.05rem; color: #1e293b;">Account Total</h5>
                <div class="uniselv-table-wrap">
                    <table class="uniselv-table" style="margin-bottom: 0;">
                        <thead>
                            <tr style="background:#f8fafc; font-size:0.82rem; text-transform:uppercase; color:#475569;">
                                <th>Description</th>
                                <th>Usage</th>
                                <th>Limit</th>
                                <th>Fault</th>
                            </tr>
                        </thead>
                        <tbody id="admin-account-total-tbody">
                            <tr><td colspan="4" style="text-align:center; color:#64748b; padding:20px;">Loading account totals...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- 2. 8 Interactive Charts Grid -->
            <div style="margin-bottom: 24px;">
                <h5 style="margin-bottom: 14px; font-weight: 700; font-size: 1.05rem; color: #1e293b;">Resource Charts</h5>
                <div id="admin-usage-8charts-grid" class="uniselv-charts-8grid">
                    <div style="grid-column: 1 / -1; text-align: center; color: #64748b; padding: 40px; background: #ffffff; border: 1px solid var(--uniselv-border); border-radius: 8px;">
                        Loading 8 interactive resource telemetry charts...
                    </div>
                </div>
            </div>

            <!-- 3. Usage Historical Rollup Table -->
            <div class="uniselv-card mb-4" id="admin-usage-rollup-card">
                <h5 style="margin-bottom: 12px; font-weight: 700; font-size: 1.05rem; color: #1e293b;">Usage</h5>
                <div class="uniselv-table-wrap">
                    <table class="uniselv-table uniselv-cpanel-usage-table" style="margin-bottom: 0;">
                        <thead>
                            <tr style="background:#f8fafc; font-size:0.8rem; text-transform:uppercase; color:#475569;">
                                <th rowspan="2" style="vertical-align:middle;">From</th>
                                <th rowspan="2" style="vertical-align:middle;">To</th>
                                <th colspan="3" style="text-align:center; border-left:1px solid #e2e8f0;">SPEED</th>
                                <th colspan="3" style="text-align:center; border-left:1px solid #e2e8f0;">PMEM</th>
                                <th colspan="3" style="text-align:center; border-left:1px solid #e2e8f0;">IO</th>
                                <th colspan="3" style="text-align:center; border-left:1px solid #e2e8f0;">EP</th>
                                <th colspan="3" style="text-align:center; border-left:1px solid #e2e8f0;">NPROC</th>
                                <th colspan="3" style="text-align:center; border-left:1px solid #e2e8f0;">IOPS</th>
                            </tr>
                            <tr style="background:#f1f5f9; font-size:0.75rem; color:#64748b; text-align:center;">
                                <th style="border-left:1px solid #e2e8f0;">a</th><th>l</th><th>f</th>
                                <th style="border-left:1px solid #e2e8f0;">a</th><th>l</th><th>f</th>
                                <th style="border-left:1px solid #e2e8f0;">a</th><th>l</th><th>f</th>
                                <th style="border-left:1px solid #e2e8f0;">a</th><th>l</th><th>f</th>
                                <th style="border-left:1px solid #e2e8f0;">a</th><th>l</th><th>f</th>
                                <th style="border-left:1px solid #e2e8f0;">a</th><th>l</th><th>f</th>
                            </tr>
                        </thead>
                        <tbody id="admin-usage-rollup-tbody">
                            <tr><td colspan="20" style="text-align:center; color:#64748b; padding:24px;">Loading hourly usage records...</td></tr>
                        </tbody>
                    </table>
                </div>
                <div id="admin-usage-rollup-pagination" class="uniselv-pagination-wrap"></div>
            </div>

            <!-- 4. Active Account Processes -->
            <div class="uniselv-card mb-4" id="admin-active-processes-card">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                    <h5 style="margin:0; font-weight:700; font-size:1.05rem; color:#1e293b;">Active Processes</h5>
                    <button class="uniselv-cpanel-btn" onclick="UniselvResMan.loadAdminUserProcesses()" title="Refresh Processes">Refresh Processes</button>
                </div>
                <div class="uniselv-table-wrap">
                    <table class="uniselv-table" style="margin-bottom:0;">
                        <thead>
                            <tr style="background:#f8fafc; font-size:0.8rem; text-transform:uppercase; color:#475569;">
                                <th style="width:100px;">PID</th>
                                <th>CMD</th>
                                <th style="width:110px; text-align:right;">CPU</th>
                                <th style="width:110px; text-align:right;">MEM</th>
                                <th style="width:100px; text-align:right;">Actions</th>
                            </tr>
                        </thead>
                        <tbody id="admin-live-processes-tbody">
                            <tr><td colspan="5" style="text-align:center; color:#64748b; padding:24px;">Loading active processes...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- VIEW 2: SNAPSHOTS INSPECTOR -->
        <div id="admin-view-snapshots" style="display: none;">
            <div class="uniselv-card mb-4" id="admin-snapshots-section">
                <div class="uniselv-cpanel-header" style="margin-bottom: 16px;">
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <h5 style="margin: 0; font-weight: 700; font-size: 1.15rem; color: #1e293b;">Snapshots</h5>
                        <div class="uniselv-cpanel-arrows">
                            <button class="uniselv-cpanel-btn" id="admin-snap-prev-btn" onclick="UniselvResMan.adminPrevSnapshot()" title="Previous Snapshot">&laquo;</button>
                            <button class="uniselv-cpanel-btn" id="admin-snap-next-btn" onclick="UniselvResMan.adminNextSnapshot()" title="Next Snapshot">&raquo;</button>
                        </div>
                    </div>
                    <div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap;">
                        <div style="display: flex; align-items: center; gap: 6px;">
                            <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="color: #64748b;"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
                            <select id="admin-snap-date-select" class="uniselv-cpanel-select" onchange="UniselvResMan.onAdminSnapshotDateChange(this.value)">
                                <option value="">Loading dates...</option>
                            </select>
                        </div>
                        <div style="display: flex; align-items: center; gap: 6px;">
                            <span style="font-size: 0.85rem; color: #64748b;">Choose snapshot:</span>
                            <select id="admin-snap-time-select" class="uniselv-cpanel-select" onchange="UniselvResMan.onAdminSnapshotTimeChange(this.value)">
                                <option value="">Loading snapshots...</option>
                            </select>
                        </div>
                        <span id="admin-snap-trigger-badge" class="uniselv-badge badge-normal" style="font-size: 0.75rem;">READY</span>
                    </div>
                </div>

                <!-- Subtabs bar: Process list / Database Queries / HTTP Queries -->
                <div class="uniselv-cpanel-subtabs">
                    <button class="uniselv-cpanel-subtab active" data-subtab="procs" onclick="UniselvResMan.setAdminSnapshotSubtab(\'procs\')">Process list</button>
                    <button class="uniselv-cpanel-subtab" data-subtab="db" onclick="UniselvResMan.setAdminSnapshotSubtab(\'db\')">Database Queries</button>
                    <button class="uniselv-cpanel-subtab" data-subtab="http" onclick="UniselvResMan.setAdminSnapshotSubtab(\'http\')">HTTP Queries</button>
                </div>

                <div id="admin-snap-content" style="padding-top: 14px;">
                    <div style="text-align: center; color: #64748b; padding: 30px;">Loading snapshot records...</div>
                </div>
            </div>
        </div>
    </div>';

    // TAB 3: AUDIT
    echo '<div id="tab-audit" class="uniselv-tab-content">
        <div class="uniselv-card mb-3">
            <h5 style="margin-bottom: 8px; font-weight: 700;">Configured versus Effective Cgroup Limits Audit</h5>
            <p style="color: #64748b; font-size: 0.88rem; margin-bottom: 14px;">Audits synchronization between Webuzo native configuration (/var/webuzo/cgroups), systemd slice files (/etc/systemd/system/*.slice), and kernel active cgroup v2 controllers (/sys/fs/cgroup).</p>
            <div class="uniselv-table-wrap">
                <table class="uniselv-table">
                    <thead>
                        <tr>
                            <th>Account</th>
                            <th>Plan</th>
                            <th>Configured CPU</th>
                            <th>Effective Cgroup CPU</th>
                            <th>Configured RAM</th>
                            <th>Effective Cgroup RAM</th>
                            <th>Configured I/O (R/W, MB/s)</th>
                            <th>Effective I/O (R/W, MiB/s)</th>
                            <th>Sync Health</th>
                        </tr>
                    </thead>
                    <tbody>';
    if (!empty($audit['audit'])) {
        foreach ($audit['audit'] as $row) {
            $is_sync = $row['is_synchronized'];
            $status_badge = !empty($is_sync) ? '<span class="uniselv-badge badge-normal">IN SYNC</span>' : '<span class="uniselv-badge badge-warning">DRIFT DETECTED</span>';
            $raw_rbw = isset($row['configured_read_bw']) ? $row['configured_read_bw'] : '0M';
            $raw_wbw = isset($row['configured_write_bw']) ? $row['configured_write_bw'] : '0M';
            $cfg_r_str = is_numeric($raw_rbw) ? round($raw_rbw / 1024 / 1024) . 'M' : $raw_rbw;
            $cfg_w_str = is_numeric($raw_wbw) ? round($raw_wbw / 1024 / 1024) . 'M' : $raw_wbw;
            $cfg_io = $cfg_r_str . ' / ' . $cfg_w_str;
            $eff_rbps = isset($row['effective_rbps']) ? $row['effective_rbps'] : 'max';
            $eff_wbps = isset($row['effective_wbps']) ? $row['effective_wbps'] : 'max';
            $eff_io = (is_numeric($eff_rbps) ? round($eff_rbps / 1024 / 1024) . 'M' : $eff_rbps) . ' / ' . (is_numeric($eff_wbps) ? round($eff_wbps / 1024 / 1024) . 'M' : $eff_wbps);

            echo '<tr>
                <td><strong>' . htmlspecialchars($row['username']) . '</strong> (UID ' . $row['uid'] . ')</td>
                <td>' . htmlspecialchars(strtoupper($row['plan_name'])) . '</td>
                <td>' . $row['configured_cpuquota'] . '%</td>
                <td>' . htmlspecialchars($row['effective_cpu_max']) . '</td>
                <td>' . round($row['configured_mem_max'] / 1024 / 1024) . ' MiB</td>
                <td>' . (is_numeric($row['effective_mem_max']) ? round($row['effective_mem_max'] / 1024 / 1024) . ' MiB' : htmlspecialchars($row['effective_mem_max'])) . '</td>
                <td>' . htmlspecialchars($cfg_io) . '</td>
                <td>' . htmlspecialchars($eff_io) . '</td>
                <td>' . $status_badge . '</td>
            </tr>';
        }
    }
    echo '          </tbody>
                </table>
            </div>
        </div>
    </div>';

    // TAB 4: GOLDEN SHIELD GOVERNANCE & CAPACITY
    $g_state = isset($golden['state']) ? $golden['state'] : 'Not installed';
    $g_badge = ($g_state === 'Active') ? 'badge-normal' : (($g_state === 'Degraded') ? 'badge-warning' : 'badge-critical');
    $g_msg = isset($golden['message']) ? $golden['message'] : 'Golden Shield governance is ready for configuration.';
    $g_mode = isset($golden['mode']) ? strtoupper($golden['mode']) : 'AUTO';
    $hw = isset($golden['hardware']) ? $golden['hardware'] : ['cpu_count' => 4, 'ram_total_mib' => 7752, 'swap_total_mib' => 1024, 'fingerprint' => ''];
    $calc = isset($golden['calculated_policy']) ? $golden['calculated_policy'] : [];
    $cfg = isset($golden['configured_policy']) ? $golden['configured_policy'] : [];
    $eff = isset($golden['effective_values']) ? $golden['effective_values'] : [];
    $outside = isset($golden['outside_processes']) ? $golden['outside_processes'] : [];

    echo '<div id="tab-goldenshield" class="uniselv-tab-content">
        <!-- Golden Shield Governance Banner Card -->
        <div class="uniselv-card mb-3" style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;">
            <div>
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
                    <h5 style="margin: 0; font-weight: 700;">Golden Shield Kernel Governor</h5>
                    <span class="uniselv-badge ' . $g_badge . '">' . htmlspecialchars(strtoupper($g_state)) . '</span>
                    <span class="uniselv-badge badge-outline">MODE: ' . htmlspecialchars($g_mode) . '</span>
                </div>
                <p style="margin: 0; color: #64748b; font-size: 0.88rem;">' . htmlspecialchars($g_msg) . '</p>
            </div>
            <div style="display: flex; gap: 8px;">
                ' . (($g_state === 'disabled' || $g_state === 'inactive') ? '
                <button class="uniselv-btn btn-success btn-sm" onclick="UniselvResMan.enableGoldenShield()">
                    <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg> Enable Governor
                </button>' : '
                <button class="uniselv-btn btn-danger btn-sm" onclick="UniselvResMan.disableGoldenShield()">
                    <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636"/></svg> Disable Governor
                </button>') . '
                <button class="uniselv-btn btn-primary btn-sm" onclick="UniselvResMan.openGoldenModal()">
                    <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"/></svg> Reconfigure
                </button>
                <button class="uniselv-btn btn-outline btn-sm" onclick="UniselvResMan.openRestoreBackupModal()">
                    <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg> Restore Backup
                </button>
                <button class="uniselv-btn btn-outline btn-sm" onclick="UniselvResMan.verifyGoldenShield()">
                    <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg> Run Verification
                </button>
            </div>
        </div>

        <!-- 4-Tier Governance Comparison Grid -->
        <div class="uniselv-grid" style="grid-template-columns: repeat(4, 1fr); margin-bottom: 20px;">
            <div class="uniselv-card">
                <div class="uniselv-card-header"><span class="uniselv-card-title">1. Detected Hardware</span></div>
                <div class="uniselv-card-value">' . (isset($hw['cpu_count']) ? $hw['cpu_count'] : 4) . ' vCPUs</div>
                <div class="uniselv-card-sub">
                    Visible RAM: <strong>' . (isset($hw['ram_total_mib']) ? round($hw['ram_total_mib'] / 1024, 2) : 8) . ' GiB</strong><br>
                    Swap Available: ' . (isset($hw['swap_total_mib']) ? $hw['swap_total_mib'] : 0) . ' MiB<br>
                    <small style="color:#94a3b8;">Hash: ' . substr(isset($hw['fingerprint']) ? $hw['fingerprint'] : '', 0, 12) . '...</small>
                </div>
            </div>
            <div class="uniselv-card">
                <div class="uniselv-card-header"><span class="uniselv-card-title">2. Calculated Policy (Auto)</span></div>
                <div class="uniselv-card-value">' . (isset($calc['customerCpuPercent']) ? $calc['customerCpuPercent'] : '') . '% Hosting</div>
                <div class="uniselv-card-sub">
                    Shared System: <strong>' . (isset($calc['reservedCpuPercent']) ? $calc['reservedCpuPercent'] : '') . '%</strong><br>
                    Hosting RAM Cap: <strong>' . (isset($calc['hostingMemoryMaxMiB']) ? $calc['hostingMemoryMaxMiB'] : '') . ' MiB</strong><br>
                    Reserve Headroom: ' . (isset($calc['headroomMiB']) ? $calc['headroomMiB'] : '') . ' MiB
                </div>
            </div>
            <div class="uniselv-card">
                <div class="uniselv-card-header"><span class="uniselv-card-title">3. Configured Policy</span></div>
                <div class="uniselv-card-value">' . (isset($cfg['customerCpuPercent']) ? $cfg['customerCpuPercent'] : '') . '% Quota</div>
                <div class="uniselv-card-sub">
                    System Headroom: <strong>' . (isset($cfg['reservedCpuPercent']) ? $cfg['reservedCpuPercent'] : '') . '%</strong><br>
                    Configured Memory: <strong>' . (isset($cfg['hostingMemoryMaxMiB']) ? $cfg['hostingMemoryMaxMiB'] : '') . ' MiB</strong><br>
                    Recovery Margin: ' . (isset($cfg['recoveryMarginMiB']) ? $cfg['recoveryMarginMiB'] : '') . ' MiB
                </div>
            </div>
            <div class="uniselv-card">
                <div class="uniselv-card-header"><span class="uniselv-card-title">4. Active Kernel Limits</span></div>
                <div class="uniselv-card-value">' . (isset($eff['aggregate_cpu_max']) ? $eff['aggregate_cpu_max'] : 'n/a') . '</div>
                <div class="uniselv-card-sub">
                    Memory Max: <strong>' . (isset($eff['aggregate_mem_max']) && is_numeric($eff['aggregate_mem_max']) ? round($eff['aggregate_mem_max'] / 1024 / 1024) . ' MiB' : 'n/a') . '</strong><br>
                    Swap Max: <strong>' . (isset($eff['aggregate_swap_max']) ? $eff['aggregate_swap_max'] : '0') . ' (Blocked)</strong><br>
                    Webuzo Admin: System.slice (Protected)
                </div>
            </div>
        </div>

        <!-- Escaped Process Audit & Coverage -->
        <div class="uniselv-card mb-3">
            <h5 style="font-weight: 700; margin-bottom: 10px;">Enforcement Coverage & Escaped Process Audit</h5>';
    if (!empty($outside)) {
        echo '<div style="background: #fef2f2; border: 1px solid #fecaca; border-radius: 8px; padding: 14px; margin-bottom: 14px; color: #991b1b; font-size: 0.88rem;">
            <strong>Warning: ' . count($outside) . ' customer process(es) detected running outside golden.slice!</strong> Workloads must run strictly inside their assigned boundaries.
        </div>
        <div class="uniselv-table-wrap">
            <table class="uniselv-table">
                <thead>
                    <tr><th>PID</th><th>Executable</th><th>Current Cgroup</th></tr>
                </thead>
                <tbody>';
        foreach ($outside as $op) {
            echo '<tr>
                <td>' . $op['pid'] . '</td>
                <td><code>' . htmlspecialchars($op['exe']) . '</code></td>
                <td><code>' . htmlspecialchars($op['cgroup']) . '</code></td>
            </tr>';
        }
        echo '  </tbody>
            </table>
        </div>';
    } else {
        echo '<div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 14px; color: #166534; font-size: 0.88rem; display: flex; align-items: center; gap: 8px;">
            <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
            <span><strong>Observed Process Coverage.</strong> ' . ($g_state === 'active' ? 'No escaped customer process was observed in the latest scan. This is a point-in-time check; use Run Verification to check effective limits and services.' : 'Containment is not verified while the governor is inactive, degraded, or unavailable. Use Run Verification and inspect the reported status.') . '</span>
        </div>';
    }
    echo '</div>

        <!-- Side-by-Side 2-Column Governance & Backup Restoration Grid -->
        <div class="uniselv-grid" style="grid-template-columns: repeat(auto-fit, minmax(420px, 1fr)); gap: 20px; margin-top: 24px;">
            <!-- Column 1: Reconfigure Golden Shield Governance -->
            <div class="uniselv-card" id="card-golden-reconfigure">
                <div class="uniselv-card-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                    <h5 style="margin: 0; font-weight: 700; display: flex; align-items: center; gap: 8px;">
                        <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="color: var(--uniselv-primary);"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"/></svg>
                        Reconfigure Golden Shield Governance
                    </h5>
                    <span class="uniselv-badge badge-outline">MODE: ' . htmlspecialchars($g_mode) . '</span>
                </div>
                <p style="font-size: 0.86rem; color: #64748b; margin-bottom: 14px;">Configure shared aggregate CPU headroom and physical memory safety thresholds. Manual values may reduce hosting capacity but cannot consume the hardware-scaled Auto reserve.</p>
                <div class="uniselv-form-group" style="margin-bottom: 12px;">
                    <label class="uniselv-form-label">Governance Mode</label>
                    <select id="golden-mode-select" class="uniselv-form-input" style="width: 100%;" onchange="UniselvResMan.onGoldenModeChange(this.value)">
                        <option value="AUTO" ' . ($g_mode === 'AUTO' ? 'selected' : '') . '>Auto (Hardware-Scaled 85% Hosting / 15% Headroom)</option>
                        <option value="MANUAL" ' . ($g_mode === 'MANUAL' ? 'selected' : '') . '>Advanced Manual Mode (Custom Overrides)</option>
                    </select>
                </div>
                <div id="golden-manual-fields" style="display: ' . ($g_mode === 'MANUAL' ? 'block' : 'none') . '; margin-bottom: 12px;">
                    <div style="margin-bottom: 12px;">
                        <label class="uniselv-form-label">Hosting Pool CPU Quota (%)</label>
                        <input type="number" id="golden-cpu-pct" value="' . (isset($cfg['customerCpuPercent']) ? $cfg['customerCpuPercent'] : '') . '" min="50" class="uniselv-form-input" style="width: 100%;">
                        <small style="color: #64748b; display: block; margin-top: 4px;">E.g. 340% for 4 vCPUs (leaving 60% shared system headroom).</small>
                    </div>
                    <div>
                        <label class="uniselv-form-label">Hosting Memory Cap (MiB)</label>
                        <input type="number" id="golden-mem-mib" value="' . (isset($cfg['hostingMemoryMaxMiB']) ? $cfg['hostingMemoryMaxMiB'] : '') . '" min="512" class="uniselv-form-input" style="width: 100%;">
                        <small style="color: #64748b; display: block; margin-top: 4px;">Enforces physical RAM safety boundary across all customer slices.</small>
                    </div>
                </div>
                <button class="uniselv-btn btn-primary" onclick="UniselvResMan.submitGoldenReconfigure()">
                    <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg> Save & Apply Policy
                </button>
            </div>

            <!-- Column 2: Restore Golden Shield Policy Backup -->
            <div class="uniselv-card" id="card-golden-restore">
                <div class="uniselv-card-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                    <h5 style="margin: 0; font-weight: 700; display: flex; align-items: center; gap: 8px;">
                        <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="color: #8b5cf6;"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
                        Restore Policy Backup Checkpoint
                    </h5>
                    <button class="uniselv-btn btn-outline btn-sm" onclick="UniselvResMan.refreshBackupsList()">
                        <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg> Refresh List
                    </button>
                </div>
                <p style="font-size: 0.86rem; color: #64748b; margin-bottom: 14px;">Select a verified configuration checkpoint to restore with automatic rollback protection.</p>
                <div id="uniselv-backups-container" style="max-height: 240px; overflow-y: auto; margin-bottom: 16px;">
                    <div style="text-align: center; padding: 20px; color: #64748b;">Loading configuration backups...</div>
                </div>
                <button class="uniselv-btn btn-primary" onclick="UniselvResMan.submitRestoreBackup()">
                    <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg> Restore Selected Backup
                </button>
            </div>
        </div>
    </div>';

    // TAB: CAPACITY PLANNING & OVERSELL
    echo '<div id="tab-capacity" class="uniselv-tab-content">
        <div class="uniselv-card mb-4">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 10px;">
                <div>
                    <h5 style="font-weight: 700; margin: 0 0 4px 0;"><svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="color: var(--uniselv-primary);"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"/></svg> Hardware Capacity & Oversell Governance (A11, G06)</h5>
                    <p style="font-size: 0.88rem; color: #64748b; margin: 0;">Evaluates committed/sold tenant allowances against physical hardware boundaries, Golden Shield shared pool quotas, and observed 24h peak concurrency.</p>
                </div>
                <button class="uniselv-btn btn-outline" onclick="UniselvResMan.loadCapacityPlanning()">
                    <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg> Refresh Assessment
                </button>
            </div>

            <div id="capacity-loading" style="text-align: center; padding: 30px; color: #64748b;">Loading hardware capacity metrics...</div>
            <div id="capacity-content" style="display: none;">
                <!-- Key Metrics Grid -->
                <div class="uniselv-grid" style="grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-bottom: 20px;">
                    <div class="uniselv-card" style="background: var(--uniselv-bg-subtle);">
                        <div class="uniselv-card-title">Capacity Risk Level</div>
                        <div id="cap-risk-badge" class="uniselv-badge badge-normal" style="font-size: 1rem; margin-top: 6px;">LOW</div>
                        <div class="uniselv-card-sub" id="cap-summary-desc" style="margin-top: 6px;">Safe operating margins</div>
                    </div>
                    <div class="uniselv-card" style="background: var(--uniselv-bg-subtle);">
                        <div class="uniselv-card-title">CPU Commit Ratio</div>
                        <div id="cap-cpu-commit" class="uniselv-card-value" style="font-size: 1.4rem;">--</div>
                        <div class="uniselv-card-sub" id="cap-cpu-sold-sub">Total sold vs Physical</div>
                    </div>
                    <div class="uniselv-card" style="background: var(--uniselv-bg-subtle);">
                        <div class="uniselv-card-title">Memory Commit Ratio</div>
                        <div id="cap-mem-commit" class="uniselv-card-value" style="font-size: 1.4rem;">--</div>
                        <div class="uniselv-card-sub" id="cap-mem-sold-sub">Total sold RAM vs Physical</div>
                    </div>
                    <div class="uniselv-card" style="background: var(--uniselv-bg-subtle);">
                        <div class="uniselv-card-title">Physical Server Boundary</div>
                        <div id="cap-physical-desc" class="uniselv-card-value" style="font-size: 1.2rem;">--</div>
                        <div class="uniselv-card-sub" id="cap-golden-pool-desc">Shared Headroom Pool</div>
                    </div>
                </div>

                <!-- Observed Decoupled Peaks Card (Finding 8 / A11) -->
                <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; margin-bottom: 20px;">
                    <h6 style="font-weight: 700; color: #1e293b; margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
                        <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="color: #2563eb;"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg>
                        Observed 24-Hour Concurrent Demand Peaks (Independent Historical Maxima)
                    </h6>
                    <p style="font-size: 0.85rem; color: #64748b; margin-bottom: 16px;">True independent telemetry maxima: CPU and Memory peaks are evaluated separately with independent timestamp tracking to reflect realistic cluster pressure.</p>
                    <div class="uniselv-grid" style="grid-template-columns: repeat(2, 1fr); gap: 20px;">
                        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px;">
                            <span style="font-size: 0.82rem; font-weight: 600; color: #64748b; text-transform: uppercase;">Peak Concurrent CPU Usage</span>
                            <div id="cap-peak-cpu-val" style="font-size: 1.5rem; font-weight: 700; color: #2563eb; margin: 4px 0;">-- %</div>
                            <div id="cap-peak-cpu-time" style="font-size: 0.8rem; color: #64748b;">Timestamp: Recorded UTC</div>
                        </div>
                        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px;">
                            <span style="font-size: 0.82rem; font-weight: 600; color: #64748b; text-transform: uppercase;">Peak Concurrent Memory Usage</span>
                            <div id="cap-peak-mem-val" style="font-size: 1.5rem; font-weight: 700; color: #059669; margin: 4px 0;">-- MiB</div>
                            <div id="cap-peak-mem-time" style="font-size: 0.8rem; color: #64748b;">Timestamp: Recorded UTC</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>';

    // TAB: SCHEDULED REPORTS
    echo '<div id="tab-reports" class="uniselv-tab-content">
        <div class="uniselv-card mb-4">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 10px;">
                <div>
                    <h5 style="font-weight: 700; margin: 0 0 4px 0;"><svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="color: var(--uniselv-primary);"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg> Automated Capacity & Security Reports (A16)</h5>
                    <p style="font-size: 0.88rem; color: #64748b; margin: 0;">Background daemon generates and stores periodic infrastructure reports on daily/weekly cadence.</p>
                </div>
                <div style="display: flex; gap: 10px; align-items: center; flex-wrap: wrap;">
                    <select id="scheduled-report-type" class="uniselv-form-input" style="width: auto; padding: 6px 12px;">
                        <option value="daily">Daily Report</option>
                        <option value="weekly">Weekly Report</option>
                    </select>
                    <button class="uniselv-btn btn-primary" onclick="UniselvResMan.dispatchReportNow()">
                        <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg> Dispatch Report Now
                    </button>
                    <button class="uniselv-btn btn-outline" onclick="UniselvResMan.loadScheduledReports()">
                        <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg> Refresh
                    </button>
                </div>
            </div>

            <!-- Schedule Automation Configuration Card (A16) -->
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 18px; margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 10px;">
                    <h6 style="font-weight: 700; color: #1e293b; margin: 0; display: flex; align-items: center; gap: 8px;">
                        <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="color: #2563eb;"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                        ' . __u('schedule_automation', $locale) . '
                    </h6>
                    <span id="report-schedule-status-badge" class="uniselv-badge badge-normal">Schedule: Daily Active</span>
                </div>
                <p style="font-size: 0.85rem; color: #64748b; margin-bottom: 16px;">Configure recurring background report generation cadence, target admin recipient, and monitor next scheduled dispatch epoch.</p>
                <div class="uniselv-grid" style="grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; align-items: end;">
                    <div class="uniselv-form-group" style="margin-bottom: 0;">
                        <label class="uniselv-form-label">Recurrence Cadence</label>
                        <select id="report-schedule-cadence" class="uniselv-select" style="width: 100%;">
                            <option value="daily">Daily (Every 24 Hours)</option>
                            <option value="weekly">Weekly (Every 7 Days)</option>
                            <option value="disabled">Disabled (Manual Only)</option>
                        </select>
                    </div>
                    <div class="uniselv-form-group" style="margin-bottom: 0;">
                        <label class="uniselv-form-label">Recipient / Target</label>
                        <input type="text" id="report-schedule-recipient" class="uniselv-form-input" style="width: 100%;" value="system_admin" placeholder="system_admin or email">
                    </div>
                    <div class="uniselv-form-group" style="margin-bottom: 0;">
                        <label class="uniselv-form-label">Next Due Dispatch</label>
                        <div id="report-schedule-next-due" style="font-weight: 600; font-size: 0.88rem; color: #1e293b; padding: 7px 0;">Calculating...</div>
                    </div>
                    <div style="margin-bottom: 0;">
                        <button class="uniselv-btn btn-primary" onclick="UniselvResMan.saveReportSchedule()" style="width: 100%;">
                            Save Schedule Settings
                        </button>
                    </div>
                </div>
            </div>

            <div class="uniselv-table-wrap">
                <table class="uniselv-table" id="reports-table">
                    <thead>
                        <tr>
                            <th>Report ID</th>
                            <th>Generated Time (UTC)</th>
                            <th>Period</th>
                            <th>Total Accounts</th>
                            <th>System Load</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody id="reports-table-body">
                        <tr><td colspan="7" style="text-align: center; color: #64748b; padding: 25px;">Loading scheduled reports...</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>';

    // TAB: BRANDING & BILLING INTEGRATIONS
    echo '<div id="tab-integrations" class="uniselv-tab-content">
        <div class="uniselv-grid" style="grid-template-columns: repeat(auto-fit, minmax(460px, 1fr)); gap: 20px;">
            <!-- Subcard 1: Branding & Localization (B02, B03) -->
            <div class="uniselv-card">
                <div class="uniselv-card-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                    <h5 style="margin: 0; font-weight: 700; display: flex; align-items: center; gap: 8px;">
                        <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="color: var(--uniselv-primary);"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01"/></svg>
                        Branding & Localization Settings (B02, B03)
                    </h5>
                </div>
                <p style="font-size: 0.86rem; color: #64748b; margin-bottom: 16px;">Customize plugin portal name, brand logo URL, primary accent color, and interface locale.</p>

                <div class="uniselv-form-group">
                    <label class="uniselv-form-label">Brand / Product Title</label>
                    <input type="text" id="brand-name-input" class="uniselv-form-input" style="max-width: 100%;" value="' . $brand_name . '">
                </div>
                <div class="uniselv-form-group">
                    <label class="uniselv-form-label">Brand Logo Image URL (Optional)</label>
                    <input type="text" id="brand-logo-input" class="uniselv-form-input" style="max-width: 100%;" placeholder="https://yourdomain.com/logo.png" value="' . $brand_logo . '">
                    <small style="color: #64748b;">Leave blank to use default UNISELV SVG icon.</small>
                </div>
                <div class="uniselv-form-group">
                    <label class="uniselv-form-label">Primary Theme Accent Color</label>
                    <div style="display: flex; gap: 10px; align-items: center;">
                        <input type="color" id="brand-color-picker" value="' . $brand_color . '" style="width: 44px; height: 38px; border-radius: 6px; border: 1px solid var(--uniselv-border); cursor: pointer;" onchange="document.getElementById(\'brand-color-input\').value = this.value">
                        <input type="text" id="brand-color-input" class="uniselv-form-input" style="max-width: 120px;" value="' . $brand_color . '" onchange="document.getElementById(\'brand-color-picker\').value = this.value">
                    </div>
                </div>
                <div class="uniselv-form-group">
                    <label class="uniselv-form-label">Support Portal Link</label>
                    <input type="text" id="brand-support-input" class="uniselv-form-input" style="max-width: 100%;" value="' . $brand_support . '">
                </div>
                <div class="uniselv-form-group">
                    <label class="uniselv-form-label">Documentation URL</label>
                    <input type="text" id="brand-docs-input" class="uniselv-form-input" style="max-width: 100%;" value="' . $brand_docs . '">
                </div>
                <div class="uniselv-form-group">
                    <label class="uniselv-form-label">Default UI Language Locale</label>
                    <select id="brand-locale-select" class="uniselv-form-input" style="max-width: 100%;">
                        <option value="en"' . ($locale === 'en' ? ' selected' : '') . '>English (Default)</option>
                        <option value="bn"' . ($locale === 'bn' ? ' selected' : '') . '>বাংলা (Bengali)</option>
                    </select>
                </div>
                <button class="uniselv-btn btn-primary" onclick="UniselvResMan.saveBrandingSettings()">
                    <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg> Save Branding & Theme
                </button>
            </div>

            <!-- Subcard 2: Package Mappings CRUD (B05) -->
            <div class="uniselv-card">
                <div class="uniselv-card-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                    <h5 style="margin: 0; font-weight: 700; display: flex; align-items: center; gap: 8px;">
                        <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="color: #059669;"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"/></svg>
                        Billing Package Mappings (B05)
                    </h5>
                    <button class="uniselv-btn btn-outline btn-sm" onclick="UniselvResMan.loadPackageMappings()">
                        <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg> Refresh
                    </button>
                </div>
                <p style="font-size: 0.86rem; color: #64748b; margin-bottom: 16px;">Map WHMCS, Blesta, or custom billing package names to Webuzo native cgroup resource plans.</p>

                <!-- Mapping Table -->
                <div style="max-height: 220px; overflow-y: auto; margin-bottom: 16px;">
                    <table class="uniselv-table" style="font-size: 0.84rem;">
                        <thead>
                            <tr><th>Billing Package</th><th>Webuzo Plan</th><th>Action</th></tr>
                        </thead>
                        <tbody id="package-mappings-body">
                            <tr><td colspan="3" style="text-align: center; color: #64748b; padding: 15px;">Loading mappings...</td></tr>
                        </tbody>
                    </table>
                </div>

                <!-- Add/Edit Mapping Form -->
                <div style="background: var(--uniselv-bg-subtle); border: 1px solid var(--uniselv-border); border-radius: 8px; padding: 14px;">
                    <h6 style="font-weight: 600; margin-bottom: 10px; font-size: 0.88rem;">Add / Update Mapping</h6>
                    <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                        <input type="text" id="map-billing-pkg" class="uniselv-form-input" placeholder="e.g. Bronze Plan" style="flex: 1; min-width: 140px;">
                        <select id="map-target-plan" class="uniselv-form-input" style="flex: 1; min-width: 130px;">' . $native_plan_options . '</select>
                        <button class="uniselv-btn btn-primary" onclick="UniselvResMan.savePackageMapping()">Save</button>
                    </div>
                </div>

                <!-- Subcard 3: External Webhook Documentation (B06, B07) -->
                <div style="margin-top: 20px; border-top: 1px solid var(--uniselv-border); padding-top: 16px;">
                    <h6 style="font-weight: 700; color: #1e293b; margin-bottom: 8px;">Billing Webhook Integration Endpoint (B06, B07)</h6>
                    <p style="font-size: 0.84rem; color: #64748b; margin-bottom: 8px;">External billing systems (WHMCS post-provisioning hooks, Blesta events) can synchronize user plans securely with transactional rollback:</p>
                    <div style="background: #0f172a; color: #f8fafc; padding: 12px; border-radius: 8px; font-size: 0.78rem; font-family: monospace; overflow-x: auto; margin-bottom: 8px;">
Admin session required: port 2005, subact=adapter_sync, POST form data and the current CSRF token.<br>
External integrations use subact=webhook with configured Bearer/HMAC authentication. The Webuzo routing layer must also authorize the request.<br>
Do not use the customer port (2003). An unattended external provider route has not been validated by this release; verify it with a dedicated test account before connecting billing.
                    </div>
                </div>

                <!-- Subcard 4: Role & Account Feature Permissions Governance (B04) -->
                <div style="margin-top: 24px; border-top: 1px solid var(--uniselv-border); padding-top: 20px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                        <h6 style="font-weight: 700; color: #1e293b; margin: 0; display: flex; align-items: center; gap: 8px;">
                            <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="color: #6366f1;"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/></svg>
                            Role & Account Feature Permissions Governance (B04)
                        </h6>
                        <button class="uniselv-btn btn-outline btn-sm" onclick="UniselvResMan.loadPermissions()">
                            <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg> Refresh Permissions
                        </button>
                    </div>
                    <p style="font-size: 0.84rem; color: #64748b; margin-bottom: 16px;">Configure role baselines and per-account granular overrides for enduser process termination, telemetry exports, and historical queries.</p>

                    <div class="uniselv-grid" style="grid-template-columns: 1fr 1fr; gap: 20px;">
                        <!-- Role Baselines -->
                        <div style="background: #f8fafc; border: 1px solid var(--uniselv-border); border-radius: 8px; padding: 16px;">
                            <h6 style="font-size: 0.88rem; font-weight: 700; color: #1e293b; margin-bottom: 12px;">Role-Level Baselines</h6>
                            <table class="uniselv-table" style="font-size: 0.82rem;">
                                <thead><tr><th>Role</th><th>Permission</th><th>Granted</th><th>Action</th></tr></thead>
                                <tbody id="role-permissions-body"><tr><td colspan="4" style="text-align:center; color:#64748b; padding:10px;">Loading...</td></tr></tbody>
                            </table>
                        </div>

                        <!-- Account Granular Overrides -->
                        <div style="background: #f8fafc; border: 1px solid var(--uniselv-border); border-radius: 8px; padding: 16px;">
                            <h6 style="font-size: 0.88rem; font-weight: 700; color: #1e293b; margin-bottom: 12px;">Granular Account Overrides</h6>
                            <div style="display: flex; gap: 8px; margin-bottom: 12px; flex-wrap: wrap;">
                                <input type="text" id="perm-user-input" class="uniselv-form-input" placeholder="Username (e.g. ub1)" style="flex: 1; min-width: 120px; font-size: 0.82rem;">
                                <select id="perm-key-select" class="uniselv-form-input" style="flex: 1; min-width: 160px; font-size: 0.82rem;">
                                    <option value="can_stop_processes">can_stop_processes</option>
                                    <option value="can_export_diagnostics">can_export_diagnostics</option>
                                    <option value="can_view_history">can_view_history</option>
                                </select>
                                <select id="perm-grant-select" class="uniselv-form-input" style="width: 100px; font-size: 0.82rem;">
                                    <option value="1">Allow</option>
                                    <option value="0">Deny</option>
                                </select>
                                <button class="uniselv-btn btn-primary btn-sm" onclick="UniselvResMan.saveAccountPermission()">Apply Override</button>
                            </div>
                            <table class="uniselv-table" style="font-size: 0.82rem;">
                                <thead><tr><th>Account</th><th>Permission</th><th>Status</th><th>Updated By</th></tr></thead>
                                <tbody id="account-permissions-body"><tr><td colspan="4" style="text-align:center; color:#64748b; padding:10px;">No overrides configured.</td></tr></tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>';

    // TAB: ADMINISTRATIVE AUDIT LOG (B08)
    echo '<div id="tab-auditlog" class="uniselv-tab-content">
        <div class="uniselv-card mb-4">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 10px;">
                <div>
                    <h5 style="font-weight: 700; margin: 0 0 4px 0;"><svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="color: var(--uniselv-primary);"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg> Administrative Audit History (B08)</h5>
                    <p style="font-size: 0.88rem; color: #64748b; margin: 0;">Searchable, exportable administrative audit history tracking all boost allocations, policy changes, plan modifications, and system rollbacks.</p>
                </div>
                <div style="display: flex; gap: 10px; align-items: center; flex-wrap: wrap;">
                    <input type="text" id="audit-search-input" class="uniselv-form-input" placeholder="Search actor, action, account..." style="width: 220px;" onkeyup="if(event.key===\'Enter\') UniselvResMan.loadAuditLogs()">
                    <select id="audit-action-filter" class="uniselv-form-input" style="width: auto;" onchange="UniselvResMan.loadAuditLogs()">
                        <option value="">All Actions</option>
                        <option value="set_override">set_override</option>
                        <option value="cancel_override">cancel_override</option>
                        <option value="save_native_plan">save_native_plan</option>
                        <option value="save_package_mapping">save_package_mapping</option>
                        <option value="adapter_sync">adapter_sync</option>
                        <option value="dispatch_report">dispatch_report</option>
                        <option value="golden_reconfigure">golden_reconfigure</option>
                        <option value="save_branding">save_branding</option>
                    </select>
                    <button class="uniselv-btn btn-primary" onclick="UniselvResMan.loadAuditLogs()">
                        <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg> Filter
                    </button>
                    <button class="uniselv-btn btn-outline" style="color: #ef4444; border-color: #fca5a5;" onclick="UniselvResMan.clearAuditLogs()" title="Clear administrative audit records">
                        <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg> Clear Log
                    </button>
                </div>
            </div>

            <div class="uniselv-table-wrap">
                <table class="uniselv-table" id="audit-log-table">
                    <thead>
                        <tr>
                            <th>Timestamp (UTC)</th>
                            <th>Actor</th>
                            <th>Action</th>
                            <th>Target</th>
                            <th>Details</th>
                        </tr>
                    </thead>
                    <tbody id="audit-log-body">
                        <tr><td colspan="5" style="text-align: center; color: #64748b; padding: 25px;">Loading administrative audit logs...</td></tr>
                    </tbody>
                </table>
            </div>
            <div id="uniselv-audit-pagination" class="uniselv-pagination-wrap"></div>
        </div>
    </div>';

    // TAB 5: HEALTH, FEATURE GOVERNANCE & RETENTION SETTINGS
    echo '<div id="tab-health" class="uniselv-tab-content">
        <!-- Card 1: Feature Controls & Self-Service Governance -->
        <div class="uniselv-card mb-4">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 10px;">
                <div>
                    <h5 style="font-weight: 700; margin: 0 0 4px 0;"><i class="fas fa-sliders-h"></i> System Settings & Feature Governance</h5>
                    <p style="font-size: 0.88rem; color: #64748b; margin: 0;">Configure background agent behaviors, automated diagnostic triggers, visual threshold alerts, and enduser self-service capabilities.</p>
                </div>
                <button class="uniselv-btn btn-primary" id="btn-save-features" onclick="UniselvResMan.saveFeatureSettings()">
                    <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg> Save Feature Settings
                </button>
            </div>

            <div class="uniselv-grid" style="grid-template-columns: repeat(2, 1fr); gap: 20px;">
                
                <!-- Section A: Telemetry & Engine Frequency -->
                <div style="background: var(--uniselv-bg-subtle); border: 1px solid var(--uniselv-border); border-radius: 12px; padding: 18px;">
                    <h6 style="font-weight: 700; color: #1e293b; margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
                        <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="color: var(--uniselv-primary);"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
                        Telemetry & Sampling Engine
                    </h6>
                    
                    <div class="uniselv-switch-container">
                        <div class="uniselv-switch-text">
                            <div class="uniselv-switch-title">Telemetry Collection Engine</div>
                            <div class="uniselv-switch-desc">Continuously sample cgroups v2 metrics and account CPU/RAM usage.</div>
                        </div>
                        <label class="uniselv-switch">
                            <input type="checkbox" id="setting-telemetry-enabled" checked>
                            <span class="uniselv-slider"></span>
                        </label>
                    </div>

                    <div class="uniselv-form-group" style="margin-top: 12px;">
                        <label class="uniselv-form-label">Telemetry Sampling Frequency</label>
                        <select id="setting-telemetry-interval" class="uniselv-form-input" style="max-width: 100%;">
                            <option value="5">5 Seconds — Ultra Responsive (Default / Recommended)</option>
                            <option value="10">10 Seconds — Balanced Production</option>
                            <option value="15">15 Seconds — Low CPU Overhead</option>
                            <option value="30">30 Seconds — Minimal Headroom</option>
                        </select>
                        <small style="color: #64748b; display: block; margin-top: 4px;">Controls the background sampling frequency across all customer cgroup slices.</small>
                    </div>

                    <div class="uniselv-switch-container" style="margin-top: 12px; margin-bottom: 0;">
                        <div class="uniselv-switch-text">
                            <div class="uniselv-switch-title">Hourly Auto-Pruning & WAL Truncate</div>
                            <div class="uniselv-switch-desc">Automatically purge expired samples and reclaim disk space every hour.</div>
                        </div>
                        <label class="uniselv-switch">
                            <input type="checkbox" id="setting-auto-prune" checked>
                            <span class="uniselv-slider"></span>
                        </label>
                    </div>
                </div>

                <!-- Section B: Automated Forensic Diagnostics -->
                <div style="background: var(--uniselv-bg-subtle); border: 1px solid var(--uniselv-border); border-radius: 12px; padding: 18px;">
                    <h6 style="font-weight: 700; color: #1e293b; margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
                        <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="color: #8b5cf6;"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
                        Automated Incident Snapshots
                    </h6>

                    <div class="uniselv-switch-container">
                        <div class="uniselv-switch-text">
                            <div class="uniselv-switch-title">Capture on CPU Throttling</div>
                            <div class="uniselv-switch-desc">Save process tree and active HTTP traces when quota is exhausted.</div>
                        </div>
                        <label class="uniselv-switch">
                            <input type="checkbox" id="setting-snap-throttle" checked>
                            <span class="uniselv-slider"></span>
                        </label>
                    </div>

                    <div class="uniselv-switch-container">
                        <div class="uniselv-switch-text">
                            <div class="uniselv-switch-title">Capture on OOM (Out Of Memory) Kill</div>
                            <div class="uniselv-switch-desc">Capture forensic state when kernel terminates an account worker.</div>
                        </div>
                        <label class="uniselv-switch">
                            <input type="checkbox" id="setting-snap-oom" checked>
                            <span class="uniselv-slider"></span>
                        </label>
                    </div>

                    <div class="uniselv-switch-container">
                        <div class="uniselv-switch-text">
                            <div class="uniselv-switch-title">Capture on Task / PID Max Ceiling</div>
                            <div class="uniselv-switch-desc">Record snapshots when an account hits thread ceiling or fork limits.</div>
                        </div>
                        <label class="uniselv-switch">
                            <input type="checkbox" id="setting-snap-task" checked>
                            <span class="uniselv-slider"></span>
                        </label>
                    </div>

                    <div class="uniselv-form-group" style="margin-top: 10px; margin-bottom: 0;">
                        <label class="uniselv-form-label">Incident Snapshot Cooldown (Seconds)</label>
                        <input type="number" id="setting-snap-cooldown" min="5" max="600" class="uniselv-form-input" style="max-width: 100%;" value="60">
                        <small style="color: #64748b; display: block; margin-top: 4px;">Minimum interval between snapshots per tenant to guard against burst storage flood.</small>
                    </div>
                </div>

                <!-- Section C: Visual Warning Thresholds -->
                <div style="background: var(--uniselv-bg-subtle); border: 1px solid var(--uniselv-border); border-radius: 12px; padding: 18px;">
                    <h6 style="font-weight: 700; color: #1e293b; margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
                        <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="color: var(--uniselv-warning);"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
                        Warning Alert Thresholds
                    </h6>
                    <p style="font-size: 0.8rem; color: #64748b; margin-bottom: 14px;">Controls when dashboard progress bars and status badges switch to ELEVATED / WARNING states.</p>

                    <div class="uniselv-form-group">
                        <label class="uniselv-form-label">CPU Warning Threshold (% of Assigned Allowance)</label>
                        <input type="number" id="setting-thresh-cpu" min="10" max="99" class="uniselv-form-input" style="max-width: 100%;" value="75">
                        <small style="color: #64748b; display: block; margin-top: 4px;">Default: 75%. Displays orange warning badge when exceeded.</small>
                    </div>

                    <div class="uniselv-form-group">
                        <label class="uniselv-form-label">Memory Warning Threshold (% of Assigned RAM)</label>
                        <input type="number" id="setting-thresh-mem" min="10" max="99" class="uniselv-form-input" style="max-width: 100%;" value="80">
                        <small style="color: #64748b; display: block; margin-top: 4px;">Default: 80%. Displays moderate pressure warning badge.</small>
                    </div>

                    <div class="uniselv-form-group" style="margin-bottom: 0;">
                        <label class="uniselv-form-label">Active Tasks / PIDs Warning Threshold (% of Limit)</label>
                        <input type="number" id="setting-thresh-tasks" min="10" max="99" class="uniselv-form-input" style="max-width: 100%;" value="80">
                        <small style="color: #64748b; display: block; margin-top: 4px;">Default: 80%. Warns when worker threads approach ceiling.</small>
                    </div>
                </div>

                <!-- Section D: Enduser Self-Service Permissions -->
                <div style="background: var(--uniselv-bg-subtle); border: 1px solid var(--uniselv-border); border-radius: 12px; padding: 18px;">
                    <h6 style="font-weight: 700; color: #1e293b; margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
                        <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="color: var(--uniselv-success);"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"/></svg>
                        Enduser Self-Service Permissions
                    </h6>
                    <p style="font-size: 0.8rem; color: #64748b; margin-bottom: 14px;">Govern capabilities and troubleshooting actions available in customer control panels.</p>

                    <div class="uniselv-switch-container">
                        <div class="uniselv-switch-text">
                            <div class="uniselv-switch-title">Allow Process Termination</div>
                            <div class="uniselv-switch-desc">Tenants can safely terminate their own runaway PHP workers via PIDFD identity checks.</div>
                        </div>
                        <label class="uniselv-switch">
                            <input type="checkbox" id="setting-allow-kill" checked>
                            <span class="uniselv-slider"></span>
                        </label>
                    </div>

                    <div class="uniselv-switch-container">
                        <div class="uniselv-switch-text">
                            <div class="uniselv-switch-title">Allow Support Report Export</div>
                            <div class="uniselv-switch-desc">Tenants can download 24h JSON telemetry & incident traces for technical support.</div>
                        </div>
                        <label class="uniselv-switch">
                            <input type="checkbox" id="setting-allow-export" checked>
                            <span class="uniselv-slider"></span>
                        </label>
                    </div>

                    <div class="uniselv-switch-container" style="margin-bottom: 0;">
                        <div class="uniselv-switch-text">
                            <div class="uniselv-switch-title">Allow MySQL Query Forensics</div>
                            <div class="uniselv-switch-desc">Tenants can inspect active slow queries belonging to their database in incident snapshots.</div>
                        </div>
                        <label class="uniselv-switch">
                            <input type="checkbox" id="setting-allow-db-trace" checked>
                            <span class="uniselv-slider"></span>
                        </label>
                    </div>
                </div>

            </div>
        </div>

        <!-- Side-by-Side 2-Column Storage & Health Grid -->
        <div class="uniselv-grid" style="grid-template-columns: repeat(auto-fit, minmax(460px, 1fr)); gap: 20px;">
            <!-- Card 2: Telemetry Storage & Retention Policy -->
            <div class="uniselv-card">
                <h5 style="font-weight: 700; margin-bottom: 12px;"><i class="fas fa-database"></i> Telemetry Storage & Retention Policy</h5>
                <p style="font-size: 0.88rem; color: #64748b; margin-bottom: 16px;">Configure sliding-window retention thresholds to prevent unbounded SQLite disk growth. Automated hourly maintenance purges stale records, while manual pruning can be triggered immediately.</p>
                
                <div style="background: var(--uniselv-bg-subtle); border: 1px solid var(--uniselv-border); border-radius: 8px; padding: 16px; margin-bottom: 20px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.9rem; font-weight: 600;">
                        <span>Current Database Footprint: <strong id="storage-total-display">Loading...</strong> of <span id="storage-limit-display">100 MiB</span> warning threshold</span>
                        <span id="storage-used-pct" class="uniselv-badge badge-normal">0%</span>
                    </div>
                    <div class="uniselv-storage-bar-bg">
                        <div id="storage-bar-fill" class="uniselv-storage-bar-fill" style="width: 1%;"></div>
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-top: 14px; font-size: 0.82rem; color: #475569;">
                        <div><strong>Samples:</strong> <span id="storage-samples-count">--</span></div>
                        <div><strong>Snapshots:</strong> <span id="storage-snapshots-count">--</span></div>
                        <div><strong>Incident Events:</strong> <span id="storage-events-count">--</span></div>
                        <div><strong>Audit Logs:</strong> <span id="storage-audit-count">--</span></div>
                    </div>
                </div>

                <div class="uniselv-grid" style="grid-template-columns: repeat(2, 1fr); gap: 18px; margin-bottom: 20px;">
                    <div class="uniselv-form-group">
                        <label class="uniselv-form-label">Telemetry Samples Retention (Days)</label>
                        <input type="number" id="retention-samples" min="1" max="365" class="uniselv-form-input" value="30">
                        <small style="color: #64748b; display: block; margin-top: 4px;">High-resolution CPU, memory, and I/O records.</small>
                    </div>
                    <div class="uniselv-form-group">
                        <label class="uniselv-form-label">Diagnostic Snapshots Retention (Days)</label>
                        <input type="number" id="retention-snapshots" min="1" max="90" class="uniselv-form-input" value="14">
                        <small style="color: #64748b; display: block; margin-top: 4px;">Process hierarchy, HTTP traces, and slow SQL query snapshots.</small>
                    </div>
                    <div class="uniselv-form-group">
                        <label class="uniselv-form-label">Resource Events & Throttling Incidents (Days)</label>
                        <input type="number" id="retention-events" min="1" max="180" class="uniselv-form-input" value="30">
                        <small style="color: #64748b; display: block; margin-top: 4px;">CPU throttling events, OOM terminations, and task exhaustion alerts.</small>
                    </div>
                    <div class="uniselv-form-group">
                        <label class="uniselv-form-label">Audit Trail Logs Retention (Days)</label>
                        <input type="number" id="retention-audit" min="7" max="365" class="uniselv-form-input" value="90">
                        <small style="color: #64748b; display: block; margin-top: 4px;">Administrative plan mutations, overrides, and billing webhook entries.</small>
                    </div>
                </div>

                <div class="uniselv-form-group">
                    <label class="uniselv-form-label" for="retention-max-storage">Storage Warning Threshold (MiB)</label>
                    <input type="number" id="retention-max-storage" min="10" max="102400" class="uniselv-form-input" value="100">
                    <small>Usage indicator only, not a hard disk quota. Retention pruning follows the days above.</small>
                </div>
                <div style="display: flex; gap: 12px; align-items: center; margin-bottom: 10px; flex-wrap: wrap;">
                    <button id="btn-save-retention" class="uniselv-btn btn-primary" onclick="UniselvResMan.saveStorageSettings()">
                        Save Retention Policy
                    </button>
                    <button id="btn-prune-db" class="uniselv-btn btn-danger" onclick="UniselvResMan.pruneDatabaseNow()">
                        Prune & Optimize Database Now
                    </button>
                    <button id="btn-purge-snapshots" class="uniselv-btn btn-outline" style="color: #ef4444; border-color: #fca5a5;" onclick="UniselvResMan.openPurgeSnapshotsModal()">
                        <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg> Purge Snapshots...
                    </button>
                </div>
            </div>

            <!-- Card 3: Background Daemon Health & Maintenance Mode -->
            <div class="uniselv-card">
                <h5 style="font-weight: 700; margin-bottom: 12px;">Background Daemon Health</h5>
                <p style="font-size: 0.88rem; color: #64748b; margin-bottom: 16px;">Telemetry collection agent status, runtime memory footprint, and maintenance mode controls.</p>
                <div class="uniselv-grid" style="grid-template-columns: repeat(3, 1fr); margin-bottom: 16px;">
                    <div>
                        <label style="font-size: 0.85rem; color:#64748b;">Agent PID</label>
                        <div style="font-weight: 700; font-size: 1.1rem;">' . (isset($health['agent_pid']) ? $health['agent_pid'] : 'Unavailable') . '</div>
                    </div>
                    <div>
                        <label style="font-size: 0.85rem; color:#64748b;">Agent Memory (RSS)</label>
                        <div style="font-weight: 700; font-size: 1.1rem;">' . (isset($health['agent_rss_formatted']) ? $health['agent_rss_formatted'] : 'Unavailable') . '</div>
                    </div>
                    <div>
                        <label style="font-size: 0.85rem; color:#64748b;">Systemd Memory Constraint</label>
                        <div style="font-weight: 700; font-size: 1.1rem; color: var(--uniselv-success);">' . (isset($health['memory_cap_formatted']) ? htmlspecialchars($health['memory_cap_formatted']) : 'Unavailable') . '</div>
                    </div>
                </div>

                <div style="display: flex; gap: 14px; align-items: center; flex-wrap: wrap; margin-top: 20px;">
                    <button class="uniselv-btn btn-outline" onclick="UniselvResMan.toggleMaintenanceMode(' . (empty($health['maintenance_mode']) ? 'true' : 'false') . ')">
                        ' . (empty($health['maintenance_mode']) ? 'Enable Maintenance Mode' : 'Disable Maintenance Mode') . '
                    </button>
                    <small style="color: #64748b;">Pauses automated telemetry changes and background events during maintenance work.</small>
                </div>
            </div>
        </div>
    </div>';

    // TAB 6: HELP & ABOUT (ADMIN)
    if (file_exists(__DIR__ . '/views/admin_help.php')) {
        include __DIR__ . '/views/admin_help.php';
    }

    // Temporary Override Modal
    echo '<div id="uniselv-override-modal" class="uniselv-modal-overlay" style="display: none;">
        <div class="uniselv-modal">
            <h4 style="font-weight: 700; margin-bottom: 14px;">Grant Temporary Resource Boost</h4>
            <p style="font-size: 0.88rem; color: #64748b; margin-bottom: 16px;">Temporarily boost account <strong id="override-target-display"></strong>. The boost automatically expires and cleanly restores the original plan.</p>
            <input type="hidden" id="override-username">
            <div style="margin-bottom: 14px;">
                <label style="font-weight: 600; font-size: 0.85rem; display: block; margin-bottom: 6px;">Select Boosted Plan:</label>
                <select id="override-plan" class="form-select" style="width: 100%; padding: 8px; border-radius: 6px; border: 1px solid var(--uniselv-border);">' . $native_plan_options . '</select>
            </div>
            <div style="margin-bottom: 14px;">
                <label style="font-weight: 600; font-size: 0.85rem; display: block; margin-bottom: 6px;">Duration (Minutes):</label>
                <input type="number" id="override-duration" value="60" style="width: 100%; padding: 8px; border-radius: 6px; border: 1px solid var(--uniselv-border);">
            </div>
            <div style="margin-bottom: 18px;">
                <label style="font-weight: 600; font-size: 0.85rem; display: block; margin-bottom: 6px;">Reason:</label>
                <input type="text" id="override-reason" value="Temporary high-traffic event" style="width: 100%; padding: 8px; border-radius: 6px; border: 1px solid var(--uniselv-border);">
            </div>
            <div style="display: flex; justify-content: flex-end; gap: 10px;">
                <button class="uniselv-btn btn-outline" onclick="UniselvResMan.closeModal(\'uniselv-override-modal\')">Cancel</button>
                <button class="uniselv-btn btn-primary" onclick="UniselvResMan.submitOverride()">Apply Boost</button>
            </div>
        </div>
    </div>';

    // Golden Shield Reconfigure Modal
    echo '<div id="uniselv-golden-modal" class="uniselv-modal-overlay" style="display: none;">
        <div class="uniselv-modal">
            <h4 style="font-weight: 700; margin-bottom: 14px;">Reconfigure Golden Shield Governance</h4>
            <p style="font-size: 0.88rem; color: #64748b; margin-bottom: 16px;">Configure shared aggregate CPU headroom and physical memory safety thresholds. Manual values may reduce hosting capacity but cannot consume the hardware-scaled Auto reserve.</p>
            <div style="margin-bottom: 14px;">
                <label style="font-weight: 600; font-size: 0.85rem; display: block; margin-bottom: 6px;">Governance Mode:</label>
                <select id="golden-mode" class="form-select" style="width: 100%; padding: 8px; border-radius: 6px; border: 1px solid var(--uniselv-border);" onchange="UniselvResMan.onGoldenModeChange(this.value)">
                    <option value="auto" ' . ($g_mode === 'AUTO' ? 'selected' : '') . '>Auto (Hardware-Scaled 85% Hosting / 15% Headroom)</option>
                    <option value="manual" ' . ($g_mode === 'MANUAL' ? 'selected' : '') . '>Advanced Manual Mode (Custom Overrides)</option>
                </select>
            </div>
            <div id="golden-manual-fields-modal" style="display: ' . ($g_mode === 'MANUAL' ? 'block' : 'none') . ';">
                <div style="margin-bottom: 14px;">
                    <label style="font-weight: 600; font-size: 0.85rem; display: block; margin-bottom: 6px;">Hosting Pool CPU Quota (%):</label>
                    <input type="number" id="golden-cpu-pct-modal" value="' . (isset($cfg['customerCpuPercent']) ? $cfg['customerCpuPercent'] : '') . '" min="50" style="width: 100%; padding: 8px; border-radius: 6px; border: 1px solid var(--uniselv-border);">
                    <small style="color: #64748b;">E.g. 340% for 4 vCPUs (leaving 60% system headroom).</small>
                </div>
                <div style="margin-bottom: 14px;">
                    <label style="font-weight: 600; font-size: 0.85rem; display: block; margin-bottom: 6px;">Hosting Memory Cap (MiB):</label>
                    <input type="number" id="golden-mem-mib-modal" value="' . (isset($cfg['hostingMemoryMaxMiB']) ? $cfg['hostingMemoryMaxMiB'] : '') . '" min="512" style="width: 100%; padding: 8px; border-radius: 6px; border: 1px solid var(--uniselv-border);">
                </div>
            </div>
            <div style="display: flex; justify-content: flex-end; gap: 10px;">
                <button class="uniselv-btn btn-outline" onclick="UniselvResMan.closeModal(\'uniselv-golden-modal\')">Cancel</button>
                <button class="uniselv-btn btn-primary" onclick="UniselvResMan.submitGoldenReconfigure()">Save & Apply</button>
            </div>
        </div>
    </div>';

    // Golden Shield Restore Backup Modal
    echo '<div id="uniselv-restore-modal" class="uniselv-modal-overlay" style="display: none;">
        <div class="uniselv-modal" style="max-width: 600px;">
            <h4 style="font-weight: 700; margin-bottom: 8px;">Restore Golden Shield Policy Backup</h4>
            <p style="font-size: 0.88rem; color: #64748b; margin-bottom: 16px;">Select a verified configuration checkpoint to restore. The system validates the schema, checks path traversal safety, applies kernel memory caps and CPU quotas, and automatically creates a rollback checkpoint.</p>
            <div id="uniselv-backups-container-modal" style="max-height: 280px; overflow-y: auto; margin-bottom: 20px;">
                <div style="text-align: center; padding: 20px; color: #64748b;">Loading configuration backups...</div>
            </div>
            <div style="display: flex; justify-content: flex-end; gap: 10px;">
                <button class="uniselv-btn btn-outline" onclick="UniselvResMan.closeModal(\'uniselv-restore-modal\')">Cancel</button>
                <button class="uniselv-btn btn-primary" onclick="UniselvResMan.submitRestoreBackup()">Restore Selected Backup</button>
            </div>
        </div>
    </div>';

    echo uniselv_render_developer_footer();
    echo '</div>'; // End container
    echo '<script>UniselvResMan.init(window.location.href, true, "' . htmlspecialchars($SESS['user']) . '", "' . uniselv_csrf_token($SESS['user']) . '");</script>';
}

// ==================== ENDUSER PANEL INTEGRATION ====================

if (function_exists('add_filter')) {
    add_filter('enduser_cats_icons', 'uniselv_resman_enduser_cats_icons', 10, 1);
}
function uniselv_resman_enduser_cats_icons($icons) {
    global $globals;
    $icons['apps']['icons']['uniselv-resman'] = [
        'name' => 'Resource Usage',
        'icon' => $globals['panel_url'] . '/uniselv-resman/images/logo.png',
        'href' => $globals['index'] . 'act=uniselv-resman',
    ];
    return $icons;
}

if (function_exists('enduser_act')) {
    enduser_act('uniselv-resman', 'uniselv_resman_enduser');
}
function uniselv_resman_enduser() {
    global $globals, $SESS;

    $current_user = isset($SESS['user']) ? $SESS['user'] : '';

    if (isset($_REQUEST['api']) && $_REQUEST['api'] === 'json') {
        header('Content-Type: application/json');
        $subact = isset($_REQUEST['subact']) ? $_REQUEST['subact'] : '';
        $params = $_POST;

        if (in_array($subact, ['stop_process', 'mark_notification'])) {
            uniselv_verify_csrf($current_user);
        }

        $action_map = [
            'dashboard' => 'get_enduser_dashboard',
            'history' => 'get_enduser_history',
            'processes' => 'get_enduser_processes',
            'stop_process' => 'stop_enduser_process',
            'snapshots' => 'get_enduser_snapshots',
            'snapshots_index' => 'get_snapshots_index',
            'snapshot_detail' => 'get_snapshot_detail',
            'notifications' => 'get_enduser_notifications',
            'mark_notification' => 'mark_notification',
            'export_report' => 'get_enduser_support_export'
        ];

        if (isset($action_map[$subact])) {
            $resp = UniselvApiClient::call($action_map[$subact], $params, $current_user, false);
            echo json_encode($resp);
        } else {
            echo json_encode(['error' => 'Unknown enduser subaction']);
        }
        exit(0);
    }

    if (function_exists('theme_for_act')) {
        theme_for_act('uniselv_resman_enduser_theme', 'uniselv-resman');
    }
}

function uniselv_resman_enduser_theme() {
    global $globals, $SESS;

    $current_user = isset($SESS['user']) ? $SESS['user'] : '';
    $dash = UniselvApiClient::call('get_enduser_dashboard', [], $current_user, false);
    $procs = UniselvApiClient::call('get_enduser_processes', [], $current_user, false);
    $notifs = UniselvApiClient::call('get_enduser_notifications', [], $current_user, false);
    $snaps = UniselvApiClient::call('get_enduser_snapshots', ['limit' => 10], $current_user, false);
    $branding = UniselvApiClient::call('get_branding_settings', [], $current_user, false);

    $brand_name = !empty($branding['brand_name']) ? htmlspecialchars($branding['brand_name']) : 'UNISELV Resource Manager';
    $brand_logo = !empty($branding['brand_logo_url']) ? uniselv_safe_brand_url($branding['brand_logo_url']) : '';
    $brand_color = !empty($branding['brand_primary_color']) && preg_match('/^#[0-9a-fA-F]{6}$/', $branding['brand_primary_color']) ? $branding['brand_primary_color'] : '#2563eb';
    $brand_support = !empty($branding['brand_support_url']) ? uniselv_safe_brand_url($branding['brand_support_url']) : 'https://uniselv.com/support';
    $brand_docs = !empty($branding['brand_docs_url']) ? uniselv_safe_brand_url($branding['brand_docs_url']) : '';
    if (rtrim($brand_docs, '/') === 'https://docs.uniselv.com') $brand_docs = ''; // Historical placeholder; use bundled local Help.

    $cur = isset($dash['current']) ? $dash['current'] : [];
    $limits = isset($dash['limits']) ? $dash['limits'] : [];

    $panel_url = !empty($globals['panel_url']) ? rtrim($globals['panel_url'], '/') : '';
    $i18n_dict = uniselv_get_i18n_dict();

    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '">';
    echo '<style>:root { --uniselv-primary: ' . $brand_color . '; --primary-color: ' . $brand_color . '; }</style>';
    echo '<script>
window.UNISELV_LOCALE = ' . json_encode($locale) . ';
window.UNISELV_TRANSLATIONS = ' . json_encode($i18n_dict[$locale] ?? $i18n_dict['en']) . ';
</script>';
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '"></script>';

    echo '<div class="uniselv-container">';

    // Header
    echo '<div class="uniselv-header">
        <div class="uniselv-brand">
            <div class="uniselv-logo-icon">
                ' . (!empty($brand_logo) ? '<img src="' . $brand_logo . '" alt="' . $brand_name . '" style="max-height: 38px; max-width: 38px; object-fit: contain;">' : '<svg width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 4a2 2 0 114 0v1a1 1 0 001 1h3a1 1 0 011 1v3a1 1 0 01-1 1h-1a2 2 0 100 4h1a1 1 0 011 1v3a1 1 0 01-1 1h-3a1 1 0 01-1-1v-1a2 2 0 10-4 0v1a1 1 0 01-1 1H7a1 1 0 01-1-1v-3a1 1 0 00-1-1H4a2 2 0 110-4h1a1 1 0 001-1V7a1 1 0 011-1h3a1 1 0 001-1V4z"/></svg>') . '
            </div>
            <div>
                <h2 class="uniselv-brand-title">' . $brand_name . '</h2>
                <p class="uniselv-brand-subtitle">Account: <strong>' . htmlspecialchars($current_user) . '</strong> (' . htmlspecialchars(isset($dash['domain']) ? $dash['domain'] : '') . ') &bull; Assigned Plan: <strong>' . htmlspecialchars(strtoupper(isset($dash['plan_name']) ? $dash['plan_name'] : 'DEFAULT')) . '</strong></p>
            </div>
        </div>
        <div style="display: flex; gap: 10px; align-items: center; flex-wrap: wrap;">
            <a href="' . $brand_support . '" target="_blank" class="uniselv-help-pill" style="text-decoration: none;">
                <svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192l-3.536 3.536M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-5 0a4 4 0 11-8 0 4 4 0 018 0z"/></svg> Support
            </a>
            <button class="uniselv-help-pill" onclick="UniselvResMan.openHelpTopic(\'quickstart\')">
                <svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg> Help Guide
            </button>
            <div class="uniselv-live-badge" id="uniselv-telemetry-freshness">Reading latest telemetry sample...</div>
            <button class="uniselv-btn btn-outline" id="uniselv-export-btn" onclick="UniselvResMan.exportReport()">
                <svg width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg> Export Support Report
            </button>
        </div>
    </div>';

    // Tabs
    echo '<div class="uniselv-tabs">
        <button class="uniselv-tab-btn active" data-tab="dashboard" id="tab-btn-dashboard">
            <svg class="uniselv-tab-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/></svg> Dashboard
        </button>
        <button class="uniselv-tab-btn" data-tab="processes" id="tab-btn-processes">
            <svg class="uniselv-tab-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg> Current Usage
        </button>
        <button class="uniselv-tab-btn" data-tab="history" id="tab-btn-history">
            <svg class="uniselv-tab-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"/></svg> Historical Charts
        </button>
        <button class="uniselv-tab-btn" data-tab="snapshots" id="tab-btn-snapshots">
            <svg class="uniselv-tab-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"/></svg> Snapshots (<span id="uniselv-snaps-count-badge">' . (isset($snaps['count']) ? $snaps['count'] : 0) . '</span>)
        </button>
        <button class="uniselv-tab-btn" data-tab="notifications" id="tab-btn-notifications">
            <svg class="uniselv-tab-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/></svg> Notifications & Events (<span id="uniselv-notif-count-badge">' . count(isset($notifs['events']) ? $notifs['events'] : []) . '</span>)
        </button>
        <button class="uniselv-tab-btn" data-tab="help" id="tab-btn-help">
            <svg class="uniselv-tab-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg> Help & About
        </button>
    </div>';

    // TAB 1: DASHBOARD
    $cpu_val = isset($cur['cpu_used_percent_core']) ? $cur['cpu_used_percent_core'] : (isset($cur['cpu_percent']) ? $cur['cpu_percent'] : 0);
    $cpu_allowance = isset($cur['cpu_allowance_percent']) ? $cur['cpu_allowance_percent'] : 0;
    $cpu_quota = isset($limits['cpu_quota_percent']) ? $limits['cpu_quota_percent'] : (isset($limits['cpuquota']) ? $limits['cpuquota'] : 100);
    $cpu_badge = ($cpu_allowance > 90) ? 'badge-critical' : (($cpu_allowance > 60) ? 'badge-warning' : 'badge-normal');
    $cpu_status = ($cpu_allowance > 90) ? 'LIMIT EXCEEDED' : (($cpu_allowance > 60) ? 'ELEVATED' : 'NORMAL');

    $mem_val = isset($cur['mem_current_formatted']) ? $cur['mem_current_formatted'] : '0 B';
    $mem_pct = isset($cur['mem_percent']) ? $cur['mem_percent'] : 0;
    $mem_limit = isset($limits['mem_max_formatted']) ? $limits['mem_max_formatted'] : '1 GiB';
    $mem_badge = ($mem_pct > 90) ? 'badge-critical' : (($mem_pct > 65) ? 'badge-warning' : 'badge-normal');
    $mem_status = ($mem_pct > 90) ? 'HIGH PRESSURE' : (($mem_pct > 65) ? 'MODERATE' : 'NORMAL');

    $task_val = isset($cur['tasks_current']) ? $cur['tasks_current'] : 0;
    $task_limit = isset($limits['tasks_max']) ? $limits['tasks_max'] : (isset($limits['maxtask']) ? $limits['maxtask'] : 64);
    $task_pct = isset($cur['tasks_percent']) ? $cur['tasks_percent'] : 0;
    $io_limit_str = (!empty($limits['read_bw_formatted']) && !empty($limits['write_bw_formatted'])) ? ' | Limit: ' . $limits['read_bw_formatted'] . ' R / ' . $limits['write_bw_formatted'] . ' W' : '';
    $io_pct = isset($cur['io_percent']) ? floatval($cur['io_percent']) : 0;
    $io_badge = ($io_pct > 90) ? 'badge-critical' : (($io_pct > 65) ? 'badge-warning' : 'badge-normal');
    $io_status = ($io_pct > 90) ? 'THROTTLED' : (($io_pct > 65) ? 'ELEVATED' : 'NORMAL');

    echo '<div id="tab-dashboard" class="uniselv-tab-content active">';
    echo '<div class="uniselv-grid">
        <!-- CPU Card -->
        <div class="uniselv-card" id="uniselv-card-cpu">
            <div class="uniselv-card-header">
                <div class="uniselv-card-title-wrap">
                    <div class="uniselv-card-icon icon-cpu">
                        <svg viewBox="0 0 24 24" stroke="currentColor" fill="none"><rect x="4" y="4" width="16" height="16" rx="2" stroke-width="2"/><rect x="9" y="9" width="6" height="6" stroke-width="2"/><path stroke-linecap="round" stroke-width="2" d="M9 1v3M15 1v3M9 20v3M15 20v3M20 9h3M20 15h3M1 9h3M1 15h3"/></svg>
                    </div>
                    <span class="uniselv-card-title">CPU Usage</span>
                </div>
                <span class="uniselv-badge ' . $cpu_badge . '" id="uniselv-badge-cpu">' . $cpu_status . '</span>
            </div>
            <div class="uniselv-card-mid">
                <div class="uniselv-card-val-wrap">
                    <span class="uniselv-metric-big" id="uniselv-val-cpu">' . $cpu_val . '%</span>
                    <span class="uniselv-metric-core" id="uniselv-core-cpu">(' . round($cpu_val / 100, 2) . ' Core)</span>
                </div>
                <div class="uniselv-sparkline-wrap" aria-hidden="true" title="Waiting for measured samples">
                    <svg class="uniselv-sparkline-svg" viewBox="0 0 100 40">
                        <defs>
                            <linearGradient id="cpu-grad" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="0%" stop-color="#3b82f6" stop-opacity="0.3"/>
                                <stop offset="100%" stop-color="#3b82f6" stop-opacity="0.0"/>
                            </linearGradient>
                        </defs>
                        <path d="" fill="url(#cpu-grad)"/>
                        <path d="" fill="none" stroke="#3b82f6" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                </div>
            </div>
            <div class="uniselv-progress-bg">
                <div class="uniselv-progress-bar bar-cpu ' . (($cpu_allowance > 90) ? 'bg-danger' : (($cpu_allowance > 60) ? 'bg-warning' : '')) . '" id="uniselv-bar-cpu" style="width: ' . min(100, $cpu_allowance) . '%;"></div>
            </div>
            <div class="uniselv-card-sub" id="uniselv-sub-cpu">Allowance: <strong>' . $cpu_allowance . '%</strong> used of ' . $cpu_quota . '% limit (100% = 1 CPU Core)</div>
        </div>

        <!-- Memory Card -->
        <div class="uniselv-card" id="uniselv-card-mem">
            <div class="uniselv-card-header">
                <div class="uniselv-card-title-wrap">
                    <div class="uniselv-card-icon icon-mem">
                        <svg viewBox="0 0 24 24" stroke="currentColor" fill="none"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4"/></svg>
                    </div>
                    <span class="uniselv-card-title">Account Memory</span>
                </div>
                <span class="uniselv-badge ' . $mem_badge . '" id="uniselv-badge-mem">' . $mem_status . '</span>
            </div>
            <div class="uniselv-card-mid">
                <div class="uniselv-card-val-wrap">
                    <span class="uniselv-metric-big" id="uniselv-val-mem">' . $mem_val . '</span>
                </div>
                <div class="uniselv-sparkline-wrap" aria-hidden="true" title="Waiting for measured samples">
                    <svg class="uniselv-sparkline-svg" viewBox="0 0 100 40">
                        <defs>
                            <linearGradient id="mem-grad" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="0%" stop-color="#8b5cf6" stop-opacity="0.3"/>
                                <stop offset="100%" stop-color="#8b5cf6" stop-opacity="0.0"/>
                            </linearGradient>
                        </defs>
                        <path d="" fill="url(#mem-grad)"/>
                        <path d="" fill="none" stroke="#8b5cf6" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                </div>
            </div>
            <div class="uniselv-progress-bg">
                <div class="uniselv-progress-bar bar-mem ' . (($mem_pct > 90) ? 'bg-danger' : (($mem_pct > 65) ? 'bg-warning' : '')) . '" id="uniselv-bar-mem" style="width: ' . min(100, $mem_pct) . '%;"></div>
            </div>
            <div class="uniselv-card-sub" id="uniselv-sub-mem">Limit: <strong>' . $mem_limit . '</strong> (App: ' . (isset($cur['mem_anon_formatted']) ? $cur['mem_anon_formatted'] : '0 B') . ' | Cache: ' . (isset($cur['mem_file_cache_formatted']) ? $cur['mem_file_cache_formatted'] : '0 B') . ')</div>
        </div>

        <!-- Disk IO Card -->
        <div class="uniselv-card" id="uniselv-card-io">
            <div class="uniselv-card-header">
                <div class="uniselv-card-title-wrap">
                    <div class="uniselv-card-icon icon-io">
                        <svg viewBox="0 0 24 24" stroke="currentColor" fill="none"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4"/></svg>
                    </div>
                    <span class="uniselv-card-title">I/O Throughput</span>
                </div>
                <span class="uniselv-badge ' . $io_badge . '" id="uniselv-badge-io">' . $io_status . '</span>
            </div>
            <div class="uniselv-card-mid">
                <div class="uniselv-card-val-wrap">
                    <span class="uniselv-metric-big" id="uniselv-val-io">' . (isset($cur['total_bw_formatted']) ? $cur['total_bw_formatted'] : (isset($cur['read_bw_formatted']) ? $cur['read_bw_formatted'] : '0.0 MiB/s')) . '</span>
                    <span class="uniselv-metric-core" id="uniselv-unit-io">Total</span>
                </div>
                <div class="uniselv-sparkline-wrap" aria-hidden="true" title="Waiting for measured samples">
                    <svg class="uniselv-sparkline-svg" viewBox="0 0 100 40">
                        <defs>
                            <linearGradient id="io-grad" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="0%" stop-color="#10b981" stop-opacity="0.3"/>
                                <stop offset="100%" stop-color="#10b981" stop-opacity="0.0"/>
                            </linearGradient>
                        </defs>
                        <path d="" fill="url(#io-grad)"/>
                        <path d="" fill="none" stroke="#10b981" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                </div>
            </div>
            <div class="uniselv-progress-bg">
                <div class="uniselv-progress-bar bar-io ' . (($io_pct > 90) ? 'bg-danger' : (($io_pct > 65) ? 'bg-warning' : '')) . '" id="uniselv-bar-io" style="width: ' . min(100, $io_pct) . '%;"></div>
            </div>
            <div class="uniselv-card-sub" id="uniselv-sub-io">Read: ' . (isset($cur['read_bw_formatted']) ? $cur['read_bw_formatted'] : '0.0 MiB/s') . ' | Write: ' . (isset($cur['write_bw_formatted']) ? $cur['write_bw_formatted'] : '0.0 MiB/s') . ' | IOPS: ' . (isset($cur['read_iops']) ? $cur['read_iops'] : 0) . ' R / ' . (isset($cur['write_iops']) ? $cur['write_iops'] : 0) . ' W' . $io_limit_str . '</div>
        </div>

        <!-- Tasks Card -->
        <div class="uniselv-card" id="uniselv-card-tasks">
            <div class="uniselv-card-header">
                <div class="uniselv-card-title-wrap">
                    <div class="uniselv-card-icon icon-tasks">
                        <svg viewBox="0 0 24 24" stroke="currentColor" fill="none"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
                    </div>
                    <span class="uniselv-card-title">Tasks & Threads</span>
                </div>
                <span class="uniselv-badge badge-normal" id="uniselv-badge-tasks">NORMAL</span>
            </div>
            <div class="uniselv-card-mid">
                <div class="uniselv-card-val-wrap">
                    <span class="uniselv-metric-big" id="uniselv-val-tasks">' . $task_val . '</span>
                    <span class="uniselv-metric-core" id="uniselv-max-tasks">/ ' . $task_limit . '</span>
                </div>
                <div class="uniselv-sparkline-wrap" aria-hidden="true" title="Waiting for measured samples">
                    <svg class="uniselv-sparkline-svg" viewBox="0 0 100 40">
                        <defs>
                            <linearGradient id="tasks-grad" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="0%" stop-color="#f59e0b" stop-opacity="0.3"/>
                                <stop offset="100%" stop-color="#f59e0b" stop-opacity="0.0"/>
                            </linearGradient>
                        </defs>
                        <path d="" fill="url(#tasks-grad)"/>
                        <path d="" fill="none" stroke="#f59e0b" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                </div>
            </div>
            <div class="uniselv-progress-bg">
                <div class="uniselv-progress-bar bar-tasks ' . (($task_pct > 90) ? 'bg-danger' : '') . '" id="uniselv-bar-tasks" style="width: ' . min(100, $task_pct) . '%;"></div>
            </div>
            <div class="uniselv-card-sub" id="uniselv-sub-tasks">Includes Linux process threads. Limit: <strong>' . $task_limit . '</strong> max</div>
        </div>
    </div>';

    // Summary alert if pressure
    if ($cur['cpu_throttled_events'] > 0 || $cur['oom_kill_events'] > 0) {
        echo '<div class="uniselv-card mb-4" style="border-left: 4px solid var(--uniselv-danger); background: var(--uniselv-danger-bg); margin-top: 20px;">';
        echo '<h6 style="color: var(--uniselv-danger); font-weight: 700; margin-bottom: 4px;">Recent Resource Pressure Detected</h6>';
        echo '<p style="color: #7f1d1d; font-size: 0.9rem; margin: 0;">Your account recently hit resource ceilings (' . $cur['cpu_throttled_events'] . ' CPU throttling periods, ' . $cur['oom_kill_events'] . ' OOM terminations). Review the Notifications and Snapshots tabs for diagnostic traces.</p>';
        echo '</div>';
    }

    $php_workers = isset($dash['php_workers']) ? $dash['php_workers'] : ['total_workers' => 0, 'total_busy' => 0, 'total_idle' => 0, 'by_version' => []];
    $upgrade = isset($dash['upgrade_recommendation']) ? $dash['upgrade_recommendation'] : [];
    $opt = isset($dash['optimization_guidance']) ? $dash['optimization_guidance'] : [];

    echo '<!-- PHP Workers & Optimization Guidance (U10, U16, U17) -->
    <div class="uniselv-grid" style="grid-template-columns: repeat(auto-fit, minmax(420px, 1fr)); gap: 20px; margin-top: 20px;">
        <!-- Column 1: PHP Pool Worker Status (U10) -->
        <div class="uniselv-card">
            <div class="uniselv-card-header" style="margin-bottom: 12px;">
                <h5 style="margin: 0; font-weight: 700; display: flex; align-items: center; gap: 8px;">
                    <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="color: var(--uniselv-primary);"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/></svg>
                    PHP Workers & Engine Telemetry
                </h5>
                <span class="uniselv-badge badge-normal">' . $php_workers['total_workers'] . ' Total</span>
            </div>
            <p style="font-size: 0.86rem; color: #64748b; margin-bottom: 14px;">Active worker pools, concurrency state, and process queues running for this account.</p>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 16px; text-align: center;">
                <div style="background: var(--uniselv-bg-subtle); padding: 10px; border-radius: 8px; border: 1px solid var(--uniselv-border);">
                    <div style="font-size: 0.8rem; color: #64748b;">Active Workers</div>
                    <div style="font-size: 1.2rem; font-weight: 700; color: #1e293b;">' . $php_workers['total_workers'] . '</div>
                </div>
                <div style="background: var(--uniselv-bg-subtle); padding: 10px; border-radius: 8px; border: 1px solid var(--uniselv-border);">
                    <div style="font-size: 0.8rem; color: #64748b;">Busy (Executing)</div>
                    <div style="font-size: 1.2rem; font-weight: 700; color: #2563eb;">' . $php_workers['total_busy'] . '</div>
                </div>
                <div style="background: var(--uniselv-bg-subtle); padding: 10px; border-radius: 8px; border: 1px solid var(--uniselv-border);">
                    <div style="font-size: 0.8rem; color: #64748b;">Idle (Waiting)</div>
                    <div style="font-size: 1.2rem; font-weight: 700; color: #10b981;">' . $php_workers['total_idle'] . '</div>
                </div>
            </div>';

    if (!empty($php_workers['by_version'])) {
        echo '<div class="uniselv-table-wrap">
            <table class="uniselv-table">
                <thead><tr><th>Engine Version</th><th>Active</th><th>Busy</th><th>Idle</th><th>Queue</th></tr></thead>
                <tbody>';
        foreach ($php_workers['by_version'] as $pw) {
            echo '<tr>
                <td><strong>' . htmlspecialchars($pw['version']) . '</strong></td>
                <td>' . $pw['active'] . '</td>
                <td><span style="color:#2563eb; font-weight:600;">' . $pw['busy'] . '</span></td>
                <td><span style="color:#10b981; font-weight:600;">' . $pw['idle'] . '</span></td>
                <td>' . $pw['queue_length'] . '</td>
            </tr>';
        }
        echo '</tbody></table></div>';
    } else {
        echo '<div style="font-size: 0.86rem; color: #64748b; text-align: center; padding: 12px;">No active PHP worker pools currently spawned. Workers scale dynamically on inbound HTTP traffic.</div>';
    }
    echo '</div>

        <!-- Column 2: Growth & Optimization Recommendations (U16, U17) -->
        <div class="uniselv-card">
            <div class="uniselv-card-header" style="margin-bottom: 12px;">
                <h5 style="margin: 0; font-weight: 700; display: flex; align-items: center; gap: 8px;">
                    <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="color: #10b981;"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"/></svg>
                    Capacity & Optimization Guidance
                </h5>
                <span class="uniselv-badge ' . ((isset($upgrade['status']) && $upgrade['status'] === 'UPGRADE_RECOMMENDED') ? 'badge-warning' : 'badge-normal') . '">' . (isset($upgrade['status']) ? htmlspecialchars($upgrade['status']) : 'OPTIMAL') . '</span>
            </div>
            <p style="font-size: 0.86rem; color: #64748b; margin-bottom: 14px;">' . (isset($upgrade['summary']) ? htmlspecialchars($upgrade['summary']) : 'Resource profile is balanced.') . '</p>
            
            <div style="background: var(--uniselv-bg-subtle); border: 1px solid var(--uniselv-border); border-radius: 8px; padding: 14px; margin-bottom: 14px;">
                <div style="font-weight: 600; font-size: 0.85rem; color: #1e293b; margin-bottom: 6px;">Measured Primary Bottleneck:</div>
                <div style="font-size: 0.88rem; color: #475569;">' . (isset($opt['primary_bottleneck']) ? htmlspecialchars($opt['primary_bottleneck']) : 'No active bottleneck detected') . '</div>
            </div>';

    if (!empty($opt['recommendations'])) {
        echo '<div style="font-size: 0.84rem; color: #334155;"><strong>Actionable Recommendations:</strong><ul style="margin: 6px 0 0 16px; padding: 0;">';
        foreach (array_slice($opt['recommendations'], 0, 3) as $rec) {
            echo '<li style="margin-bottom: 4px;">' . htmlspecialchars($rec) . '</li>';
        }
        echo '</ul></div>';
    }
    echo '</div>
    </div>';

    echo '</div>'; // End Tab 1

    // TAB 2: CURRENT USAGE (cPanel CloudLinux Parity)
    echo '<div id="tab-processes" class="uniselv-tab-content">
        <!-- Top Toolbar: Timeframe & Time unit -->
        <div class="uniselv-cpanel-header" style="margin-bottom: 20px;">
            <div style="display: flex; align-items: center; gap: 14px; flex-wrap: wrap;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <label style="font-size: 0.88rem; font-weight: 600; color: #475569;">Timeframe:</label>
                    <select id="uniselv-usage-timeframe" class="uniselv-cpanel-select" onchange="UniselvResMan.loadCurrentUsage(this.value)">
                        <option value="today" selected>Today</option>
                        <option value="yesterday">Yesterday</option>
                        <option value="24h">Last 24 Hours</option>
                        <option value="7d">Last 7 Days</option>
                        <option value="30d">Last 30 Days</option>
                    </select>
                </div>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <label style="font-size: 0.88rem; font-weight: 600; color: #475569;">Time unit:</label>
                    <select id="uniselv-usage-timeunit" class="uniselv-cpanel-select">
                        <option value="hour" selected>Hour</option>
                        <option value="minute">Minute</option>
                    </select>
                </div>
                <button class="uniselv-cpanel-btn" onclick="UniselvResMan.refreshCurrentUsage()" title="Refresh Telemetry">
                    <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="vertical-align: middle; margin-right: 4px;"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg> Refresh
                </button>
            </div>
            <div style="font-size: 0.84rem; color: #64748b;">
                Server Time: <strong>' . date('Y-m-d H:i') . '</strong>
            </div>
        </div>

        <!-- 1. Account Total Card (cPanel Parity) -->
        <div class="uniselv-card mb-4" id="uniselv-account-total-card">
            <h5 style="margin-bottom: 12px; font-weight: 700; font-size: 1.05rem; color: #1e293b;">Account Total</h5>
            <div class="uniselv-table-wrap">
                <table class="uniselv-table" style="margin-bottom: 0;">
                    <thead>
                        <tr style="background:#f8fafc; font-size:0.82rem; text-transform:uppercase; color:#475569;">
                            <th>Description</th>
                            <th>Usage</th>
                            <th>Limit</th>
                            <th>Fault</th>
                        </tr>
                    </thead>
                    <tbody id="uniselv-account-total-tbody">
                        <tr><td colspan="4" style="text-align:center; color:#64748b; padding:20px;">Loading account totals...</td></tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- 2. 8 Interactive Charts Grid (cPanel Parity) -->
        <div style="margin-bottom: 24px;">
            <h5 style="margin-bottom: 14px; font-weight: 700; font-size: 1.05rem; color: #1e293b;">Resource Charts</h5>
            <div id="uniselv-usage-8charts-grid" class="uniselv-charts-8grid">
                <div style="grid-column: 1 / -1; text-align: center; color: #64748b; padding: 40px; background: #ffffff; border: 1px solid var(--uniselv-border); border-radius: 8px;">
                    Loading 8 interactive resource telemetry charts...
                </div>
            </div>
        </div>

        <!-- 3. Usage Historical Rollup Table (cPanel Parity) -->
        <div class="uniselv-card mb-4" id="uniselv-usage-rollup-card">
            <h5 style="margin-bottom: 12px; font-weight: 700; font-size: 1.05rem; color: #1e293b;">Usage</h5>
            <div class="uniselv-table-wrap">
                <table class="uniselv-table uniselv-cpanel-usage-table" style="margin-bottom: 0;">
                    <thead>
                        <tr style="background:#f8fafc; font-size:0.8rem; text-transform:uppercase; color:#475569;">
                            <th rowspan="2" style="vertical-align:middle;">From</th>
                            <th rowspan="2" style="vertical-align:middle;">To</th>
                            <th colspan="3" style="text-align:center; border-left:1px solid #e2e8f0;">SPEED</th>
                            <th colspan="3" style="text-align:center; border-left:1px solid #e2e8f0;">PMEM</th>
                            <th colspan="3" style="text-align:center; border-left:1px solid #e2e8f0;">IO</th>
                            <th colspan="3" style="text-align:center; border-left:1px solid #e2e8f0;">EP</th>
                            <th colspan="3" style="text-align:center; border-left:1px solid #e2e8f0;">NPROC</th>
                            <th colspan="3" style="text-align:center; border-left:1px solid #e2e8f0;">IOPS</th>
                        </tr>
                        <tr style="background:#f1f5f9; font-size:0.75rem; color:#64748b; text-align:center;">
                            <th style="border-left:1px solid #e2e8f0;">a</th><th>l</th><th>f</th>
                            <th style="border-left:1px solid #e2e8f0;">a</th><th>l</th><th>f</th>
                            <th style="border-left:1px solid #e2e8f0;">a</th><th>l</th><th>f</th>
                            <th style="border-left:1px solid #e2e8f0;">a</th><th>l</th><th>f</th>
                            <th style="border-left:1px solid #e2e8f0;">a</th><th>l</th><th>f</th>
                            <th style="border-left:1px solid #e2e8f0;">a</th><th>l</th><th>f</th>
                        </tr>
                    </thead>
                    <tbody id="uniselv-usage-rollup-tbody">
                        <tr><td colspan="20" style="text-align:center; color:#64748b; padding:24px;">Loading hourly usage records...</td></tr>
                    </tbody>
                </table>
            </div>
            <div id="uniselv-usage-rollup-pagination" class="uniselv-pagination-wrap"></div>
        </div>

        <!-- 4. Active Account Processes (cPanel Parity) -->
        <div class="uniselv-card mb-4" id="uniselv-active-processes-card">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                <h5 style="margin:0; font-weight:700; font-size:1.05rem; color:#1e293b;">Active Processes</h5>
                <button class="uniselv-cpanel-btn" onclick="UniselvResMan.loadLiveProcesses()" title="Refresh Processes">Refresh Processes</button>
            </div>
            <div class="uniselv-table-wrap">
                <table class="uniselv-table" style="margin-bottom:0;">
                    <thead>
                        <tr style="background:#f8fafc; font-size:0.8rem; text-transform:uppercase; color:#475569;">
                            <th style="width:100px;">PID</th>
                            <th>CMD</th>
                            <th style="width:110px; text-align:right;">CPU</th>
                            <th style="width:110px; text-align:right;">MEM</th>
                            <th style="width:100px; text-align:right;">Actions</th>
                        </tr>
                    </thead>
                    <tbody id="uniselv-live-processes-tbody">';
    if (!empty($procs['processes'])) {
        foreach ($procs['processes'] as $p) {
            $cpu_c = ($p['cpu_percent'] > 50) ? '#dc2626' : (($p['cpu_percent'] > 15) ? '#d97706' : '#1e293b');
            echo '<tr>
                <td><strong>' . $p['pid'] . '</strong></td>
                <td><span class="uniselv-cmd-text" title="' . htmlspecialchars($p['tooltip'] ?? $p['cmdline']) . '">' . htmlspecialchars($p['cmdline']) . '</span></td>
                <td style="text-align:right; font-weight:700; color:' . $cpu_c . ';">' . $p['cpu_formatted'] . '</td>
                <td style="text-align:right; font-weight:600; color:#059669;" title="' . htmlspecialchars($p['rss_formatted']) . '">' . $p['mem_formatted'] . '</td>
                <td style="text-align:right;">
                    <button class="uniselv-btn btn-danger btn-sm uniselv-stop-proc-btn" onclick="UniselvResMan.stopProcess(' . $p['pid'] . ', ' . $p['start_time'] . ')">Stop</button>
                </td>
            </tr>';
        }
    } else {
        echo '<tr><td colspan="5" style="text-align:center; color:#64748b; padding:24px;">No active background processes currently running for this account.</td></tr>';
    }
    echo '          </tbody>
                </table>
            </div>
        </div>
    </div>';

    // TAB 3: HISTORY
    echo '<div id="tab-history" class="uniselv-tab-content">
        <div style="margin-bottom: 16px; display: flex; flex-wrap: wrap; gap: 8px;">
            <button class="uniselv-btn btn-outline uniselv-range-btn active" data-range="1h">Last Hour</button>
            <button class="uniselv-btn btn-outline uniselv-range-btn" data-range="today">Today</button>
            <button class="uniselv-btn btn-outline uniselv-range-btn" data-range="yesterday">Yesterday</button>
            <button class="uniselv-btn btn-outline uniselv-range-btn" data-range="7d">Last 7 Days</button>
            <button class="uniselv-btn btn-outline uniselv-range-btn" data-range="30d">Last 30 Days</button>
        </div>
        <div id="uniselv-history-charts">
            <div class="uniselv-card" style="text-align: center; color: #64748b; padding: 40px;">Select a time range above to view historical resource telemetry charts.</div>
        </div>
    </div>';

    // TAB 4: SNAPSHOTS (cPanel Parity)
    echo '<div id="tab-snapshots" class="uniselv-tab-content">
        <div class="uniselv-card mb-4">
            <div class="uniselv-cpanel-header" style="margin-bottom: 16px;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <h5 style="margin: 0; font-weight: 700; font-size: 1.15rem; color: #1e293b;">Snapshots</h5>
                    <div class="uniselv-cpanel-arrows">
                        <button class="uniselv-cpanel-btn" id="enduser-snap-prev-btn" onclick="UniselvResMan.enduserPrevSnapshot()" title="Previous Snapshot">&laquo;</button>
                        <button class="uniselv-cpanel-btn" id="enduser-snap-next-btn" onclick="UniselvResMan.enduserNextSnapshot()" title="Next Snapshot">&raquo;</button>
                    </div>
                </div>
                <div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap;">
                    <div style="display: flex; align-items: center; gap: 6px;">
                        <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="color: #64748b;"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
                        <select id="enduser-snap-date-select" class="uniselv-cpanel-select" onchange="UniselvResMan.onEnduserSnapshotDateChange(this.value)">
                            <option value="">Loading dates...</option>
                        </select>
                    </div>
                    <div style="display: flex; align-items: center; gap: 6px;">
                        <span style="font-size: 0.85rem; color: #64748b;">Choose snapshot:</span>
                        <select id="enduser-snap-time-select" class="uniselv-cpanel-select" onchange="UniselvResMan.onEnduserSnapshotTimeChange(this.value)">
                            <option value="">Loading snapshots...</option>
                        </select>
                    </div>
                    <span id="enduser-snap-trigger-badge" class="uniselv-badge badge-normal" style="font-size: 0.75rem;">READY</span>
                </div>
            </div>

            <!-- Subtabs bar: Process list / Database Queries / HTTP Queries -->
            <div class="uniselv-cpanel-subtabs">
                <button class="uniselv-cpanel-subtab active" data-subtab="procs" onclick="UniselvResMan.setEnduserSnapshotSubtab(\'procs\')">Process list</button>
                <button class="uniselv-cpanel-subtab" data-subtab="db" onclick="UniselvResMan.setEnduserSnapshotSubtab(\'db\')">Database Queries</button>
                <button class="uniselv-cpanel-subtab" data-subtab="http" onclick="UniselvResMan.setEnduserSnapshotSubtab(\'http\')">HTTP Queries</button>
            </div>

            <div id="enduser-snap-content" style="padding-top: 14px;">
                <div style="text-align: center; color: #64748b; padding: 30px;">Loading snapshot records...</div>
            </div>
        </div>
    </div>';

    // TAB 5: NOTIFICATIONS
    echo '<div id="tab-notifications" class="uniselv-tab-content">
        <div class="uniselv-card mb-3">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; flex-wrap:wrap; gap:12px;">
                <div>
                    <h5 style="margin:0 0 4px 0; font-weight:700;">Resource Events & Incident Log</h5>
                    <p style="margin:0; font-size:0.86rem; color:#64748b;">Automated logs of resource thresholds, throttle incidents, and memory warnings.</p>
                </div>
                <div style="display:flex; gap:10px; align-items:center; flex-wrap:wrap;">
                    <select id="uniselv-notif-status-filter" class="uniselv-cpanel-select" onchange="UniselvResMan.filterNotifications(this.value)">
                        <option value="all" selected>All Events</option>
                        <option value="unread">Unread Only</option>
                        <option value="read">Read Only</option>
                        <option value="dismissed">Dismissed</option>
                    </select>
                    <button class="uniselv-btn btn-outline btn-sm" onclick="UniselvResMan.markAllNotifications(\'read\')">
                        <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg> Mark All Read
                    </button>
                    <button class="uniselv-btn btn-outline btn-sm" style="color:#ef4444; border-color:#fca5a5;" onclick="UniselvResMan.clearAllNotifications()">
                        <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg> Clear All
                    </button>
                    <button class="uniselv-btn btn-outline btn-sm" onclick="UniselvResMan.loadEnduserNotifications()" title="Refresh Notifications">
                        <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg> Refresh
                    </button>
                </div>
            </div>
            <div class="uniselv-table-wrap">
                <table class="uniselv-table">
                    <thead>
                        <tr>
                            <th>Time</th>
                            <th>Type</th>
                            <th>Severity</th>
                            <th>Status</th>
                            <th>Message</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody id="uniselv-notifs-tbody">';
    if (!empty($notifs['events'])) {
        foreach ($notifs['events'] as $e) {
            $badge = ($e['severity'] === 'critical') ? 'badge-critical' : (($e['severity'] === 'warning') ? 'badge-warning' : 'badge-normal');
            $st = isset($e['status']) ? $e['status'] : 'unread';
            $status_badge = ($st === 'unread') ? '<span class="uniselv-badge badge-warning">UNREAD</span>' : (($st === 'dismissed') ? '<span class="uniselv-badge badge-outline">DISMISSED</span>' : '<span class="uniselv-badge badge-normal">READ</span>');
            
            $actions_html = '';
            if ($st === 'unread') {
                $actions_html = '<button class="uniselv-btn btn-outline btn-sm" onclick="UniselvResMan.markNotification(' . $e['id'] . ', \'read\')">Mark Read</button> ' .
                                '<button class="uniselv-btn btn-outline btn-sm" style="color:#ef4444;" onclick="UniselvResMan.markNotification(' . $e['id'] . ', \'dismissed\')">Dismiss</button>';
            } elseif ($st === 'read') {
                $actions_html = '<button class="uniselv-btn btn-outline btn-sm" onclick="UniselvResMan.markNotification(' . $e['id'] . ', \'unread\')">Mark Unread</button> ' .
                                '<button class="uniselv-btn btn-outline btn-sm" style="color:#ef4444;" onclick="UniselvResMan.markNotification(' . $e['id'] . ', \'dismissed\')">Dismiss</button>';
            } else {
                $actions_html = '<span style="color:#94a3b8; font-size:0.8rem;">Dismissed</span>';
            }

            echo '<tr class="uniselv-notif-row" data-status="' . htmlspecialchars($st) . '">
                <td>' . date('Y-m-d H:i:s', $e['timestamp']) . '</td>
                <td>' . htmlspecialchars($e['event_type']) . '</td>
                <td><span class="uniselv-badge ' . $badge . '">' . htmlspecialchars(strtoupper($e['severity'])) . '</span></td>
                <td>' . $status_badge . '</td>
                <td>' . htmlspecialchars($e['message']) . '</td>
                <td>' . $actions_html . '</td>
            </tr>';
        }
    } else {
        echo '<tr><td colspan="6" style="text-align:center; color:#64748b; padding:24px;">No resource limit events recorded. System running smoothly.</td></tr>';
    }
    echo '          </tbody>
                </table>
            </div>
            <div id="uniselv-notif-pagination" class="uniselv-pagination-wrap"></div>
        </div>
    </div>';

    // TAB 6: HELP & ABOUT (ENDUSER)
    if (file_exists(__DIR__ . '/views/enduser_help.php')) {
        include __DIR__ . '/views/enduser_help.php';
    }

    echo uniselv_render_developer_footer();
    echo '</div>'; // End container
    echo '<script>UniselvResMan.init(window.location.href, false, "' . htmlspecialchars($current_user) . '", "' . uniselv_csrf_token($current_user) . '");</script>';
}

