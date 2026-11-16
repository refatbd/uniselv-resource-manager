<?php
/**
 * UNISELV Resource Manager - Modern Enduser Help & About View
 * Role-specific, searchable, responsive documentation tailored for Webuzo hosting customers.
 */
$uniselvEuInfo = @json_decode(@file_get_contents(__DIR__ . '/../info.json'), true) ?: [];
$uniselvEuVersion = htmlspecialchars((string)($uniselvEuInfo['version'] ?? '1.2.0'), ENT_QUOTES, 'UTF-8');
$uniselvEuPhp = [];
foreach ((array)@glob('/usr/local/apps/php*/bin/php') as $_euPhpBin) {
    if (preg_match('#/apps/(php\d{2,3})/bin/php$#', (string)$_euPhpBin, $_euM) && @is_executable($_euPhpBin)) {
        $_euBr = $_euM[1];
        $_euHasOsw = @file_exists("/usr/local/apps/{$_euBr}/ext/openswoole.so") || @file_exists("/usr/local/apps/{$_euBr}/etc/php.d/openswoole.ini");
        $uniselvEuPhp[] = strtoupper($_euBr) . ($_euHasOsw ? ' + OpenSwoole' : '');
    }
}
sort($uniselvEuPhp);
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
        <button class="uniselv-cat-btn" data-cat="stack-suite" onclick="UniselvResMan.setHelpCategory('stack-suite')">🚀 8 Services Developer Guide</button>
        <button class="uniselv-cat-btn" data-cat="quickstart" onclick="UniselvResMan.setHelpCategory('quickstart')">Getting Started</button>
        <button class="uniselv-cat-btn" data-cat="laravel" onclick="UniselvResMan.setHelpCategory('laravel')">Laravel &amp; App Blueprint</button>
        <button class="uniselv-cat-btn" data-cat="features" onclick="UniselvResMan.setHelpCategory('features')">Features & Tools</button>
        <button class="uniselv-cat-btn" data-cat="metrics" onclick="UniselvResMan.setHelpCategory('metrics')">Understanding Metrics</button>
        <button class="uniselv-cat-btn" data-cat="scenarios" onclick="UniselvResMan.setHelpCategory('scenarios')">Practical Guides</button>
        <button class="uniselv-cat-btn" data-cat="trouble" onclick="UniselvResMan.setHelpCategory('trouble')">FAQ & Diagnostics</button>
        <button class="uniselv-cat-btn" data-cat="about" onclick="UniselvResMan.setHelpCategory('about')">About Your Environment</button>
    </div>

    <!-- Documentation Articles Grid -->
    <div class="uniselv-help-grid">

        <!-- ==================== 8 MODERN SERVICES DEVELOPER GUIDES ==================== -->

        <!-- 1. REDIS GUIDE -->
        <div class="uniselv-help-card" data-cat="stack-suite laravel" id="help-topic-guide-redis" style="border-top: 3px solid #ef4444;">
            <span class="uniselv-help-badge" style="background:#fef2f2;color:#dc2626;border:1px solid #fee2e2;">Stack Guide 1 / 8</span>
            <h4 class="uniselv-help-card-title">1. Redis Caching, Session &amp; Key-Prefix Isolation Guide</h4>
            <div class="uniselv-help-card-desc">
                <p><strong>Overview &amp; Architecture:</strong> Redis is an ultra-fast in-memory key-value data store. Offloading application caching, sessions, and queue backends to Redis improves response times by up to 3x compared to MySQL or filesystem storage. UNISELV enforces dedicated ACL credentials and key-prefix isolation per account, preventing cross-tenant access and ensuring complete data isolation.</p>

                <h5 style="margin:10px 0 4px 0;font-size:0.88rem;color:#1e293b;">1. Required <code>.env</code> Configuration Fields:</h5>
                <table class="uniselv-field-table">
                    <thead>
                        <tr><th>Field Name</th><th>Value / Placement</th><th>Description</th></tr>
                    </thead>
                    <tbody>
                        <tr><td><code>REDIS_CLIENT</code></td><td><code>phpredis</code></td><td>High-speed pre-compiled C-extension in Webuzo PHP</td></tr>
                        <tr><td><code>REDIS_HOST</code></td><td><code>127.0.0.1</code></td><td>Local loopback host for minimal socket latency</td></tr>
                        <tr><td><code>REDIS_PORT</code></td><td><code>6379</code></td><td>Standard Redis TCP listener port</td></tr>
                        <tr><td><code>REDIS_USERNAME</code></td><td><code>u_&lt;your_username&gt;</code></td><td>Dedicated ACL username provisioned for your account</td></tr>
                        <tr><td><code>REDIS_PASSWORD</code></td><td>Copy from Redis card in Dashboard</td><td>Secure ACL password provisioned by UNISELV</td></tr>
                        <tr><td><code>REDIS_PREFIX</code></td><td><code>&lt;your_username&gt;:</code></td><td>Mandatory: Enforced namespace prefix for tenant isolation</td></tr>
                        <tr><td><code>CACHE_PREFIX</code></td><td><code>&lt;your_username&gt;:cache:</code></td><td>Cache subsystem namespace isolation prefix</td></tr>
                    </tbody>
                </table>

                <h5 style="margin:10px 0 4px 0;font-size:0.88rem;color:#1e293b;">2. Production Copy-Ready <code>.env</code> Snippet:</h5>
                <pre class="uniselv-code-block"><code>REDIS_CLIENT=phpredis
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_USERNAME=u_yourusername
REDIS_PASSWORD=your_acl_password_here
REDIS_PREFIX=yourusername:
CACHE_PREFIX=yourusername:cache:
HORIZON_PREFIX=yourusername:horizon:
CACHE_STORE=redis
SESSION_DRIVER=redis
QUEUE_CONNECTION=redis</code></pre>

                <h5 style="margin:10px 0 4px 0;font-size:0.88rem;color:#1e293b;">3. Laravel Implementation Example:</h5>
                <pre class="uniselv-code-block"><code>use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Facades\Redis;

// Store cache with a 1-hour expiration:
Cache::put('latest_products', $products, 3600);

// Direct Redis command execution:
Redis::set('daily_visitors', 1250);
$visitors = Redis::get('daily_visitors');</code></pre>

                <p style="font-size:0.8rem;color:#475569;margin-top:6px;"><strong>Dashboard Verification:</strong> Click the <strong>⚡ Test</strong> button on the <em>Redis</em> card in your UNISELV dashboard to instantly verify connection latency, prefix write permissions, cross-tenant denial guards, and administrative command protection.</p>
            </div>
        </div>

        <!-- 2. SUPERVISOR GUIDE -->
        <div class="uniselv-help-card" data-cat="stack-suite laravel" id="help-topic-guide-supervisor" style="border-top: 3px solid #8b5cf6;">
            <span class="uniselv-help-badge" style="background:#f5f3ff;color:#7c3aed;border:1px solid #ede9fe;">Stack Guide 2 / 8</span>
            <h4 class="uniselv-help-card-title">2. Supervisor Process Manager (Non-Root User Scoped) Guide</h4>
            <div class="uniselv-help-card-desc">
                <p><strong>Overview &amp; Architecture:</strong> Supervisor keeps background workers, queue consumers, and WebSocket servers running continuously 24/7. It automatically restarts them upon unexpected exits, fatal crashes, or server reboots. UNISELV enables non-root user-scoped drop-in configuration files located directly inside your home directory.</p>

                <h5 style="margin:10px 0 4px 0;font-size:0.88rem;color:#1e293b;">1. Drop-In Configuration File Location:</h5>
                <p style="font-size:0.83rem;margin:0 0 6px 0;">Create your configuration file in the following path inside your home directory:<br>
                <code>/home/&lt;username&gt;/.uniselv-supervisor/conf.d/worker.conf</code></p>

                <h5 style="margin:10px 0 4px 0;font-size:0.88rem;color:#1e293b;">2. Configuration Directives &amp; Parameters:</h5>
                <table class="uniselv-field-table">
                    <thead>
                        <tr><th>Directive (Key)</th><th>Recommended Value</th><th>Description</th></tr>
                    </thead>
                    <tbody>
                        <tr><td><code>[program:name]</code></td><td><code>[program:&lt;user&gt;-worker]</code></td><td>Unique program identifier</td></tr>
                        <tr><td><code>command</code></td><td><code>/usr/local/apps/php84/bin/php /home/.../artisan queue:work</code></td><td>Absolute execution path with PHP binary and flags</td></tr>
                        <tr><td><code>autostart</code></td><td><code>true</code></td><td>Start automatically on system boot or daemon start</td></tr>
                        <tr><td><code>autorestart</code></td><td><code>true</code></td><td>Restart immediately if process exits unexpectedly</td></tr>
                        <tr><td><code>numprocs</code></td><td><code>2</code></td><td>Number of parallel worker instances to spawn</td></tr>
                        <tr><td><code>stdout_logfile</code></td><td><code>/home/&lt;user&gt;/.uniselv-logs/worker.log</code></td><td>Destination for standard output and diagnostic logs</td></tr>
                    </tbody>
                </table>

                <h5 style="margin:10px 0 4px 0;font-size:0.88rem;color:#1e293b;">3. Production Copy-Ready <code>worker.conf</code> Snippet:</h5>
                <pre class="uniselv-code-block"><code>[program:my-app-worker]
process_name=%(program_name)s_%(process_num)02d
command=/usr/local/apps/php84/bin/php /home/username/public_html/artisan queue:work --sleep=3 --tries=3 --max-time=3600
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
numprocs=2
redirect_stderr=true
stdout_logfile=/home/username/.uniselv-logs/worker.log
stdout_logfile_maxbytes=10MB
stdout_logfile_backups=2</code></pre>
                <p style="font-size:0.8rem;color:#475569;margin-top:6px;"><strong>Dashboard Verification:</strong> Once saved, the UNISELV agent automatically registers the drop-in. Click <strong>⚡ Test</strong> on the <em>Supervisor</em> card to inspect daemon status and active drop-in configuration files.</p>
            </div>
        </div>

        <!-- 3. LARAVEL QUEUE WORKERS GUIDE -->
        <div class="uniselv-help-card" data-cat="stack-suite laravel" id="help-topic-guide-queue" style="border-top: 3px solid #3b82f6;">
            <span class="uniselv-help-badge" style="background:#eff6ff;color:#2563eb;border:1px solid #dbeafe;">Stack Guide 3 / 8</span>
            <h4 class="uniselv-help-card-title">3. Laravel Queue Workers Implementation Guide</h4>
            <div class="uniselv-help-card-desc">
                <p><strong>Overview &amp; Architecture:</strong> Long-running tasks such as sending emails, dispatching push notifications, PDF rendering, and processing webhooks should never block HTTP web requests. Queue workers offload these jobs to the background, allowing web requests to complete in sub-50ms latency while background tasks are handled asynchronously.</p>

                <h5 style="margin:10px 0 4px 0;font-size:0.88rem;color:#1e293b;">1. Required <code>.env</code> Configuration:</h5>
                <pre class="uniselv-code-block"><code>QUEUE_CONNECTION=redis</code></pre>

                <h5 style="margin:10px 0 4px 0;font-size:0.88rem;color:#1e293b;">2. Creating and Dispatching a Job:</h5>
                <pre class="uniselv-code-block"><code>// Generate job in project: php artisan make:job SendWelcomeEmail

namespace App\Jobs;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Queue\Queueable;
use Illuminate\Support\Facades\Mail;

class SendWelcomeEmail implements ShouldQueue
{
    use Queueable;

    public function __construct(public $user) {}

    public function handle(): void
    {
        Mail::to($this->user->email)->send(new \App\Mail\WelcomeMail($this->user));
    }
}

// Dispatching from controller or event:
SendWelcomeEmail::dispatch($user);</code></pre>

                <h5 style="margin:10px 0 4px 0;font-size:0.88rem;color:#1e293b;">3. Worker Execution Command with Memory Safeguards:</h5>
                <pre class="uniselv-code-block"><code>/usr/local/apps/php84/bin/php /home/user/public_html/artisan queue:work --sleep=3 --tries=3 --timeout=90 --max-time=3600 --memory=256</code></pre>
                <p style="font-size:0.8rem;color:#475569;margin-top:6px;"><strong>Dashboard Verification:</strong> Click <strong>⚡ Test</strong> on the <em>Laravel Queue Workers</em> card to verify your plan queue quota, PHP CLI availability, and active worker count.</p>
            </div>
        </div>

        <!-- 4. LARAVEL HORIZON GUIDE -->
        <div class="uniselv-help-card" data-cat="stack-suite laravel" id="help-topic-guide-horizon" style="border-top: 3px solid #6366f1;">
            <span class="uniselv-help-badge" style="background:#eef2ff;color:#4f46e5;border:1px solid #e0e7ff;">Stack Guide 4 / 8</span>
            <h4 class="uniselv-help-card-title">4. Laravel Horizon Queue Dashboard &amp; Monitoring Guide</h4>
            <div class="uniselv-help-card-desc">
                <p><strong>Overview &amp; Architecture:</strong> Laravel Horizon provides a dashboard and code-driven configuration for Redis queues. It offers real-time job throughput metrics, runtime graphs, queue wait times, job failure diagnostics, and auto-balancing worker pools.</p>

                <p style="font-size:0.82rem;color:#b45309;background:#fffbeb;padding:6px 10px;border-radius:6px;border:1px solid #fde68a;"><strong>Prerequisites:</strong> Horizon requires active Redis ACL credentials and at least 512 MiB of account memory allocated on your hosting plan.</p>

                <h5 style="margin:10px 0 4px 0;font-size:0.88rem;color:#1e293b;">1. Installation &amp; <code>.env</code> Configuration:</h5>
                <pre class="uniselv-code-block"><code>composer require laravel/horizon
php artisan horizon:install

# Set dedicated Horizon prefix in .env:
HORIZON_PREFIX=yourusername:horizon:</code></pre>

                <h5 style="margin:10px 0 4px 0;font-size:0.88rem;color:#1e293b;">2. Dashboard Access Authorization (HorizonServiceProvider.php):</h5>
                <pre class="uniselv-code-block"><code>// In app/Providers/HorizonServiceProvider.php define authorized users:
protected function gate(): void
{
    Gate::define('viewHorizon', function ($user = null) {
        return in_array($user?->email, [
            'admin@yourdomain.com',
        ]);
    });
}</code></pre>

                <h5 style="margin:10px 0 4px 0;font-size:0.88rem;color:#1e293b;">3. Continuous Horizon Execution via Supervisor:</h5>
                <pre class="uniselv-code-block"><code># In ~/.uniselv-supervisor/conf.d/horizon.conf:
command=/usr/local/apps/php84/bin/php /home/username/public_html/artisan horizon</code></pre>
                <p style="font-size:0.8rem;color:#475569;margin-top:6px;"><strong>Dashboard Verification:</strong> Click <strong>⚡ Test</strong> on the <em>Laravel Horizon Dashboard</em> card to check memory quota compliance, Redis dependencies, and assigned metrics port allocation.</p>
            </div>
        </div>

        <!-- 5. LARAVEL REVERB GUIDE -->
        <div class="uniselv-help-card" data-cat="stack-suite laravel" id="help-topic-guide-reverb" style="border-top: 3px solid #f59e0b;">
            <span class="uniselv-help-badge" style="background:#fffbeb;color:#d97706;border:1px solid #fef3c7;">Stack Guide 5 / 8</span>
            <h4 class="uniselv-help-card-title">5. Laravel Reverb / WebSocket &amp; SSL Reverse Proxy Guide</h4>
            <div class="uniselv-help-card-desc">
                <p><strong>Overview &amp; Architecture:</strong> Laravel Reverb is a high-speed, first-party WebSocket server designed for seamless integration with Laravel. It powers real-time chat, live notifications, live order tracking, and dynamic UI updates without page refreshes, eliminating third-party subscription costs (such as Pusher).</p>

                <p style="font-size:0.82rem;color:#1d4ed8;background:#eff6ff;padding:6px 10px;border-radius:6px;border:1px solid #bfdbfe;"><strong>Dedicated Port &amp; SSL Reverse Proxy:</strong> UNISELV assigns an exclusive private port (e.g., 22241) to your account. Browsers connect via standard <code>wss://yourdomain.com/app</code> through an Apache SSL reverse proxy configured with 1-click in the dashboard.</p>

                <h5 style="margin:10px 0 4px 0;font-size:0.88rem;color:#1e293b;">1. Required <code>.env</code> Configuration:</h5>
                <pre class="uniselv-code-block"><code>BROADCAST_CONNECTION=reverb
REVERB_APP_ID=my-reverb-app
REVERB_APP_KEY=my-reverb-key-123
REVERB_APP_SECRET=my-reverb-secret-abc
REVERB_HOST="127.0.0.1"
REVERB_PORT=22241
REVERB_SCHEME=http

# Browser &amp; Vite Frontend Settings:
VITE_REVERB_APP_KEY="${REVERB_APP_KEY}"
VITE_REVERB_HOST="yourdomain.com"
VITE_REVERB_PORT=443
VITE_REVERB_SCHEME=https</code></pre>

                <h5 style="margin:10px 0 4px 0;font-size:0.88rem;color:#1e293b;">2. Broadcasting a Real-Time Event in Laravel:</h5>
                <pre class="uniselv-code-block"><code>namespace App\Events;
use Illuminate\Broadcasting\Channel;
use Illuminate\Contracts\Broadcasting\ShouldBroadcast;

class OrderUpdated implements ShouldBroadcast
{
    public function __construct(public $order) {}

    public function broadcastOn(): Channel
    {
        return new Channel('orders');
    }
}

// Firing the event:
broadcast(new OrderUpdated($order));</code></pre>

                <h5 style="margin:10px 0 4px 0;font-size:0.88rem;color:#1e293b;">3. Client-Side Echo Listener (JavaScript):</h5>
                <pre class="uniselv-code-block"><code>window.Echo.channel('orders')
    .listen('OrderUpdated', (e) => {
        console.log('Order status updated:', e.order.status);
    });</code></pre>
                <p style="font-size:0.8rem;color:#475569;margin-top:6px;"><strong>Dashboard Verification:</strong> Click <strong>⚡ Test</strong> on the <em>Laravel Reverb / WebSocket</em> card to verify port readiness, SSL reverse proxy configuration, and connection availability.</p>
            </div>
        </div>

        <!-- 6. LARAVEL SCHEDULER GUIDE -->
        <div class="uniselv-help-card" data-cat="stack-suite laravel" id="help-topic-guide-scheduler" style="border-top: 3px solid #06b6d4;">
            <span class="uniselv-help-badge" style="background:#ecfeff;color:#0891b2;border:1px solid #cffafe;">Stack Guide 6 / 8</span>
            <h4 class="uniselv-help-card-title">6. Laravel Scheduler &amp; Automated Webuzo Cron Guide</h4>
            <div class="uniselv-help-card-desc">
                <p><strong>Overview &amp; Architecture:</strong> Instead of managing multiple disparate server crons, Laravel Scheduler uses a single 1-minute crontab entry to execute all scheduled commands defined directly in your application code (daily backups, database cleanup, hourly email summaries, etc.).</p>

                <h5 style="margin:10px 0 4px 0;font-size:0.88rem;color:#1e293b;">1. 1-Click Webuzo Cron Registration:</h5>
                <p style="font-size:0.83rem;margin:0 0 6px 0;">Click the <strong>"⏱️ Webuzo Cron"</strong> button on the Scheduler card to register the following cron command automatically without needing SSH:</p>
                <pre class="uniselv-code-block"><code>* * * * * /usr/local/apps/php84/bin/php /home/username/public_html/artisan schedule:run > /dev/null 2>&1</code></pre>

                <h5 style="margin:10px 0 4px 0;font-size:0.88rem;color:#1e293b;">2. Defining Scheduled Tasks in Laravel (routes/console.php):</h5>
                <pre class="uniselv-code-block"><code>use Illuminate\Support\Facades\Schedule;

// Daily database backup at 2:00 AM:
Schedule::command('backup:clean')->dailyAt('01:30');
Schedule::command('backup:run')->dailyAt('02:00');

// Hourly cache pruning:
Schedule::command('cache:prune-stale-tags')->hourly();

// Custom scheduled closure:
Schedule::call(function () {
    \App\Models\Order::where('status', 'unpaid')->where('created_at', '<', now()->subDays(3))->delete();
})->daily();</code></pre>
                <p style="font-size:0.8rem;color:#475569;margin-top:6px;"><strong>Dashboard Verification:</strong> Click <strong>⚡ Test</strong> on the <em>Laravel Scheduler</em> card to verify crontab registration and PHP CLI execution readiness.</p>
            </div>
        </div>

        <!-- 7. CHROME BROWSER ENGINE GUIDE -->
        <div class="uniselv-help-card" data-cat="stack-suite laravel" id="help-topic-guide-chrome" style="border-top: 3px solid #14b8a6;">
            <span class="uniselv-help-badge" style="background:#f0fdfa;color:#0d9488;border:1px solid #ccfbf1;">Stack Guide 7 / 8</span>
            <h4 class="uniselv-help-card-title">7. Chrome Browser Engine (Headless PDF &amp; Screenshots) Guide</h4>
            <div class="uniselv-help-card-desc">
                <p><strong>Overview &amp; Architecture:</strong> Headless Chrome is utilized on the server for rendering pixel-perfect PDF invoices, taking automated webpage screenshots, generating social share cards, and running headless browser automations via Spatie Browsershot or Puppeteer.</p>

                <p style="font-size:0.82rem;color:#92400e;background:#fffbeb;padding:6px 10px;border-radius:6px;border:1px solid #fde68a;"><strong>Mandatory Sandbox Flags:</strong> Running Chrome within user containment slices requires <code>--no-sandbox</code>, <code>--disable-setuid-sandbox</code>, and <code>--disable-dev-shm-usage</code> flags to ensure safe execution.</p>

                <h5 style="margin:10px 0 4px 0;font-size:0.88rem;color:#1e293b;">1. System Binary &amp; <code>.env</code> Fields:</h5>
                <table class="uniselv-field-table">
                    <thead>
                        <tr><th>Field Name</th><th>Value</th><th>Description</th></tr>
                    </thead>
                    <tbody>
                        <tr><td><code>CHROME_PATH</code></td><td><code>/usr/bin/google-chrome-stable</code></td><td>Server Google Chrome headless binary</td></tr>
                        <tr><td><code>PUPPETEER_EXECUTABLE_PATH</code></td><td><code>/usr/bin/google-chrome-stable</code></td><td>System Chrome executable for Puppeteer</td></tr>
                    </tbody>
                </table>

                <h5 style="margin:10px 0 4px 0;font-size:0.88rem;color:#1e293b;">2. Generating PDFs with Spatie Browsershot (PHP):</h5>
                <pre class="uniselv-code-block"><code>// composer require spatie/browsershot
use Spatie\Browsershot\Browsershot;

$pdfData = Browsershot::html('&lt;h1&gt;Customer Invoice #1024&lt;/h1&gt;&lt;p&gt;Payment Status: Completed&lt;/p&gt;')
    ->setChromePath('/usr/bin/google-chrome-stable')
    ->addChromiumArguments([
        'no-sandbox',
        'disable-setuid-sandbox',
        'disable-dev-shm-usage',
        'headless=new'
    ])
    ->format('A4')
    ->pdf();

return response($pdfData)->header('Content-Type', 'application/pdf');</code></pre>
                <p style="font-size:0.8rem;color:#475569;margin-top:6px;"><strong>Dashboard Verification:</strong> Click <strong>⚡ Test</strong> on the <em>Chrome Browser Engine</em> card to run a live headless DOM rendering smoke test inside your account's containment slice.</p>
            </div>
        </div>

        <!-- 8. OPENSWOOLE & OCTANE GUIDE -->
        <div class="uniselv-help-card" data-cat="stack-suite laravel" id="help-topic-guide-openswoole" style="border-top: 3px solid #10b981;">
            <span class="uniselv-help-badge" style="background:#ecfdf5;color:#059669;border:1px solid #a7f3d0;">Stack Guide 8 / 8</span>
            <h4 class="uniselv-help-card-title">8. OpenSwoole Runtime &amp; Laravel Octane Acceleration Guide</h4>
            <div class="uniselv-help-card-desc">
                <p><strong>Overview &amp; Architecture:</strong> In standard PHP-FPM, the entire Laravel framework bootstraps on every single request. OpenSwoole and Laravel Octane keep the application booted in memory, serving incoming requests via high-concurrency event loops, achieving up to 10x throughput and sub-10ms response times.</p>

                <p style="font-size:0.82rem;color:#047857;background:#ecfdf5;padding:6px 10px;border-radius:6px;border:1px solid #a7f3d0;"><strong>Pre-Compiled Extensions:</strong> OpenSwoole is pre-compiled across PHP 7.4, 8.1, 8.2, and 8.4 on the UNISELV server. A dedicated port is reserved specifically for your account's Octane server.</p>

                <h5 style="margin:10px 0 4px 0;font-size:0.88rem;color:#1e293b;">1. Installation &amp; <code>.env</code> Configuration:</h5>
                <pre class="uniselv-code-block"><code>composer require laravel/octane
php artisan octane:install --server=swoole

# In your .env file:
OCTANE_SERVER=swoole
OCTANE_PORT=22242
OCTANE_WORKERS=2
OCTANE_TASK_WORKERS=1</code></pre>

                <h5 style="margin:10px 0 4px 0;font-size:0.88rem;color:#1e293b;">2. Continuous Octane Daemon Execution via Supervisor:</h5>
                <pre class="uniselv-code-block"><code>/usr/local/apps/php84/bin/php /home/username/public_html/artisan octane:start --server=swoole --host=127.0.0.1 --port=22242 --workers=2</code></pre>

                <h5 style="margin:10px 0 4px 0;font-size:0.88rem;color:#1e293b;">3. Architecture Best Practice (Stateless Coding):</h5>
                <p style="font-size:0.83rem;color:#475569;margin:0;">Because the application remains in memory across requests, do not store request-specific state in static properties or singletons. Handle each request statelessly to maintain high reliability.</p>
                <p style="font-size:0.8rem;color:#475569;margin-top:6px;"><strong>Dashboard Verification:</strong> Click <strong>⚡ Test</strong> on the <em>OpenSwoole Runtime</em> card to verify the PHP module, Coroutine engine availability, and dedicated Octane port readiness.</p>
            </div>
        </div>

        <!-- ==================== END 8 MODERN SERVICES DEVELOPER GUIDES ==================== -->


        <!-- 1. QUICK START -->
        <div class="uniselv-help-card" data-cat="quickstart" id="help-topic-quickstart">
            <span class="uniselv-help-badge badge-cat-quickstart">Getting Started</span>
            <h4 class="uniselv-help-card-title">Quick Start: Monitoring Your Account Performance</h4>
            <div class="uniselv-help-card-desc">
                Your hosting account has enforced resource ceilings for CPU, memory, disk bandwidth, and tasks within a shared server. These ceilings are not dedicated physical resources.<br>
                <ol style="margin: 8px 0 10px 20px; padding: 0; line-height: 1.6;">
                    <li><strong>Real-Time Gauges:</strong> The <em>Dashboard</em> refreshes every 10 seconds, showing the latest collected sample and its age. Measured sparklines appear after two distinct samples. Fresh samples can be reused across tabs in the same authenticated account; separate accounts and sessions remain isolated. Unavailable connections retain the last values and show their actual age.</li>
                    <li><strong>Color Status Indicators:</strong>
                        <ul style="margin:4px 0 6px 16px; padding:0;">
                            <li><span class="uniselv-badge badge-normal" style="margin-right:6px;">NORMAL</span> Usage is safely within plan thresholds.</li>
                            <li><span class="uniselv-badge badge-warning" style="margin-right:6px;">ELEVATED</span> Usage has reached the warning threshold configured by your hosting provider.</li>
                            <li><span class="uniselv-badge badge-critical" style="margin-right:6px;">LIMIT EXCEEDED</span> The critical warning threshold has been reached. Check measured throttling events to confirm CPU enforcement.</li>
                        </ul>
                    </li>
                    <li><strong>Investigating Spikes:</strong> Switch to the <em>Historical Charts</em> tab to identify exactly when spikes occurred using Last Hour, Today, Yesterday, Last 7 Days or Last 30 Days.</li>
                </ol>
            </div>
        </div>

        <!-- 2. FEATURES & TOOLS -->
        <div class="uniselv-help-card" data-cat="features" id="help-topic-dashboard">
            <span class="uniselv-help-badge badge-cat-features">Features</span>
            <h4 class="uniselv-help-card-title">Live Resource Dashboard & Sparklines</h4>
            <div class="uniselv-help-card-desc">
                <strong>What it does:</strong> Displays live meters for CPU, Memory, Active Tasks, and Disk I/O along with measured trend sparklines collected while this page is open (up to 5 minutes). Charts stay blank until two distinct samples arrive; each card uses its own scale.<br>
                <strong>Menu:</strong> <em>Dashboard</em> tab.<br>
                <strong>Key Details:</strong> Displays your core equivalent alongside percentage utilization, ensuring you always know how many CPU cores your application is utilizing.
            </div>
        </div>

        <div class="uniselv-help-card" data-cat="features" id="help-topic-processes">
            <span class="uniselv-help-badge badge-cat-features">Features</span>
            <h4 class="uniselv-help-card-title">Process Manager & Safe Script Termination</h4>
            <div class="uniselv-help-card-desc">
                <strong>What it does:</strong> Shows all active PHP-FPM web workers, cron scripts, and CLI processes currently executing inside your account boundary.<br>
                <strong>Menu:</strong> <em>Current Usage</em> tab.<br>
                <strong>Terminating a Process:</strong> If a script is hanging or looping infinitely, click <strong>Stop</strong> next to the process entry. UNISELV securely verifies ownership before terminating only the targeted PID, preventing accidental disruption of other visitors.
            </div>
        </div>

        <div class="uniselv-help-card" data-cat="features" id="help-topic-snapshots">
            <span class="uniselv-help-badge badge-cat-features">Features</span>
            <h4 class="uniselv-help-card-title">Diagnostic Incident Snapshots</h4>
            <div class="uniselv-help-card-desc">
                <strong>What it does:</strong> When enabled by the administrator, measured CPU throttling, OOM kills and task-limit events trigger snapshots subject to the configured cooldown. Periodic snapshots may also be present.<br>
                <strong>Menu:</strong> <em>Snapshots</em> tab.<br>
                <strong>How to use:</strong> Choose a date, then use <strong>Choose snapshot</strong>. Review <strong>Process list</strong>, <strong>Database Queries</strong> and <strong>HTTP Queries</strong>. Unavailable or empty evidence is labelled separately.
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

        <div class="uniselv-help-card" data-cat="features" id="help-topic-services">
            <span class="uniselv-help-badge badge-cat-features">Laravel &amp; App Services</span>
            <h4 class="uniselv-help-card-title">One-Click Laravel Workers, Horizon, Reverb, Ports &amp; Redis ACL</h4>
            <div class="uniselv-help-card-desc">
                <strong>Menu:</strong> <em>App Services &amp; Tools</em> tab.<br>
                <strong>What it does:</strong> Manage production background services without opening an SSH terminal:
                <ul style="margin:6px 0 6px 18px; padding:0; line-height:1.55;">
                    <li><strong>Managed Laravel Services:</strong> Auto-detects your Laravel projects and lets you install, start, stop, restart, enable/disable, test, or inspect logs for <strong>Queue Workers</strong>, <strong>Horizon</strong>, <strong>Reverb WebSocket</strong>, and <strong>Scheduler</strong> when enabled by your administrator (Horizon and Reverb require at least <code>512 MiB</code> plan RAM).</li>
                    <li><strong>Dedicated Ports, Unix Sockets &amp; Copy Helpers:</strong> Shows your reserved, conflict-free ports for Octane, Reverb, Horizon, Node, and Python plus your private socket directory, with one-click Copy buttons for Reverb Apache proxy snippets.</li>
                    <li><strong>Isolated Redis ACL:</strong> When permitted by host policy, generate or rotate your private Redis ACL username/password locked strictly to your account key prefix with one-click <code>.env</code> snippet copy.</li>
                    <li><strong>App Log Watchdog:</strong> Scan oversized logs (e.g. <code>storage/logs/laravel.log</code>) and safely trim when enabled by host policy, preserving the newest 1,000 lines.</li>
                </ul>
            </div>
        </div>

        <div class="uniselv-help-card" data-cat="features" id="help-topic-openswoole">
            <span class="uniselv-help-badge badge-cat-features">OpenSwoole</span>
            <h4 class="uniselv-help-card-title">OpenSwoole &amp; Laravel Octane Plan Budgets</h4>
            <div class="uniselv-help-card-desc">
                <strong>Menu:</strong> <em>Current usage</em> tab &gt; OpenSwoole Runtime Governance.<br>
                <strong>What it shows:</strong> Whether OpenSwoole is enabled on your plan, your assigned dedicated Octane port, allowed <strong>Max Workers</strong>, <strong>Max Task Workers</strong>, memory cap, active PHP branches, and a one-click copyable <code>php artisan octane:start --port=&lt;port&gt;</code> command pre-filled with your safe worker flags.
            </div>
        </div>

        <!-- 3. UNDERSTANDING METRICS -->
        <div class="uniselv-help-card" data-cat="metrics" id="help-topic-metrics">
            <span class="uniselv-help-badge badge-cat-metrics">Resource Metrics</span>
            <h4 class="uniselv-help-card-title">Understanding Resource Metrics & Math</h4>
            <div class="uniselv-help-card-desc">
                <strong>1. CPU % (Core Equivalent):</strong> 100% CPU represents one vCPU of execution time. If your plan has a 100% CPU quota and uses 50%, you are using 0.5 cores. If your plan has a 200% CPU quota (2 cores) and consumes 150%, you are utilizing 1.5 cores (which represents 75% of your allowance).<br>
                <strong>2. Memory (Anonymous vs Cache):</strong>
                <ul style="margin:4px 0 6px 16px; padding:0;">
                    <li><strong>Physical Memory (RAM):</strong> Consumed by your active PHP code, WordPress plugins, and opcache.</li>
                    <li><strong>Page Cache:</strong> Temporary disk reads stored by the operating system. Cache contributes to accounted memory; reclaimable pages may be freed under pressure, with possible I/O latency.</li>
                    <li><strong>Zero Swap:</strong> The hosting environment enforces zero swap to prevent disk latency from slowing down your website.</li>
                </ul>
                <strong>3. Active Tasks (Processes):</strong> The number of Linux tasks (processes and threads) in the account cgroup. This is not a count of simultaneous HTTP requests. If tasks reach your plan's maximum, incoming requests may temporarily queue or return 503 errors.<br>
                <strong>4. Disk I/O Throughput:</strong> The volume of data read from or written to the underlying storage per second. Storage hardware varies by server.
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
                    <li>If an unwanted background script is stuck, click <strong>Stop</strong> to terminate it.</li>
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
                <strong>Scenario 4: Running Laravel Queues, Horizon, or Reverb WebSocket without SSH:</strong>
                <ol style="margin:6px 0 6px 20px; padding:0;">
                    <li>Open the <strong>App Services &amp; Tools</strong> tab and select your detected Laravel project pill to fill the path.</li>
                    <li>Pick <em>Queue Worker</em>, <em>Horizon</em>, <em>Reverb WebSocket</em>, or <em>Scheduler</em>, choose your PHP version, and click <strong>Install &amp; Start Service</strong>.</li>
                    <li>Use <strong>Test</strong> or <strong>Logs</strong> anytime to verify jobs are running cleanly inside your isolated slice.</li>
                </ol>
            </div>
        </div>

        <!-- 5. FAQ & DIAGNOSTICS -->
        <div class="uniselv-help-card" data-cat="trouble" id="help-topic-trouble">
            <span class="uniselv-help-badge badge-cat-trouble">FAQ & Diagnostics</span>
            <h4 class="uniselv-help-card-title">Frequently Asked Questions (FAQ)</h4>
            <div class="uniselv-help-card-desc">
                <p><strong>Q: Why does my CPU usage drop to 0% right after loading my website?</strong><br>
                A: CPU is measured over a sampling interval. A short request may finish between samples; an idle account can legitimately show 0%. Check the sample age to distinguish inactivity from stale data.</p>

                <p><strong>Q: What happens if my script exceeds the memory limit?</strong><br>
                A: The Linux kernel may reclaim memory and then terminate one or more processes in the account cgroup when it cannot satisfy the enforced ceiling. This event is recorded in your <em>Notifications &amp; Events</em> tab as an Out-Of-Memory (OOM) event.</p>

                <p><strong>Q: Is it safe to stop a process?</strong><br>
                A: Stop only an eligible process you recognize as stuck. It interrupts its work and can fail an active request, import, backup or checkout. Database transactions do not guarantee application-level consistency for every interrupted task.</p>
            </div>
        </div>

        <!-- LARAVEL DEVELOPER INTEGRATION BLUEPRINT (ZERO-TOUCH SERVER PHILOSOPHY) -->
        <div class="uniselv-help-card" data-cat="laravel" id="help-topic-laravel-blueprint" style="border-top: 3px solid #f97316;">
            <span class="uniselv-help-badge" style="background:#fff7ed;color:#ea580c;border:1px solid #ffedd5;">Zero-Touch Architecture</span>
            <h4 class="uniselv-help-card-title">Laravel Developer Integration Blueprint</h4>
            <div class="uniselv-help-card-desc">
                <p>UNISELV operates on a strict <strong>Zero-Touch Application Philosophy</strong>. The server never modifies your application source code, <code>.env</code> file, or project repository. Instead, UNISELV provisions secure server-level isolation (Cgroups v2, Redis ACLs, dedicated ports, Supervisor drop-ins, and Webuzo Cron) and lets you configure your Laravel application cleanly using standard environment variables.</p>

                <h5 style="margin:12px 0 6px 0;font-size:0.9rem;color:#1e293b;">1. Redis ACL &amp; Key-Prefix Isolation</h5>
                <p style="font-size:0.83rem;margin:0 0 6px 0;">To protect shared server resources, each tenant account is assigned an isolated Redis ACL user restricted strictly to keys matching <code>&lt;account&gt;:*</code>. In your Laravel project's <code>.env</code>, configure:</p>
                <pre style="background:#0f172a;color:#f8fafc;padding:12px;border-radius:8px;font-size:0.78rem;overflow-x:auto;margin:0 0 10px 0;"><code>REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_USERNAME=u_yourusername
REDIS_PASSWORD=your_isolated_acl_password
REDIS_PREFIX=yourusername:
HORIZON_PREFIX=yourusername:horizon:
CACHE_PREFIX=yourusername:cache:</code></pre>

                <h5 style="margin:12px 0 6px 0;font-size:0.9rem;color:#1e293b;">2. Laravel Reverb WebSocket &amp; VHost Reverse Proxy</h5>
                <p style="font-size:0.83rem;margin:0 0 6px 0;">Each account has a dedicated private port (e.g. <code>22241</code>) assigned to Reverb. In your <code>.env</code>:</p>
                <pre style="background:#0f172a;color:#f8fafc;padding:12px;border-radius:8px;font-size:0.78rem;overflow-x:auto;margin:0 0 10px 0;"><code>REVERB_APP_ID=your-app-id
REVERB_APP_KEY=your-app-key
REVERB_APP_SECRET=your-app-secret
REVERB_HOST="127.0.0.1"
REVERB_PORT=22241
REVERB_SCHEME=http

# Client-facing WebSocket configuration:
VITE_REVERB_HOST="yourdomain.com"
VITE_REVERB_PORT=443
VITE_REVERB_SCHEME=https</code></pre>
                <p style="font-size:0.82rem;color:#475569;margin:0 0 10px 0;">Click <strong>"🌐 Enable Proxy in Webuzo Apache VHost"</strong> in <em>App Services &amp; Tools</em>. This creates a non-invasive include file (<code>/usr/local/apps/apache2/etc/conf.d/uniselv-reverb-{domain}.conf</code>) that forwards <code>/app</code> and <code>/apps</code> to your private Reverb port over SSL automatically.</p>

                <h5 style="margin:12px 0 6px 0;font-size:0.9rem;color:#1e293b;">3. Non-Root Supervisor Drop-In Workers</h5>
                <p style="font-size:0.83rem;margin:0 0 6px 0;">You do not need root access to manage workers. Drop a standard Supervisor config file into your scoped configuration folder: <code>/home/&lt;user&gt;/.uniselv-supervisor/conf.d/worker.conf</code>:</p>
                <pre style="background:#0f172a;color:#f8fafc;padding:12px;border-radius:8px;font-size:0.78rem;overflow-x:auto;margin:0 0 10px 0;"><code>[program:laravel-worker]
process_name=%(program_name)s_%(process_num)02d
command=/usr/local/apps/php84/bin/php /home/user/public_html/artisan queue:work --sleep=3 --tries=3 --max-time=3600
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
numprocs=2
redirect_stderr=true
stdout_logfile=/home/user/.uniselv-logs/queue.log
stdout_logfile_maxbytes=10MB
stdout_logfile_backups=2</code></pre>
                <p style="font-size:0.82rem;color:#475569;margin:0 0 10px 0;">The UNISELV agent auto-detects this file, launches your workers under your account's isolated Cgroup slice, and provides <strong>Restart</strong>, <strong>Test</strong>, and <strong>Logs</strong> tools in your panel.</p>

                <h5 style="margin:12px 0 6px 0;font-size:0.9rem;color:#1e293b;">4. Laravel Scheduler (Automated Webuzo Cron)</h5>
                <p style="font-size:0.83rem;margin:0 0 6px 0;">Under <em>App Services &amp; Tools</em>, click <strong>"⏱️ Webuzo Cron"</strong> in the Laravel Scheduler row. UNISELV safely registers the 1-minute runner in your user crontab without terminal commands:</p>
                <pre style="background:#0f172a;color:#f8fafc;padding:12px;border-radius:8px;font-size:0.78rem;overflow-x:auto;margin:0 0 10px 0;"><code>* * * * * /usr/local/apps/php84/bin/php /home/user/public_html/artisan schedule:run > /dev/null 2>&1</code></pre>
            </div>
        </div>

        <!-- 6. ABOUT YOUR ENVIRONMENT -->
        <div class="uniselv-help-card" data-cat="about" id="help-topic-about">
            <span class="uniselv-help-badge badge-cat-about">About</span>
            <h4 class="uniselv-help-card-title">About Your Hosting Environment</h4>
            <div class="uniselv-help-card-desc">
                <table style="width:100%; border-collapse:collapse; font-size:0.86rem; color:#334155; margin-bottom:10px;">
                    <tr style="border-bottom:1px solid #f1f5f9;"><td style="padding:5px 0; font-weight:600; width:190px;">Resource Manager Version:</td><td><strong>v<?php echo $uniselvEuVersion; ?></strong> (OpenSwoole &amp; Managed Laravel Platform)</td></tr>
                    <tr style="border-bottom:1px solid #f1f5f9;"><td style="padding:5px 0; font-weight:600;">Kernel Isolation:</td><td>Linux <strong>Cgroups v2</strong> per-account resource slice</td></tr>
                    <tr style="border-bottom:1px solid #f1f5f9;"><td style="padding:5px 0; font-weight:600;">Available PHP Runtimes:</td><td><?php echo htmlspecialchars($uniselvEuPhp ? implode(', ', $uniselvEuPhp) : 'Standard Webuzo PHP', ENT_QUOTES, 'UTF-8'); ?></td></tr>
                    <tr><td style="padding:5px 0; font-weight:600;">Managed App Features:</td><td>One-Click Laravel Queue / Horizon / Reverb / Scheduler, Isolated Redis ACL &amp; Dedicated Port Registry</td></tr>
                </table>
                Account limits and the shared hosting pool reduce resource contention. Shared database, storage and host pressure can still affect site performance; this is not complete container or filesystem isolation. For questions regarding your plan allocation or upgrading your limits, contact your hosting provider.
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
