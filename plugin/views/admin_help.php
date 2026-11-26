<?php
/**
 * UNISELV Resource Manager - Modern Admin Help & About View
 * Role-specific, searchable, responsive enterprise documentation for Webuzo Administrators.
 */
$uniselvHelpInfo = json_decode(file_get_contents(__DIR__ . '/../info.json'), true) ?: [];
$uniselvHelpOs = @parse_ini_file('/etc/os-release', false, INI_SCANNER_RAW) ?: [];
$uniselvHelpEscape = static function($value) { return htmlspecialchars((string)$value, ENT_QUOTES, 'UTF-8'); };
$uniselvHelpVersion = $uniselvHelpInfo['version'] ?? 'Unavailable';
$uniselvHelpPanel = isset($globals['version']) && is_scalar($globals['version']) ? $globals['version'] : 'Read the current Webuzo panel header';
$uniselvPhpBranches = [];
foreach ((array)@glob('/usr/local/apps/php*/bin/php') as $_uPhpBin) {
    if (preg_match('#/apps/(php\d{2,3})/bin/php$#', (string)$_uPhpBin, $_uM) && @is_executable($_uPhpBin)) {
        $_uBr = $_uM[1];
        $_uHasOsw = @file_exists("/usr/local/apps/{$_uBr}/ext/openswoole.so") || @file_exists("/usr/local/apps/{$_uBr}/etc/php.d/openswoole.ini");
        $uniselvPhpBranches[] = strtoupper($_uBr) . ($_uHasOsw ? ' (OpenSwoole)' : '');
    }
}
sort($uniselvPhpBranches);
$uniselvComposerPath = @is_executable('/usr/local/bin/composer') ? '/usr/local/bin/composer' : (@is_executable('/usr/bin/composer') ? '/usr/bin/composer' : 'Not installed globally');
$uniselvSystemdRunOk = @is_executable('/usr/bin/systemd-run') || @is_executable('/bin/systemd-run');
$uniselvAgentMemoryCap = 'MemoryHigh=192M / MemoryMax=256M';
$_uSvcFile = '/etc/systemd/system/uniselv-resman-agent.service';
if (@is_file($_uSvcFile) && @is_readable($_uSvcFile)) {
    $_uSvcTxt = (string)@file_get_contents($_uSvcFile);
    if (preg_match('/^MemoryHigh=([^\r\n]+)/m', $_uSvcTxt, $_uMh) && preg_match('/^MemoryMax=([^\r\n]+)/m', $_uSvcTxt, $_uMm)) {
        $uniselvAgentMemoryCap = 'MemoryHigh=' . trim($_uMh[1]) . ' / MemoryMax=' . trim($_uMm[1]);
    }
}
$uniselvReadOptionalDoc = static function(string $relPath): string {
    $fullPath = __DIR__ . '/../' . ltrim($relPath, '/');
    if (!@is_file($fullPath) || !@is_readable($fullPath)) {
        return 'Reference document (' . basename($relPath) . ') is excluded from minimal release ZIP packages; see docs/ in the source repository.';
    }
    $content = @file_get_contents($fullPath);
    return is_string($content) && $content !== '' ? $content : 'Reference document unavailable.';
};
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
        <button class="uniselv-cat-btn" data-cat="platform" onclick="UniselvResMan.setHelpCategory('platform')">OpenSwoole &amp; Platform</button>
        <button class="uniselv-cat-btn" data-cat="metrics" onclick="UniselvResMan.setHelpCategory('metrics')">Resource Metrics</button>
        <button class="uniselv-cat-btn" data-cat="golden" onclick="UniselvResMan.setHelpCategory('golden')">Golden Shield Governor</button>
        <button class="uniselv-cat-btn" data-cat="scenarios" onclick="UniselvResMan.setHelpCategory('scenarios')">Practical Scenarios</button>
        <button class="uniselv-cat-btn" data-cat="trouble" onclick="UniselvResMan.setHelpCategory('trouble')">Troubleshooting &amp; Runbook</button>
        <button class="uniselv-cat-btn" data-cat="about" onclick="UniselvResMan.setHelpCategory('about')">About &amp; Architecture</button>
    </div>

    <!-- Documentation Articles Grid -->
    <div class="uniselv-help-grid">
        <!-- OPENSWOOLE GOVERNANCE & PHP RUNTIME SELF-HEALING -->
        <div class="uniselv-help-card" data-cat="platform" id="help-topic-openswoole">
            <span class="uniselv-help-badge badge-cat-features">OpenSwoole &amp; PHP Hygiene</span>
            <h4 class="uniselv-help-card-title">Multi-PHP OpenSwoole Installer, Symlink Sync &amp; INI Self-Healing</h4>
            <div class="uniselv-help-card-desc">
                <strong>Menu:</strong> <em>OpenSwoole</em> &amp; <em>System &amp; Agent Health</em> tabs.<br>
                <strong>What it does:</strong> Automates OpenSwoole extension provisioning across all installed Webuzo PHP branches (<code>php74</code>–<code>php84+</code>), enforces account resource fairness on long-lived coroutine/Octane servers, and continuously heals PHP CLI/INI drift caused by panel updates.
                <ol style="margin: 6px 0 10px 20px; padding: 0; line-height: 1.6;">
                    <li><strong>One-Click Build &amp; Extension Wiring:</strong> Installs version-compatible OpenSwoole builds, wires <code>ext/openswoole.so</code> + <code>php.d/openswoole.ini</code> automatically, and strips duplicate <code>extension=openswoole.so</code> entries from <code>extra.ini</code>.</li>
                    <li><strong>Autonomous CLI Symlink &amp; INI Self-Healing (v1.5.1–v1.5.3):</strong> Synchronizes <code>/usr/local/bin/php</code> and <code>/usr/bin/php</code> atomically to match Webuzo's configured Default PHP (<code>$globals['WU_DEFAULT_PHP']</code>), restores restrictive <code>0750 root:root</code> PHP INI permissions back to <code>0644</code> for unprivileged <code>webuzo</code> checks, and repairs corrupted launchers.</li>
                    <li><strong>Plan-Proportional Limits &amp; Containment:</strong> Derives <code>max_workers</code>, <code>max_task_workers</code>, memory caps, and idle timeouts strictly from each plan's vCPU &amp; RAM budget, keeping masters/workers inside <code>golden-&lt;uid&gt;.slice</code> with live self-tests and <em>Audit Events</em>.</li>
                </ol>
            </div>
        </div>

        <!-- PLATFORM OPERATIONS & LARAVEL (v1.6.0) -->
        <div class="uniselv-help-card" data-cat="platform" id="help-topic-platform">
            <span class="uniselv-help-badge badge-cat-features">Platform &amp; Laravel</span>
            <h4 class="uniselv-help-card-title">OS Preflight, Managed Laravel Services, Redis ACL Recovery &amp; Ports</h4>
            <div class="uniselv-help-card-desc">
                <strong>Menu:</strong> <em>Platform &amp; Laravel</em> tab (Admin) &amp; <em>App Services &amp; Tools</em> tab (Enduser).
                <ol style="margin: 6px 0 10px 20px; padding: 0; line-height: 1.6;">
                    <li><strong>1-Click OS Preflight &amp; Verified Composer:</strong> Audits C/C++ build headers (<code>libssl-dev</code>, <code>libcurl4-openssl-dev</code>, <code>zlib1g-dev</code>, compilers) and Composer. Missing dependencies install asynchronously via isolated transient <code>systemd-run</code> units (<code>MemoryMax=1G</code>, APT post-hooks bypassed) without straining the agent daemon.</li>
                    <li><strong>Managed Laravel Services (Global Policy + Fleet Monitor):</strong> Use <strong>Global Feature Policy</strong> checkboxes to enable/disable Managed Laravel Services and restrict allowed service types (<strong>Queue Workers</strong>, <strong>Laravel Horizon</strong>, <strong>Laravel Reverb</strong>, <strong>Scheduler</strong>) plus the global worker cap. Monitor every customer's units across the server and run 3-step self-tests; customers configure paths in <em>Enduser &rarr; App Services &amp; Tools</em>.</li>
                    <li><strong>Redis ACL Isolation &amp; Upgrade Self-Healing (v1.6.0):</strong> Enforces per-tenant prefix ACLs and optional <code>default</code> user lockdown. Tenant secrets are stored as SHA-256 hashes (UI shows plaintext only once at generation/rotation and <code>SHA-256 Hash Stored</code> afterward). Every 60s and at startup, <code>reconcile_redis_health()</code> backs up validated <code>users.acl</code> and <code>redis.conf</code> to root-only <code>/var/lib/uniselv-resource-manager/backups/redis/</code>, automatically restores or synthesizes missing <code>users.acl</code> after Webuzo Redis package upgrades with <code>0640 redis:redis</code> ownership, and surfaces <code>REDIS SERVICE STOPPED</code> if Redis goes offline while respecting intentional administrator <code>systemctl stop redis</code>.</li>
                    <li><strong>Dedicated Port Registry &amp; Socket Dir:</strong> Assigns persistent conflict-free ports per account for Octane (<code>--port</code>), Reverb, Horizon, Node, and Python alongside <code>/run/uniselv-apps/&lt;account&gt;</code>.</li>
                    <li><strong>Heavy Runtime Containment &amp; Log Watchdog:</strong> Confines or terminates out-of-slice heavy runtimes, flags bloated <code>laravel.log</code> / debug logs, and truncates safely while keeping the newest 1,000 lines (rejecting symlinks).</li>
                    <li><strong>Cluster Policy JSON Migration:</strong> Exports plans, overrides, and platform settings (with all ACL secrets stripped) and supports <strong>Dry-Run Preview</strong> before importing on another server.</li>
                </ol>
            </div>
        </div>

        <!-- HEADLESS CHROME BROWSER ENGINE GOVERNANCE -->
        <div class="uniselv-help-card" data-cat="platform" id="help-topic-chrome">
            <span class="uniselv-help-badge badge-cat-features">Headless Chrome Engine</span>
            <h4 class="uniselv-help-card-title">Headless Chrome Governance, POSIX ACL Isolation &amp; Upgrade Self-Heal</h4>
            <div class="uniselv-help-card-desc">
                <strong>Menu:</strong> <em>Platform &amp; Laravel &rarr; Chrome Engine</em> (Admin) &amp; <em>Dashboard / App Services &amp; Tools</em> (Enduser).<br>
                <strong>What it does:</strong> Provisions shared Google Chrome headless rendering for Browsershot/Puppeteer PDF &amp; screenshot workflows without exposing the binary globally.
                <ol style="margin: 6px 0 10px 20px; padding: 0; line-height: 1.6;">
                    <li><strong>Group &amp; POSIX ACL Lockdown:</strong> Locks <code>/opt/google/chrome/chrome</code> and <code>google-chrome</code> to <code>0750 root:uniselv-chrome</code> plus per-account <code>setfacl</code> permissions so only globally and individually authorized tenants can execute headless Chrome inside <code>golden-&lt;uid&gt;.slice</code>.</li>
                    <li><strong>Autonomous <code>apt</code>-Upgrade Self-Healing (v1.6.0):</strong> Unattended system Chrome package updates reset binary permissions to <code>0755 root:root</code>. On startup and every 5 minutes, <code>reconcile_chrome_permissions()</code> detects permission drift and automatically restores <code>0750 root:uniselv-chrome</code> and active tenant POSIX ACLs.</li>
                    <li><strong>Admin &amp; Customer Smoke Tests:</strong> Verify binary hardening, group/ACL membership, and isolated headless DOM execution via <code>systemd-run --quiet</code> directly from the UI.</li>
                </ol>
            </div>
        </div>

        <div class="uniselv-help-card" data-cat="features" id="help-topic-runtime">
            <span class="uniselv-help-badge badge-cat-features">Runtime Governance</span>
            <h4 class="uniselv-help-card-title">PHP Lifecycle, Configuration Drift &amp; Recovery</h4>
            <div class="uniselv-help-card-desc">
                <strong>Menu:</strong> System &amp; Agent Health &gt; Runtime Governance &amp; Configuration Evidence.
                <ol>
                    <li><strong>Install or update PHP:</strong> Apply the generator values globally for that version. Automatic onboarding/repair waits for stable observations, matching reviewed settings and successful preflight. Maintenance Mode pauses background governance.</li>
                    <li><strong>Review differences:</strong> Choose <strong>Refresh Evidence</strong>. Expected/actual settings, account INI exceptions and per-section coverage are displayed. Incomplete scans and sections not checked are labelled; no differences is not full deployment certification.</li>
                    <li><strong>Retry after fixing a cause:</strong> Choose <strong>Reconcile PHP Changes</strong>. This resets retry history without bypassing safety checks.</li>
                    <li><strong>Uninstall PHP:</strong> Move its sites first, then choose <strong>Retire Runtime</strong> and confirm successful retirement before removing software in Webuzo. <strong>Enable Runtime</strong> permits registration again. Missing files or remaining pools block unsafe retirement.</li>
                    <li><strong>Investigate busy responses:</strong> Read <strong>Capacity Events</strong> and <strong>Recent Capacity Event Timeline</strong>. These are bounded journal events, not unique visitors; account limits, shared budget and queues can have different causes.</li>
                    <li><strong>Recover or export:</strong> Use <strong>Recover Pending Operation</strong> for an interrupted lifecycle transaction, or <strong>Prepare &amp; Download Comparison</strong> for private diagnostics. Failed recovery retains its journal. Exports contain account paths; share privately.</li>
                </ol>
                Native PHP-FPM defaults remain global; automatic account runtime caps borrow available shared capacity rather than reserving workers for idle accounts. Tuning values come from the reviewed generator profile, not this help page. Configured vs Effective Audit separates the private FPM ceiling from the current concurrent relay grant. A partial grant advertises queued demand and can grow in place without a PHP/OPcache restart. Active peers publish short-lived demand heartbeats separately from waiting tickets. Deterministic sharing charges idle reservations in full and lets lightly used peers leave worker capacity available to busier peers. A missing waiting ticket alone no longer means an account is idle. Queued demand is retained and refreshed across a drained backend restart. New arrivals can trigger immediate growth without erasing the separate cooldown after a deferred shrink. Fair-share reductions hold new work in the bounded queue and wait for forwarded work and verified backend idleness before re-admission. Root-only backend sockets and a PID/start-token proxy handshake prevent bypass and preserve compatibility with older running proxies. Warm masters retain OPcache while headroom permits, with a hardware-derived maximum idle duration; eligible peer demand or low host reserve can reclaim a quiescent lease early. Ondemand workers still retire using inherited global defaults. The native cgroup service uses a plugin-owned coexistence drop-in, preserving the vendor script and managed service descendants. Native reload reconciles changed definitions selectively and gracefully reloads surviving PHP masters without closing their public socket/proxy. The managed master control grace is derived from the inherited finite request timeout, preserving longer explicit operator grace. This protects bounded post-response work from the vendor ten-second escalation. Reload can delay queued work; explicit restart, changed routing, and resource downgrades remain maintenance operations.
            </div>
        </div>
        <div class="uniselv-help-card" data-cat="trouble" id="help-topic-runtime-advanced">
            <span class="uniselv-help-badge">Baseline Reference</span>
            <h4 class="uniselv-help-card-title">Native PHP-FPM Baseline Architecture &amp; Historical Specs (v1.1.33)</h4>
            <div class="uniselv-help-card-desc">Active Plugin Release: <strong><?php echo $uniselvHelpEscape($uniselvHelpVersion); ?></strong>. The collapsible notes below preserve the reviewed v1.1.33 native PHP-FPM relay &amp; cgroup baseline for architectural reference (already applied; not manual install steps).</div>
            <details><summary>Operations, expected profile and verification scope</summary><pre style="white-space:pre-wrap;overflow-wrap:anywhere"><?php echo $uniselvHelpEscape($uniselvReadOptionalDoc('docs/release-1.1.33.md')); ?></pre></details>
            <details><summary>Exact source replacement and insertion guide</summary><pre style="white-space:pre-wrap;overflow-wrap:anywhere"><?php echo $uniselvHelpEscape($uniselvReadOptionalDoc('docs/source-changes-1.1.33.md')); ?></pre></details>
            <details><summary>Measured resource allocation and current-host tests</summary><pre style="white-space:pre-wrap;overflow-wrap:anywhere"><?php echo $uniselvHelpEscape($uniselvReadOptionalDoc('docs/server-policy-report-1.1.33.md')); ?></pre></details>
        </div>


        <!-- 1. QUICK START -->
        <div class="uniselv-help-card" data-cat="quickstart" id="help-topic-quickstart">
            <span class="uniselv-help-badge badge-cat-quickstart">Quick Start</span>
            <h4 class="uniselv-help-card-title">Administrative Quick Start & Verification</h4>
            <div class="uniselv-help-card-desc">
                UNISELV Resource Manager automates server-wide resource governance, real-time telemetry collection, and cgroups v2 kernel isolation for Webuzo.
            </div>
            <ol style="margin: 0 0 14px 20px; padding: 0; color: var(--uniselv-text-muted); font-size: 0.9rem; line-height: 1.6;">
                <li><strong>Automatic Governance:</strong> The background agent (<code>uniselv-resman-agent.service</code>) starts automatically, collects telemetry at the frequency selected under System &amp; Agent Health (5 seconds is the default), manages database retention, and validates cgroup sync.</li>
                <li><strong>Native Plan Synchronization:</strong> Click <strong>Bulk Sync All Plans</strong> at the top right to verify that all Webuzo plans are propagated into individual account slices (<code>golden-&lt;uid&gt;.slice</code>).</li>
                <li><strong>Golden Shield Safety Cap:</strong> Check the <strong>Golden Shield Governance</strong> tab to confirm that parent aggregate limits (<code>golden.slice</code>) are active with shared aggregate CPU headroom (e.g. 340% hosting + 60% system headroom on 4 vCPUs).</li>
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
                <strong>What it does:</strong> Provides telemetry of visible server hardware, aggregate shared headroom, active RAM safety budget, 1m/5m/15m system loads, and live ranking of the top consuming hosting accounts.<br>
                <strong>Menu:</strong> <em>Server Overview</em> tab.<br>
                <strong>Prerequisites:</strong> Active background agent daemon.<br>
                <strong>Usage Steps:</strong>
                <ol style="margin: 6px 0 10px 20px; padding: 0;">
                    <li>Review the hardware detection card for accurate vCPU and RAM readings.</li>
                    <li>Inspect the <strong>Top Resource Consumers</strong> table to spot accounts approaching 100% of their CPU allowance or suffering throttling.</li>
                    <li>Click <strong>Grant Boost</strong> to provide temporary emergency headroom to any account experiencing a traffic spike.</li>
                </ol>
                <strong>Expected Result:</strong> Telemetry refreshes while the dashboard is active. Check sample age; responsiveness depends on browser and server load.
            </div>
        </div>

        <!-- 3. ALL ACCOUNTS & TEMPORARY BOOST -->
        <div class="uniselv-help-card" data-cat="features" id="help-topic-accounts">
            <span class="uniselv-help-badge badge-cat-features">Features</span>
            <h4 class="uniselv-help-card-title">All Accounts Directory & Temporary Resource Boost</h4>
            <div class="uniselv-help-card-desc">
                <strong>What it does:</strong> Comprehensive inventory of all Webuzo accounts showing assigned plan, core-equivalent CPU %, allowance utilization %, memory footprint, task counts, and throttling incidents. Allows granting temporary plan upgrades that expire cleanly.<br>
                <strong>Menu:</strong> <em>All Accounts</em> tab.<br>
                <strong>Realistic Example:</strong> An e-commerce site experiences a flash-sale slowdown. First identify the limiting account, shared budget or queue. If the account is constrained and aggregate headroom exists, select a suitable higher plan using its displayed current limits and a bounded duration. A temporary boost does not create more physical RAM or CPU and cannot guarantee removal of 503 errors. Verify restoration or any reported failure after expiry.<br>
                <strong>Reversal Steps:</strong> To cancel early, click <strong>Revoke Now</strong> in the top <em>Active Temporary Resource Boosts</em> banner (via <code>cancel_temporary_override</code>), cancel from the account modal, or wait for automatic expiry.
            </div>
        </div>

        <!-- 4. CONFIGURED VS EFFECTIVE AUDIT -->
        <div class="uniselv-help-card" data-cat="features" id="help-topic-audit">
            <span class="uniselv-help-badge badge-cat-features">Features</span>
            <h4 class="uniselv-help-card-title">Configured vs Effective Kernel Limit Audit</h4>
            <div class="uniselv-help-card-desc">
                <strong>What it does:</strong> Rigorously audits every configured Webuzo plan limit against actual kernel cgroup v2 parameters. A customer slice is only labeled <strong>SYNCHRONIZED</strong> when its implemented checks match, including:<br>
                1. <code>cpu.max</code> numerical quota matches plan CPUQuota.<br>
                2. <code>memory.max</code> matches plan configured memory ceiling.<br>
                3. <code>memory.high</code> matches plan memory warning threshold.<br>
                4. <code>memory.swap.max</code> is strictly enforced to 0 bytes.<br>
                5. <code>pids.max</code> matches plan maxtask.<br>
                6. <code>io.max</code> read/write throughput and IOPS rules match the configured plan where limits apply.<br>
                7. <strong>Ancestor Slice:</strong> The slice is strictly located inside <code>/sys/fs/cgroup/golden.slice/</code>.<br>
                8. <strong>Process Placement:</strong> Observed customer processes remain inside the account boundary; shared Apache workers are audited at the hosting aggregate, not attributed as private account workers.<br>
                <strong>Menu:</strong> <em>Configured vs Effective Audit</em> tab.<br>
                <strong>Action:</strong> If any slice shows <em>MISCONFIGURED</em>, click <strong>Bulk Sync All Plans</strong> to reconcile immediately.
            </div>
        </div>

        <!-- 5. RESOURCE METRICS EXPLAINED -->
        <div class="uniselv-help-card" data-cat="metrics" id="help-topic-metrics">
            <span class="uniselv-help-badge badge-cat-metrics">Resource Metrics</span>
            <h4 class="uniselv-help-card-title">Resource Metrics & Allowance Mathematics</h4>
            <div class="uniselv-help-card-desc">
                <strong>Gauge fill:</strong> 0% is empty, 50% half and 100% full. Missing data is neutral. Hardware Detection is inventory; its ring does not represent usage. Admin Shared CPU Headroom shows configured hosting share (340% / 400% = 85% on four vCPUs). RAM is aggregate memory usage / enforced cap; System Load is load1 / vCPU count, not CPU utilization.<br>
                <strong>1. CPU % (Core Equivalent):</strong> 100% CPU represents one logical CPU/vCPU worth of scheduled execution time; it does not guarantee a dedicated physical core. On a 4 vCPU server, 400% represents total machine capacity.<br>
                <strong>Allowance Percentage Example:</strong> If an account is assigned a 200% CPU quota (2 cores) and consumes 150% CPU, its allowance usage is:
                <div style="background: var(--uniselv-bg-subtle); padding:8px 12px; border-radius:6px; margin:6px 0; font-family:monospace; font-size:0.85rem;">
                    Allowance Used = (150% Actual / 200% Quota) * 100 = 75.0%
                </div>
                <strong>2. Memory Breakdown (Anon vs Cache vs Swap):</strong>
                <ul style="margin:6px 0 6px 20px; padding:0;">
                    <li><strong>Anonymous memory:</strong> Heap and stack allocations, including PHP request data. Processes can release memory; anonymous memory is not synonymous with total RSS or shared MySQL memory.</li>
                    <li><strong>File Page Cache:</strong> Cached file data can count toward cgroup memory usage. Reclaimability varies; cache does not make an account immune to OOM.</li>
                    <li><strong>Swap Max = 0:</strong> Strict zero swap enforcement prevents VPS disk thrashing and protects NVMe performance.</li>
                </ul>
                <a href="https://docs.kernel.org/admin-guide/cgroup-v2.html" target="_blank" rel="noopener noreferrer">Linux kernel cgroup v2 reference</a><br>
                <strong>3. Tasks / PIDs (<code>pids.max</code>):</strong> Maximum concurrent threads, PHP-FPM workers, and background subprocesses permitted in the slice. Prevents fork bombs.<br>
                <strong>4. Throttling Events (<code>nr_throttled</code>):</strong> Number of configured CPU bandwidth periods in which execution was throttled. Read the actual period from <code>cpu.max</code>; do not assume every server uses 100 ms.<br>
                <strong>5. OOM Kills (<code>oom_kill</code>):</strong> Number of processes killed by an OOM killer in this cgroup. Check memory events and ancestor limits to identify the boundary involved.
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
                <strong>Transactional Backups &amp; Safe Restore:</strong> Before every policy modification, a timestamped backup is saved to <code>/var/lib/uniselv-resource-manager/golden-backups/</code>. When restoring, the manager validates schema integrity, sets drop-in limits, reloads systemd, and attempts a bounded rollback if live kernel verification fails. A failed rollback is reported as inconsistent and requires recovery review.<br>
                <strong>Vendor-Upgrade Self-Healing &amp; Scope Hygiene (v1.6.0):</strong> Every 60s and during lifecycle checks, <code>golden-shield.py heal-upgrades</code> detects Webuzo upgrades that overwrite <code>/usr/local/apps/apache2/bin/apachectl</code> or Shared Redis <code>redis.conf</code> directives, archives the vendor binary to <code>apachectl.original</code>, restores the Golden Shield wrapper/directives, and reconciles <code>shared-files.json</code> hashes alongside Redis <code>aclfile</code>. Transient session/worker units created by <code>webuzo-isolation.py</code> and <code>webuzo-session-guard.py</code> set <code>CollectMode=inactive-or-failed</code> so exited tasks do not leak stale failed scopes.<br>
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
                <strong>Installation:</strong> Activation installs missing bundled isolation, Golden Shield and session protection dependencies on a supported native layout, runs Redis &amp; Golden Shield pre-verify healing, and checks effective protection. Scripted builds can pass <code>UNISELV_SKIP_FPM_RELOAD=1</code> to suppress FPM reloads deterministically even after INI normalization. Unsupported or changed integrations stop activation and retain recovery files.<br>
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
                    <li>Review <em>System &amp; Agent Health &gt; Runtime Governance &amp; Configuration Evidence</em> for admission/queue reasons. Grant a suitable temporary boost only when account limits and aggregate headroom justify it; investigate slow application/database work separately.</li>
                </ol>
                <p><strong>Temporary boost recovery:</strong> Application, cancellation and expiry use verified plan transactions. An unresolved boost blocks overlapping boosts. A failed restore remains retryable and appears under <em>System &amp; Agent Health &gt; Temporary boost recovery</em> and <em>Audit Log</em>. UID reuse or a separately changed account plan requires administrator review; the previous boost does not overwrite that new identity or plan.</p>
                <strong>Scenario 2: Investigating Rogue Process Outside Boundary:</strong>
                <ol style="margin:6px 0 10px 20px; padding:0;">
                    <li>Open <em>Golden Shield Governance</em> tab and check <strong>Enforcement Coverage</strong>.</li>
                    <li>If any process is detected outside <code>golden.slice</code>, note the PID and executable.</li>
                    <li>Verify whether the customer process was launched via CLI or cron outside systemd user slices.</li>
                </ol>
                <strong>Scenario 3: Rolling Back Bad Policy Settings:</strong>
                <ol style="margin:6px 0 10px 20px; padding:0;">
                    <li>Click <strong>Restore Backup</strong> in the Golden Shield Governance tab.</li>
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
            
            <p style="margin:8px 0 4px 0; font-weight:600; font-size:0.85rem; color: var(--uniselv-text-main);">1. Verify Background Daemon Status & Memory:</p>
            <div class="uniselv-code-block">
                <code>systemctl status uniselv-resman-agent</code>
                <button class="uniselv-copy-btn" onclick="UniselvResMan.copyToClipboard('systemctl status uniselv-resman-agent', this)">Copy</button>
            </div>

            <p style="margin:8px 0 4px 0; font-weight:600; font-size:0.85rem; color: var(--uniselv-text-main);">2. Inspect Live Daemon Logs for Reconciliation or Errors:</p>
            <div class="uniselv-code-block">
                <code>journalctl -u uniselv-resman-agent -n 50 --no-pager</code>
                <button class="uniselv-copy-btn" onclick="UniselvResMan.copyToClipboard('journalctl -u uniselv-resman-agent -n 50 --no-pager', this)">Copy</button>
            </div>

            <p style="margin:8px 0 4px 0; font-weight:600; font-size:0.85rem; color: var(--uniselv-text-main);">3. Verify Kernel Cgroup Slices & Limits:</p>
            <div class="uniselv-code-block">
                <code>cat /sys/fs/cgroup/golden.slice/cpu.max && cat /sys/fs/cgroup/golden.slice/memory.max</code>
                <button class="uniselv-copy-btn" onclick="UniselvResMan.copyToClipboard('cat /sys/fs/cgroup/golden.slice/cpu.max && cat /sys/fs/cgroup/golden.slice/memory.max', this)">Copy</button>
            </div>

            <p style="margin:8px 0 4px 0; font-weight:600; font-size:0.85rem; color: var(--uniselv-text-main);">4. Inspect Persistent Systemd Drop-in Configuration:</p>
            <div class="uniselv-code-block">
                <code>cat /etc/systemd/system/golden.slice.d/50-uniselv-limits.conf</code>
                <button class="uniselv-copy-btn" onclick="UniselvResMan.copyToClipboard('cat /etc/systemd/system/golden.slice.d/50-uniselv-limits.conf', this)">Copy</button>
            </div>

            <p style="margin:8px 0 4px 0; font-weight:600; font-size:0.85rem; color: var(--uniselv-text-main);">5. Execute IPC Socket Health Query Directly:</p>
            <div class="uniselv-code-block">
                <code>sudo python3 -c "import json,socket; s=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM); s.settimeout(10); s.connect('/run/uniselv-resman/agent.sock'); s.sendall((json.dumps({'action':'get_agent_health','auth':{'user':'root','is_admin':True}})+'\n').encode()); print(s.makefile().readline()); s.close()"</code>
                <button class="uniselv-copy-btn" onclick="UniselvResMan.copyToClipboard(this.previousElementSibling.textContent, this)">Copy</button>
            </div>

            <p style="margin:8px 0 4px 0; font-weight:600; font-size:0.85rem; color: var(--uniselv-text-main);">6. Verify OpenSwoole Loaded Across All Webuzo PHP Branches:</p>
            <div class="uniselv-code-block">
                <code>for p in /usr/local/apps/php*/bin/php; do echo "=== $p ==="; "$p" -m | grep -i swoole; done</code>
                <button class="uniselv-copy-btn" onclick="UniselvResMan.copyToClipboard(this.previousElementSibling.textContent, this)">Copy</button>
            </div>

            <p style="margin:8px 0 4px 0; font-weight:600; font-size:0.85rem; color: var(--uniselv-text-main);">7. Inspect Managed Laravel Services &amp; Platform Dependency Job:</p>
            <div class="uniselv-code-block">
                <code>systemctl list-units 'uniselv-app-*' --no-pager && cat /var/lib/uniselv-resource-manager/platform/dep_job.json</code>
                <button class="uniselv-copy-btn" onclick="UniselvResMan.copyToClipboard(this.previousElementSibling.textContent, this)">Copy</button>
            </div>

            <p style="margin:8px 0 4px 0; font-weight:600; font-size:0.85rem; color: var(--uniselv-text-main);">8. Verify Redis ACL, Durable Backups &amp; Golden Shield Upgrade Self-Heal:</p>
            <div class="uniselv-code-block">
                <code>ls -la /usr/local/apps/redis/users.acl /var/lib/uniselv-resource-manager/backups/redis/ && python3 /usr/local/sbin/golden-shield.py heal-upgrades && python3 /usr/local/sbin/golden-shield.py check</code>
                <button class="uniselv-copy-btn" onclick="UniselvResMan.copyToClipboard(this.previousElementSibling.textContent, this)">Copy</button>
            </div>

            <p style="margin:8px 0 4px 0; font-weight:600; font-size:0.85rem; color: var(--uniselv-text-main);">9. Verify Headless Chrome Hardening &amp; Transient Scope Hygiene:</p>
            <div class="uniselv-code-block">
                <code>ls -la /opt/google/chrome/chrome /opt/google/chrome/google-chrome && systemctl --failed --no-pager</code>
                <button class="uniselv-copy-btn" onclick="UniselvResMan.copyToClipboard(this.previousElementSibling.textContent, this)">Copy</button>
            </div>
        </div>

        <!-- 10. ABOUT & COMPATIBILITY -->
        <div class="uniselv-help-card" data-cat="about" id="help-topic-about">
            <span class="uniselv-help-badge badge-cat-about">About</span>
            <h4 class="uniselv-help-card-title">About UNISELV Resource Manager & System Compatibility</h4>
            <div class="uniselv-help-card-desc">
                <table class="uniselv-table" style="width:100%; border-collapse:collapse; font-size:0.88rem; color: var(--uniselv-text-main);">
                    <tr style="border-bottom:1px solid var(--uniselv-border);"><td style="padding:6px 0; font-weight:600; width:220px;">Plugin Version:</td><td><strong><?php echo $uniselvHelpEscape($uniselvHelpVersion); ?></strong> — OpenSwoole, Headless Chrome &amp; Self-Healing Platform Governance Edition.</td></tr>
                    <tr style="border-bottom:1px solid var(--uniselv-border);"><td style="padding:6px 0; font-weight:600;">Host Operating System:</td><td><?php echo $uniselvHelpEscape($uniselvHelpOs['PRETTY_NAME'] ?? 'Unavailable'); ?></td></tr>
                    <tr style="border-bottom:1px solid var(--uniselv-border);"><td style="padding:6px 0; font-weight:600;">Active Linux Kernel:</td><td><?php echo $uniselvHelpEscape(php_uname('r') . ' (' . php_uname('m') . ')'); ?></td></tr>
                    <tr style="border-bottom:1px solid var(--uniselv-border);"><td style="padding:6px 0; font-weight:600;">Control Panel:</td><td>Webuzo <?php echo $uniselvHelpEscape($uniselvHelpPanel); ?></td></tr>
                    <tr style="border-bottom:1px solid var(--uniselv-border);"><td style="padding:6px 0; font-weight:600;">Detected PHP Stack:</td><td><?php echo $uniselvHelpEscape($uniselvPhpBranches ? implode(', ', $uniselvPhpBranches) : 'None detected'); ?></td></tr>
                    <tr style="border-bottom:1px solid var(--uniselv-border);"><td style="padding:6px 0; font-weight:600;">Platform Tooling:</td><td>Composer: <code><?php echo $uniselvHelpEscape($uniselvComposerPath); ?></code> &bull; Transient Sandbox: <code><?php echo $uniselvSystemdRunOk ? 'systemd-run OK' : 'Unavailable'; ?></code></td></tr>
                    <tr style="border-bottom:1px solid var(--uniselv-border);"><td style="padding:6px 0; font-weight:600;">Agent Service Ceiling:</td><td><code><?php echo $uniselvHelpEscape($uniselvAgentMemoryCap); ?></code> (SQLite WAL bounded footprint)</td></tr>
                    <tr style="border-bottom:1px solid var(--uniselv-border);"><td style="padding:6px 0; font-weight:600;">Self-Healing Subsystems:</td><td>Redis <code>users.acl</code> durable recovery (60s), Golden Shield <code>heal-upgrades</code> (60s), Chrome <code>0750</code>+ACL heal (300s), Default PHP CLI Sync &amp; INI <code>0644</code> guard (60s)</td></tr>
                    <tr style="border-bottom:1px solid var(--uniselv-border);"><td style="padding:6px 0; font-weight:600;">Cgroups Implementation:</td><td>Cgroups v2 Unified Hierarchy (<code>/sys/fs/cgroup</code>)</td></tr>
                    <tr style="border-bottom:1px solid var(--uniselv-border);"><td style="padding:6px 0; font-weight:600;">Process Safety:</td><td>Process identity checks with <code>pidfd</code> where supported; strict account slice containment.</td></tr>
                    <tr style="border-bottom:1px solid var(--uniselv-border);"><td style="padding:6px 0; font-weight:600;">Ownership Manifest:</td><td><code>/var/lib/uniselv-resource-manager/ownership_manifest.json</code></td></tr>
                    <tr style="border-bottom:1px solid var(--uniselv-border);"><td style="padding:6px 0; font-weight:600;">Source Repository:</td><td><a href="https://github.com/refatbd/uniselv-resource-manager" target="_blank" rel="noopener noreferrer" style="color:var(--uniselv-primary); text-decoration:none; font-weight:600;">github.com/refatbd/uniselv-resource-manager</a></td></tr>
                    <tr><td style="padding:6px 0; font-weight:600;">Developer:</td><td><strong>Refat Rahman</strong> (<a href="https://refat.ovh" target="_blank" style="color:var(--uniselv-primary); text-decoration:none; font-weight:600;">refat.ovh</a>)</td></tr>
                </table>
            </div>
        </div>

        <!-- 11. DEVELOPER PROFILE -->
        <div class="uniselv-help-card" data-cat="about" id="help-topic-developer" style="border-top: 3px solid var(--uniselv-primary);">
            <span class="uniselv-help-badge badge-cat-about">Developer Info</span>
            <h4 class="uniselv-help-card-title">Lead Developer & Systems Architect</h4>
            <div class="uniselv-help-card-desc">
                <div style="display: flex; gap: 16px; align-items: flex-start; margin-bottom: 14px;">
                    <div style="width: 48px; height: 48px; border-radius: 50%; background: linear-gradient(135deg, var(--uniselv-primary), var(--uniselv-primary-hover)); display: flex; align-items: center; justify-content: center; color: #fff; font-weight: 700; font-size: 1.2rem; flex-shrink: 0; box-shadow: 0 4px 6px rgba(23,107,91,0.25);">RR</div>
                    <div>
                        <h5 style="margin: 0 0 4px 0; font-weight: 700; color: var(--uniselv-text-main); font-size: 1.05rem;">Refat Rahman</h5>
                        <p style="margin: 0; font-size: 0.85rem; color: var(--uniselv-text-muted);">Full-Stack Engineer, Linux Systems Specialist & Extension Developer</p>
                    </div>
                </div>
                <p style="font-size: 0.88rem; color: var(--uniselv-text-muted); margin-bottom: 16px; line-height: 1.5;">
                    Specialized in enterprise web hosting automation, Linux kernel containerization (cgroups v2), high-concurrency microservices, and Webuzo ecosystem integration.
                </p>
                <div style="display: flex; flex-direction: column; gap: 8px; font-size: 0.88rem;">
                    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid var(--uniselv-border); padding-bottom: 6px;">
                        <span style="font-weight: 600; color: var(--uniselv-text-muted);">Website:</span>
                        <a href="https://refat.ovh" target="_blank" style="color: var(--uniselv-primary); font-weight: 600; text-decoration: none;">refat.ovh</a>
                    </div>
                    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid var(--uniselv-border); padding-bottom: 6px;">
                        <span style="font-weight: 600; color: var(--uniselv-text-muted);">GitHub:</span>
                        <a href="https://github.com/refatbd" target="_blank" style="color: var(--uniselv-text-main); font-weight: 600; text-decoration: none;">github.com/refatbd</a>
                    </div>
                    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #f1f5f9; padding-bottom: 6px;">
                        <span style="font-weight: 600; color: var(--uniselv-text-muted);">Telegram:</span>
                        <a href="https://t.me/refatbd" target="_blank" style="color: #0284c7; font-weight: 600; text-decoration: none;">t.me/refatbd</a>
                    </div>
                    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #f1f5f9; padding-bottom: 6px;">
                        <span style="font-weight: 600; color: var(--uniselv-text-muted);">Facebook:</span>
                        <a href="https://www.facebook.com/rjrefat/" target="_blank" style="color: #1877f2; font-weight: 600; text-decoration: none;">facebook.com/rjrefat</a>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="font-weight: 600; color: var(--uniselv-text-muted);">Instagram:</span>
                        <a href="https://www.instagram.com/refat_official" target="_blank" style="color: #e1306c; font-weight: 600; text-decoration: none;">instagram.com/refat_official</a>
                    </div>
                </div>
            </div>
        </div>

    </div>
</div>
