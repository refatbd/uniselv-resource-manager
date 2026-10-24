import os
import sys
import time
import json
import socket
import signal
import threading
import pathlib
import subprocess
import shutil
import struct
import secrets
import grp
import pwd
import sqlite3

from collector import MetricsCollector
from ipc_server import IpcRequestHandler
from golden_shield_manager import GoldenShieldManager

SOCKET_PATH = '/run/uniselv-resman/agent.sock'
TOKEN_PATH = '/run/uniselv-resman/broker.token'
DB_PATH = '/var/lib/uniselv-resource-manager/resman.sqlite'
MAX_PAYLOAD_BYTES = 65536
MAX_CONCURRENT_CLIENTS = 16

class AgentDaemon:
    def __init__(self, socket_path: str = SOCKET_PATH, db_path: str = DB_PATH):
        self.socket_path = socket_path
        self.db_path = db_path
        self.running = True
        self.collector = MetricsCollector(db_path=self.db_path)
        self.handler = IpcRequestHandler(db_path=self.db_path, collector=self.collector)
        self.golden_shield = GoldenShieldManager(db_conn_factory=self.handler.get_db)
        self.server_sock = None
        self.broker_token = None
        self.client_semaphore = threading.BoundedSemaphore(MAX_CONCURRENT_CLIENTS)

    def generate_broker_token(self):
        """Generate ephemeral high-entropy token readable only by root and webuzo group."""
        self.broker_token = secrets.token_hex(32)
        token_file = pathlib.Path(TOKEN_PATH)
        token_file.parent.mkdir(parents=True, exist_ok=True)
        token_file.write_text(self.broker_token, encoding='utf-8')
        try:
            gid = grp.getgrnam('webuzo').gr_gid
            os.chown(str(token_file), 0, gid)
            os.chmod(str(token_file), 0o640)
        except Exception:
            os.chmod(str(token_file), 0o600)

    def check_expired_overrides(self):
        """Serialize boost recovery and only finish after effective restoration."""
        with self.handler._override_lock:
            conn = self.handler.get_db()
            try:
                expired = conn.execute("SELECT * FROM temporary_overrides WHERE (status IN ('applying','active','failed_restoration') AND expires_at <= ?) OR status = 'applying'", (int(time.time()),)).fetchall()
            finally:
                conn.close()
            for row in expired:
                try:
                    result = self.handler.restore_temporary_override(row, 'system')
                except Exception as error:
                    result = {'error': str(error)}
                success = result.get('success') is True
                status = 'expired' if success else 'failed_restoration'
                conn = self.handler.get_db()
                try:
                    changed = conn.execute("UPDATE temporary_overrides SET status = ? WHERE id = ? AND status IN ('applying','active','failed_restoration')", (status, row['id'])).rowcount
                    if changed and (success or row['status'] != status):
                        conn.execute("INSERT INTO audit_log (timestamp, actor, action, target_account, details_json) VALUES (?, 'system', ?, ?, ?)",
                            (int(time.time()), 'override_expired' if success else 'override_restoration_failed', row['username'], json.dumps({'override_id': row['id'], 'restored_plan': row['original_plan'], 'result': result})))
                    conn.commit()
                finally:
                    conn.close()

    def ensure_startup_enforcement_boundaries(self):
        """Verify that every registered Webuzo account has its cgroup limits active before workloads run."""
        users = self.collector.get_webuzo_users()
        for uname, udata in users.items():
            uid = udata['uid']
            golden_slice = pathlib.Path(f'/sys/fs/cgroup/golden.slice/golden-{uid}.slice')
            if not golden_slice.exists():
                try:
                    subprocess.run(['python3', '/usr/local/sbin/golden-shield.py', 'prepare-account', str(uid)], capture_output=True, timeout=15)
                except Exception:
                    pass

        try:
            self.golden_shield.reconcile_hardware_changes()
        except Exception as e:
            print(f"[Agent Hardware Init Error] {e}", file=sys.stderr)

        try:
            if getattr(self.collector, 'circuit_breaker_active', False):
                print(f"[Agent Startup] Circuit breaker active with {len(self.collector.circuit_breaker_throttled_users)} throttled users. Checking load...", file=sys.stderr)
                load1, _, _ = os.getloadavg()
                if load1 <= self.collector.circuit_breaker_recovery_threshold:
                    print(f"[Agent Startup] Load healthy ({load1:.2f} <= {self.collector.circuit_breaker_recovery_threshold}), restoring quotas...", file=sys.stderr)
                    self.collector._restore_circuit_breaker_quotas()
                else:
                    print(f"[Agent Startup] Load elevated ({load1:.2f} > {self.collector.circuit_breaker_recovery_threshold}), maintaining throttled state.", file=sys.stderr)
        except Exception as e:
            print(f"[Agent Circuit Breaker Init Error] {e}", file=sys.stderr)

    def check_scheduled_reports(self):
        """A16: Automatic background execution of daily/weekly capacity & security reports."""
        conn = sqlite3.connect(self.db_path)
        try:
            cur = conn.cursor()
            cur.execute("SELECT key, value FROM settings WHERE key IN ('report_schedule', 'last_scheduled_report_ts')")
            settings = dict(cur.fetchall())
            schedule = settings.get('report_schedule', 'daily').lower()
            if schedule == 'disabled' or schedule == '0':
                return

            last_ts = int(settings.get('last_scheduled_report_ts', 0))
            now = int(time.time())
            interval = 86400 if schedule == 'daily' else (7 * 86400)

            if now - last_ts >= interval:
                print(f"[Agent Scheduled Report] Triggering {schedule} background report...", file=sys.stderr)
                res = self.handler.action_dispatch_scheduled_report('daemon_scheduler', {'report_type': schedule})
                if res.get('success'):
                    print(f"[Agent Scheduled Report] Successfully stored report #{res.get('report_id')}", file=sys.stderr)
        except Exception as e:
            print(f"[Agent Scheduled Report Error] {e}", file=sys.stderr)
        finally:
            conn.close()

    def collector_loop(self):
        """Periodic background collection thread."""
        last_prune = 0
        last_drift_check = 0
        last_report_check = 0
        self.ensure_startup_enforcement_boundaries()

        while self.running:
            try:
                # 1. ALWAYS check expired overrides, even during maintenance mode
                self.check_expired_overrides()

                # 2. Collect telemetry only if not in maintenance mode
                if not self.handler.maintenance_mode:
                    self.collector.collect_step()
                    self.collector.check_runaway_watchdog()
                    self.collector.check_overload_circuit_breaker()

                # 3. Prune database once per hour if auto_prune_hourly is enabled
                if self.collector.settings.get('auto_prune_hourly', True) and (time.time() - last_prune > 3600):
                    self.collector.prune_retention()
                    last_prune = time.time()

                # 4. Check hardware capacity changes & reconcile every 5 minutes
                if time.time() - last_drift_check > 300:
                    try:
                        rec = self.golden_shield.reconcile_hardware_changes()
                        if rec and rec.get('reconciled'):
                            print(f"[Agent Hardware Reconciled] {rec['description']}", file=sys.stderr)
                    except Exception as e:
                        print(f"[Agent Hardware Check Error] {e}", file=sys.stderr)
                    last_drift_check = time.time()

                # 5. Check background scheduled reports
                if time.time() - last_report_check > 60:
                    self.check_scheduled_reports()
                    last_report_check = time.time()

            except Exception as e:
                print(f"[Agent Collector Error] {e}", file=sys.stderr)

            # Configurable dynamic sampling interval
            interval = int(self.collector.settings.get('telemetry_interval', 5))
            time.sleep(max(3, min(60, interval)))

    def governance_loop(self):
        while self.running:
            try:
                if not self.handler.maintenance_mode:
                    self.handler.governance_tick()
            except Exception as error:
                print('[Runtime Governance Error] ' + str(error), file=sys.stderr)
            for _ in range(60):
                if not self.running: return
                time.sleep(1)

    def run_ipc_server(self):
        """UNIX domain socket server loop with strict permissions and peer credentials."""
        sock_dir = os.path.dirname(self.socket_path)
        os.makedirs(sock_dir, exist_ok=True)
        if os.path.exists(self.socket_path):
            os.unlink(self.socket_path)

        self.generate_broker_token()

        self.server_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server_sock.bind(self.socket_path)
        self.server_sock.listen(MAX_CONCURRENT_CLIENTS)

        # Set restrictive permissions: 0660 root:webuzo
        try:
            gid = grp.getgrnam('webuzo').gr_gid
            os.chown(self.socket_path, 0, gid)
            os.chmod(self.socket_path, 0o660)
        except Exception:
            os.chmod(self.socket_path, 0o600)

        print(f"UNISELV Agent listening securely on {self.socket_path}")

        while self.running:
            try:
                conn, _ = self.server_sock.accept()
                if not self.client_semaphore.acquire(blocking=False):
                    conn.sendall(json.dumps({'error': 'Server busy: Max concurrent connections reached'}).encode('utf-8') + b"\n")
                    conn.close()
                    continue

                t = threading.Thread(target=self._client_worker, args=(conn,), daemon=True)
                t.start()
            except Exception:
                if not self.running:
                    break

    def _client_worker(self, conn: socket.socket):
        try:
            self.client_thread(conn)
        finally:
            self.client_semaphore.release()

    def client_thread(self, conn: socket.socket):
        try:
            conn.settimeout(10.0)

            # 1. Peer credential verification via SO_PEERCRED
            creds = conn.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, 12)
            peer_pid, peer_uid, peer_gid = struct.unpack('3i', creds)

            # Only root (UID 0) or webuzo broker (UID 999) permitted
            webuzo_uid = 999
            try:
                webuzo_uid = pwd.getpwnam('webuzo').pw_uid
            except Exception:
                pass

            if peer_uid != 0 and peer_uid != webuzo_uid:
                err_resp = json.dumps({'error': 'Security Refusal: Unauthorized socket peer credentials'}).encode('utf-8') + b"\n"
                conn.sendall(err_resp)
                conn.close()
                return

            # 2. Read bounded request payload (max 64 KiB)
            data = b""
            while len(data) < MAX_PAYLOAD_BYTES:
                chunk = conn.recv(4096)
                if not chunk:
                    break
                data += chunk
                if b"\n" in chunk:
                    break

            if len(data) >= MAX_PAYLOAD_BYTES:
                err_resp = json.dumps({'error': 'Payload too large: Max 64 KiB allowed'}).encode('utf-8') + b"\n"
                conn.sendall(err_resp)
                return

            if data:
                raw_req = data.strip().decode('utf-8', errors='replace')
                req = json.loads(raw_req)

                # 3. Verify broker token
                req_token = req.get('broker_token') or req.get('auth', {}).get('broker_token', '')
                if peer_uid == webuzo_uid or req_token:
                    if not self.broker_token or not secrets.compare_digest(str(req_token), self.broker_token):
                        err_resp = json.dumps({'error': 'Security Refusal: Invalid or missing broker authentication token'}).encode('utf-8') + b"\n"
                        conn.sendall(err_resp)
                        return


                response = self.handler.handle_request(req)
                resp_bytes = json.dumps(response).encode('utf-8') + b"\n"
                conn.sendall(resp_bytes)
        except Exception as e:
            try:
                err_resp = json.dumps({'error': str(e)}).encode('utf-8') + b"\n"
                conn.sendall(err_resp)
            except Exception:
                pass
        finally:
            try:
                conn.close()
            except Exception:
                pass

    def start(self):
        def sig_handler(signum, frame):
            print("Shutting down UNISELV Resource Manager Agent...")
            self.running = False
            if self.server_sock:
                try:
                    self.server_sock.close()
                except Exception:
                    pass
            if os.path.exists(self.socket_path):
                try:
                    os.unlink(self.socket_path)
                except Exception:
                    pass
            if os.path.exists(TOKEN_PATH):
                try:
                    os.unlink(TOKEN_PATH)
                except Exception:
                    pass
            sys.exit(0)

        signal.signal(signal.SIGTERM, sig_handler)
        signal.signal(signal.SIGINT, sig_handler)

        try:
            os.makedirs('/dev/shm/uniselv_fpm', mode=0o1777, exist_ok=True)
            os.chmod('/dev/shm/uniselv_fpm', 0o1777)
        except Exception:
            pass

        collector_thread = threading.Thread(target=self.collector_loop, daemon=True)
        collector_thread.start()

        threading.Thread(target=self.governance_loop, daemon=True).start()
        self.run_ipc_server()

if __name__ == '__main__':
    daemon = AgentDaemon()
    daemon.start()
