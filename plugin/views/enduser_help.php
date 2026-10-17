<?php
/**
 * UNISELV Resource Manager - Modern Enduser Help & About View
 * Role-specific, searchable, responsive documentation tailored for Webuzo hosting customers.
 */
?>
<div id="tab-help" class="uniselv-tab-content">
    <!-- Help Header & Real-time Search -->
    <div class="uniselv-help-header">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 16px;">
            <div>
                <h3>Resource Usage & Performance Guide</h3>
                <p>Learn how your hosting resources are measured, how to identify bottlenecks, optimize script execution, and resolve traffic spikes.</p>
            </div>
            <span class="uniselv-badge badge-normal" style="background: rgba(255,255,255,0.15); color: #fff; border: 1px solid rgba(255,255,255,0.25);">Role: Hosting Customer</span>
        </div>
        <div class="uniselv-search-box">
            <svg class="uniselv-search-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
            </svg>
            <input type="text" id="help-search-input" placeholder="Search topics, metrics, features, or troubleshooting tips..." oninput="UniselvResMan.filterHelp()">
        </div>
    </div>

    <!-- Category Filter Navigation Pills -->
    <div class="uniselv-help-cats">
        <button class="uniselv-cat-btn active" data-cat="all" onclick="UniselvResMan.setHelpCategory('all')">All Documentation</button>
        <button class="uniselv-cat-btn" data-cat="quickstart" onclick="UniselvResMan.setHelpCategory('quickstart')">Getting Started</button>
        <button class="uniselv-cat-btn" data-cat="features" onclick="UniselvResMan.setHelpCategory('features')">Features & Tools</button>
        <button class="uniselv-cat-btn" data-cat="metrics" onclick="UniselvResMan.setHelpCategory('metrics')">Understanding Metrics</button>
        <button class="uniselv-cat-btn" data-cat="scenarios" onclick="UniselvResMan.setHelpCategory('scenarios')">Practical Guides</button>
        <button class="uniselv-cat-btn" data-cat="trouble" onclick="UniselvResMan.setHelpCategory('trouble')">FAQ & Diagnostics</button>
        <button class="uniselv-cat-btn" data-cat="about" onclick="UniselvResMan.setHelpCategory('about')">About Your Environment</button>
    </div>

    <!-- Documentation Articles Grid -->
    <div class="uniselv-help-grid">

        <!-- 1. QUICK START -->
        <div class="uniselv-help-card" data-cat="quickstart" id="help-topic-quickstart">
            <span class="uniselv-help-badge badge-cat-quickstart">Getting Started</span>
            <h4 class="uniselv-help-card-title">Quick Start: Monitoring Your Account Performance</h4>
            <div class="uniselv-help-card-desc">
                Your hosting account operates in an isolated environment with dedicated allocations for CPU, physical memory, disk bandwidth, and concurrent tasks.<br>
                <ol style="margin: 8px 0 10px 20px; padding: 0; line-height: 1.6;">
                    <li><strong>Real-Time Gauges:</strong> The <em>Dashboard</em> refreshes every 3 seconds, showing current resource consumption with animated sparklines.</li>
                    <li><strong>Color Status Indicators:</strong>
                        <ul style="margin:4px 0 6px 16px; padding:0;">
                            <li><span class="uniselv-badge badge-normal" style="margin-right:6px;">NORMAL</span> Usage is safely within plan thresholds.</li>
                            <li><span class="uniselv-badge badge-warning" style="margin-right:6px;">ELEVATED</span> Usage has exceeded 60% of capacity.</li>
                            <li><span class="uniselv-badge badge-critical" style="margin-right:6px;">LIMIT EXCEEDED</span> Usage has reached plan limits; script execution may be throttled.</li>
                        </ul>
                    </li>
                    <li><strong>Investigating Spikes:</strong> Switch to the <em>Historical Charts</em> tab to identify exactly when spikes occurred over 1 hour, 24 hours, or 30 days.</li>
                </ol>
            </div>
        </div>

        <!-- 2. FEATURES & TOOLS -->
        <div class="uniselv-help-card" data-cat="features" id="help-topic-dashboard">
            <span class="uniselv-help-badge badge-cat-features">Features</span>
            <h4 class="uniselv-help-card-title">Live Resource Dashboard & Sparklines</h4>
            <div class="uniselv-help-card-desc">
                <strong>What it does:</strong> Displays live meters for CPU, Memory, Active Tasks, and Disk I/O along with 5-minute animated trend sparklines.<br>
                <strong>Menu:</strong> <em>Dashboard</em> tab.<br>
                <strong>Key Details:</strong> Displays your core equivalent alongside percentage utilization, ensuring you always know how many CPU cores your application is utilizing.
            </div>
        </div>

        <div class="uniselv-help-card" data-cat="features" id="help-topic-processes">
            <span class="uniselv-help-badge badge-cat-features">Features</span>
            <h4 class="uniselv-help-card-title">Process Manager & Safe Script Termination</h4>
            <div class="uniselv-help-card-desc">
                <strong>What it does:</strong> Shows all active PHP-FPM web workers, cron scripts, and CLI processes currently executing inside your account boundary.<br>
                <strong>Menu:</strong> <em>Current Usage & Processes</em> tab.<br>
                <strong>Terminating a Process:</strong> If a script is hanging or looping infinitely, click <strong>Stop Process</strong> next to the process entry. UNISELV securely verifies ownership before terminating only the targeted PID, preventing accidental disruption of other visitors.
            </div>
        </div>

        <div class="uniselv-help-card" data-cat="features" id="help-topic-snapshots">
            <span class="uniselv-help-badge badge-cat-features">Features</span>
            <h4 class="uniselv-help-card-title">Diagnostic Incident Snapshots</h4>
            <div class="uniselv-help-card-desc">
                <strong>What it does:</strong> Whenever your account experiences high resource pressure (such as reaching 90% CPU allowance or task limit exhaustion), the system automatically captures a diagnostic snapshot.<br>
                <strong>Menu:</strong> <em>Snapshots</em> tab.<br>
                <strong>How to use:</strong> Click <strong>Inspect</strong> on any snapshot to view the exact process command lines, execution state, and memory consumption at the time of the event.
            </div>
        </div>

        <div class="uniselv-help-card" data-cat="features" id="help-topic-export">
            <span class="uniselv-help-badge badge-cat-features">Features</span>
            <h4 class="uniselv-help-card-title">Export Support Diagnostic Report</h4>
            <div class="uniselv-help-card-desc">
                <strong>What it does:</strong> Generates a comprehensive, downloadable JSON diagnostics file containing your account’s recent resource history, limits, incidents, and process details.<br>
                <strong>Usage:</strong> Click the <strong>Export Support Report</strong> button in the top right header. You can attach this report when opening a support ticket with your hosting provider or sharing performance data with your web developers.
            </div>
        </div>

        <!-- 3. UNDERSTANDING METRICS -->
        <div class="uniselv-help-card" data-cat="metrics" id="help-topic-metrics">
            <span class="uniselv-help-badge badge-cat-metrics">Resource Metrics</span>
            <h4 class="uniselv-help-card-title">Understanding Resource Metrics & Math</h4>
            <div class="uniselv-help-card-desc">
                <strong>1. CPU % (Core Equivalent):</strong> 100% CPU represents one full physical CPU core. If your plan has a 100% CPU quota and uses 50%, you are using 0.5 cores. If your plan has a 200% CPU quota (2 cores) and consumes 150%, you are utilizing 1.5 cores (which represents 75% of your allowance).<br>
                <strong>2. Memory (Anonymous vs Cache):</strong>
                <ul style="margin:4px 0 6px 16px; padding:0;">
                    <li><strong>Physical Memory (RAM):</strong> Consumed by your active PHP code, WordPress plugins, and opcache.</li>
                    <li><strong>Page Cache:</strong> Temporary disk reads stored by the operating system. Cache is harmless and freed automatically when your application requires more memory.</li>
                    <li><strong>Zero Swap:</strong> The hosting environment enforces zero swap to prevent disk latency from slowing down your website.</li>
                </ul>
                <strong>3. Active Tasks (Processes):</strong> The number of concurrent requests being handled by your website. If tasks reach your plan's maximum, incoming requests may temporarily queue or return 503 errors.<br>
                <strong>4. Disk I/O Throughput:</strong> The volume of data read from or written to high-speed NVMe storage per second.
            </div>
        </div>

        <!-- 4. PRACTICAL GUIDES -->
        <div class="uniselv-help-card" data-cat="scenarios" id="help-topic-scenarios">
            <span class="uniselv-help-badge badge-cat-scenarios">Practical Guides</span>
            <h4 class="uniselv-help-card-title">Practical Troubleshooting Scenarios</h4>
            <div class="uniselv-help-card-desc">
                <strong>Scenario 1: My website is loading slowly or freezing:</strong>
                <ol style="margin:6px 0 10px 20px; padding:0;">
                    <li>Check the <strong>CPU Usage</strong> gauge on the Dashboard. If it shows <em>ELEVATED</em> or <em>LIMIT EXCEEDED</em>, your site is using all available processing time.</li>
                    <li>Navigate to the <strong>Processes</strong> tab to check if a specific script (like a backup plugin, import tool, or scraper) is consuming CPU.</li>
                    <li>If an unwanted background script is stuck, click <strong>Stop Process</strong> to terminate it.</li>
                </ol>
                <strong>Scenario 2: Visitors are seeing "503 Service Unavailable" or "Resource Limit Reached":</strong>
                <ol style="margin:6px 0 10px 20px; padding:0;">
                    <li>Check the <strong>Active Tasks</strong> gauge on the Dashboard.</li>
                    <li>If tasks are at 100%, your web workers are saturated. Check the <strong>Notifications</strong> tab to review task exhaustion events.</li>
                    <li>Consider enabling server-side caching (e.g. OPcache, Redis, or Nginx microcaching) to reduce the number of dynamic PHP workers required per page view.</li>
                </ol>
                <strong>Scenario 3: Preparing for a large marketing event or product launch:</strong>
                <ol style="margin:6px 0 10px 20px; padding:0;">
                    <li>Export your support report via the <strong>Export Support Report</strong> button.</li>
                    <li>Contact your hosting administrator to request a temporary <strong>Turbo</strong> or <strong>Enterprise</strong> resource boost for the duration of the campaign.</li>
                </ol>
            </div>
        </div>

        <!-- 5. FAQ & DIAGNOSTICS -->
        <div class="uniselv-help-card" data-cat="trouble" id="help-topic-trouble">
            <span class="uniselv-help-badge badge-cat-trouble">FAQ & Diagnostics</span>
            <h4 class="uniselv-help-card-title">Frequently Asked Questions (FAQ)</h4>
            <div class="uniselv-help-card-desc">
                <p><strong>Q: Why does my CPU usage drop to 0% right after loading my website?</strong><br>
                A: Web server requests typically execute in 100–300 milliseconds. Once the page is sent to the browser, the PHP worker sleeps, and CPU usage naturally drops to 0%.</p>

                <p><strong>Q: What happens if my script exceeds the memory limit?</strong><br>
                A: The Linux kernel will terminate the specific worker process that breached the memory ceiling to preserve the stability of your other processes. This event is recorded in your <em>Notifications</em> tab as an Out-Of-Memory (OOM) event.</p>

                <p><strong>Q: Is it safe to stop a process?</strong><br>
                A: Yes. Stopping a web worker terminates only that specific HTTP request or background task. Database integrity is protected by MariaDB/MySQL transactions.</p>
            </div>
        </div>

        <!-- 6. ABOUT YOUR ENVIRONMENT -->
        <div class="uniselv-help-card" data-cat="about" id="help-topic-about">
            <span class="uniselv-help-badge badge-cat-about">About</span>
            <h4 class="uniselv-help-card-title">About Your Hosting Environment</h4>
            <div class="uniselv-help-card-desc">
                Your account is hosted on high-performance cloud infrastructure utilizing Linux <strong>Cgroups v2</strong> kernel containerization.<br>
                This ensures complete resource isolation: activities or traffic spikes occurring on other accounts on the server cannot affect your site's performance or allocated resources.<br>
                For questions regarding your plan allocation or upgrading your limits, contact your hosting provider.
            </div>
        </div>

        <!-- 7. DEVELOPER INFORMATION -->
        <div class="uniselv-help-card" data-cat="about" id="help-topic-developer" style="border-top: 3px solid #2563eb;">
            <span class="uniselv-help-badge badge-cat-about">Developer Info</span>
            <h4 class="uniselv-help-card-title">Developer & Technology Partner</h4>
            <div class="uniselv-help-card-desc">
                <div style="display: flex; gap: 14px; align-items: center; margin-bottom: 12px;">
                    <div style="width: 42px; height: 42px; border-radius: 50%; background: linear-gradient(135deg, #2563eb, #1d4ed8); display: flex; align-items: center; justify-content: center; color: #fff; font-weight: 700; font-size: 1.1rem; flex-shrink: 0;">RR</div>
                    <div>
                        <h5 style="margin: 0 0 2px 0; font-weight: 700; color: #1e293b;">Refat Rahman</h5>
                        <p style="margin: 0; font-size: 0.82rem; color: #64748b;">Systems Architect • <a href="https://refat.ovh" target="_blank" style="color: #2563eb; text-decoration: none; font-weight: 600;">refat.ovh</a></p>
                    </div>
                </div>
                <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                    <a href="https://github.com/refatbd" target="_blank" style="padding: 4px 10px; border-radius: 6px; background: #f8fafc; border: 1px solid #e2e8f0; color: #1e293b; font-size: 0.8rem; font-weight: 600; text-decoration: none;">GitHub</a>
                    <a href="https://t.me/refatbd" target="_blank" style="padding: 4px 10px; border-radius: 6px; background: #f8fafc; border: 1px solid #e2e8f0; color: #0284c7; font-size: 0.8rem; font-weight: 600; text-decoration: none;">Telegram</a>
                    <a href="https://www.facebook.com/rjrefat/" target="_blank" style="padding: 4px 10px; border-radius: 6px; background: #f8fafc; border: 1px solid #e2e8f0; color: #1877f2; font-size: 0.8rem; font-weight: 600; text-decoration: none;">Facebook</a>
                    <a href="https://www.instagram.com/refat_official" target="_blank" style="padding: 4px 10px; border-radius: 6px; background: #f8fafc; border: 1px solid #e2e8f0; color: #e1306c; font-size: 0.8rem; font-weight: 600; text-decoration: none;">Instagram</a>
                </div>
            </div>
        </div>

    </div>
</div>
