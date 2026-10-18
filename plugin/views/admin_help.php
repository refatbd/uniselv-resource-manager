<?php
/**
 * UNISELV Resource Manager - Modern Admin Help & About View
 * Role-specific, searchable, responsive enterprise documentation for Webuzo Administrators.
 */
?>
<div id="tab-help" class="uniselv-tab-content">
    <!-- Help Header & Real-time Search -->
    <div class="uniselv-help-header">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 16px;">
            <div>
                <h3>UNISELV Documentation & Administrative Runbook</h3>
                <p>Comprehensive operational guidance, resource metrics breakdown, Golden Shield kernel architecture, and copyable diagnostic runbooks.</p>
            </div>
            <span class="uniselv-badge badge-normal" style="background: rgba(255,255,255,0.15); color: #fff; border: 1px solid rgba(255,255,255,0.25);">Role: Administrator</span>
        </div>
        <div class="uniselv-search-box">
            <svg class="uniselv-search-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
            </svg>
            <input type="text" id="help-search-input" placeholder="Search topics, metrics, features, commands, or scenarios..." oninput="UniselvResMan.filterHelp()">
        </div>
    </div>

    <!-- Category Filter Navigation Pills -->
    <div class="uniselv-help-cats">
        <button class="uniselv-cat-btn active" data-cat="all" onclick="UniselvResMan.setHelpCategory('all')">All Documentation</button>
        <button class="uniselv-cat-btn" data-cat="quickstart" onclick="UniselvResMan.setHelpCategory('quickstart')">Quick Start</button>
        <button class="uniselv-cat-btn" data-cat="features" onclick="UniselvResMan.setHelpCategory('features')">Feature Guide</button>
        <button class="uniselv-cat-btn" data-cat="metrics" onclick="UniselvResMan.setHelpCategory('metrics')">Resource Metrics</button>
        <button class="uniselv-cat-btn" data-cat="golden" onclick="UniselvResMan.setHelpCategory('golden')">Golden Shield Governor</button>
        <button class="uniselv-cat-btn" data-cat="scenarios" onclick="UniselvResMan.setHelpCategory('scenarios')">Practical Scenarios</button>
        <button class="uniselv-cat-btn" data-cat="trouble" onclick="UniselvResMan.setHelpCategory('trouble')">Troubleshooting & Runbook</button>
        <button class="uniselv-cat-btn" data-cat="about" onclick="UniselvResMan.setHelpCategory('about')">About & Architecture</button>
    </div>

    <!-- Documentation Articles Grid -->
    <div class="uniselv-help-grid">

        <!-- 1. QUICK START -->
        <div class="uniselv-help-card" data-cat="quickstart" id="help-topic-quickstart">
            <span class="uniselv-help-badge badge-cat-quickstart">Quick Start</span>
            <h4 class="uniselv-help-card-title">Administrative Quick Start & Verification</h4>
            <div class="uniselv-help-card-desc">
                UNISELV Resource Manager automates server-wide resource governance, real-time telemetry collection, and cgroups v2 kernel isolation for Webuzo.
            </div>
            <ol style="margin: 0 0 14px 20px; padding: 0; color: #475569; font-size: 0.9rem; line-height: 1.6;">
                <li><strong>Automatic Governance:</strong> The background agent (<code>uniselv-resman-agent.service</code>) starts automatically, collects 10-second telemetry samples, manages database retention, and validates cgroup sync.</li>
                <li><strong>Native Plan Synchronization:</strong> Click <strong>Bulk Sync All Plans</strong> at the top right to verify that all Webuzo plans are propagated into individual account slices (<code>golden-&lt;uid&gt;.slice</code>).</li>
                <li><strong>Golden Shield Safety Cap:</strong> Check the <strong>Golden Shield & Capacity</strong> tab to confirm that parent aggregate limits (<code>golden.slice</code>) are active with shared aggregate CPU headroom (e.g. 340% hosting + 60% system headroom on 4 vCPUs).</li>
            </ol>
            <div class="uniselv-code-block">
                <code>systemctl status uniselv-resman-agent --no-pager</code>
                <button class="uniselv-copy-btn" onclick="UniselvResMan.copyToClipboard('systemctl status uniselv-resman-agent --no-pager', this)">Copy</button>
            </div>
        </div>

        <!-- 2. SERVER OVERVIEW FEATURE -->
        <div class="uniselv-help-card" data-cat="features" id="help-topic-overview">
            <span class="uniselv-help-badge badge-cat-features">Features</span>
            <h4 class="uniselv-help-card-title">Server Overview & Top Consumers Dashboard</h4>
            <div class="uniselv-help-card-desc">
                <strong>What it does:</strong> Provides instant visual telemetry of physical hardware, aggregate shared headroom, active RAM safety budget, 1m/5m/15m system loads, and live ranking of the top consuming hosting accounts.<br>
                <strong>Menu:</strong> <em>Server Overview</em> tab.<br>
                <strong>Prerequisites:</strong> Active background agent daemon.<br>
                <strong>Usage Steps:</strong>
                <ol style="margin: 6px 0 10px 20px; padding: 0;">
                    <li>Review the hardware detection card for accurate physical core and RAM readings.</li>
                    <li>Inspect the <strong>Top Resource Consumers</strong> table to spot accounts approaching 100% of their CPU allowance or suffering throttling.</li>
                    <li>Click <strong>Grant Boost</strong> to provide temporary emergency headroom to any account experiencing a traffic spike.</li>
                </ol>
                <strong>Expected Result:</strong> Real-time animated telemetry updates with zero browser lag.
            </div>
        </div>

        <!-- 3. ALL ACCOUNTS & TEMPORARY BOOST -->
        <div class="uniselv-help-card" data-cat="features" id="help-topic-accounts">
            <span class="uniselv-help-badge badge-cat-features">Features</span>
            <h4 class="uniselv-help-card-title">All Accounts Directory & Temporary Resource Boost</h4>
            <div class="uniselv-help-card-desc">
                <strong>What it does:</strong> Comprehensive inventory of all Webuzo accounts showing assigned plan, core-equivalent CPU %, allowance utilization %, memory footprint, task counts, and throttling incidents. Allows granting temporary plan upgrades that expire cleanly.<br>
                <strong>Menu:</strong> <em>All Accounts</em> tab.<br>
                <strong>Realistic Example:</strong> An e-commerce customer runs a flash sale and their site begins throwing 503 errors due to task exhaustion. An administrator grants a <strong>Turbo</strong> boost (200% CPU, 3072M RAM) for 120 minutes. The agent dynamically reconfigures the slice without touching permanent billing plans, and cleanly restores the original plan upon expiration.<br>
                <strong>Reversal Steps:</strong> To cancel early, open the modal and select cancel, or wait for the timer to expire automatically.
            </div>
        </div>

        <!-- 4. CONFIGURED VS EFFECTIVE AUDIT -->
        <div class="uniselv-help-card" data-cat="features" id="help-topic-audit">
            <span class="uniselv-help-badge badge-cat-features">Features</span>
            <h4 class="uniselv-help-card-title">Configured vs Effective Kernel Limit Audit</h4>
            <div class="uniselv-help-card-desc">
                <strong>What it does:</strong> Rigorously audits every configured Webuzo plan limit against actual kernel cgroup v2 parameters. A customer slice is only labeled <strong>SYNCHRONIZED</strong> if all six criteria match:<br>
                1. <code>cpu.max</code> numerical quota matches plan CPUQuota.<br>
                2. <code>memory.max</code> matches plan configured memory ceiling.<br>
                3. <code>memory.high</code> matches plan memory warning threshold.<br>
                4. <code>memory.swap.max</code> is strictly enforced to 0 bytes.<br>
                5. <code>pids.max</code> matches plan maxtask.<br>
                6. <strong>Ancestor Slice:</strong> The slice is strictly located inside <code>/sys/fs/cgroup/golden.slice/</code>.<br>
                <strong>Menu:</strong> <em>Configured vs Effective Audit</em> tab.<br>
                <strong>Action:</strong> If any slice shows <em>MISCONFIGURED</em>, click <strong>Bulk Sync All Plans</strong> to reconcile immediately.
            </div>
        </div>

        <!-- 5. RESOURCE METRICS EXPLAINED -->
        <div class="uniselv-help-card" data-cat="metrics" id="help-topic-metrics">
            <span class="uniselv-help-badge badge-cat-metrics">Resource Metrics</span>
            <h4 class="uniselv-help-card-title">Resource Metrics & Allowance Mathematics</h4>
            <div class="uniselv-help-card-desc">
                <strong>1. CPU % (Core Equivalent):</strong> 100% CPU equals exactly one full physical CPU core. On a 4 vCPU server, 400% represents total machine capacity.<br>
                <strong>Allowance Percentage Example:</strong> If an account is assigned a 200% CPU quota (2 cores) and consumes 150% CPU, its allowance usage is:
                <div style="background:#f1f5f9; padding:8px 12px; border-radius:6px; margin:6px 0; font-family:monospace; font-size:0.85rem;">
                    Allowance Used = (150% Actual / 200% Quota) * 100 = 75.0%
                </div>
                <strong>2. Memory Breakdown (Anon vs Cache vs Swap):</strong>
                <ul style="margin:6px 0 6px 20px; padding:0;">
                    <li><strong>Anonymous (RSS):</strong> Real application code, PHP-FPM variables, opcache, and MySQL query buffers. Cannot be freed without terminating workers.</li>
                    <li><strong>File Page Cache:</strong> Cached disk files managed by Linux. Automatically reclaimed under pressure; does not trigger OOM.</li>
                    <li><strong>Swap Max = 0:</strong> Strict zero swap enforcement prevents VPS disk thrashing and protects NVMe performance.</li>
                </ul>
                <strong>3. Tasks / PIDs (<code>pids.max</code>):</strong> Maximum concurrent threads, PHP-FPM workers, and background subprocesses permitted in the slice. Prevents fork bombs.<br>
                <strong>4. Throttling Events (<code>nr_throttled</code>):</strong> Number of 100ms quota periods where the CFS scheduler paused execution because the account exceeded its quota.<br>
                <strong>5. OOM Kills (<code>oom_kill</code>):</strong> Number of processes terminated by kernel because total slice memory breached <code>memory.max</code>.
            </div>
        </div>

        <!-- 6. GOLDEN SHIELD ARCHITECTURE & RESTORE -->
        <div class="uniselv-help-card" data-cat="golden" id="help-topic-golden">
            <span class="uniselv-help-badge badge-cat-golden">Golden Shield</span>
            <h4 class="uniselv-help-card-title">Golden Shield Governor Architecture & Transactional Backups</h4>
            <div class="uniselv-help-card-desc">
                <strong>Shared Aggregate Headroom Model:</strong> Rather than isolating a dedicated physical CPU core (which wastes idle capacity), Golden Shield enforces a shared aggregate headroom model across all CPU cores.<br>
                <strong>4 vCPU Sizing Example:</strong>
                <ul style="margin:4px 0 6px 20px; padding:0;">
                    <li>Total Physical Capacity: 400% CPU</li>
                    <li>Hosting Pool Quota (<code>golden.slice</code>): <strong>340%</strong> (85%)</li>
                    <li>System & Emergency Headroom: <strong>60%</strong> (15% reserved for SSH, Webuzo Admin, Cron)</li>
                </ul>
                <strong>8 vCPU Sizing Example:</strong>
                <ul style="margin:4px 0 6px 20px; padding:0;">
                    <li>Total Physical Capacity: 800% CPU</li>
                    <li>Hosting Pool Quota: <strong>680%</strong> (85%)</li>
                    <li>System Headroom: <strong>120%</strong> (15%)</li>
                </ul>
                <strong>Reboot Persistence:</strong> Drop-in file at <code>/etc/systemd/system/golden.slice.d/50-uniselv-limits.conf</code> stores limits for reboots and systemd reloads; verify effective limits after maintenance.<br>
                <strong>Transactional Backups & Safe Restore:</strong> Before every policy modification, a timestamped backup is saved to <code>/var/lib/uniselv-resource-manager/golden-backups/</code>. When restoring, the manager validates schema integrity, sets drop-in limits, reloads systemd, and attempts a bounded rollback if live kernel verification fails. A failed rollback is reported as inconsistent and requires recovery review.<br>
                <strong>Zero Fabricated Fallbacks:</strong> Hardware detection fails closed (RuntimeError) if physical metrics cannot be determined, preventing unsafe fabricated assumptions.
            </div>
            <div class="uniselv-code-block">
                <code>python3 /usr/local/sbin/golden-shield.py check</code>
                <button class="uniselv-copy-btn" onclick="UniselvResMan.copyToClipboard('python3 /usr/local/sbin/golden-shield.py check', this)">Copy</button>
            </div>
        </div>

        <div class="uniselv-help-card" data-cat="golden" id="help-topic-installation-ownership">
            <span class="uniselv-help-badge badge-cat-golden">Maintenance</span>
            <h4 class="uniselv-help-card-title">Installation, Deactivation and Ownership</h4>
            <div class="uniselv-help-card-desc">
                <strong>Installation:</strong> Activation installs missing bundled isolation, Golden Shield and session protection dependencies on a supported native layout, then checks effective protection. Unsupported or changed integrations stop activation and retain recovery files.<br>
                <strong>Deactivation:</strong> Pauses plugin monitoring and restores its PHP tracker settings. Existing kernel isolation remains active.<br>
                <strong>Uninstallation:</strong> Restores protection components installed by this plugin. Previously adopted integrations remain installed. Changed files or failed restoration block cleanup rather than reporting success.<br>
                <strong>Recovery:</strong> Keep the installation backup and ownership records. If a lifecycle action fails, read the reported error and verify services before retrying. Do not delete recovery manifests to bypass a failure. Existing-server lifecycle evidence does not certify every fresh operating-system or vendor layout.
            </div>
        </div>

        <div class="uniselv-help-card" data-cat="features" id="help-topic-live-refresh">
            <span class="uniselv-help-badge">Monitoring</span>
            <h4 class="uniselv-help-card-title">Efficient Live Updates</h4>
            <div class="uniselv-help-card-desc">
                Server Overview and the customer dashboard refresh every 10 seconds while active. The displayed sample age comes from the server, not a simulated timer. A hidden page does not start automatic telemetry requests.<br>
                Modern secure browsers can reuse a fresh read-only sample across pages with the same login, account and role. This uses a session-scoped in-memory channel and Web Locks; tokens and telemetry are not written to persistent browser storage. Unsupported browsers retain local caching and prevent overlapping requests.<br>
                Telemetry requests time out after 15 seconds where fetch cancellation is supported. Failed connections retry with a delay of 10, 20, 40, then 60 seconds. Last displayed values remain visible with an unavailable indication. Permission changes and other actions are sent directly and are never shared or cached by this mechanism.<br>
                Example: opening two Server Overview pages in the same authenticated session can reuse one fresh sample instead of sending identical refresh requests. Closing a tab releases its coordination resources. Server collection, kernel limits and protection checks continue independently.
            </div>
        </div>

        <!-- 7. HARDWARE CHANGE RECONCILIATION -->
        <div class="uniselv-help-card" data-cat="golden" id="help-topic-hardware">
            <span class="uniselv-help-badge badge-cat-golden">Golden Shield</span>
            <h4 class="uniselv-help-card-title">Hardware Change Reconciliation (VPS Resizing)</h4>
            <div class="uniselv-help-card-desc">
                When a VPS is upgraded or downgraded in the cloud console (e.g. 4 vCPUs -> 8 vCPUs, or 8 GiB -> 16 GiB RAM), UNISELV Resource Manager checks for changed capacity:<br>
                <strong>Auto Mode:</strong> The background agent detects the hardware capacity change, automatically recalculates hosting pool quotas and memory safety budgets, writes persistent drop-in configs, and applies verified limits. The detected hardware record is updated only after a successful reconciliation.<br>
                <strong>Manual Mode:</strong> If custom administrator overrides are active, the reconciler preserves your manual limits and issues an administrative warning so you must review sizing. Before a downgrade, reduce manual limits to fit the new physical capacity and its reserve. Actual VPS resizing has not been exercised on this validation host.<br>
                <strong>Governance Mode Persistence:</strong> Mode is stored in <code>/etc/golden-shield/mode.json</code>. Manual overrides cannot exceed the current Auto hosting CPU/RAM safety budgets.
            </div>
        </div>

        <!-- 8. PRACTICAL SCENARIOS -->
        <div class="uniselv-help-card" data-cat="scenarios" id="help-topic-scenarios">
            <span class="uniselv-help-badge badge-cat-scenarios">Practical Scenarios</span>
            <h4 class="uniselv-help-card-title">Administrative Scenarios & Step-by-Step Runbooks</h4>
            <div class="uniselv-help-card-desc">
                <strong>Scenario 1: Customer Site Throwing 503 / 504 Gateway Errors:</strong>
                <ol style="margin:6px 0 10px 20px; padding:0;">
                    <li>Open <em>All Accounts</em> tab and check customer’s active tasks vs maximum task limit.</li>
                    <li>If tasks are exhausted, navigate to Enduser view or use SSH to identify hanging PHP-FPM workers.</li>
                    <li>Grant a temporary <strong>Turbo</strong> boost to relieve immediate congestion while debugging slow database queries.</li>
                </ol>
                <strong>Scenario 2: Investigating Rogue Process Outside Boundary:</strong>
                <ol style="margin:6px 0 10px 20px; padding:0;">
                    <li>Open <em>Golden Shield & Capacity</em> tab and check <strong>Enforcement Coverage</strong>.</li>
                    <li>If any process is detected outside <code>golden.slice</code>, note the PID and executable.</li>
                    <li>Verify whether the customer process was launched via CLI or cron outside systemd user slices.</li>
                </ol>
                <strong>Scenario 3: Rolling Back Bad Policy Settings:</strong>
                <ol style="margin:6px 0 10px 20px; padding:0;">
                    <li>Click <strong>Restore Backup</strong> in the Golden Shield Governor tab.</li>
                    <li>Select the desired configuration checkpoint from the list.</li>
                    <li>Click <strong>Restore Selected Backup</strong>. The system verifies kernel status and confirms success.</li>
                </ol>
            </div>
        </div>

        <!-- 9. TROUBLESHOOTING & DIAGNOSTIC RUNBOOK -->
        <div class="uniselv-help-card" data-cat="trouble" id="help-topic-trouble">
            <span class="uniselv-help-badge badge-cat-trouble">Troubleshooting</span>
            <h4 class="uniselv-help-card-title">Troubleshooting & Verified Diagnostic Commands</h4>
            <div class="uniselv-help-card-desc">
                Diagnostic commands for terminal verification. Click <strong>Copy</strong> to copy any command to your clipboard.
            </div>
            
            <p style="margin:8px 0 4px 0; font-weight:600; font-size:0.85rem; color:#1e293b;">1. Verify Background Daemon Status & Memory:</p>
            <div class="uniselv-code-block">
                <code>systemctl status uniselv-resman-agent</code>
                <button class="uniselv-copy-btn" onclick="UniselvResMan.copyToClipboard('systemctl status uniselv-resman-agent', this)">Copy</button>
            </div>

            <p style="margin:8px 0 4px 0; font-weight:600; font-size:0.85rem; color:#1e293b;">2. Inspect Live Daemon Logs for Reconciliation or Errors:</p>
            <div class="uniselv-code-block">
                <code>journalctl -u uniselv-resman-agent -n 50 --no-pager</code>
                <button class="uniselv-copy-btn" onclick="UniselvResMan.copyToClipboard('journalctl -u uniselv-resman-agent -n 50 --no-pager', this)">Copy</button>
            </div>

            <p style="margin:8px 0 4px 0; font-weight:600; font-size:0.85rem; color:#1e293b;">3. Verify Kernel Cgroup Slices & Limits:</p>
            <div class="uniselv-code-block">
                <code>cat /sys/fs/cgroup/golden.slice/cpu.max && cat /sys/fs/cgroup/golden.slice/memory.max</code>
                <button class="uniselv-copy-btn" onclick="UniselvResMan.copyToClipboard('cat /sys/fs/cgroup/golden.slice/cpu.max && cat /sys/fs/cgroup/golden.slice/memory.max', this)">Copy</button>
            </div>

            <p style="margin:8px 0 4px 0; font-weight:600; font-size:0.85rem; color:#1e293b;">4. Inspect Persistent Systemd Drop-in Configuration:</p>
            <div class="uniselv-code-block">
                <code>cat /etc/systemd/system/golden.slice.d/50-uniselv-limits.conf</code>
                <button class="uniselv-copy-btn" onclick="UniselvResMan.copyToClipboard('cat /etc/systemd/system/golden.slice.d/50-uniselv-limits.conf', this)">Copy</button>
            </div>

            <p style="margin:8px 0 4px 0; font-weight:600; font-size:0.85rem; color:#1e293b;">5. Execute IPC Socket Health Query Directly:</p>
            <div class="uniselv-code-block">
                <code>python3 -c "import socket; s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM); s.connect('/run/uniselv-resman/agent.sock'); s.send(b'{\"action\":\"get_agent_health\"}\\n'); print(s.recv(4096).decode())"</code>
                <button class="uniselv-copy-btn" onclick="UniselvResMan.copyToClipboard('python3 -c &quot;import socket; s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM); s.connect(\'/run/uniselv-resman/agent.sock\'); s.send(b\'{\\\&quot;action\\\&quot;:\\\&quot;get_agent_health\\\&quot;}\\n\'); print(s.recv(4096).decode())&quot;', this)">Copy</button>
            </div>
        </div>

        <!-- 10. ABOUT & COMPATIBILITY -->
        <div class="uniselv-help-card" data-cat="about" id="help-topic-about">
            <span class="uniselv-help-badge badge-cat-about">About</span>
            <h4 class="uniselv-help-card-title">About UNISELV Resource Manager & System Compatibility</h4>
            <div class="uniselv-help-card-desc">
                <table style="width:100%; border-collapse:collapse; font-size:0.88rem; color:#334155;">
                    <tr style="border-bottom:1px solid #f1f5f9;"><td style="padding:6px 0; font-weight:600; width:220px;">Plugin Version:</td><td>1.1.13 — see bundled docs/FRONTEND-OPTIMIZATION-1.1.13.md and docs/LIFECYCLE-REVIEW-1.1.12.md for tested scope and docs/apache-fcgi-integration.md for automatic Apache integration and rollback.</td></tr>
                    <tr style="border-bottom:1px solid #f1f5f9;"><td style="padding:6px 0; font-weight:600;">Host Operating System:</td><td>Ubuntu 24.04.5 LTS (Noble Numbat)</td></tr>
                    <tr style="border-bottom:1px solid #f1f5f9;"><td style="padding:6px 0; font-weight:600;">Active Linux Kernel:</td><td>6.8.0-147-generic (x86_64)</td></tr>
                    <tr style="border-bottom:1px solid #f1f5f9;"><td style="padding:6px 0; font-weight:600;">Control Panel:</td><td>Webuzo 4.8.4 Enterprise</td></tr>
                    <tr style="border-bottom:1px solid #f1f5f9;"><td style="padding:6px 0; font-weight:600;">Cgroups Implementation:</td><td>Cgroups v2 Unified Hierarchy (<code>/sys/fs/cgroup</code>)</td></tr>
                    <tr style="border-bottom:1px solid #f1f5f9;"><td style="padding:6px 0; font-weight:600;">Process Safety:</td><td>Zero-race <code>os.pidfd_open</code> signal delivery</td></tr>
                    <tr style="border-bottom:1px solid #f1f5f9;"><td style="padding:6px 0; font-weight:600;">Ownership Manifest:</td><td><code>/var/lib/uniselv-resource-manager/ownership_manifest.json</code></td></tr>
                    <tr><td style="padding:6px 0; font-weight:600;">Developer:</td><td><strong>Refat Rahman</strong> (<a href="https://refat.ovh" target="_blank" style="color:var(--uniselv-primary); text-decoration:none; font-weight:600;">refat.ovh</a>)</td></tr>
                </table>
            </div>
        </div>

        <!-- 11. DEVELOPER PROFILE -->
        <div class="uniselv-help-card" data-cat="about" id="help-topic-developer" style="border-top: 3px solid #2563eb;">
            <span class="uniselv-help-badge badge-cat-about">Developer Info</span>
            <h4 class="uniselv-help-card-title">Lead Developer & Systems Architect</h4>
            <div class="uniselv-help-card-desc">
                <div style="display: flex; gap: 16px; align-items: flex-start; margin-bottom: 14px;">
                    <div style="width: 48px; height: 48px; border-radius: 50%; background: linear-gradient(135deg, #2563eb, #1d4ed8); display: flex; align-items: center; justify-content: center; color: #fff; font-weight: 700; font-size: 1.2rem; flex-shrink: 0; box-shadow: 0 4px 6px rgba(37,99,235,0.25);">RR</div>
                    <div>
                        <h5 style="margin: 0 0 4px 0; font-weight: 700; color: #1e293b; font-size: 1.05rem;">Refat Rahman</h5>
                        <p style="margin: 0; font-size: 0.85rem; color: #64748b;">Full-Stack Engineer, Linux Systems Specialist & Extension Developer</p>
                    </div>
                </div>
                <p style="font-size: 0.88rem; color: #475569; margin-bottom: 16px; line-height: 1.5;">
                    Specialized in enterprise web hosting automation, Linux kernel containerization (cgroups v2), high-concurrency microservices, and Webuzo ecosystem integration.
                </p>
                <div style="display: flex; flex-direction: column; gap: 8px; font-size: 0.88rem;">
                    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #f1f5f9; padding-bottom: 6px;">
                        <span style="font-weight: 600; color: #475569;">Website:</span>
                        <a href="https://refat.ovh" target="_blank" style="color: #2563eb; font-weight: 600; text-decoration: none;">refat.ovh</a>
                    </div>
                    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #f1f5f9; padding-bottom: 6px;">
                        <span style="font-weight: 600; color: #475569;">GitHub:</span>
                        <a href="https://github.com/refatbd" target="_blank" style="color: #1e293b; font-weight: 600; text-decoration: none;">github.com/refatbd</a>
                    </div>
                    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #f1f5f9; padding-bottom: 6px;">
                        <span style="font-weight: 600; color: #475569;">Telegram:</span>
                        <a href="https://t.me/refatbd" target="_blank" style="color: #0284c7; font-weight: 600; text-decoration: none;">t.me/refatbd</a>
                    </div>
                    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #f1f5f9; padding-bottom: 6px;">
                        <span style="font-weight: 600; color: #475569;">Facebook:</span>
                        <a href="https://www.facebook.com/rjrefat/" target="_blank" style="color: #1877f2; font-weight: 600; text-decoration: none;">facebook.com/rjrefat</a>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="font-weight: 600; color: #475569;">Instagram:</span>
                        <a href="https://www.instagram.com/refat_official" target="_blank" style="color: #e1306c; font-weight: 600; text-decoration: none;">instagram.com/refat_official</a>
                    </div>
                </div>
            </div>
        </div>

    </div>
</div>
