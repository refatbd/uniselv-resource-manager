import os
import sys
import json
import time
import socket
import sqlite3
import signal
import pathlib
import subprocess
import glob
import re
import shutil
import hashlib
import secrets
import uuid
import stat
try:
    import fcntl
except ImportError:
    fcntl = None
from typing import Dict, Any, List, Optional, Tuple, Set

from collector import parse_int_file, parse_key_value_file, redact_command_line
from golden_shield_manager import GoldenShieldManager

def format_bytes(b: Any) -> str:
    if not b:
        return "0 B"
    if isinstance(b, str):
        if not b.isdigit():
            dec, _ = parse_bw_to_bytes(b)
            if dec > 0:
                b = dec
            else:
                return str(b)
        else:
            b = int(b)
    elif not isinstance(b, (int, float)):
        try:
            b = int(b)
        except Exception:
            return str(b)

    if b < 1024:
        return f"{b} B"
    elif b < 1024 * 1024:
        return f"{round(b / 1024, 1)} KiB"
    elif b < 1024 * 1024 * 1024:
        return f"{round(b / 1024 / 1024, 1)} MiB"
    else:
        return f"{round(b / 1024 / 1024 / 1024, 2)} GiB"

def parse_bw_to_bytes(val: Any) -> Tuple[int, int]:
    """Returns tuple of (decimal_bytes, binary_bytes) for bandwidth limit strings."""
    if not val:
        return (0, 0)
    s = str(val).strip().upper()
    if s.endswith('K'):
        num = float(s[:-1])
        return (int(num * 1000), int(num * 1024))
    elif s.endswith('M'):
        num = float(s[:-1])
        return (int(num * 1000 * 1000), int(num * 1024 * 1024))
    elif s.endswith('G'):
        num = float(s[:-1])
        return (int(num * 1000 * 1000 * 1000), int(num * 1024 * 1024 * 1024))
    elif s.endswith('T'):
        num = float(s[:-1])
        return (int(num * 1000 * 1000 * 1000 * 1000), int(num * 1024 * 1024 * 1024 * 1024))
    elif s.isdigit():
        n = int(s)
        return (n, n)
    return (0, 0)

def parse_iops(val: Any) -> int:
    """Parses integer IOPS value from string/int."""
    if not val:
        return 0
    s = str(val).strip()
    if s.isdigit():
        return int(s)
    return 0

def parse_cgroup_io_max(content: str) -> Dict[str, Dict[str, int]]:
    """
    Parses cgroup v2 io.max file into a dictionary of device rules:
    {
        '8:0': {'rbps': 147000000, 'wbps': 88000000, 'riops': 1764, 'wiops': 1176}, ...
    }
    """
    devices = {}
    if not content:
        return devices
    for line in content.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if not parts:
            continue
        dev = parts[0]
        dev_limits = {}
        for item in parts[1:]:
            if '=' in item:
                k, v = item.split('=', 1)
                k = k.lower().strip()
                v = v.strip()
                if v == 'max':
                    dev_limits[k] = -1
                elif v.isdigit():
                    dev_limits[k] = int(v)
        if dev_limits:
            devices[dev] = dev_limits
    return devices

class DeviceInventory(set):
    """
    Backing storage device inventory representing both required primary backing disks
    and all supported/recognized partitions and device-mapper slaves.
    Inherits from set for seamless membership tests: 'dev in inventory' checks supported devices.
    """
    def __init__(self, required: Set[str], supported: Set[str]):
        super().__init__(supported)
        self.required: Set[str] = set(required)
        self.supported: Set[str] = set(supported)


def discover_backing_devices(username: Optional[str] = None, paths: Optional[List[str]] = None) -> DeviceInventory:
    """
    Discovers block devices (major:minor) serving tenant storage.
    Inspects tenant home, Webuzo user directory, root mount, and resolves
    partition-to-parent-disk as well as device-mapper relationships.
    Returns DeviceInventory containing both required canonical disks and all supported devices.
    """
    required_devs: Set[str] = set()
    supported_devs: Set[str] = set()

    primary_targets = []
    if username:
        primary_targets.extend([f"/home/{username}", f"/var/webuzo/users/{username}"])
    primary_targets.extend(["/home", "/var/webuzo", "/"])
    if paths:
        primary_targets.extend(paths)

    # Method 1: Check st_dev for each path and resolve sysfs relationships
    for p in primary_targets:
        target_check = p
        while target_check and not os.path.exists(target_check) and target_check != os.path.dirname(target_check):
            target_check = os.path.dirname(target_check)

        if os.path.exists(target_check):
            try:
                st = os.stat(target_check)
                maj = os.major(st.st_dev)
                min_num = os.minor(st.st_dev)
                dev_str = f"{maj}:{min_num}"
                supported_devs.add(dev_str)
                parent_disk_str = dev_str

                # Check sysfs block device directory
                sys_dev = pathlib.Path(f"/sys/dev/block/{dev_str}")
                if sys_dev.exists():
                    if (sys_dev / "partition").exists():
                        try:
                            parent_disk = pathlib.Path(os.path.realpath(str(sys_dev))).parent
                            dev_file = parent_disk / "dev"
                            if dev_file.exists():
                                p_dev = dev_file.read_text(encoding='utf-8', errors='replace').strip()
                                if p_dev:
                                    supported_devs.add(p_dev)
                                    parent_disk_str = p_dev
                        except Exception:
                            pass

                    # Check device mapper or raid slaves
                    slaves_dir = sys_dev / "slaves"
                    if slaves_dir.is_dir():
                        try:
                            for slave in slaves_dir.iterdir():
                                s_dev_file = slave / "dev"
                                if s_dev_file.exists():
                                    s_dev = s_dev_file.read_text(encoding='utf-8', errors='replace').strip()
                                    if s_dev:
                                        supported_devs.add(s_dev)
                                        s_part = pathlib.Path(f"/sys/dev/block/{s_dev}/partition")
                                        if s_part.exists():
                                            p_dev_s = pathlib.Path(os.path.realpath(f"/sys/dev/block/{s_dev}")).parent / "dev"
                                            if p_dev_s.exists():
                                                ps = p_dev_s.read_text(encoding='utf-8', errors='replace').strip()
                                                supported_devs.add(ps)
                                                parent_disk_str = ps
                        except Exception:
                            pass
                required_devs.add(parent_disk_str)
            except Exception:
                pass

    # Method 2: Check /proc/mounts to find underlying block device nodes
    if os.path.exists('/proc/mounts'):
        try:
            with open('/proc/mounts', 'r') as mf:
                for line in mf:
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        m_dev, m_point = parts[0], parts[1]
                        if m_point in primary_targets or any(p.startswith(m_point) for p in primary_targets):
                            if m_dev.startswith('/dev/') and os.path.exists(m_dev):
                                try:
                                    b_st = os.stat(m_dev)
                                    if stat.S_ISBLK(b_st.st_mode):
                                        b_maj = os.major(b_st.st_rdev)
                                        b_min = os.minor(b_st.st_rdev)
                                        b_str = f"{b_maj}:{b_min}"
                                        supported_devs.add(b_str)
                                        p_disk = b_str
                                        sys_b = pathlib.Path(f"/sys/dev/block/{b_str}")
                                        if sys_b.exists() and (sys_b / "partition").exists():
                                            p_file = pathlib.Path(os.path.realpath(str(sys_b))).parent / "dev"
                                            if p_file.exists():
                                                p_disk = p_file.read_text(encoding='utf-8', errors='replace').strip()
                                                supported_devs.add(p_disk)
                                        required_devs.add(p_disk)
                                except Exception:
                                    pass
        except Exception:
            pass

    # Fallback: Optional admin-configured persistent inventory (/etc/uniselv/disk_inventory.txt)
    # Validated strictly against actual sysfs block devices
    if not supported_devs:
        admin_inv = pathlib.Path('/etc/uniselv/disk_inventory.txt')
        if admin_inv.exists():
            try:
                for line in admin_inv.read_text(encoding='utf-8', errors='replace').splitlines():
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    tokens = line.replace('├─', ' ').replace('└─', ' ').split()
                    is_disk = 'disk' in line or '[required]' in line
                    for token in tokens:
                        if ':' in token:
                            a, b = token.split(':', 1)
                            if a.isdigit() and b.isdigit():
                                d_id = f"{a}:{b}"
                                if pathlib.Path(f"/sys/dev/block/{d_id}").exists():
                                    supported_devs.add(d_id)
                                    if is_disk:
                                        required_devs.add(d_id)
            except Exception:
                pass

    return DeviceInventory(required_devs, supported_devs)


def verify_io_rules(
    io_str: str,
    plan_limits: dict,
    expected_devices: Optional[Set[str]] = None,
    username: Optional[str] = None,
    required_devices: Optional[Set[str]] = None
) -> Tuple[bool, str]:
    """
    Verifies that cgroup v2 io.max content enforces the limits specified in plan_limits
    and establishes coverage over actual tenant-data backing block devices.
    Returns (True, "") on success, or (False, error_message) on failure.
    """
    req_rbps_dec, req_rbps_bin = parse_bw_to_bytes(plan_limits.get('read_bw'))
    req_wbps_dec, req_wbps_bin = parse_bw_to_bytes(plan_limits.get('write_bw'))
    req_riops = parse_iops(plan_limits.get('diskread'))
    req_wiops = parse_iops(plan_limits.get('diskwrite'))

    has_req = (req_rbps_dec > 0 or req_wbps_dec > 0 or req_riops > 0 or req_wiops > 0)
    if not has_req:
        return True, ""

    if not io_str or not io_str.strip():
        return False, "Plan specifies I/O limits but io.max is empty"

    devices = parse_cgroup_io_max(io_str)
    if not devices:
        return False, f"io.max contains no valid device rules: '{io_str}'"

    # 1. Backing Storage Device Coverage Verification
    if expected_devices is not None:
        supp_devs = set(expected_devices)
        req_devs = set(required_devices) if required_devices is not None else set(expected_devices)
    else:
        inv = discover_backing_devices(username)
        supp_devs = set(inv.supported)
        req_devs = set(required_devices) if required_devices is not None else set(inv.required)

    # CRITICAL (P1): If plan specifies I/O limits, we MUST establish non-empty supported and required device inventory.
    # An empty or unknown inventory must FAIL CLOSED.
    if not supp_devs or not req_devs:
        return False, "Storage inventory error: unable to establish backing storage devices for tenant data; refusing to verify unverified device rules (fail-closed)"

    # Every device in io.max must be a supported/known backing storage device
    for dev in devices.keys():
        if dev not in supp_devs:
            return False, f"Device '{dev}' does not match any backing storage device for tenant data (expected one of: {', '.join(sorted(supp_devs))})"

    # Check that all required backing devices are covered in io.max
    for req in req_devs:
        if req not in devices:
            return False, f"io.max is missing coverage for required tenant backing device '{req}' (required: {', '.join(sorted(req_devs))})"

    # 2. Limit Rule Verification for Covered Devices
    for dev, limits in devices.items():
        if ':' not in dev:
            return False, f"Device identifier '{dev}' has invalid format (expected major:minor)"
        maj, min_num = dev.split(':', 1)
        if not maj.isdigit() or not min_num.isdigit():
            return False, f"Device identifier '{dev}' has invalid non-numeric major:minor"

        if req_rbps_dec > 0:
            if 'rbps' not in limits:
                return False, f"Device {dev} missing required 'rbps' limit"
            val = limits['rbps']
            if val <= 0 or val not in (req_rbps_dec, req_rbps_bin):
                return False, f"Device {dev} rbps={val} does not match expected {req_rbps_dec} (or {req_rbps_bin})"

        if req_wbps_dec > 0:
            if 'wbps' not in limits:
                return False, f"Device {dev} missing required 'wbps' limit"
            val = limits['wbps']
            if val <= 0 or val not in (req_wbps_dec, req_wbps_bin):
                return False, f"Device {dev} wbps={val} does not match expected {req_wbps_dec} (or {req_wbps_bin})"

        if req_riops > 0:
            if 'riops' not in limits:
                return False, f"Device {dev} missing required 'riops' limit"
            val = limits['riops']
            if val <= 0 or val != req_riops:
                return False, f"Device {dev} riops={val} does not match expected {req_riops}"

        if req_wiops > 0:
            if 'wiops' not in limits:
                return False, f"Device {dev} missing required 'wiops' limit"
            val = limits['wiops']
            if val <= 0 or val != req_wiops:
                return False, f"Device {dev} wiops={val} does not match expected {req_wiops}"

    return True, ""

class IpcRequestHandler:
    def __init__(self, db_path: str, collector):
        self.db_path = db_path
        self.collector = collector
        self.golden_shield = GoldenShieldManager(db_conn_factory=self.get_db)
        self.maintenance_mode = self._load_maintenance_mode()

    def _load_maintenance_mode(self) -> bool:
        """Load persisted maintenance state from SQLite settings."""
        try:
            conn = self.get_db()
            cur = conn.cursor()
            cur.execute("SELECT value FROM settings WHERE key = 'maintenance_mode'")
            row = cur.fetchone()
            conn.close()
            if row and row['value'] == '1':
                return True
        except Exception:
            pass
        return False

    def get_db(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=30)
        conn.row_factory = sqlite3.Row
        return conn

    def get_installed_phps(self) -> List[str]:
        phps = []
        for p in sorted(glob.glob('/usr/local/apps/php*')):
            base = os.path.basename(p)
            if os.path.exists(os.path.join(p, 'bin', 'php')):
                phps.append(base)
        return phps if phps else ['php81', 'php82']

    def is_reseller_actor(self, auth: Dict[str, Any], params: Dict[str, Any]) -> tuple:
        """
        B01: Determine if the caller is operating under Reseller scope.
        Returns (is_reseller: bool, actor_username: str).
        """
        actor = auth.get('user', '')
        if not actor or actor == 'root':
            # Root can optionally simulate/filter by reseller if reseller_user/owner param provided
            owner_filter = params.get('owner') or params.get('reseller_user')
            if owner_filter and owner_filter != 'root':
                return True, owner_filter
            return False, 'root'

        # Non-root caller
        if auth.get('is_reseller') or auth.get('role') == 'reseller' or params.get('actor_role') == 'reseller':
            return True, actor

        users = self.collector.get_webuzo_users()
        if users.get(actor, {}).get('reseller'):
            return True, actor

        return False, actor

    def is_permission_granted(self, username: str, role: str, permission: str) -> bool:
        """
        B04: Evaluate effective permission for account and role.
        Resolution order:
        1. Specific per-account grant/revocation in account_permissions table.
        2. Role-level baseline in role_permissions table.
        3. Default fallback (True).
        """
        conn = self.get_db()
        try:
            cur = conn.cursor()
            # 1. Per-account override
            cur.execute("SELECT granted FROM account_permissions WHERE username = ? AND permission = ?", (username, permission))
            row = cur.fetchone()
            if row is not None:
                return bool(row['granted'])

            # 2. Role-level baseline
            cur.execute("SELECT granted FROM role_permissions WHERE role = ? AND permission = ?", (role, permission))
            r_row = cur.fetchone()
            if r_row is not None:
                return bool(r_row['granted'])

            return True
        except Exception:
            return True
        finally:
            conn.close()

    def handle_request(self, req: Dict[str, Any]) -> Dict[str, Any]:
        action = req.get('action')
        auth = req.get('auth', {})
        if not isinstance(auth, dict):
            auth = {}

        params = req.get('params', {})
        if not isinstance(params, dict):
            params = {}

        user = auth.get('user', '')
        is_admin = bool(auth.get('is_admin', False))
        is_reseller, reseller_actor = self.is_reseller_actor(auth, params)

        try:
            # Resolve target user: Admin can inspect any user; Enduser is strictly scoped to authenticated session
            target_user = params.get('username') if (is_admin and params.get('username')) else user

            # A reseller's administrator-panel access is not server-root authority.
            restricted_reseller = is_admin and user != 'root'
            if restricted_reseller:
                inventory = self.collector.get_webuzo_users()
                if not inventory.get(user, {}).get('reseller'):
                    return {'error': 'Forbidden: Non-root administrator identity is not a reseller', 'status_code': 403}
                is_reseller, reseller_actor = True, user
                owned = {name for name, data in inventory.items() if data.get('owner') == user or name == user}
                if target_user not in owned:
                    return {'error': 'Forbidden: Account is outside reseller ownership', 'status_code': 403}
                reseller_common = {'get_enduser_dashboard', 'get_enduser_history', 'get_enduser_processes',
                    'stop_enduser_process', 'get_enduser_snapshots', 'get_snapshots_index', 'get_snapshot_detail',
                    'get_enduser_notifications', 'mark_notification', 'get_enduser_support_export', 'get_branding_settings'}
                reseller_admin = {'get_admin_accounts', 'get_admin_account_detail', 'set_temporary_override', 'cancel_temporary_override', 'get_audit_log', 'get_admin_audit_limits', 'audit_limits'}
                if action not in reseller_common | reseller_admin:
                    return {'error': 'Forbidden: Server-wide action requires root', 'status_code': 403}
                if action in {'set_temporary_override', 'cancel_temporary_override'} and not self.is_permission_granted(user, 'reseller', 'can_set_overrides'):
                    return {'error': 'Forbidden: Reseller overrides permission denied', 'status_code': 403}
                if action == 'get_audit_log':
                    if not self.is_permission_granted(user, 'reseller', 'can_view_audit_log'):
                        return {'error': 'Forbidden: Reseller audit permission denied', 'status_code': 403}
                    return self.action_get_audit_log(params, allowed_targets=owned, actor_scope=user)
                if action in {'get_admin_audit_limits', 'audit_limits'}:
                    result = self.action_admin_audit_limits()
                    result['audit'] = [row for row in result.get('audit', []) if row.get('username') in owned]
                    return result
                if action == 'get_enduser_support_export' and not self.is_permission_granted(user, 'reseller', 'can_export_diagnostics'):
                    return {'error': 'Forbidden: Reseller export permission denied', 'status_code': 403}
                # Keep tenant self-service policies in force for reseller process operations.
                if action == 'stop_enduser_process':
                    return self.action_stop_enduser_process(target_user, params, is_admin=False)

            # Common / Enduser endpoints
            if action == 'get_enduser_dashboard':
                return self.action_enduser_dashboard(target_user)
            elif action == 'get_enduser_history':
                return self.action_enduser_history(target_user, params)
            elif action == 'get_enduser_processes':
                return self.action_enduser_processes(target_user)
            elif action == 'stop_enduser_process':
                return self.action_stop_enduser_process(target_user, params, is_admin=is_admin)
            elif action == 'get_enduser_snapshots':
                return self.action_enduser_snapshots(target_user, params)
            elif action == 'get_snapshots_index':
                return self.action_get_snapshots_index(target_user, params)
            elif action == 'get_snapshot_detail':
                return self.action_get_snapshot_detail(target_user, params)
            elif action == 'get_enduser_notifications':
                return self.action_enduser_notifications(target_user)
            elif action == 'mark_notification':
                return self.action_mark_notification(user, params)
            elif action == 'get_enduser_support_export':
                return self.action_enduser_support_export(target_user, params)
            elif action == 'get_branding_settings':
                return self.action_get_branding_settings()
            elif action == 'process_webhook':
                return self.action_process_webhook(params)

            # Admin endpoints (strictly require is_admin)
            if not is_admin:
                return {'error': 'Forbidden: Admin privilege required'}

            if action == 'get_admin_overview':
                return self.action_admin_overview()
            elif action == 'get_admin_accounts':
                return self.action_admin_accounts(params, actor=reseller_actor, is_reseller=is_reseller)
            elif action == 'get_admin_account_detail':
                target_user = params.get('username', '')
                return self.action_admin_account_detail(target_user, params, actor=reseller_actor, is_reseller=is_reseller)
            elif action in ('get_admin_audit_limits', 'audit_limits'):
                return self.action_admin_audit_limits()
            elif action == 'get_admin_out_of_boundary':
                return self.action_admin_out_of_boundary()
            elif action == 'set_temporary_override':
                return self.action_set_temporary_override(user, params, is_reseller=is_reseller)
            elif action == 'cancel_temporary_override':
                return self.action_cancel_temporary_override(user, params, is_reseller=is_reseller)
            elif action == 'get_permissions':
                return self.action_get_permissions(params)
            elif action == 'save_account_permission':
                return self.action_save_account_permission(user, params)
            elif action == 'save_role_permission':
                return self.action_save_role_permission(user, params)
            elif action == 'sync_native_plans':
                return self.action_sync_native_plans(user)
            elif action == 'save_native_plan':
                return self.action_save_native_plan(user, params)
            elif action == 'delete_native_plan':
                return self.action_delete_native_plan(user, params)
            elif action == 'get_capacity_planning':
                return self.action_get_capacity_planning()
            elif action == 'get_scheduled_reports':
                return self.action_get_scheduled_reports()
            elif action == 'dispatch_scheduled_report':
                return self.action_dispatch_scheduled_report(user, params)
            elif action == 'get_report_schedule':
                return self.action_get_report_schedule()
            elif action == 'save_report_schedule':
                return self.action_save_report_schedule(user, params)
            elif action == 'get_package_mappings':
                return self.action_get_package_mappings()
            elif action == 'save_package_mapping':
                return self.action_save_package_mapping(user, params)
            elif action == 'delete_package_mapping':
                return self.action_delete_package_mapping(user, params)
            elif action == 'save_branding_settings':
                return self.action_save_branding_settings(user, params)
            elif action == 'get_audit_log':
                return self.action_get_audit_log(params)
            elif action == 'set_maintenance_mode':
                return self.action_set_maintenance_mode(user, params)
            elif action == 'get_agent_health':
                return self.action_get_agent_health()
            elif action == 'get_feature_settings':
                return self.action_get_feature_settings()
            elif action == 'save_feature_settings':
                return self.action_save_feature_settings(user, params)
            elif action == 'get_overload_protection_status':
                return self.action_get_overload_protection_status()
            elif action == 'get_storage_settings':
                return self.action_get_storage_settings()
            elif action == 'save_storage_settings':
                return self.action_save_storage_settings(user, params)
            elif action == 'prune_database_now':
                return self.action_prune_database_now(user, params)
            elif action == 'clear_audit_logs':
                return self.action_clear_audit_logs(user, params)
            elif action == 'purge_snapshots':
                return self.action_purge_snapshots(user, params)
            elif action == 'run_adapter_sync':
                return self.action_run_adapter_sync(user, params)
            elif action == 'get_golden_shield_status':
                return self.golden_shield.get_status()
            elif action == 'enable_golden_shield':
                return self.golden_shield.reconfigure_or_enable('auto')
            elif action == 'reconfigure_golden_shield':
                mode = str(params.get('mode', 'auto')).lower()
                overrides = {}
                if 'customer_cpu_pct' in params and params['customer_cpu_pct']:
                    overrides['customerCpuPercent'] = params['customer_cpu_pct']
                if 'hosting_mem_mib' in params and params['hosting_mem_mib']:
                    overrides['hostingMemoryMaxMiB'] = params['hosting_mem_mib']
                if 'overrides' in params and isinstance(params['overrides'], dict):
                    overrides.update(params['overrides'])
                return self.golden_shield.reconfigure_or_enable(mode, overrides if overrides else None)
            elif action == 'verify_golden_shield':
                return self.golden_shield.verify()
            elif action == 'disable_golden_shield':
                return self.golden_shield.disable()
            elif action == 'restore_golden_shield_config':
                backup_id = str(params.get('backup_id') or params.get('backup_file') or '')
                if 'golden-shield-backup-' in backup_id:
                    backup_id = backup_id.split('golden-shield-backup-')[-1].replace('.json', '')
                return self.golden_shield.restore_backup(backup_id)
            elif action == 'list_golden_shield_backups':
                return {'success': True, 'backups': self.golden_shield.list_backups()}
            else:
                return {'error': f'Unknown action: {action}'}
        except Exception as e:
            return {'error': f'Internal handler error: {str(e)}'}

    # ==================== ENDUSER ACTIONS ====================

    def get_php_workers_by_version(self, uid: int) -> Dict[str, Any]:
        """
        U10: Per-PHP-version FPM worker inventory and execution state analysis.
        Verifies executable path and pool ownership rather than arbitrary cmdline substrings.
        Measures authoritative Linux kernel listen socket backlog (Recv-Q / Send-Q) via UNIX domain sockets,
        with graceful fallback and truthful unmonitored semantics when socket is absent.
        """
        workers_by_ver: Dict[str, Dict[str, Any]] = {}
        total_workers = 0
        total_executing = 0
        total_sleeping = 0

        # Step 1: Resolve username for socket discovery
        username = None
        try:
            import pwd
            username = pwd.getpwuid(uid).pw_name
        except Exception:
            pass

        # Step 2: Measure kernel listen socket backlogs for this user
        socket_backlogs: Dict[str, Dict[str, Any]] = {}
        if username:
            try:
                # ss -l -x -H lists listening UNIX domain sockets without headers
                # Output format: Netid State Recv-Q Send-Q Local_Address:Port Peer_Address:Port
                res = subprocess.run(['ss', '-l', '-x', '-H'], capture_output=True, text=True, timeout=2.5)
                if res.returncode == 0:
                    for line in res.stdout.splitlines():
                        parts = line.split()
                        if len(parts) >= 5:
                            sock_path = parts[4]
                            if f"fpm-{username}.sock" in sock_path or f"/{username}.sock" in sock_path:
                                recv_q = int(parts[1]) if parts[1].isdigit() else 0
                                send_q = int(parts[2]) if parts[2].isdigit() else 0

                                ver_match = re.search(r'php(\d{2})', sock_path) or re.search(r'php-?(\d+\.\d+)', sock_path)
                                ver_key = f"PHP {ver_match.group(1)[0]}.{ver_match.group(1)[1]}" if ver_match and len(ver_match.group(1)) == 2 else (f"PHP {ver_match.group(1)}" if ver_match else "PHP Default")

                                socket_backlogs[ver_key] = {
                                    'path': sock_path,
                                    'recv_q': recv_q,
                                    'send_q': send_q
                                }
            except Exception:
                pass

        # Step 3: Scan /proc for running PHP-FPM worker processes belonging to this UID
        try:
            for pid_dir in os.listdir('/proc'):
                if not pid_dir.isdigit():
                    continue
                pid = int(pid_dir)
                try:
                    p_stat = os.stat(f'/proc/{pid}')
                    if p_stat.st_uid != uid:
                        continue

                    # 1. Verify executable is actually a PHP-FPM binary
                    exe_path = ''
                    try:
                        exe_path = os.readlink(f'/proc/{pid}/exe')
                    except Exception:
                        pass

                    cmdline = ''
                    try:
                        with open(f'/proc/{pid}/cmdline', 'rb') as f:
                            cmdline = f.read().replace(b'\x00', b' ').decode('utf-8', 'replace').strip()
                    except Exception:
                        continue

                    # Strict FPM worker qualification: must be php-fpm binary or php-fpm pool worker
                    is_fpm = ('php-fpm' in exe_path) or ('php-fpm: pool' in cmdline) or ('php-fpm' in cmdline and 'pool' in cmdline)
                    if not is_fpm:
                        continue

                    # 2. Extract engine version from verified exe path or cmdline
                    ver_match = re.search(r'php(\d{2})', exe_path) or re.search(r'php-?(\d+\.\d+)', exe_path) or \
                                re.search(r'php(\d{2})', cmdline) or re.search(r'php-?(\d+\.\d+)', cmdline)
                    ver_label = "PHP " + (ver_match.group(1) if ver_match else "Engine")
                    if len(ver_label) == 6 and ver_label[-2:].isdigit():
                        ver_label = f"PHP {ver_label[-2]}.{ver_label[-1]}"

                    # 3. Read Linux scheduler state (R/D = actively executing on CPU or disk; S = waiting/idle)
                    state = 'S'
                    try:
                        with open(f'/proc/{pid}/stat', 'r') as f:
                            sparts = f.read().split()
                            if len(sparts) >= 3:
                                state = sparts[2]
                    except Exception:
                        pass

                    is_executing = (state == 'R' or state == 'D')

                    sock_info = socket_backlogs.get(ver_label) or (next(iter(socket_backlogs.values())) if len(socket_backlogs) == 1 else None)
                    if sock_info:
                        q_len = sock_info['recv_q']
                        b_lim = sock_info['send_q']
                        q_disp = f"{q_len} queued / {b_lim} limit"
                        q_mon = 'kernel_socket_backlog'
                    else:
                        q_len = 'unmonitored'
                        b_lim = 'unmonitored'
                        q_disp = 'N/A (Status Socket Inactive)'
                        q_mon = 'unmonitored_without_status_socket'

                    stats = workers_by_ver.setdefault(ver_label, {
                        'version': ver_label,
                        'active': 0,
                        'busy': 0,
                        'idle': 0,
                        'queue_length': q_len,
                        'backlog_limit': b_lim,
                        'queue_display': q_disp,
                        'queue_monitoring': q_mon,
                        'socket_path': sock_info['path'] if sock_info else None,
                        'state_method': 'scheduler_executing_vs_waiting'
                    })
                    stats['active'] += 1
                    total_workers += 1
                    if is_executing:
                        stats['busy'] += 1
                        total_executing += 1
                    else:
                        stats['idle'] += 1
                        total_sleeping += 1
                except (FileNotFoundError, ProcessLookupError, PermissionError):
                    continue
        except Exception:
            pass

        # If workers were not executing but listening socket exists (e.g. ondemand mode idle)
        for ver_k, s_data in socket_backlogs.items():
            if ver_k not in workers_by_ver:
                workers_by_ver[ver_k] = {
                    'version': ver_k,
                    'active': 0,
                    'busy': 0,
                    'idle': 0,
                    'queue_length': s_data['recv_q'],
                    'backlog_limit': s_data['send_q'],
                    'queue_display': f"{s_data['recv_q']} queued / {s_data['send_q']} limit",
                    'queue_monitoring': 'kernel_socket_backlog',
                    'socket_path': s_data['path'],
                    'state_method': 'ondemand_socket_idle'
                }

        has_socket_monitoring = bool(socket_backlogs)
        queue_mon_status = 'kernel_socket_backlog' if has_socket_monitoring else 'unmonitored_without_status_socket'
        conf_status = 'kernel_socket_inventory' if has_socket_monitoring else 'process_table_inventory'

        tot_recv_q = sum(s['recv_q'] for s in socket_backlogs.values()) if socket_backlogs else 0
        tot_send_q = sum(s['send_q'] for s in socket_backlogs.values()) if socket_backlogs else 0

        return {
            'total_workers': total_workers,
            'total_busy': total_executing,
            'total_idle': total_sleeping,
            'total_queued': tot_recv_q,
            'total_backlog_limit': tot_send_q,
            'measurement_confidence': conf_status,
            'queue_monitoring': queue_mon_status,
            'queue_note': 'Authoritative listen queue measured from Linux kernel UNIX domain socket backlog buffer (ss -l -x). Worker execution state reflects scheduler state (R/D executing, S idle/waiting).' if has_socket_monitoring else 'Worker state reflects scheduler state (R/D executing, S waiting on I/O/network or idle). FPM listen backlog requires private pm.status_path socket.',
            'by_version': list(workers_by_ver.values())
        }

    def get_account_upgrade_recommendations(self, username: str) -> Dict[str, Any]:
        """U16: Sustained-history upgrade recommendations based on measured historical pressure."""
        users = self.collector.get_webuzo_users()
        current_plan = users.get(username, {}).get('plan_name')
        if not current_plan:
            conn_u = self.get_db()
            try:
                c_u = conn_u.cursor()
                c_u.execute("SELECT plan_name FROM samples WHERE username = ? ORDER BY timestamp DESC LIMIT 1", (username,))
                r_u = c_u.fetchone()
                if r_u and r_u['plan_name']:
                    current_plan = r_u['plan_name']
                else:
                    current_plan = 'default'
            finally:
                conn_u.close()

        limits = self.collector.get_plan_limits(current_plan)

        conn = self.get_db()
        try:
            cur = conn.cursor()
            week_ago = int(time.time()) - (7 * 86400)
            cur.execute("""
                SELECT COUNT(*) as sample_count,
                       MIN(timestamp) as min_ts,
                       MAX(timestamp) as max_ts,
                       SUM(cpu_throttled_events) as total_throttled,
                       SUM(oom_kill_events) as total_oom,
                       SUM(task_limit_events) as total_task_limit,
                       AVG(cpu_allowance_percent) as avg_cpu_allowance,
                       MAX(cpu_allowance_percent) as peak_cpu_allowance,
                       AVG(mem_current_bytes) as avg_mem,
                       MAX(mem_current_bytes) as peak_mem
                FROM samples
                WHERE username = ? AND timestamp >= ?
            """, (username, week_ago))
            row = cur.fetchone()
        finally:
            conn.close()

        sample_cnt = row['sample_count'] if row else 0
        min_ts = row['min_ts'] if row and row['min_ts'] else 0
        max_ts = row['max_ts'] if row and row['max_ts'] else 0
        span_seconds = (max_ts - min_ts) if (max_ts and min_ts and max_ts > min_ts) else 0
        span_hours = round(span_seconds / 3600.0, 1)

        tot_throttle = row['total_throttled'] if row and row['total_throttled'] else 0
        tot_oom = row['total_oom'] if row and row['total_oom'] else 0
        tot_tasks = row['total_task_limit'] if row and row['total_task_limit'] else 0
        avg_cpu = round(row['avg_cpu_allowance'] or 0.0, 1) if row else 0.0
        peak_cpu = round(row['peak_cpu_allowance'] or 0.0, 1) if row else 0.0
        peak_mem = row['peak_mem'] or 0 if row else 0
        mem_limit = limits.get('mem_max', 1024*1024*1024)
        peak_mem_pct = round((peak_mem / max(1, mem_limit)) * 100, 1)

        # Truthful minimum observation check: requires >= 1 hour (3600s) and >= 12 samples
        if sample_cnt < 12 or span_seconds < 3600:
            return {
                'status': 'INSUFFICIENT_DATA',
                'current_plan': current_plan,
                'recommended_plan': current_plan,
                'summary': f"Insufficient historical telemetry to evaluate upgrade recommendations (observed {sample_cnt} sample(s) over {span_hours} hours; minimum 12 samples spanning at least 1 hour required).",
                'evidence': {
                    'samples_evaluated': sample_cnt,
                    'observed_span_seconds': span_seconds,
                    'observed_span_hours': span_hours,
                    'minimum_span_required_seconds': 3600,
                    'minimum_samples_required': 12,
                    'throttled_events': tot_throttle,
                    'oom_kills': tot_oom,
                    'task_limit_events': tot_tasks,
                    'avg_cpu_allowance_pct': avg_cpu,
                    'peak_cpu_allowance_pct': peak_cpu,
                    'peak_mem_pct': peak_mem_pct,
                    '7d_throttled_events': tot_throttle,
                    '7d_oom_kills': tot_oom,
                    '7d_task_limit_events': tot_tasks,
                    '7d_avg_cpu_allowance_pct': avg_cpu,
                    '7d_peak_cpu_allowance_pct': peak_cpu,
                    '7d_peak_mem_pct': peak_mem_pct
                },
                'reasons': [
                    f"Baseline telemetry is still accumulating ({sample_cnt}/12 samples across {span_hours} hours). Continuous monitoring is in progress."
                ]
            }

        # Commercial customer ladder - strictly excludes admin-only 'master' tier
        commercial_ladder = ['go', 'starter', 'default', 'pro', 'turbo', 'enterprise']
        curr_idx = commercial_ladder.index(current_plan) if current_plan in commercial_ladder else -1

        status = "ADEQUATE"
        reasons = []
        if tot_oom > 0:
            status = "UPGRADE_RECOMMENDED"
            reasons.append(f"Recorded {tot_oom} kernel Out-Of-Memory (OOM) termination event(s) across {span_hours} hours of telemetry.")
        if tot_throttle > 10:
            status = "UPGRADE_RECOMMENDED"
            reasons.append(f"Recorded {tot_throttle} CPU throttling events due to exhausted core quota.")
        if peak_mem_pct > 92.0:
            status = "UPGRADE_RECOMMENDED"
            reasons.append(f"Peak memory pressure reached {peak_mem_pct}% of plan ceiling.")
        if avg_cpu > 70.0:
            status = "UPGRADE_RECOMMENDED"
            reasons.append(f"Sustained average CPU allowance is elevated at {avg_cpu}% across {span_hours} hours.")

        if not reasons:
            if peak_cpu < 40.0 and peak_mem_pct < 50.0:
                summary = f"Account utilization is optimal on the '{current_plan.upper()}' plan. Resource headroom is abundant."
            else:
                summary = f"Account operates comfortably within '{current_plan.upper()}' limits with healthy headroom."
            recommended_plan = current_plan
        else:
            if current_plan == 'enterprise' or (curr_idx >= 0 and curr_idx >= len(commercial_ladder) - 1):
                status = "MAX_TIER_REACHED"
                recommended_plan = current_plan
                summary = f"Account '{username}' is already on the top commercial tier ('{current_plan.upper()}'). Contact enterprise support for dedicated virtual instance or clustering options."
            elif curr_idx >= 0 and curr_idx < len(commercial_ladder) - 1:
                recommended_plan = commercial_ladder[curr_idx + 1]
                summary = f"Upgrade to '{recommended_plan.upper()}' recommended to alleviate observed bottlenecks ({span_hours}h evaluated)."
            else:
                recommended_plan = 'pro'
                summary = f"Upgrade to '{recommended_plan.upper()}' recommended to alleviate observed bottlenecks."

        return {
            'status': status,
            'current_plan': current_plan,
            'recommended_plan': recommended_plan,
            'summary': summary,
            'evidence': {
                'evaluation_window': f"{round(span_hours / 24.0, 1)} days ({span_hours} hours)",
                'samples_evaluated': sample_cnt,
                'observed_span_seconds': span_seconds,
                'observed_span_hours': span_hours,
                'throttled_events': tot_throttle,
                'oom_kills': tot_oom,
                'task_limit_events': tot_tasks,
                'avg_cpu_allowance_pct': avg_cpu,
                'peak_cpu_allowance_pct': peak_cpu,
                'peak_mem_pct': peak_mem_pct,
                '7d_throttled_events': tot_throttle,
                '7d_oom_kills': tot_oom,
                '7d_task_limit_events': tot_tasks,
                '7d_avg_cpu_allowance_pct': avg_cpu,
                '7d_peak_cpu_allowance_pct': peak_cpu,
                '7d_peak_mem_pct': peak_mem_pct
            },
            'reasons': reasons
        }

    def get_account_optimization_guidance(self, username: str) -> Dict[str, Any]:
        """U17: Evidence-based optimization and slow-site explanation."""
        conn = self.get_db()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT AVG(cpu_allowance_percent) as avg_cpu,
                       AVG(mem_current_bytes) as avg_mem,
                       AVG(read_bytes_sec) as avg_read_bw,
                       AVG(write_bytes_sec) as avg_write_bw,
                       AVG(read_iops_sec + write_iops_sec) as avg_iops,
                       SUM(cpu_throttled_events) as throttled,
                       SUM(oom_kill_events) as oom
                FROM samples
                WHERE username = ? AND timestamp >= ?
            """, (username, int(time.time()) - 86400))
            row = cur.fetchone()
        finally:
            conn.close()

        avg_cpu = row['avg_cpu'] or 0.0 if row else 0.0
        avg_iops = row['avg_iops'] or 0.0 if row else 0.0
        avg_io_bw = (row['avg_read_bw'] or 0.0) + (row['avg_write_bw'] or 0.0) if row else 0.0
        throttled = row['throttled'] or 0 if row else 0
        oom = row['oom'] or 0 if row else 0

        bottlenecks = []
        actionable_steps = []

        if throttled > 0 or avg_cpu > 65.0:
            bottlenecks.append("PHP CPU Execution Bound")
            actionable_steps.append("Verify PHP OPcache is enabled. Benchmark optional JIT against your application before enabling it.")
            actionable_steps.append("Offload WordPress wp-cron.php from front-end pageviews to a scheduled system crontab.")
            actionable_steps.append("Audit third-party plugins and themes for recursive database lookups and unindexed queries.")

        if oom > 0:
            bottlenecks.append("Physical RAM Exhaustion (OOM Events)")
            actionable_steps.append("Lower PHP memory_limit if workers consume excess RAM per request.")
            actionable_steps.append("Install an in-memory object cache (Redis/Memcached) to prevent repetitive data hydration.")

        if avg_iops > 200 or avg_io_bw > 10 * 1024 * 1024:
            bottlenecks.append("Disk Throughput / IOPS Contention")
            actionable_steps.append("Enable server-side page caching (Nginx Microcache, LiteSpeed, or static HTML caching).")
            actionable_steps.append("Compress images to WebP/AVIF and leverage browser client caching headers.")

        if not bottlenecks:
            bottlenecks.append("No active bottlenecks detected")
            actionable_steps.append("Account resource profile is healthy. Continue monitoring live telemetry.")

        return {
            'primary_bottleneck': bottlenecks[0],
            'detected_bottlenecks': bottlenecks,
            'recommendations': actionable_steps,
            'metrics_observed': {
                '24h_avg_cpu_allowance_pct': round(avg_cpu, 1),
                '24h_avg_iops': round(avg_iops, 1),
                '24h_avg_io_bandwidth_mib': round(avg_io_bw / 1024 / 1024, 2),
                '24h_throttling_events': throttled,
                '24h_oom_events': oom
            }
        }

    def action_enduser_dashboard(self, username: str) -> Dict[str, Any]:
        users = self.collector.get_webuzo_users()
        if username not in users:
            conn_fb = self.get_db()
            try:
                c_fb = conn_fb.cursor()
                c_fb.execute("SELECT uid, plan_name FROM samples WHERE username = ? ORDER BY timestamp DESC LIMIT 1", (username,))
                r_fb = c_fb.fetchone()
                if r_fb:
                    udata = {'uid': r_fb['uid'], 'username': username, 'domain': f"{username}.test", 'plan_name': r_fb['plan_name'] or 'default'}
                else:
                    return {'error': f'User {username} not found on server'}
            finally:
                conn_fb.close()
        else:
            udata = users[username]

        uid = udata['uid']
        plan_name = udata['plan_name']
        limits = self.collector.get_plan_limits(plan_name)

        conn = self.get_db()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT * FROM samples WHERE username = ? ORDER BY timestamp DESC LIMIT 1
            """, (username,))
            latest = cur.fetchone()

            cur.execute("""
                SELECT * FROM temporary_overrides 
                WHERE username = ? AND status = 'active' AND expires_at > ?
                ORDER BY id DESC LIMIT 1
            """, (username, int(time.time())))
            active_override = cur.fetchone()
        finally:
            conn.close()

        is_telemetry_available = latest is not None
        sample_dict = dict(latest) if latest else {
            'cpu_percent': 0.0,
            'cpu_allowance_percent': 0.0,
            'cpu_throttled_events': 0,
            'mem_current_bytes': 0,
            'mem_anon_bytes': 0,
            'mem_file_bytes': 0,
            'mem_swap_bytes': 0,
            'oom_kill_events': 0,
            'tasks_current': 0,
            'task_limit_events': 0,
            'read_bytes_sec': 0.0,
            'write_bytes_sec': 0.0,
            'read_iops_sec': 0.0,
            'write_iops_sec': 0.0,
            'timestamp': int(time.time())
        }

        cpu_quota = limits['cpuquota']
        cpu_used_core = sample_dict.get('cpu_percent', 0.0)
        cpu_allowance_pct = sample_dict.get('cpu_allowance_percent', 0.0)

        mem_cur = sample_dict.get('mem_current_bytes', 0)
        mem_limit = limits['mem_max']
        mem_pct = round((mem_cur / mem_limit * 100), 2) if mem_limit > 0 else 0.0

        tasks_cur = sample_dict.get('tasks_current', 0)
        tasks_max = limits['maxtask']
        tasks_pct = round((tasks_cur / tasks_max * 100), 2) if tasks_max > 0 else 0.0

        read_lim_dec, read_lim_bin = parse_bw_to_bytes(limits.get('read_bw', 0))
        write_lim_dec, write_lim_bin = parse_bw_to_bytes(limits.get('write_bw', 0))
        read_limit_bytes = read_lim_bin if read_lim_bin > 0 else read_lim_dec
        write_limit_bytes = write_lim_bin if write_lim_bin > 0 else write_lim_dec

        cur_rbytes = float(sample_dict.get('read_bytes_sec', 0.0))
        cur_wbytes = float(sample_dict.get('write_bytes_sec', 0.0))

        r_ratio = (cur_rbytes / read_limit_bytes) if read_limit_bytes > 0 else 0.0
        w_ratio = (cur_wbytes / write_limit_bytes) if write_limit_bytes > 0 else 0.0
        io_pct = round(max(r_ratio, w_ratio) * 100, 1)

        return {
            'username': username,
            'domain': udata['domain'],
            'plan_name': plan_name,
            'telemetry_available': is_telemetry_available,
            'telemetry_status': 'available' if is_telemetry_available else 'initializing',
            'active_override': dict(active_override) if active_override else None,
            'current': {
                'cpu_percent': cpu_used_core,
                'cpu_used_percent_core': cpu_used_core,
                'cpu_allowance_percent': cpu_allowance_pct,
                'cpu_core_equivalent_formatted': f"{cpu_used_core}% of 1 CPU Core",
                'cpu_allowance_formatted': f"{cpu_allowance_pct}% of Assigned Allowance",
                'cpu_throttled_events': sample_dict.get('cpu_throttled_events', 0),
                'mem_current_bytes': mem_cur,
                'mem_current_formatted': format_bytes(mem_cur),
                'mem_anon_bytes': sample_dict.get('mem_anon_bytes', 0),
                'mem_anon_formatted': format_bytes(sample_dict.get('mem_anon_bytes', 0)),
                'mem_file_cache_bytes': sample_dict.get('mem_file_bytes', 0),
                'mem_file_cache_formatted': format_bytes(sample_dict.get('mem_file_bytes', 0)),
                'mem_swap_bytes': sample_dict.get('mem_swap_bytes', 0),
                'mem_swap_formatted': format_bytes(sample_dict.get('mem_swap_bytes', 0)),
                'mem_percent': mem_pct,
                'oom_kill_events': sample_dict.get('oom_kill_events', 0),
                'tasks_current': tasks_cur,
                'tasks_percent': tasks_pct,
                'task_limit_events': sample_dict.get('task_limit_events', 0),
                'read_bw_formatted': f"{round(cur_rbytes / 1024 / 1024, 2)} MiB/s",
                'write_bw_formatted': f"{round(cur_wbytes / 1024 / 1024, 2)} MiB/s",
                'total_bw_formatted': f"{round((cur_rbytes + cur_wbytes) / 1024 / 1024, 2)} MiB/s",
                'read_bytes_sec': cur_rbytes,
                'write_bytes_sec': cur_wbytes,
                'io_percent': io_pct,
                'read_iops': int(sample_dict.get('read_iops_sec', 0)),
                'write_iops': int(sample_dict.get('write_iops_sec', 0)),
                'last_sample_epoch': sample_dict.get('timestamp', int(time.time())),
                'freshness_seconds': int(time.time()) - sample_dict.get('timestamp', int(time.time()))
            },
            'limits': {
                'cpuquota': cpu_quota,
                'cpu_quota_percent': cpu_quota,
                'cpu_cores_equivalent': f"{cpu_quota / 100} Cores",
                'mem_max': mem_limit,
                'mem_max_formatted': format_bytes(mem_limit),
                'memhigh': limits['memhigh'],
                'memhigh_formatted': format_bytes(limits['memhigh']),
                'maxtask': tasks_max,
                'tasks_max': tasks_max,
                'read_bw': limits['read_bw'],
                'read_bw_bytes': read_limit_bytes,
                'read_bw_formatted': format_bytes(limits['read_bw']) + "/s",
                'write_bw': limits['write_bw'],
                'write_bw_bytes': write_limit_bytes,
                'write_bw_formatted': format_bytes(limits['write_bw']) + "/s",
                'diskread': limits['diskread'],
                'diskwrite': limits['diskwrite']
            },
            'permissions': {
                'allow_kill': self.collector.settings.get('enduser_allow_kill', True),
                'allow_export': self.collector.settings.get('enduser_allow_export', True),
                'allow_db_trace': self.collector.settings.get('enduser_allow_db_trace', True),
            },
            'thresholds': {
                'alert_threshold_cpu': self.collector.settings.get('alert_threshold_cpu', 75),
                'alert_threshold_mem': self.collector.settings.get('alert_threshold_mem', 80),
                'alert_threshold_tasks': self.collector.settings.get('alert_threshold_tasks', 80),
            },
            'php_workers': self.get_php_workers_by_version(uid),
            'upgrade_recommendation': self.get_account_upgrade_recommendations(username),
            'optimization_guidance': self.get_account_optimization_guidance(username)
        }

    def action_enduser_history(self, username: str, params: Dict[str, Any]) -> Dict[str, Any]:
        time_range = params.get('range', 'today')
        now = int(time.time())

        # Align 'today' and 'yesterday' to local midnight
        local_now = time.localtime(now)
        midnight_today = int(time.mktime((local_now.tm_year, local_now.tm_mon, local_now.tm_mday, 0, 0, 0, 0, 0, -1)))

        if time_range == 'today':
            start_ts = midnight_today
            end_ts = now
        elif time_range == 'yesterday':
            start_ts = midnight_today - 86400
            end_ts = midnight_today - 1
        elif time_range == '1h':
            start_ts = now - 3600
            end_ts = now
        elif time_range == '24h':
            start_ts = now - 86400
            end_ts = now
        elif time_range == '7d':
            start_ts = now - (7 * 86400)
            end_ts = now
        elif time_range == '30d':
            start_ts = now - (30 * 86400)
            end_ts = now
        elif time_range == 'custom':
            start_ts = int(params.get('start', now - 86400))
            end_ts = int(params.get('end', now))
        else:
            start_ts = midnight_today
            end_ts = now

        if 'end' in params and time_range == 'custom':
            try:
                end_ts = int(params['end'])
            except Exception:
                pass

        conn = self.get_db()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT timestamp, cpu_percent, cpu_allowance_percent, cpu_throttled_events,
                       mem_current_bytes, mem_anon_bytes, mem_swap_bytes, oom_kill_events,
                       tasks_current, task_limit_events, read_bytes_sec, write_bytes_sec,
                       read_iops_sec, write_iops_sec,
                       limit_cpu_quota, limit_mem_max_bytes, limit_tasks_max,
                       limit_io_read_bps, limit_io_write_bps, limit_io_read_iops, limit_io_write_iops
                FROM samples
                WHERE username = ? AND timestamp >= ? AND timestamp <= ?
                ORDER BY timestamp ASC
            """, (username, start_ts, end_ts))
            rows = [dict(row) for row in cur.fetchall()]
        finally:
            conn.close()

        def _to_int(val):
            if not val:
                return 0
            if isinstance(val, int):
                return val
            s = str(val).strip()
            if s.isdigit():
                return int(s)
            dec, _ = parse_bw_to_bytes(s)
            return dec

        total_len = len(rows)
        cpu_sum = 0.0
        cpu_peak = 0.0
        mem_sum = 0
        mem_peak = 0
        read_sum = 0.0
        write_sum = 0.0
        read_peak = 0.0
        write_peak = 0.0
        iops_sum = 0.0
        iops_peak = 0.0
        tasks_sum = 0
        tasks_peak = 0

        # Hourly grouping for Usage rollup table
        hourly_buckets: Dict[int, List[Any]] = {}

        for r in rows:
            ts = r['timestamp']
            h_start = (ts // 3600) * 3600
            if h_start not in hourly_buckets:
                hourly_buckets[h_start] = []
            hourly_buckets[h_start].append(r)

            c_val = float(r['cpu_percent'] or 0.0)
            m_val = int(r['mem_current_bytes'] or 0)
            rb_val = float(r['read_bytes_sec'] or 0.0)
            wb_val = float(r['write_bytes_sec'] or 0.0)
            ri_val = float(r['read_iops_sec'] or 0.0)
            wi_val = float(r['write_iops_sec'] or 0.0)
            tot_iops = ri_val + wi_val
            t_val = int(r['tasks_current'] or 0)

            cpu_sum += c_val
            if c_val > cpu_peak: cpu_peak = c_val
            mem_sum += m_val
            if m_val > mem_peak: mem_peak = m_val
            read_sum += rb_val
            write_sum += wb_val
            if rb_val > read_peak: read_peak = rb_val
            if wb_val > write_peak: write_peak = wb_val
            iops_sum += tot_iops
            if tot_iops > iops_peak: iops_peak = tot_iops
            tasks_sum += t_val
            if t_val > tasks_peak: tasks_peak = t_val

        # Construct Hourly Rollup Table (cPanel parity)
        hourly_usage = []
        for h_start in sorted(hourly_buckets.keys(), reverse=True):
            h_rows = hourly_buckets[h_start]
            c = len(h_rows)
            h_last = h_rows[-1]
            avg_cpu = sum(float(r['cpu_percent'] or 0) for r in h_rows) / c
            fault_cpu = sum(int(r['cpu_throttled_events'] or 0) for r in h_rows)
            lim_cpu = _to_int(h_last['limit_cpu_quota']) or 100

            avg_mem = sum(int(r['mem_current_bytes'] or 0) for r in h_rows) / c
            fault_mem = sum(int(r['oom_kill_events'] or 0) for r in h_rows)
            lim_mem = _to_int(h_last['limit_mem_max_bytes']) or (1024 * 1024 * 1024)

            avg_io = sum(float(r['read_bytes_sec'] or 0) + float(r['write_bytes_sec'] or 0) for r in h_rows) / c
            lim_io = _to_int(h_last['limit_io_read_bps']) + _to_int(h_last['limit_io_write_bps'])

            avg_nproc = sum(int(r['tasks_current'] or 0) for r in h_rows) / c
            fault_nproc = sum(int(r['task_limit_events'] or 0) for r in h_rows)
            lim_nproc = _to_int(h_last['limit_tasks_max']) or 64

            avg_iops = sum(float(r['read_iops_sec'] or 0) + float(r['write_iops_sec'] or 0) for r in h_rows) / c
            lim_iops = _to_int(h_last['limit_io_read_iops']) + _to_int(h_last['limit_io_write_iops'])

            hourly_usage.append({
                'from_time': time.strftime('%m-%d %H:00', time.localtime(h_start)),
                'to_time': time.strftime('%m-%d %H:00', time.localtime(h_start + 3600)),
                'from_ts': h_start,
                'to_ts': h_start + 3600,
                'speed': {'a': f"{avg_cpu:.1f}%", 'l': f"{lim_cpu}%", 'f': fault_cpu},
                'pmem': {'a': format_bytes(avg_mem), 'l': format_bytes(lim_mem), 'f': fault_mem},
                'io': {'a': f"{format_bytes(avg_io)}/s", 'l': f"{format_bytes(lim_io)}/s" if lim_io > 0 else 'Unlimited', 'f': 0},
                'ep': {'a': 'N/A', 'l': 'N/A', 'f': 0, 'status': 'unavailable'},
                'nproc': {'a': str(int(round(avg_nproc))), 'l': str(lim_nproc), 'f': fault_nproc},
                'iops': {'a': str(int(round(avg_iops))), 'l': str(lim_iops) if lim_iops > 0 else 'Unlimited', 'f': 0}
            })

        # Construct Account Total Summary Table
        last_sample = rows[-1] if rows else None
        cur_limit_cpu = _to_int(last_sample['limit_cpu_quota']) if last_sample else 100
        cur_limit_mem = _to_int(last_sample['limit_mem_max_bytes']) if last_sample else (1024 * 1024 * 1024)
        cur_limit_tasks = _to_int(last_sample['limit_tasks_max']) if last_sample else 64
        cur_limit_io = (_to_int(last_sample['limit_io_read_bps']) + _to_int(last_sample['limit_io_write_bps'])) if last_sample else 0
        cur_limit_iops = (_to_int(last_sample['limit_io_read_iops']) + _to_int(last_sample['limit_io_write_iops'])) if last_sample else 0

        tot_cpu_faults = sum(int(r['cpu_throttled_events'] or 0) for r in rows)
        tot_oom_faults = sum(int(r['oom_kill_events'] or 0) for r in rows)
        tot_task_faults = sum(int(r['task_limit_events'] or 0) for r in rows)

        avg_cpu_tot = cpu_sum / max(1, total_len)
        avg_mem_tot = mem_sum / max(1, total_len)
        avg_io_tot = (read_sum + write_sum) / max(1, total_len)
        avg_iops_tot = iops_sum / max(1, total_len)
        avg_tasks_tot = tasks_sum / max(1, total_len)

        account_total = [
            {'desc': 'SPEED', 'usage': f"{round(avg_cpu_tot, 1)}%", 'limit': f"{cur_limit_cpu}%", 'fault': tot_cpu_faults},
            {'desc': 'I/O', 'usage': f"{format_bytes(avg_io_tot)}/s", 'limit': f"{format_bytes(cur_limit_io)}/s" if cur_limit_io > 0 else 'Unlimited', 'fault': 0},
            {'desc': 'IOPS', 'usage': str(int(round(avg_iops_tot))), 'limit': str(cur_limit_iops) if cur_limit_iops > 0 else 'Unlimited', 'fault': 0},
            {'desc': 'NPROC', 'usage': str(int(round(avg_tasks_tot))), 'limit': str(cur_limit_tasks), 'fault': tot_task_faults},
            {'desc': 'Entry Processes', 'usage': 'N/A', 'limit': 'N/A', 'fault': 0, 'status': 'unavailable', 'note': 'Unenforced under Linux cgroups v2; concurrency governed via NPROC'},
            {'desc': 'Physical Memory', 'usage': format_bytes(int(avg_mem_tot)), 'limit': format_bytes(cur_limit_mem), 'fault': tot_oom_faults}
        ]

        # Downsample points for smooth browser chart rendering (target ~300 points)
        target_points = 300
        step = max(1, total_len // target_points)
        points = []

        for i in range(0, total_len, step):
            chunk = rows[i:i+step]
            if not chunk: continue
            cl = len(chunk)
            last_c = chunk[-1]
            mid_c = chunk[cl // 2]

            c_cpu = sum(float(r['cpu_percent'] or 0) for r in chunk) / cl
            c_mem = sum(int(r['mem_current_bytes'] or 0) for r in chunk) / cl
            c_swap = sum(int(r['mem_swap_bytes'] or 0) for r in chunk) / cl
            c_rb = sum(float(r['read_bytes_sec'] or 0) for r in chunk) / cl
            c_wb = sum(float(r['write_bytes_sec'] or 0) for r in chunk) / cl
            c_ri = sum(float(r['read_iops_sec'] or 0) for r in chunk) / cl
            c_wi = sum(float(r['write_iops_sec'] or 0) for r in chunk) / cl
            c_tasks = sum(int(r['tasks_current'] or 0) for r in chunk) / cl
            c_faults = sum(int(r['cpu_throttled_events'] or 0) + int(r['oom_kill_events'] or 0) + int(r['task_limit_events'] or 0) for r in chunk)

            lim_c_cpu = _to_int(last_c['limit_cpu_quota']) or 100
            lim_c_mem = _to_int(last_c['limit_mem_max_bytes']) or (1024 * 1024 * 1024)
            lim_c_swap = None  # Historical swap ceilings were not stored in this schema.
            lim_c_tasks = _to_int(last_c['limit_tasks_max']) or 64
            lim_c_io = _to_int(last_c['limit_io_read_bps']) + _to_int(last_c['limit_io_write_bps'])
            lim_c_iops = _to_int(last_c['limit_io_read_iops']) + _to_int(last_c['limit_io_write_iops'])

            points.append({
                't': mid_c['timestamp'],
                'cpu': round(c_cpu, 1),
                'speed': round(c_cpu, 1),
                'limit_cpu': lim_c_cpu,
                'limit_speed': lim_c_cpu,
                'cpu_allowance': float(mid_c['cpu_allowance_percent'] or 0.0),
                'cpu_throttled': int(mid_c['cpu_throttled_events'] or 0),
                'mem': int(c_mem),
                'pmem': round(c_mem / (1024 * 1024), 1),
                'limit_mem': lim_c_mem,
                'limit_pmem': round(lim_c_mem / (1024 * 1024), 1),
                'vmem': round((c_mem + c_swap) / (1024 * 1024), 1),
                'limit_vmem': None,
                'vmem_label': 'RAM + Swap (historical combined limit unavailable)',
                'read_bytes': round(c_rb, 1),
                'write_bytes': round(c_wb, 1),
                'io': round((c_rb + c_wb) / 1024, 1),  # KiB/s
                'limit_io': round(lim_c_io / 1024, 1) if lim_c_io > 0 else 0,
                'read_iops': round(c_ri, 1),
                'write_iops': round(c_wi, 1),
                'iops': round(c_ri + c_wi, 1),
                'limit_iops': lim_c_iops,
                'tasks': int(round(c_tasks)),
                'nproc': int(round(c_tasks)),
                'limit_tasks': lim_c_tasks,
                'limit_nproc': lim_c_tasks,
                'ep': None,
                'limit_ep': None,
                'faults': c_faults
            })

        summary = {
            'cpu_avg': round(avg_cpu_tot, 2),
            'cpu_peak': round(cpu_peak, 2),
            'mem_avg_bytes': int(avg_mem_tot),
            'mem_peak_bytes': mem_peak,
            'read_bps_peak': round(read_peak, 2),
            'write_bps_peak': round(write_peak, 2),
            'iops_peak': round(iops_peak, 2),
            'tasks_peak': tasks_peak
        }

        return {
            'username': username,
            'range': time_range,
            'start_timestamp': start_ts,
            'end_timestamp': end_ts,
            'start_ts': start_ts,
            'end_ts': end_ts,
            'points_count': len(points),
            'total_samples': total_len,
            'summary': summary,
            'account_total': account_total,
            'hourly_usage': hourly_usage,
            'points': points
        }

    def action_enduser_processes(self, username: str) -> Dict[str, Any]:
        users = self.collector.get_webuzo_users()
        if username not in users:
            return {'error': f'User {username} not found'}
        uid = users[username]['uid']
        slice_path, _ = self.collector.read_user_cgroup(uid)
        procs = self.collector.get_process_list_for_user(uid, slice_path)
        return {
            'username': username,
            'uid': uid,
            'count': len(procs),
            'processes': procs
        }

    def action_stop_enduser_process(self, username: str, params: Dict[str, Any], is_admin: bool = False) -> Dict[str, Any]:
        """
        Controlled process termination with strict identity verification.
        Uses stable Linux pidfd handle where supported, and verifies UID + start_time before every signal.
        """
        pid = int(params.get('pid', 0))
        expected_start_time = int(params.get('start_time', 0))

        if not is_admin:
            if not self.collector.settings.get('enduser_allow_kill', True) or not self.is_permission_granted(username, 'enduser', 'can_stop_processes'):
                return {'error': f"Permission Denied: Process termination is disabled for account '{username}'.", 'status_code': 403}

        if pid <= 1:
            return {'error': 'Invalid PID'}

        # Defect D Fix: strictly reject start_time=0 bypass
        if expected_start_time <= 0:
            return {'error': 'Security Refusal: Positive process start_time verification token required'}

        has_pidfd = getattr(self, 'has_pidfd', hasattr(os, 'pidfd_open') and hasattr(signal, 'pidfd_send_signal'))
        if not has_pidfd:
            return {'error': 'Safe process termination requires Linux pidfd support (kernel 5.3+). Operation aborted to prevent PID recycling races.'}

        users = self.collector.get_webuzo_users()
        if username not in users:
            return {'error': 'User not found'}
        uid = users[username]['uid']

        proc_stat_path = f'/proc/{pid}/stat'
        if not os.path.exists(proc_stat_path):
            return {'error': 'Process does not exist or already terminated'}

        pfd = None
        try:
            try:
                # 1. Acquire stable pidfd handle FIRST to pin the kernel process instance
                pfd = os.pidfd_open(pid, 0)
            except ProcessLookupError:
                return {'error': 'Process does not exist or already terminated'}
            except Exception as e:
                return {'error': f'Failed to acquire stable process handle (pidfd): {str(e)}'}

            # 2. Re-verify process ownership and start_time under handle protection
            try:
                stat_info = os.stat(f'/proc/{pid}')
                if stat_info.st_uid != uid:
                    return {'error': 'Security Refusal: Process does not belong to your account'}

                with open(proc_stat_path, 'r', encoding='utf-8', errors='replace') as f:
                    c = f.read()
                    parts = c[c.rfind(')') + 2:].split()
                    actual_start = int(parts[19]) if len(parts) > 19 else 0
                    if actual_start != expected_start_time:
                        return {'error': 'Security Refusal: Process start-time verification failed (PID was reused by another process)'}
            except (FileNotFoundError, ProcessLookupError):
                return {'error': 'Process terminated during identity verification'}

            # 3. Send SIGTERM via stable pinned handle
            try:
                signal.pidfd_send_signal(pfd, signal.SIGTERM)
                time.sleep(0.4)
                if os.path.exists(proc_stat_path):
                    # Re-verify stat before sending SIGKILL through the SAME pinned handle
                    try:
                        with open(proc_stat_path, 'r', encoding='utf-8', errors='replace') as f2:
                            c2 = f2.read()
                            p2 = c2[c2.rfind(')') + 2:].split()
                            if int(p2[19]) == expected_start_time:
                                signal.pidfd_send_signal(pfd, signal.SIGKILL)
                    except Exception:
                        pass
            except Exception:
                pass
            conn = self.get_db()
            try:
                conn.execute("""
                    INSERT INTO audit_log (timestamp, actor, action, target_account, details_json)
                    VALUES (?, ?, ?, ?, ?)
                """, (int(time.time()), username, 'stop_process', username, json.dumps({'pid': pid, 'start_time': expected_start_time})))
                conn.commit()
            finally:
                conn.close()

            return {'success': True, 'message': f'Process {pid} terminated safely'}
        except ProcessLookupError:
            return {'success': True, 'message': f'Process {pid} already stopped'}
        except Exception as e:
            return {'error': f'Failed to terminate process: {str(e)}'}
        finally:
            if pfd is not None:
                try:
                    os.close(pfd)
                except OSError:
                    pass
                pfd = None

    def action_enduser_snapshots(self, username: str, params: Dict[str, Any]) -> Dict[str, Any]:
        limit = int(params.get('limit', 20))
        conn = self.get_db()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT id, timestamp, trigger_type, processes_json, web_diagnostics_json, db_diagnostics_json, metrics_summary_json
                FROM snapshots
                WHERE username = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (username, limit))
            rows = cur.fetchall()
        finally:
            conn.close()

        allow_db_trace = self.collector.settings.get('enduser_allow_db_trace', True)
        snapshots = []
        for r in rows:
            snapshots.append({
                'id': r['id'],
                'timestamp': r['timestamp'],
                'trigger_type': r['trigger_type'],
                'processes': json.loads(r['processes_json']) if r['processes_json'] else [],
                'web_diagnostics': json.loads(r['web_diagnostics_json']) if r['web_diagnostics_json'] else [],
                'db_diagnostics': (json.loads(r['db_diagnostics_json']) if r['db_diagnostics_json'] else []) if allow_db_trace else [],
                'metrics_summary': json.loads(r['metrics_summary_json']) if r['metrics_summary_json'] else {}
            })
        return {'success': True, 'username': username, 'count': len(snapshots), 'snapshots': snapshots}

    def action_get_snapshots_index(self, username: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fetch distinct snapshot dates and list of snapshots on the selected date for cPanel-style navigation.
        """
        conn = self.get_db()
        try:
            cur = conn.cursor()
            # 1. Distinct dates for this user
            cur.execute("""
                SELECT DISTINCT strftime('%Y-%m-%d', timestamp, 'unixepoch') AS d, COUNT(*) as cnt
                FROM snapshots
                WHERE username = ?
                GROUP BY d
                ORDER BY d DESC
            """, (username,))
            date_rows = cur.fetchall()

            if not date_rows:
                return {
                    'username': username,
                    'available_dates': [],
                    'selected_date': '',
                    'snapshots': [],
                    'current_snapshot': None,
                    'count': 0
                }

            available_dates = []
            for r in date_rows:
                d_str = r['d']
                try:
                    dt = time.strptime(d_str, '%Y-%m-%d')
                    lbl = time.strftime('%B %d, %Y', dt)
                except Exception:
                    lbl = d_str
                available_dates.append({
                    'date': d_str,
                    'label': lbl,
                    'count': r['cnt']
                })

            selected_date = params.get('date') or available_dates[0]['date']
            if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', selected_date):
                selected_date = available_dates[0]['date']

            # 2. Fetch all snapshots on selected_date ordered chronologically
            cur.execute("""
                SELECT id, timestamp, trigger_type, processes_json, web_diagnostics_json, db_diagnostics_json, metrics_summary_json
                FROM snapshots
                WHERE username = ? AND strftime('%Y-%m-%d', timestamp, 'unixepoch') = ?
                ORDER BY timestamp ASC
            """, (username, selected_date))
            snap_rows = cur.fetchall()

            snapshots = []
            target_snap_id = int(params.get('snapshot_id', 0)) if params.get('snapshot_id') else None
            selected_snap_row = None

            for sr in snap_rows:
                ts = sr['timestamp']
                t_str = time.strftime('%H:%M:%S', time.gmtime(ts))
                snapshots.append({
                    'id': sr['id'],
                    'timestamp': ts,
                    'time_str': t_str,
                    'trigger_type': sr['trigger_type']
                })
                if target_snap_id and sr['id'] == target_snap_id:
                    selected_snap_row = sr

            if not selected_snap_row and snap_rows:
                selected_snap_row = snap_rows[-1]

            # 3. Format current snapshot detail
            current_snapshot = None
            if selected_snap_row:
                allow_db_trace = self.collector.settings.get('enduser_allow_db_trace', True)
                procs = json.loads(selected_snap_row['processes_json']) if selected_snap_row['processes_json'] else []
                for p in procs:
                    if 'cpu_formatted' not in p:
                        cpu_pct = p.get('cpu_percent', 0.0)
                        p['cpu_formatted'] = f"{int(round(cpu_pct))}%"
                    if 'mem_formatted' not in p:
                        mem_mb = p.get('mem_mb', round(p.get('rss_bytes', 0) / (1024 * 1024)))
                        p['mem_formatted'] = f"{mem_mb}"

                current_snapshot = {
                    'id': selected_snap_row['id'],
                    'timestamp': selected_snap_row['timestamp'],
                    'date_str': time.strftime('%B %d, %Y', time.gmtime(selected_snap_row['timestamp'])),
                    'time_str': time.strftime('%H:%M:%S', time.gmtime(selected_snap_row['timestamp'])),
                    'trigger_type': selected_snap_row['trigger_type'],
                    'processes': procs,
                    'web_diagnostics': json.loads(selected_snap_row['web_diagnostics_json']) if selected_snap_row['web_diagnostics_json'] else [],
                    'db_diagnostics': (json.loads(selected_snap_row['db_diagnostics_json']) if selected_snap_row['db_diagnostics_json'] else []) if allow_db_trace else [],
                    'metrics_summary': json.loads(selected_snap_row['metrics_summary_json']) if selected_snap_row['metrics_summary_json'] else {}
                }

            return {
                'username': username,
                'available_dates': available_dates,
                'selected_date': selected_date,
                'snapshots': snapshots,
                'current_snapshot': current_snapshot,
                'count': len(snapshots)
            }
        finally:
            conn.close()

    def action_get_snapshot_detail(self, username: str, params: Dict[str, Any]) -> Dict[str, Any]:
        snap_id = int(params.get('snapshot_id', 0))
        if snap_id <= 0:
            return {'error': 'Invalid snapshot_id'}

        conn = self.get_db()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT id, timestamp, trigger_type, processes_json, web_diagnostics_json, db_diagnostics_json, metrics_summary_json
                FROM snapshots
                WHERE id = ? AND username = ?
            """, (snap_id, username))
            row = cur.fetchone()
            if not row:
                return {'error': 'Snapshot not found or does not belong to specified user'}

            allow_db_trace = self.collector.settings.get('enduser_allow_db_trace', True)
            procs = json.loads(row['processes_json']) if row['processes_json'] else []
            for p in procs:
                if 'cpu_formatted' not in p:
                    cpu_pct = p.get('cpu_percent', 0.0)
                    p['cpu_formatted'] = f"{int(round(cpu_pct))}%"
                if 'mem_formatted' not in p:
                    mem_mb = p.get('mem_mb', round(p.get('rss_bytes', 0) / (1024 * 1024)))
                    p['mem_formatted'] = f"{mem_mb}"

            return {
                'snapshot': {
                    'id': row['id'],
                    'timestamp': row['timestamp'],
                    'date_str': time.strftime('%B %d, %Y', time.gmtime(row['timestamp'])),
                    'time_str': time.strftime('%H:%M:%S', time.gmtime(row['timestamp'])),
                    'trigger_type': row['trigger_type'],
                    'processes': procs,
                    'web_diagnostics': json.loads(row['web_diagnostics_json']) if row['web_diagnostics_json'] else [],
                    'db_diagnostics': (json.loads(row['db_diagnostics_json']) if row['db_diagnostics_json'] else []) if allow_db_trace else [],
                    'metrics_summary': json.loads(row['metrics_summary_json']) if row['metrics_summary_json'] else {}
                }
            }
        finally:
            conn.close()

    def action_enduser_notifications(self, username: str) -> Dict[str, Any]:
        conn = self.get_db()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT e.id, e.timestamp, e.event_type, e.severity, e.message, e.details_json,
                       COALESCE(ns.status, 'unread') AS status
                FROM events e
                LEFT JOIN notification_state ns ON e.id = ns.event_id AND e.username = ns.username
                WHERE e.username = ?
                ORDER BY e.timestamp DESC
                LIMIT 50
            """, (username,))
            rows = cur.fetchall()
        finally:
            conn.close()

        events = []
        unread_count = 0
        for r in rows:
            st = r['status']
            if st == 'unread':
                unread_count += 1
            events.append({
                'id': r['id'],
                'timestamp': r['timestamp'],
                'event_type': r['event_type'],
                'severity': r['severity'],
                'message': r['message'],
                'status': st,
                'details': json.loads(r['details_json']) if r['details_json'] else {}
            })
        return {'username': username, 'count': len(events), 'unread_count': unread_count, 'events': events}

    def action_mark_notification(self, username: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """U14: Persisted notification read/dismiss preferences with single and bulk clearing support."""
        event_id_raw = params.get('event_id', 0)
        mark_all = bool(params.get('all', False)) or str(event_id_raw).lower() in ('all', 'clear_all', '0')
        status = str(params.get('status', 'read')).lower()
        if status not in ('read', 'dismissed', 'unread'):
            status = 'read'

        conn = self.get_db()
        try:
            now = int(time.time())
            if mark_all:
                # Query all events for target tenant
                events = conn.execute("SELECT id FROM events WHERE username = ?", (username,)).fetchall()
                
                count = 0
                for ev in events:
                    eid = ev['id']
                    if status == 'unread':
                        conn.execute("DELETE FROM notification_state WHERE username = ? AND event_id = ?", (username, eid))
                    else:
                        conn.execute("""
                            INSERT INTO notification_state (username, event_id, status, updated_at)
                            VALUES (?, ?, ?, ?)
                            ON CONFLICT(username, event_id) DO UPDATE SET status = excluded.status, updated_at = excluded.updated_at
                        """, (username, eid, status, now))
                    count += 1
                conn.commit()
                return {
                    'success': True,
                    'bulk': True,
                    'count': count,
                    'status': status,
                    'message': f'All notifications ({count}) marked as {status}.'
                }

            event_id = int(event_id_raw)
            if event_id <= 0:
                return {'error': 'Invalid event_id'}

            if status == 'unread':
                conn.execute("DELETE FROM notification_state WHERE username = ? AND event_id = ?", (username, event_id))
            else:
                conn.execute("""
                    INSERT INTO notification_state (username, event_id, status, updated_at)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(username, event_id) DO UPDATE SET status = excluded.status, updated_at = excluded.updated_at
                """, (username, event_id, status, now))
            conn.commit()
            return {'success': True, 'event_id': event_id, 'status': status}
        finally:
            conn.close()

    def action_enduser_support_export(self, username: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """U18: Selected-time-range support export with full telemetry, process, and diagnostics."""
        if not self.collector.settings.get('enduser_allow_export', True) or not self.is_permission_granted(username, 'enduser', 'can_export_diagnostics'):
            return {'error': f"Permission Denied: Diagnostic report export has been disabled for account '{username}'.", 'status_code': 403}

        export_range = str(params.get('range', '24h'))
        dash = self.action_enduser_dashboard(username)
        history = self.action_enduser_history(username, {
            'range': export_range,
            'start': params.get('start'),
            'end': params.get('end')
        })
        notifs = self.action_enduser_notifications(username)
        snaps = self.action_enduser_snapshots(username, {'limit': 10})
        procs = self.action_enduser_processes(username)

        points = history.get('points', [])
        export_data = {
            'report_metadata': {
                'generator': 'UNISELV Resource Manager v1.1.13',
                'account': username,
                'exported_at': int(time.time()),
                'exported_iso': time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime()),
                'range_requested': export_range,
                'points_count': len(points),
                'privacy_policy': 'Sensitive credentials, passwords, and authorization tokens have been redacted.'
            },
            'range_requested': export_range,
            'account_summary': dash,
            'php_workers': dash.get('php_workers', {}),
            'telemetry_summary': history.get('summary', {}),
            'telemetry_data': points,
            'recent_24h_telemetry': points[-720:] if points else [],
            'active_processes': procs.get('processes', []),
            'incidents_and_events': notifs.get('events', []),
            'diagnostic_snapshots': snaps.get('snapshots', []),
            'upgrade_recommendation': dash.get('upgrade_recommendation', {}),
            'optimization_guidance': dash.get('optimization_guidance', {})
        }
        return {'success': True, 'report': export_data}

    # ==================== ADMIN ACTIONS ====================

    def action_admin_overview(self) -> Dict[str, Any]:
        users = self.collector.get_webuzo_users()
        total_accounts = len(users)

        conn = self.get_db()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM system_metrics ORDER BY timestamp DESC LIMIT 1")
            sys_m = cur.fetchone()
            cur.execute("""
                SELECT s.* FROM samples s
                INNER JOIN (
                    SELECT username, MAX(timestamp) as max_ts FROM samples GROUP BY username
                ) latest ON s.username = latest.username AND s.timestamp = latest.max_ts
            """)
            latest_user_samples = {r['username']: dict(r) for r in cur.fetchall()}
        finally:
            conn.close()

        sys_dict = dict(sys_m) if sys_m else {}

        # Real-time kernel load averages directly from /proc/loadavg
        try:
            l1, l5, l15 = os.getloadavg()
        except Exception:
            l1 = float(sys_dict.get('load1', 0.0))
            l5 = float(sys_dict.get('load5', 0.0))
            l15 = float(sys_dict.get('load15', 0.0))

        # Shared services breakdown
        mariadb_mem = parse_int_file('/sys/fs/cgroup/golden.slice/mariadb.service/memory.current')
        apache_mem = parse_int_file('/sys/fs/cgroup/golden.slice/golden-apache.service/memory.current')
        panel_mem = parse_int_file('/sys/fs/cgroup/system.slice/webuzo.service/memory.current')
        agent_mem = parse_int_file('/sys/fs/cgroup/system.slice/uniselv-resman-agent.service/memory.current')

        tot_mem = sys_dict.get('mem_used_bytes', 0) + sys_dict.get('mem_available_bytes', 0)
        mem_pct = round((sys_dict.get('mem_used_bytes', 0) / tot_mem * 100), 2) if tot_mem > 0 else 0.0
        cpu_count = os.cpu_count()

        host_dict = {
            'cpu_count': cpu_count,
            'cpu_cores': cpu_count,
            'cpu_percent': sys_dict.get('cpu_percent', 0.0),
            'mem_total_formatted': format_bytes(tot_mem) if sys_m else 'Unavailable',
            'total_ram_formatted': format_bytes(tot_mem) if sys_m else 'Unavailable',
            'mem_used_formatted': format_bytes(sys_dict.get('mem_used_bytes', 0)),
            'mem_percent': mem_pct,
            'swap_used_formatted': format_bytes(sys_dict.get('swap_used_bytes', 0)),
            'load1': round(l1, 2),
            'load5': round(l5, 2),
            'load15': round(l15, 2),
            'maintenance_mode': self.maintenance_mode
        }

        gs_status = self.golden_shield.get_status()
        calc = gs_status.get('calculated_policy') or gs_status.get('configured_policy') or {}
        # Display configured policy, not an unapplied Auto recommendation in Manual mode.
        policy = gs_status.get('configured_policy') or {}
        gs_status['customer_cpu_percent'] = policy.get('customerCpuPercent')
        gs_status['reserved_cpu_percent'] = policy.get('reservedCpuPercent')
        host_mem_max_mib = policy.get('hostingMemoryMaxMiB')
        gs_status['hosting_memory_max_mib'] = host_mem_max_mib
        gs_status['golden_mem_max_formatted'] = (f"{round(host_mem_max_mib / 1024, 2)} GiB"
                                                 if host_mem_max_mib is not None else 'Unavailable')
        gs_status['headroom_mib'] = policy.get('headroomMiB')
        # The aggregate includes MariaDB/Apache as well as accounts; summing a
        # nonexistent samples.mem_bytes field previously fabricated zero usage.
        try:
            aggregate_mem = int(pathlib.Path('/sys/fs/cgroup/golden.slice/memory.current').read_text().strip())
        except (OSError, ValueError):
            aggregate_mem = None
        gs_status['golden_mem_current_bytes'] = aggregate_mem
        gs_status['golden_mem_current_formatted'] = format_bytes(aggregate_mem) if aggregate_mem is not None else 'Unavailable'
        gs_status['memory_measurement'] = 'golden.slice/memory.current' if aggregate_mem is not None else 'unavailable'
        host_dict['telemetry_available'] = bool(sys_m)
        host_dict['last_sample_epoch'] = sys_dict.get('timestamp')

        return {
            'server': host_dict,
            'host': host_dict,
            'golden_shield': gs_status,
            'shared_services': {
                'mariadb_mem_formatted': format_bytes(mariadb_mem),
                'apache_mem_formatted': format_bytes(apache_mem),
                'webuzo_panel_mem_formatted': format_bytes(panel_mem),
                'agent_daemon_mem_formatted': format_bytes(agent_mem)
            },
            'total_accounts': total_accounts
        }

    def action_admin_accounts(self, params: Dict[str, Any], actor: str = 'root', is_reseller: bool = False) -> Dict[str, Any]:
        users = self.collector.get_webuzo_users()
        conn = self.get_db()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT s.* FROM samples s
                INNER JOIN (
                    SELECT username, MAX(timestamp) as max_ts FROM samples GROUP BY username
                ) latest ON s.username = latest.username AND s.timestamp = latest.max_ts
            """)
            latest_samples = {r['username']: dict(r) for r in cur.fetchall()}
        finally:
            conn.close()

        accounts_list = []
        for uname, udata in sorted(users.items()):
            uid = udata['uid']
            plan_name = udata['plan_name']
            domain = udata['domain']
            limits = self.collector.get_plan_limits(plan_name)
            sample = latest_samples.get(uname, {})

            mem_used = sample.get('mem_current_bytes', 0)
            mem_max = limits['mem_max']
            mem_pct = round((mem_used / mem_max * 100), 2) if mem_max > 0 else 0.0

            accounts_list.append({
                'username': uname,
                'uid': uid,
                'domain': domain,
                'plan_name': plan_name,
                'cpu_percent': sample.get('cpu_percent', 0.0),
                'cpu_allowance_percent': sample.get('cpu_allowance_percent', 0.0),
                'mem_used_bytes': mem_used,
                'mem_formatted': format_bytes(mem_used),
                'mem_percent': mem_pct,
                'tasks_current': sample.get('tasks_current', 0),
                'tasks_max': limits['maxtask'],
                'throttled_events': sample.get('cpu_throttled_events', 0),
                'oom_events': sample.get('oom_kill_events', 0),
                'last_sample_epoch': sample.get('timestamp', 0),
                'owner': udata.get('owner', 'root'),
                'is_reseller': udata.get('reseller', False)
            })

        # B01: Reseller ownership filtering
        if is_reseller and actor != 'root':
            accounts_list = [a for a in accounts_list if a.get('owner') == actor or a.get('username') == actor]
        elif params.get('owner'):
            accounts_list = [a for a in accounts_list if a.get('owner') == params.get('owner')]

        return {
            'count': len(accounts_list),
            'accounts': accounts_list,
            'reseller_scope': actor if is_reseller else None
        }

    def action_admin_account_detail(self, username: str, params: Dict[str, Any], actor: str = 'root', is_reseller: bool = False) -> Dict[str, Any]:
        if is_reseller and actor != 'root':
            users = self.collector.get_webuzo_users()
            target_data = users.get(username)
            if not target_data or (target_data.get('owner') != actor and username != actor):
                return {
                    'error': f"Forbidden: Reseller '{actor}' is not authorized to inspect account '{username}' (owned by '{target_data.get('owner') if target_data else 'unknown'}')",
                    'status_code': 403
                }

        dash = self.action_enduser_dashboard(username)
        procs = self.action_enduser_processes(username)
        history = self.action_enduser_history(username, params)
        notifications = self.action_enduser_notifications(username)
        snapshots = self.action_enduser_snapshots(username, params)

        return {
            'account': dash,
            'processes': procs,
            'history': history,
            'notifications': notifications,
            'snapshots': snapshots
        }

    def action_get_permissions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """B04: Query role-level baselines and per-account granular permission overrides."""
        target_user = params.get('username')
        conn = self.get_db()
        try:
            cur = conn.cursor()
            cur.execute("SELECT role, permission, granted, updated_at FROM role_permissions ORDER BY role, permission")
            role_perms = [dict(r) for r in cur.fetchall()]

            if target_user:
                cur.execute("SELECT username, permission, granted, updated_at, updated_by FROM account_permissions WHERE username = ?", (target_user,))
            else:
                cur.execute("SELECT username, permission, granted, updated_at, updated_by FROM account_permissions ORDER BY username, permission")
            acc_perms = [dict(r) for r in cur.fetchall()]

            return {
                'role_permissions': role_perms,
                'account_permissions': acc_perms,
                'available_permissions': [
                    {'key': 'can_stop_processes', 'label': 'Stop Own Processes', 'description': 'Allow enduser to terminate their own stuck processes'},
                    {'key': 'can_export_diagnostics', 'label': 'Support Diagnostic Export', 'description': 'Allow generating and downloading support export bundles'},
                    {'key': 'can_view_history', 'label': 'View Historical Telemetry', 'description': 'Allow querying historical metrics charts and samples'}
                ]
            }
        finally:
            conn.close()

    def action_save_account_permission(self, admin_user: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """B04: Set granular permission grant or denial for an individual hosting account."""
        username = params.get('username')
        permission = params.get('permission')
        granted = 1 if params.get('granted', True) in (True, 1, '1', 'true', 'True') else 0

        if not username or not permission:
            return {'error': 'Missing required fields: username and permission are mandatory', 'status_code': 400}

        conn = self.get_db()
        try:
            now = int(time.time())
            conn.execute("""
                INSERT INTO account_permissions (username, permission, granted, updated_at, updated_by)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(username, permission) DO UPDATE SET
                    granted = excluded.granted,
                    updated_at = excluded.updated_at,
                    updated_by = excluded.updated_by
            """, (username, permission, granted, now, admin_user))

            conn.execute("""
                INSERT INTO audit_log (timestamp, actor, action, target_account, details_json)
                VALUES (?, ?, 'set_account_permission', ?, ?)
            """, (now, admin_user, username, json.dumps({'permission': permission, 'granted': granted})))

            conn.commit()
            return {
                'status': 'success',
                'username': username,
                'permission': permission,
                'granted': bool(granted),
                'updated_at': now
            }
        finally:
            conn.close()

    def action_save_role_permission(self, admin_user: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """B04: Update role baseline permission."""
        role = params.get('role')
        permission = params.get('permission')
        granted = 1 if params.get('granted', True) in (True, 1, '1', 'true', 'True') else 0

        if not role or not permission:
            return {'error': 'Missing required fields: role and permission are mandatory', 'status_code': 400}

        conn = self.get_db()
        try:
            now = int(time.time())
            conn.execute("""
                INSERT INTO role_permissions (role, permission, granted, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(role, permission) DO UPDATE SET
                    granted = excluded.granted,
                    updated_at = excluded.updated_at
            """, (role, permission, granted, now))

            conn.execute("""
                INSERT INTO audit_log (timestamp, actor, action, target_account, details_json)
                VALUES (?, ?, 'set_role_permission', ?, ?)
            """, (now, admin_user, f"role:{role}", json.dumps({'permission': permission, 'granted': granted})))

            conn.commit()
            return {
                'status': 'success',
                'role': role,
                'permission': permission,
                'granted': bool(granted),
                'updated_at': now
            }
        finally:
            conn.close()

    def action_admin_audit_limits(self) -> Dict[str, Any]:
        """
        Audit configured versus active kernel limits with numerical quota/period comparisons.
        Validates cpu.max, memory.max, memory.high, memory.swap.max, and pids.max.
        """
        users = self.collector.get_webuzo_users()
        audit_results = []
        for uname, udata in users.items():
            uid = udata['uid']
            plan_name = udata['plan_name']
            limits = self.collector.get_plan_limits(plan_name)

            unit_path = f'/etc/systemd/system/golden-{uid}.slice'
            unit_exists = os.path.exists(unit_path)
            cgroup_path = f'/sys/fs/cgroup/golden.slice/golden-{uid}.slice'
            if not os.path.exists(cgroup_path):
                cgroup_path = f'/sys/fs/cgroup/{uid}.slice'

            effective_cpu = "n/a"
            effective_mem = "n/a"
            effective_mem_high = "n/a"
            effective_swap = "n/a"
            effective_pids = "n/a"

            if os.path.exists(cgroup_path):
                try:
                    with open(os.path.join(cgroup_path, 'cpu.max')) as f:
                        effective_cpu = f.read().strip()
                    with open(os.path.join(cgroup_path, 'memory.max')) as f:
                        effective_mem = f.read().strip()
                    with open(os.path.join(cgroup_path, 'memory.high')) as f:
                        effective_mem_high = f.read().strip()
                    with open(os.path.join(cgroup_path, 'memory.swap.max')) as f:
                        effective_swap = f.read().strip()
                    with open(os.path.join(cgroup_path, 'pids.max')) as f:
                        effective_pids = f.read().strip()
                except Exception:
                    pass

            # Defect F Fix: Numerical CPU quota/period calculation
            cpu_synced = False
            actual_cpu_pct = 0.0
            if effective_cpu != "n/a" and " " in effective_cpu:
                q_str, p_str = effective_cpu.split()
                if q_str.isdigit() and p_str.isdigit() and int(p_str) > 0:
                    actual_cpu_pct = round((int(q_str) / int(p_str)) * 100, 1)
                    cpu_synced = (actual_cpu_pct == float(limits['cpuquota']))

            mem_synced = (effective_mem.isdigit() and int(effective_mem) == limits['mem_max'])
            mem_high_synced = (effective_mem_high.isdigit() and int(effective_mem_high) == limits['memhigh'])
            swap_zero = (effective_swap == '0')
            pids_synced = (effective_pids.isdigit() and int(effective_pids) == limits['maxtask'])
            ancestor_protected = (
                os.path.exists('/sys/fs/cgroup/golden.slice') and 
                cgroup_path.startswith('/sys/fs/cgroup/golden.slice/')
            )

            # I/O cgroup verification (A06): read /sys/fs/cgroup/.../io.max
            io_path = os.path.join(cgroup_path, 'io.max')
            effective_rbps = "max"
            effective_wbps = "max"
            effective_riops = "max"
            effective_wiops = "max"
            io_synced = True

            if os.path.exists(io_path):
                try:
                    with open(io_path, 'r') as f:
                        io_content = f.read().strip()
                    for line in io_content.splitlines():
                        parts = line.split()
                        if len(parts) >= 2:
                            for p in parts[1:]:
                                if '=' in p:
                                    k, v = p.split('=', 1)
                                    if k == 'rbps': effective_rbps = v
                                    elif k == 'wbps': effective_wbps = v
                                    elif k == 'riops': effective_riops = v
                                    elif k == 'wiops': effective_wiops = v
                except Exception:
                    pass

            req_rbps_dec, req_rbps_bin = parse_bw_to_bytes(limits.get('read_bw'))
            req_wbps_dec, req_wbps_bin = parse_bw_to_bytes(limits.get('write_bw'))
            req_riops = parse_iops(limits.get('diskread'))
            req_wiops = parse_iops(limits.get('diskwrite'))

            if req_rbps_dec > 0:
                if effective_rbps.isdigit():
                    if int(effective_rbps) not in (req_rbps_dec, req_rbps_bin):
                        io_synced = False
                else:
                    io_synced = False

            if req_wbps_dec > 0:
                if effective_wbps.isdigit():
                    if int(effective_wbps) not in (req_wbps_dec, req_wbps_bin):
                        io_synced = False
                else:
                    io_synced = False

            if req_riops > 0:
                if effective_riops.isdigit():
                    if int(effective_riops) != req_riops:
                        io_synced = False
                else:
                    io_synced = False

            if req_wiops > 0:
                if effective_wiops.isdigit():
                    if int(effective_wiops) != req_wiops:
                        io_synced = False
                else:
                    io_synced = False

            # Strict complete synchronization requires all parameters, I/O, and ancestor isolation to match
            is_synchronized = (
                cpu_synced and 
                mem_synced and 
                mem_high_synced and 
                swap_zero and 
                pids_synced and 
                io_synced and
                ancestor_protected
            )

            audit_results.append({
                'username': uname,
                'uid': uid,
                'plan_name': plan_name,
                'configured_cpuquota': limits['cpuquota'],
                'configured_mem_max': limits['mem_max'],
                'configured_memhigh': limits['memhigh'],
                'configured_maxtask': limits['maxtask'],
                'configured_read_bw': limits.get('read_bw', 0),
                'configured_write_bw': limits.get('write_bw', 0),
                'configured_diskread': limits.get('diskread', 0),
                'configured_diskwrite': limits.get('diskwrite', 0),
                'unit_file_exists': unit_exists,
                'active_cgroup_path': cgroup_path,
                'ancestor_protected': ancestor_protected,
                'effective_cpu_max': effective_cpu,
                'effective_cpu_pct': actual_cpu_pct,
                'effective_mem_max': effective_mem,
                'effective_mem_high': effective_mem_high,
                'effective_swap_max': effective_swap,
                'effective_pids_max': effective_pids,
                'effective_rbps': effective_rbps,
                'effective_wbps': effective_wbps,
                'effective_riops': effective_riops,
                'effective_wiops': effective_wiops,
                'is_synchronized': is_synchronized,
                'cpu_synced': cpu_synced,
                'mem_synced': mem_synced,
                'mem_high_synced': mem_high_synced,
                'swap_zero': swap_zero,
                'pids_synced': pids_synced,
                'io_synced': io_synced
            })
        total_accounts = len(audit_results)
        mismatch_count = sum(1 for a in audit_results if not a.get('is_synchronized', False))
        return {
            'success': True,
            'total_accounts': total_accounts,
            'mismatch_count': mismatch_count,
            'accounts': audit_results,
            'audit': audit_results
        }

    def action_admin_out_of_boundary(self) -> Dict[str, Any]:
        """Detect customer processes running outside their exact cgroup boundary."""
        users = self.collector.get_webuzo_users()
        uid_to_user = {udata['uid']: uname for uname, udata in users.items()}
        out_of_bounds = []

        for entry in os.listdir('/proc'):
            if entry.isdigit():
                pid = int(entry)
                try:
                    stat = os.stat(f'/proc/{pid}')
                    p_uid = stat.st_uid
                    if p_uid in uid_to_user:
                        cgroup_content = pathlib.Path(f'/proc/{pid}/cgroup').read_text().strip()
                        # Defect F Fix: Exact cgroup path match, not substring 'golden'
                        expected_slice = f"/golden.slice/golden-{p_uid}.slice"
                        is_contained = (cgroup_content == f"0::{expected_slice}" or 
                                        cgroup_content.startswith(f"0::{expected_slice}/"))
                        if not is_contained:
                            cmdline = pathlib.Path(f'/proc/{pid}/cmdline').read_text().replace('\x00', ' ').strip()
                            out_of_bounds.append({
                                'pid': pid,
                                'username': uid_to_user[p_uid],
                                'uid': p_uid,
                                'current_cgroup': cgroup_content,
                                'cmdline': redact_command_line(cmdline[:150])
                            })
                except Exception:
                    continue
        return {'count': len(out_of_bounds), 'out_of_bounds_processes': out_of_bounds}

    def _write_native_slice(self, uid: int, plan_name: str) -> bool:
        """Write native systemd slice file /etc/systemd/system/{uid}.slice from plan definition and reload systemd."""
        plan_file = f"/var/webuzo/cgroups/{plan_name}"
        if not os.path.exists(plan_file):
            return False
        try:
            with open(plan_file, 'r', encoding='utf-8') as pf:
                spec = json.load(pf)
            req_keys = ['cpuquota', 'read_bw', 'write_bw', 'diskread', 'diskwrite', 'mem_max', 'memhigh', 'maxtask']
            for k in req_keys:
                if not str(spec.get(k, '')).strip():
                    return False
            slice_content = (
                "[Unit]\nDescription=User Slice\n\n[Slice]\n"
                f"CPUQuota={spec['cpuquota']}%\n"
                f"IOReadBandwidthMax=/ {spec['read_bw']}\n"
                f"IOWriteBandwidthMax=/ {spec['write_bw']}\n"
                f"IOReadIOPSMax=/ {spec['diskread']}\n"
                f"IOWriteIOPSMax=/ {spec['diskwrite']}\n"
                f"MemoryMax={spec['mem_max']}\n"
                f"MemoryHigh={spec['memhigh']}\n"
                f"TasksMax={spec['maxtask']}\n\n"
                "[Install]\nWantedBy=multi-user.target\n"
            )
            slice_path = f"/etc/systemd/system/{uid}.slice"
            slice_dir = os.path.dirname(slice_path)
            if not os.path.exists(slice_dir):
                return True  # Non-systemd test environment
            tmp_slice = f"{slice_path}.tmp.{os.getpid()}_{uuid.uuid4().hex[:4]}"
            with open(tmp_slice, 'w', encoding='utf-8') as f:
                f.write(slice_content)
            os.replace(tmp_slice, slice_path)
            subprocess.run(['systemctl', 'daemon-reload'], check=False, timeout=15)
            subprocess.run(['systemctl', 'restart', f"{uid}.slice"], check=False, timeout=15)
            return True
        except Exception as e:
            print(f"[Write Native Slice Error] UID {uid} plan {plan_name}: {e}", file=sys.stderr)
            return False

    def action_set_temporary_override(self, admin_user: str, params: Dict[str, Any], is_reseller: bool = False) -> Dict[str, Any]:
        target_user = params.get('username')
        override_plan = params.get('override_plan') or params.get('plan')
        duration_minutes = int(params.get('duration_minutes') or params.get('duration') or 60)
        reason = params.get('reason', 'Admin temporary boost')

        if not target_user or not override_plan:
            return {'error': 'Username and override_plan are required', 'status_code': 400}

        target_user = str(target_user).strip()
        override_plan = str(override_plan).strip()

        if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9_.-]{0,63}$', target_user) or '..' in target_user or '/' in target_user or '\\' in target_user:
            return {'error': f"Security Refusal: Invalid target username format '{target_user}'", 'status_code': 400}

        if not re.match(r'^[a-zA-Z0-9_.-]{1,64}$', override_plan) or '..' in override_plan or '/' in override_plan or '\\' in override_plan:
            return {'error': f"Security Refusal: Invalid override plan format '{override_plan}'", 'status_code': 400}

        users = self.collector.get_webuzo_users()
        if target_user not in users:
            return {'error': 'User not found', 'status_code': 404}

        # B01: Reseller ownership enforcement
        if is_reseller and admin_user != 'root':
            target_data = users.get(target_user, {})
            if target_data.get('owner') != admin_user and target_user != admin_user:
                return {
                    'error': f"Forbidden: Reseller '{admin_user}' is not authorized to apply overrides to account '{target_user}'",
                    'status_code': 403
                }

        original_plan = users[target_user]['plan_name']
        now = int(time.time())
        expires_at = now + (duration_minutes * 60)

        # Validate target plan exists in Webuzo cgroups
        plan_file = f"/var/webuzo/cgroups/{override_plan}"
        if not os.path.exists(plan_file):
            return {'error': f"Target override plan '{override_plan}' does not exist in /var/webuzo/cgroups/", 'status_code': 422}

        # Transactional update: update Webuzo user info
        user_info_path = f"/var/webuzo/users/{target_user}/info"
        if os.path.exists(user_info_path):
            try:
                with open(user_info_path, 'r', encoding='utf-8') as f:
                    u_info = json.load(f)
                u_info['resource_limit'] = override_plan
                tmp_path = f"{user_info_path}.tmp.{os.getpid()}"
                with open(tmp_path, 'w', encoding='utf-8') as f:
                    json.dump(u_info, f, indent=4)
                os.replace(tmp_path, user_info_path)
            except Exception as e:
                return {'error': f"Failed to update Webuzo user info: {e}"}

        # Sync native slice definition so golden-shield mirror reads active boost plan
        uid = users[target_user]['uid']
        self._write_native_slice(uid, override_plan)

        # Apply slice limits immediately
        prep_res = subprocess.run(['python3', '/usr/local/sbin/golden-shield.py', 'prepare-account', str(uid)], capture_output=True, text=True, timeout=15)
        if prep_res.returncode != 0:
            # Revert info file and native slice
            try:
                with open(user_info_path, 'r', encoding='utf-8') as f:
                    u_info = json.load(f)
                u_info['resource_limit'] = original_plan
                with open(user_info_path, 'w', encoding='utf-8') as f:
                    json.dump(u_info, f, indent=4)
                self._write_native_slice(uid, original_plan)
                subprocess.run(['python3', '/usr/local/sbin/golden-shield.py', 'prepare-account', str(uid)], capture_output=True, timeout=15)
            except Exception:
                pass
            return {'error': f"Failed to apply slice limits for override: {prep_res.stderr or prep_res.stdout}"}

        conn = self.get_db()
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO temporary_overrides (username, uid, original_plan, override_plan, created_at, expires_at, status, reason)
                VALUES (?, ?, ?, ?, ?, ?, 'active', ?)
            """, (target_user, uid, original_plan, override_plan, now, expires_at, reason))
            new_id = cur.lastrowid

            conn.execute("""
                INSERT INTO audit_log (timestamp, actor, action, target_account, details_json)
                VALUES (?, ?, 'set_override', ?, ?)
            """, (now, admin_user, target_user, json.dumps({'override_id': new_id, 'from': original_plan, 'to': override_plan, 'expires_at': expires_at})))
            conn.commit()
        finally:
            conn.close()

        return {
            'success': True,
            'override_id': new_id,
            'active_plan': override_plan,
            'original_plan': original_plan,
            'expires_at': expires_at,
            'message': f'Temporary override applied: {target_user} boosted to {override_plan} for {duration_minutes} minutes'
        }

    def action_cancel_temporary_override(self, admin_user: str, params: Dict[str, Any], is_reseller: bool = False) -> Dict[str, Any]:
        override_id = int(params.get('id') or params.get('override_id') or 0)
        conn = self.get_db()
        try:
            cur = conn.cursor()
            if override_id > 0:
                cur.execute("SELECT * FROM temporary_overrides WHERE id = ? AND status = 'active'", (override_id,))
            elif 'username' in params:
                cur.execute("SELECT * FROM temporary_overrides WHERE username = ? AND status = 'active' ORDER BY id DESC LIMIT 1", (params['username'],))
            else:
                return {'error': 'Missing override id or username'}
            row = cur.fetchone()
            if not row:
                return {'error': 'Active override not found'}

            target_user = row['username']
            if is_reseller and admin_user != 'root':
                users = self.collector.get_webuzo_users()
                target_data = users.get(target_user, {})
                if target_data.get('owner') != admin_user and target_user != admin_user:
                    return {
                        'error': f"Forbidden: Reseller '{admin_user}' is not authorized to cancel overrides for account '{target_user}'",
                        'status_code': 403
                    }

            original_plan = row['original_plan']
            actual_id = row['id']

            # Restore Webuzo user info
            user_info_path = f"/var/webuzo/users/{target_user}/info"
            if os.path.exists(user_info_path):
                try:
                    with open(user_info_path, 'r', encoding='utf-8') as f:
                        u_info = json.load(f)
                    u_info['resource_limit'] = original_plan
                    tmp_path = f"{user_info_path}.tmp.{os.getpid()}"
                    with open(tmp_path, 'w', encoding='utf-8') as f:
                        json.dump(u_info, f, indent=4)
                    os.replace(tmp_path, user_info_path)
                except Exception as e:
                    return {'error': f"Failed to restore Webuzo user info: {e}"}

            users = self.collector.get_webuzo_users()
            if target_user in users:
                uid = users[target_user]['uid']
                self._write_native_slice(uid, original_plan)
                subprocess.run(['python3', '/usr/local/sbin/golden-shield.py', 'prepare-account', str(uid)], capture_output=True, timeout=15)

            cur.execute("UPDATE temporary_overrides SET status = 'cancelled' WHERE id = ?", (actual_id,))
            cur.execute("""
                INSERT INTO audit_log (timestamp, actor, action, target_account, details_json)
                VALUES (?, ?, 'cancel_override', ?, ?)
            """, (int(time.time()), admin_user, target_user, json.dumps({'override_id': actual_id, 'restored_to': original_plan})))
            conn.commit()
        finally:
            conn.close()

        return {
            'success': True,
            'override_id': actual_id,
            'username': target_user,
            'restored_plan': original_plan,
            'message': f'Override cancelled. Restored {target_user} to {original_plan}'
        }

    def action_sync_native_plans(self, admin_user: str) -> Dict[str, Any]:
        """
        Defect F Fix: True bulk synchronization.
        Iterates over all Webuzo hosting tenants, reapplies plan limits to slices, and triggers PHP isolation reload.
        """
        users = self.collector.get_webuzo_users()
        synced_accounts = []
        failed_accounts = []

        for uname, udata in users.items():
            uid = udata['uid']
            plan_name = udata['plan_name']
            try:
                r = subprocess.run(['python3', '/usr/local/sbin/golden-shield.py', 'prepare-account', str(uid)], capture_output=True, text=True, timeout=20)
                if r.returncode == 0:
                    synced_accounts.append({'username': uname, 'uid': uid, 'plan': plan_name})
                else:
                    failed_accounts.append({'username': uname, 'uid': uid, 'plan': plan_name, 'error': r.stderr or r.stdout})
            except Exception as e:
                failed_accounts.append({'username': uname, 'uid': uid, 'plan': plan_name, 'error': str(e)})

        subprocess.run(['systemctl', 'daemon-reload'], check=False)

        # Reconcile isolation on installed PHP versions
        for ver in self.get_installed_phps():
            try:
                subprocess.run(['python3', '/usr/local/sbin/webuzo-isolation.py', 'action', ver, 'reload'], capture_output=True, timeout=30)
            except Exception:
                pass

        conn = self.get_db()
        try:
            conn.execute("""
                INSERT INTO audit_log (timestamp, actor, action, target_account, details_json)
                VALUES (?, ?, 'sync_native_plans', 'all', ?)
            """, (int(time.time()), admin_user, json.dumps({'synced_count': len(synced_accounts), 'failed_count': len(failed_accounts)})))
            conn.commit()
        finally:
            conn.close()

        return {
            'success': (len(failed_accounts) == 0),
            'synced_count': len(synced_accounts),
            'failed_count': len(failed_accounts),
            'synced_accounts': synced_accounts,
            'failed_accounts': failed_accounts
        }

    def action_save_native_plan(self, admin_user: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Defect F Fix: Verified native plan update.
        Rejects on native API failure and updates mirrored slices immediately.
        """
        plan_name = params.get('plan', '').lower()
        if not plan_name:
            return {'error': 'Plan name is required'}

        api_args = ['/bin/webuzo', '--api', 'act=resource_limits', '--save=1', f'--plan={plan_name}', f'--edit={plan_name}']
        for k in ['cpuquota', 'mem_max', 'memhigh', 'maxtask', 'read_bw', 'write_bw', 'diskread', 'diskwrite']:
            if k in params:
                api_args.append(f'--{k}={params[k]}')

        res = subprocess.run(api_args, capture_output=True, text=True, timeout=60)
        out = {}
        try:
            out = json.loads(res.stdout) if res.stdout else {}
        except Exception:
            pass

        if res.returncode != 0 or out.get('error') or not out.get('done'):
            err_msg = out.get('error') or res.stderr or "Webuzo API rejected plan update"
            return {'error': f'Failed to save native plan: {err_msg}', 'webuzo_response': out}

        # Native save may have succeeded even when a mirror update fails. Report
        # that partial state explicitly; do not silently return full success.
        users = self.collector.get_webuzo_users()
        sync_errors = []
        for uname, udata in users.items():
            if udata['plan_name'] == plan_name:
                try:
                    mirrored = subprocess.run(['python3', '/usr/local/sbin/golden-shield.py', 'prepare-account', str(udata['uid'])], capture_output=True, text=True, timeout=20)
                    if mirrored.returncode:
                        sync_errors.append({'username': uname, 'error': mirrored.stderr or mirrored.stdout or 'Mirror command failed'})
                except Exception as exc:
                    sync_errors.append({'username': uname, 'error': str(exc)})
        conn = self.get_db()
        try:
            conn.execute("""
                INSERT INTO audit_log (timestamp, actor, action, target_account, details_json)
                VALUES (?, ?, 'save_plan', ?, ?)
            """, (int(time.time()), admin_user, plan_name, json.dumps({**params, "synchronization_errors": sync_errors})))
            conn.commit()
        finally:
            conn.close()

        if sync_errors:
            return {'success': False, 'native_saved': True, 'error': 'Native plan was saved, but account enforcement synchronization failed. Review affected accounts before retrying.', 'sync_errors': sync_errors}

        return {'success': True, 'webuzo_response': out, 'message': f'Plan {plan_name} updated successfully.'}

    def action_set_maintenance_mode(self, admin_user: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Defect F Fix: Wires set_maintenance_mode into IPC dispatcher and persists state to SQLite.
        Pauses automated telemetry collection while ensuring override expiration checks continue.
        """
        val = params.get('enabled', False)
        if isinstance(val, str):
            enable = val.strip().lower() in ('1', 'true', 'yes', 'on')
        elif isinstance(val, (int, float)):
            enable = (val != 0)
        else:
            enable = bool(val)

        self.maintenance_mode = enable

        conn = self.get_db()
        try:
            conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('maintenance_mode', ?)", ('1' if enable else '0',))
            conn.execute("""
                INSERT INTO audit_log (timestamp, actor, action, target_account, details_json)
                VALUES (?, ?, 'set_maintenance_mode', 'system', ?)
            """, (int(time.time()), admin_user, json.dumps({'maintenance_mode': enable})))
            conn.commit()
        finally:
            conn.close()

        return {'success': True, 'maintenance_mode': enable}

    def action_get_agent_health(self) -> Dict[str, Any]:
        """Collect daemon health, memory footprint, and telemetry storage footprint."""
        daemon_pid = os.getpid()
        rss_bytes = 0
        try:
            with open(f'/proc/{daemon_pid}/status') as f:
                for line in f:
                    if line.startswith('VmRSS:'):
                        rss_bytes = int(line.split()[1]) * 1024
        except Exception:
            pass

        db_size_bytes = 0
        wal_size_bytes = 0
        shm_size_bytes = 0
        if os.path.exists(self.db_path):
            db_size_bytes = os.path.getsize(self.db_path)
        wal_path = f"{self.db_path}-wal"
        if os.path.exists(wal_path):
            wal_size_bytes = os.path.getsize(wal_path)
        shm_path = f"{self.db_path}-shm"
        if os.path.exists(shm_path):
            shm_size_bytes = os.path.getsize(shm_path)

        tot_storage_bytes = db_size_bytes + wal_size_bytes + shm_size_bytes

        try:
            cap = pathlib.Path('/sys/fs/cgroup/system.slice/uniselv-resman-agent.service/memory.max').read_text().strip()
            cap_display = format_bytes(int(cap)) if cap.isdigit() else ('Unlimited' if cap == 'max' else 'Unavailable')
            cap_bytes = int(cap) if cap.isdigit() else None
        except (OSError, ValueError):
            cap_display, cap_bytes = 'Unavailable', None
        return {
            'memory_cap_formatted': cap_display,
            'agent_pid': daemon_pid,
            'agent_status': 'active_running',
            'agent_rss_bytes': rss_bytes,
            'agent_rss_formatted': f"{round(rss_bytes / 1024 / 1024, 2)} MiB",
            'memory_cap_bytes': cap_bytes,
            'memory_health': ('UNAVAILABLE' if cap_bytes is None else ('WARNING' if rss_bytes >= cap_bytes * 0.8 else 'HEALTHY')),
            'db_size_bytes': db_size_bytes,
            'wal_size_bytes': wal_size_bytes,
            'shm_size_bytes': shm_size_bytes,
            'total_storage_bytes': tot_storage_bytes,
            'storage_formatted': f"{round(tot_storage_bytes / 1024, 1)} KiB",
            'maintenance_mode': self.maintenance_mode
        }

    def action_get_feature_settings(self) -> Dict[str, Any]:
        """Fetch all configurable feature settings, thresholds, and self-service toggles."""
        self.collector.reload_settings()
        return {'success': True, 'settings': self.collector.settings}

    def action_save_feature_settings(self, admin_user: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Atomically persist feature settings, audit changes, and update active daemon loop state."""
        allowed_int_keys = {
            'telemetry_interval': (3, 60),
            'snapshot_cooldown_sec': (5, 600),
            'alert_threshold_cpu': (10, 100),
            'alert_threshold_mem': (10, 100),
            'alert_threshold_tasks': (10, 100),
            'retention_samples_days': (1, 365),
            'retention_snapshots_days': (1, 180),
            'retention_events_days': (1, 365),
            'retention_audit_days': (7, 730),
            'retention_max_storage_mib': (10, 2048),
            'runaway_cpu_percent': (20, 100),
            'runaway_max_duration_sec': (5, 600),
        }
        allowed_float_keys = {
            'circuit_breaker_load_threshold': (0.5, 50.0),
            'circuit_breaker_recovery_threshold': (0.1, 40.0),
        }
        allowed_bool_keys = [
            'telemetry_enabled', 'snapshot_on_throttle', 'snapshot_on_oom',
            'snapshot_on_task_limit', 'enduser_allow_kill', 'enduser_allow_export',
            'enduser_allow_db_trace', 'auto_prune_hourly',
            'enable_runaway_watchdog', 'enable_circuit_breaker',
            'runaway_watchdog_kill_enabled', 'watchdog_require_account_saturation'
        ]

        validated = {}
        for k, (min_v, max_v) in allowed_int_keys.items():
            if k in params:
                try:
                    val = int(params[k])
                    validated[k] = str(max(min_v, min(max_v, val)))
                except (ValueError, TypeError):
                    pass

        for k, (min_v, max_v) in allowed_float_keys.items():
            if k in params:
                try:
                    val = float(params[k])
                    validated[k] = str(round(max(min_v, min(max_v, val)), 2))
                except (ValueError, TypeError):
                    pass

        for k in allowed_bool_keys:
            if k in params:
                v = params[k]
                is_true = v is True or v == '1' or v == 1 or str(v).lower() == 'true'
                validated[k] = '1' if is_true else '0'

        if 'watchdog_action' in params:
            act = str(params['watchdog_action']).strip().lower()
            if act in ('notify', 'terminate'):
                validated['watchdog_action'] = act

        if 'watchdog_excluded_commands' in params:
            ex = str(params['watchdog_excluded_commands']).strip()
            # Sanitize: allow alphanumeric, comma, hyphen, underscore, dot, slash
            clean_ex = re.sub(r'[^a-zA-Z0-9,\-_./]', '', ex)
            validated['watchdog_excluded_commands'] = clean_ex

        if not validated:
            return {'error': 'No valid configuration parameters provided'}

        conn = self.get_db()
        try:
            for k, v in validated.items():
                conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (k, v))
            conn.execute("""
                INSERT INTO audit_log (timestamp, actor, action, target_account, details_json)
                VALUES (?, ?, 'save_feature_settings', 'system', ?)
            """, (int(time.time()), admin_user, json.dumps(validated)))
            conn.commit()
        finally:
            conn.close()

        # Update collector's internal settings cache immediately
        self.collector.reload_settings()

        return {'success': True, 'message': 'Configuration settings saved and applied successfully.', 'settings': self.collector.settings}

    def action_get_overload_protection_status(self) -> Dict[str, Any]:
        """Return live status of the runaway watchdog, tracked suspicious processes, and circuit breaker."""
        try:
            load1, load5, load15 = os.getloadavg()
        except Exception:
            load1, load5, load15 = (0.0, 0.0, 0.0)

        now = time.time()
        tracked = []
        for k, v in list(self.collector.runaway_proc_tracker.items()):
            tracked.append({
                'uid': v.get('uid'),
                'pid': v.get('pid'),
                'uname': v.get('uname'),
                'comm': v.get('comm'),
                'cmdline': v.get('cmdline'),
                'peak_cpu': v.get('peak_cpu'),
                'running_sec': round(now - v.get('first_seen', now), 1)
            })

        return {
            'success': True,
            'system_load': {
                'load1': round(load1, 2),
                'load5': round(load5, 2),
                'load15': round(load15, 2),
                'host_cpus': self.collector.host_cpu_count
            },
            'circuit_breaker': {
                'enabled': self.collector.settings.get('enable_circuit_breaker', True),
                'active': self.collector.circuit_breaker_active,
                'load_threshold': self.collector.settings.get('circuit_breaker_load_threshold', 3.2),
                'recovery_threshold': self.collector.settings.get('circuit_breaker_recovery_threshold', 2.2),
                'throttled_users': self.collector.circuit_breaker_throttled_users
            },
            'runaway_watchdog': {
                'enabled': self.collector.settings.get('enable_runaway_watchdog', True),
                'cpu_threshold': self.collector.settings.get('runaway_cpu_percent', 80),
                'max_duration_sec': self.collector.settings.get('runaway_max_duration_sec', 60),
                'tracked_processes_count': len(tracked),
                'tracked_processes': tracked
            }
        }

    def action_get_storage_settings(self) -> Dict[str, Any]:
        settings = self.collector.get_retention_settings()
        health = self.action_get_agent_health()
        conn = self.get_db()
        try:
            counts = {table: conn.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]
                      for table in ('samples', 'snapshots', 'events', 'audit_log')}
        finally:
            conn.close()
        return {'settings': settings, 'storage': {
            'total_formatted': format_bytes(health['total_storage_bytes']),
            'used_percent': round(health['total_storage_bytes'] / (settings['max_storage_mib'] * 1024 * 1024) * 100, 2),
            'samples_count': counts['samples'], 'snapshots_count': counts['snapshots'],
            'events_count': counts['events'], 'audit_count': counts['audit_log'],
            'size_limit_kind': 'warning_threshold_not_hard_quota'}}

    def action_save_storage_settings(self, admin_user: str, params: Dict[str, Any]) -> Dict[str, Any]:
        bounds = {'samples_days': (1, 90), 'snapshots_days': (1, 90),
                  'events_days': (1, 180), 'audit_days': (7, 365), 'max_storage_mib': (10, 102400)}
        validated = {}
        for key, (low, high) in bounds.items():
            if key in params:
                try:
                    value = int(str(params[key]))
                except (ValueError, TypeError):
                    return {'error': f'{key} must be an integer between {low} and {high}'}
                if not low <= value <= high:
                    return {'error': f'{key} must be between {low} and {high}'}
                validated[key] = value
        params = validated
        conn = self.get_db()
        try:
            for k in ['samples_days', 'snapshots_days', 'events_days', 'audit_days', 'max_storage_mib']:
                if k in params:
                    val = str(int(params[k]))
                    conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (f"retention_{k}", val))
            conn.execute("""
                INSERT INTO audit_log (timestamp, actor, action, target_account, details_json)
                VALUES (?, ?, 'save_storage_settings', 'system', ?)
            """, (int(time.time()), admin_user, json.dumps(params)))
            conn.commit()
        finally:
            conn.close()
        return {'success': True, 'settings': self.collector.get_retention_settings()}

    def action_prune_database_now(self, admin_user: str, params: Dict[str, Any]) -> Dict[str, Any]:
        vacuum = bool(params.get('vacuum', True))
        res = self.collector.prune_retention(vacuum=vacuum)
        conn = self.get_db()
        try:
            conn.execute("""
                INSERT INTO audit_log (timestamp, actor, action, target_account, details_json)
                VALUES (?, ?, 'prune_database_now', 'system', ?)
            """, (int(time.time()), admin_user, json.dumps(res)))
            conn.commit()
        finally:
            conn.close()
        return {'success': True, 'prune_results': res, 'prune_details': res}

    def action_clear_audit_logs(self, admin_user: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Admin capability to clear audit log history with durable logging."""
        conn = self.get_db()
        try:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) as cnt FROM audit_log")
            row = cur.fetchone()
            total = row['cnt'] if row else 0
            cur.execute("DELETE FROM audit_log")
            # Reinsert clear event so audit trail notes the reset
            cur.execute("""
                INSERT INTO audit_log (timestamp, actor, action, target_account, details_json)
                VALUES (?, ?, 'clear_audit_logs', 'system', ?)
            """, (int(time.time()), admin_user, json.dumps({'cleared_records': total})))
            conn.commit()
            return {'success': True, 'cleared_count': total, 'message': f'Audit log cleared ({total} records removed).'}
        finally:
            conn.close()

    def action_purge_snapshots(self, admin_user: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Admin capability to immediately purge all or stale forensic snapshots."""
        older_than_days = int(params.get('older_than_days', 0))
        target_user = params.get('username')
        conn = self.get_db()
        try:
            cur = conn.cursor()
            query = "DELETE FROM snapshots WHERE 1=1"
            q_params = []
            if older_than_days > 0:
                cutoff = int(time.time()) - (older_than_days * 86400)
                query += " AND timestamp < ?"
                q_params.append(cutoff)
            if target_user:
                query += " AND username = ?"
                q_params.append(target_user)
            cur.execute(query, q_params)
            deleted = cur.rowcount
            conn.commit()
            try:
                cur.execute("PRAGMA wal_checkpoint(PASSIVE)")
                cur.fetchall()
            except Exception:
                pass
            finally:
                cur.close()

            cur2 = conn.cursor()
            cur2.execute("""
                INSERT INTO audit_log (timestamp, actor, action, target_account, details_json)
                VALUES (?, ?, 'purge_snapshots', ?, ?)
            """, (int(time.time()), admin_user, target_user or 'all', json.dumps({'deleted_snapshots': deleted, 'older_than_days': older_than_days})))
            conn.commit()
            cur2.close()

            return {
                'success': True,
                'deleted_snapshots': deleted,
                'message': f'Purged {deleted} forensic snapshots successfully.'
            }
        finally:
            conn.close()

    def action_run_adapter_sync(self, admin_user: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Defect 1, B05, B07: Verified native Webuzo plan synchronization with package mapping and billing idempotency.
        Updates /var/webuzo/users/<uname>/info and /etc/systemd/system/<uid>.slice with transactional backup & rollback,
        regenerates kernel slices, reloads PHP isolation, and logs transaction. Fails closed on unknown plans.
        """
        adapter_type = str(params.get('adapter', 'whmcs')).lower()
        payload = dict(params.get('payload', {})) if isinstance(params.get('payload'), dict) else {}
        for k in ('username', 'plan', 'billing_package', 'package', 'event_id', 'idempotency_key'):
            if k in params and k not in payload:
                payload[k] = params[k]

        target_user = payload.get('username')
        billing_plan = payload.get('plan') or payload.get('billing_package') or payload.get('package')

        if not target_user or not billing_plan:
            return {'error': 'Adapter payload must include target username and plan'}

        target_user_str = str(target_user).strip()
        billing_plan_str = str(billing_plan).strip()

        if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9_.-]{0,63}$', target_user_str) or '..' in target_user_str or '/' in target_user_str or '\\' in target_user_str:
            return {'error': f"Security Refusal: Invalid target username format '{target_user_str}'", 'status_code': 400}

        if not re.match(r'^[a-zA-Z0-9 _.-]{1,64}$', billing_plan_str) or '..' in billing_plan_str or '/' in billing_plan_str or '\\' in billing_plan_str:
            return {'error': f"Security Refusal: Invalid plan name format '{billing_plan_str}'", 'status_code': 400}

        target_user = target_user_str
        billing_plan = billing_plan_str

        # 1. Distinguish between explicit provider-scoped event ID vs non-event reconciliation request
        event_id = payload.get('idempotency_key') or payload.get('event_id')
        is_explicit_event = bool(event_id)

        if is_explicit_event:
            idempotency_key = f"{adapter_type}_{event_id}"
        else:
            # Direct non-event reconciliation: assign unique execution key so legitimate future transitions (A->B->A) are never suppressed
            idempotency_key = f"reconcile_{target_user}_{int(time.time())}_{uuid.uuid4().hex[:8]}"

        # 2. Account-scoped serialization: bounded lock acquisition with retry to serialize rapid transactions
        lock_dir = "/run/uniselv-resman"
        lock_fd = None
        lock_path = os.path.join(lock_dir, f"account_{target_user}.lock")
        acquire_timeout = 5.0
        start_lock = time.time()
        lock_acquired = False
        last_lock_err = None

        os.makedirs(lock_dir, exist_ok=True)
        while time.time() - start_lock < acquire_timeout:
            try:
                lock_fd = open(lock_path, 'w')
                if fcntl:
                    fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                lock_acquired = True
                break
            except Exception as lock_err:
                last_lock_err = lock_err
                if lock_fd:
                    try: lock_fd.close()
                    except Exception: pass
                    lock_fd = None
                time.sleep(0.1)

        if not lock_acquired:
            return {
                'error': f"Account '{target_user}' mutation rejected: account is currently locked by a concurrent transaction ({str(last_lock_err)})",
                'status_code': 423,
                'locked': True
            }

        try:
            # 3. Check for existing event within the serialized lock scope
            if is_explicit_event:
                conn = self.get_db()
                try:
                    cur = conn.cursor()
                    cur.execute("SELECT target_account, payload_json, response_json FROM webhook_log WHERE idempotency_key = ?", (idempotency_key,))
                    existing = cur.fetchone()
                    if existing:
                        stored_payload = json.loads(existing['payload_json']) if existing['payload_json'] else {}
                        stored_resp = json.loads(existing['response_json']) if existing['response_json'] else {}
                        stored_user = existing['target_account']
                        stored_plan = stored_payload.get('plan') or stored_payload.get('billing_package') or stored_payload.get('package') or stored_resp.get('active_plan')
                        if stored_user != target_user or (stored_plan and str(stored_plan).lower() != str(billing_plan).lower()):
                            return {
                                'error': f"Conflicting idempotency key reuse: Key '{event_id}' was previously recorded for account '{stored_user}' with plan '{stored_plan}'",
                                'status_code': 409,
                                'conflict': True
                            }
                        if existing['response_json']:
                            resp = json.loads(existing['response_json'])
                            resp['idempotent_replay'] = True
                            resp['replayed'] = True
                            return resp
                finally:
                    conn.close()

            # 4. Check package mapping
            conn = self.get_db()
            try:
                cur = conn.cursor()
                cur.execute("SELECT resource_plan FROM package_mappings WHERE LOWER(billing_package) = LOWER(?)", (billing_plan,))
                map_row = cur.fetchone()
                target_plan = map_row['resource_plan'] if map_row else billing_plan
            finally:
                conn.close()

            # 5. Validate target user exists
            users = self.collector.get_webuzo_users()
            if target_user not in users:
                return {'error': f"User '{target_user}' does not exist on this Webuzo server", 'status_code': 404}

            uid = users[target_user]['uid']
            old_plan = users[target_user]['plan_name']

            # 6. Validate target plan exists in Webuzo cgroups (Fail-closed: refuse silent fallback to default)
            plan_file = f"/var/webuzo/cgroups/{target_plan}"
            if not os.path.exists(plan_file):
                return {
                    'error': f"Target resource plan '{target_plan}' does not exist in /var/webuzo/cgroups/. Billing sync rejected (fail-closed; refusing silent degradation to default).",
                    'requested_plan': target_plan,
                    'billing_package': billing_plan,
                    'adapter': adapter_type,
                    'status_code': 422
                }

            # Load and validate all 8 native plan parameters
            try:
                with open(plan_file, 'r', encoding='utf-8') as pf:
                    plan_spec = json.load(pf)
                req_keys = ['cpuquota', 'read_bw', 'write_bw', 'diskread', 'diskwrite', 'mem_max', 'memhigh', 'maxtask']
                for k in req_keys:
                    if not str(plan_spec.get(k, '')).strip():
                        raise ValueError(f"Plan '{target_plan}' has empty or missing directive '{k}'")
            except Exception as pe:
                return {'error': f"Invalid target plan definition '{target_plan}': {str(pe)}", 'status_code': 422}

            user_info_path = f"/var/webuzo/users/{target_user}/info"
            slice_path = f"/etc/systemd/system/{uid}.slice"
            golden_slice_path = f"/etc/systemd/system/golden-{uid}.slice"

            slice_existed_originally = os.path.exists(slice_path)
            golden_slice_existed_originally = os.path.exists(golden_slice_path)
            user_info_existed_originally = os.path.exists(user_info_path)

            ts_nonce = f"{os.getpid()}_{int(time.time())}_{uuid.uuid4().hex[:4]}"
            backup_info_path = f"{user_info_path}.bak.{ts_nonce}"
            backup_slice_path = f"{slice_path}.bak.{ts_nonce}"
            backup_golden_slice_path = f"{golden_slice_path}.bak.{ts_nonce}"

            target_slice_content = (
                "[Unit]\nDescription=User Slice\n\n[Slice]\n"
                f"CPUQuota={plan_spec['cpuquota']}%\n"
                f"IOReadBandwidthMax=/ {plan_spec['read_bw']}\n"
                f"IOWriteBandwidthMax=/ {plan_spec['write_bw']}\n"
                f"IOReadIOPSMax=/ {plan_spec['diskread']}\n"
                f"IOWriteIOPSMax=/ {plan_spec['diskwrite']}\n"
                f"MemoryMax={plan_spec['mem_max']}\n"
                f"MemoryHigh={plan_spec['memhigh']}\n"
                f"TasksMax={plan_spec['maxtask']}\n\n"
                "[Install]\nWantedBy=multi-user.target\n"
            )

            try:
                # 7. Transactional backups
                if user_info_existed_originally:
                    shutil.copy2(user_info_path, backup_info_path)
                if slice_existed_originally:
                    shutil.copy2(slice_path, backup_slice_path)
                if golden_slice_existed_originally:
                    shutil.copy2(golden_slice_path, backup_golden_slice_path)

                # Step A: Update Webuzo user info
                with open(user_info_path, 'r', encoding='utf-8') as f:
                    u_info = json.load(f)
                u_info['resource_limit'] = target_plan
                tmp_info = f"{user_info_path}.tmp.{ts_nonce}"
                with open(tmp_info, 'w', encoding='utf-8') as f:
                    json.dump(u_info, f, indent=4)
                os.replace(tmp_info, user_info_path)

                # Step B: Write native systemd slice
                tmp_slice = f"{slice_path}.tmp.{ts_nonce}"
                with open(tmp_slice, 'w', encoding='utf-8') as f:
                    f.write(target_slice_content)
                os.replace(tmp_slice, slice_path)

                # Step C: Daemon reload and restart native slice with exit-code verification
                d_res = subprocess.run(['systemctl', 'daemon-reload'], capture_output=True, text=True, timeout=30)
                if d_res.returncode != 0:
                    raise RuntimeError(f"systemctl daemon-reload failed (exit {d_res.returncode}): {d_res.stderr or d_res.stdout}")

                s_res = subprocess.run(['systemctl', 'restart', f"{uid}.slice"], capture_output=True, text=True, timeout=30)
                if s_res.returncode != 0:
                    raise RuntimeError(f"systemctl restart {uid}.slice failed (exit {s_res.returncode}): {s_res.stderr or s_res.stdout}")

                # Step D: Golden Shield prepare-account to mirror native slice into hosting pool
                prep_res = subprocess.run(['python3', '/usr/local/sbin/golden-shield.py', 'prepare-account', str(uid)], capture_output=True, text=True, timeout=30)
                if prep_res.returncode != 0:
                    raise RuntimeError(f"Golden Shield prepare-account failed (exit {prep_res.returncode}): {prep_res.stderr or prep_res.stdout}")

                # Step E: Complete desired-versus-effective kernel cgroup numerical limit verification
                cg_dir = f"/sys/fs/cgroup/golden.slice/golden-{uid}.slice"
                native_cg_dir = f"/sys/fs/cgroup/{uid}.slice"

                # 1. Cgroup hierarchy existence is mandatory: fail-closed if absent
                if not os.path.exists('/sys/fs/cgroup/golden.slice'):
                    raise RuntimeError("Verification Failure: /sys/fs/cgroup/golden.slice is absent")
                if not os.path.exists(cg_dir):
                    raise RuntimeError(f"Verification Failure: Golden cgroup directory '{cg_dir}' was not created by prepare-account")

                # Parse exact byte and quota values using collector helper and plan_spec
                plan_limits = dict(self.collector.get_plan_limits(target_plan))
                for k in ['cpuquota', 'mem_max', 'memhigh', 'maxtask', 'read_bw', 'write_bw', 'diskread', 'diskwrite']:
                    if k not in plan_limits or not plan_limits[k]:
                        if k in plan_spec and plan_spec[k]:
                            plan_limits[k] = plan_spec[k]

                # 2. cpu.max verification: MUST match numerical plan quota
                cpu_max_file = os.path.join(cg_dir, 'cpu.max')
                if not os.path.exists(cpu_max_file):
                    raise RuntimeError(f"Verification Failure: {cpu_max_file} is absent")
                with open(cpu_max_file, 'r') as f:
                    cur_cpu = f.read().strip()
                if " " not in cur_cpu:
                    raise RuntimeError(f"Verification Failure: Kernel cpu.max has invalid format '{cur_cpu}'")
                q_str, p_str = cur_cpu.split()
                if q_str == 'max' or not q_str.isdigit() or not p_str.isdigit() or int(p_str) <= 0:
                    raise RuntimeError(f"Verification Failure: Kernel cpu.max is unlimited or malformed: '{cur_cpu}'")
                actual_cpu_pct = round((int(q_str) / int(p_str)) * 100, 1)
                if abs(actual_cpu_pct - float(plan_limits['cpuquota'])) > 0.1:
                    raise RuntimeError(f"Verification Failure: Kernel cpu.max quota mismatch: expected {plan_limits['cpuquota']}%, got {actual_cpu_pct}%")

                # 3. memory.max verification: MUST match numerical plan limit
                mem_max_file = os.path.join(cg_dir, 'memory.max')
                if not os.path.exists(mem_max_file):
                    raise RuntimeError(f"Verification Failure: {mem_max_file} is absent")
                with open(mem_max_file, 'r') as f:
                    cur_mem_max = f.read().strip()
                if cur_mem_max == 'max' or not cur_mem_max.isdigit() or int(cur_mem_max) != int(plan_limits['mem_max']):
                    raise RuntimeError(f"Verification Failure: Kernel memory.max mismatch: expected {plan_limits['mem_max']}, got '{cur_mem_max}'")

                # 4. memory.high verification: MUST match numerical plan limit
                mem_high_file = os.path.join(cg_dir, 'memory.high')
                if not os.path.exists(mem_high_file):
                    raise RuntimeError(f"Verification Failure: {mem_high_file} is absent")
                with open(mem_high_file, 'r') as f:
                    cur_mem_high = f.read().strip()
                if cur_mem_high == 'max' or not cur_mem_high.isdigit() or int(cur_mem_high) != int(plan_limits['memhigh']):
                    raise RuntimeError(f"Verification Failure: Kernel memory.high mismatch: expected {plan_limits['memhigh']}, got '{cur_mem_high}'")

                # 5. memory.swap.max verification: MUST be '0'
                swap_max_file = os.path.join(cg_dir, 'memory.swap.max')
                if not os.path.exists(swap_max_file):
                    raise RuntimeError(f"Verification Failure: {swap_max_file} is absent")
                with open(swap_max_file, 'r') as f:
                    cur_swap = f.read().strip()
                if cur_swap != '0':
                    raise RuntimeError(f"Verification Failure: Kernel memory.swap.max must be 0, got '{cur_swap}'")

                # 6. pids.max verification: MUST match numerical plan limit
                pids_max_file = os.path.join(cg_dir, 'pids.max')
                if not os.path.exists(pids_max_file):
                    raise RuntimeError(f"Verification Failure: {pids_max_file} is absent")
                with open(pids_max_file, 'r') as f:
                    cur_pids = f.read().strip()
                if cur_pids == 'max' or not cur_pids.isdigit() or int(cur_pids) != int(plan_limits['maxtask']):
                    raise RuntimeError(f"Verification Failure: Kernel pids.max mismatch: expected {plan_limits['maxtask']}, got '{cur_pids}'")

                # 7. io.max verification: MUST exist and enforce plan limits
                io_max_file = os.path.join(cg_dir, 'io.max')
                if not os.path.exists(io_max_file):
                    raise RuntimeError(f"Verification Failure: {io_max_file} is absent")
                with open(io_max_file, 'r') as f:
                    cur_io = f.read().strip()

                valid_io, io_err = verify_io_rules(cur_io, plan_limits, username=target_user)
                if not valid_io:
                    raise RuntimeError(f"Verification Failure: Golden io.max does not enforce plan limits: {io_err}")

                native_io_file = os.path.join(native_cg_dir, 'io.max')
                if os.path.exists(native_cg_dir):
                    if not os.path.exists(native_io_file):
                        raise RuntimeError(f"Verification Failure: {native_io_file} is absent")
                    with open(native_io_file, 'r') as nf:
                        native_io = nf.read().strip()
                    valid_native_io, native_io_err = verify_io_rules(native_io, plan_limits, username=target_user)
                    if not valid_native_io:
                        raise RuntimeError(f"Verification Failure: Native slice io.max does not enforce plan limits: {native_io_err}")
                    if parse_cgroup_io_max(cur_io) != parse_cgroup_io_max(native_io):
                        raise RuntimeError(f"Verification Failure: Kernel io.max mismatch between golden and native slice: '{cur_io}' != '{native_io}'")
                elif os.path.exists(native_io_file):
                    with open(native_io_file, 'r') as nf:
                        native_io = nf.read().strip()
                    valid_native_io, native_io_err = verify_io_rules(native_io, plan_limits, username=target_user)
                    if not valid_native_io:
                        raise RuntimeError(f"Verification Failure: Native io.max does not enforce plan limits: {native_io_err}")
                    if parse_cgroup_io_max(cur_io) != parse_cgroup_io_max(native_io):
                        raise RuntimeError(f"Verification Failure: Kernel io.max mismatch between golden and native slice: '{cur_io}' != '{native_io}'")

                # Step F: Trigger PHP isolation reload across all installed PHP versions and verify return codes
                php_versions = self.get_installed_phps()
                reloaded_phps = []
                for ver in php_versions:
                    p_res = subprocess.run(['python3', '/usr/local/sbin/webuzo-isolation.py', 'action', ver, 'reload'], capture_output=True, text=True, timeout=90)
                    if p_res.returncode != 0:
                        raise RuntimeError(f"PHP isolation reload failed for PHP {ver} (exit {p_res.returncode}): {p_res.stderr or p_res.stdout}")
                    reloaded_phps.append(ver)

            except Exception as txn_err:
                # TRANSACTION FAILURE: PERFORM VERIFIED RECOVERY / ROLLBACK WITH RETURNCODE CHECKING
                rollback_errs = []
                try:
                    if user_info_existed_originally and os.path.exists(backup_info_path):
                        shutil.copy2(backup_info_path, user_info_path)
                    elif not user_info_existed_originally and os.path.exists(user_info_path):
                        try: os.remove(user_info_path)
                        except Exception as e: rollback_errs.append(f"Failed to remove created info file: {e}")

                    if slice_existed_originally and os.path.exists(backup_slice_path):
                        shutil.copy2(backup_slice_path, slice_path)
                    elif not slice_existed_originally and os.path.exists(slice_path):
                        try: os.remove(slice_path)
                        except Exception as e: rollback_errs.append(f"Failed to remove created slice file: {e}")

                    # Checked execution of recovery commands
                    rb_d = subprocess.run(['systemctl', 'daemon-reload'], capture_output=True, text=True, timeout=30)
                    if rb_d.returncode != 0:
                        rollback_errs.append(f"daemon-reload failed on rollback (exit {rb_d.returncode}): {rb_d.stderr or rb_d.stdout}")

                    rb_s = subprocess.run(['systemctl', 'restart', f"{uid}.slice"], capture_output=True, text=True, timeout=30)
                    if rb_s.returncode != 0:
                        rollback_errs.append(f"restart {uid}.slice failed on rollback (exit {rb_s.returncode}): {rb_s.stderr or rb_s.stdout}")

                    rb_p = subprocess.run(['python3', '/usr/local/sbin/golden-shield.py', 'prepare-account', str(uid)], capture_output=True, text=True, timeout=30)
                    if rb_p.returncode != 0:
                        rollback_errs.append(f"golden-shield prepare-account failed on rollback (exit {rb_p.returncode}): {rb_p.stderr or rb_p.stdout}")

                    for ver in self.get_installed_phps():
                        rb_php = subprocess.run(['python3', '/usr/local/sbin/webuzo-isolation.py', 'action', ver, 'reload'], capture_output=True, text=True, timeout=90)
                        if rb_php.returncode != 0:
                            rollback_errs.append(f"PHP {ver} isolation reload failed on rollback (exit {rb_php.returncode}): {rb_php.stderr or rb_php.stdout}")

                    # VERIFY RESTORED EFFECTIVE STATE MATCHES ORIGINAL PLAN LIMITS
                    old_plan_limits = dict(self.collector.get_plan_limits(old_plan))
                    old_plan_file = f"/var/webuzo/cgroups/{old_plan}"
                    if os.path.exists(old_plan_file):
                        try:
                            with open(old_plan_file, 'r', encoding='utf-8') as opf:
                                old_plan_spec = json.load(opf)
                            for k in ['cpuquota', 'mem_max', 'memhigh', 'maxtask', 'read_bw', 'write_bw', 'diskread', 'diskwrite']:
                                if k not in old_plan_limits or not old_plan_limits[k]:
                                    if k in old_plan_spec and old_plan_spec[k]:
                                        old_plan_limits[k] = old_plan_spec[k]
                        except Exception:
                            pass
                    restored_cg_dir = f"/sys/fs/cgroup/golden.slice/golden-{uid}.slice"
                    if not os.path.exists(restored_cg_dir):
                        rollback_errs.append(f"Restored golden cgroup directory '{restored_cg_dir}' does not exist")
                    else:
                        # 1. cpu.max
                        restored_cpu_file = os.path.join(restored_cg_dir, 'cpu.max')
                        if not os.path.exists(restored_cpu_file):
                            rollback_errs.append("Restored cpu.max is absent")
                        else:
                            with open(restored_cpu_file, 'r') as rf:
                                r_cpu = rf.read().strip()
                            if ' ' not in r_cpu:
                                rollback_errs.append(f"Restored cpu.max has invalid format: '{r_cpu}'")
                            else:
                                rq, rp = r_cpu.split()
                                if rq != 'max' and rq.isdigit() and rp.isdigit() and int(rp) > 0:
                                    r_pct = round((int(rq) / int(rp)) * 100, 1)
                                    if abs(r_pct - float(old_plan_limits['cpuquota'])) > 0.1:
                                        rollback_errs.append(f"Restored CPU quota {r_pct}% does not match original plan quota {old_plan_limits['cpuquota']}%")
                                else:
                                    rollback_errs.append(f"Restored CPU quota is invalid or unlimited: '{r_cpu}'")

                        # 2. memory.max
                        restored_mem_file = os.path.join(restored_cg_dir, 'memory.max')
                        if not os.path.exists(restored_mem_file):
                            rollback_errs.append("Restored memory.max is absent")
                        else:
                            with open(restored_mem_file, 'r') as rmf:
                                r_mem = rmf.read().strip()
                            if not r_mem.isdigit() or int(r_mem) != int(old_plan_limits['mem_max']):
                                rollback_errs.append(f"Restored memory.max '{r_mem}' does not match original plan {old_plan_limits['mem_max']}")

                        # 3. memory.high
                        restored_high_file = os.path.join(restored_cg_dir, 'memory.high')
                        if not os.path.exists(restored_high_file):
                            rollback_errs.append("Restored memory.high is absent")
                        else:
                            with open(restored_high_file, 'r') as rhf:
                                r_high = rhf.read().strip()
                            if not r_high.isdigit() or int(r_high) != int(old_plan_limits['memhigh']):
                                rollback_errs.append(f"Restored memory.high '{r_high}' does not match original plan {old_plan_limits['memhigh']}")

                        # 4. memory.swap.max
                        restored_swap_file = os.path.join(restored_cg_dir, 'memory.swap.max')
                        if not os.path.exists(restored_swap_file):
                            rollback_errs.append("Restored memory.swap.max is absent")
                        else:
                            with open(restored_swap_file, 'r') as rsf:
                                r_swap = rsf.read().strip()
                            if r_swap != '0':
                                rollback_errs.append(f"Restored memory.swap.max '{r_swap}' is not '0'")

                        # 5. pids.max
                        restored_pids_file = os.path.join(restored_cg_dir, 'pids.max')
                        if not os.path.exists(restored_pids_file):
                            rollback_errs.append("Restored pids.max is absent")
                        else:
                            with open(restored_pids_file, 'r') as rpf:
                                r_pids = rpf.read().strip()
                            if not r_pids.isdigit() or int(r_pids) != int(old_plan_limits['maxtask']):
                                rollback_errs.append(f"Restored pids.max '{r_pids}' does not match original plan {old_plan_limits['maxtask']}")

                        # 6. io.max
                        restored_io_file = os.path.join(restored_cg_dir, 'io.max')
                        if not os.path.exists(restored_io_file):
                            rollback_errs.append("Restored io.max is absent")
                        else:
                            with open(restored_io_file, 'r') as riof:
                                r_io = riof.read().strip()
                            r_valid_io, r_io_err = verify_io_rules(r_io, old_plan_limits, username=target_user)
                            if not r_valid_io:
                                rollback_errs.append(f"Restored io.max does not match original plan limits: {r_io_err}")

                    # Check restored native cgroup if native slice existed
                    restored_native_cg_dir = f"/sys/fs/cgroup/{uid}.slice"
                    if os.path.exists(restored_native_cg_dir):
                        restored_native_cpu = os.path.join(restored_native_cg_dir, 'cpu.max')
                        if os.path.exists(restored_native_cpu):
                            with open(restored_native_cpu, 'r') as rf:
                                r_ncpu = rf.read().strip()
                            if ' ' in r_ncpu:
                                rq, rp = r_ncpu.split()
                                if rq != 'max' and rq.isdigit() and rp.isdigit() and int(rp) > 0:
                                    r_pct = round((int(rq) / int(rp)) * 100, 1)
                                    if abs(r_pct - float(old_plan_limits['cpuquota'])) > 0.1:
                                        rollback_errs.append(f"Restored native CPU quota {r_pct}% does not match original plan quota {old_plan_limits['cpuquota']}%")
                        restored_native_mem = os.path.join(restored_native_cg_dir, 'memory.max')
                        if os.path.exists(restored_native_mem):
                            with open(restored_native_mem, 'r') as rmf:
                                r_nmem = rmf.read().strip()
                            if not r_nmem.isdigit() or int(r_nmem) != int(old_plan_limits['mem_max']):
                                rollback_errs.append(f"Restored native memory.max '{r_nmem}' does not match original plan {old_plan_limits['mem_max']}")
                        restored_native_io = os.path.join(restored_native_cg_dir, 'io.max')
                        if os.path.exists(restored_native_io):
                            with open(restored_native_io, 'r') as rnf:
                                r_nio = rnf.read().strip()
                            r_nvalid_io, r_nio_err = verify_io_rules(r_nio, old_plan_limits, username=target_user)
                            if not r_nvalid_io:
                                rollback_errs.append(f"Restored native io.max does not match original plan limits: {r_nio_err}")

                except Exception as rb_exc:
                    rollback_errs.append(f"Unexpected exception during rollback: {str(rb_exc)}")

                retained_backups = [bp for bp in [backup_info_path, backup_slice_path, backup_golden_slice_path] if os.path.exists(bp)]

                if rollback_errs:
                    # Incomplete recovery: retain backup artifacts for forensic analysis and record in audit_log
                    conn = self.get_db()
                    try:
                        conn.execute("""
                            INSERT INTO audit_log (timestamp, actor, action, target_account, details_json)
                            VALUES (?, ?, 'adapter_sync_rollback_failed', ?, ?)
                        """, (int(time.time()), f"{adapter_type}_adapter", target_user, json.dumps({
                            'forward_error': str(txn_err),
                            'rollback_errors': rollback_errs,
                            'retained_artifacts': retained_backups
                        })))
                        conn.commit()
                    finally:
                        conn.close()

                    return {
                        'error': f"Plan synchronization failed: {str(txn_err)}. CRITICAL: Rollback failed: {'; '.join(rollback_errs)}",
                        'rolled_back': False,
                        'state': 'FAILED_INCONSISTENT',
                        'status_code': 500,
                        'retained_artifacts': retained_backups
                    }

                # Clean up temporary backup files ONLY when rollback cleanly completed AND verified
                for bp in retained_backups:
                    try: os.remove(bp)
                    except Exception: pass

                return {
                    'error': f"Plan synchronization failed: {str(txn_err)}. Account '{target_user}' rolled back cleanly to '{old_plan}'.",
                    'rolled_back': True,
                    'restored_plan': old_plan,
                    'state': 'ROLLED_BACK',
                    'status_code': 500
                }

            # FORWARD SUCCESS PATH: COMMIT DATABASE TRANSACTION FIRST, THEN DELETE RECOVERY BACKUPS
            result = {
                'success': True,
                'adapter': adapter_type,
                'username': target_user,
                'previous_plan': old_plan,
                'active_plan': target_plan,
                'message': f"Adapter {adapter_type} synchronized account '{target_user}' from '{old_plan}' to '{target_plan}'",
                'reloaded': True,
                'phps_reloaded': reloaded_phps,
                'replayed': False
            }

            conn = self.get_db()
            try:
                conn.execute("""
                    INSERT INTO audit_log (timestamp, actor, action, target_account, details_json)
                    VALUES (?, ?, 'adapter_sync', ?, ?)
                """, (int(time.time()), f"{adapter_type}_adapter", target_user, json.dumps({
                    'previous_plan': old_plan,
                    'new_plan': target_plan,
                    'billing_input': billing_plan,
                    'adapter': adapter_type
                })))
                conn.execute("""
                    INSERT OR REPLACE INTO webhook_log (idempotency_key, timestamp, source, event_type, target_account, payload_json, response_json, status_code)
                    VALUES (?, ?, ?, 'plan_sync', ?, ?, ?, 200)
                """, (idempotency_key, int(time.time()), adapter_type, target_user, json.dumps(payload), json.dumps(result)))
                conn.commit()
            except Exception as db_commit_err:
                retained_backups = [bp for bp in [backup_info_path, backup_slice_path, backup_golden_slice_path] if os.path.exists(bp)]
                return {
                    'error': f"Plan applied to kernel but database commit failed: {str(db_commit_err)}. Recovery artifacts retained.",
                    'rolled_back': False,
                    'state': 'FAILED_INCONSISTENT',
                    'status_code': 500,
                    'retained_artifacts': retained_backups
                }
            finally:
                conn.close()

            # DISCARD BACKUPS ONLY AFTER SUCCESSFUL DURABLE DATABASE COMMIT
            for bp in [backup_info_path, backup_slice_path, backup_golden_slice_path]:
                if os.path.exists(bp):
                    try: os.remove(bp)
                    except Exception: pass

            return result

        finally:
            if lock_fd:
                try:
                    if fcntl: fcntl.flock(lock_fd, fcntl.LOCK_UN)
                    lock_fd.close()
                except Exception: pass

    def action_delete_native_plan(self, admin_user: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """A04: Delete native Webuzo resource plan with safety check against assigned accounts."""
        plan_name = str(params.get('plan_name', '')).strip().lower()
        if not plan_name:
            return {'error': 'Parameter plan_name is required'}
        if plan_name == 'default':
            return {'error': "Safety Refusal: The 'default' resource plan cannot be deleted."}

        # Check assigned accounts
        users = self.collector.get_webuzo_users()
        assigned = [u for u, d in users.items() if d.get('plan_name') == plan_name]
        if assigned:
            return {'error': f"Cannot delete plan '{plan_name}': {len(assigned)} account(s) are currently assigned to it ({', '.join(assigned[:3])}). Reassign them first."}

        plan_file = f"/var/webuzo/cgroups/{plan_name}"
        if not os.path.exists(plan_file):
            return {'error': f"Plan '{plan_name}' does not exist in /var/webuzo/cgroups/"}

        try:
            os.remove(plan_file)
        except Exception as e:
            return {'error': f"Failed to delete plan file: {str(e)}"}

        conn = self.get_db()
        try:
            conn.execute("""
                INSERT INTO audit_log (timestamp, actor, action, target_account, details_json)
                VALUES (?, ?, 'delete_native_plan', ?, ?)
            """, (int(time.time()), admin_user, plan_name, json.dumps({'deleted_plan': plan_name})))
            conn.commit()
        finally:
            conn.close()

        return {'success': True, 'message': f"Resource plan '{plan_name}' deleted successfully."}

    def action_get_capacity_planning(self) -> Dict[str, Any]:
        """A11, G06: Sold allowances vs physical capacity vs observed demand."""
        users = self.collector.get_webuzo_users()
        total_accounts = len(users)

        total_sold_cpu = 0
        total_sold_mem = 0
        total_sold_tasks = 0
        for uname, udata in users.items():
            p_limits = self.collector.get_plan_limits(udata.get('plan_name', 'default'))
            total_sold_cpu += p_limits.get('cpuquota', 100)
            total_sold_mem += p_limits.get('mem_max', 1024 * 1024 * 1024)
            total_sold_tasks += p_limits.get('maxtask', 128)

        # Physical capacity
        host_cpus = self.collector.host_cpu_count
        meminfo = parse_key_value_file('/proc/meminfo')
        ram_total_bytes = int(meminfo.get('MemTotal:', '0').replace('kB', '')) * 1024
        ram_total_mib = round(ram_total_bytes / 1024 / 1024)

        # Golden Shield hosting pool quota
        gs_status = self.golden_shield.get_status()
        cfg_policy = gs_status.get('configured_policy', {})
        hosting_cpu = cfg_policy.get('customerCpuPercent', host_cpus * 85)
        hosting_mem_mib = cfg_policy.get('hostingMemoryMaxMiB', round(ram_total_mib * 0.85))

        sold_mem_mib = round(total_sold_mem / 1024 / 1024)
        cpu_commit_ratio = round(total_sold_cpu / max(1, hosting_cpu), 2)
        mem_commit_ratio = round(sold_mem_mib / max(1, hosting_mem_mib), 2)

        # Observed 24h peak concurrent demand - decoupled independent queries (Finding 8)
        conn = self.get_db()
        peak_concurrent_cpu = 0.0
        peak_cpu_epoch = 0
        peak_concurrent_mem = 0
        peak_mem_epoch = 0
        try:
            cur = conn.cursor()
            # 1. Independent peak concurrent CPU
            cur.execute("""
                SELECT timestamp, SUM(cpu_percent) as total_cpu
                FROM samples
                WHERE timestamp >= ?
                GROUP BY timestamp
                ORDER BY total_cpu DESC
                LIMIT 1
            """, (int(time.time()) - 86400,))
            row_cpu = cur.fetchone()
            if row_cpu:
                peak_concurrent_cpu = round(row_cpu['total_cpu'] or 0.0, 1)
                peak_cpu_epoch = row_cpu['timestamp'] or 0

            # 2. Independent peak concurrent memory
            cur.execute("""
                SELECT timestamp, SUM(mem_current_bytes) as total_mem
                FROM samples
                WHERE timestamp >= ?
                GROUP BY timestamp
                ORDER BY total_mem DESC
                LIMIT 1
            """, (int(time.time()) - 86400,))
            row_mem = cur.fetchone()
            if row_mem:
                peak_concurrent_mem = row_mem['total_mem'] or 0
                peak_mem_epoch = row_mem['timestamp'] or 0
        finally:
            conn.close()

        risk = "OPTIMAL"
        if mem_commit_ratio > 2.0 or cpu_commit_ratio > 3.0:
            risk = "HIGH_OVERCOMMIT"
        elif mem_commit_ratio > 1.3 or cpu_commit_ratio > 1.8:
            risk = "MODERATE_OVERCOMMIT"

        cap_dict = {
            'physical_cores': host_cpus,
            'physical_ram_mib': ram_total_mib,
            'hosting_pool_cpu_percent': hosting_cpu,
            'hosting_pool_mem_mib': hosting_mem_mib,
            'total_sold_cpu_percent': total_sold_cpu,
            'total_sold_mem_mib': sold_mem_mib,
            'cpu_oversell_ratio': cpu_commit_ratio,
            'mem_oversell_ratio': mem_commit_ratio,
            'total_accounts': total_accounts,
            'capacity_risk': risk
        }

        return {
            'success': True,
            'capacity': cap_dict,
            'summary': {
                'total_accounts': total_accounts,
                'capacity_risk': risk,
                'cpu_commit_ratio': cpu_commit_ratio,
                'mem_commit_ratio': mem_commit_ratio
            },
            'physical_hardware': {
                'cpu_cores': host_cpus,
                'cpu_capacity_pct': host_cpus * 100,
                'ram_total_mib': ram_total_mib
            },
            'golden_shield_pool': {
                'hosting_cpu_quota_pct': hosting_cpu,
                'system_headroom_cpu_pct': (host_cpus * 100) - hosting_cpu,
                'hosting_ram_cap_mib': hosting_mem_mib
            },
            'sold_allocations': {
                'total_sold_cpu_pct': total_sold_cpu,
                'total_sold_mem_mib': sold_mem_mib,
                'total_sold_tasks': total_sold_tasks
            },
            'observed_24h_peaks': {
                'peak_concurrent_cpu_pct': peak_concurrent_cpu,
                'peak_concurrent_cpu_timestamp': peak_cpu_epoch,
                'peak_concurrent_mem_mib': round(peak_concurrent_mem / 1024 / 1024, 1),
                'peak_concurrent_mem_timestamp': peak_mem_epoch
            }
        }

    def action_get_scheduled_reports(self) -> Dict[str, Any]:
        """A16: Retrieve generated scheduled reports."""
        conn = self.get_db()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM scheduled_reports ORDER BY timestamp DESC LIMIT 20")
            rows = cur.fetchall()
            reports = []
            for r in rows:
                reports.append({
                    'id': r['id'],
                    'timestamp': r['timestamp'],
                    'report_type': r['report_type'],
                    'summary': json.loads(r['summary_json']) if r['summary_json'] else {},
                    'dispatched_to': r['dispatched_to'],
                    'status': r['status']
                })
            return {'success': True, 'reports': reports}
        finally:
            conn.close()

    def action_dispatch_scheduled_report(self, admin_user: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """A16: Generate and dispatch daily/weekly capacity & security report."""
        report_type = str(params.get('report_type', 'daily')).lower()
        users = self.collector.get_webuzo_users()
        overview = self.action_admin_overview()
        capacity = self.action_get_capacity_planning()

        # Compute real top consumers from latest telemetry samples
        top_consumers = []
        conn = self.get_db()
        report_id = None
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT s.username, s.cpu_allowance_percent, s.mem_current_bytes, s.tasks_current,
                       s.cpu_throttled_events, s.oom_kill_events
                FROM samples s
                INNER JOIN (
                    SELECT username, MAX(timestamp) as max_ts FROM samples GROUP BY username
                ) latest ON s.username = latest.username AND s.timestamp = latest.max_ts
                ORDER BY s.cpu_allowance_percent DESC
                LIMIT 5
            """)
            for r in cur.fetchall():
                top_consumers.append({
                    'username': r['username'],
                    'cpu_allowance_percent': r['cpu_allowance_percent'],
                    'mem_current_formatted': format_bytes(r['mem_current_bytes'] or 0),
                    'tasks_current': r['tasks_current'],
                    'cpu_throttled_events': r['cpu_throttled_events'],
                    'oom_kill_events': r['oom_kill_events']
                })

            summary = {
                'generated_at': int(time.time()),
                'period': report_type,
                'total_accounts': len(users),
                'capacity_summary': capacity.get('summary', {}),
                'top_consumers': top_consumers,
                'system_load': overview.get('server', {}).get('load1', 0.0),
                'golden_shield_status': overview.get('golden_shield', {}).get('state', 'Unknown')
            }

            cur.execute("""
                INSERT INTO scheduled_reports (timestamp, report_type, summary_json, dispatched_to, status)
                VALUES (?, ?, ?, ?, 'dispatched')
            """, (int(time.time()), report_type, json.dumps(summary), 'system_admin'))
            report_id = cur.lastrowid
            conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('last_scheduled_report_ts', ?)", (str(int(time.time())),))
            conn.execute("""
                INSERT INTO audit_log (timestamp, actor, action, target_account, details_json)
                VALUES (?, ?, 'dispatch_report', 'system', ?)
            """, (int(time.time()), admin_user, json.dumps({'type': report_type, 'report_id': report_id})))
            conn.commit()
        finally:
            conn.close()

        return {'success': True, 'report_type': report_type, 'report_id': report_id, 'summary': summary}

    def action_get_report_schedule(self) -> Dict[str, Any]:
        """A16: Retrieve automated report schedule configuration and due status."""
        conn = self.get_db()
        try:
            cur = conn.cursor()
            cur.execute("SELECT key, value FROM settings WHERE key IN ('report_schedule', 'last_scheduled_report_ts', 'report_recipient')")
            rows = dict(cur.fetchall())
        finally:
            conn.close()

        schedule = rows.get('report_schedule', 'daily').lower()
        last_ts = int(rows.get('last_scheduled_report_ts', 0))
        recipient = rows.get('report_recipient', 'system_admin')
        now = int(time.time())

        interval = 86400 if schedule == 'daily' else (7 * 86400 if schedule == 'weekly' else 0)
        if schedule == 'disabled' or interval == 0:
            next_due = 0
            is_due = False
            due_str = 'Disabled'
        else:
            next_due = (last_ts + interval) if last_ts > 0 else now
            is_due = (now >= next_due)
            due_str = time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(next_due))

        return {
            'success': True,
            'schedule': schedule,
            'recipient': recipient,
            'last_run_timestamp': last_ts,
            'last_run_formatted': time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(last_ts)) if last_ts > 0 else 'Never',
            'next_due_timestamp': next_due,
            'next_due_formatted': due_str,
            'due_date': due_str,
            'next_due': next_due,
            'is_due': is_due
        }

    def action_save_report_schedule(self, admin_user: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """A16: Save report schedule configuration."""
        cadence = str(params.get('schedule', 'daily')).strip().lower()
        if cadence not in ('daily', 'weekly', 'disabled'):
            return {'error': "Invalid schedule cadence. Must be 'daily', 'weekly', or 'disabled'."}
        recipient = str(params.get('recipient', 'system_admin')).strip()

        conn = self.get_db()
        try:
            now = int(time.time())
            conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('report_schedule', ?)", (cadence,))
            if recipient:
                conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('report_recipient', ?)", (recipient,))
            conn.execute("""
                INSERT INTO audit_log (timestamp, actor, action, target_account, details_json)
                VALUES (?, ?, 'save_report_schedule', 'system', ?)
            """, (now, admin_user, json.dumps({'schedule': cadence, 'recipient': recipient})))
            conn.commit()
        finally:
            conn.close()

        return {'success': True, 'message': f"Report schedule updated to '{cadence}'.", 'schedule': self.action_get_report_schedule()}

    def action_get_package_mappings(self) -> Dict[str, Any]:
        """B05: Retrieve billing package to resource plan mappings."""
        conn = self.get_db()
        try:
            cur = conn.cursor()
            cur.execute("SELECT billing_package, resource_plan, updated_at FROM package_mappings ORDER BY billing_package ASC")
            rows = cur.fetchall()
            mappings = []
            for r in rows:
                mappings.append({
                    'billing_package': r['billing_package'],
                    'resource_plan': r['resource_plan'],
                    'updated_at': r['updated_at'],
                    'updated_formatted': time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(r['updated_at']))
                })
            native_plans = []
            for plan_path in sorted(pathlib.Path('/var/webuzo/cgroups').glob('*')):
                if not plan_path.is_file() or not re.fullmatch(r'[a-zA-Z0-9_-]{1,64}', plan_path.name):
                    continue
                try:
                    json.loads(plan_path.read_text())  # Ignore non-plan files and malformed configuration.
                    limits = self.collector.get_plan_limits(plan_path.name)
                    native_plans.append({'name': plan_path.name,
                                         'label': f"{plan_path.name} ({limits['cpuquota']}% CPU, {format_bytes(limits['mem_max'])} RAM)"})
                except (OSError, ValueError, TypeError, KeyError):
                    continue
            return {'success': True, 'mappings': mappings, 'native_plans': native_plans}
        finally:
            conn.close()

    def action_save_package_mapping(self, admin_user: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """B05: Add or update billing package to resource plan mapping."""
        pkg = str(params.get('billing_package', '')).strip()
        plan = str(params.get('resource_plan', '')).strip().lower()

        if not pkg or not plan:
            return {'error': 'Both billing_package and resource_plan are required.'}

        if not re.fullmatch(r'[a-zA-Z0-9_-]{1,64}', plan):
            return {'error': 'Invalid resource plan name'}
        if len(pkg) > 120:
            return {'error': 'Billing package name must be at most 120 characters'}
        # Validate that the resource plan exists in Webuzo cgroups
        plan_file = f"/var/webuzo/cgroups/{plan}"
        if not os.path.exists(plan_file):
            return {'error': f"Target resource plan '{plan}' does not exist in /var/webuzo/cgroups/"}

        conn = self.get_db()
        try:
            now = int(time.time())
            conn.execute("""
                INSERT OR REPLACE INTO package_mappings (billing_package, resource_plan, updated_at)
                VALUES (?, ?, ?)
            """, (pkg, plan, now))
            conn.execute("""
                INSERT INTO audit_log (timestamp, actor, action, target_account, details_json)
                VALUES (?, ?, 'save_package_mapping', ?, ?)
            """, (now, admin_user, pkg, json.dumps({'billing_package': pkg, 'resource_plan': plan})))
            conn.commit()
        finally:
            conn.close()

        return {'success': True, 'message': f"Mapping saved: '{pkg}' -> '{plan}'", 'mapping': {'billing_package': pkg, 'resource_plan': plan}}

    def action_delete_package_mapping(self, admin_user: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """B05: Remove a billing package mapping."""
        pkg = str(params.get('billing_package', '')).strip()
        if not pkg:
            return {'error': 'Parameter billing_package is required.'}

        conn = self.get_db()
        try:
            now = int(time.time())
            conn.execute("DELETE FROM package_mappings WHERE LOWER(billing_package) = LOWER(?)", (pkg,))
            conn.execute("""
                INSERT INTO audit_log (timestamp, actor, action, target_account, details_json)
                VALUES (?, ?, 'delete_package_mapping', ?, ?)
            """, (now, admin_user, pkg, json.dumps({'deleted_package': pkg})))
            conn.commit()
        finally:
            conn.close()

        return {'success': True, 'message': f"Mapping for '{pkg}' deleted successfully."}

    def action_get_branding_settings(self) -> Dict[str, Any]:
        """B02: Retrieve configurable UI branding settings."""
        conn = self.get_db()
        try:
            cur = conn.cursor()
            cur.execute("SELECT key, value FROM settings WHERE key LIKE 'brand_%'")
            rows = dict(cur.fetchall())
            return {
                'brand_name': rows.get('brand_name', 'UNISELV Resource Manager'),
                'brand_logo_url': rows.get('brand_logo_url', ''),
                'brand_primary_color': rows.get('brand_primary_color', '#2563eb'),
                'brand_support_url': rows.get('brand_support_url', 'https://uniselv.com/support'),
                'brand_docs_url': rows.get('brand_docs_url', 'https://docs.uniselv.com'),
                'locale': rows.get('brand_locale', 'en')
            }
        finally:
            conn.close()

    def action_save_branding_settings(self, admin_user: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """B02: Save validated branding colors, logo, and links atomically."""
        from urllib.parse import urlsplit
        for key in ('brand_logo_url', 'brand_support_url', 'brand_docs_url'):
            if key not in params:
                continue
            value = str(params[key]).strip()
            try:
                parsed = urlsplit(value)
                valid = (not value or (parsed.scheme in ('http', 'https') and parsed.hostname
                         and not parsed.username and not parsed.password and not re.search(r'[\s<>"\\]', value)))
            except ValueError:
                valid = False
            if not valid or len(value) > 2048:
                return {'error': f'{key} must be blank or an absolute HTTP(S) URL without embedded credentials'}
            params[key] = value
        if 'brand_primary_color' in params and not re.fullmatch(r'#[0-9a-fA-F]{6}', str(params['brand_primary_color'])):
            return {'error': 'Theme color must use #RRGGBB format'}
        if 'brand_locale' in params and params['brand_locale'] not in ('en', 'bn'):
            return {'error': 'Unsupported language locale'}
        if 'brand_name' in params and (not str(params['brand_name']).strip() or len(str(params['brand_name'])) > 120):
            return {'error': 'Product title must contain 1 to 120 characters'}
        conn = self.get_db()
        try:
            for k in ['brand_name', 'brand_logo_url', 'brand_primary_color', 'brand_support_url', 'brand_docs_url', 'brand_locale']:
                if k in params:
                    conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (k, str(params[k])))
            conn.execute("""
                INSERT INTO audit_log (timestamp, actor, action, target_account, details_json)
                VALUES (?, ?, 'save_branding', 'system', ?)
            """, (int(time.time()), admin_user, json.dumps(params)))
            conn.commit()
        finally:
            conn.close()

        return {'success': True, 'branding': self.action_get_branding_settings()}

    def action_get_audit_log(self, params: Dict[str, Any], allowed_targets=None, actor_scope=None) -> Dict[str, Any]:
        """B08: Searchable and exportable administrative audit history."""
        search = str(params.get('search', '')).strip().lower()
        actor = str(params.get('actor', '')).strip()
        action_type = str(params.get('action_type', '')).strip()
        limit = min(500, max(10, int(params.get('limit', 100))))

        conn = self.get_db()
        try:
            cur = conn.cursor()
            query = "SELECT * FROM audit_log WHERE 1=1"
            q_args = []

            if allowed_targets is not None:
                targets = sorted(allowed_targets)
                placeholders = ','.join('?' for _ in targets) or 'NULL'
                query += f' AND (actor = ? OR target_account IN ({placeholders}))'
                q_args.extend([actor_scope] + targets)
            if actor:
                query += " AND actor = ?"
                q_args.append(actor)
            if action_type:
                query += " AND action = ?"
                q_args.append(action_type)
            if search:
                query += " AND (actor LIKE ? OR action LIKE ? OR target_account LIKE ? OR details_json LIKE ?)"
                like_term = f"%{search}%"
                q_args.extend([like_term, like_term, like_term, like_term])

            query += " ORDER BY timestamp DESC LIMIT ?"
            q_args.append(limit)

            cur.execute(query, tuple(q_args))
            rows = cur.fetchall()

            logs = []
            for r in rows:
                logs.append({
                    'id': r['id'],
                    'timestamp': r['timestamp'],
                    'date_formatted': time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(r['timestamp'])),
                    'actor': r['actor'],
                    'action': r['action'],
                    'target_account': r['target_account'],
                    'details': json.loads(r['details_json']) if r['details_json'] else {}
                })
            return {'success': True, 'count': len(logs), 'audit_logs': logs, 'logs': logs}
        finally:
            conn.close()

    def action_process_webhook(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """B06, B07: Authenticated integration endpoint with HMAC/bearer auth, normalized provider adapters, and transactional execution."""
        auth_header = params.get('token') or params.get('bearer_token') or ''
        sig_header = params.get('signature') or params.get('x_uniselv_signature') or ''
        raw_body = params.get('raw_body') or ''

        conn = self.get_db()
        expected_token = ''
        expected_secret = ''
        try:
            cur = conn.cursor()
            cur.execute("SELECT key, value FROM settings WHERE key IN ('webhook_bearer_token', 'webhook_secret')")
            rows = dict(cur.fetchall())
            expected_token = rows.get('webhook_bearer_token', '').strip()
            expected_secret = rows.get('webhook_secret', '').strip()
        finally:
            conn.close()

        # 1. Fail closed if neither secret nor bearer token is configured on this server
        if not expected_token and not expected_secret:
            return {
                'error': 'Forbidden: Inbound webhook integration is disabled (no webhook bearer token or HMAC secret configured in settings)',
                'status_code': 403
            }

        # 2. HMAC signature verification (if HMAC secret configured, signature + raw body are mandatory)
        if expected_secret:
            if not sig_header or not raw_body:
                return {'error': 'Forbidden: Missing webhook HMAC-SHA256 signature or request body', 'status_code': 401}
            import hmac
            expected_sig = hmac.new(expected_secret.encode('utf-8'), raw_body.encode('utf-8'), hashlib.sha256).hexdigest()
            clean_sig = sig_header.replace('sha256=', '').strip()
            if not secrets.compare_digest(expected_sig, clean_sig):
                return {'error': 'Forbidden: Webhook HMAC-SHA256 signature verification failed', 'status_code': 401}

        # 3. Bearer token verification (if token configured)
        if expected_token:
            if not auth_header or not secrets.compare_digest(str(auth_header).strip(), expected_token):
                return {'error': 'Forbidden: Invalid or missing webhook authentication bearer token', 'status_code': 403}

        # 4. Authoritative Payload Resolution: Parse directly from verified raw_body if present!
        if raw_body:
            try:
                parsed_body = json.loads(raw_body)
                if isinstance(parsed_body, dict):
                    # Replace params with parsed_body so verified bytes strictly control execution
                    params = parsed_body
            except Exception as e:
                return {'error': f'Bad Request: Malformed JSON in webhook request body: {str(e)}', 'status_code': 400}

        adapter = str(params.get('adapter', 'whmcs')).lower()
        payload = params.get('payload') or {}
        if not isinstance(payload, dict):
            payload = {}

        # 5. Provider Payload Normalization: WHMCS Post-Provisioning Hook format
        whmcs_params = params.get('params') or (payload.get('params') if isinstance(payload.get('params'), dict) else None)
        if isinstance(whmcs_params, dict):
            adapter = 'whmcs'
            username = whmcs_params.get('username') or whmcs_params.get('user')
            plan = whmcs_params.get('package') or whmcs_params.get('package_name') or whmcs_params.get('plan')
            # Event ID must identify the discrete change event/transaction, NEVER static service ID alone!
            event_id = whmcs_params.get('event_id') or whmcs_params.get('idempotency_key') or whmcs_params.get('transaction_id')
            service_id = whmcs_params.get('serviceid') or whmcs_params.get('service_id')
            payload = {'username': username, 'billing_package': plan}
            if event_id:
                payload['idempotency_key'] = event_id
            if service_id:
                payload['service_id'] = service_id

        # 6. Provider Payload Normalization: Blesta Services.edit Event format
        blesta_vars = params.get('vars') or (payload.get('vars') if isinstance(payload.get('vars'), dict) else None)
        if isinstance(blesta_vars, dict):
            adapter = 'blesta'
            username = blesta_vars.get('username') or blesta_vars.get('user')
            plan = blesta_vars.get('package_name') or blesta_vars.get('package') or blesta_vars.get('plan')
            event_id = blesta_vars.get('event_id') or blesta_vars.get('idempotency_key') or blesta_vars.get('transaction_id')
            service_id = blesta_vars.get('service_id') or blesta_vars.get('serviceid')
            payload = {'username': username, 'billing_package': plan}
            if event_id:
                payload['idempotency_key'] = event_id
            if service_id:
                payload['service_id'] = service_id

        # Ensure top-level fields are propagated into payload
        if 'username' in params and 'username' not in payload:
            payload['username'] = params['username']
        if 'billing_package' in params and 'billing_package' not in payload:
            payload['billing_package'] = params['billing_package']
        if 'plan' in params and 'plan' not in payload:
            payload['plan'] = params['plan']
        if 'idempotency_key' in params and 'idempotency_key' not in payload:
            payload['idempotency_key'] = params['idempotency_key']

        return self.action_run_adapter_sync(f"{adapter}_webhook", {
            'adapter': adapter,
            'payload': payload
        })

