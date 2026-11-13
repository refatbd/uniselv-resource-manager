/**
 * UNISELV Resource Manager Frontend Application
 * Lightweight, accessible, dependency-free interactive UI, real-time telemetry animation,
 * modern toast/modal notification system, and native SVG chart renderer.
 */

// ==================== DYNAMIC I18N SYSTEM (B03) ====================
const UniselvI18n = {
    locale: (typeof window !== 'undefined' && window.UNISELV_LOCALE) ? window.UNISELV_LOCALE : 'en',
    translations: (typeof window !== 'undefined' && window.UNISELV_TRANSLATIONS) ? window.UNISELV_TRANSLATIONS : {},
    t: function(key, fallback) {
        if (this.translations && this.translations[key]) {
            return this.translations[key];
        }
        return fallback !== undefined ? fallback : key;
    }
};

// ==================== MODERN TOAST NOTIFICATION SYSTEM ====================
const UniselvNotify = {
    container: null,

    init: function() {
        if (!this.container) {
            this.container = document.getElementById('uniselv-toast-container');
            if (!this.container) {
                this.container = document.createElement('div');
                this.container.id = 'uniselv-toast-container';
                this.container.className = 'uniselv-toast-container';
                document.body.appendChild(this.container);
            }
        }
    },

    show: function(type, title, message, duration = 4500) {
        this.init();

        const safe = value => String(value).replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
        const toast = document.createElement('div');
        toast.className = `uniselv-toast uniselv-toast-${type}`;
        toast.setAttribute('role', type === 'error' ? 'alert' : 'status');

        const icons = {
            success: `<svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/></svg>`,
            error: `<svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12"/></svg>`,
            warning: `<svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>`,
            info: `<svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>`
        };

        toast.innerHTML = `
            <div class="uniselv-toast-icon">${icons[type] || icons.info}</div>
            <div class="uniselv-toast-body">
                <div class="uniselv-toast-title">${safe(title)}</div>
                <div class="uniselv-toast-msg">${safe(message)}</div>
            </div>
            <button class="uniselv-toast-close" title="Dismiss">&times;</button>
            <div class="uniselv-toast-progress">
                <div class="uniselv-toast-progress-fill" style="animation-duration: ${duration}ms;"></div>
            </div>
        `;

        this.container.appendChild(toast);

        // Close on click
        const closeBtn = toast.querySelector('.uniselv-toast-close');
        let timer = null;

        const dismiss = () => {
            if (timer) clearTimeout(timer);
            toast.classList.add('uniselv-toast-dismissing');
            setTimeout(() => {
                if (toast.parentNode) toast.parentNode.removeChild(toast);
            }, 300);
        };

        closeBtn.addEventListener('click', dismiss);
        timer = setTimeout(dismiss, duration);
    },

    success: function(msg, title = 'Operation Successful') {
        this.show('success', title, msg, 4500);
    },

    error: function(msg, title = 'Error Encountered') {
        this.show('error', title, msg, 6500);
    },

    warning: function(msg, title = 'Attention Required') {
        this.show('warning', title, msg, 5500);
    },

    info: function(msg, title = 'System Notification') {
        this.show('info', title, msg, 4500);
    }
};

// Notifications remain scoped to this plugin; Webuzo owns window.alert.

// ==================== MODERN MODAL DIALOG SYSTEM ====================
const UniselvModal = {
    confirm: function({ title, message, icon = 'warning', confirmText = 'Confirm', cancelText = 'Cancel', isDanger = false, onConfirm, onCancel }) {
        const backdrop = document.createElement('div');
        backdrop.className = 'uniselv-modal-backdrop';

        const icons = {
            warning: `<div class="uniselv-modal-icon icon-modal-warning"><svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg></div>`,
            danger: `<div class="uniselv-modal-icon icon-modal-danger"><svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg></div>`,
            info: `<div class="uniselv-modal-icon icon-modal-info"><svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg></div>`
        };

        backdrop.innerHTML = `
            <div class="uniselv-modal">
                ${icons[icon] || icons.warning}
                <div class="uniselv-modal-title">${title}</div>
                <div class="uniselv-modal-msg">${message}</div>
                <div class="uniselv-modal-actions">
                    <button class="uniselv-modal-btn uniselv-modal-cancel">${cancelText}</button>
                    <button class="uniselv-modal-btn uniselv-modal-confirm ${isDanger ? 'danger' : ''}">${confirmText}</button>
                </div>
            </div>
        `;

        const previousFocus = document.activeElement;
        const dialog = backdrop.querySelector('.uniselv-modal');
        dialog.setAttribute('role', 'dialog');
        dialog.setAttribute('aria-modal', 'true');
        dialog.setAttribute('aria-label', title);
        document.body.appendChild(backdrop);
        setTimeout(() => backdrop.classList.add('show'), 20);

        const close = () => {
            backdrop.removeEventListener('keydown', onKey);
            previousFocus?.focus();
            backdrop.classList.remove('show');
            setTimeout(() => {
                if (backdrop.parentNode) backdrop.parentNode.removeChild(backdrop);
            }, 250);
        };

        const cancelBtn = backdrop.querySelector('.uniselv-modal-cancel');
        const confirmBtn = backdrop.querySelector('.uniselv-modal-confirm');

        cancelBtn.addEventListener('click', () => {
            close();
            if (typeof onCancel === 'function') onCancel();
        });

        confirmBtn.addEventListener('click', () => {
            close();
            if (typeof onConfirm === 'function') onConfirm();
        });

        const onKey = e => {
            if (e.key === 'Escape') { e.preventDefault(); cancelBtn.click(); }
            if (e.key === 'Tab') {
                e.preventDefault();
                (document.activeElement === cancelBtn ? confirmBtn : cancelBtn).focus();
            }
        };
        backdrop.addEventListener('keydown', onKey);
        cancelBtn.focus();

        // Close on clicking backdrop
        backdrop.addEventListener('click', (e) => {
            if (e.target === backdrop) {
                close();
                if (typeof onCancel === 'function') onCancel();
            }
        });
    }
};

// ==================== REUSABLE CLIENT-SIDE PAGINATION ====================
const UniselvPagination = {
    render: function({ containerId, totalItems, currentPage, pageSize, onPageChange, onPageSizeChange }) {
        const container = document.getElementById(containerId);
        if (!container) return;
        if (totalItems <= 0) {
            container.innerHTML = '';
            return;
        }
        const totalPages = Math.max(1, Math.ceil(totalItems / pageSize));
        currentPage = Math.min(Math.max(1, currentPage), totalPages);
        const startIdx = (currentPage - 1) * pageSize + 1;
        const endIdx = Math.min(currentPage * pageSize, totalItems);

        let html = `
            <div class="uniselv-pagination-info">
                Showing <strong>${startIdx}</strong> to <strong>${endIdx}</strong> of <strong>${totalItems}</strong> entries
            </div>
            <div class="uniselv-pagination-controls">
                <select class="uniselv-page-size-select" title="Rows per page">
                    <option value="10" ${pageSize === 10 ? 'selected' : ''}>10 / page</option>
                    <option value="15" ${pageSize === 15 ? 'selected' : ''}>15 / page</option>
                    <option value="25" ${pageSize === 25 ? 'selected' : ''}>25 / page</option>
                    <option value="50" ${pageSize === 50 ? 'selected' : ''}>50 / page</option>
                </select>
                <button class="uniselv-page-btn prev-btn" ${currentPage <= 1 ? 'disabled' : ''}>&laquo; Prev</button>
        `;

        let startPage = Math.max(1, currentPage - 2);
        let endPage = Math.min(totalPages, startPage + 4);
        if (endPage - startPage < 4) {
            startPage = Math.max(1, endPage - 4);
        }
        for (let p = startPage; p <= endPage; p++) {
            html += `<button class="uniselv-page-btn page-num-btn ${p === currentPage ? 'active' : ''}" data-page="${p}">${p}</button>`;
        }

        html += `
                <button class="uniselv-page-btn next-btn" ${currentPage >= totalPages ? 'disabled' : ''}>Next &raquo;</button>
            </div>
        `;
        container.innerHTML = html;

        const sel = container.querySelector('.uniselv-page-size-select');
        if (sel) {
            sel.addEventListener('change', (e) => {
                if (typeof onPageSizeChange === 'function') onPageSizeChange(parseInt(e.target.value, 10));
            });
        }
        const prevBtn = container.querySelector('.prev-btn');
        if (prevBtn) {
            prevBtn.addEventListener('click', () => {
                if (currentPage > 1 && typeof onPageChange === 'function') onPageChange(currentPage - 1);
            });
        }
        const nextBtn = container.querySelector('.next-btn');
        if (nextBtn) {
            nextBtn.addEventListener('click', () => {
                if (currentPage < totalPages && typeof onPageChange === 'function') onPageChange(currentPage + 1);
            });
        }
        container.querySelectorAll('.page-num-btn').forEach(b => {
            b.addEventListener('click', (e) => {
                const p = parseInt(e.target.getAttribute('data-page'), 10);
                if (p !== currentPage && typeof onPageChange === 'function') onPageChange(p);
            });
        });
    }
};

// Session-scoped, memory-only sharing of read-only telemetry. Never share mutations,
// CSRF tokens, other accounts, or data through persistent browser storage.
class UniselvLiveTelemetry {
    constructor(app) {
        this.app = app;
        this.action = app.isAdmin ? 'overview' : 'dashboard';
        this.interval = 10000;
        this.reuseMs = 5000;
        this.cached = null;
        this.receivedAt = 0;
        this.pending = false;
        this.waiters = [];
        this.subscriber = null;
        this.retryAt = 0;
        this.failures = 0;
        this.closed = false;
        this.channel = null;
        this.lockName = null;
        this.cancelRequest = null;
        this.ready = this.connect();
    }
    async connect() {
        try {
            if (!this.app.csrfToken || typeof BroadcastChannel === 'undefined' ||
                !window.crypto?.subtle || typeof TextEncoder === 'undefined') return;
            const identity = JSON.stringify([new URL(this.app.apiEndpoint, window.location.origin).toString(),
                this.app.currentUser, this.app.isAdmin, this.app.csrfToken]);
            const digest = await window.crypto.subtle.digest('SHA-256', new TextEncoder().encode(identity));
            if (this.closed) return;
            const key = Array.from(new Uint8Array(digest), b => b.toString(16).padStart(2, '0')).join('');
            this.lockName = 'uniselv-live-v1-' + key;
            this.channel = new BroadcastChannel(this.lockName);
            this.channel.onmessage = event => this.receive(event.data);
            this.post({kind: 'hello'});
        } catch (_) { this.lockName = null; }
    }
    sampleEpoch(data) {
        const row = this.action === 'overview' ? (data?.host || data?.server) : data?.current;
        return Number(row?.last_sample_epoch) || 0;
    }
    fresh() {
        const age = Date.now() - this.receivedAt;
        return this.cached !== null && age >= 0 && age < this.reuseMs;
    }
    post(message) {
        try { this.channel?.postMessage({...message, action: this.action}); } catch (_) {}
    }
    receive(message) {
        if (this.closed || !message || message.action !== this.action) return;
        if (message.kind === 'hello') {
            if (this.fresh()) this.post({kind: 'sample', at: this.receivedAt, data: this.cached});
            return;
        }
        const now = Date.now();
        if (message.kind === 'failure' && Number.isFinite(message.until) &&
            message.until > now && message.until <= now + 60000 && !this.fresh()) {
            this.retryAt = Math.max(this.retryAt, message.until);
            this.failures = Math.max(this.failures, Math.min(6, Number(message.failures) || 1));
            const callbacks = this.waiters.splice(0);
            if (!callbacks.length && this.subscriber && this.app.isLiveTelemetryVisible()) callbacks.push(this.subscriber);
            this.notify(callbacks, new Error('Telemetry connection unavailable'), null);
            return;
        }
        if (message.kind !== 'sample' || !Number.isFinite(message.at) || message.at <= this.receivedAt ||
            message.at > now + 1000 || now - message.at >= this.reuseMs ||
            !message.data || typeof message.data !== 'object' || message.data.error ||
            this.sampleEpoch(message.data) < this.sampleEpoch(this.cached)) return;
        this.cached = message.data;
        this.receivedAt = Math.min(now, message.at);
        this.failures = 0;
        this.retryAt = 0;
        const callbacks = this.waiters.splice(0);
        if (!callbacks.length && this.subscriber && this.app.isLiveTelemetryVisible()) callbacks.push(this.subscriber);
        this.notify(callbacks, null, this.cached);
    }
    notify(callbacks, error, data) {
        for (const callback of callbacks) {
            try { callback(error, data); } catch (error) { console.error('Telemetry render failed', error); }
        }
    }
    read(action, callback) {
        if (action !== this.action) throw new Error('Telemetry scope mismatch');
        if (this.closed) return;
        this.subscriber = callback;
        if (this.fresh()) { callback(null, this.cached); return; }
        if (Date.now() < this.retryAt) { callback(new Error('Telemetry reconnect pending'), null); return; }
        this.waiters.push(callback);
        if (this.pending) return;
        this.pending = true;
        const run = async () => {
            // Process any queued cross-tab sample before issuing another request.
            await new Promise(resolve => setTimeout(resolve, 0));
            if (this.closed) return;
            if (this.fresh()) { this.finish(null, this.cached, false); return; }
            if (Date.now() < this.retryAt) { this.finish(new Error('Telemetry reconnect pending'), null, false); return; }
            await new Promise(resolve => {
                this.cancelRequest = this.app.callApi(action, {}, (error, data) => {
                    this.finish(error || (data?.error ? new Error('Telemetry request failed') : null), data, true);
                    resolve();
                }, {timeoutMs: 15000});
            });
        };
        this.ready.then(() => {
            if (this.closed) return;
            const locks = typeof navigator !== 'undefined' ? navigator.locks : null;
            if (this.channel && this.lockName && locks?.request) {
                return locks.request(this.lockName, run);
            }
            return run();
        }).catch(error => { if (!this.closed) this.finish(error, null, true); });
    }
    finish(error, data, network) {
        this.pending = false;
        this.cancelRequest = null;
        if (this.closed) return;
        if (error && this.fresh()) { error = null; data = this.cached; network = false; }
        if (!error && this.cached && this.sampleEpoch(data) < this.sampleEpoch(this.cached)) { data = this.cached; network = false; }
        if (!error && (!data || typeof data !== 'object')) error = new Error('Telemetry unavailable');
        if (error) {
            if (network) {
                this.failures++;
                this.retryAt = Date.now() + Math.min(60000, this.interval * Math.pow(2, this.failures - 1));
                this.post({kind: 'failure', until: this.retryAt, failures: this.failures});
            }
        } else {
            this.cached = data;
            if (network) this.receivedAt = Date.now();
            this.failures = 0;
            this.retryAt = 0;
            if (network) this.post({kind: 'sample', at: this.receivedAt, data});
        }
        this.notify(this.waiters.splice(0), error, error ? null : data);
    }
    close() {
        this.closed = true;
        if (this.cancelRequest) this.cancelRequest();
        this.channel?.close();
        this.waiters = [];
        this.subscriber = null;
    }
}

// ==================== MAIN APPLICATION CONTROLLER ====================
const UniselvResMan = {
    apiEndpoint: '',
    isAdmin: false,
    currentUser: '',
    csrfToken: '',
    pollTimer: null,

    init: function(endpoint, isAdmin, user, csrfToken) {
        this.apiEndpoint = endpoint;
        this.isAdmin = isAdmin;
        this.currentUser = user;
        this.csrfToken = csrfToken || '';
        this.bindTabs();
        this.bindEvents();

        this.startLivePolling();
        if (this.isAdmin) {
            this.loadFeatureSettings();
            this.loadStorageSettings();
            const sel = document.getElementById('admin-user-selector');
            if (sel && sel.value) {
                this.selectedAdminUser = sel.value;
            }
        }

        // URL Fragment / Hash Route Navigation
        const initialTab = this.resolveTabAlias(window.location.hash);
        if (initialTab && document.querySelector(`.uniselv-tab-btn[data-tab="${initialTab}"]`)) {
            this.switchTab(initialTab, false);
        } else {
            const defaultTab = this.isAdmin ? 'overview' : 'dashboard';
            if (!window.location.hash) {
                if (window.history && window.history.replaceState) {
                    window.history.replaceState(null, null, '#' + defaultTab);
                }
            }
            if (!this.isAdmin) {
                this.loadEnduserSnapshotsIndex();
            }
            if (this.isAdmin) this.refreshLiveTelemetry();
        }
        if (!this.isAdmin) this.refreshLiveTelemetry(true);
    },

    resolveTabAlias: function(hash) {
        if (!hash) return null;
        let clean = String(hash).replace(/^#+/, '').trim().toLowerCase();
        clean = clean.replace(/^tab-/, '');
        if (!/^[a-z][a-z0-9-]*$/.test(clean)) return null;
        const aliasMap = {
            'current-usage': 'processes',
            'usage': 'processes',
            'server-overview': 'overview',
            'events': 'notifications',
            'notifs': 'notifications',
            'charts': 'history',
            'shield': 'goldenshield',
            'settings': 'health',
            'storage': 'health'
        };
        return aliasMap[clean] || clean;
    },

    handleHashChange: function() {
        const target = this.resolveTabAlias(window.location.hash);
        if (!target) return;
        const btn = document.querySelector(`.uniselv-tab-btn[data-tab="${target}"]`);
        if (btn && !btn.classList.contains('active')) {
            this.switchTab(target, false);
        }
    },

    translate: function(key, fallback) {
        return window.UNISELV_TRANSLATIONS?.[key] || fallback;
    },

    bindTabs: function() {
        const tabs = document.querySelector('.uniselv-tabs');
        if (tabs && !document.getElementById('uniselv-mobile-section')) {
            const label = document.createElement('label');
            label.className = 'uniselv-mobile-navigation';
            label.textContent = this.translate('section', 'Section');
            const select = document.createElement('select');
            select.id = 'uniselv-mobile-section';
            select.className = 'uniselv-select';
            tabs.querySelectorAll('.uniselv-tab-btn').forEach(button => {
                const option = document.createElement('option');
                option.value = button.dataset.tab;
                option.textContent = button.textContent.trim();
                select.appendChild(option);
            });
            select.addEventListener('change', () => this.switchTab(select.value));
            label.appendChild(select);
            tabs.before(label);
        }
        if (tabs && this.isAdmin && !document.getElementById('uniselv-more-sections')) {
            const label = this.translate('more_sections', 'More sections');
            const select = document.createElement('select');
            select.id = 'uniselv-more-sections';
            select.className = 'uniselv-section-overflow uniselv-cpanel-select';
            select.setAttribute('aria-label', label);
            select.add(new Option(label, ''));
            const primary = new Set(['overview', 'accounts', 'analytics', 'openswoole', 'platform', 'health']);
            tabs.querySelectorAll('.uniselv-tab-btn').forEach(button => {
                if (primary.has(button.dataset.tab)) return;
                button.classList.add('uniselv-secondary-tab');
                select.add(new Option(button.textContent.trim(), button.dataset.tab));
            });
            select.addEventListener('change', () => {
                if (select.value) this.switchTab(select.value);
            });
            tabs.appendChild(select);
        }
        document.querySelectorAll('.uniselv-tab-btn').forEach(btn => {
            btn.setAttribute('aria-controls', 'tab-' + btn.dataset.tab);
            btn.setAttribute('aria-pressed', String(btn.classList.contains('active')));
            btn.addEventListener('click', (e) => {
                const targetTab = btn.getAttribute('data-tab');
                this.switchTab(targetTab, true);
            });
        });

        // Browser back/forward navigation support
        window.addEventListener('hashchange', () => {
            this.handleHashChange();
        });
    },

    switchTab: function(targetTab, updateHash = true) {
        const resolved = this.resolveTabAlias(targetTab) || targetTab;
        const btn = document.querySelector(`.uniselv-tab-btn[data-tab="${resolved}"]`);
        const content = document.getElementById('tab-' + resolved);

        if (!btn || !content) return;

        document.querySelectorAll('.uniselv-tab-btn').forEach(b => {
            b.classList.toggle('active', b === btn);
            b.setAttribute('aria-pressed', String(b === btn));
        });
        document.querySelectorAll('.uniselv-tab-content').forEach(c => c.classList.remove('active'));

        content.classList.add('active');
        const mobileSelect = document.getElementById('uniselv-mobile-section');
        if (mobileSelect) mobileSelect.value = resolved;
        const moreSections = document.getElementById('uniselv-more-sections');
        if (moreSections) moreSections.value = btn.classList.contains('uniselv-secondary-tab') ? resolved : '';

        if (updateHash) {
            if (window.history && window.history.replaceState) {
                window.history.replaceState(null, null, '#' + resolved);
            } else {
                window.location.hash = resolved;
            }
        }

        // Trigger tab-specific data loading
        if (this.isAdmin) {
            if (resolved === 'overview') {
                this.loadAdminOverview();
            } else if (resolved === 'openswoole') {
                this.loadOpenSwooleGovernance();
            } else if (resolved === 'platform') {
                this.loadPlatformAdmin();
            } else if (resolved === 'health') {
                this.loadPhpLifecycle();
                this.loadRuntimeGovernance();
                this.loadFeatureSettings();
                this.loadStorageSettings();
            } else if (resolved === 'goldenshield') {
                this.refreshBackupsList();
            } else if (resolved === 'capacity') {
                this.loadCapacityPlanning();
            } else if (resolved === 'reports') {
                this.loadScheduledReports();
                this.loadReportSchedule();
            } else if (resolved === 'integrations') {
                this.loadPackageMappings();
                this.loadPermissions();
            } else if (resolved === 'auditlog') {
                this.loadAuditLogs();
            } else if (resolved === 'analytics') {
                const sel = document.getElementById('admin-user-selector');
                const targetU = this.selectedAdminUser || (sel ? sel.value : '');
                if (sel && targetU) {
                    sel.value = targetU;
                    this.onAdminUserSelected(targetU);
                }
            } else if (resolved === 'accounts') {
                this.initAccountsPagination();
            }
        } else {
            if (resolved === 'processes') {
                const tf = document.getElementById('uniselv-usage-timeframe')?.value || 'today';
                this.loadCurrentUsage(tf);
                this.loadLiveProcesses();
                this.loadEnduserOpenSwoole();
            } else if (resolved === 'snapshots') {
                this.loadEnduserSnapshotsIndex();
            } else if (resolved === 'notifications') {
                this.loadEnduserNotifications();
            } else if (resolved === 'services') {
                this.loadEnduserServices();
            } else if (resolved === 'history') {
                const range = this.activeEnduserRange || '1h';
                this.loadHistory(range);
            }
        }
    },

    bindEvents: function() {
        document.querySelectorAll('.uniselv-container input, .uniselv-container select, .uniselv-container textarea').forEach(el => {
            if (el.labels?.length || el.getAttribute('aria-label')) return;
            const group = el.closest('.uniselv-form-group');
            const label = group?.querySelector('label');
            el.setAttribute('aria-label', label?.textContent.trim() || el.placeholder || el.id.replace(/[-_]/g, ' ') || 'Setting');
        });
        // Range buttons for history
        document.querySelectorAll('.uniselv-range-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.uniselv-range-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                const range = e.target.getAttribute('data-range');
                this.activeEnduserRange = range;
                this.loadHistory(range);
            });
        });

        // Search in admin table with pagination integration
        const searchInput = document.getElementById('uniselv-account-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.adminAccountsQuery = e.target.value;
                this.adminAccountsPage = 1;
                this.renderAccountsPage();
            });
        }
    },

    adminAccountsPage: 1,
    adminAccountsPageSize: 15,
    adminAccountsQuery: '',

    initAccountsPagination: function() {
        this.renderAccountsPage();
    },

    renderAccountsPage: function() {
        const rows = Array.from(document.querySelectorAll('.uniselv-account-row'));
        if (rows.length === 0) return;

        const q = (this.adminAccountsQuery || '').toLowerCase();
        const matchedRows = rows.filter(row => {
            const uname = (row.getAttribute('data-user') || '').toLowerCase();
            const domain = (row.getAttribute('data-domain') || '').toLowerCase();
            return !q || uname.includes(q) || domain.includes(q);
        });

        // Hide all rows initially
        rows.forEach(r => r.style.display = 'none');

        const totalItems = matchedRows.length;
        const totalPages = Math.max(1, Math.ceil(totalItems / this.adminAccountsPageSize));
        this.adminAccountsPage = Math.min(Math.max(1, this.adminAccountsPage), totalPages);

        const startIdx = (this.adminAccountsPage - 1) * this.adminAccountsPageSize;
        const pageRows = matchedRows.slice(startIdx, startIdx + this.adminAccountsPageSize);
        pageRows.forEach(r => r.style.display = '');

        UniselvPagination.render({
            containerId: 'uniselv-accounts-pagination',
            totalItems: totalItems,
            currentPage: this.adminAccountsPage,
            pageSize: this.adminAccountsPageSize,
            onPageChange: (newPage) => {
                this.adminAccountsPage = newPage;
                this.renderAccountsPage();
            },
            onPageSizeChange: (newSize) => {
                this.adminAccountsPageSize = newSize;
                this.adminAccountsPage = 1;
                this.renderAccountsPage();
            }
        });
    },

    isLiveTelemetryVisible: function() {
        if (document.hidden) return false;
        const tab = document.getElementById(this.isAdmin ? 'tab-overview' : 'tab-dashboard');
        return !!tab && tab.classList.contains('active');
    },

    requestLiveTelemetry: function(action, callback) {
        if (this.liveTelemetry) return this.liveTelemetry.read(action, callback);
        return this.callApi(action, {}, callback); // Initial/static test contexts.
    },

    refreshLiveTelemetry: function(initial = false) {
        if (!initial && !this.isLiveTelemetryVisible()) return;
        if (this.isAdmin) { this.loadAdminOverview(); return; }
        this.requestLiveTelemetry('dashboard', (error, data) => {
            if (error || !data || data.error) { this.showTelemetryFreshness(null, true); return; }
            this.updateDashboardMetrics(data);
        });
    },

    startLivePolling: function() {
        if (this.pollTimer) clearInterval(this.pollTimer);
        if (!this.liveTelemetry || this.liveTelemetry.closed) this.liveTelemetry = new UniselvLiveTelemetry(this);
        this.pollTimer = setInterval(() => this.refreshLiveTelemetry(), 10000);
        if (this.freshnessTimer) clearInterval(this.freshnessTimer);
        this.freshnessTimer = setInterval(() => {
            if (!document.hidden && this.telemetryAgeInitialized) this.renderTelemetryFreshness();
        }, 1000);
        if (!this.telemetryLifecycleBound) {
            this.telemetryLifecycleBound = true;
            document.addEventListener('visibilitychange', () => {
                if (!document.hidden && this.pollTimer) this.refreshLiveTelemetry();
            });
            window.addEventListener('pagehide', () => {
                clearInterval(this.pollTimer);
                clearInterval(this.freshnessTimer);
                this.pollTimer = null;
                this.freshnessTimer = null;
                this.liveTelemetry?.close();
            });
            window.addEventListener('pageshow', event => {
                if (event.persisted) { this.startLivePolling(); this.refreshLiveTelemetry(); }
            });
        }
    },

    showTelemetryFreshness: function(epoch, failed = false) {
        this.telemetryAgeInitialized = true;
        this.telemetryLastEpoch = epoch;
        this.telemetryConnectionFailed = failed;
        this.renderTelemetryFreshness();
    },

        renderTelemetryFreshness: function() {
        const epoch = this.telemetryLastEpoch;
        const failed = this.telemetryConnectionFailed;
        const el = document.getElementById(this.isAdmin ? 'admin-telemetry-freshness' : 'uniselv-telemetry-freshness');
        if (!el) return;
        const age = epoch ? Math.max(0, Math.floor(Date.now() / 1000 - epoch)) : null;
        const stale = failed || age === null || age > 180;
        const lastSample = !stale && !this.isAdmin && (!this.isLiveTelemetryVisible() || age > 30);
        el.classList.toggle('badge-last-sample', lastSample);
        const dotClass = stale ? 'dot-danger' : lastSample ? 'dot-neutral' : 'dot-normal';
        if (stale) el.classList.add('badge-stale');
        else el.classList.remove('badge-stale');
        const msg = failed ? this.translate('telemetry_offline', 'Telemetry offline') :
            (age === null ? this.translate('telemetry_waiting', 'Waiting for telemetry') :
                this.translate(stale ? 'telemetry_stale' : lastSample ? 'telemetry_last_sample' : 'telemetry_live', stale ? 'Stale telemetry' : lastSample ? 'Last sample' : 'Live telemetry'));
        if (el.dataset.status !== msg) {
            el.dataset.status = msg;
            el.innerHTML = '<span aria-hidden="true" class="uniselv-live-dot"></span> <span></span><span aria-hidden="true"></span>';
            el.children[1].textContent = msg;
        }
        el.firstElementChild.className = 'uniselv-live-dot ' + dotClass;
        el.lastElementChild.textContent = !failed && age !== null ? '· ' + age + 's' : '';
    },

    sparklineSamples: [],
    updateMeasuredSparklines: function(cur) {
        const epoch = Number(cur.last_sample_epoch);
        if (!Number.isFinite(epoch) || epoch <= 0) return;
        let samples = this.sparklineSamples;
        if (!samples.length || samples[samples.length - 1].t < epoch) {
            samples.push({t: epoch, cpu: Number(cur.cpu_percent), mem: Number(cur.mem_current_bytes),
                          io: Number(cur.read_bytes_sec) + Number(cur.write_bytes_sec), tasks: Number(cur.tasks_current)});
        }
        samples = this.sparklineSamples = samples.filter(p => p.t >= epoch - 300);
        if (samples.length < 2) {
            document.querySelectorAll('.uniselv-sparkline-wrap').forEach(w => delete w.dataset.measured);
            return;
        }
        for (const metric of ['cpu', 'mem', 'io', 'tasks']) {
            const wrap = document.querySelector(`#uniselv-card-${metric} .uniselv-sparkline-wrap`);
            if (!wrap || samples.some(p => !Number.isFinite(p[metric]))) continue;
            const max = Math.max(1, ...samples.map(p => p[metric]));
            const span = Math.max(1, samples[samples.length-1].t - samples[0].t);
            const coords = samples.map(p => `${((p.t-samples[0].t)/span*100).toFixed(2)} ${(38-p[metric]/max*36).toFixed(2)}`);
            const line = 'M' + coords.join(' L');
            const paths = wrap.querySelectorAll('path');
            if (paths.length < 2) continue;
            paths[0].setAttribute('d', line + ' L100 40 L0 40 Z');
            paths[1].setAttribute('d', line);
            wrap.dataset.measured = 'true';
            wrap.title = `Measured trend: ${samples.length} samples since this page opened, up to 5 minutes. Each card uses its own vertical scale.`;
        }
    },

    metricNumber: function(value) {
        if (!['number','string'].includes(typeof value) || (typeof value==='string' && value.trim()==='')) return null;
        const number = Number(value);
        return Number.isFinite(number) ? number : null;
    },

    adminGaugePercentages: function(host, shield) {
        const calc = shield.configured_policy || {};
        const cores = this.metricNumber(host.cpu_cores ?? host.cpu_count);
        const quota = this.metricNumber(shield.customer_cpu_percent ?? calc.customerCpuPercent);
        const load = host.telemetry_available === false ? null : this.metricNumber(host.load1);
        const used = this.metricNumber(shield.golden_mem_current_bytes);
        const maxBytes = this.metricNumber(shield.golden_mem_max_bytes);
        const percent = this.metricNumber(shield.golden_mem_percent);
        return {hardware:null, cpu:cores>0 && quota!==null ? quota/(cores*100)*100 : null,
            ram:used!==null && maxBytes>0 ? used/maxBytes*100 : percent,
            load:cores>0 && load!==null ? load/cores*100 : null};
    },

    updateGaugeCard: function(cardType, percent) {
        const number = this.metricNumber(percent);
        const known = number !== null;
        const validPct = known ? Math.max(0, Math.min(100, number)) : 0;
        const arc = document.getElementById('uniselv-arc-' + cardType);
        if (arc) {
            // SVG pathLength normalizes circle circumference to 100 units.
            arc.setAttribute('pathLength','100');
            arc.setAttribute('stroke-dasharray','100');
            arc.style.strokeDashoffset = String(100-validPct);
            arc.style.opacity = known && validPct>0 ? '1' : '0';
            arc.dataset.percent = known ? String(validPct) : '';
        }
        const thumb = document.getElementById('uniselv-thumb-rot-' + cardType);
        if (thumb) {
            thumb.style.transform = `rotate(${validPct*3.6}deg)`;
            thumb.style.opacity = known && validPct>0 ? '1':'0';
        }
        const wave = document.getElementById('uniselv-wave-' + cardType);
        if (wave) wave.style.height = `${validPct}%`;
        const wrap = arc?.closest('.uniselv-gauge-wrap');
        if (wrap) {
            wrap.dataset.metricState = known ? 'measured':'unavailable';
            wrap.title = known ? `${number.toFixed(1)}% of this metric boundary${number>100 ? ' (visual fill capped at 100%)':''}` : 'No usage percentage is represented.';
        }
    },

    updateEqualizer: function(eqId, percent, active) {
        const wrap = document.getElementById(eqId);
        if (!wrap) return;
        const bars = wrap.querySelectorAll('.eq-bar');
        if (!bars.length) return;
        const p = Math.max(10, Math.min(100, parseFloat(percent) || 0));
        const factors = [0.65, 1.15, 0.8, 1.25, 0.7, 1.05, 0.9];
        bars.forEach((bar, idx) => {
            const factor = factors[idx % factors.length];
            const h = active ? Math.min(100, Math.max(15, Math.round(p * factor))) : 15;
            bar.style.height = h + '%';
            if (active) bar.classList.add('eq-active');
            else bar.classList.remove('eq-active');
        });
    },

    updateAdminSparkline: function(wrapId, val, epoch) {
        const wrap=document.getElementById(wrapId);
        if(!wrap)return;
        const value=this.metricNumber(val), timestamp=this.metricNumber(epoch);
        if(value===null || timestamp===null || timestamp<=0){delete wrap.dataset.measured;return;}
        if(!this.adminSparkSamples)this.adminSparkSamples={};
        const arr=this.adminSparkSamples[wrapId] ||= [];
        if(!arr.length || arr[arr.length-1].t<timestamp)arr.push({t:timestamp,v:value});
        if(arr.length>20)arr.shift();
        if(arr.length<2){delete wrap.dataset.measured;return;}
        wrap.dataset.measured='true';
        wrap.title='Measured samples since this page opened; independently scaled trend, not an absolute percentage gauge.';
        const minVal = Math.min(...arr.map(p => p.v));
        const maxVal = Math.max(1, ...arr.map(p => p.v));
        const range = (maxVal - minVal) || 1;
        const coords = arr.map((p, idx) => {
            const x = (idx / (arr.length - 1) * 100).toFixed(1);
            const y = (36 - ((p.v - minVal) / range) * 28).toFixed(1);
            return `${x} ${y}`;
        });
        const line = 'M' + coords.join(' L');
        const paths = wrap.querySelectorAll('path');
        if (paths.length >= 2) {
            paths[0].setAttribute('d', line + ' L100 40 L0 40 Z');
            paths[1].setAttribute('d', line);
        }
    },

    updateDashboardMetrics: function(dash) {
        const cur = dash.current || {};
        this.showTelemetryFreshness(dash.telemetry_available === false ? null : cur.last_sample_epoch);
        if (dash.telemetry_available === false) return;
        this.updateMeasuredSparklines(cur);
        const limits = dash.limits || {};

        const permissions = dash.permissions || {};
        const thresholds = dash.thresholds || {};

        const warnCpu = thresholds.alert_threshold_cpu || 75;
        const warnMem = thresholds.alert_threshold_mem || 80;
        const warnTasks = thresholds.alert_threshold_tasks || 80;

        // 1. CPU Metrics
        const cpuVal = (typeof cur.cpu_used_percent_core !== 'undefined') ? cur.cpu_used_percent_core : (typeof cur.cpu_percent !== 'undefined' ? cur.cpu_percent : 0);
        const cpuAllowance = (typeof cur.cpu_allowance_percent !== 'undefined') ? cur.cpu_allowance_percent : 0;
        const cpuQuota = limits.cpu_quota_percent || limits.cpuquota || 100;
        const cpuBadge = (cpuAllowance > 90) ? 'badge-critical' : ((cpuAllowance >= warnCpu) ? 'badge-warning' : 'badge-normal');
        const cpuStatus = (cpuAllowance > 90) ? 'LIMIT EXCEEDED' : ((cpuAllowance >= warnCpu) ? 'ELEVATED' : 'NORMAL');

        const cpuValEl = document.getElementById('uniselv-val-cpu');
        if (cpuValEl) cpuValEl.innerText = `${cpuVal}%`;
        const cpuCoreEl = document.getElementById('uniselv-core-cpu');
        if (cpuCoreEl) cpuCoreEl.innerText = `(${Math.round(cpuVal / 100 * 100) / 100} Core)`;

        const cpuBarEl = document.getElementById('uniselv-bar-cpu');
        if (cpuBarEl) {
            cpuBarEl.style.width = Math.min(100, Math.max(0, cpuAllowance)) + '%';
            cpuBarEl.className = 'uniselv-progress-bar bar-cpu ' + ((cpuAllowance > 90) ? 'bg-danger' : ((cpuAllowance >= warnCpu) ? 'bg-warning' : ''));
        }
        const cpuBadgeEl = document.getElementById('uniselv-badge-cpu');
        if (cpuBadgeEl) {
            cpuBadgeEl.className = 'uniselv-badge ' + cpuBadge;
            cpuBadgeEl.innerText = cpuStatus;
        }
        const cpuSubEl = document.getElementById('uniselv-sub-cpu');
        if (cpuSubEl) cpuSubEl.innerHTML = `Allowance: <strong>${cpuAllowance}%</strong> used of ${cpuQuota}% limit (100% = 1 CPU Core)`;

        // 2. Memory Metrics
        const memFormatted = cur.mem_current_formatted || '0 B';
        const memPct = cur.mem_percent || 0;
        const memLimit = limits.mem_max_formatted || '1.0 GiB';
        const memBadge = (memPct > 90) ? 'badge-critical' : ((memPct >= warnMem) ? 'badge-warning' : 'badge-normal');
        const memStatus = (memPct > 90) ? 'HIGH PRESSURE' : ((memPct >= warnMem) ? 'MODERATE' : 'NORMAL');

        const memValEl = document.getElementById('uniselv-val-mem');
        if (memValEl) memValEl.innerText = memFormatted;
        const memBarEl = document.getElementById('uniselv-bar-mem');
        if (memBarEl) {
            memBarEl.style.width = Math.min(100, Math.max(0, memPct)) + '%';
            memBarEl.className = 'uniselv-progress-bar bar-mem ' + ((memPct > 90) ? 'bg-danger' : ((memPct >= warnMem) ? 'bg-warning' : ''));
        }
        const memBadgeEl = document.getElementById('uniselv-badge-mem');
        if (memBadgeEl) {
            memBadgeEl.className = 'uniselv-badge ' + memBadge;
            memBadgeEl.innerText = memStatus;
        }
        const memSubEl = document.getElementById('uniselv-sub-mem');
        if (memSubEl) memSubEl.innerHTML = `Limit: <strong>${memLimit}</strong> (App: ${cur.mem_anon_formatted ?? 'Unavailable'} | Cache: ${cur.mem_file_cache_formatted ?? 'Unavailable'})`;

        // 3. I/O Metrics
        const ioRead = cur.read_bw_formatted || '0.0 MiB/s';
        const ioWrite = cur.write_bw_formatted || '0.0 MiB/s';
        const ioTotal = cur.total_bw_formatted || `${(parseFloat(ioRead) + parseFloat(ioWrite)).toFixed(2)} MiB/s`;
        const iopsRead = cur.read_iops || 0;
        const iopsWrite = cur.write_iops || 0;
        const ioValEl = document.getElementById('uniselv-val-io');
        if (ioValEl) ioValEl.innerText = cur.total_bw_formatted || ioTotal;
        const ioSubEl = document.getElementById('uniselv-sub-io');
        const ioLimitText = (limits.read_bw_formatted && limits.write_bw_formatted) ? ` | Limit: ${limits.read_bw_formatted} R / ${limits.write_bw_formatted} W` : '';
        if (ioSubEl) ioSubEl.innerText = `Read: ${ioRead} | Write: ${ioWrite} | IOPS: ${iopsRead} R / ${iopsWrite} W${ioLimitText}`;

        let ioPct = 0;
        if (typeof cur.io_percent !== 'undefined') {
            ioPct = parseFloat(cur.io_percent);
        } else {
            const limitReadBytes = limits.read_bw_bytes || 230686720;
            const limitWriteBytes = limits.write_bw_bytes || 138412032;
            const curR = parseFloat(cur.read_bytes_sec || 0);
            const curW = parseFloat(cur.write_bytes_sec || 0);
            const rRatio = limitReadBytes > 0 ? (curR / limitReadBytes) : 0;
            const wRatio = limitWriteBytes > 0 ? (curW / limitWriteBytes) : 0;
            ioPct = Math.round(Math.max(rRatio, wRatio) * 1000) / 10;
        }

        const ioBarEl = document.getElementById('uniselv-bar-io');
        if (ioBarEl) {
            ioBarEl.style.width = Math.min(100, Math.max(0, ioPct)) + '%';
            ioBarEl.className = 'uniselv-progress-bar bar-io ' + ((ioPct > 90) ? 'bg-danger' : ((ioPct >= 65) ? 'bg-warning' : ''));
        }
        const ioBadgeEl = document.getElementById('uniselv-badge-io');
        if (ioBadgeEl) {
            const ioStatus = (ioPct > 90) ? 'THROTTLED' : ((ioPct >= 65) ? 'ELEVATED' : 'NORMAL');
            const ioBadge = (ioPct > 90) ? 'badge-critical' : ((ioPct >= 65) ? 'badge-warning' : 'badge-normal');
            ioBadgeEl.className = 'uniselv-badge ' + ioBadge;
            ioBadgeEl.innerText = ioStatus;
        }

        // 4. Tasks Metrics
        const tasksCur = cur.tasks_current || 0;
        const tasksMax = limits.tasks_max || limits.maxtask || 64;
        const tasksPct = cur.tasks_percent || 0;
        const tasksBadge = (tasksPct > 90) ? 'badge-critical' : ((tasksPct >= warnTasks) ? 'badge-warning' : 'badge-normal');
        const tasksStatus = (tasksPct > 90) ? 'TASK LIMIT NEAR' : ((tasksPct >= warnTasks) ? 'ELEVATED' : 'NORMAL');

        const tasksValEl = document.getElementById('uniselv-val-tasks');
        if (tasksValEl) tasksValEl.innerText = tasksCur;
        const tasksMaxEl = document.getElementById('uniselv-max-tasks');
        if (tasksMaxEl) tasksMaxEl.innerText = `/ ${tasksMax}`;
        const tasksSubEl = document.getElementById('uniselv-sub-tasks');
        if (tasksSubEl) tasksSubEl.innerHTML = `Includes Linux process threads. Limit: <strong>${tasksMax}</strong> max`;

        const tasksBarEl = document.getElementById('uniselv-bar-tasks');
        if (tasksBarEl) {
            tasksBarEl.style.width = Math.min(100, Math.max(0, tasksPct)) + '%';
            tasksBarEl.className = 'uniselv-progress-bar bar-tasks ' + ((tasksPct > 90) ? 'bg-danger' : ((tasksPct >= warnTasks) ? 'bg-warning' : ''));
        }
        const tasksBadgeEl = document.getElementById('uniselv-badge-tasks');
        if (tasksBadgeEl) {
            tasksBadgeEl.className = 'uniselv-badge ' + tasksBadge;
            tasksBadgeEl.innerText = tasksStatus;
        }

                this.updateGaugeCard('cpu', cpuAllowance);
        this.updateGaugeCard('mem', memPct);
        this.updateGaugeCard('io', ioPct);
        this.updateGaugeCard('tasks', tasksPct);
        const ioActive = ((Number(cur.read_bytes_sec) || 0) + (Number(cur.write_bytes_sec) || 0)) > 0;
        this.updateEqualizer('uniselv-eq-io', ioPct, ioActive);
        this.updateEqualizer('uniselv-eq-tasks', tasksPct, (Number(cur.tasks_current) || 0) > 0);

        // Apply Enduser Permissions
        if (permissions.allow_kill === false) {
            document.querySelectorAll('.uniselv-stop-proc-btn').forEach(btn => {
                btn.disabled = true;
                btn.style.opacity = '0.4';
                btn.title = 'Process termination disabled by administrator';
            });
        }
        if (permissions.allow_export === false) {
            const expBtn = document.getElementById('uniselv-export-btn');
            if (expBtn) {
                expBtn.disabled = true;
                expBtn.style.opacity = '0.4';
                expBtn.title = 'Support report export disabled by administrator';
            }
        }

        // Animated pulse highlight on cards
        ['uniselv-card-cpu', 'uniselv-card-mem', 'uniselv-card-io', 'uniselv-card-tasks'].forEach(id => {
            const el = document.getElementById(id);
            if (el) {
                el.classList.remove('uniselv-card-pulse');
                void el.offsetWidth;
                el.classList.add('uniselv-card-pulse');
            }
        });
    },

    loadFeatureSettings: function() {
        this.callApi('get_feature_settings', {}, (err, res) => {
            if (err || res.error) {
                console.error("Failed to load feature settings:", err || res.error);
                return;
            }
            const s = res.settings || {};

            const setCheck = (id, val) => {
                const el = document.getElementById(id);
                if (el) el.checked = (val !== false && val !== '0' && val !== 0);
            };
            const setVal = (id, val) => {
                const el = document.getElementById(id);
                if (el && typeof val !== 'undefined') el.value = val;
            };

            setCheck('setting-telemetry-enabled', s.telemetry_enabled);
            setVal('setting-telemetry-interval', s.telemetry_interval || 5);
            setCheck('setting-auto-prune', s.auto_prune_hourly);

            setCheck('setting-snap-throttle', s.snapshot_on_throttle);
            setCheck('setting-snap-oom', s.snapshot_on_oom);
            setCheck('setting-snap-task', s.snapshot_on_task_limit);
            setVal('setting-snap-cooldown', s.snapshot_cooldown_sec || 60);

            setVal('setting-thresh-cpu', s.alert_threshold_cpu || 75);
            setVal('setting-thresh-mem', s.alert_threshold_mem || 80);
            setVal('setting-thresh-tasks', s.alert_threshold_tasks || 80);

            setCheck('setting-allow-kill', s.enduser_allow_kill);
            setCheck('setting-allow-export', s.enduser_allow_export);
            setCheck('setting-allow-db-trace', s.enduser_allow_db_trace);
        });
    },

    saveFeatureSettings: function() {
        const getCheck = (id) => {
            const el = document.getElementById(id);
            return el ? (el.checked ? 1 : 0) : 1;
        };
        const getVal = (id, def) => {
            const el = document.getElementById(id);
            return el ? parseInt(el.value, 10) : def;
        };

        const payload = {
            telemetry_enabled: getCheck('setting-telemetry-enabled'),
            telemetry_interval: getVal('setting-telemetry-interval', 5),
            auto_prune_hourly: getCheck('setting-auto-prune'),
            snapshot_on_throttle: getCheck('setting-snap-throttle'),
            snapshot_on_oom: getCheck('setting-snap-oom'),
            snapshot_on_task_limit: getCheck('setting-snap-task'),
            snapshot_cooldown_sec: getVal('setting-snap-cooldown', 60),
            alert_threshold_cpu: getVal('setting-thresh-cpu', 75),
            alert_threshold_mem: getVal('setting-thresh-mem', 80),
            alert_threshold_tasks: getVal('setting-thresh-tasks', 80),
            enduser_allow_kill: getCheck('setting-allow-kill'),
            enduser_allow_export: getCheck('setting-allow-export'),
            enduser_allow_db_trace: getCheck('setting-allow-db-trace')
        };

        const btn = document.getElementById('btn-save-features');
        if (btn) {
            btn.disabled = true;
            btn.innerHTML = '<span class="uniselv-live-dot" style="background:#fff; margin-right:6px;"></span> Saving...';
        }

        this.callApi('save_feature_settings', payload, (err, res) => {
            if (btn) {
                btn.disabled = false;
                btn.innerHTML = '<svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg> Save Feature Settings';
            }
            if (err || res.error) {
                UniselvNotify.error(`Failed to save settings: ${err || res.error}`);
            } else {
                UniselvNotify.success(res.message || 'System settings and feature policies saved successfully.');
                this.loadFeatureSettings();
            }
        });
    },

    enableGoldenShield: function() {
        UniselvModal.confirm({
            title: 'Enable Golden Shield Governor?',
            message: 'This will dynamically calculate CPU headroom and memory safety caps based on detected hardware, create golden.slice kernel limits, and update persistent systemd drop-ins.',
            icon: 'success',
            confirmText: 'Enable Governor',
            isDanger: false,
            onConfirm: () => {
                this.callApi('golden_enable', {}, (err, res) => {
                    if (err || res.error) {
                        UniselvNotify.error(`Failed to enable Golden Shield: ${err || res.error}`);
                    } else {
                        UniselvNotify.success(res.message || 'Golden Shield enabled and verified successfully.');
                        setTimeout(() => location.reload(), 1200);
                    }
                });
            }
        });
    },

    loadStorageSettings: function() {
        this.callApi('get_storage_settings', {}, (err, res) => {
            if (err || res.error) {
                console.error("Failed to load storage settings:", err || res.error);
                return;
            }
            const s = res.settings || {};
            const st = res.storage || {};

            if (document.getElementById('retention-samples')) document.getElementById('retention-samples').value = s.samples_days || 30;
            if (document.getElementById('retention-snapshots')) document.getElementById('retention-snapshots').value = s.snapshots_days || 14;
            if (document.getElementById('retention-events')) document.getElementById('retention-events').value = s.events_days || 30;
            if (document.getElementById('retention-audit')) document.getElementById('retention-audit').value = s.audit_days || 90;
            if (document.getElementById('retention-max-storage')) document.getElementById('retention-max-storage').value = s.max_storage_mib || 100;

            if (document.getElementById('storage-total-display')) document.getElementById('storage-total-display').innerText = st.total_formatted ?? 'Unavailable';
            if (document.getElementById('storage-limit-display')) document.getElementById('storage-limit-display').innerText = (s.max_storage_mib || 100) + ' MiB';
            const storagePct = Number(st.used_percent);
            const storageKnown = st.used_percent != null && Number.isFinite(storagePct) && storagePct >= 0;
            const storageWarning = storageKnown && storagePct >= 100;
            const storageFill = document.getElementById('storage-bar-fill');
            if (storageFill) {
                storageFill.style.width = (storageKnown ? Math.min(100, storagePct) : 0) + '%';
                storageFill.style.background = storageWarning ? '#f59e0b' : '';
            }
            const storageBadge = document.getElementById('storage-used-pct');
            if (storageBadge) {
                storageBadge.textContent = storageKnown ? storagePct + '%' : 'Unavailable';
                storageBadge.className = 'uniselv-badge ' + (storageWarning ? 'badge-warning' : 'badge-normal');
            }
            if (document.getElementById('storage-samples-count')) document.getElementById('storage-samples-count').innerText = st.samples_count || 0;
            if (document.getElementById('storage-snapshots-count')) document.getElementById('storage-snapshots-count').innerText = st.snapshots_count || 0;
            if (document.getElementById('storage-events-count')) document.getElementById('storage-events-count').innerText = st.events_count || 0;
            if (document.getElementById('storage-audit-count')) document.getElementById('storage-audit-count').innerText = st.audit_count || 0;
        });
    },

    saveStorageSettings: function() {
        const sDays = document.getElementById('retention-samples').value;
        const snDays = document.getElementById('retention-snapshots').value;
        const eDays = document.getElementById('retention-events').value;
        const aDays = document.getElementById('retention-audit').value;
        const maxMib = document.getElementById('retention-max-storage').value;

        const btn = document.getElementById('btn-save-retention');
        if (btn) btn.disabled = true;

        this.callApi('save_storage_settings', {
            samples_days: sDays,
            snapshots_days: snDays,
            events_days: eDays,
            audit_days: aDays,
            max_storage_mib: maxMib
        }, (err, res) => {
            if (btn) btn.disabled = false;
            if (err || res.error) {
                UniselvNotify.error(`Error saving retention settings: ${err || res.error}`);
            } else {
                UniselvNotify.success(res.message || 'Retention settings saved successfully.');
                this.loadStorageSettings();
            }
        });
    },

    pruneDatabaseNow: function() {
        UniselvModal.confirm({
            title: 'Optimize Telemetry Database?',
            message: 'This will purge data older than your retention thresholds, truncate Write-Ahead Logs, and reclaim disk space using SQLite VACUUM.',
            icon: 'warning',
            confirmText: 'Prune & Optimize',
            isDanger: false,
            onConfirm: () => {
                const btn = document.getElementById('btn-prune-db');
                if (btn) {
                    btn.disabled = true;
                    btn.innerText = 'Optimizing & Reclaiming...';
                }

                this.callApi('prune_database', { vacuum: 1 }, (err, res) => {
                    if (btn) {
                        btn.disabled = false;
                        btn.innerText = 'Prune & Optimize Database Now';
                    }
                    if (err || res.error) {
                        UniselvNotify.error(`Optimization failed: ${err || res.error}`);
                    } else {
                        const det = res.prune_details || res.prune_results || {};
                        const delSamples = (typeof det.deleted_samples !== 'undefined') ? det.deleted_samples : (res.deleted_samples || 0);
                        const delSnaps = (typeof det.deleted_snapshots !== 'undefined') ? det.deleted_snapshots : (res.deleted_snapshots || 0);
                        const freed = det.freed_formatted || res.freed_formatted || '0 B';
                        const footprint = det.current_size_formatted || res.current_size_formatted || 'Bounded';
                        if (det.over_budget) {
                            UniselvNotify.warning('Database remains above the target size. The newest hour of telemetry is protected.');
                        }
                        UniselvNotify.success(
                            `Deleted ${delSamples} samples, ${delSnaps} snapshots. Reclaimed ${freed} space. Footprint: ${footprint}.`,
                            'Database Optimized'
                        );
                        this.loadStorageSettings();
                    }
                });
            }
        });
    },

    openPurgeSnapshotsModal: function() {
        UniselvModal.confirm({
            title: 'Purge Diagnostic Snapshots?',
            message: 'Purge forensic incident snapshots older than 7 days to reclaim disk space? (Live limits and metrics are preserved).',
            icon: 'warning',
            confirmText: 'Purge Snapshots Now',
            isDanger: true,
            onConfirm: () => {
                this.callApi('purge_snapshots', { older_than_days: 7 }, (err, res) => {
                    if (err || res.error) {
                        UniselvNotify.error(`Snapshot purge failed: ${err || res.error}`);
                    } else {
                        UniselvNotify.success(res.message || `Deleted ${res.deleted_snapshots || 0} snapshots.`);
                        this.loadStorageSettings();
                    }
                });
            }
        });
    },

    loadRuntimeGovernance: function() {
        const host = document.getElementById('uniselv-runtime-governance');
        if (!this.isAdmin || !host) return;
        const bind = (id, fn) => {const b=document.getElementById(id);if(b)b.onclick=fn;};
        bind('governance-refresh',()=>this.loadRuntimeGovernance());
        bind('governance-scan',()=>this.runGovernance('scan'));
        bind('governance-recover',()=>this.confirmGovernance('recover'));
        bind('governance-export',()=>this.runGovernance('export'));
        this.callApi('runtime_governance',{},(err,response)=>{
            const data=response?.data || response;
            if(err || !data?.success){host.textContent='Evidence unavailable. Check agent health and retry.';return;}
            const job=document.getElementById('governance-job');
            if(job && !this.governancePolling)job.textContent=data.job ? `Last operation: ${data.job.operation} — ${data.job.state}${data.job.error ? ': '+data.job.error : ''}` : '';
            const value=data.snapshot;host.replaceChildren();
            if(!value){host.textContent='No scan has completed yet. Choose Reconcile PHP Changes.';return;}
            const note=(text)=>{const p=document.createElement('p');p.textContent=text;host.append(p);};
            note(`Observed: ${new Date(value.at*1000).toLocaleString()}${data.stale ? ' — STALE' : ''}. Global setting differences: ${(value.drift || []).length}. ${value.readiness?.scope || ''}`);
            const table=(title,labels,rows)=>{
                const details=document.createElement('details');details.className='uniselv-governance-detail';
                const summary=document.createElement('summary');summary.textContent=title;details.append(summary);
                const wrap=document.createElement('div');wrap.className='uniselv-table-wrap';
                const element=document.createElement('table');element.className='uniselv-table';
                const head=element.createTHead().insertRow();labels.forEach(label=>{const th=document.createElement('th');th.scope='col';th.textContent=label;head.append(th);});
                const body=element.createTBody();rows.forEach(cells=>{const row=body.insertRow();cells.forEach(value=>{const cell=row.insertCell();if(value instanceof Node)cell.append(value);else cell.textContent=String(value ?? 'Unavailable');});});
                if(!rows.length){const cell=body.insertRow().insertCell();cell.colSpan=labels.length;cell.textContent='No entries in this observation.';}
                wrap.append(element);details.append(wrap);host.append(details);return details;
            };
            table('PHP Lifecycle Automation',['Version','State','Last action','Explanation','Maintenance'],Object.entries(value.versions || {}).map(([version,state])=>{
                const b=document.createElement('button');b.className='uniselv-btn btn-outline';b.textContent=state.state==='retired'?'Enable Runtime':'Retire Runtime';b.disabled=!state.managed && state.state!=='retired';b.onclick=()=>state.state==='retired'?this.runGovernance('activate',version):this.confirmGovernance('retire',version);
                return [version,state.state,state.action,state.reason,b];
            })).open=true;
            table('Global Settings Drift — Expected vs Actual',['PHP','Section','Directive','Expected','Actual'],(value.drift || []).map(r=>[r.version,r.section,r.key,r.expected,r.actual]));
            table('Server Configuration Drift — All Reviewed Sections',['Section','Directive','Expected','Actual'],(value.configurationComparison?.mismatches || []).map(r=>[r.section,r.key,r.expected,r.actual]));
            note(value.configurationComparison?.error || `Server comparison: ${value.configurationComparison?.checks ?? 0} configured-value checks; observed ${value.configurationComparison?.at ? new Date(value.configurationComparison.at*1000).toLocaleString() : 'unavailable'}. Workload tests are separate.`);
            table('Configuration Audit Coverage — All Generator Sections',['Section','Checks','Evidence'],(value.configurationComparison?.sectionCoverage || []).map(r=>[r.section,r.checks,r.status]));
            table('Account Inheritance Exceptions',['File','Directive','Override'],(value.inheritance?.rows || []).map(r=>[r.path,r.key,r.value]));
            note(`Override coverage: ${value.inheritance?.scope || 'Unavailable'} Complete within scope: ${value.inheritance?.completeWithinScope ? 'Yes':'No'}. ${value.inheritance?.boundedStopReason || ''}`);
            table('Capacity Events — Last Hour, Bounded Journal Sample',['Reason','Observed events'],Object.entries(value.diagnostics?.counts || {}));
            note(value.diagnostics?.scope || 'Journal diagnostics unavailable.');
            table('Recent Capacity Event Timeline',['Time','Unit','Reason'],(value.diagnostics?.recent || []).map(r=>[r.at ? new Date(r.at*1000).toLocaleString():'Before timestamp instrumentation',r.unit,r.reason]));
            table('Lifecycle Recovery History',['PHP','Operation','Status','Started'],(value.lifecycle?.history || []).map(r=>[r.version,r.operation,r.status,r.startedAt ? new Date(r.startedAt*1000).toLocaleString():'Unavailable']));
            note(value.lifecycle?.pending ? `PENDING: ${value.lifecycle.pending.operation} ${value.lifecycle.pending.version}. ${value.lifecycle.guidance}` : 'No pending lifecycle journal.');
            (value.errors || []).forEach(note);
        },{timeoutMs:15000});
    },

    confirmGovernance: function(operation,version='') {
        UniselvModal.confirm({title:operation==='retire'?'Retire PHP Runtime':'Recover Pending Operation',
            message:operation==='retire'?`Retire ${version} before vendor uninstall. Move all sites first. Native launcher restoration requires valid installation files.`:'Restore the recorded pre-operation state. Conflicting files stop recovery for administrator review.',
            onConfirm:()=>this.runGovernance(operation,version)});
    },

    runGovernance: function(operation,version='') {
        if(this.governancePolling){UniselvNotify.error('Wait for the current operation to finish.');return;}
        this.callApi('run_governance',{operation,version},(err,response)=>{
            const result=response?.data || response;
            if(err || !result?.success || !result.jobId){UniselvNotify.error(result?.error || 'Could not queue operation.');return;}
            this.governancePolling=true;let remaining=100;
            const poll=()=>this.callApi('runtime_governance',{},(error,reply)=>{
                const data=reply?.data || reply;const job=data?.job;const status=document.getElementById('governance-job');
                if(status)status.textContent=`${operation}: ${job?.id===result.jobId ? job.state:'waiting for status'}...`;
                if(!error && job?.id===result.jobId && job.state!=='running'){
                    this.governancePolling=false;
                    if(job.state!=='completed')UniselvNotify.error(job.error || 'Operation failed.');
                    else if(operation==='export')this.downloadGovernanceExport();
                    this.loadRuntimeGovernance();this.loadPhpLifecycle();return;
                }
                if(--remaining>0){setTimeout(poll,3000);return;}
                this.governancePolling=false;if(status)status.textContent='Still running or unavailable. Refresh Evidence later; the server operation continues.';
            },{timeoutMs:10000});poll();
        });
    },

    downloadGovernanceExport: function() {
        this.callApi('export_governance',{},(err,response)=>{
            const data=response?.data || response;
            if(err || !data?.export){UniselvNotify.error('Comparison export unavailable.');return;}
            const url=URL.createObjectURL(new Blob([JSON.stringify(data.export,null,2)],{type:'application/json'}));
            const link=document.createElement('a');link.href=url;link.download='runtime-configuration-comparison.json';link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
        });
    },

    loadPhpLifecycle: function() {
        const host = document.getElementById('uniselv-php-lifecycle');
        if (!this.isAdmin || !host) return;
        host.textContent = 'Loading PHP runtime status...';
        this.callApi('php_lifecycle', {}, (err, res) => {
            const versions = res?.versions || res?.data?.versions;
            if (err || !versions) { host.textContent = 'PHP runtime status unavailable. Check agent health and retry.'; return; }
            const table = document.createElement('table'); table.className = 'uniselv-table';
            const head = table.createTHead().insertRow();
            ['PHP version','Installed','Registered','Coordinator','Health master','Pools'].forEach(label => {
                const th = document.createElement('th'); th.scope = 'col'; th.textContent = label; head.append(th);
            });
            const body = table.createTBody();
            Object.entries(versions).forEach(([version, state]) => {
                const row = body.insertRow();
                [version,state.installed?'Yes':'Missing',state.managed?'Yes':'No',state.coordinator_active?'Active':'Stopped',state.health_master_active?'Active':'Stopped',String(state.pool_count)].forEach(value => { row.insertCell().textContent = value; });
            });
            host.replaceChildren(table);
            if (!Object.keys(versions).length) host.textContent = 'No PHP runtime registrations found.';
        }, {timeoutMs:20000});
    },

    callApi: function(subact, params, callback, options = {}) {
        const url = new URL(this.apiEndpoint, window.location.origin);
        url.searchParams.set('subact', subact);
        url.searchParams.set('api', 'json');

        const postData = new FormData();
        for (let k in params) {
            postData.append(k, params[k]);
        }
        if (this.csrfToken) {
            postData.append('csrf_token', this.csrfToken);
        }

        // Timeout only bounded read-only telemetry; long-running mutations keep
        // their existing lifecycle and are never cached or sent across tabs.
        const controller = options.timeoutMs && typeof AbortController !== 'undefined' ? new AbortController() : null;
        let finished = false;
        let timer = null;
        const finish = (error, data) => {
            if (finished) return;
            finished = true;
            if (timer) clearTimeout(timer);
            callback(error, data);
        };
        if (controller) timer = setTimeout(() => controller.abort(), options.timeoutMs);
        fetch(url.toString(), {
            method: 'POST', body: postData,
            ...(controller ? {signal: controller.signal} : {})
        }).then(response => {
            if (!response.ok) throw new Error('Request failed (HTTP ' + response.status + ')');
            return response.json();
        }).then(data => finish(null, data), error => finish(error, null));
        return () => { if (controller) controller.abort(); };

    },

    latestRead: function(view, action, params, callback) {
        this.pendingReads ??= new Map();
        const previous = this.pendingReads.get(view);
        const request = {};
        this.pendingReads.set(view, request);
        previous?.cancel?.();
        request.cancel = this.callApi(action, params, (err, res) => {
            if (this.pendingReads.get(view) !== request) return;
            this.pendingReads.delete(view);
            if (view.startsWith('admin-') && this.selectedAdminUser && params.username !== this.selectedAdminUser) return;
            callback(err, res);
        }, {timeoutMs: 17000});
    },

    showUsageError: function(grid, tables, message, retry) {
        for (const [table, columns] of tables) {
            if (!table) continue;
            table.innerHTML = '<tr><td class="uniselv-request-error" colspan="' + columns + '"></td></tr>';
            table.rows[0].cells[0].textContent = message;
        }
        if (!grid) return;
        const notice = document.createElement('div');
        notice.className = 'uniselv-request-error';
        notice.style.gridColumn = '1 / -1';
        notice.setAttribute('role', 'status');
        notice.append(document.createTextNode(message + ' '));
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'uniselv-btn btn-outline';
        button.textContent = this.translate('retry', 'Retry');
        button.addEventListener('click', retry);
        notice.appendChild(button);
        grid.replaceChildren(notice);
    },

    renderChartsToContainer: function(chartContainer, points) {
        chartContainer.innerHTML = '';
        const cpuData = points.map(p => ({ x: Number(p.t) || 0, y: Number(p.cpu) || 0, limit: Number(p.limit_cpu) || 0 }));
        chartContainer.appendChild(this.renderSvgChart(this.translate('chart_cpu', 'CPU usage') + ' (100% = 1 vCPU)', cpuData, '%', '#2563eb'));

        const memData = points.map(p => ({ x: Number(p.t) || 0, y: Math.round((Number(p.mem) || 0) / 1024 / 1024), limit: Math.round((Number(p.limit_mem) || 0) / 1024 / 1024) }));
        chartContainer.appendChild(this.renderSvgChart(this.translate('chart_mem', 'Memory usage'), memData, 'MiB', '#059669'));

        const taskData = points.map(p => ({ x: Number(p.t) || 0, y: Number(p.tasks) || 0, limit: Number(p.limit_tasks) || 0 }));
        chartContainer.appendChild(this.renderSvgChart(this.translate('chart_tasks', 'Active tasks and threads'), taskData, 'tasks', '#7c3aed'));

        const ioData = points.map(p => ({ x: Number(p.t) || 0, y: Math.round(((Number(p.read_bw) || 0) + (Number(p.write_bw) || 0)) / 1024), limit: 0 }));
        chartContainer.appendChild(this.renderSvgChart(this.translate('chart_io', 'Disk throughput'), ioData, 'KiB/s', '#d97706'));
    },

    // ==================== CPANEL CURRENT USAGE & 8 CHARTS ENGINE ====================
    loadCurrentUsage: function(timeframe) {
        timeframe = timeframe || 'today';
        const dateEl = document.getElementById('uniselv-usage-date-str');
        if (dateEl) {
            dateEl.innerText = new Date().toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' });
        }

        const totalTbody = document.getElementById('uniselv-account-total-tbody');
        const gridEl = document.getElementById('uniselv-usage-8charts-grid');
        const rollupTbody = document.getElementById('uniselv-usage-rollup-tbody');
        this.hourlyUsageRecords = [];
        document.getElementById('uniselv-usage-rollup-pagination')?.replaceChildren();

        if (totalTbody) totalTbody.innerHTML = '<tr><td colspan="4" style="text-align:center; color:#64748b; padding:20px;">Loading account totals...</td></tr>';
        if (gridEl) gridEl.innerHTML = '<div style="grid-column: 1 / -1; text-align:center; color:#64748b; padding:40px; background:#fff; border:1px solid var(--uniselv-border); border-radius:8px;">Loading resource charts...</div>';
        if (rollupTbody) rollupTbody.innerHTML = '<tr><td colspan="20" style="text-align:center; color:#64748b; padding:24px;">Loading hourly usage records...</td></tr>';

        this.latestRead('enduser-usage', 'history', { range: timeframe, username: this.currentUser }, (err, res) => {
            if (err || !res || res.error) {
                const message = String(err?.message || res?.error || this.translate('telemetry_offline', 'Telemetry offline'));
                this.showUsageError(gridEl, [[totalTbody, 4], [rollupTbody, 20]], message, () => this.loadCurrentUsage(timeframe));
                return;
            }

            // 1. Render Account Total Card
            if (totalTbody) {
                const totals = res.account_total || [];
                if (totals.length === 0) {
                    totalTbody.innerHTML = '<tr><td colspan="4" style="text-align:center; color:#64748b; padding:16px;">No account totals recorded.</td></tr>';
                } else {
                    let html = '';
                    totals.forEach(r => {
                        const faultHtml = (r.fault > 0) ? `<span class="uniselv-fault-badge">${r.fault}</span>` : '0';
                        let usageStr = r.usage;
                        if (typeof usageStr === 'string' && usageStr.includes('B/s')) {
                            const parts = usageStr.split(' ');
                            const num = parseFloat(parts[0]);
                            if (!isNaN(num)) {
                                usageStr = (num >= 100 ? num.toFixed(1) : num.toFixed(2)) + ' ' + (parts.slice(1).join(' ') || 'B/s');
                            }
                        }
                        html += `
                            <tr>
                                <td style="font-weight:600; color:#1e293b;">${this.escapeHtml(r.desc)}</td>
                                <td style="font-weight:600;">${this.escapeHtml(usageStr)}</td>
                                <td style="color:#64748b;">${this.escapeHtml(r.limit)}</td>
                                <td>${faultHtml}</td>
                            </tr>
                        `;
                    });
                    totalTbody.innerHTML = html;
                }
            }

            // 2. Render 8 Interactive Charts Grid
            if (gridEl) {
                gridEl.innerHTML = '';
                const pts = res.points || [];
                if (pts.length < 2) {
                    gridEl.innerHTML = '<div style="grid-column: 1 / -1; text-align:center; color:#64748b; padding:40px; background:#fff; border:1px solid var(--uniselv-border); border-radius:8px;">Not enough telemetry points collected for this timeframe yet. Telemetry daemon is actively sampling.</div>';
                } else {
                    // Chart 1: CPU (SPEED)
                    const cpuData = pts.map(p => ({ x: p.t, y: p.speed, limit: p.limit_speed }));
                    const cpuAvg = (cpuData.reduce((s, p) => s + p.y, 0) / cpuData.length).toFixed(1);
                    const cpuMax = Math.max(...cpuData.map(p => p.y)).toFixed(1);
                    gridEl.appendChild(this.renderUsage8Chart(this.translate('chart_cpu', 'CPU usage') + ' (100% = 1 vCPU)', cpuData, '%', '#2563eb', `Plotted avg: ${cpuAvg}% | max: ${cpuMax}%`));

                    // Chart 2: Virtual memory (RAM + Swap)
                    const vmemData = pts.map(p => ({ x: p.t, y: p.vmem, limit: p.limit_vmem }));
                    const vmemMax = Math.max(...vmemData.map(p => p.y)).toFixed(1);
                    gridEl.appendChild(this.renderUsage8Chart(this.translate('chart_vmem', 'Virtual memory (RAM + Swap)'), vmemData, 'MiB', '#6366f1', `Plotted max: ${vmemMax} MiB; historical limit unavailable`));

                    // Chart 3: Physical memory
                    const pmemData = pts.map(p => ({ x: p.t, y: p.pmem, limit: p.limit_pmem }));
                    const pmemMax = Math.max(...pmemData.map(p => p.y)).toFixed(1);
                    const pmemAvg = (pmemData.reduce((s, p) => s + p.y, 0) / pmemData.length).toFixed(1);
                    gridEl.appendChild(this.renderUsage8Chart(this.translate('chart_mem', 'Memory usage'), pmemData, 'MiB', '#059669', `Plotted avg: ${pmemAvg} MiB | max: ${pmemMax} MiB`));

                    // Chart 4: IO
                    const ioData = pts.map(p => ({ x: p.t, y: p.io, limit: p.limit_io }));
                    const ioMax = Math.max(...ioData.map(p => p.y)).toFixed(1);
                    gridEl.appendChild(this.renderUsage8Chart(this.translate('chart_io', 'Disk throughput'), ioData, 'KiB/s', '#d97706', `Plotted max: ${ioMax} KiB/s`));

                    // Chart 5: IOPS
                    const iopsData = pts.map(p => ({ x: p.t, y: p.iops, limit: p.limit_iops }));
                    const iopsMax = Math.max(...iopsData.map(p => p.y)).toFixed(0);
                    gridEl.appendChild(this.renderUsage8Chart('IOPS', iopsData, 'iops', '#0891b2', `Max: ${iopsMax} iops`));

                    // Chart 6: Entry processes
                    const epData = pts.map(p => ({ x: p.t, y: p.ep, limit: p.limit_ep }));
                    const hasEp = pts.some(p => p.ep !== null && p.ep !== undefined);
                    const epStat = hasEp ? `Max: ${Math.max(...epData.filter(p => p.y !== null).map(p => p.y)).toFixed(1)} EP` : 'N/A (Governed via NPROC)';
                    gridEl.appendChild(this.renderUsage8Chart(this.translate('chart_ep', 'Entry processes'), epData, 'EP', '#7c3aed', epStat));

                    // Chart 7: Processes
                    const nprocData = pts.map(p => ({ x: p.t, y: p.nproc, limit: p.limit_nproc }));
                    const nprocMax = Math.max(...nprocData.map(p => p.y));
                    gridEl.appendChild(this.renderUsage8Chart(this.translate('chart_tasks', 'Active tasks and threads'), nprocData, 'procs', '#4f46e5', `Max: ${nprocMax}`));

                    // Chart 8: Faults
                    const faultData = pts.map(p => ({ x: p.t, y: p.faults, limit: 0 }));
                    const faultTot = faultData.reduce((s, p) => s + p.y, 0);
                    gridEl.appendChild(this.renderUsage8Chart(this.translate('chart_faults', 'Faults'), faultData, 'events', '#dc2626', `Total: ${faultTot} events`));
                }
            }

            // 3. Render Usage Historical Rollup Table with client-side pagination
            this.hourlyUsageRecords = res.hourly_usage || [];
            this.rollupCurrentPage = 1;
            this.renderRollupPage();
        });
    },

    hourlyUsageRecords: [],
    rollupCurrentPage: 1,
    rollupPageSize: 12,

    renderRollupPage: function() {
        const rollupTbody = document.getElementById('uniselv-usage-rollup-tbody');
        if (!rollupTbody) return;

        const hourly = this.hourlyUsageRecords || [];
        if (hourly.length === 0) {
            rollupTbody.innerHTML = '<tr><td colspan="20" style="text-align:center; color:#64748b; padding:24px;">No historical telemetry records logged yet for this period.</td></tr>';
            const pag = document.getElementById('uniselv-usage-rollup-pagination');
            if (pag) pag.innerHTML = '';
            return;
        }

        const startIdx = (this.rollupCurrentPage - 1) * this.rollupPageSize;
        const pageItems = hourly.slice(startIdx, startIdx + this.rollupPageSize);

        let html = '';
        pageItems.forEach(h => {
            const sf = (h.speed && h.speed.f > 0) ? `<span class="uniselv-fault-badge">${h.speed.f}</span>` : '0';
            const mf = (h.pmem && h.pmem.f > 0) ? `<span class="uniselv-fault-badge">${h.pmem.f}</span>` : '0';
            const nf = (h.nproc && h.nproc.f > 0) ? `<span class="uniselv-fault-badge">${h.nproc.f}</span>` : '0';

            let ioAvg = (h.io && h.io.a) ? String(h.io.a) : '0 B/s';
            if (ioAvg.includes('B/s')) {
                const parts = ioAvg.split(' ');
                const num = parseFloat(parts[0]);
                if (!isNaN(num)) {
                    ioAvg = (num >= 100 ? num.toFixed(1) : num.toFixed(2)) + ' ' + (parts.slice(1).join(' ') || 'B/s');
                }
            }

            html += `
                <tr>
                    <td>${this.escapeHtml(h.from_time)}</td>
                    <td>${this.escapeHtml(h.to_time)}</td>
                    <td style="border-left:1px solid #e2e8f0;">${h.speed.a}</td><td>${h.speed.l}</td><td>${sf}</td>
                    <td style="border-left:1px solid #e2e8f0;">${h.pmem.a}</td><td>${h.pmem.l}</td><td>${mf}</td>
                    <td style="border-left:1px solid #e2e8f0;">${ioAvg}</td><td>${h.io.l}</td><td>${h.io.f}</td>
                    <td style="border-left:1px solid #e2e8f0;">${h.ep.a}</td><td>${h.ep.l}</td><td>${h.ep.f}</td>
                    <td style="border-left:1px solid #e2e8f0;">${h.nproc.a}</td><td>${h.nproc.l}</td><td>${nf}</td>
                    <td style="border-left:1px solid #e2e8f0;">${h.iops.a}</td><td>${h.iops.l}</td><td>${h.iops.f}</td>
                </tr>
            `;
        });
        rollupTbody.innerHTML = html;

        UniselvPagination.render({
            containerId: 'uniselv-usage-rollup-pagination',
            totalItems: hourly.length,
            currentPage: this.rollupCurrentPage,
            pageSize: this.rollupPageSize,
            onPageChange: (newPage) => {
                this.rollupCurrentPage = newPage;
                this.renderRollupPage();
            },
            onPageSizeChange: (newSize) => {
                this.rollupPageSize = newSize;
                this.rollupCurrentPage = 1;
                this.renderRollupPage();
            }
        });
    },

    refreshCurrentUsage: function() {
        const tf = document.getElementById('uniselv-usage-timeframe')?.value || 'today';
        this.loadCurrentUsage(tf);
        this.loadLiveProcesses();
    },

    loadLiveProcesses: function() {
        const tbody = document.getElementById('uniselv-live-processes-tbody');
        if (!tbody) return;
        tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; color:#64748b; padding:20px;">Refreshing live process table...</td></tr>';

        this.callApi('processes', { username: this.currentUser }, (err, res) => {
            if (err || res.error || !res.processes) {
                tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; color:#b91c1c; padding:20px;">Failed to load processes: ${err || res.error}</td></tr>`;
                return;
            }

            const procs = res.processes;
            if (procs.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; color:#64748b; padding:24px;">No active background processes currently running for this account.</td></tr>';
                return;
            }

            let html = '';
            procs.forEach(p => {
                const cpuVal = (typeof p.cpu_percent === 'number') ? p.cpu_percent : 0;
                const cpuColor = (cpuVal > 50) ? '#dc2626' : ((cpuVal > 15) ? '#d97706' : '#1e293b');
                const memVal = p.mem_formatted || p.mem_mb || 0;
                const cmdEsc = this.escapeHtml(p.cmdline || p.comm || 'unknown');
                const tooltipEsc = this.escapeHtml(p.tooltip || p.cmdline || cmdEsc);

                html += `
                    <tr>
                        <td><strong>${p.pid}</strong></td>
                        <td>
                            <span class="uniselv-cmd-text" title="${tooltipEsc}">${cmdEsc}</span>
                        </td>
                        <td style="text-align:right; font-weight:700; color:${cpuColor};">${p.cpu_formatted || cpuVal + '%'}</td>
                        <td style="text-align:right; font-weight:600; color:#059669;" title="${p.rss_formatted || memVal + ' MB'}">${memVal}</td>
                        <td style="text-align:right;">
                            <button class="uniselv-btn btn-danger btn-sm uniselv-stop-proc-btn" onclick="UniselvResMan.stopProcess(${p.pid}, ${p.start_time})">Stop</button>
                        </td>
                    </tr>
                `;
            });
            tbody.innerHTML = html;
        });
    },

    renderUsage8Chart: function(title, points, unit, strokeColor, statText) {
        const card = document.createElement('div');
        card.className = 'uniselv-chart-card';

        const header = document.createElement('div');
        header.className = 'uniselv-chart-card-header';
        header.innerHTML = `
            <h6 class="uniselv-chart-title">${this.escapeHtml(title)}</h6>
            <span class="uniselv-chart-stat">${this.escapeHtml(statText || '')}</span>
        `;
        card.appendChild(header);

        if (!points || points.length < 2) {
            const empty = document.createElement('div');
            empty.innerText = 'No chart telemetry available for this range.';
            empty.style.padding = '30px';
            empty.style.textAlign = 'center';
            empty.style.color = '#94a3b8';
            card.appendChild(empty);
            return card;
        }

        const allNull = points.every(p => p.y === null || p.y === undefined);
        if (allNull) {
            const empty = document.createElement('div');
            empty.innerHTML = `<div style="padding: 34px 16px; text-align: center; color: #64748b; font-size: 0.82rem; line-height: 1.5;">
                <div style="font-weight: 600; color: #475569; margin-bottom: 4px;">Metric Unavailable</div>
                Linux cgroups v2 does not track mod_hostinglimits Entry Processes independently.<br>Account concurrency is governed via <strong>Processes (NPROC)</strong>.
            </div>`;
            card.appendChild(empty);
            return card;
        }

        const width = 540;
        const height = 150;
        const padLeft = 45;
        const padRight = 20;
        const padTop = 20;
        const padBottom = 25;

        const cleanPoints = points.map(p => ({
            x: Number(p.x) || 0,
            y: (typeof p.y === 'number' && !isNaN(p.y)) ? p.y : 0,
            limit: (typeof p.limit === 'number' && !isNaN(p.limit)) ? p.limit : 0
        }));

        let maxY = 0;
        let limitY = 0;
        cleanPoints.forEach(p => {
            if (p.y > maxY) maxY = p.y;
            if (p.limit > limitY) limitY = p.limit;
        });
        maxY = Math.max(maxY, limitY, 1);
        maxY = (title === 'CPU (SPEED)' && limitY > 0) ? Math.max(maxY, limitY) : Math.ceil(maxY * 1.15);

        const minX = cleanPoints[0].x;
        const maxX = cleanPoints[cleanPoints.length - 1].x;
        const rangeX = Math.max(1, maxX - minX);

        const scaleX = (x) => padLeft + ((x - minX) / rangeX) * (width - padLeft - padRight);
        const scaleY = (y) => height - padBottom - (y / maxY) * (height - padTop - padBottom);

        let pathD = `M ${scaleX(cleanPoints[0].x)} ${scaleY(cleanPoints[0].y)}`;
        cleanPoints.forEach((p, idx) => {
            if (idx > 0) pathD += ` L ${scaleX(p.x)} ${scaleY(p.y)}`;
        });

        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('viewBox', `0 0 ${width} ${height}`);
        svg.style.width = '100%';
        svg.style.height = 'auto';
        svg.style.display = 'block';

        // Horizontal Gridlines
        for (let i = 0; i <= 3; i++) {
            const gridVal = Math.round((maxY / 3) * i);
            const yPos = scaleY(gridVal);
            const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            line.setAttribute('x1', padLeft);
            line.setAttribute('x2', width - padRight);
            line.setAttribute('y1', yPos);
            line.setAttribute('y2', yPos);
            line.setAttribute('stroke', '#f1f5f9');
            line.setAttribute('stroke-width', '1');
            svg.appendChild(line);

            const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            text.setAttribute('x', padLeft - 6);
            text.setAttribute('y', yPos + 3);
            text.setAttribute('text-anchor', 'end');
            text.setAttribute('font-size', '9');
            text.setAttribute('fill', '#94a3b8');
            text.textContent = gridVal;
            svg.appendChild(text);
        }

        // Limit Line (dashed red)
        if (limitY > 0) {
            const limYPos = scaleY(limitY);
            const limLine = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            limLine.setAttribute('x1', padLeft);
            limLine.setAttribute('x2', width - padRight);
            limLine.setAttribute('y1', limYPos);
            limLine.setAttribute('y2', limYPos);
            limLine.setAttribute('stroke', '#dc2626');
            limLine.setAttribute('stroke-width', '1.5');
            limLine.setAttribute('stroke-dasharray', '4 4');
            svg.appendChild(limLine);

            const limText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            limText.setAttribute('x', width - padRight);
            limText.setAttribute('y', limYPos - 4);
            limText.setAttribute('text-anchor', 'end');
            limText.setAttribute('font-size', '9');
            limText.setAttribute('fill', '#dc2626');
            limText.setAttribute('font-weight', '600');
            limText.textContent = `Limit: ${limitY} ${unit}`;
            svg.appendChild(limText);
        }

        // Telemetry Path
        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        path.setAttribute('d', pathD);
        path.setAttribute('fill', 'none');
        path.setAttribute('stroke', strokeColor);
        path.setAttribute('stroke-width', '2');
        path.setAttribute('stroke-linecap', 'round');
        svg.appendChild(path);

        card.appendChild(svg);
        return card;
    },

    loadHistory: function(range) {
        const chartContainer = document.getElementById('uniselv-history-charts');
        if (!chartContainer) return;
        chartContainer.innerHTML = '<div style="padding: 30px; text-align: center; color: #64748b;">Loading historical telemetry data...</div>';

        this.latestRead('enduser-history', 'history', { range: range, username: this.currentUser }, (err, res) => {
            if (err || !res || res.error) {
                const message = String(err?.message || res?.error || this.translate('telemetry_offline', 'Telemetry offline'));
                this.showUsageError(chartContainer, [], message, () => this.loadHistory(range));
                return;
            }

            if (!res.points || res.points.length === 0) {
                chartContainer.innerHTML = '<div class="uniselv-card" style="text-align: center; color: #64748b; padding: 40px;">No historical telemetry recorded yet for this time window. Data collection is running.</div>';
                return;
            }

            this.renderChartsToContainer(chartContainer, res.points);
        });
    },

    // ==================== ADMIN USER ANALYTICS & CHARTS ====================
    selectedAdminUser: '',
    activeAdminUserSubtab: 'usage',

    inspectUserCharts: function(username) {
        this.inspectUserUsage(username);
    },

    inspectUserUsage: function(username) {
        this.switchTab('analytics');
        const sel = document.getElementById('admin-user-selector');
        if (sel) sel.value = username;
        this.onAdminUserSelected(username, 'usage');
    },

    inspectUserSnapshots: function(username) {
        this.switchTab('analytics');
        const sel = document.getElementById('admin-user-selector');
        if (sel) sel.value = username;
        this.onAdminUserSelected(username, 'snapshots');
    },

    switchAdminUserSubtab: function(subtab) {
        this.activeAdminUserSubtab = subtab;
        const usageBtn = document.getElementById('admin-subtab-usage');
        const snapsBtn = document.getElementById('admin-subtab-snapshots');
        const usageView = document.getElementById('admin-view-usage');
        const snapsView = document.getElementById('admin-view-snapshots');

        if (usageBtn) usageBtn.classList.toggle('active', subtab === 'usage');
        if (snapsBtn) snapsBtn.classList.toggle('active', subtab === 'snapshots');
        if (usageView) usageView.style.display = (subtab === 'usage') ? 'block' : 'none';
        if (snapsView) snapsView.style.display = (subtab === 'snapshots') ? 'block' : 'none';

        const targetUser = this.selectedAdminUser || document.getElementById('admin-user-selector')?.value || '';
        if (!targetUser) return;

        if (subtab === 'usage') {
            this.loadAdminUserUsage();
            this.loadAdminUserProcesses();
        } else if (subtab === 'snapshots') {
            this.loadAdminSnapshotsIndex();
        }
    },

    onAdminUserSelected: function(username, subview) {
        if (!username) {
            const sel = document.getElementById('admin-user-selector');
            username = sel ? sel.value : '';
        }
        this.selectedAdminUser = username;
        const userDisplay = document.getElementById('admin-usage-selected-user');
        if (userDisplay) userDisplay.innerText = username;

        const targetSubview = subview || this.activeAdminUserSubtab || 'usage';
        this.switchAdminUserSubtab(targetSubview);
    },

    refreshAdminUserUsage: function() {
        const tf = document.getElementById('admin-usage-timeframe')?.value || 'today';
        this.loadAdminUserUsage(tf);
        this.loadAdminUserProcesses();
    },

    adminHourlyUsageRecords: [],
    adminRollupCurrentPage: 1,
    adminRollupPageSize: 12,

    loadAdminUserUsage: function(timeframe) {
        timeframe = timeframe || document.getElementById('admin-usage-timeframe')?.value || 'today';
        const targetUser = this.selectedAdminUser || document.getElementById('admin-user-selector')?.value || '';
        if (!targetUser) return;

        const totalTbody = document.getElementById('admin-account-total-tbody');
        const gridEl = document.getElementById('admin-usage-8charts-grid');
        const rollupTbody = document.getElementById('admin-usage-rollup-tbody');
        this.adminHourlyUsageRecords = [];
        document.getElementById('admin-usage-rollup-pagination')?.replaceChildren();

        if (totalTbody) totalTbody.innerHTML = '<tr><td colspan="4" style="text-align:center; color:#64748b; padding:20px;">Loading account totals for ' + this.escapeHtml(targetUser) + '...</td></tr>';
        if (gridEl) gridEl.innerHTML = '<div style="grid-column: 1 / -1; text-align:center; color:#64748b; padding:40px; background:#fff; border:1px solid var(--uniselv-border); border-radius:8px;">Loading 8 resource telemetry charts...</div>';
        if (rollupTbody) rollupTbody.innerHTML = '<tr><td colspan="20" style="text-align:center; color:#64748b; padding:24px;">Loading hourly usage records...</td></tr>';

        this.latestRead('admin-usage', 'history', { range: timeframe, username: targetUser }, (err, res) => {
            if (err || !res || res.error) {
                const message = String(err?.message || res?.error || this.translate('telemetry_offline', 'Telemetry offline'));
                this.showUsageError(gridEl, [[totalTbody, 4], [rollupTbody, 20]], message, () => this.loadAdminUserUsage(timeframe));
                return;
            }

            // 1. Render Account Total Card
            if (totalTbody) {
                const totals = res.account_total || [];
                if (totals.length === 0) {
                    totalTbody.innerHTML = '<tr><td colspan="4" style="text-align:center; color:#64748b; padding:16px;">No account totals recorded.</td></tr>';
                } else {
                    let html = '';
                    totals.forEach(r => {
                        const faultHtml = (r.fault > 0) ? `<span class="uniselv-fault-badge">${r.fault}</span>` : '0';
                        let usageStr = r.usage;
                        if (typeof usageStr === 'string' && usageStr.includes('B/s')) {
                            const parts = usageStr.split(' ');
                            const num = parseFloat(parts[0]);
                            if (!isNaN(num)) {
                                usageStr = (num >= 100 ? num.toFixed(1) : num.toFixed(2)) + ' ' + (parts.slice(1).join(' ') || 'B/s');
                            }
                        }
                        html += `
                            <tr>
                                <td style="font-weight:600; color:#1e293b;">${this.escapeHtml(r.desc)}</td>
                                <td style="font-weight:600;">${this.escapeHtml(usageStr)}</td>
                                <td style="color:#64748b;">${this.escapeHtml(r.limit)}</td>
                                <td>${faultHtml}</td>
                            </tr>
                        `;
                    });
                    totalTbody.innerHTML = html;
                }
            }

            // 2. Render 8 Interactive Charts Grid
            if (gridEl) {
                gridEl.innerHTML = '';
                const pts = res.points || [];
                if (pts.length < 2) {
                    gridEl.innerHTML = `<div style="grid-column: 1 / -1; text-align:center; color:#64748b; padding:40px; background:#fff; border:1px solid var(--uniselv-border); border-radius:8px;">Not enough telemetry points collected for <strong>${this.escapeHtml(targetUser)}</strong> in this timeframe yet. Telemetry daemon is actively sampling.</div>`;
                } else {
                    // Chart 1: CPU (SPEED)
                    const cpuData = pts.map(p => ({ x: p.t, y: p.speed, limit: p.limit_speed }));
                    const cpuAvg = (cpuData.reduce((s, p) => s + p.y, 0) / cpuData.length).toFixed(1);
                    const cpuMax = Math.max(...cpuData.map(p => p.y)).toFixed(1);
                    gridEl.appendChild(this.renderUsage8Chart(this.translate('chart_cpu', 'CPU usage') + ' (100% = 1 vCPU)', cpuData, '%', '#2563eb', `Plotted avg: ${cpuAvg}% | max: ${cpuMax}%`));

                    // Chart 2: Virtual memory (RAM + Swap)
                    const vmemData = pts.map(p => ({ x: p.t, y: p.vmem, limit: p.limit_vmem }));
                    const vmemMax = Math.max(...vmemData.map(p => p.y)).toFixed(1);
                    gridEl.appendChild(this.renderUsage8Chart(this.translate('chart_vmem', 'Virtual memory (RAM + Swap)'), vmemData, 'MiB', '#6366f1', `Plotted max: ${vmemMax} MiB; historical limit unavailable`));

                    // Chart 3: Physical memory
                    const pmemData = pts.map(p => ({ x: p.t, y: p.pmem, limit: p.limit_pmem }));
                    const pmemMax = Math.max(...pmemData.map(p => p.y)).toFixed(1);
                    const pmemAvg = (pmemData.reduce((s, p) => s + p.y, 0) / pmemData.length).toFixed(1);
                    gridEl.appendChild(this.renderUsage8Chart(this.translate('chart_mem', 'Memory usage'), pmemData, 'MiB', '#059669', `Plotted avg: ${pmemAvg} MiB | max: ${pmemMax} MiB`));

                    // Chart 4: IO
                    const ioData = pts.map(p => ({ x: p.t, y: p.io, limit: p.limit_io }));
                    const ioMax = Math.max(...ioData.map(p => p.y)).toFixed(1);
                    gridEl.appendChild(this.renderUsage8Chart(this.translate('chart_io', 'Disk throughput'), ioData, 'KiB/s', '#d97706', `Plotted max: ${ioMax} KiB/s`));

                    // Chart 5: IOPS
                    const iopsData = pts.map(p => ({ x: p.t, y: p.iops, limit: p.limit_iops }));
                    const iopsMax = Math.max(...iopsData.map(p => p.y)).toFixed(0);
                    gridEl.appendChild(this.renderUsage8Chart('IOPS', iopsData, 'iops', '#0891b2', `Max: ${iopsMax} iops`));

                    // Chart 6: Entry processes
                    const epData = pts.map(p => ({ x: p.t, y: p.ep, limit: p.limit_ep }));
                    const hasEp = pts.some(p => p.ep !== null && p.ep !== undefined);
                    const epStat = hasEp ? `Max: ${Math.max(...epData.filter(p => p.y !== null).map(p => p.y)).toFixed(1)} EP` : 'N/A (Governed via NPROC)';
                    gridEl.appendChild(this.renderUsage8Chart(this.translate('chart_ep', 'Entry processes'), epData, 'EP', '#7c3aed', epStat));

                    // Chart 7: Processes
                    const nprocData = pts.map(p => ({ x: p.t, y: p.nproc, limit: p.limit_nproc }));
                    const nprocMax = Math.max(...nprocData.map(p => p.y));
                    gridEl.appendChild(this.renderUsage8Chart(this.translate('chart_tasks', 'Active tasks and threads'), nprocData, 'procs', '#4f46e5', `Max: ${nprocMax}`));

                    // Chart 8: Faults
                    const faultData = pts.map(p => ({ x: p.t, y: p.faults, limit: 0 }));
                    const faultTot = faultData.reduce((s, p) => s + p.y, 0);
                    gridEl.appendChild(this.renderUsage8Chart(this.translate('chart_faults', 'Faults'), faultData, 'events', '#dc2626', `Total: ${faultTot} events`));
                }
            }

            // 3. Hourly Rollup Table
            this.adminHourlyUsageRecords = res.hourly_usage || [];
            this.adminRollupCurrentPage = 1;
            this.renderAdminRollupPage();
        });
    },

    renderAdminRollupPage: function() {
        const rollupTbody = document.getElementById('admin-usage-rollup-tbody');
        if (!rollupTbody) return;

        const hourly = this.adminHourlyUsageRecords || [];
        if (hourly.length === 0) {
            rollupTbody.innerHTML = '<tr><td colspan="20" style="text-align:center; color:#64748b; padding:24px;">No historical telemetry records logged yet for this period.</td></tr>';
            const pag = document.getElementById('admin-usage-rollup-pagination');
            if (pag) pag.innerHTML = '';
            return;
        }

        const startIdx = (this.adminRollupCurrentPage - 1) * this.adminRollupPageSize;
        const pageItems = hourly.slice(startIdx, startIdx + this.adminRollupPageSize);

        let html = '';
        pageItems.forEach(h => {
            const sf = (h.speed && h.speed.f > 0) ? `<span class="uniselv-fault-badge">${h.speed.f}</span>` : '0';
            const mf = (h.pmem && h.pmem.f > 0) ? `<span class="uniselv-fault-badge">${h.pmem.f}</span>` : '0';
            const nf = (h.nproc && h.nproc.f > 0) ? `<span class="uniselv-fault-badge">${h.nproc.f}</span>` : '0';

            let ioAvg = (h.io && h.io.a) ? String(h.io.a) : '0 B/s';
            if (ioAvg.includes('B/s')) {
                const parts = ioAvg.split(' ');
                const num = parseFloat(parts[0]);
                if (!isNaN(num)) {
                    ioAvg = (num >= 100 ? num.toFixed(1) : num.toFixed(2)) + ' ' + (parts.slice(1).join(' ') || 'B/s');
                }
            }

            html += `
                <tr>
                    <td>${this.escapeHtml(h.from_time)}</td>
                    <td>${this.escapeHtml(h.to_time)}</td>
                    <td style="border-left:1px solid #e2e8f0;">${h.speed.a}</td><td>${h.speed.l}</td><td>${sf}</td>
                    <td style="border-left:1px solid #e2e8f0;">${h.pmem.a}</td><td>${h.pmem.l}</td><td>${mf}</td>
                    <td style="border-left:1px solid #e2e8f0;">${ioAvg}</td><td>${h.io.l}</td><td>${h.io.f}</td>
                    <td style="border-left:1px solid #e2e8f0;">${h.ep.a}</td><td>${h.ep.l}</td><td>${h.ep.f}</td>
                    <td style="border-left:1px solid #e2e8f0;">${h.nproc.a}</td><td>${h.nproc.l}</td><td>${nf}</td>
                    <td style="border-left:1px solid #e2e8f0;">${h.iops.a}</td><td>${h.iops.l}</td><td>${h.iops.f}</td>
                </tr>
            `;
        });
        rollupTbody.innerHTML = html;

        UniselvPagination.render({
            containerId: 'admin-usage-rollup-pagination',
            totalItems: hourly.length,
            currentPage: this.adminRollupCurrentPage,
            pageSize: this.adminRollupPageSize,
            onPageChange: (newPage) => {
                this.adminRollupCurrentPage = newPage;
                this.renderAdminRollupPage();
            },
            onPageSizeChange: (newSize) => {
                this.adminRollupPageSize = newSize;
                this.adminRollupCurrentPage = 1;
                this.renderAdminRollupPage();
            }
        });
    },

    loadAdminUserProcesses: function() {
        const tbody = document.getElementById('admin-live-processes-tbody');
        if (!tbody) return;
        const targetUser = this.selectedAdminUser || document.getElementById('admin-user-selector')?.value || '';
        if (!targetUser) return;

        tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; color:#64748b; padding:20px;">Refreshing live process table for ' + this.escapeHtml(targetUser) + '...</td></tr>';

        this.latestRead('admin-processes', 'processes', { username: targetUser }, (err, res) => {
            if (err || res.error || !res.processes) {
                tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; color:#b91c1c; padding:20px;">Failed to load processes: ${err || res.error}</td></tr>`;
                return;
            }

            const procs = res.processes;
            if (procs.length === 0) {
                tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; color:#64748b; padding:24px;">No active background processes currently running for <strong>${this.escapeHtml(targetUser)}</strong>.</td></tr>`;
                return;
            }

            let html = '';
            procs.forEach(p => {
                const cpuVal = (typeof p.cpu_percent === 'number') ? p.cpu_percent : 0;
                const cpuColor = (cpuVal > 50) ? '#dc2626' : ((cpuVal > 15) ? '#d97706' : '#1e293b');
                const memVal = p.mem_formatted || p.mem_mb || 0;
                const cmdEsc = this.escapeHtml(p.cmdline || p.comm || 'unknown');
                const tooltipEsc = this.escapeHtml(p.tooltip || p.cmdline || cmdEsc);

                html += `
                    <tr>
                        <td><strong>${p.pid}</strong></td>
                        <td>
                            <span class="uniselv-cmd-text" title="${tooltipEsc}">${cmdEsc}</span>
                        </td>
                        <td style="text-align:right; font-weight:700; color:${cpuColor};">${p.cpu_formatted || cpuVal + '%'}</td>
                        <td style="text-align:right; font-weight:600; color:#059669;" title="${p.rss_formatted || memVal + ' MB'}">${memVal}</td>
                        <td style="text-align:right;">
                            <button class="uniselv-btn btn-danger btn-sm uniselv-stop-proc-btn" onclick="UniselvResMan.stopProcess(${p.pid}, ${p.start_time}, '${targetUser}')">Stop</button>
                        </td>
                    </tr>
                `;
            });
            tbody.innerHTML = html;
        });
    },

    renderSvgChart: function(title, points, unit, strokeColor) {
        const card = document.createElement('div');
        card.className = 'uniselv-card';
        card.style.marginBottom = '20px';

        const header = document.createElement('div');
        header.style.display = 'flex';
        header.style.justifyContent = 'space-between';
        header.style.alignItems = 'center';
        header.style.marginBottom = '12px';
        header.innerHTML = `<h5 style="font-weight: 700; margin: 0; font-size: 0.95rem; text-transform: uppercase; color: #1e293b;">${title}</h5>
                            <span style="font-size: 0.8rem; color: #64748b; font-weight: 500;">${points.length} points</span>`;
        card.appendChild(header);

        if (points.length < 2) {
            const empty = document.createElement('div');
            empty.innerText = 'Not enough samples to construct vector curve.';
            empty.style.padding = '30px';
            empty.style.color = '#94a3b8';
            card.appendChild(empty);
            return card;
        }

        const width = 800;
        const height = 180;
        const padX = 45;
        const padY = 25;

        // Clean and sanitize numbers
        const cleanPoints = points.map(p => ({
            x: Number(p.x) || 0,
            y: (typeof p.y === 'number' && !isNaN(p.y)) ? p.y : 0,
            limit: (typeof p.limit === 'number' && !isNaN(p.limit)) ? p.limit : 0
        }));

        let maxY = 0;
        let limitY = 0;
        cleanPoints.forEach(p => {
            if (p.y > maxY) maxY = p.y;
            if (p.limit > limitY) limitY = p.limit;
        });
        maxY = Math.max(maxY, limitY, 1);
        maxY = Math.ceil(maxY * 1.15); // headroom

        const minX = cleanPoints[0].x;
        const maxX = cleanPoints[cleanPoints.length - 1].x;
        const rangeX = Math.max(1, maxX - minX);

        const scaleX = (x) => {
            const val = Number(x) || 0;
            return padX + ((val - minX) / rangeX) * (width - 2 * padX);
        };
        const scaleY = (y) => {
            const val = Number(y) || 0;
            return height - padY - (val / maxY) * (height - 2 * padY);
        };

        let pathD = `M ${scaleX(cleanPoints[0].x)} ${scaleY(cleanPoints[0].y)}`;
        cleanPoints.forEach((p, idx) => {
            if (idx > 0) {
                pathD += ` L ${scaleX(p.x)} ${scaleY(p.y)}`;
            }
        });

        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('viewBox', `0 0 ${width} ${height}`);
        svg.style.width = '100%';
        svg.style.height = 'auto';

        // Draw horizontal grid lines
        for (let i = 0; i <= 3; i++) {
            const gridVal = Math.round((maxY / 3) * i);
            const yPos = scaleY(gridVal);
            const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            line.setAttribute('x1', padX);
            line.setAttribute('x2', width - padX);
            line.setAttribute('y1', yPos);
            line.setAttribute('y2', yPos);
            line.setAttribute('stroke', '#f1f5f9');
            line.setAttribute('stroke-width', '1');
            svg.appendChild(line);

            const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            text.setAttribute('x', padX - 8);
            text.setAttribute('y', yPos + 4);
            text.setAttribute('text-anchor', 'end');
            text.setAttribute('font-size', '10');
            text.setAttribute('fill', '#475569');
            text.textContent = gridVal;
            svg.appendChild(text);
        }

        // Time ticks use the same scale as the samples, including gaps in collection.
        const tickFormat = new Intl.DateTimeFormat(undefined, rangeX >= 86400
            ? {month: 'short', day: 'numeric'}
            : {hour: '2-digit', minute: '2-digit', hourCycle: 'h23'});
        for (let i = 0; i < 4; i++) {
            const epoch = minX + rangeX * i / 3;
            const tick = document.createElementNS(svg.namespaceURI, 'text');
            tick.setAttribute('x', scaleX(epoch));
            tick.setAttribute('y', height - 7);
            tick.setAttribute('text-anchor', i === 0 ? 'start' : i === 3 ? 'end' : 'middle');
            tick.setAttribute('font-size', '12');
            tick.setAttribute('fill', '#475569');
            tick.textContent = tickFormat.format(epoch * 1000);
            svg.appendChild(tick);
        }

        // Draw Limit Line if present
        if (limitY > 0) {
            const limitYPos = scaleY(limitY);
            const limLine = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            limLine.setAttribute('x1', padX);
            limLine.setAttribute('x2', width - padX);
            limLine.setAttribute('y1', limitYPos);
            limLine.setAttribute('y2', limitYPos);
            limLine.setAttribute('stroke', '#dc2626');
            limLine.setAttribute('stroke-width', '1.5');
            limLine.setAttribute('stroke-dasharray', '4 4');
            svg.appendChild(limLine);

            const limText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            limText.setAttribute('x', width - padX);
            limText.setAttribute('y', limitYPos - 6);
            limText.setAttribute('text-anchor', 'end');
            limText.setAttribute('font-size', '10');
            limText.setAttribute('fill', '#dc2626');
            limText.setAttribute('font-weight', '600');
            limText.textContent = `Limit: ${limitY} ${unit}`;
            svg.appendChild(limText);
        }

        // Draw Telemetry Line
        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        path.setAttribute('d', pathD);
        path.setAttribute('fill', 'none');
        path.setAttribute('stroke', strokeColor);
        path.setAttribute('stroke-width', '2.5');
        path.setAttribute('stroke-linecap', 'round');
        svg.appendChild(path);

        card.appendChild(svg);
        const detail = document.createElement('label');
        detail.className = 'uniselv-chart-inspector';
        const output = document.createElement('output');
        output.setAttribute('aria-live', 'off');
        const range = document.createElement('input');
        range.type = 'range';
        range.min = '0';
        range.max = String(cleanPoints.length - 1);
        range.value = range.max;
        range.setAttribute('aria-label', title + ' · ' + this.translate('chart_sample', 'Inspect sample'));
        const dateFormat = new Intl.DateTimeFormat(undefined, {
            year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit',
            minute: '2-digit', hourCycle: 'h23', timeZoneName: 'short'
        });
        const formatSample = point => dateFormat.format(point.x * 1000) + ' · ' + point.y + ' ' + unit;
        const marker = document.createElementNS(svg.namespaceURI, 'circle');
        marker.setAttribute('r', '4');
        marker.setAttribute('fill', strokeColor);
        marker.setAttribute('stroke', 'white');
        marker.setAttribute('aria-hidden', 'true');
        svg.appendChild(marker);
        const showSample = () => {
            const point = cleanPoints[Number(range.value)];
            output.textContent = formatSample(point);
            range.setAttribute('aria-valuetext', output.textContent);
            marker.setAttribute('cx', scaleX(point.x));
            marker.setAttribute('cy', scaleY(point.y));
        };
        range.addEventListener('input', showSample);
        detail.append(this.translate('chart_sample', 'Inspect sample'), range, output);
        card.appendChild(detail);
        showSample();
        return card;
    },

    stopProcess: function(pid, startTime, targetUser) {
        const u = targetUser || (this.isAdmin ? (this.selectedAdminUser || document.getElementById('admin-user-selector')?.value) : this.currentUser);
        UniselvModal.confirm({
            title: `Terminate Process ${pid}?`,
            message: `Are you sure you want to stop this process? The system will verify process ownership and start-time identity to guard against PID reuse.`,
            icon: 'danger',
            confirmText: 'Stop Process',
            isDanger: true,
            onConfirm: () => {
                this.callApi('stop_process', { pid: pid, start_time: startTime, username: u }, (err, res) => {
                    if (err || res.error) {
                        UniselvNotify.error(`Error stopping process: ${err || res.error}`);
                    } else {
                        UniselvNotify.success(res.message || 'Process stopped successfully');
                        if (this.isAdmin) {
                            setTimeout(() => this.loadAdminUserProcesses(), 1000);
                        } else {
                            setTimeout(() => this.loadLiveProcesses(), 1000);
                        }
                    }
                });
            }
        });
    },

    // ==================== CPANEL SNAPSHOTS ENGINE ====================
    adminSnapshotsState: {
        username: '',
        available_dates: [],
        selected_date: '',
        snapshots: [],
        current_snapshot: null,
        active_subtab: 'procs'
    },

    enduserSnapshotsState: {
        username: '',
        available_dates: [],
        selected_date: '',
        snapshots: [],
        current_snapshot: null,
        active_subtab: 'procs'
    },

    loadAdminSnapshotsIndex: function(date, snapshotId) {
        const username = this.selectedAdminUser || document.getElementById('admin-user-selector')?.value || '';
        if (!username) return;
        this.adminSnapshotsState.username = username;
        this.fetchSnapshotsIndex(username, date, snapshotId, 'admin');
    },

    loadEnduserSnapshotsIndex: function(date, snapshotId) {
        this.fetchSnapshotsIndex(this.currentUser, date, snapshotId, 'enduser');
    },

    fetchSnapshotsIndex: function(username, date, snapshotId, role) {
        const params = { username: username };
        if (date) params.date = date;
        if (snapshotId) params.snapshot_id = snapshotId;

        const contentEl = document.getElementById(`${role}-snap-content`);
        if (contentEl) contentEl.innerHTML = '<div style="text-align:center; padding:30px; color:#64748b;">Loading snapshot records...</div>';

        this.latestRead(role + '-snapshots', 'snapshots_index', params, (err, res) => {
            const state = (role === 'admin') ? this.adminSnapshotsState : this.enduserSnapshotsState;
            if (err || res.error) {
                if (contentEl) contentEl.innerHTML = `<div style="color:#b91c1c; padding:20px;">Failed to load snapshots: ${err || res.error}</div>`;
                return;
            }

            state.available_dates = res.available_dates || [];
            state.selected_date = res.selected_date || '';
            state.snapshots = res.snapshots || [];
            state.current_snapshot = res.current_snapshot || null;

            this.updateSnapshotToolbar(role);
            this.renderSnapshotContent(role);
        });
    },

    updateSnapshotToolbar: function(role) {
        const state = (role === 'admin') ? this.adminSnapshotsState : this.enduserSnapshotsState;
        const dateSel = document.getElementById(`${role}-snap-date-select`);
        const timeSel = document.getElementById(`${role}-snap-time-select`);
        const badgeEl = document.getElementById(`${role}-snap-trigger-badge`);
        const prevBtn = document.getElementById(`${role}-snap-prev-btn`);
        const nextBtn = document.getElementById(`${role}-snap-next-btn`);

        if (dateSel) {
            if (!state.available_dates || state.available_dates.length === 0) {
                dateSel.innerHTML = '<option value="">No snapshots recorded</option>';
            } else {
                let html = '';
                state.available_dates.forEach(d => {
                    const sel = (d.date === state.selected_date) ? 'selected' : '';
                    html += `<option value="${d.date}" ${sel}>${d.label} (${d.count})</option>`;
                });
                dateSel.innerHTML = html;
            }
        }

        if (timeSel) {
            if (!state.snapshots || state.snapshots.length === 0) {
                timeSel.innerHTML = '<option value="">No snapshots</option>';
            } else {
                let html = '';
                const curId = state.current_snapshot ? state.current_snapshot.id : null;
                state.snapshots.forEach(s => {
                    const sel = (s.id === curId) ? 'selected' : '';
                    html += `<option value="${s.id}" ${sel}>${s.time_str} - [${(s.trigger_type || 'snap').toUpperCase()}]</option>`;
                });
                timeSel.innerHTML = html;
            }
        }

        if (badgeEl && state.current_snapshot) {
            const t = state.current_snapshot.trigger_type || 'INCIDENT';
            const isCrit = (t === 'oom_kill' || t === 'cpu_throttle');
            badgeEl.className = 'uniselv-badge ' + (isCrit ? 'badge-critical' : 'badge-normal');
            badgeEl.innerText = t.toUpperCase();
        }

        // Prev / Next button state
        if (state.snapshots && state.snapshots.length > 0 && state.current_snapshot) {
            const curIdx = state.snapshots.findIndex(s => s.id === state.current_snapshot.id);
            if (prevBtn) prevBtn.disabled = (curIdx <= 0);
            if (nextBtn) nextBtn.disabled = (curIdx >= state.snapshots.length - 1);
        } else {
            if (prevBtn) prevBtn.disabled = true;
            if (nextBtn) nextBtn.disabled = true;
        }
    },

    onAdminSnapshotDateChange: function(date) {
        this.loadAdminSnapshotsIndex(date);
    },

    onEnduserSnapshotDateChange: function(date) {
        this.loadEnduserSnapshotsIndex(date);
    },

    onAdminSnapshotTimeChange: function(snapId) {
        this.fetchSnapshotDetail(this.adminSnapshotsState.username, snapId, 'admin');
    },

    onEnduserSnapshotTimeChange: function(snapId) {
        this.fetchSnapshotDetail(this.currentUser, snapId, 'enduser');
    },

    adminPrevSnapshot: function() {
        this.navigateSnapshot('admin', -1);
    },

    adminNextSnapshot: function() {
        this.navigateSnapshot('admin', 1);
    },

    enduserPrevSnapshot: function() {
        this.navigateSnapshot('enduser', -1);
    },

    enduserNextSnapshot: function() {
        this.navigateSnapshot('enduser', 1);
    },

    navigateSnapshot: function(role, delta) {
        const state = (role === 'admin') ? this.adminSnapshotsState : this.enduserSnapshotsState;
        if (!state.current_snapshot || !state.snapshots || state.snapshots.length === 0) return;
        const curIdx = state.snapshots.findIndex(s => s.id === state.current_snapshot.id);
        const nextIdx = curIdx + delta;
        if (nextIdx >= 0 && nextIdx < state.snapshots.length) {
            const nextSnap = state.snapshots[nextIdx];
            const username = (role === 'admin') ? state.username : this.currentUser;
            this.fetchSnapshotDetail(username, nextSnap.id, role);
        }
    },

    fetchSnapshotDetail: function(username, snapId, role) {
        const contentEl = document.getElementById(`${role}-snap-content`);
        if (contentEl) contentEl.innerHTML = '<div style="text-align:center; padding:30px; color:#64748b;">Loading snapshot details...</div>';

        this.latestRead(role + '-snapshots', 'snapshot_detail', { username: username, snapshot_id: snapId }, (err, res) => {
            const state = (role === 'admin') ? this.adminSnapshotsState : this.enduserSnapshotsState;
            if (err || res.error || !res.snapshot) {
                if (contentEl) contentEl.innerHTML = `<div style="color:#b91c1c; padding:20px;">Failed to load snapshot details: ${err || res.error}</div>`;
                return;
            }
            state.current_snapshot = res.snapshot;
            this.updateSnapshotToolbar(role);
            this.renderSnapshotContent(role);
        });
    },

    setAdminSnapshotSubtab: function(subtab) {
        this.adminSnapshotsState.active_subtab = subtab;
        document.querySelectorAll('#admin-snapshots-section .uniselv-cpanel-subtab').forEach(b => {
            b.classList.toggle('active', b.getAttribute('data-subtab') === subtab);
        });
        this.renderSnapshotContent('admin');
    },

    setEnduserSnapshotSubtab: function(subtab) {
        this.enduserSnapshotsState.active_subtab = subtab;
        document.querySelectorAll('#tab-snapshots .uniselv-cpanel-subtab').forEach(b => {
            b.classList.toggle('active', b.getAttribute('data-subtab') === subtab);
        });
        this.renderSnapshotContent('enduser');
    },

    renderSnapshotContent: function(role) {
        const state = (role === 'admin') ? this.adminSnapshotsState : this.enduserSnapshotsState;
        const container = document.getElementById(`${role}-snap-content`);
        if (!container) return;

        const snap = state.current_snapshot;
        if (!snap) {
            container.innerHTML = `
                <div class="uniselv-empty-box">
                    <div class="uniselv-empty-icon">
                        <svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
                    </div>
                    <div class="uniselv-empty-title">No Diagnostic Snapshots Recorded</div>
                    <div class="uniselv-empty-desc">No threshold breaches, CPU throttling, or memory limits were exceeded on this date. Automated incident snapshots trigger only when an account exhausts allocated resources.</div>
                </div>
            `;
            return;
        }

        const subtab = state.active_subtab || 'procs';

        if (subtab === 'procs') {
            const procs = snap.processes || [];
            if (procs.length === 0) {
                container.innerHTML = `
                    <div class="uniselv-empty-box">
                        <div class="uniselv-empty-title">Zero Active Tenant Processes</div>
                        <div class="uniselv-empty-desc">No customer worker processes were executing in this cgroup at the moment of snapshot capture.</div>
                    </div>
                `;
                return;
            }

            let html = `
                <div class="uniselv-table-wrap">
                    <table class="uniselv-table" style="margin-bottom:0;">
                        <thead>
                            <tr style="background:#f8fafc; font-size:0.8rem; text-transform:uppercase; color:#475569;">
                                <th style="width:90px;">PID</th>
                                <th>CMD</th>
                                <th style="width:110px; text-align:right;">CPU</th>
                                <th style="width:110px; text-align:right;">MEM</th>
                            </tr>
                        </thead>
                        <tbody>
            `;

            procs.forEach(p => {
                const cpuVal = (typeof p.cpu_percent === 'number') ? p.cpu_percent : 0;
                const cpuColor = (cpuVal > 50) ? '#dc2626' : ((cpuVal > 15) ? '#d97706' : '#1e293b');
                const memVal = p.mem_formatted || p.mem_mb || 0;
                const cmdEsc = this.escapeHtml(p.cmdline || p.comm || 'unknown');
                const tooltipEsc = this.escapeHtml(p.tooltip || p.cmdline || cmdEsc);

                html += `
                    <tr>
                        <td><strong>${p.pid}</strong></td>
                        <td>
                            <span class="uniselv-cmd-text" title="${tooltipEsc}">${cmdEsc}</span>
                        </td>
                        <td style="text-align:right; font-weight:700; color:${cpuColor};">${p.cpu_formatted || cpuVal + '%'}</td>
                        <td style="text-align:right; font-weight:600; color:#059669;" title="${p.rss_formatted || memVal + ' MB'}">${memVal}</td>
                    </tr>
                `;
            });

            html += `
                        </tbody>
                    </table>
                </div>
            `;
            container.innerHTML = html;

        } else if (subtab === 'db') {
            const dbList = snap.db_diagnostics || [];
            if (dbList.length === 0) {
                container.innerHTML = `
                    <div class="uniselv-empty-box">
                        <div class="uniselv-empty-title">No Active Database Queries Detected</div>
                        <div class="uniselv-empty-desc">No slow or active MySQL/MariaDB database queries were executing during this snapshot timestamp.</div>
                    </div>
                `;
                return;
            }

            let html = `
                <div class="uniselv-table-wrap">
                    <table class="uniselv-table" style="margin-bottom:0;">
                        <thead>
                            <tr style="background:#f8fafc; font-size:0.8rem; text-transform:uppercase; color:#475569;">
                                <th style="width:70px;">ID</th>
                                <th>User</th>
                                <th>Database</th>
                                <th>Command</th>
                                <th style="width:80px;">Time</th>
                                <th style="width:90px;">State</th>
                                <th>Sanitized Query</th>
                            </tr>
                        </thead>
                        <tbody>
            `;

            dbList.forEach(q => {
                html += `
                    <tr>
                        <td><strong>${q.id}</strong></td>
                        <td><span class="uniselv-badge badge-normal">${this.escapeHtml(q.user || '')}</span></td>
                        <td>${this.escapeHtml(q.db || 'none')}</td>
                        <td>${this.escapeHtml(q.command || '')}</td>
                        <td>${q.time_seconds || 0}s</td>
                        <td>${this.escapeHtml(q.state || '')}</td>
                        <td><code style="font-size:0.8rem; background:#f1f5f9; padding:2px 6px; border-radius:4px; max-width:400px; display:inline-block; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">${this.escapeHtml(q.query || '')}</code></td>
                    </tr>
                `;
            });

            html += `
                        </tbody>
                    </table>
                </div>
            `;
            container.innerHTML = html;

        } else if (subtab === 'http') {
            const webList = snap.web_diagnostics || [];
            if (webList.length === 0) {
                container.innerHTML = `
                    <div class="uniselv-empty-box">
                        <div class="uniselv-empty-title">No Concurrent Inbound HTTP Traces</div>
                        <div class="uniselv-empty-desc">Web server access logs showed no active or hung inbound HTTP connections at this snapshot capture point.</div>
                    </div>
                `;
                return;
            }

            let html = '<div style="background:#0f172a; color:#f8fafc; padding:14px; border-radius:8px; font-family:ui-monospace,SFMono-Regular,Consolas,monospace; font-size:0.8rem; max-height:360px; overflow-y:auto; line-height:1.6;">';
            webList.forEach(w => {
                const rawEsc = this.escapeHtml(w.raw || JSON.stringify(w));
                html += `<div>${rawEsc}</div>`;
            });
            html += '</div>';
            container.innerHTML = html;
        }
    },

    escapeHtml: function(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    },

    activeEnduserRange: '24h',

    exportReport: function() {
        const range = this.activeEnduserRange || '24h';
        this.callApi('export_report', { range: range }, (err, res) => {
            if (err || res.error) {
                UniselvNotify.error(`Failed to export report: ${err || res.error}`);
                return;
            }
            const blob = new Blob([JSON.stringify(res.report, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `uniselv-resource-report-${this.currentUser}-${range}-${Date.now()}.json`;
            a.click();
            URL.revokeObjectURL(url);
            UniselvNotify.success(`Resource audit report (${range}) downloaded successfully.`, 'Export Complete');
        });
    },

    // ==================== ENDUSER NOTIFICATIONS & INCIDENTS ====================
    notifEvents: [],
    notifFilter: 'all',
    notifCurrentPage: 1,
    notifPageSize: 10,

    loadEnduserNotifications: function() {
        const tbody = document.getElementById('uniselv-notifs-tbody');
        if (!tbody) return;
        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; color:#64748b; padding:20px;">Refreshing incident events...</td></tr>';

        this.callApi('notifications', {}, (err, res) => {
            if (err || res.error) {
                tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; color:#b91c1c; padding:20px;">Failed to load events: ${err || res.error}</td></tr>`;
                return;
            }

            this.notifEvents = res.events || [];
            const badge = document.getElementById('uniselv-notif-count-badge');
            if (badge) {
                badge.innerText = this.notifEvents.length;
            }
            this.notifCurrentPage = 1;
            this.renderNotificationsPage();
        });
    },

    filterNotifications: function(val) {
        this.notifFilter = val || 'all';
        this.notifCurrentPage = 1;
        this.renderNotificationsPage();
    },

    renderNotificationsPage: function() {
        const tbody = document.getElementById('uniselv-notifs-tbody');
        if (!tbody) return;

        const all = this.notifEvents || [];
        const filtered = all.filter(e => {
            const st = (e.status || 'unread').toLowerCase();
            if (this.notifFilter === 'unread') return st === 'unread';
            if (this.notifFilter === 'read') return st === 'read';
            if (this.notifFilter === 'dismissed') return st === 'dismissed';
            return true;
        });

        if (filtered.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" style="padding:0; border:none;">
                        <div class="uniselv-empty-box">
                            <div class="uniselv-empty-icon">
                                <svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                            </div>
                            <div class="uniselv-empty-title">No Incident Events</div>
                            <div class="uniselv-empty-desc">No resource threshold warnings or throttling events match this filter. All hosting limits are currently respected.</div>
                        </div>
                    </td>
                </tr>
            `;
            const pag = document.getElementById('uniselv-notif-pagination');
            if (pag) pag.innerHTML = '';
            return;
        }

        const totalItems = filtered.length;
        const totalPages = Math.max(1, Math.ceil(totalItems / this.notifPageSize));
        this.notifCurrentPage = Math.min(Math.max(1, this.notifCurrentPage), totalPages);

        const startIdx = (this.notifCurrentPage - 1) * this.notifPageSize;
        const pageItems = filtered.slice(startIdx, startIdx + this.notifPageSize);

        let html = '';
        const eventTime = new Intl.DateTimeFormat('en-GB', {
            day: 'numeric', month: 'short', year: 'numeric',
            hour: '2-digit', minute: '2-digit', second: '2-digit', timeZoneName: 'short'
        });
        pageItems.forEach(e => {
            const badge = (e.severity === 'critical') ? 'badge-critical' : ((e.severity === 'warning') ? 'badge-warning' : 'badge-normal');
            const st = (e.status || 'unread').toLowerCase();
            const statusBadge = (st === 'unread')
                ? '<span class="uniselv-badge badge-unread">UNREAD</span>'
                : ((st === 'dismissed') ? '<span class="uniselv-badge badge-outline">DISMISSED</span>' : '<span class="uniselv-badge badge-outline">READ</span>');

            let actionsHtml = '';
            if (st === 'unread') {
                actionsHtml = `<button class="uniselv-btn btn-outline btn-sm" onclick="UniselvResMan.markNotification(${e.id}, 'read')">Mark Read</button> ` +
                              `<button class="uniselv-btn btn-outline btn-sm" style="color:#ef4444;" onclick="UniselvResMan.markNotification(${e.id}, 'dismissed')">Dismiss</button>`;
            } else if (st === 'read') {
                actionsHtml = `<button class="uniselv-btn btn-outline btn-sm" onclick="UniselvResMan.markNotification(${e.id}, 'unread')">Mark Unread</button> ` +
                              `<button class="uniselv-btn btn-outline btn-sm" style="color:#ef4444;" onclick="UniselvResMan.markNotification(${e.id}, 'dismissed')">Dismiss</button>`;
            } else {
                actionsHtml = '<span style="color:#94a3b8; font-size:0.8rem;">Dismissed</span>';
            }

            const dt = eventTime.format(e.timestamp * 1000);
            html += `
                <tr class="uniselv-notif-row" data-status="${st}">
                    <td>${this.escapeHtml(dt)}</td>
                    <td>${this.escapeHtml(e.event_type || 'throttle')}</td>
                    <td><span class="uniselv-badge ${badge}">${(e.severity || 'info').toUpperCase()}</span></td>
                    <td>${statusBadge}</td>
                    <td>${this.escapeHtml(e.message || '')}</td>
                    <td>${actionsHtml}</td>
                </tr>
            `;
        });
        tbody.innerHTML = html;

        UniselvPagination.render({
            containerId: 'uniselv-notif-pagination',
            totalItems: totalItems,
            currentPage: this.notifCurrentPage,
            pageSize: this.notifPageSize,
            onPageChange: (newPage) => {
                this.notifCurrentPage = newPage;
                this.renderNotificationsPage();
            },
            onPageSizeChange: (newSize) => {
                this.notifPageSize = newSize;
                this.notifCurrentPage = 1;
                this.renderNotificationsPage();
            }
        });
    },

    markNotification: function(eventId, status) {
        this.callApi('mark_notification', { event_id: eventId, status: status }, (err, res) => {
            if (err || res.error) {
                UniselvNotify.error(`Failed to update notification: ${err || res.error}`);
            } else {
                UniselvNotify.success(res.message || `Notification marked as ${status}.`);
                this.loadEnduserNotifications();
            }
        });
    },

    markAllNotifications: function(status) {
        this.callApi('mark_notification', { all: 1, status: status }, (err, res) => {
            if (err || res.error) {
                UniselvNotify.error(`Failed to update all notifications: ${err || res.error}`);
            } else {
                UniselvNotify.success(res.message || `All notifications marked as ${status}.`);
                this.loadEnduserNotifications();
            }
        });
    },

    clearAllNotifications: function() {
        UniselvModal.confirm({
            title: 'Clear All Incident Notifications?',
            message: 'Are you sure you want to dismiss all recorded incident notifications? All events will be marked as dismissed.',
            icon: 'warning',
            confirmText: 'Dismiss All',
            isDanger: true,
            onConfirm: () => {
                this.markAllNotifications('dismissed');
            }
        });
    },

    openOverrideModal: function(user, currentPlan) {
        const quickUser = document.getElementById('quick-override-username');
        const card = document.getElementById('card-temporary-boost');
        if (quickUser && card) {
            quickUser.value = user;
            this.switchTab('accounts');
            card.scrollIntoView({ behavior: 'smooth', block: 'center' });
            card.classList.add('uniselv-card-highlight');
            setTimeout(() => card.classList.remove('uniselv-card-highlight'), 1800);
            return;
        }
        const modal = document.getElementById('uniselv-override-modal');
        if (modal) {
            document.getElementById('override-username').value = user;
            document.getElementById('override-target-display').innerText = user;
            modal.style.display = 'flex';
        }
    },

    submitQuickOverride: function() {
        const username = document.getElementById('quick-override-username') ? document.getElementById('quick-override-username').value : '';
        if (!username) {
            UniselvNotify.warning('Please select a target account to boost.');
            return;
        }
        const plan = document.getElementById('quick-override-plan') ? document.getElementById('quick-override-plan').value : 'turbo';
        const duration = document.getElementById('quick-override-duration') ? document.getElementById('quick-override-duration').value : 60;
        const reason = document.getElementById('quick-override-reason') ? document.getElementById('quick-override-reason').value : 'Temporary high-traffic event';

        this.callApi('set_override', {
            username: username,
            override_plan: plan,
            duration_minutes: duration,
            reason: reason
        }, (err, res) => {
            if (err || res.error) {
                UniselvNotify.error(`Failed to set temporary override: ${err || res.error}`);
            } else {
                UniselvNotify.success(res.message || 'Temporary override granted successfully');
                setTimeout(() => location.reload(), 1200);
            }
        });
    },


    closeModal: function(id) {
        const modal = document.getElementById(id);
        if (modal) modal.style.display = 'none';
    },

    submitOverride: function() {
        const username = document.getElementById('override-username').value;
        const plan = document.getElementById('override-plan').value;
        const duration = document.getElementById('override-duration').value;
        const reason = document.getElementById('override-reason').value;

        this.callApi('set_override', {
            username: username,
            override_plan: plan,
            duration_minutes: duration,
            reason: reason
        }, (err, res) => {
            if (err || res.error) {
                UniselvNotify.error(`Failed to set temporary override: ${err || res.error}`);
            } else {
                UniselvNotify.success(res.message || 'Temporary override granted');
                setTimeout(() => location.reload(), 1200);
            }
        });
    },

    syncNativePlans: function() {
        UniselvModal.confirm({
            title: 'Bulk Synchronize Resource Limits?',
            message: 'This will reapply native resource limits across all hosting accounts and reconcile systemd slices with zero policy drift.',
            icon: 'warning',
            confirmText: 'Sync All Plans',
            isDanger: false,
            onConfirm: () => {
                this.callApi('sync_plans', {}, (err, res) => {
                    const runtimeErrors = res?.runtime_errors || [];
                    if (err || !res || res.error || res.success === false || runtimeErrors.length || Number(res.failed_count || 0) > 0) {
                        const reason = err || res?.error || (runtimeErrors.length ? 'PHP runtime reload failed: ' + runtimeErrors.map(x => x.version).join(', ') : 'Some accounts could not be synchronized.');
                        UniselvNotify.error(`Sync failed: ${reason}`);
                        return;
                    }
                    const accounts = Number.isFinite(res.synced_count) ? res.synced_count : null;
                    const plans = Array.isArray(res.synced_plans) ? res.synced_plans.length : null;
                    if (accounts === null && plans === null) { UniselvNotify.error('Sync result could not be verified. Check the audit log.'); return; }
                    UniselvNotify.success(`Successfully synchronized ${accounts ?? plans} ${accounts !== null ? 'accounts' : 'resource plans'}.`);
                    setTimeout(() => location.reload(), 1200);
                });
            }
        });
    },

    toggleMaintenanceMode: function(enable) {
        const isEnabling = (enable === true || enable === 1 || enable === '1' || enable === 'true');
        const title = isEnabling ? 'Enable Maintenance Mode?' : 'Disable Maintenance Mode?';
        const msg = isEnabling
            ? 'Are you sure you want to enable Maintenance Mode? This will pause automated background telemetry sampling while keeping temporary boost expirations active.'
            : 'Are you sure you want to disable Maintenance Mode? This will resume continuous background telemetry sampling and incident monitoring across all accounts.';
        const confirmText = isEnabling ? 'Enable Maintenance' : 'Disable Maintenance';
        const iconType = isEnabling ? 'warning' : 'info';

        UniselvModal.confirm({
            title: title,
            message: msg,
            icon: iconType,
            confirmText: confirmText,
            isDanger: false,
            onConfirm: () => {
                this.callApi('set_maintenance', { enabled: isEnabling ? 1 : 0 }, (err, res) => {
                    if (err || res.error) {
                        UniselvNotify.error(`Failed to change maintenance mode: ${err || res.error}`);
                    } else {
                        const stateStr = res.maintenance_mode ? 'ENABLED' : 'DISABLED';
                        UniselvNotify.success(`Maintenance mode is now ${stateStr}`);
                        setTimeout(() => location.reload(), 1000);
                    }
                });
            }
        });
    },

    openGoldenModal: function() {
        const card = document.getElementById('card-golden-reconfigure');
        if (card) {
            this.switchTab('goldenshield');
            card.scrollIntoView({ behavior: 'smooth', block: 'center' });
            card.classList.add('uniselv-card-highlight');
            setTimeout(() => card.classList.remove('uniselv-card-highlight'), 1800);
            return;
        }
        const modal = document.getElementById('uniselv-golden-modal');
        if (modal) modal.style.display = 'flex';
    },

    onGoldenModeChange: function(val) {
        const mode = val || (document.getElementById('golden-mode-select') ? document.getElementById('golden-mode-select').value : 'AUTO');
        ['golden-manual-fields', 'golden-manual-fields-modal'].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.style.display = (mode.toUpperCase() === 'MANUAL') ? 'block' : 'none';
        });
    },

    submitGoldenReconfigure: function() {
        const modeEl = document.getElementById('golden-mode-select') || document.getElementById('golden-mode');
        const mode = modeEl ? modeEl.value : 'AUTO';
        const cpuEl = document.getElementById('golden-cpu-pct') || document.getElementById('golden-cpu-pct-modal');
        const memEl = document.getElementById('golden-mem-mib') || document.getElementById('golden-mem-mib-modal');
        const params = { mode: mode };
        if (mode.toUpperCase() === 'MANUAL') {
            const cpu = Number(cpuEl?.value), mem = Number(memEl?.value);
            if (!Number.isInteger(cpu) || !Number.isInteger(mem) || cpu <= 0 || mem <= 0) {
                UniselvNotify.error('Enter valid positive CPU and memory values for Manual mode.');
                return;
            }
            params.customer_cpu_pct = cpu;
            params.hosting_mem_mib = mem;
        }
        this.callApi('golden_reconfigure', params, (err, res) => {
            if (err || res.error) {
                UniselvNotify.error(`Reconfiguration failed: ${err || res.error}`);
            } else {
                UniselvNotify.success(res.message || 'Golden Shield reconfigured and applied successfully.');
                setTimeout(() => location.reload(), 1200);
            }
        });
    },

    verifyGoldenShield: function() {
        this.callApi('golden_verify', {}, (err, res) => {
            if (err || res.error) {
                UniselvNotify.error(`Verification check failed: ${err || res.error}`);
            } else {
                const r = res.results || res.report || {};
                const verified = res.verified || res.success;
                const outsideCount = (res.outside_processes || []).length || r.outside_processes_count || 0;
                const drift = res.hardware_drift || r.hardware_drift;

                if (verified && outsideCount === 0 && !drift) {
                    UniselvNotify.success(`All kernel limits verified: CPU, Memory, and Swap limits match governor policy. 0 Escaped Processes.`, 'Verification Passed');
                } else {
                    let warnMsg = `Verification Notice: `;
                    if (!verified) warnMsg += `Checks failed. `;
                    if (outsideCount > 0) warnMsg += `${outsideCount} outside processes. `;
                    if (drift) warnMsg += `Hardware drift detected. `;
                    UniselvNotify.warning(warnMsg, 'Verification Findings');
                }
            }
        });
    },

    disableGoldenShield: function() {
        UniselvModal.confirm({
            title: 'Disable Golden Shield Governor?',
            message: 'Disabling Golden Shield removes hosting pool CPU quota and aggregate memory protection from the kernel. Customer slices will fall back to uncoordinated individual limits.',
            icon: 'danger',
            confirmText: 'Disable Golden Shield',
            isDanger: true,
            onConfirm: () => {
                this.callApi('golden_disable', {}, (err, res) => {
                    if (err || res.error) {
                        UniselvNotify.error(`Failed to disable: ${err || res.error}`);
                    } else {
                        UniselvNotify.success(res.message || 'Golden Shield disabled successfully.');
                        setTimeout(() => location.reload(), 1200);
                    }
                });
            }
        });
    },

    // ==================== GOLDEN SHIELD BACKUP RESTORE ====================
    selectedBackupId: null,

    refreshBackupsList: function() {
        const containers = ['uniselv-backups-container', 'uniselv-backups-container-modal'];
        containers.forEach(cid => {
            const container = document.getElementById(cid);
            if (!container) return;
            container.innerHTML = '<div style="text-align:center; padding:15px; color:#64748b;">Loading configuration backups...</div>';
            this.callApi('golden_list_backups', {}, (err, res) => {
                if (err || res.error) {
                    container.innerHTML = `<div style="color:#b91c1c; padding:12px;">Failed to load backups: ${err || res.error}</div>`;
                    return;
                }
                const backups = res.backups || [];
                if (backups.length === 0) {
                    container.innerHTML = '<div style="text-align:center; padding:15px; color:#64748b; font-size:0.86rem;">No configuration backup checkpoints found. Backups are automatically created before any policy reconfiguration.</div>';
                    return;
                }
                let html = '';
                backups.forEach(b => {
                    const dateStr = new Date(b.created_at * 1000).toLocaleString();
                    const p = b.policy || {};
                    html += `
                        <div class="uniselv-backup-item ${UniselvResMan.selectedBackupId === b.id ? 'selected' : ''}" id="backup-item-${b.id}" onclick="UniselvResMan.selectBackup('${b.id}')">
                            <div>
                                <div style="font-weight:700; color:#1e293b; font-size:0.88rem;">${b.id} <span class="uniselv-badge badge-outline" style="margin-left:6px; font-size:0.75rem;">MODE: ${b.mode || 'AUTO'}</span></div>
                                <div style="font-size:0.78rem; color:#64748b; margin-top:2px;">Created: ${dateStr}</div>
                                <div style="font-size:0.8rem; color:#475569; margin-top:4px;">
                                    CPU: <strong>${p.customerCpuPercent || 'n/a'}%</strong> | RAM Cap: <strong>${p.hostingMemoryMaxMiB || 'n/a'} MiB</strong> | Headroom: <strong>${p.headroomMiB || 'n/a'} MiB</strong>
                                </div>
                            </div>
                            <div>
                                <span class="uniselv-badge ${UniselvResMan.selectedBackupId === b.id ? 'badge-success' : 'badge-normal'}" id="backup-badge-${b.id}">${UniselvResMan.selectedBackupId === b.id ? 'Selected' : 'Select'}</span>
                            </div>
                        </div>
                    `;
                });
                container.innerHTML = html;
            });
        });
    },

    openRestoreBackupModal: function() {
        const card = document.getElementById('card-golden-restore');
        if (card) {
            this.switchTab('goldenshield');
            card.scrollIntoView({ behavior: 'smooth', block: 'center' });
            card.classList.add('uniselv-card-highlight');
            setTimeout(() => card.classList.remove('uniselv-card-highlight'), 1800);
            this.refreshBackupsList();
            return;
        }
        const modal = document.getElementById('uniselv-restore-modal');
        if (modal) modal.style.display = 'flex';
        this.refreshBackupsList();
    },

    selectBackup: function(backupId) {
        this.selectedBackupId = backupId;
        document.querySelectorAll('.uniselv-backup-item').forEach(el => el.classList.remove('selected'));
        document.querySelectorAll('[id^="backup-badge-"]').forEach(el => {
            el.className = 'uniselv-badge badge-normal';
            el.innerText = 'Select';
        });

        const activeItems = document.querySelectorAll(`[id="backup-item-${backupId}"]`);
        const activeBadges = document.querySelectorAll(`[id="backup-badge-${backupId}"]`);
        activeItems.forEach(el => el.classList.add('selected'));
        activeBadges.forEach(el => {
            el.className = 'uniselv-badge badge-success';
            el.innerText = 'Selected';
        });
    },

    submitRestoreBackup: function() {
        if (!this.selectedBackupId) {
            UniselvNotify.warning('Please select a backup checkpoint to restore.');
            return;
        }

        UniselvModal.confirm({
            title: `Restore Backup ${this.selectedBackupId}?`,
            message: 'This will atomically restore policy settings, apply memory/CPU limits to the kernel, and update persistent systemd slice drop-ins. A rollback checkpoint is created automatically in case verification fails.',
            icon: 'warning',
            confirmText: 'Restore & Apply',
            isDanger: false,
            onConfirm: () => {
                this.callApi('golden_restore', { backup_id: this.selectedBackupId }, (err, res) => {
                    if (err || res.error || !res.success) {
                        UniselvNotify.error(`Restoration failed: ${err || res.error || 'Verification rejected'}`);
                    } else {
                        UniselvNotify.success(res.message || 'Backup successfully restored and verified.');
                        this.closeModal('uniselv-restore-modal');
                        setTimeout(() => location.reload(), 1200);
                    }
                });
            }
        });
    },

    // ==================== MODERN HELP & ABOUT SYSTEM ====================
    activeHelpCategory: 'all',

    setHelpCategory: function(cat) {
        this.activeHelpCategory = cat;
        document.querySelectorAll('.uniselv-cat-btn').forEach(btn => {
            btn.classList.toggle('active', btn.getAttribute('data-cat') === cat);
        });
        this.filterHelp();
    },

    filterHelp: function() {
        const query = (document.getElementById('help-search-input')?.value || '').toLowerCase().trim();
        const cat = this.activeHelpCategory;

        document.querySelectorAll('.uniselv-help-card').forEach(card => {
            const cardCat = card.getAttribute('data-cat') || '';
            const text = card.innerText.toLowerCase();

            const matchesCat = (cat === 'all' || cardCat === cat);
            const matchesQuery = (!query || text.includes(query));

            card.style.display = (matchesCat && matchesQuery) ? 'block' : 'none';
        });
    },

    openHelpTopic: function(topicKey) {
        // Switch to the 'help' tab
        const helpBtn = document.querySelector('.uniselv-tab-btn[data-tab="help"]');
        if (helpBtn) {
            helpBtn.click();
        }

        setTimeout(() => {
            // Reset filters to show all
            this.setHelpCategory('all');
            const searchInput = document.getElementById('help-search-input');
            if (searchInput) searchInput.value = '';

            const target = document.getElementById(`help-topic-${topicKey}`);
            if (target) {
                target.style.display = 'block';
                target.scrollIntoView({ behavior: 'smooth', block: 'center' });
                target.style.transition = 'box-shadow 0.3s ease, border-color 0.3s ease';
                target.style.boxShadow = '0 0 0 3px rgba(37, 99, 235, 0.4)';
                target.style.borderColor = 'var(--uniselv-primary)';
                setTimeout(() => {
                    target.style.boxShadow = '';
                    target.style.borderColor = '';
                }, 2500);
            }
        }, 150);
    },

    copyToClipboard: function(text, btn) {
        if (navigator.clipboard && window.isSecureContext) {
            navigator.clipboard.writeText(text).then(() => {
                this.indicateCopied(btn);
            }).catch(() => {
                this.fallbackCopy(text, btn);
            });
        } else {
            this.fallbackCopy(text, btn);
        }
    },

    fallbackCopy: function(text, btn) {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.opacity = '0';
        document.body.appendChild(textArea);
        textArea.select();
        try {
            document.execCommand('copy');
            this.indicateCopied(btn);
        } catch (e) {
            UniselvNotify.error('Failed to copy to clipboard.');
        }
        document.body.removeChild(textArea);
    },

    indicateCopied: function(btn) {
        if (!btn) return;
        const origText = btn.innerHTML;
        btn.innerHTML = '&#10003; Copied!';
        btn.style.background = 'rgba(5, 150, 105, 0.8)';
        btn.style.color = '#ffffff';
        setTimeout(() => {
            btn.innerHTML = origText;
            btn.style.background = '';
            btn.style.color = '';
        }, 2000);
    },

    // ==================== ADMIN OVERVIEW LIVE POLLING ====================
    loadAdminOverview: function() {
        this.requestLiveTelemetry('overview', (err, res) => {
            if (err || !res || res.error) { this.showTelemetryFreshness(null, true); return; }
            const host = res.host || res.server || {};
            this.showTelemetryFreshness(host.last_sample_epoch);
            const shield = res.golden_shield || {};
            const calc = shield.configured_policy || {};

            // 1. Hardware Detection
            const cores = this.metricNumber(host.cpu_cores ?? host.cpu_count);
            const hwCpuEl = document.getElementById('admin-card-hw-cpu');
            if (hwCpuEl && cores > 0) hwCpuEl.textContent = cores + ' vCPUs';
            const hostCpu = host.telemetry_available === false ? null : this.metricNumber(host.cpu_percent);
            const hostCpuEl = document.getElementById('admin-host-cpu-usage');
            if (hostCpuEl) hostCpuEl.textContent = hostCpu === null ? '—' : hostCpu.toFixed(1) + '%';
            const hwRamEl = document.getElementById('admin-host-ram-value');
            if (hwRamEl && (host.total_ram_formatted || host.mem_total_formatted)) {
                hwRamEl.textContent = host.total_ram_formatted || host.mem_total_formatted;
            }

            // 2. Shared CPU Headroom
            const cpuHeadroomEl = document.getElementById('admin-card-cpu-headroom');
            if (cpuHeadroomEl) {
                const quota = this.metricNumber(shield.customer_cpu_percent ?? calc.customerCpuPercent);
                cpuHeadroomEl.textContent = quota === null || !(cores > 0) ? '—' :
                    (quota / 100).toFixed(2).replace(/\.?0+$/, '') + ' / ' + cores;
            }
            const cpuSubEl = document.getElementById('admin-card-cpu-sub');
            if (cpuSubEl) {
                const reserve = this.metricNumber(shield.reserved_cpu_percent ?? calc.reservedCpuPercent);
                cpuSubEl.textContent = reserve === null ? 'System reserve unavailable' :
                    'System reserve: ' + (reserve / 100).toFixed(2).replace(/\.?0+$/, '') + ' vCPU equivalent';
            }

            // 3. RAM Safety Budget
            const ramCurrEl = document.getElementById('admin-card-ram-curr');
            if (ramCurrEl) {
                ramCurrEl.textContent = shield.golden_mem_current_formatted ?? 'Unavailable';
            }
            const ramCapEl = document.getElementById('admin-card-ram-cap');
            if (ramCapEl) {
                const maxFmt = shield.golden_mem_max_formatted || (calc.hostingMemoryMaxMiB ? (Math.round(calc.hostingMemoryMaxMiB / 1024 * 100) / 100) + ' GiB' : 'Unavailable');
                const hMib = shield.headroom_mib ?? calc.headroomMiB ?? 'Unavailable';
                ramCapEl.textContent = 'Hosting Cap: ' + maxFmt + ' (Reserve: ' + hMib + ' MiB)';
            }

            // 4. System Load
            const loadValue = key => {
                const value = host.telemetry_available === false ? null : this.metricNumber(host[key]);
                return value === null ? '—' : value.toFixed(2);
            };
            const load1El = document.getElementById('admin-card-load-1');
            if (load1El) load1El.textContent = loadValue('load1');
            const loadSubEl = document.getElementById('admin-card-load-sub-values');
            if (loadSubEl) loadSubEl.textContent = '5m: ' + loadValue('load5') + ' | 15m: ' + loadValue('load15');
            const loadStatus = document.getElementById('admin-load-status');
            if (loadStatus) {
                const {load} = this.adminGaugePercentages(host, shield);
                loadStatus.classList.toggle('badge-warning', load !== null && load >= 100);
                loadStatus.classList.toggle('badge-normal', load !== null && load < 100);
                loadStatus.textContent = load === null ? this.translate('unavailable', 'Unavailable') :
                    (load >= 100 ? this.translate('load_elevated', 'Elevated') : this.translate('load_below', 'Below capacity'));
            }
            // Update Admin Gauges & Dynamic Live Footers
            if (typeof this.updateGaugeCard === 'function') {
                const metrics = this.adminGaugePercentages(host,shield);
                const loadPct=metrics.load, cCpuPct=metrics.cpu, ramPct=metrics.ram;
                this.updateGaugeCard('admin-hw', hostCpu);
                this.updateGaugeCard('admin-cpu',cCpuPct);
                this.updateGaugeCard('admin-ram',ramPct);
                this.updateGaugeCard('admin-load',loadPct);
                const cpuGauge=document.getElementById('uniselv-arc-admin-cpu')?.closest('.uniselv-gauge-wrap');
                if(cpuGauge && cCpuPct!==null)cpuGauge.title=`Configured hosting allocation: ${cCpuPct.toFixed(1)}% of total visible CPU capacity. This is a policy share, not live CPU usage.`;
                const loadGauge=document.getElementById('uniselv-arc-admin-load')?.closest('.uniselv-gauge-wrap');
                if(loadGauge && loadPct!==null)loadGauge.title=`One-minute load divided by vCPU count: ${loadPct.toFixed(1)}%. Load is not CPU utilization; visual fill is capped at 100%.`;
                // Update Dynamic Footers (Sparklines & Equalizers)
                if (typeof this.updateAdminSparkline === 'function') {
                    this.updateAdminSparkline('admin-sparkline-hw', hostCpu, host.last_sample_epoch);
                    this.updateAdminSparkline('admin-sparkline-cpu', cCpuPct,host.last_sample_epoch);
                }
                if (typeof this.updateEqualizer === 'function') {
                    this.updateEqualizer('admin-eq-ram', ramPct, true);
                    this.updateEqualizer('admin-eq-load', loadPct, true);
                }
            }

            // Real-time Top Consumers Table Update
            if (Array.isArray(res.top_consumers)) {
                this.renderTopConsumers(res.top_consumers);
            }

            // Real-time Active Resource Boosts Countdown Banner Update
            if (res.active_boosts) {
                this.renderActiveBoostsBanner(res.active_boosts);
            }
        });
    },

    renderTopConsumers: function(consumers) {
        const tbody = document.getElementById('uniselv-top-consumers-tbody');
        if (!tbody) return;
        if (!consumers || !consumers.length) {
            tbody.innerHTML = '<tr><td colspan="9" style="text-align:center;color:#64748b;padding:16px;">No account telemetry recorded yet.</td></tr>';
            return;
        }
        tbody.innerHTML = '';
        consumers.forEach(acc => {
            const tr = document.createElement('tr');
            const pct = Number(acc.cpu_allowance_percent) || 0;
            const badge = pct > 90 ? 'badge-critical' : (pct > 60 ? 'badge-warning' : 'badge-normal');
            const statusTxt = pct > 90 ? 'CRITICAL' : (pct > 60 ? 'ELEVATED' : 'NORMAL');
            const sampleTime = acc.last_sample_epoch ? new Date(acc.last_sample_epoch * 1000).toLocaleTimeString() : 'Unavailable';
            
            tr.innerHTML = `
                <td><strong>${this.escapeHtml(acc.username)}</strong><br><small style="color:#64748b;">${this.escapeHtml(acc.domain || '')}</small></td>
                <td><span class="uniselv-badge badge-normal">${this.escapeHtml(String(acc.plan_name || 'default').toUpperCase())}</span></td>
                <td>${Number(acc.cpu_percent || 0).toFixed(1)}%</td>
                <td><span class="uniselv-badge ${badge}">${pct.toFixed(1)}% (${statusTxt})</span></td>
                <td>${this.escapeHtml(acc.mem_formatted || '0 B')}</td>
                <td>${acc.tasks_current || 0} / ${acc.tasks_max || '-'}</td>
                <td>${acc.throttled_events || 0}</td>
                <td>${sampleTime}</td>
                <td>
                    <button class="uniselv-btn btn-outline btn-sm" onclick="UniselvResMan.openOverrideModal('${this.escapeHtml(acc.username)}', '${this.escapeHtml(acc.plan_name || '')}')">Grant Boost</button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    },

    renderActiveBoostsBanner: function(boostsData) {
        const banner = document.getElementById('uniselv-active-boosts-banner');
        if (!banner) return;
        const list = boostsData?.boosts || [];
        if (!list.length) {
            banner.innerHTML = '';
            banner.style.display = 'none';
            return;
        }
        banner.style.display = 'block';
        let itemsHtml = list.map(b => `
            <div style="display:flex;align-items:center;justify-content:space-between;background:rgba(255,255,255,0.7);padding:6px 12px;border-radius:6px;margin-top:6px;font-size:0.83rem;">
                <div>
                    <strong>${this.escapeHtml(b.username)}</strong>: Plan boosted from <code>${this.escapeHtml(b.original_plan || 'base')}</code> &rarr; <span class="uniselv-badge badge-warning" style="font-weight:700;">${this.escapeHtml(String(b.target_plan).toUpperCase())}</span>
                    <span style="color:#64748b;margin-left:8px;">(${this.escapeHtml(b.reason || 'Manual boost')})</span>
                </div>
                <div style="display:flex;align-items:center;gap:10px;">
                    <span style="color:#b45309;font-weight:700;">⏳ ${b.remaining_minutes} min remaining</span>
                    <button class="uniselv-btn btn-danger btn-sm" style="padding:2px 8px;font-size:0.75rem;" onclick="UniselvResMan.revokePlanOverride(${b.id}, '${this.escapeHtml(b.username)}')">Revoke Now</button>
                </div>
            </div>
        `).join('');

        banner.innerHTML = `
            <div style="background:#fffbeb;border:1px solid #fde68a;border-left:4px solid #f59e0b;padding:10px 14px;border-radius:8px;margin-bottom:16px;">
                <div style="display:flex;align-items:center;justify-content:space-between;">
                    <span style="font-weight:700;color:#92400e;font-size:0.88rem;">🚀 Active Temporary Resource Boosts (${list.length})</span>
                    <span style="font-size:0.78rem;color:#b45309;">Auto-reverts to original plan when countdown expires</span>
                </div>
                ${itemsHtml}
            </div>
        `;
    },

    revokePlanOverride: function(id, username) {
        if (!confirm(`Are you sure you want to revoke the temporary resource boost for ${username}? This will immediately restore their original plan limits.`)) return;
        this.callApi('cancel_temporary_override', { id: id, username: username }, (err, res) => {
            const d = res?.data || res;
            if (err || !d?.success) {
                UniselvNotify.error(err || d?.error || 'Failed to revoke temporary override');
            } else {
                UniselvNotify.success(`Resource boost revoked for ${username}. Original plan restored.`);
                this.loadAdminOverview();
            }
        });
    },

    // ==================== CAPACITY PLANNING & OVERSELL (A11, G06) ====================
    loadCapacityPlanning: function() {
        const loading = document.getElementById('capacity-loading');
        const content = document.getElementById('capacity-content');
        if (loading) loading.style.display = 'block';
        if (content) content.style.display = 'none';

        this.callApi('capacity', {}, (err, res) => {
            if (loading) loading.style.display = 'none';
            if (err || res.error) {
                if (loading) {
                    loading.style.display = 'block';
                    loading.innerHTML = `<span style="color: #b91c1c;">Failed to load capacity planning: ${err || res.error}</span>`;
                }
                return;
            }

            if (content) content.style.display = 'block';
            const sum = res.summary || {};
            const hw = res.physical_hardware || {};
            const pool = res.golden_shield_pool || {};
            const sold = res.sold_allocations || {};
            const peaks = res.observed_24h_peaks || {};

            // Risk badge
            const riskBadge = document.getElementById('cap-risk-badge');
            if (riskBadge) {
                const risk = (sum.capacity_risk || 'LOW').toUpperCase();
                riskBadge.textContent = risk;
                riskBadge.className = 'uniselv-badge ' + (risk === 'CRITICAL' ? 'badge-critical' : (risk === 'MODERATE' ? 'badge-warning' : 'badge-normal'));
            }

            // Commit ratios
            const cpuCommit = document.getElementById('cap-cpu-commit');
            if (cpuCommit) cpuCommit.textContent = (sum.cpu_commit_ratio ?? 'Unavailable') + ' : 1';
            const cpuSoldSub = document.getElementById('cap-cpu-sold-sub');
            const acctCount = sum.total_accounts ?? res.capacity?.total_accounts ?? res.total_accounts ?? 0;
            if (cpuSoldSub) cpuSoldSub.textContent = `Sold: ${sold.total_sold_cpu_pct || 0}% across ${acctCount} accounts`;

            const memCommit = document.getElementById('cap-mem-commit');
            if (memCommit) memCommit.textContent = (sum.mem_commit_ratio ?? 'Unavailable') + ' : 1';
            const memSoldSub = document.getElementById('cap-mem-sold-sub');
            if (memSoldSub) memSoldSub.textContent = `Sold: ${sold.total_sold_mem_mib || 0} MiB (${Math.round((sold.total_sold_mem_mib || 0)/1024)} GiB)`;

            // Physical boundary
            const physDesc = document.getElementById('cap-physical-desc');
            if (physDesc) physDesc.textContent = `${hw.cpu_cores ?? 'Unavailable'} vCPUs / ${hw.ram_total_mib != null ? Math.round(hw.ram_total_mib/1024*100)/100 : 'Unavailable'} GiB RAM`;
            const poolDesc = document.getElementById('cap-golden-pool-desc');
            if (poolDesc) poolDesc.textContent = `Pool: ${pool.hosting_cpu_quota_pct ?? 'Unavailable'}% Quota / ${pool.system_headroom_cpu_pct ?? 'Unavailable'}% Headroom`;

            // Decoupled independent 24h peaks
            const peakCpu = document.getElementById('cap-peak-cpu-val');
            if (peakCpu) peakCpu.textContent = (peaks.peak_concurrent_cpu_pct || 0) + ' %';
            const peakCpuTime = document.getElementById('cap-peak-cpu-time');
            if (peakCpuTime) {
                const ts = peaks.peak_concurrent_cpu_timestamp;
                peakCpuTime.textContent = ts ? 'Peak Recorded: ' + new Date(ts * 1000).toUTCString() : 'Continuous evaluation';
            }

            const peakMem = document.getElementById('cap-peak-mem-val');
            if (peakMem) peakMem.textContent = (peaks.peak_concurrent_mem_mib || 0) + ' MiB';
            const peakMemTime = document.getElementById('cap-peak-mem-time');
            if (peakMemTime) {
                const ts = peaks.peak_concurrent_mem_timestamp;
                peakMemTime.textContent = ts ? 'Peak Recorded: ' + new Date(ts * 1000).toUTCString() : 'Continuous evaluation';
            }
        });
    },

    // ==================== SCHEDULED REPORTS (A16) ====================
    loadScheduledReports: function() {
        const body = document.getElementById('reports-table-body');
        if (!body) return;
        body.innerHTML = '<tr><td colspan="7" style="text-align: center; color: #64748b; padding: 25px;">Loading scheduled reports...</td></tr>';

        this.callApi('scheduled_reports', {}, (err, res) => {
            if (err || res.error) {
                body.innerHTML = `<tr><td colspan="7" style="color: #b91c1c; text-align: center; padding: 20px;">Failed to load reports: ${err || res.error}</td></tr>`;
                return;
            }

            const reports = res.reports || [];
            if (reports.length === 0) {
                body.innerHTML = '<tr><td colspan="7" style="text-align: center; color: #64748b; padding: 30px;">No scheduled reports stored yet. Click "Generate Report Now" to trigger immediate evaluation.</td></tr>';
                return;
            }

            body.innerHTML = '';
            reports.forEach(r => {
                const tr = document.createElement('tr');
                const dt = new Date(r.timestamp * 1000).toUTCString();
                const sum = r.summary || {};
                tr.innerHTML = `
                    <td><strong>#${r.id}</strong></td>
                    <td>${dt}</td>
                    <td><span class="uniselv-badge badge-normal">${(r.report_type || 'daily').toUpperCase()}</span></td>
                    <td>${sum.total_accounts || 0}</td>
                    <td><code>load: ${sum.system_load || '0.00'}</code></td>
                    <td><span class="uniselv-badge badge-normal">${r.status === 'generated' ? 'Generated' : this.escapeHtml(r.status || 'Stored')}</span></td>
                    <td>
                        <button class="uniselv-btn btn-outline btn-sm" data-report-detail>
                            View Summary
                        </button>
                    </td>
                `;
                tr.querySelector('[data-report-detail]').addEventListener('click', () => this.showReportDetail(sum));
                body.appendChild(tr);
            });
        });
    },

    dispatchReportNow: function() {
        const typeSel = document.getElementById('scheduled-report-type');
        const reportType = typeSel ? typeSel.value : 'daily';
        UniselvNotify.info(`Generating ${reportType} report...`);

        this.callApi('dispatch_report', { report_type: reportType }, (err, res) => {
            if (err || res.error) {
                UniselvNotify.error(`Report generation failed: ${err || res.error}`);
                return;
            }
            UniselvNotify.success(`Report #${res.report_id} generated and stored.`);
            this.loadScheduledReports();
        });
    },

    showReportDetail: function(summaryJsonStr) {
        try {
            const summary = typeof summaryJsonStr === 'string' ? JSON.parse(summaryJsonStr) : summaryJsonStr;
            const formatted = JSON.stringify(summary, null, 2);
            UniselvModal.confirm({
                title: 'Report / Audit Details JSON',
                message: `<pre style="max-height: 350px; overflow-y: auto; background: #0f172a; color: #f8fafc; padding: 14px; border-radius: 8px; font-size: 0.78rem; text-align: left;">${this.escapeHtml(formatted)}</pre>`,
                confirmText: 'Close',
                cancelText: 'Copy JSON',
                onCancel: () => {
                    navigator.clipboard.writeText(formatted);
                    UniselvNotify.success('JSON copied to clipboard.');
                }
            });
        } catch (e) {
            UniselvNotify.error('Failed to parse details.');
        }
    },

    loadReportSchedule: function() {
        this.callApi('get_report_schedule', {}, (err, res) => {
            if (err || res.error) {
                console.error('Failed to load report schedule:', err || res?.error);
                return;
            }
            const cadenceSel = document.getElementById('report-schedule-cadence');
            if (cadenceSel && res.schedule) {
                cadenceSel.value = res.schedule;
            }
            const dueDiv = document.getElementById('report-schedule-next-due');
            if (dueDiv) {
                if (res.schedule === 'disabled' || !res.next_due_timestamp) {
                    dueDiv.textContent = 'Disabled';
                } else {
                    dueDiv.textContent = res.next_due_formatted || res.due_date || (res.next_due ? new Date(res.next_due * 1000).toUTCString() : 'Active');
                }
            }
            const badge = document.getElementById('report-schedule-status-badge');
            if (badge) {
                const sched = (res.schedule || 'daily').toUpperCase();
                badge.textContent = `Schedule: ${sched} ${res.schedule === 'disabled' ? 'Inactive' : 'Active'}`;
                badge.className = `uniselv-badge ${res.schedule === 'disabled' ? 'badge-normal' : 'badge-good'}`;
            }
        });
    },

    saveReportSchedule: function() {
        const cadence = (document.getElementById('report-schedule-cadence') || {}).value || 'daily';
        this.callApi('save_report_schedule', { schedule: cadence }, (err, res) => {
            if (err || res.error) {
                UniselvNotify.error(`Save failed: ${err || res.error}`);
                return;
            }
            UniselvNotify.success(`Report schedule updated to '${cadence}'.`);
            this.loadReportSchedule();
        });
    },

    // ==================== BRANDING & PACKAGE MAPPINGS (B02, B03, B05) ====================
    loadPackageMappings: function() {
        const body = document.getElementById('package-mappings-body');
        if (!body) return;
        body.innerHTML = '<tr><td colspan="3" style="text-align: center; color: #64748b; padding: 15px;">Loading mappings...</td></tr>';

        this.callApi('package_mappings', {}, (err, res) => {
            if (err || res.error) {
                body.innerHTML = `<tr><td colspan="3" style="color: #b91c1c; text-align: center;">Failed: ${this.escapeHtml(String(err || res.error))}</td></tr>`;
                return;
            }

            const maps = res.mappings || [];
            if (maps.length === 0) {
                body.innerHTML = '<tr><td colspan="3" style="text-align: center; color: #64748b; padding: 15px;">No package mappings configured yet.</td></tr>';
                return;
            }

            body.innerHTML = '';
            const availablePlans = new Set((res.native_plans || []).map(p => p.name));
            maps.forEach(m => {
                const tr = document.createElement('tr');
                tr.innerHTML = `<td><strong>${this.escapeHtml(m.billing_package)}</strong></td>
                    <td><code>${this.escapeHtml(m.resource_plan)}</code>${availablePlans.has(m.resource_plan) ? '' : ' <span class="uniselv-badge badge-warning">Missing native plan</span>'}</td>
                    <td><button class="uniselv-btn btn-danger btn-sm">Delete</button></td>`;
                tr.querySelector('button').addEventListener('click', () => this.deletePackageMapping(m.billing_package));
                body.appendChild(tr);
            });
        });
    },

    savePackageMapping: function() {
        const pkgInput = document.getElementById('map-billing-pkg');
        const planInput = document.getElementById('map-target-plan');
        const pkg = pkgInput ? pkgInput.value.trim() : '';
        const plan = planInput ? planInput.value.trim() : '';

        if (!pkg || !plan) {
            UniselvNotify.warning('Billing package name and target resource plan are required.');
            return;
        }

        this.callApi('save_package_mapping', { billing_package: pkg, resource_plan: plan }, (err, res) => {
            if (err || res.error) {
                UniselvNotify.error(`Save failed: ${err || res.error}`);
                return;
            }
            UniselvNotify.success(`Package mapping saved: '${pkg}' -> '${plan}'`);
            if (pkgInput) pkgInput.value = '';
            this.loadPackageMappings();
        });
    },

    deletePackageMapping: function(pkg) {
        UniselvModal.confirm({
            title: 'Delete Package Mapping',
            message: `Are you sure you want to delete the mapping for billing package <strong>${this.escapeHtml(pkg)}</strong>?`,
            isDanger: true,
            confirmText: 'Delete Mapping',
            onConfirm: () => {
                this.callApi('delete_package_mapping', { billing_package: pkg }, (err, res) => {
                    if (err || res.error) {
                        UniselvNotify.error(`Delete failed: ${err || res.error}`);
                        return;
                    }
                    UniselvNotify.success(`Mapping for '${pkg}' deleted successfully.`);
                    this.loadPackageMappings();
                });
            }
        });
    },

    saveBrandingSettings: function() {
        const name = (document.getElementById('brand-name-input') || {}).value || 'UNISELV Resource Manager';
        const logo = (document.getElementById('brand-logo-input') || {}).value || '';
        const color = (document.getElementById('brand-color-input') || {}).value || '#2563eb';
        const support = (document.getElementById('brand-support-input') || {}).value || '';
        const docs = (document.getElementById('brand-docs-input') || {}).value || '';
        const locale = (document.getElementById('brand-locale-select') || {}).value || 'en';

        this.callApi('branding_save', {
            brand_name: name,
            brand_logo_url: logo,
            brand_primary_color: color,
            brand_support_url: support,
            brand_docs_url: docs,
            brand_locale: locale
        }, (err, res) => {
            if (err || res.error) {
                UniselvNotify.error(`Save failed: ${err || res.error}`);
                return;
            }
            // Update active theme colors immediately
            document.documentElement.style.setProperty('--uniselv-primary', color);
            document.documentElement.style.setProperty('--primary-color', color);
            document.querySelectorAll('.uniselv-brand-title').forEach(el => el.textContent = name);
            UniselvNotify.success('Branding and theme settings persisted successfully.');
            const curLocale = document.getElementById('uniselv-locale-selector');
            if (curLocale && curLocale.value !== locale) {
                setTimeout(() => window.location.reload(), 600);
            }
        });
    },

    setLocale: function(newLocale) {
        if (!newLocale) return;
        this.callApi('branding_save', { brand_locale: newLocale }, (err, res) => {
            if (err || res.error) {
                UniselvNotify.error(`Failed to update locale: ${err || res.error}`);
                return;
            }
            window.location.reload();
        });
    },

    // ==================== ADMINISTRATIVE AUDIT LOG (B08) ====================
    auditLogEntries: [],
    auditCurrentPage: 1,
    auditPageSize: 20,

    loadAuditLogs: function() {
        const body = document.getElementById('audit-log-body');
        if (!body) return;
        body.innerHTML = '<tr><td colspan="5" style="text-align: center; color: #64748b; padding: 25px;">Loading administrative audit logs...</td></tr>';

        const search = (document.getElementById('audit-search-input') || {}).value || '';
        const actionType = (document.getElementById('audit-action-filter') || {}).value || '';

        this.callApi('audit_log', { search: search, action_type: actionType, limit: 500 }, (err, res) => {
            if (err || res.error) {
                body.innerHTML = `<tr><td colspan="5" style="color: #b91c1c; text-align: center; padding: 20px;">Failed to load logs: ${err || res.error}</td></tr>`;
                return;
            }

            this.auditLogEntries = res.audit_logs || res.logs || [];
            this.auditCurrentPage = 1;
            this.renderAuditLogsPage();
        });
    },

    renderAuditLogsPage: function() {
        const body = document.getElementById('audit-log-body');
        if (!body) return;

        const logs = this.auditLogEntries || [];
        if (logs.length === 0) {
            body.innerHTML = `
                <tr>
                    <td colspan="5" style="padding:0; border:none;">
                        <div class="uniselv-empty-box">
                            <div class="uniselv-empty-icon">
                                <svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                            </div>
                            <div class="uniselv-empty-title">No Audit Log Records</div>
                            <div class="uniselv-empty-desc">No administrative plan mutations, overrides, or system activities match the current filter.</div>
                        </div>
                    </td>
                </tr>
            `;
            const pag = document.getElementById('uniselv-audit-pagination');
            if (pag) pag.innerHTML = '';
            return;
        }

        const totalItems = logs.length;
        const totalPages = Math.max(1, Math.ceil(totalItems / this.auditPageSize));
        this.auditCurrentPage = Math.min(Math.max(1, this.auditCurrentPage), totalPages);

        const startIdx = (this.auditCurrentPage - 1) * this.auditPageSize;
        const pageItems = logs.slice(startIdx, startIdx + this.auditPageSize);

        body.innerHTML = '';
        pageItems.forEach(l => {
            const tr = document.createElement('tr');
            const dt = l.date_formatted || new Date(l.timestamp * 1000).toUTCString();
            const detailsStr = JSON.stringify(l.details || {});
            tr.innerHTML = `
                <td><small style="color: #64748b;">${dt}</small></td>
                <td><strong>${this.escapeHtml(l.actor)}</strong></td>
                <td><span class="uniselv-badge badge-normal">${this.escapeHtml(l.action)}</span></td>
                <td><code>${this.escapeHtml(l.target_account || 'all')}</code></td>
                <td>
                    <button class="uniselv-btn btn-outline btn-sm" data-audit-detail>
                        View Details
                    </button>
                </td>
            `;
            tr.querySelector('[data-audit-detail]').addEventListener('click', () => this.showReportDetail(detailsStr));
            body.appendChild(tr);
        });

        UniselvPagination.render({
            containerId: 'uniselv-audit-pagination',
            totalItems: totalItems,
            currentPage: this.auditCurrentPage,
            pageSize: this.auditPageSize,
            onPageChange: (newPage) => {
                this.auditCurrentPage = newPage;
                this.renderAuditLogsPage();
            },
            onPageSizeChange: (newSize) => {
                this.auditPageSize = newSize;
                this.auditCurrentPage = 1;
                this.renderAuditLogsPage();
            }
        });
    },

    clearAuditLogs: function() {
        UniselvModal.confirm({
            title: 'Clear Administrative Audit Log?',
            message: 'Are you sure you want to purge historical audit records? A record documenting this purge will be durably retained.',
            icon: 'danger',
            confirmText: 'Clear Audit Log',
            isDanger: true,
            onConfirm: () => {
                this.callApi('clear_audit_logs', {}, (err, res) => {
                    if (err || res.error) {
                        UniselvNotify.error(`Failed to clear audit log: ${err || res.error}`);
                    } else {
                        UniselvNotify.success(res.message || 'Audit log history purged successfully.');
                        this.loadAuditLogs();
                    }
                });
            }
        });
    },

    // ==================== ROLE & ACCOUNT FEATURE PERMISSIONS (B04) ====================
    loadPermissions: function() {
        const rBody = document.getElementById('role-permissions-body');
        const aBody = document.getElementById('account-permissions-body');
        if (!rBody || !aBody) return;

        rBody.innerHTML = '<tr><td colspan="4" style="text-align:center; color:#64748b; padding:10px;">Loading role baselines...</td></tr>';
        aBody.innerHTML = '<tr><td colspan="4" style="text-align:center; color:#64748b; padding:10px;">Loading account overrides...</td></tr>';

        this.callApi('get_permissions', {}, (err, res) => {
            if (err || res.error) {
                rBody.innerHTML = `<tr><td colspan="4" style="color:#b91c1c; text-align:center;">Failed: ${this.escapeHtml(String(err || res.error))}</td></tr>`;
                aBody.innerHTML = `<tr><td colspan="4" style="color:#b91c1c; text-align:center;">Failed: ${this.escapeHtml(String(err || res.error))}</td></tr>`;
                return;
            }

            const roles = res.role_permissions || [];
            if (roles.length === 0) {
                rBody.innerHTML = '<tr><td colspan="4" style="text-align:center; color:#64748b; padding:10px;">No role baselines found.</td></tr>';
            } else {
                let html = '';
                roles.forEach(r => {
                    const isGranted = Boolean(r.granted);
                    const badge = isGranted ? '<span class="uniselv-badge badge-normal">Allowed</span>' : '<span class="uniselv-badge badge-critical">Denied</span>';
                    const toggleAction = isGranted ? 0 : 1;
                    const btnLabel = isGranted ? 'Deny' : 'Allow';
                    const btnClass = isGranted ? 'btn-danger' : 'btn-primary';
                    html += `<tr>
                        <td><strong>${r.role}</strong></td>
                        <td><code>${r.permission}</code></td>
                        <td>${badge}</td>
                        <td>
                            <button class="uniselv-btn ${btnClass} btn-sm" onclick="UniselvResMan.saveRolePermission('${r.role}', '${r.permission}', ${toggleAction})">${btnLabel}</button>
                        </td>
                    </tr>`;
                });
                rBody.innerHTML = html;
            }

            const accs = res.account_permissions || [];
            if (accs.length === 0) {
                aBody.innerHTML = '<tr><td colspan="4" style="text-align:center; color:#64748b; padding:10px;">No custom overrides active (using role baselines).</td></tr>';
            } else {
                let html = '';
                accs.forEach(a => {
                    const isGranted = Boolean(a.granted);
                    const badge = isGranted ? '<span class="uniselv-badge badge-normal">Allowed</span>' : '<span class="uniselv-badge badge-critical">Denied</span>';
                    html += `<tr>
                        <td><strong>${a.username}</strong></td>
                        <td><code>${a.permission}</code></td>
                        <td>${badge}</td>
                        <td style="font-size:0.75rem; color:#64748b;">${a.updated_by || 'admin'}</td>
                    </tr>`;
                });
                aBody.innerHTML = html;
            }
        });
    },

    saveRolePermission: function(role, permission, granted) {
        this.callApi('save_role_permission', { role: role, permission: permission, granted: granted }, (err, res) => {
            if (err || res.error) {
                UniselvNotify.error(`Failed to update role baseline: ${err || res.error}`);
                return;
            }
            UniselvNotify.success(`Role baseline for ${role}:${permission} updated.`);
            this.loadPermissions();
        });
    },

    saveAccountPermission: function() {
        const user = (document.getElementById('perm-user-input') || {}).value;
        const perm = (document.getElementById('perm-key-select') || {}).value;
        const grant = (document.getElementById('perm-grant-select') || {}).value;

        if (!user || !perm) {
            UniselvNotify.warning('Please enter both account username and permission key.');
            return;
        }

        this.callApi('save_account_permission', { username: user.trim(), permission: perm, granted: parseInt(grant) }, (err, res) => {
            if (err || res.error) {
                UniselvNotify.error(`Failed to save account override: ${err || res.error}`);
                return;
            }
            UniselvNotify.success(`Permission override applied to ${user}.`);
            const uInput = document.getElementById('perm-user-input');
            if (uInput) uInput.value = '';
            this.loadPermissions();
        });
    },

    // ==================== OPENSWOOLE GOVERNANCE & MULTI-PHP AUTOMATION ====================

    loadOpenSwooleGovernance: function() {
        const host = document.getElementById('uniselv-openswoole-admin-body');
        if (!this.isAdmin || !host) return;
        host.textContent = 'Loading OpenSwoole multi-PHP & resource governance status...';
        this.callApi('openswoole_status', {}, (err, response) => {
            const data = response?.data || response;
            if (err || !data?.success) {
                host.textContent = `OpenSwoole governance unavailable: ${err || data?.error || 'Check agent status'}`;
                return;
            }
            const jobEl = document.getElementById('uniselv-openswoole-job');
            if (jobEl && !this.oswPolling) {
                const j = data.job;
                jobEl.textContent = j ? `Last OpenSwoole job: ${j.operation} (${j.version || 'all'}) — ${j.state}${j.error ? ': ' + j.error : ''}` : '';
            }
            host.replaceChildren();
            const settings = data.settings || {};

            const mk = (tag, attrs = {}, text = null) => {
                const el = document.createElement(tag);
                for (const [k, v] of Object.entries(attrs)) {
                    if (k === 'class') el.className = v;
                    else if (k === 'style') el.style.cssText = v;
                    else if (v !== undefined && v !== null) el.setAttribute(k, String(v));
                }
                if (text !== null) el.textContent = String(text);
                return el;
            };

            // 1. Global Automation & Resource Directives Form
            const cfgBox = mk('div', { style: 'background:var(--uniselv-bg-subtle,#f8fafc);border:1px solid var(--uniselv-border,#e2e8f0);border-radius:10px;padding:14px;margin-bottom:16px;' });
            cfgBox.append(mk('h6', { style: 'font-weight:700;margin:0 0 10px 0;' }, '1. Automation, Isolation & PHP Extension Directives'));
            const grid = mk('div', { style: 'display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:12px;align-items:end;' });

            const makeCheck = (id, label, checked) => {
                const wrap = mk('label', { style: 'display:flex;align-items:center;gap:8px;font-size:0.86rem;font-weight:600;cursor:pointer;padding:6px 0;' });
                const inp = mk('input', { type: 'checkbox', id });
                inp.checked = Boolean(checked);
                wrap.append(inp, document.createTextNode(label));
                return wrap;
            };
            const makeField = (id, label, type, value, opts = {}) => {
                const wrap = mk('div');
                wrap.append(mk('label', { for: id, style: 'display:block;font-size:0.78rem;font-weight:600;color:#475569;margin-bottom:4px;' }, label));
                if (type === 'select') {
                    const sel = mk('select', { id, class: 'uniselv-form-input', style: 'width:100%;' });
                    (opts.options || []).forEach(([val, txt]) => {
                        const o = mk('option', { value: val }, txt);
                        if (String(value) === String(val)) o.selected = true;
                        sel.append(o);
                    });
                    wrap.append(sel);
                } else {
                    const inp = mk('input', { id, type, class: 'uniselv-form-input', style: 'width:100%;', value: String(value ?? ''), ...(opts.min ? { min: opts.min } : {}), ...(opts.max ? { max: opts.max } : {}) });
                    wrap.append(inp);
                }
                return wrap;
            };

            grid.append(
                makeCheck('osw-auto-new-php', 'Auto-enable on new PHP versions', settings.openswoole_auto_install_new_php === '1'),
                makeCheck('osw-strict-cgroup', 'Strict cgroups v2 slice containment', settings.openswoole_strict_cgroup === '1'),
                makeCheck('osw-enable-coroutine', 'Enable OpenSwoole coroutines', settings.openswoole_enable_coroutine !== '0'),
                makeCheck('osw-preemptive', 'Preemptive coroutine scheduler', settings.openswoole_preemptive_scheduler === '1'),
                makeField('osw-enforce-mode', 'Resource enforcement mode', 'select', settings.openswoole_enforcement_mode || 'enforce', {
                    options: [['enforce', 'Enforce (Cap workers & block disabled)'], ['monitor', 'Monitor & alert only']]
                }),
                makeField('osw-worker-rss', 'Estimated RAM per worker (MiB)', 'number', settings.openswoole_worker_rss_mib || '128', { min: 64, max: 512 }),
                makeField('osw-global-max', 'Global max workers cap', 'number', settings.openswoole_global_max_workers || '4', { min: 1, max: 64 }),
                makeField('osw-sock-buf', 'Unix socket buffer (bytes)', 'number', settings.openswoole_unixsock_buffer_size || '8388608', { min: 1048576, max: 67108864 })
            );
            const saveBtn = mk('button', { class: 'uniselv-btn btn-primary', type: 'button' }, 'Save OpenSwoole Settings');
            saveBtn.onclick = () => this.saveOpenSwooleSettings();
            const btnWrap = mk('div');
            btnWrap.append(saveBtn);
            grid.append(btnWrap);
            cfgBox.append(grid);
            host.append(cfgBox);

            // helper table builder
            const buildTable = (title, cols, rows) => {
                const sec = mk('div', { style: 'margin-bottom:16px;' });
                sec.append(mk('h6', { style: 'font-weight:700;margin:0 0 8px 0;' }, title));
                const wrap = mk('div', { class: 'uniselv-table-wrap' });
                const tbl = mk('table', { class: 'uniselv-table' });
                const trHead = tbl.createTHead().insertRow();
                cols.forEach(c => trHead.append(mk('th', { scope: 'col' }, c)));
                const tbody = tbl.createTBody();
                if (!rows.length) {
                    const td = tbody.insertRow().insertCell();
                    td.colSpan = cols.length;
                    td.style.color = '#64748b';
                    td.textContent = 'No entries found.';
                } else {
                    rows.forEach(cells => {
                        const r = tbody.insertRow();
                        cells.forEach(c => {
                            const td = r.insertCell();
                            if (c instanceof Node) td.append(c);
                            else td.textContent = String(c ?? '');
                        });
                    });
                }
                wrap.append(tbl);
                sec.append(wrap);
                host.append(sec);
            };

            // 2. Live Verification, Diagnostics & Launch Command Console
            const accountsList = data.accounts || [];
            const phpEntries = Object.entries(data.php_versions || {});
            const testBox = mk('div', { id: 'osw-console-box', style: 'background:var(--uniselv-bg-subtle,#f8fafc);border:1px solid var(--uniselv-border,#e2e8f0);border-radius:10px;padding:14px;margin-bottom:16px;' });
            testBox.append(mk('h6', { style: 'font-weight:700;margin:0 0 8px 0;' }, '2. Verification, Readiness Diagnostics & Launch Command Console'));
            testBox.append(mk('p', { style: 'font-size:0.83rem;color:#64748b;margin:0 0 12px 0;' }, 'Verify PHP/INI startup & compiler toolchain readiness, run an isolated ephemeral OpenSwoole loopback test inside an account slice, or generate plan-aligned Octane launch commands.'));

            const ctrlRow = mk('div', { style: 'display:flex;gap:10px;flex-wrap:wrap;align-items:end;margin-bottom:12px;' });
            const accWrap = mk('div', { style: 'min-width:210px;flex:1;' });
            accWrap.append(mk('label', { for: 'osw-test-account', style: 'display:block;font-size:0.78rem;font-weight:600;color:#475569;margin-bottom:4px;' }, 'Target Account (for Self-Test & Command)'));
            const accSel = mk('select', { id: 'osw-test-account', class: 'uniselv-form-input', style: 'width:100%;' });
            const preferredAcc = this._oswSelectedAccount
                || (accountsList.find(a => a.allowed) || accountsList[0] || {}).username
                || '';
            accountsList.forEach(a => {
                const label = `${a.username} (${a.plan_name}: ${a.allowed ? `${a.max_workers}w / ${a.max_task_workers}t` : 'Blocked'})`;
                const o = mk('option', { value: a.username }, label);
                if (a.username === preferredAcc) o.selected = true;
                accSel.append(o);
            });
            if (!accountsList.length) {
                accSel.append(mk('option', { value: '' }, 'No hosted accounts found'));
            }
            accWrap.append(accSel);

            const phpWrap = mk('div', { style: 'min-width:170px;' });
            phpWrap.append(mk('label', { for: 'osw-test-php', style: 'display:block;font-size:0.78rem;font-weight:600;color:#475569;margin-bottom:4px;' }, 'PHP Branch'));
            const phpSel = mk('select', { id: 'osw-test-php', class: 'uniselv-form-input', style: 'width:100%;' });
            const loadedPhp = phpEntries.filter(([, m]) => m.loaded).map(([v]) => v);
            const preferredPhp = (this._oswSelectedPhp && (data.php_versions || {})[this._oswSelectedPhp])
                ? this._oswSelectedPhp
                : (loadedPhp[loadedPhp.length - 1] || (phpEntries[0] && phpEntries[0][0]) || 'php84');
            phpEntries.forEach(([v, m]) => {
                const o = mk('option', { value: v }, `${v} (${m.loaded ? 'Loaded' : m.status})`);
                if (v === preferredPhp) o.selected = true;
                phpSel.append(o);
            });
            if (!phpEntries.length) {
                phpSel.append(mk('option', { value: 'php84' }, 'php84'));
            }
            phpWrap.append(phpSel);

            const diagInlineBtn = mk('button', { id: 'osw-inline-diag-btn', class: 'uniselv-btn btn-outline', type: 'button' }, 'Check PHP & Build Readiness');
            diagInlineBtn.onclick = () => this.runOpenSwooleDiagnostics();
            const selfTestBtn = mk('button', { id: 'osw-selftest-btn', class: 'uniselv-btn btn-primary', type: 'button' }, 'Run Live Self-Test');
            selfTestBtn.onclick = () => this.runOpenSwooleSelfTest();

            ctrlRow.append(accWrap, phpWrap, diagInlineBtn, selfTestBtn);
            testBox.append(ctrlRow);

            const cmdCard = mk('div', { style: 'background:#0f172a;color:#e2e8f0;border-radius:8px;padding:12px;margin-bottom:12px;' });
            const cmdHeader = mk('div', { style: 'display:flex;justify-content:space-between;align-items:center;gap:8px;margin-bottom:6px;' });
            cmdHeader.append(mk('span', { style: 'font-size:0.76rem;font-weight:700;color:#94a3b8;text-transform:uppercase;' }, 'Account-Aligned Launch Command & Server->set() Snippet'));
            const copyCmdBtn = mk('button', { class: 'uniselv-btn btn-sm', type: 'button', style: 'background:#1e293b;color:#f8fafc;border:1px solid #475569;padding:4px 10px;border-radius:6px;cursor:pointer;' }, 'Copy Command');
            cmdHeader.append(copyCmdBtn);
            const cmdPre = mk('pre', { id: 'osw-cmd-preview', style: 'margin:0;white-space:pre-wrap;word-break:break-word;font-family:monospace;font-size:0.8rem;line-height:1.45;color:#f8fafc;' });
            cmdCard.append(cmdHeader, cmdPre);
            testBox.append(cmdCard);

            const updateLaunchPreview = () => {
                const chosenAcc = accountsList.find(a => a.username === accSel.value) || accountsList[0];
                const chosenPhp = phpSel.value || 'php84';
                this._oswSelectedAccount = chosenAcc ? chosenAcc.username : '';
                this._oswSelectedPhp = chosenPhp;
                if (!chosenAcc) {
                    cmdPre.textContent = 'No account selected.';
                    return;
                }
                const phpBin = `/usr/local/apps/${chosenPhp}/bin/php`;
                const w = chosenAcc.allowed ? chosenAcc.max_workers : 0;
                const tw = chosenAcc.allowed ? chosenAcc.max_task_workers : 0;
                const maxReq = chosenAcc.max_requests || 1000;
                const memMb = chosenAcc.mem_max_mib || 512;
                const slice = chosenAcc.expected_slice || `golden-${chosenAcc.uid}.slice`;
                if (!chosenAcc.allowed || w < 1) {
                    cmdPre.textContent = `# OpenSwoole is currently BLOCKED for ${chosenAcc.username} (${chosenAcc.plan_name}).\n# Enable Access via Account Override or Plan Policy above to generate an active launch command.`;
                } else {
                    cmdPre.textContent =
                        `# Slice: ${slice} | Plan: ${chosenAcc.plan_name} | Memory Cap: ${memMb} MiB\n` +
                        `${phpBin} artisan octane:start --server=openswoole --host=127.0.0.1 --port=8000 --workers=${w} --task-workers=${tw} --max-requests=${maxReq}\n` +
                        `# Raw OpenSwoole\\HTTP\\Server->set([...]):\n` +
                        `$server->set(['worker_num' => ${w}, 'task_worker_num' => ${tw}, 'max_request' => ${maxReq}]);`;
                }
            };
            accSel.onchange = updateLaunchPreview;
            phpSel.onchange = updateLaunchPreview;
            copyCmdBtn.onclick = () => {
                const txt = cmdPre.textContent || '';
                if (!txt) return;
                if (navigator.clipboard && navigator.clipboard.writeText) {
                    navigator.clipboard.writeText(txt).then(
                        () => UniselvNotify.success('Launch command copied to clipboard.'),
                        () => UniselvNotify.info('Copy selected command manually from preview box.')
                    );
                } else {
                    UniselvNotify.info('Clipboard API unavailable; copy command from preview box.');
                }
            };
            updateLaunchPreview();

            const diagOut = mk('div', { id: 'osw-diag-output', style: 'margin-bottom:10px;' });
            const selfOut = mk('div', { id: 'osw-selftest-output' });
            testBox.append(diagOut, selfOut);
            host.append(testBox);
            if (this._lastOswDiagnostics) this._renderOpenSwooleDiagnostics(this._lastOswDiagnostics);
            if (this._lastOswSelfTest) this._renderOpenSwooleSelfTest(this._lastOswSelfTest);

            // 3. Installed PHP Versions Matrix
            buildTable(
                '3. Installed Webuzo PHP Versions & OpenSwoole Extensions',
                ['PHP Branch', 'PHP Version', 'Target PECL', 'Status / Loaded', 'Real extension_dir', 'Actions'],
                phpEntries.map(([ver, m]) => {
                    const badge = mk('span', { class: `uniselv-badge ${m.status === 'active' || m.status === 'active_manual' ? 'badge-normal' : (m.status === 'disabled' ? 'badge-warning' : 'badge-critical')}` },
                        m.loaded ? `Active (${m.openswoole_version || 'loaded'})` : m.status);
                    if (m.last_error && !m.loaded) {
                        badge.title = m.last_error;
                    }
                    const actWrap = mk('div', { style: 'display:flex;gap:6px;flex-wrap:wrap;' });
                    if (m.compatible_versions && m.compatible_versions.length) {
                        if (m.status === 'active' || m.status === 'active_manual') {
                            const bDis = mk('button', { class: 'uniselv-btn btn-outline btn-sm', type: 'button' }, 'Disable');
                            bDis.onclick = () => this.triggerOpenSwoolePhpAction('disable', ver);
                            const bReb = mk('button', { class: 'uniselv-btn btn-outline btn-sm', type: 'button' }, 'Rebuild');
                            bReb.onclick = () => this.triggerOpenSwoolePhpAction('rebuild', ver);
                            actWrap.append(bDis, bReb);
                        } else {
                            const bEn = mk('button', { class: 'uniselv-btn btn-primary btn-sm', type: 'button' }, m.so_exists ? 'Enable' : 'Compile & Enable');
                            bEn.onclick = () => this.triggerOpenSwoolePhpAction(m.so_exists ? 'enable' : 'install', ver);
                            actWrap.append(bEn);
                        }
                    } else {
                        actWrap.textContent = 'Unsupported PHP';
                    }
                    return [ver, m.php_version || '-', m.recommended_release || '-', badge, m.extension_dir || '-', actWrap];
                })
            );

            // 4. Per-Plan OpenSwoole Resource Policies
            buildTable(
                '4. Plan-Level OpenSwoole Resource Budgets',
                ['Plan', 'Plan Limits (CPU / RAM / Tasks)', 'Auto Workers', 'Allow OpenSwoole', 'Overrides (Workers / Tasks)', 'Save'],
                (data.plans || []).map(pl => {
                    const allowSel = mk('select', { class: 'uniselv-form-input', style: 'min-width:105px;' });
                    [['1', 'Allowed'], ['0', 'Disabled']].forEach(([v, t]) => {
                        const o = mk('option', { value: v }, t);
                        if ((pl.allowed ? '1' : '0') === v) o.selected = true;
                        allowSel.append(o);
                    });
                    const ovInp = mk('input', { type: 'number', min: '0', max: '64', class: 'uniselv-form-input', style: 'width:68px;', value: String(pl.max_workers_override || 0), title: 'Max Workers (0 = Auto)' });
                    const taskOvInp = mk('input', { type: 'number', min: '-1', max: '64', class: 'uniselv-form-input', style: 'width:68px;', value: String(pl.max_task_workers_override ?? -1), title: 'Max Task Workers (-1 = Auto)' });
                    const ovWrap = mk('div', { style: 'display:flex;gap:6px;align-items:center;' });
                    ovWrap.append(ovInp, taskOvInp);
                    const savePl = mk('button', { class: 'uniselv-btn btn-outline btn-sm', type: 'button' }, 'Apply');
                    savePl.onclick = () => this.saveOpenSwoolePolicy('plan', pl.plan_name, allowSel.value, ovInp.value, taskOvInp.value);
                    return [
                        pl.plan_name,
                        `${pl.cpuquota}% / ${pl.mem_max_mib} MiB / ${pl.maxtask}`,
                        `${pl.auto_calculated_workers} (task: ${pl.max_task_workers})`,
                        allowSel,
                        ovWrap,
                        savePl
                    ];
                })
            );

            // 5. Per-Account Effective Limits & Active Processes
            buildTable(
                '5. Account OpenSwoole Enforcement & Live Activity',
                ['Account (Plan)', 'Assigned Slice', 'Budget (Workers / Tasks)', 'Live (Workers / RSS)', 'Account Override (Access / W / T)', 'Actions'],
                (data.accounts || []).map(acc => {
                    const allowSel = mk('select', { class: 'uniselv-form-input', style: 'min-width:115px;' });
                    [['-1', 'Inherit Plan'], ['1', 'Force Allow'], ['0', 'Block']].forEach(([v, t]) => {
                        const o = mk('option', { value: v }, t);
                        if (String(acc.override_allowed) === v) o.selected = true;
                        allowSel.append(o);
                    });
                    const ovInp = mk('input', { type: 'number', min: '0', max: '64', class: 'uniselv-form-input', style: 'width:64px;', value: String(acc.override_max_workers || 0), title: 'Workers Override (0 = Inherit/Auto)' });
                    const taskOvInp = mk('input', { type: 'number', min: '-1', max: '64', class: 'uniselv-form-input', style: 'width:64px;', value: String(acc.override_max_task_workers ?? -1), title: 'Task Workers Override (-1 = Inherit/Auto)' });
                    const ovWrap = mk('div', { style: 'display:flex;gap:6px;align-items:center;' });
                    ovWrap.append(allowSel, ovInp, taskOvInp);
                    const actWrap = mk('div', { style: 'display:flex;gap:6px;align-items:center;' });
                    const saveAcc = mk('button', { class: 'uniselv-btn btn-outline btn-sm', type: 'button' }, 'Save');
                    saveAcc.onclick = () => this.saveOpenSwoolePolicy('account', acc.username, allowSel.value, ovInp.value, taskOvInp.value);
                    const testUseBtn = mk('button', { class: 'uniselv-btn btn-outline btn-sm', type: 'button', title: 'Select this account in Test & Launch Command console' }, 'Test/Cmd');
                    testUseBtn.onclick = () => {
                        this._oswSelectedAccount = acc.username;
                        accSel.value = acc.username;
                        updateLaunchPreview();
                        testBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                    };
                    actWrap.append(saveAcc, testUseBtn);
                    const liveText = acc.active_process_count
                        ? `${acc.active_worker_count}w / ${acc.active_rss_mib} MiB` + (acc.escaped_count ? ` (${acc.escaped_count} escaped!)` : '')
                        : 'Idle';
                    return [
                        `${acc.username} (${acc.plan_name})`,
                        acc.expected_slice,
                        acc.allowed ? `${acc.max_workers}w / ${acc.max_task_workers}t (${acc.policy_source})` : `Blocked (${acc.policy_source})`,
                        liveText,
                        ovWrap,
                        actWrap
                    ];
                })
            );

            // 6. Running OpenSwoole Processes
            buildTable(
                '6. Live OpenSwoole / Octane Processes',
                ['PID', 'Account', 'PHP', 'Role', 'RSS', 'Cgroup Containment', 'Command', 'Action'],
                (data.live_processes || []).map(p => {
                    const cgBadge = mk('span', { class: `uniselv-badge ${p.contained ? 'badge-normal' : 'badge-critical'}` }, p.contained ? 'Contained' : 'Outside Slice!');
                    const stopBtn = mk('button', { class: 'uniselv-btn btn-danger btn-sm', type: 'button' }, 'Stop');
                    stopBtn.onclick = () => this.stopOpenSwoolePid(p.uid, p.pid);
                    return [
                        String(p.pid),
                        p.username,
                        p.php_version || '-',
                        p.role,
                        `${Math.round((p.rss_bytes || 0) / (1024 * 1024))} MiB`,
                        cgBadge,
                        p.cmdline || p.comm,
                        stopBtn
                    ];
                })
            );

            // 7. Recent OpenSwoole Audit & Enforcement Events
            const fmtTs = (ts) => {
                const n = Number(ts);
                return Number.isFinite(n) && n > 1000000000 ? new Date(n * 1000).toLocaleString() : String(ts || '-');
            };
            const fmtDetails = (det) => {
                if (!det) return '-';
                if (typeof det === 'string') return det;
                if (typeof det === 'object') {
                    const parts = Object.entries(det).map(([k, v]) => `${k}: ${typeof v === 'object' && v !== null ? JSON.stringify(v) : v}`);
                    return parts.length ? parts.join(' · ') : '-';
                }
                return String(det);
            };
            buildTable(
                '7. Recent OpenSwoole Audit & Enforcement Events',
                ['Time', 'Event', 'Account', 'Details'],
                (data.audit_logs || []).map(ev => [
                    fmtTs(ev.timestamp),
                    ev.action || '-',
                    ev.target_account || ev.username || '-',
                    fmtDetails(ev.details)
                ])
            );
        }, { timeoutMs: 20000 });
    },

    saveOpenSwooleSettings: function() {
        const payload = {
            openswoole_auto_install_new_php: document.getElementById('osw-auto-new-php')?.checked ? '1' : '0',
            openswoole_strict_cgroup: document.getElementById('osw-strict-cgroup')?.checked ? '1' : '0',
            openswoole_enable_coroutine: document.getElementById('osw-enable-coroutine')?.checked ? '1' : '0',
            openswoole_preemptive_scheduler: document.getElementById('osw-preemptive')?.checked ? '1' : '0',
            openswoole_enforcement_mode: document.getElementById('osw-enforce-mode')?.value || 'enforce',
            openswoole_worker_rss_mib: document.getElementById('osw-worker-rss')?.value || '128',
            openswoole_global_max_workers: document.getElementById('osw-global-max')?.value || '4',
            openswoole_unixsock_buffer_size: document.getElementById('osw-sock-buf')?.value || '8388608'
        };
        this.callApi('openswoole_save_settings', payload, (err, res) => {
            const d = res?.data || res;
            if (err || !d?.success) {
                UniselvNotify.error(`Failed saving OpenSwoole settings: ${err || d?.error || 'Unknown error'}`);
                return;
            }
            const synced = (d.ini_sync?.updated || []).join(', ');
            UniselvNotify.success(synced ? `OpenSwoole settings saved & synced to: ${synced}` : 'OpenSwoole settings saved.');
            this.loadOpenSwooleGovernance();
        }, { timeoutMs: 25000 });
    },

    triggerOpenSwoolePhpAction: function(operation, version = '') {
        if (this.oswPolling) {
            UniselvNotify.warning('An OpenSwoole build/provisioning job is already in progress.');
            return;
        }
        this.callApi('openswoole_php_action', { operation, version }, (err, res) => {
            const d = res?.data || res;
            if (err || !d?.success) {
                UniselvNotify.error(d?.error || err || 'Failed triggering OpenSwoole operation');
                return;
            }
            if (!d.queued) {
                UniselvNotify.success(`OpenSwoole ${operation} applied to ${version}.`);
                this.loadOpenSwooleGovernance();
                return;
            }
            this.oswPolling = true;
            const jobEl = document.getElementById('uniselv-openswoole-job');
            if (jobEl) jobEl.textContent = `Running: ${operation} (${version || 'all PHP versions'})... compiling in isolated build slice.`;
            let attempts = 160;
            const poll = () => {
                this.callApi('openswoole_status', {}, (pErr, pRes) => {
                    const st = pRes?.data || pRes;
                    const job = st?.job;
                    if (!pErr && job && job.id === d.jobId && job.state !== 'running') {
                        this.oswPolling = false;
                        if (job.state === 'completed') {
                            UniselvNotify.success(`OpenSwoole ${operation} (${version || 'all'}) completed.`);
                        } else {
                            UniselvNotify.error(job.error || `OpenSwoole ${operation} failed.`);
                        }
                        this.loadOpenSwooleGovernance();
                        return;
                    }
                    if (--attempts > 0) {
                        setTimeout(poll, 3000);
                    } else {
                        this.oswPolling = false;
                        if (jobEl) jobEl.textContent = 'OpenSwoole job is still compiling in background; click Refresh shortly.';
                    }
                }, { timeoutMs: 15000 });
            };
            setTimeout(poll, 2000);
        }, { timeoutMs: 20000 });
    },

    saveOpenSwoolePolicy: function(scope, target, allowed, maxWorkersOverride, maxTaskWorkersOverride) {
        this.callApi('openswoole_save_policy', {
            scope,
            target,
            allowed,
            max_workers_override: maxWorkersOverride || '0',
            max_task_workers_override: maxTaskWorkersOverride ?? '-1'
        }, (err, res) => {
            const d = res?.data || res;
            if (err || !d?.success) {
                UniselvNotify.error(`Failed saving OpenSwoole policy: ${err || d?.error}`);
                return;
            }
            UniselvNotify.success(`Updated OpenSwoole ${scope} policy for ${target}.`);
            this.loadOpenSwooleGovernance();
        });
    },

    runOpenSwooleDiagnostics: function() {
        const out = document.getElementById('osw-diag-output');
        if (out) {
            out.textContent = 'Running multi-PHP OpenSwoole readiness & compiler toolchain check...';
        }
        this.callApi('openswoole_diagnostics', {}, (err, res) => {
            const d = res?.data || res;
            if (err || !d?.success) {
                const msg = err || d?.error || 'Diagnostics failed';
                if (out) out.textContent = `Diagnostics error: ${msg}`;
                UniselvNotify.error(msg);
                return;
            }
            this._lastOswDiagnostics = d;
            this._renderOpenSwooleDiagnostics(d);
            if (d.all_passed) {
                UniselvNotify.success('All PHP branches, INI directives, and build toolchain checks passed.');
            } else {
                UniselvNotify.warning('Some PHP branches or readiness checks require attention.');
            }
        }, { timeoutMs: 25000 });
    },

    _renderOpenSwooleDiagnostics: function(d) {
        const out = document.getElementById('osw-diag-output');
        if (!out || !d) return;
        out.replaceChildren();
        const mk = (tag, attrs = {}, text = null) => {
            const el = document.createElement(tag);
            for (const [k, v] of Object.entries(attrs)) {
                if (k === 'class') el.className = v;
                else if (k === 'style') el.style.cssText = v;
                else if (v !== undefined && v !== null) el.setAttribute(k, String(v));
            }
            if (text !== null) el.textContent = String(text);
            return el;
        };

        const box = mk('div', { style: `border:1px solid ${d.all_passed ? '#86efac' : '#fcd34d'};background:${d.all_passed ? '#f0fdf4' : '#fffbeb'};border-radius:8px;padding:12px;` });
        const head = mk('div', { style: 'display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;margin-bottom:8px;' });
        const checkedN = Number(d.checked_at);
        const checkedLabel = Number.isFinite(checkedN) && checkedN > 1000000000 ? new Date(checkedN * 1000).toLocaleString() : (d.checked_at || '');
        head.append(
            mk('strong', { style: 'color:#0f172a;font-size:0.9rem;' }, `PHP & Build Readiness Check${checkedLabel ? ` (${checkedLabel})` : ''}`),
            mk('span', { class: `uniselv-badge ${d.all_passed ? 'badge-normal' : 'badge-warning'}` }, d.all_passed ? 'ALL CHECKS PASSED' : 'ATTENTION NEEDED')
        );
        box.append(head);

        const tools = d.toolchain || {};
        const toolLine = mk('div', { style: 'display:flex;gap:6px;flex-wrap:wrap;margin-bottom:10px;font-size:0.78rem;' });
        toolLine.append(mk('span', { style: 'font-weight:600;color:#475569;align-self:center;' }, 'Toolchain & Policy:'));
        Object.entries(tools).forEach(([name, ok]) => {
            toolLine.append(mk('span', { class: `uniselv-badge ${ok ? 'badge-normal' : 'badge-critical'}` }, `${name}: ${ok ? 'OK' : 'Missing'}`));
        });
        toolLine.append(mk('span', { class: `uniselv-badge ${d.policy_manifest_ok ? 'badge-normal' : 'badge-critical'}`, title: d.policy_manifest_path || '' }, `Policy JSON: ${d.policy_manifest_ok ? 'OK' : 'Missing'}`));

        const missingTools = Object.entries(tools).filter(([_, ok]) => !ok);
        if (missingTools.length > 0 && this.isAdmin) {
            const instBtn = mk('button', { class: 'uniselv-btn btn-primary btn-sm', style: 'padding:2px 8px;font-size:0.75rem;margin-left:auto;' }, '🛠️ Install Missing Build Dependencies Now');
            instBtn.onclick = () => {
                UniselvModal.confirm({
                    title: 'Install Missing OS Build Dependencies?',
                    message: `The server is missing build tools (<strong>${missingTools.map(([n]) => n).join(', ')}</strong>). This will run an automated package manager update and install required compilers and header packages.`,
                    icon: 'warning',
                    confirmText: 'Install Dependencies',
                    onConfirm: () => {
                        UniselvNotify.info('Starting background installation of build dependencies...');
                        this.callApi('install_build_dependencies', { target: 'toolchain' }, (iErr, iRes) => {
                            const id = iRes?.data || iRes;
                            if (iErr || !id?.success) {
                                UniselvNotify.error(iErr || id?.error || 'Failed to start build dependency installation');
                            } else {
                                UniselvNotify.success(id.message || 'Build dependency installation started in background.');
                                if (this.isAdmin) setTimeout(() => this.runOpenSwooleDiagnostics(), 4000);
                            }
                        });
                    }
                });
            };
            toolLine.append(instBtn);
        }
        box.append(toolLine);

        const wrap = mk('div', { class: 'uniselv-table-wrap' });
        const tbl = mk('table', { class: 'uniselv-table' });
        const thRow = tbl.createTHead().insertRow();
        ['Branch', 'PHP / Ext', '.so Present', 'openswoole.ini', 'CLI Startup', 'FPM Guard', 'Result'].forEach(c => thRow.append(mk('th', { scope: 'col' }, c)));
        const tbody = tbl.createTBody();
        (d.php_checks || []).forEach(c => {
            const tr = tbody.insertRow();
            [
                c.version,
                `${c.php_version || '-'} (${c.openswoole_version || c.status})`,
                c.so_exists ? 'Yes' : 'No',
                c.ini_exists ? (c.ini_synced ? 'Synced' : 'Out-of-sync') : 'Missing',
                c.startup_ok ? 'OK' : (c.error || 'Fail'),
                c.fpm_isolated_active ? 'Yes' : 'No',
                mk('span', { class: `uniselv-badge ${c.passed ? 'badge-normal' : (c.status === 'unsupported' ? 'badge-warning' : 'badge-critical')}` }, c.passed ? 'PASS' : c.status)
            ].forEach(val => {
                const td = tr.insertCell();
                if (val instanceof Node) td.append(val);
                else td.textContent = String(val ?? '-');
            });
        });
        wrap.append(tbl);
        box.append(wrap);
        out.append(box);
    },

    runOpenSwooleSelfTest: function() {
        const username = document.getElementById('osw-test-account')?.value || this._oswSelectedAccount || '';
        const phpVersion = document.getElementById('osw-test-php')?.value || this._oswSelectedPhp || 'php84';
        if (!username) {
            UniselvNotify.warning('Select a target hosted account before running the live self-test.');
            return;
        }
        const btn = document.getElementById('osw-selftest-btn');
        const out = document.getElementById('osw-selftest-output');
        if (btn) btn.disabled = true;
        if (out) {
            out.textContent = `Running live OpenSwoole cgroup v2 & worker-cap self-test for ${username} (${phpVersion})...`;
        }
        this.callApi('openswoole_selftest', { username, php_version: phpVersion }, (err, res) => {
            if (btn) btn.disabled = false;
            const d = res?.data || res;
            if (err || !d?.success) {
                const msg = err || d?.error || 'Live self-test failed';
                if (out) out.textContent = `Live self-test error: ${msg}`;
                UniselvNotify.error(msg);
                return;
            }
            this._lastOswSelfTest = d;
            if (d.all_passed) {
                UniselvNotify.success(`OpenSwoole live self-test PASSED for ${d.username} (${d.elapsed_ms || 0} ms).`);
            } else {
                UniselvNotify.error(`OpenSwoole live self-test detected failures for ${d.username}.`);
            }
            this.loadOpenSwooleGovernance();
        }, { timeoutMs: 40000 });
    },

    _renderOpenSwooleSelfTest: function(d) {
        const out = document.getElementById('osw-selftest-output');
        if (!out || !d) return;
        out.replaceChildren();
        const mk = (tag, attrs = {}, text = null) => {
            const el = document.createElement(tag);
            for (const [k, v] of Object.entries(attrs)) {
                if (k === 'class') el.className = v;
                else if (k === 'style') el.style.cssText = v;
                else if (v !== undefined && v !== null) el.setAttribute(k, String(v));
            }
            if (text !== null) el.textContent = String(text);
            return el;
        };

        const box = mk('div', { style: `border:1px solid ${d.all_passed ? '#86efac' : '#fca5a5'};background:${d.all_passed ? '#f0fdf4' : '#fef2f2'};border-radius:8px;padding:12px;` });
        const head = mk('div', { style: 'display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;margin-bottom:8px;' });
        head.append(
            mk('strong', { style: 'color:#0f172a;font-size:0.9rem;' }, `Live E2E Self-Test: ${d.username} (UID ${d.uid}, ${d.plan_name}, ${d.php_version}) · ${d.elapsed_ms || 0} ms`),
            mk('span', { class: `uniselv-badge ${d.all_passed ? 'badge-normal' : 'badge-critical'}` }, d.all_passed ? 'PASSED' : 'FAILED')
        );
        box.append(head);

        const list = mk('div', { style: 'display:flex;flex-direction:column;gap:6px;' });
        (d.steps || []).forEach(st => {
            const row = mk('div', { style: 'display:flex;gap:8px;align-items:flex-start;font-size:0.83rem;background:#ffffff;border:1px solid #e2e8f0;border-radius:6px;padding:8px 10px;' });
            row.append(
                mk('span', { class: `uniselv-badge ${st.passed ? 'badge-normal' : 'badge-critical'}`, style: 'flex-shrink:0;' }, st.passed ? 'PASS' : 'FAIL'),
                mk('div', {}, `${st.label}: ${st.detail || ''}`)
            );
            list.append(row);
        });
        box.append(list);
        out.append(box);
    },

    enforceOpenSwooleNow: function() {
        this.callApi('openswoole_enforce', { mode: 'reconcile' }, (err, res) => {
            const d = res?.data || res;
            if (err || !d?.success) {
                UniselvNotify.error(`Enforcement pass failed: ${err || d?.error}`);
                return;
            }
            UniselvNotify.success(`Checked ${d.scanned || 0} OpenSwoole processes (${d.contained_moves || 0} contained, ${(d.terminated_pids || []).length} stopped).`);
            this.loadOpenSwooleGovernance();
        });
    },

    stopOpenSwoolePid: function(uid, pid) {
        this.callApi('openswoole_enforce', { mode: 'stop_pid', uid, pid }, (err, res) => {
            const d = res?.data || res;
            if (err || !d?.success) {
                UniselvNotify.error(d?.error || d?.message || 'Failed stopping PID');
                return;
            }
            UniselvNotify.success(`Stopped OpenSwoole PID ${pid}.`);
            this.loadOpenSwooleGovernance();
        });
    },

    loadEnduserOpenSwoole: function() {
        const host = document.getElementById('uniselv-enduser-openswoole-body');
        if (!host) return;
        host.textContent = 'Loading your OpenSwoole resource limits...';
        this.callApi('openswoole_status', {}, (err, res) => {
            const d = res?.data || res;
            if (err || !d?.success) {
                host.textContent = 'OpenSwoole budget information unavailable.';
                return;
            }
            const pol = d.policy || {};
            const g = d.guidance || {};
            host.replaceChildren();

            const summary = document.createElement('div');
            summary.style.cssText = 'display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px;margin-bottom:12px;';
            const card = (lbl, val) => {
                const box = document.createElement('div');
                box.style.cssText = 'background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:10px 12px;';
                const l = document.createElement('div');
                l.style.cssText = 'font-size:0.75rem;color:#64748b;text-transform:uppercase;font-weight:600;';
                l.textContent = lbl;
                const v = document.createElement('div');
                v.style.cssText = 'font-size:1rem;font-weight:700;color:#1e293b;margin-top:2px;';
                v.textContent = val;
                box.append(l, v);
                return box;
            };
            summary.append(
                card('OpenSwoole Access', pol.allowed ? 'Enabled' : 'Disabled on Plan'),
                card('Max Workers', pol.allowed ? `${pol.max_workers} Workers` : '0'),
                card('Max Task Workers', pol.allowed ? `${pol.max_task_workers} Tasks` : '0'),
                card('Account Slice', pol.expected_slice || '-'),
                card('Active PHP Builds', (g.active_php_versions || []).join(', ') || 'None')
            );
            host.append(summary);

            if (pol.allowed && g.recommended_octane_command) {
                const cmdRow = this._mkCodeCopyBox(g.recommended_octane_command, 'Copy Octane Command');
                if (g.assigned_octane_port) {
                    const pBadge = document.createElement('div');
                    pBadge.style.cssText = 'font-size:0.78rem;color:#475569;margin-bottom:6px;';
                    pBadge.textContent = `Assigned Dedicated Octane Port: ${g.assigned_octane_port}`;
                    host.append(pBadge);
                }
                host.append(cmdRow);
            }

            const procs = d.live_processes || [];
            const note = document.createElement('div');
            note.style.cssText = 'font-size:0.84rem;color:#475569;';
            note.textContent = procs.length
                ? `Currently running ${procs.length} OpenSwoole processes inside ${pol.expected_slice}.`
                : 'No active OpenSwoole server processes running for this account.';
            host.append(note);
        }, { timeoutMs: 15000 });
    },

    // ==================== PLATFORM OPS & MANAGED LARAVEL SERVICES (ADMIN) ====================

    _mkCodeCopyBox: function(codeText, copyLabel = 'Copy') {
        const wrap = this._mkEl('div', { style: 'position:relative;margin-bottom:10px;' });
        const pre = this._mkEl('pre', { style: 'background:#0f172a;color:#e2e8f0;padding:10px 84px 10px 12px;border-radius:8px;font-size:0.78rem;overflow-x:auto;margin:0;white-space:pre-wrap;word-break:break-word;' }, String(codeText || ''));
        const btn = this._mkEl('button', {
            class: 'uniselv-btn btn-outline btn-sm',
            type: 'button',
            style: 'position:absolute;top:8px;right:8px;background:#1e293b;color:#f8fafc;border-color:#475569;font-size:0.74rem;padding:4px 9px;'
        }, copyLabel);
        btn.onclick = () => this.copyToClipboard(String(codeText || ''), btn);
        wrap.append(pre, btn);
        return wrap;
    },

    _mkEl: function(tag, attrs = {}, ...children) {
        const el = document.createElement(tag);
        for (const [k, v] of Object.entries(attrs || {})) {
            if (k === 'class') el.className = v;
            else if (k === 'style') el.style.cssText = v;
            else if (v !== undefined && v !== null) el.setAttribute(k, String(v));
        }
        children.forEach(c => {
            if (c === null || c === undefined) return;
            if (c instanceof Node) el.appendChild(c);
            else el.appendChild(document.createTextNode(String(c)));
        });
        return el;
    },

    loadPlatformAdmin: function() {
        const host = document.getElementById('uniselv-platform-admin-body');
        if (!this.isAdmin || !host) return;
        host.textContent = 'Loading platform preflight, Laravel services, Redis isolation, ports & logs...';
        const selectedUser = this._pltSelectedUser || '';
        this.callApi('platform_status', selectedUser ? { username: selectedUser } : {}, (err, res) => {
            const d = res?.data || res;
            if (err || !d?.success) {
                host.textContent = `Platform console unavailable: ${err || d?.error || 'Check agent status'}`;
                return;
            }
            const mk = this._mkEl.bind(this);
            const pre = d.preflight || {};
            const settings = d.settings || {};
            const lrv = d.laravel || {};
            const redis = d.redis || {};
            const ports = d.port_allocations || [];
            const runtimes = d.runtimes || [];
            const logsData = d.logs || this._pltLogResult || {};
            const accounts = lrv.accounts || [];
            const curUser = this._pltSelectedUser || '';

            const jobEl = document.getElementById('uniselv-platform-job');
            if (jobEl && pre.job) {
                const j = pre.job;
                jobEl.textContent = `Last dependency job (${j.target || 'toolchain'}): ${j.state || ''}${j.error ? ' — ' + j.error : ''}`;
                if (j.state === 'running' && !this._pltPolling) {
                    this._startDepPolling();
                }
            }

            host.replaceChildren();

            // 1. OS Preflight & Build Toolchain
            const preBox = mk('div', { style: 'background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:14px;margin-bottom:16px;' });
            const preHead = mk('div', { style: 'display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;margin-bottom:10px;' });
            preHead.append(
                mk('h6', { style: 'font-weight:700;margin:0;' }, `1. OS Build Preflight, Native Headers & Composer (${(pre.distro?.pretty_name || pre.distro?.id || 'Linux')})`),
                mk('span', { class: `uniselv-badge ${pre.ready_for_openswoole_build ? 'badge-normal' : 'badge-warning'}` }, pre.ready_for_openswoole_build ? 'BUILD READY' : 'MISSING BUILD PACKAGES')
            );
            preBox.append(preHead);

            const chipWrap = mk('div', { style: 'display:flex;flex-wrap:wrap;gap:6px;margin-bottom:10px;' });
            Object.entries(pre.binaries || {}).forEach(([name, ok]) => {
                chipWrap.append(mk('span', { class: `uniselv-badge ${ok ? 'badge-normal' : 'badge-outline'}`, style: 'font-size:0.75rem;' }, `${name}: ${ok ? 'OK' : 'Missing'}`));
            });
            Object.entries(pre.headers || {}).forEach(([name, ok]) => {
                chipWrap.append(mk('span', { class: `uniselv-badge ${ok ? 'badge-normal' : 'badge-critical'}`, style: 'font-size:0.75rem;' }, `${name}: ${ok ? 'OK' : 'Missing'}`));
            });
            preBox.append(chipWrap);

            const depActions = mk('div', { style: 'display:flex;gap:8px;flex-wrap:wrap;align-items:center;' });
            const b1 = mk('button', { class: 'uniselv-btn btn-outline btn-sm', type: 'button' }, 'One-Click Install OS Build Deps');
            b1.onclick = () => this.installPlatformDeps('toolchain');
            const b2 = mk('button', { class: 'uniselv-btn btn-outline btn-sm', type: 'button' }, pre.binaries?.composer ? 'Reinstall/Verify Composer' : 'Install Verified Composer');
            b2.onclick = () => this.installPlatformDeps('composer');
            const b3 = mk('button', { class: 'uniselv-btn btn-primary btn-sm', type: 'button' }, 'Install Full Toolchain + Composer');
            b3.onclick = () => this.installPlatformDeps('all');
            depActions.append(b1, b2, b3, mk('span', { style: 'font-size:0.78rem;color:#64748b;' }, pre.composer_path ? `Composer: ${pre.composer_path}` : 'Composer not installed globally'));
            preBox.append(depActions);
            host.append(preBox);

            // 2. Laravel Stack & Supervisor — Install, Activate/Deactivate & User Permissions
            const sup = d.supervisor || pre.supervisor || {};
            const stack = d.stack_readiness || {};
            const lrvBox = mk('div', { style: 'background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:14px;margin-bottom:16px;' });
            const lrvHead = mk('div', { style: 'display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;margin-bottom:10px;' });
            const lrvEnabled = settings.platform_laravel_services_enabled !== '0';
            const supGlobalEn = settings.platform_supervisor_enabled !== '0';
            const allowedList = String(settings.platform_laravel_allowed_types || 'queue,horizon,reverb,scheduler').split(',').map(x => x.trim()).filter(Boolean);
            lrvHead.append(
                mk('h6', { style: 'font-weight:700;margin:0;' }, '2. Laravel Stack & Supervisor — Install, Activate/Deactivate & User Permissions'),
                mk('span', { class: `uniselv-badge ${lrvEnabled ? 'badge-normal' : 'badge-warning'}` }, lrvEnabled ? 'SERVER CAPABILITIES ACTIVE' : 'GLOBALLY PAUSED BY ADMIN')
            );
            lrvBox.append(lrvHead);
            lrvBox.append(mk('p', { style: 'margin:0 0 10px 0;font-size:0.82rem;color:#475569;' },
                'Admin installs missing server packages, activates or deactivates capabilities globally, and grants per-user permissions. Users configure Queue, Horizon, Reverb, and Scheduler strictly from their own project settings — zero .env editing here.'
            ));

            // 2A. Server Capabilities Matrix (Supervisor, Queue, Horizon, Reverb, Scheduler)
            const capWrap = mk('div', { class: 'uniselv-table-wrap', style: 'background:#ffffff;border:1px solid #e2e8f0;border-radius:8px;margin-bottom:10px;' });
            const capTbl = mk('table', { class: 'uniselv-table' });
            const capHr = capTbl.createTHead().insertRow();
            ['Server Capability', 'Server Installation & Prerequisites', 'Status', 'Admin Controls'].forEach(c => capHr.append(mk('th', {}, c)));
            const capTb = capTbl.createTBody();
            const capRows = [
                { key: 'supervisor', info: stack.supervisor || {}, installed: Boolean(sup.installed), active: Boolean(sup.runtime_active) && supGlobalEn, summary: (stack.supervisor?.summary) || (sup.installed ? `${sup.unit_name || 'supervisor.service'}` : 'Supervisor binaries not installed'), installTarget: sup.installed ? '' : 'supervisor' },
                { key: 'queue', info: stack.queue || {}, installed: stack.queue ? Boolean(stack.queue.installed) : true, active: lrvEnabled && allowedList.includes('queue'), summary: stack.queue?.summary || 'PHP CLI + Supervisor/systemd worker ready', installTarget: stack.queue?.install_target || '' },
                { key: 'horizon', info: stack.horizon || {}, installed: stack.horizon ? Boolean(stack.horizon.installed) : Boolean(pre.binaries?.['redis-cli']), active: lrvEnabled && allowedList.includes('horizon'), summary: stack.horizon?.summary || 'Redis + PHP pcntl/posix/redis', installTarget: stack.horizon?.install_target || '' },
                { key: 'reverb', info: stack.reverb || {}, installed: stack.reverb ? Boolean(stack.reverb.installed) : true, active: lrvEnabled && allowedList.includes('reverb'), summary: stack.reverb?.summary || 'Dedicated WS port pool (20000-59990) + PHP sockets/pcntl', installTarget: stack.reverb?.install_target || '' },
                { key: 'scheduler', info: stack.scheduler || {}, installed: stack.scheduler ? Boolean(stack.scheduler.installed) : true, active: lrvEnabled && allowedList.includes('scheduler'), summary: stack.scheduler?.summary || 'Cron daemon + PHP CLI', installTarget: stack.scheduler?.install_target || '' },
            ];
            capRows.forEach(row => {
                const tr = capTb.insertRow();
                const labels = { supervisor: 'Supervisor Daemon', queue: 'Laravel Queue Workers', horizon: 'Laravel Horizon', reverb: 'Laravel Reverb / WebSocket', scheduler: 'Laravel Scheduler' };
                const instBadge = mk('span', { class: `uniselv-badge ${row.installed ? 'badge-normal' : 'badge-warning'}`, style: 'margin-right:6px;' }, row.installed ? 'Installed / Ready' : 'Missing Package');
                const instCell = mk('div', { style: 'display:flex;align-items:center;gap:6px;flex-wrap:wrap;' });
                instCell.append(instBadge, mk('span', { style: 'font-size:0.78rem;color:#475569;' }, row.summary));
                const stBadge = mk('span', { class: `uniselv-badge ${row.active ? 'badge-normal' : 'badge-critical'}` }, row.active ? 'ACTIVE' : 'DEACTIVATED');
                const actTd = mk('div', { style: 'display:flex;gap:6px;flex-wrap:wrap;' });
                if (row.key === 'supervisor') {
                    if (!sup.installed) {
                        const sbInst = mk('button', { class: 'uniselv-btn btn-primary btn-sm', type: 'button', id: 'plt-sup-install-btn' }, 'Install Supervisor');
                        sbInst.onclick = () => this.runSupervisorAction('install');
                        actTd.append(sbInst);
                    } else {
                        const sbToggle = mk('button', { class: `uniselv-btn btn-sm ${sup.runtime_active ? 'btn-danger' : 'btn-primary'}`, type: 'button', id: sup.runtime_active ? 'plt-sup-stop-btn' : 'plt-sup-start-btn' }, sup.runtime_active ? 'Deactivate' : 'Activate');
                        sbToggle.onclick = () => this.runSupervisorAction(sup.runtime_active ? 'disable' : 'enable');
                        const sbRest = mk('button', { class: 'uniselv-btn btn-outline btn-sm', type: 'button', id: 'plt-sup-start-btn-restart' }, 'Restart');
                        sbRest.onclick = () => this.runSupervisorAction('restart');
                        const sbTest = mk('button', { class: 'uniselv-btn btn-outline btn-sm', type: 'button', id: 'plt-sup-test-btn' }, 'Test');
                        sbTest.onclick = () => this.runSupervisorAction('test');
                        actTd.append(sbToggle, sbRest, sbTest);
                    }
                } else {
                    if (row.installTarget) {
                        const ib = mk('button', { class: 'uniselv-btn btn-primary btn-sm', type: 'button' }, `Install ${row.installTarget.toUpperCase()}`);
                        ib.onclick = () => this.installPlatformDeps(row.installTarget);
                        actTd.append(ib);
                    }
                    const tb = mk('button', { class: `uniselv-btn btn-sm ${row.active ? 'btn-danger' : 'btn-primary'}`, type: 'button', id: `plt-cap-toggle-${row.key}` }, row.active ? 'Deactivate' : 'Activate');
                    tb.onclick = () => this.toggleGlobalCapability(row.key, !row.active, allowedList, settings);
                    actTd.append(tb);
                }
                [mk('strong', {}, labels[row.key]), instCell, stBadge, actTd].forEach(v => {
                    const td = tr.insertCell();
                    if (v instanceof Node) td.append(v);
                    else td.textContent = String(v ?? '-');
                });
            });
            capWrap.append(capTbl);
            lrvBox.append(capWrap);
            const supOut = mk('div', { id: 'plt-sup-output', style: 'margin-bottom:10px;' });
            lrvBox.append(supOut);
            if (this._pltSupResult) this._renderPlatformStepBox(supOut, this._pltSupResult, 'Supervisor Verification');

            const mkCheck = (id, label, checked) => {
                const w = mk('label', { style: 'display:flex;align-items:center;gap:7px;font-size:0.83rem;font-weight:600;cursor:pointer;' });
                const i = mk('input', { type: 'checkbox', id });
                i.checked = Boolean(checked);
                w.append(i, document.createTextNode(label));
                return w;
            };
            const mkInput = (id, label, type, val, opts = {}) => {
                const w = mk('div');
                w.append(mk('label', { for: id, style: 'display:block;font-size:0.76rem;font-weight:600;color:#475569;margin-bottom:4px;' }, label));
                if (type === 'select') {
                    const s = mk('select', { id, class: 'uniselv-form-input', style: 'width:100%;' });
                    (opts.options || []).forEach(([v, t]) => {
                        const o = mk('option', { value: v }, t);
                        if (String(v) === String(val)) o.selected = true;
                        s.append(o);
                    });
                    w.append(s);
                } else {
                    w.append(mk('input', { id, type, class: 'uniselv-form-input', style: 'width:100%;', value: String(val ?? ''), ...(opts.min ? { min: opts.min } : {}), ...(opts.max ? { max: opts.max } : {}) }));
                }
                return w;
            };

            const lrvPolicyRow = mk('div', { style: 'display:flex;gap:14px;flex-wrap:wrap;align-items:center;padding:10px 12px;background:#ffffff;border:1px solid #e2e8f0;border-radius:8px;margin-bottom:10px;' });
            lrvPolicyRow.append(
                mkCheck('plt-lrv-global-en', 'Enable User Laravel Access', lrvEnabled),
                mkCheck('plt-lrv-allow-queue', 'Queue', allowedList.includes('queue')),
                mkCheck('plt-lrv-allow-horizon', 'Horizon (>=512 MiB)', allowedList.includes('horizon')),
                mkCheck('plt-lrv-allow-reverb', 'Reverb WS (>=512 MiB)', allowedList.includes('reverb')),
                mkCheck('plt-lrv-allow-scheduler', 'Scheduler', allowedList.includes('scheduler')),
                mkCheck('plt-sup-global-en', 'Allow Scoped Supervisor Mode', supGlobalEn)
            );
            const saveLrvPolicyBtn = mk('button', { class: 'uniselv-btn btn-primary btn-sm', type: 'button', style: 'margin-left:auto;' }, 'Save Global Policy');
            saveLrvPolicyBtn.onclick = () => this.savePlatformSettings();
            lrvPolicyRow.append(saveLrvPolicyBtn);
            lrvBox.append(lrvPolicyRow);

            // Per-User Permission Matrix (Admin decides which users get Queue / Horizon / Reverb / Scheduler / Supervisor)
            const allUserPerms = d.user_permissions || {};
            const permAcct = curUser || accounts[0] || '';
            if (accounts.length) {
                const pCard = mk('div', { style: 'background:#ffffff;border:1px solid #e2e8f0;border-radius:8px;padding:10px 12px;margin-bottom:10px;' });
                const pTop = mk('div', { style: 'display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin-bottom:8px;' });
                pTop.append(mk('span', { style: 'font-size:0.82rem;font-weight:700;color:#1e293b;' }, 'Per-User Feature Permissions:'));
                const pAcctSel = mk('select', { id: 'plt-perm-acct', class: 'uniselv-form-input', style: 'min-width:170px;' });
                accounts.forEach(u => {
                    const o = mk('option', { value: u }, u);
                    if (u === permAcct) o.selected = true;
                    pAcctSel.append(o);
                });
                const pChecks = mk('div', { style: 'display:flex;gap:14px;flex-wrap:wrap;align-items:center;' });
                const renderUserPermChecks = (uname) => {
                    pChecks.replaceChildren();
                    const up = allUserPerms[uname] || {};
                    pChecks.append(
                        mkCheck('plt-up-queue', 'Queue Workers', up.platform_laravel_queue !== false),
                        mkCheck('plt-up-horizon', 'Horizon', up.platform_laravel_horizon !== false),
                        mkCheck('plt-up-reverb', 'Reverb WS', up.platform_laravel_reverb !== false),
                        mkCheck('plt-up-scheduler', 'Scheduler', up.platform_laravel_scheduler !== false),
                        mkCheck('plt-up-supervisor', 'Supervisor Access (No Terminal Needed)', Boolean(up.platform_supervisor))
                    );
                };
                renderUserPermChecks(permAcct);
                pAcctSel.onchange = () => renderUserPermChecks(pAcctSel.value);

                const pSave = mk('button', { class: 'uniselv-btn btn-primary btn-sm', type: 'button', id: 'plt-up-save-btn' }, 'Save User Permissions');
                pSave.onclick = () => this.saveUserPlatformPermissions(pAcctSel.value);
                const pAllowAll = mk('button', { class: 'uniselv-btn btn-outline btn-sm', type: 'button' }, 'Enable All');
                pAllowAll.onclick = () => this.saveUserPlatformPermissions(pAcctSel.value, { platform_laravel_queue: 1, platform_laravel_horizon: 1, platform_laravel_reverb: 1, platform_laravel_scheduler: 1, platform_supervisor: 1 });
                const pRevokeAll = mk('button', { class: 'uniselv-btn btn-danger btn-sm', type: 'button' }, 'Disable All');
                pRevokeAll.onclick = () => this.saveUserPlatformPermissions(pAcctSel.value, { platform_laravel_queue: 0, platform_laravel_horizon: 0, platform_laravel_reverb: 0, platform_laravel_scheduler: 0, platform_supervisor: 0 });
                pTop.append(pAcctSel, pSave, pAllowAll, pRevokeAll);
                pCard.append(pTop, pChecks);
                lrvBox.append(pCard);
            }

            const fleetBar = mk('div', { style: 'display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:10px;' });
            fleetBar.append(mk('span', { style: 'font-size:0.82rem;font-weight:600;color:#475569;' }, 'Fleet Account Filter:'));
            const acctSel = mk('select', { id: 'plt-acct-select', class: 'uniselv-form-input', style: 'min-width:200px;' });
            const allOpt = mk('option', { value: '' }, 'All Accounts (Fleet Overview)');
            if (!curUser) allOpt.selected = true;
            acctSel.append(allOpt);
            accounts.forEach(u => {
                const o = mk('option', { value: u }, u);
                if (u === curUser) o.selected = true;
                acctSel.append(o);
            });
            acctSel.onchange = () => {
                this._pltSelectedUser = acctSel.value;
                this.loadPlatformAdmin();
            };
            const selfTestBtn = mk('button', { class: 'uniselv-btn btn-outline btn-sm', type: 'button', id: 'plt-lrv-selftest-btn' }, curUser ? `Run Self-Test (${curUser})` : 'Run Live Laravel Self-Test');
            selfTestBtn.onclick = () => this.runPlatformLaravelSelfTest(accounts[0] || '');
            fleetBar.append(acctSel, selfTestBtn, mk('span', { style: 'font-size:0.79rem;color:#64748b;' }, 'Auto-discovered project Supervisor workers & active tenant services (no manual setup or .env editing).'));
            lrvBox.append(fleetBar);

            if (lrv.budget) {
                const b = lrv.budget;
                lrvBox.append(mk('div', { style: 'font-size:0.82rem;color:#475569;margin-bottom:10px;' },
                    `Account Budget (${b.username}): Plan=${b.plan_name} · Slice=${b.expected_slice} · Max Queue Workers=${b.max_queue_workers} · Max Worker RAM=${b.max_worker_memory_mb} MiB · Horizon/Reverb=${b.horizon_allowed ? 'Allowed' : 'Disabled (<512 MiB or policy)'}`
                ));
            }

            const lrvOut = mk('div', { id: 'plt-lrv-output', style: 'margin-bottom:10px;' });
            lrvBox.append(lrvOut);
            if (this._pltLaravelResult) {
                this._renderPlatformStepBox(lrvOut, this._pltLaravelResult, 'Laravel Service Verification');
            }

            // Services fleet table
            const svcs = lrv.services || [];
            if (svcs.length) {
                const wrap = mk('div', { class: 'uniselv-table-wrap', style: 'margin-bottom:10px;' });
                const tbl = mk('table', { class: 'uniselv-table' });
                const hr = tbl.createTHead().insertRow();
                ['Account', 'Service', 'Project', 'PHP', 'Workers / Port', 'Slice / State', 'Admin Controls'].forEach(c => hr.append(mk('th', {}, c)));
                const tb = tbl.createTBody();
                svcs.forEach(s => {
                    const tr = tb.insertRow();
                    const actTd = mk('div', { style: 'display:flex;gap:4px;flex-wrap:wrap;' });
                    [['start', 'Start'], ['stop', 'Stop'], ['restart', 'Restart'], [s.enabled ? 'disable' : 'enable', s.enabled ? 'Disable' : 'Enable'], ['test', 'Test'], ['logs', 'Logs'], ['uninstall', s.orphaned ? 'Clean / Remove' : 'Remove']].forEach(([op, lbl]) => {
                        const b = mk('button', { class: `uniselv-btn btn-sm ${op === 'uninstall' ? 'btn-danger' : 'btn-outline'}`, type: 'button', style: 'padding:3px 7px;font-size:0.74rem;' }, lbl);
                        b.onclick = () => {
                            if (op === 'uninstall' && !confirm(`Are you sure you want to stop and remove worker "${s.service_slug}" for ${s.username}?`)) return;
                            this.controlLaravelService(s.id, op, false, s.username);
                        };
                        actTd.append(b);
                    });
                    const cells = [
                        s.username,
                        `${s.service_type.toUpperCase()} (${s.service_slug})`,
                        s.app_path,
                        s.php_branch,
                        s.service_type === 'reverb' ? `Port ${s.port || '-'}` : `${s.workers}w (${s.queues})`,
                        mk('span', { class: `uniselv-badge ${s.orphaned ? 'badge-critical' : (s.runtime_active ? 'badge-normal' : (s.active_state === 'failed' ? 'badge-critical' : 'badge-warning'))}` }, s.orphaned ? `⚠️ Orphaned (Missing Project)` : `${s.active_state || 'inactive'} · ${s.slice || '-'}`),
                        actTd
                    ];
                    cells.forEach(v => {
                        const td = tr.insertCell();
                        if (v instanceof Node) td.append(v);
                        else td.textContent = String(v ?? '-');
                    });
                });
                wrap.append(tbl);
                lrvBox.append(wrap);
            } else {
                lrvBox.append(mk('p', { style: 'margin:0 0 10px 0;font-size:0.84rem;color:#64748b;' }, curUser ? `No managed Laravel services deployed by ${curUser}.` : 'No managed Laravel services deployed across accounts yet. Customers configure their own projects from Enduser -> App Services & Tools.'));
            }

            // Optional collapsible Admin Support Override
            const supDet = mk('details', { style: 'background:#ffffff;border:1px solid #e2e8f0;border-radius:8px;padding:8px 12px;' });
            supDet.append(mk('summary', { style: 'cursor:pointer;font-size:0.82rem;font-weight:600;color:#475569;' }, 'Support Override: Provision Laravel Service on Behalf of Selected Account (Optional)'));
            const supBody = mk('div', { style: 'margin-top:10px;' });
            const disc = lrv.discovered_apps || [];
            const phpBranches = lrv.php_branches || ['php84'];
            const defaultPhp = disc[0]?.recommended_php || phpBranches[phpBranches.length - 1] || 'php84';
            if (!curUser) {
                supBody.append(mk('p', { style: 'margin:0;font-size:0.82rem;color:#64748b;' }, 'Select a specific account from Fleet Account Filter above to inspect its Laravel projects or provision a support unit.'));
            } else {
                const warnBox = mk('div', { id: 'plt-lrv-env-warn', style: 'display:none;background:#fffbeb;border:1px solid #fcd34d;color:#92400e;border-radius:8px;padding:8px 10px;font-size:0.8rem;margin-bottom:10px;' });
                if (disc.length) {
                    const dWrap = mk('div', { style: 'display:flex;flex-wrap:wrap;gap:6px;margin-bottom:10px;align-items:center;' });
                    dWrap.append(mk('span', { style: 'font-size:0.8rem;font-weight:600;color:#334155;' }, 'Discovered Laravel Projects:'));
                    disc.forEach(app => {
                        const tag = this._formatLaravelAppLabel(app, app.relative_path === '.' ? '~/ (root)' : app.app_path);
                        const btn = mk('button', { class: 'uniselv-btn btn-outline btn-sm', type: 'button', style: 'font-size:0.76rem;' }, tag);
                        btn.onclick = () => this._applyLaravelAppDefaults('plt-lrv', app, phpBranches);
                        dWrap.append(btn);
                    });
                    supBody.append(dWrap);
                }
                const fGrid = mk('div', { style: 'display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:10px;align-items:end;' });
                const defaultAppPath = disc[0]?.app_path || `/home/${curUser}/public_html`;
                fGrid.append(
                    mkInput('plt-lrv-type', 'Service Type', 'select', 'queue', {
                        options: [['queue', 'Laravel Queue Worker'], ['horizon', 'Laravel Horizon'], ['reverb', 'Laravel Reverb WebSocket'], ['scheduler', 'Laravel Scheduler']]
                    }),
                    mkInput('plt-lrv-app-path', 'Project Path (artisan)', 'text', defaultAppPath),
                    mkInput('plt-lrv-php', 'PHP Version', 'select', defaultPhp, {
                        options: phpBranches.map(p => [p, p.toUpperCase()])
                    }),
                    mkInput('plt-lrv-workers', 'Workers', 'number', '1', { min: 1, max: 16 }),
                    mkInput('plt-lrv-queues', 'Queues', 'text', disc[0]?.recommended_queues || 'default')
                );
                const instBtn = mk('button', { class: 'uniselv-btn btn-outline', type: 'button' }, `Install for ${curUser}`);
                instBtn.onclick = () => this.installLaravelService(true);
                const instWrap = mk('div');
                instWrap.append(instBtn);
                fGrid.append(instWrap);
                supBody.append(fGrid, warnBox);
                if (disc[0]) this._renderLaravelEnvWarning(warnBox, disc[0]);
            }
            supDet.append(supBody);
            lrvBox.append(supDet);
            host.append(lrvBox);

            // 3. Redis ACL Isolation Policy & Dedicated Port Registry
            const isoBox = mk('div', { style: 'background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:14px;margin-bottom:16px;' });
            const isoHead = mk('div', { style: 'display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;margin-bottom:10px;' });
            const redisGlobalEn = settings.platform_redis_acl_enabled !== '0';
            isoHead.append(
                mk('h6', { style: 'font-weight:700;margin:0;' }, `3. Redis ACL Tenant Isolation Policy (Redis ${redis.redis_version || 'N/A'}) & Dedicated Port Registry`),
                mk('span', { class: `uniselv-badge ${redis.default_protected ? 'badge-normal' : 'badge-warning'}` }, redis.default_protected ? 'DEFAULT USER PROTECTED' : 'DEFAULT USER OPEN (LEGACY SAFE)')
            );
            isoBox.append(isoHead);
            const rBar = mk('div', { style: 'display:flex;gap:12px;flex-wrap:wrap;align-items:center;padding:10px 12px;background:#ffffff;border:1px solid #e2e8f0;border-radius:8px;margin-bottom:10px;' });
            const rSaveEn = mk('button', { class: 'uniselv-btn btn-primary btn-sm', type: 'button' }, 'Save Redis Policy');
            rSaveEn.onclick = () => this.savePlatformSettings();
            const rLock = mk('button', { class: 'uniselv-btn btn-outline btn-sm', type: 'button' }, redis.default_protected ? 'Unlock Default User (Compatibility)' : 'Lock Default User (Strict Isolation)');
            rLock.onclick = () => this.runAdminRedisAction('lock_default', !redis.default_protected);
            rBar.append(
                mkCheck('plt-redis-global-en', 'Allow Enduser Self-Service Redis ACL', redisGlobalEn),
                rSaveEn,
                rLock
            );
            isoBox.append(rBar);
            const rOut = mk('div', { id: 'plt-redis-output', style: 'margin-bottom:10px;' });
            isoBox.append(rOut);
            if (this._pltRedisTestResult) {
                this._renderPlatformStepBox(rOut, this._pltRedisTestResult, 'Redis ACL Isolation Verification');
            }

            if ((redis.accounts || []).length) {
                const rWrap = mk('div', { class: 'uniselv-table-wrap', style: 'margin-bottom:10px;' });
                const rt = mk('table', { class: 'uniselv-table' });
                const rh = rt.createTHead().insertRow();
                ['Account', 'Redis User', 'Key Prefix', 'Status', 'Password (Masked)', 'Actions'].forEach(c => rh.append(mk('th', {}, c)));
                const rb = rt.createTBody();
                redis.accounts.forEach(a => {
                    const tr = rb.insertRow();
                    const acts = mk('div', { style: 'display:flex;gap:6px;flex-wrap:wrap;' });
                    const tBtn = mk('button', { class: 'uniselv-btn btn-outline btn-sm', type: 'button', style: 'padding:3px 8px;font-size:0.74rem;' }, 'Test ACL');
                    tBtn.onclick = () => this.runAdminRedisAction('test', false, a.username);
                    const rvBtn = mk('button', { class: 'uniselv-btn btn-danger btn-sm', type: 'button', style: 'padding:3px 8px;font-size:0.74rem;' }, 'Revoke');
                    rvBtn.onclick = () => this.runAdminRedisAction('revoke', false, a.username);
                    acts.append(tBtn, rvBtn);
                    [a.username, a.redis_user, a.key_prefix, a.enabled ? 'ENABLED' : 'DISABLED', a.password_masked || 'configured', acts].forEach(v => {
                        const td = tr.insertCell();
                        if (v instanceof Node) td.append(v);
                        else td.textContent = String(v ?? '-');
                    });
                });
                rWrap.append(rt);
                isoBox.append(rWrap);
            } else {
                isoBox.append(mk('p', { style: 'margin:0 0 10px 0;font-size:0.83rem;color:#64748b;' }, 'No tenant Redis ACL credentials provisioned yet. Endusers create and manage their own prefix-locked Redis credentials inside App Services & Tools.'));
            }

            const rSup = mk('details', { style: 'background:#ffffff;border:1px solid #e2e8f0;border-radius:8px;padding:8px 12px;margin-bottom:10px;' });
            rSup.append(mk('summary', { style: 'cursor:pointer;font-size:0.82rem;font-weight:600;color:#475569;' }, 'Support Override: Manually Provision / Test Redis ACL for a Username'));
            const rSupBar = mk('div', { style: 'display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-top:8px;' });
            const rUser = mk('input', { id: 'plt-redis-user', class: 'uniselv-form-input', style: 'max-width:180px;', value: curUser, placeholder: 'username' });
            const rProv = mk('button', { class: 'uniselv-btn btn-outline btn-sm', type: 'button' }, 'Provision/Rotate ACL');
            rProv.onclick = () => this.runAdminRedisAction('provision');
            const rTest = mk('button', { class: 'uniselv-btn btn-outline btn-sm', type: 'button' }, 'Test Isolation');
            rTest.onclick = () => this.runAdminRedisAction('test');
            rSupBar.append(rUser, rProv, rTest);
            rSup.append(rSupBar);
            isoBox.append(rSup);

            if (ports.length) {
                const pWrap = mk('div', { class: 'uniselv-table-wrap' });
                const pt = mk('table', { class: 'uniselv-table' });
                const ph = pt.createTHead().insertRow();
                ['Account', 'Octane Port', 'Reverb WS Port', 'Horizon Port', 'Node Port', 'Python Port', 'Socket Dir'].forEach(c => ph.append(mk('th', {}, c)));
                const pb = pt.createTBody();
                ports.forEach(p => {
                    const pm = p.ports || {};
                    const tr = pb.insertRow();
                    [p.username, pm.octane_port, pm.reverb_port, pm.horizon_metrics_port, pm.node_port, pm.python_port, p.socket_dir].forEach(v => { tr.insertCell().textContent = String(v ?? '-'); });
                });
                pWrap.append(pt);
                isoBox.append(pWrap);
            }
            host.append(isoBox);

            // 4. Node/Python Containment, Heavy Binary Guard & Platform Settings
            const guardBox = mk('div', { style: 'background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:14px;margin-bottom:16px;' });
            guardBox.append(mk('h6', { style: 'font-weight:700;margin:0 0 10px 0;' }, `4. Node.js, Python, Log Watchdog & Heavy Binary Containment Guard (${runtimes.length} active detected)`));
            const sGrid = mk('div', { style: 'display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:10px;align-items:end;margin-bottom:12px;' });
            sGrid.append(
                mkCheck('plt-rt-contain', 'Enforce slice containment (Node/Python/Laravel)', settings.platform_runtime_containment !== '0'),
                mkCheck('plt-hb-guard', 'Guard Chromium/FFmpeg/LibreOffice', settings.platform_heavy_binary_guard !== '0'),
                mkCheck('plt-log-global-en', 'Allow Enduser App Log Self-Trim', settings.platform_log_watchdog_enabled !== '0'),
                mkCheck('plt-log-auto', 'Auto-trim oversized logs (>threshold)', settings.platform_log_auto_truncate === '1'),
                mkInput('plt-rt-mode', 'Guard Mode', 'select', settings.platform_runtime_mode || 'enforce', { options: [['enforce', 'Enforce (Contain & Cap)'], ['monitor', 'Monitor Only']] }),
                mkInput('plt-max-node', 'Max Node/Pm2 Procs', 'number', settings.platform_max_node_workers || '2', { min: 1, max: 32 }),
                mkInput('plt-max-py', 'Max Python Workers', 'number', settings.platform_max_python_workers || '2', { min: 1, max: 32 }),
                mkInput('plt-hb-conc', 'Heavy Binary Concurrency', 'number', settings.platform_heavy_binary_max_concurrent || '2', { min: 1, max: 16 }),
                mkInput('plt-hb-sec', 'Heavy Binary Max Sec', 'number', settings.platform_heavy_binary_max_sec || '300', { min: 30, max: 3600 }),
                mkInput('plt-log-mb', 'Log Bloat Threshold (MiB)', 'number', settings.platform_log_threshold_mib || '250', { min: 20, max: 10240 }),
                mkInput('plt-lrv-cap', 'Global Max Laravel Workers', 'number', settings.platform_laravel_max_workers_cap || '4', { min: 1, max: 32 })
            );
            const saveSetBtn = mk('button', { class: 'uniselv-btn btn-primary', type: 'button' }, 'Save Platform Policies');
            saveSetBtn.onclick = () => this.savePlatformSettings();
            sGrid.append(mk('div', {}, null));
            sGrid.lastChild.append(saveSetBtn);
            guardBox.append(sGrid);

            if (runtimes.length) {
                const rtWrap = mk('div', { class: 'uniselv-table-wrap' });
                const rtbl = mk('table', { class: 'uniselv-table' });
                const rhr = rtbl.createTHead().insertRow();
                ['PID', 'Account', 'Type', 'Binary', 'RSS (MiB)', 'Age (s)', 'Slice Containment'].forEach(c => rhr.append(mk('th', {}, c)));
                const rtb = rtbl.createTBody();
                runtimes.slice(0, 40).forEach(p => {
                    const tr = rtb.insertRow();
                    [
                        p.pid,
                        p.username,
                        p.kind,
                        p.comm,
                        p.rss_mib,
                        p.age_sec,
                        mk('span', { class: `uniselv-badge ${p.contained ? 'badge-normal' : 'badge-warning'}` }, p.contained ? `CONTAINED (${p.expected_slice})` : `ESCAPED -> ${p.expected_slice}`)
                    ].forEach(v => {
                        const td = tr.insertCell();
                        if (v instanceof Node) td.append(v);
                        else td.textContent = String(v ?? '-');
                    });
                });
                rtWrap.append(rtbl);
                guardBox.append(rtWrap);
            }
            host.append(guardBox);

            // 5. App Log Watchdog & Inode Monitor + 6. Server-to-Server Migration
            const logBox = mk('div', { style: 'background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:14px;margin-bottom:16px;' });
            logBox.append(mk('h6', { style: 'font-weight:700;margin:0 0 8px 0;' }, '5. App Log Bloat & Inode Watchdog'));
            if ((logsData.inodes || []).length) {
                const inoWrap = mk('div', { style: 'display:flex;gap:10px;flex-wrap:wrap;margin-bottom:10px;' });
                logsData.inodes.forEach(inRow => {
                    inoWrap.append(mk('span', { class: 'uniselv-badge badge-outline' }, `${inRow.mount}: Inodes ${inRow.used}/${inRow.total} (${inRow.use_pct})`));
                });
                logBox.append(inoWrap);
            }
            const findings = logsData.findings || [];
            if (findings.length) {
                const lWrap = mk('div', { class: 'uniselv-table-wrap' });
                const lt = mk('table', { class: 'uniselv-table' });
                const lh = lt.createTHead().insertRow();
                ['Account', 'Log Path', 'Size (MiB)', 'Status', 'Action'].forEach(c => lh.append(mk('th', {}, c)));
                const lb = lt.createTBody();
                findings.slice(0, 30).forEach(f => {
                    const tr = lb.insertRow();
                    const trimBtn = mk('button', { class: 'uniselv-btn btn-outline btn-sm', type: 'button' }, 'Trim (Keep Last 1000 Lines)');
                    trimBtn.onclick = () => this.truncateAppLog(f.username, f.log_path, false);
                    [
                        f.username,
                        f.log_path,
                        `${f.size_mib} MiB`,
                        mk('span', { class: `uniselv-badge ${f.over_threshold ? 'badge-critical' : 'badge-normal'}` }, f.over_threshold ? 'OVERSIZED' : 'OK'),
                        trimBtn
                    ].forEach(v => {
                        const td = tr.insertCell();
                        if (v instanceof Node) td.append(v);
                        else td.textContent = String(v ?? '-');
                    });
                });
                lWrap.append(lt);
                logBox.append(lWrap);
            } else {
                logBox.append(mk('p', { style: 'margin:0;font-size:0.84rem;color:#64748b;' }, 'No large app log files found in tenant homes.'));
            }
            host.append(logBox);

            // 6. Server-to-Server Policy Migration Export / Import
            const migBox = mk('div', { style: 'background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:14px;' });
            migBox.append(
                mk('h6', { style: 'font-weight:700;margin:0 0 6px 0;' }, '6. Server-to-Server Policy Migration (Secrets Excluded)'),
                mk('p', { style: 'font-size:0.83rem;color:#64748b;margin:0 0 8px 0;' }, 'Export plans, OpenSwoole & platform policies, package mappings, RBAC permissions, and managed Laravel service templates to JSON or preview/apply an imported bundle on a new server.')
            );
            const migTa = mk('textarea', { id: 'plt-import-json', class: 'uniselv-form-input', rows: '5', style: 'width:100%;font-family:monospace;font-size:0.78rem;margin-bottom:8px;', placeholder: 'Paste exported uniselv-policy-bundle JSON here...' }, this._pltImportText || '');
            migTa.oninput = () => { this._pltImportText = migTa.value; };
            const migBtns = mk('div', { style: 'display:flex;gap:8px;flex-wrap:wrap;margin-bottom:8px;' });
            const dryBtn = mk('button', { class: 'uniselv-btn btn-outline btn-sm', type: 'button' }, 'Dry-Run Preview Import');
            dryBtn.onclick = () => this.importPlatformPolicy(true);
            const appBtn = mk('button', { class: 'uniselv-btn btn-primary btn-sm', type: 'button' }, 'Apply Policy Bundle');
            appBtn.onclick = () => this.importPlatformPolicy(false);
            migBtns.append(dryBtn, appBtn);
            const migOut = mk('div', { id: 'plt-import-output', style: 'font-size:0.84rem;' });
            if (this._pltImportPreview) migOut.textContent = this._pltImportPreview;
            migBox.append(migTa, migBtns, migOut);
            host.append(migBox);
        }, { timeoutMs: 25000 });
    },

    _renderPlatformStepBox: function(container, res, title) {
        if (!container || !res) return;
        const mk = this._mkEl.bind(this);
        container.replaceChildren();
        const ok = res.all_passed !== undefined ? res.all_passed : Boolean(res.success);
        const box = mk('div', { style: `border:1px solid ${ok ? '#86efac' : '#fca5a5'};background:${ok ? '#f0fdf4' : '#fef2f2'};border-radius:8px;padding:10px 12px;` });
        box.append(mk('div', { style: 'font-weight:700;font-size:0.86rem;margin-bottom:6px;' }, `${title} — ${ok ? 'PASSED' : 'ATTENTION REQUIRED'}`));
        if (Array.isArray(res.steps)) {
            res.steps.forEach(s => {
                const row = mk('div', { style: 'font-size:0.81rem;margin-bottom:4px;display:flex;gap:8px;align-items:center;' });
                row.append(
                    mk('span', { class: `uniselv-badge ${s.passed ? 'badge-normal' : 'badge-critical'}` }, s.passed ? 'PASS' : 'FAIL'),
                    mk('span', {}, `${s.label || s.name}: ${s.detail || ''}`)
                );
                box.append(row);
            });
        } else if (Array.isArray(res.lines)) {
            const pre = mk('pre', { style: 'background:#0f172a;color:#e2e8f0;padding:8px;border-radius:6px;max-height:220px;overflow:auto;font-size:0.76rem;margin:0;' }, res.lines.join('\n') || '(empty log)');
            box.append(pre);
        } else {
            box.append(mk('div', { style: 'font-size:0.82rem;' }, res.message || res.error || JSON.stringify(res)));
        }
        container.append(box);
    },

    _startDepPolling: function() {
        const jobEl = document.getElementById('uniselv-platform-job');
        if (this._pltPolling) clearInterval(this._pltPolling);
        this._pltPollInFlight = false;
        this._pltPolling = setInterval(() => {
            if (this._pltPollInFlight) return;
            this._pltPollInFlight = true;
            this.callApi('platform_dep_status', {}, (e2, r2) => {
                this._pltPollInFlight = false;
                const d2 = r2?.data || r2;
                const j = d2?.job;
                if (!j) return;
                if (jobEl) jobEl.textContent = `Dependency job (${j.target || 'all'}): ${j.state}${j.error ? ' — ' + j.error : ''}`;
                if (j.state === 'completed' || j.state === 'failed') {
                    clearInterval(this._pltPolling);
                    this._pltPolling = null;
                    if (j.state === 'completed') UniselvNotify.success(`Dependency install (${j.target}) completed.`);
                    else UniselvNotify.error(`Dependency install failed: ${j.error || 'see logs'}`);
                    this.loadPlatformAdmin();
                }
            }, { timeoutMs: 12000 });
        }, 3000);
    },

    installPlatformDeps: function(target) {
        const jobEl = document.getElementById('uniselv-platform-job');
        if (jobEl) jobEl.textContent = `Starting background dependency installation (${target})...`;
        this.callApi('platform_install_deps', { target }, (err, res) => {
            const d = res?.data || res;
            if (err || !d?.success) {
                UniselvNotify.error(err || d?.error || 'Could not start dependency installer');
                return;
            }
            UniselvNotify.success(d.message || `Started ${target} installer`);
            this._startDepPolling();
        }, { timeoutMs: 30000 });
    },

    savePlatformSettings: function() {
        const allowedTypes = [
            document.getElementById('plt-lrv-allow-queue')?.checked ? 'queue' : '',
            document.getElementById('plt-lrv-allow-horizon')?.checked ? 'horizon' : '',
            document.getElementById('plt-lrv-allow-reverb')?.checked ? 'reverb' : '',
            document.getElementById('plt-lrv-allow-scheduler')?.checked ? 'scheduler' : '',
        ].filter(Boolean).join(',');
        const payload = {
            platform_laravel_services_enabled: document.getElementById('plt-lrv-global-en')?.checked ? '1' : '0',
            platform_laravel_allowed_types: allowedTypes,
            platform_supervisor_enabled: document.getElementById('plt-sup-global-en')?.checked ? '1' : '0',
            platform_redis_acl_enabled: document.getElementById('plt-redis-global-en')?.checked ? '1' : '0',
            platform_log_watchdog_enabled: document.getElementById('plt-log-global-en')?.checked ? '1' : '0',
            platform_runtime_containment: document.getElementById('plt-rt-contain')?.checked ? '1' : '0',
            platform_heavy_binary_guard: document.getElementById('plt-hb-guard')?.checked ? '1' : '0',
            platform_log_auto_truncate: document.getElementById('plt-log-auto')?.checked ? '1' : '0',
            platform_runtime_mode: document.getElementById('plt-rt-mode')?.value || 'enforce',
            platform_max_node_workers: document.getElementById('plt-max-node')?.value || '2',
            platform_max_python_workers: document.getElementById('plt-max-py')?.value || '2',
            platform_heavy_binary_max_concurrent: document.getElementById('plt-hb-conc')?.value || '2',
            platform_heavy_binary_max_sec: document.getElementById('plt-hb-sec')?.value || '300',
            platform_log_threshold_mib: document.getElementById('plt-log-mb')?.value || '250',
            platform_laravel_max_workers_cap: document.getElementById('plt-lrv-cap')?.value || '4',
        };
        this.callApi('platform_save_settings', payload, (err, res) => {
            const d = res?.data || res;
            if (err || !d?.success) UniselvNotify.error(err || d?.error || 'Failed saving platform policies');
            else {
                UniselvNotify.success('Platform governance policies saved.');
                this.loadPlatformAdmin();
            }
        });
    },

    toggleGlobalCapability: function(capKey, enableFlag, currentAllowed, settings) {
        const nextAllowed = new Set(currentAllowed || []);
        if (enableFlag) nextAllowed.add(capKey);
        else nextAllowed.delete(capKey);
        const payload = {
            platform_laravel_services_enabled: nextAllowed.size > 0 ? '1' : (settings?.platform_laravel_services_enabled || '1'),
            platform_laravel_allowed_types: Array.from(nextAllowed).join(','),
        };
        this.callApi('platform_save_settings', payload, (err, res) => {
            const d = res?.data || res;
            if (err || !d?.success) UniselvNotify.error(err || d?.error || `Failed updating ${capKey}`);
            else {
                UniselvNotify.success(`${capKey.toUpperCase()} ${enableFlag ? 'activated' : 'deactivated'} globally.`);
                this.loadPlatformAdmin();
            }
        });
    },

    runSupervisorAction: function(operation) {
        if (operation === 'install') {
            this.callApi('platform_supervisor_action', { operation: 'install' }, (err, res) => {
                const d = res?.data || res;
                if (err || !d?.success) UniselvNotify.error(err || d?.error || 'Failed installing Supervisor');
                else {
                    UniselvNotify.success('Supervisor installation started...');
                    this._startDepPolling();
                }
            }, { timeoutMs: 30000 });
            return;
        }
        this.callApi('platform_supervisor_action', { operation }, (err, res) => {
            const d = res?.data || res;
            if (err || !d?.success) {
                UniselvNotify.error(err || d?.error || `Supervisor ${operation} failed`);
                return;
            }
            if (operation === 'test') {
                this._pltSupResult = d;
            } else {
                UniselvNotify.success(`Supervisor ${operation} completed (${d.supervisor?.active_state || 'ok'}).`);
            }
            this.loadPlatformAdmin();
        }, { timeoutMs: 30000 });
    },

    saveUserPlatformPermissions: function(username, explicitMap) {
        if (!username) {
            UniselvNotify.warning('Select an account first.');
            return;
        }
        const perms = explicitMap || {
            platform_laravel_queue: document.getElementById('plt-up-queue')?.checked ? 1 : 0,
            platform_laravel_horizon: document.getElementById('plt-up-horizon')?.checked ? 1 : 0,
            platform_laravel_reverb: document.getElementById('plt-up-reverb')?.checked ? 1 : 0,
            platform_laravel_scheduler: document.getElementById('plt-up-scheduler')?.checked ? 1 : 0,
            platform_supervisor: document.getElementById('plt-up-supervisor')?.checked ? 1 : 0,
        };
        const payload = Object.assign({ username }, perms);
        this.callApi('save_user_platform_permissions', payload, (err, res) => {
            const d = res?.data || res;
            if (err || !d?.success) UniselvNotify.error(err || d?.error || 'Failed updating user permissions');
            else {
                UniselvNotify.success(`Permissions updated for ${username}.`);
                this.loadPlatformAdmin();
            }
        }, { timeoutMs: 30000 });
    },

    installLaravelService: function(isAdminContext) {
        const prefix = isAdminContext ? 'plt-lrv' : 'eu-lrv';
        const payload = {
            username: isAdminContext ? (document.getElementById('plt-acct-select')?.value || this._pltSelectedUser || '') : '',
            service_type: document.getElementById(`${prefix}-type`)?.value || 'queue',
            app_path: document.getElementById(`${prefix}-app-path`)?.value || '',
            php_branch: document.getElementById(`${prefix}-php`)?.value || 'php84',
            workers: document.getElementById(`${prefix}-workers`)?.value || '1',
            queues: document.getElementById(`${prefix}-queues`)?.value || 'default',
            enabled: '1',
        };
        this.callApi('save_laravel_service', payload, (err, res) => {
            const d = res?.data || res;
            if (err || !d?.success) {
                UniselvNotify.error(err || d?.error || 'Failed installing Laravel service');
                return;
            }
            UniselvNotify.success(`Installed & enabled ${d.unit_name} (${d.active_state}) in ${d.slice || 'account slice'}.`);
            if (isAdminContext) this.loadPlatformAdmin();
            else this.loadEnduserServices();
        }, { timeoutMs: 40000 });
    },

    controlLaravelService: function(serviceId, operation, isEnduser, username) {
        this.callApi('control_laravel_service', { service_id: serviceId, operation, ...(username ? { username } : {}) }, (err, res) => {
            const d = res?.data || res;
            if (err || !d?.success) {
                UniselvNotify.error(err || d?.error || `Laravel service ${operation} failed`);
                return;
            }
            if (operation === 'test' || operation === 'logs') {
                if (isEnduser) {
                    this._euLaravelResult = d;
                    this.loadEnduserServices();
                } else {
                    this._pltLaravelResult = d;
                    this.loadPlatformAdmin();
                }
                return;
            }
            UniselvNotify.success(`Service ${d.unit_name}: ${operation} complete (${d.uninstalled ? 'removed' : d.active_state}).`);
            if (isEnduser) this.loadEnduserServices();
            else this.loadPlatformAdmin();
        }, { timeoutMs: 40000 });
    },

    runPlatformLaravelSelfTest: function(fallbackUser = '') {
        const username = document.getElementById('plt-acct-select')?.value || this._pltSelectedUser || fallbackUser || '';
        const php_branch = document.getElementById('plt-lrv-php')?.value || 'php84';
        if (!username) return UniselvNotify.warning('Select a target account first.');
        const out = document.getElementById('plt-lrv-output');
        if (out) out.textContent = `Running live ephemeral Laravel worker & slice self-test for ${username}...`;
        this.callApi('platform_selftest_laravel', { username, php_branch }, (err, res) => {
            const d = res?.data || res;
            if (err || !d?.success) {
                UniselvNotify.error(err || d?.error || 'Laravel self-test failed');
                return;
            }
            this._pltLaravelResult = d;
            if (d.all_passed) UniselvNotify.success(`Laravel service self-test PASSED for ${username}.`);
            else UniselvNotify.error(`Laravel service self-test failed for ${username}.`);
            this.loadPlatformAdmin();
        }, { timeoutMs: 45000 });
    },

    runAdminRedisAction: function(operation, lockDefault, explicitUser) {
        const username = explicitUser || document.getElementById('plt-redis-user')?.value?.trim() || this._pltSelectedUser || '';
        const payload = { operation, username };
        if (operation === 'lock_default') payload.lock_default = lockDefault ? '1' : '0';
        this.callApi('platform_redis_action', payload, (err, res) => {
            const d = res?.data || res;
            if (err || !d?.success) {
                UniselvNotify.error(err || d?.error || `Redis ${operation} failed`);
                return;
            }
            if (operation === 'test') {
                this._pltRedisTestResult = d;
            } else {
                UniselvNotify.success(d.message || `Redis ${operation} succeeded${d.redis_user ? ' for ' + d.redis_user : ''}.`);
            }
            this.loadPlatformAdmin();
        }, { timeoutMs: 30000 });
    },

    enforcePlatformRuntimes: function() {
        this.callApi('platform_enforce_runtimes', {}, (err, res) => {
            const d = res?.data || res;
            if (err || !d?.success) UniselvNotify.error(err || d?.error || 'Enforcement sweep failed');
            else {
                UniselvNotify.success(`Contained ${d.contained || 0} runtimes, stopped ${d.terminated || 0} offending binaries.`);
                this.loadPlatformAdmin();
            }
        });
    },

    scanPlatformLogs: function() {
        this.callApi('platform_scan_logs', {}, (err, res) => {
            const d = res?.data || res;
            if (err || !d?.success) UniselvNotify.error(err || d?.error || 'Log scan failed');
            else {
                this._pltLogResult = d;
                UniselvNotify.success(`Scanned ${(d.findings || []).length} log files.`);
                this.loadPlatformAdmin();
            }
        });
    },

    syncLaravelWorkersAdmin: function() {
        const username = document.getElementById('plt-acct-select')?.value || this._pltSelectedUser || '';
        const btn = document.getElementById('plt-sync-btn');
        if (btn) btn.disabled = true;
        UniselvNotify.info(username ? `Scanning and reconciling workers for ${username}...` : 'Auto-detecting and reconciling workers across all accounts...');
        this.callApi('sync_laravel_workers', { ...(username ? { username } : {}), auto_prune: true }, (err, res) => {
            if (btn) btn.disabled = false;
            const d = res?.data || res;
            if (err || !d?.success) {
                UniselvNotify.error(err || d?.error || 'Worker auto-detection failed');
                return;
            }
            const synced = d.synced_count ?? (d.synced || []).length;
            const pruned = d.pruned_count ?? (d.pruned || []).length;
            UniselvNotify.success(`Sync complete: ${synced} active worker(s) synced, ${pruned} orphaned config(s) cleaned up.`);
            this.loadPlatformAdmin();
        }, { timeoutMs: 45000 });
    },

    truncateAppLog: function(username, logPath, isEnduser) {
        this.callApi('truncate_app_log', { username, log_path: logPath, keep_lines: 1000 }, (err, res) => {
            const d = res?.data || res;
            if (err || !d?.success) UniselvNotify.error(err || d?.error || 'Log trim failed');
            else {
                UniselvNotify.success(`Trimmed ${d.log_path}: freed ${d.freed_bytes || 0} bytes (kept last 1000 lines).`);
                if (isEnduser) this.loadEnduserServices();
                else this.scanPlatformLogs();
            }
        });
    },

    exportPlatformPolicy: function() {
        this.callApi('platform_export_policy', {}, (err, res) => {
            const d = res?.data || res;
            if (err || !d?.bundle) return UniselvNotify.error(err || d?.error || 'Export failed');
            const jsonText = JSON.stringify(d.bundle, null, 2);
            this._pltImportText = jsonText;
            const blob = new Blob([jsonText], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `uniselv-policy-bundle-${new Date().toISOString().slice(0, 10)}.json`;
            a.click();
            URL.revokeObjectURL(url);
            UniselvNotify.success('Policy migration bundle exported (secrets stripped).');
            this.loadPlatformAdmin();
        });
    },

    importPlatformPolicy: function(dryRun) {
        const raw = document.getElementById('plt-import-json')?.value || '';
        if (!raw.trim()) return UniselvNotify.warning('Paste an exported policy bundle JSON first.');
        this.callApi('platform_import_policy', { bundle: raw, dry_run: dryRun ? '1' : '0' }, (err, res) => {
            const d = res?.data || res;
            if (err || !d?.success) return UniselvNotify.error(err || d?.error || 'Import failed');
            this._pltImportPreview = `${dryRun ? '[DRY-RUN PREVIEW]' : '[APPLIED]'} Summary: ${JSON.stringify(d.summary || {})}${d.reinstalled_services !== undefined ? ' · Reinstalled services: ' + d.reinstalled_services : ''}`;
            UniselvNotify.success(dryRun ? 'Dry-run preview ready.' : 'Policy migration bundle applied cleanly.');
            this.loadPlatformAdmin();
        }, { timeoutMs: 30000 });
    },

    _formatLaravelAppLabel: function(app, baseLabel) {
        const flags = [
            app && app.has_horizon ? 'Horizon' : '',
            app && app.has_reverb ? 'Reverb' : '',
            app && app.has_vendor === false ? 'no-vendor' : '',
            app && app.env && app.env.has_env === false ? 'no-.env' : '',
        ].filter(Boolean);
        return flags.length ? `${baseLabel} [${flags.join(', ')}]` : baseLabel;
    },

    _renderLaravelEnvWarning: function(warnEl, app) {
        if (!warnEl) return;
        if (app && app.env && app.env.has_env === false) {
            const phpHint = app.php_constraint ? ` (requires PHP ${app.php_constraint})` : '';
            warnEl.style.display = 'block';
            warnEl.textContent = `Heads up: No ".env" file found yet in ${app.app_path}${phpHint}. Run your web installer or create .env before expecting workers to process database/Redis jobs.`;
        } else {
            warnEl.style.display = 'none';
            warnEl.textContent = '';
        }
    },

    _applyLaravelAppDefaults: function(prefix, app, phpBranches) {
        if (!app) return;
        const inp = document.getElementById(`${prefix}-app-path`);
        if (inp) inp.value = app.app_path;
        const phpSel = document.getElementById(`${prefix}-php`);
        if (phpSel) {
            const fallbackPhp = (phpBranches || [])[(phpBranches || []).length - 1] || 'php84';
            const targetPhp = app.recommended_php || fallbackPhp;
            if (Array.from(phpSel.options).some(o => o.value === targetPhp)) {
                phpSel.value = targetPhp;
            }
        }
        const qInp = document.getElementById(`${prefix}-queues`);
        if (qInp && app.recommended_queues) {
            qInp.value = app.recommended_queues;
        }
        this._renderLaravelEnvWarning(document.getElementById(`${prefix}-env-warn`), app);
    },

    // ==================== ENDUSER APP SERVICES & TOOLS ====================

    loadEnduserServices: function() {
        const host = document.getElementById('uniselv-enduser-services-body');
        if (!host) return;
        host.textContent = 'Loading your Laravel services, dedicated ports, Redis ACL & logs...';
        this.callApi('platform_services', {}, (err, res) => {
            const d = res?.data || res;
            if (err || !d?.success) {
                host.textContent = `App services unavailable: ${err || d?.error || 'Check daemon status'}`;
                return;
            }
            const mk = this._mkEl.bind(this);
            const cfg = d.settings || {};
            const lrv = d.laravel || {};
            const redis = d.redis || {};
            const alloc = d.port_allocation || lrv.port_allocation || {};
            const logsData = d.logs || {};
            const disc = lrv.discovered_apps || [];
            host.replaceChildren();

            // 1. Granted Feature Permissions & Scoped Supervisor Access (Zero manual forms / zero .env edits)
            const lrvBox = mk('div', { style: 'background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:14px;margin-bottom:16px;' });
            lrvBox.append(mk('h6', { style: 'font-weight:700;margin:0 0 6px 0;' }, '1. Granted Feature Permissions & Project Integration'));
            lrvBox.append(mk('p', { style: 'margin:0 0 10px 0;font-size:0.82rem;color:#475569;' },
                'Your server administrator manages server packages and grants permissions below. Configure Queue Workers, Horizon, Reverb WebSocket, Scheduler, and Supervisor directly inside your own Laravel project admin panel or settings — UNISELV never edits your .env or requires terminal access.'
            ));
            const lrvBudget = lrv.budget || {};
            const lrvGlobalOn = cfg.platform_laravel_services_enabled !== '0' && lrvBudget.services_globally_enabled !== false;
            const supReady = lrvBudget.supervisor_allowed && lrvBudget.supervisor_active;
            const phpBranches = lrv.php_branches || ['php84'];
            const latestPhp = phpBranches[phpBranches.length - 1] || 'php84';
            const reverbPort = alloc.ports?.reverb_port || '-';
            const horizonPort = alloc.ports?.horizon_metrics_port || '-';

            if (!lrvGlobalOn) {
                lrvBox.append(mk('div', { style: 'background:#fffbeb;border:1px solid #fcd34d;color:#92400e;border-radius:8px;padding:10px 12px;font-size:0.84rem;margin-bottom:10px;' }, 'Laravel platform capabilities are currently deactivated globally by your server administrator.'));
            }

            const permWrap = mk('div', { class: 'uniselv-table-wrap', style: 'background:#ffffff;border:1px solid #e2e8f0;border-radius:8px;margin-bottom:12px;' });
            const permTbl = mk('table', { class: 'uniselv-table' });
            const permHr = permTbl.createTHead().insertRow();
            ['Feature / Runtime', 'Permission Status', 'How Your Project Uses It'].forEach(c => permHr.append(mk('th', {}, c)));
            const permTb = permTbl.createTBody();
            [
                [
                    'Supervisor (No Terminal)',
                    supReady ? 'ACTIVE & PERMITTED' : (lrvBudget.supervisor_allowed ? 'PERMITTED (DAEMON STOPPED)' : 'DISABLED BY ADMIN'),
                    supReady,
                    `Scoped drop-in folder: /home/${d.username}/.uniselv-supervisor/conf.d/ — projects with built-in Supervisor setup run automatically under ${lrvBudget.expected_slice || 'your account slice'}.`
                ],
                [
                    'Laravel Queue Workers',
                    lrvBudget.queue_allowed ? `PERMITTED (Max ${lrvBudget.max_queue_workers || 1} Workers)` : 'DISABLED BY ADMIN',
                    lrvBudget.queue_allowed,
                    `Configure queue driver & workers inside your project's own admin panel or installer (${lrvBudget.max_worker_memory_mb || 256} MiB/worker cap).`
                ],
                [
                    'Laravel Horizon',
                    lrvBudget.horizon_allowed ? `PERMITTED (Port ${horizonPort})` : (lrvBudget.mem_max_mib < 512 ? 'NEEDS >=512 MiB PLAN' : 'DISABLED BY ADMIN'),
                    lrvBudget.horizon_allowed,
                    `Configure Redis & Horizon in your Laravel project settings when enabled on your plan.`
                ],
                [
                    'Laravel Reverb / WebSocket',
                    lrvBudget.reverb_allowed ? `PERMITTED (Port ${reverbPort})` : (lrvBudget.mem_max_mib < 512 ? 'NEEDS >=512 MiB PLAN' : 'DISABLED BY ADMIN'),
                    lrvBudget.reverb_allowed,
                    `Set assigned WebSocket port ${reverbPort} directly in your project's Reverb/Broadcasting settings.`
                ],
                [
                    'Laravel Scheduler',
                    lrvBudget.scheduler_allowed ? 'PERMITTED' : 'DISABLED BY ADMIN',
                    lrvBudget.scheduler_allowed,
                    `Use PHP CLI (/usr/local/apps/${latestPhp}/bin/php) in your project scheduler or Webuzo Cron (* * * * * ... artisan schedule:run).`
                ]
            ].forEach(([feat, statusTxt, ok, guide]) => {
                const tr = permTb.insertRow();
                let guideCellContent = mk('span', { style: 'font-size:0.8rem;color:#475569;' }, guide);
                if (feat === 'Laravel Scheduler' && ok) {
                    const wrapGuide = mk('div', { style: 'display:flex;align-items:center;justify-content:space-between;gap:8px;flex-wrap:wrap;' });
                    wrapGuide.append(guideCellContent);
                    const cronBtn = mk('button', { class: 'uniselv-btn btn-outline btn-sm', type: 'button', style: 'padding:2px 8px;font-size:0.75rem;white-space:nowrap;' }, '⏱️ Webuzo Cron');
                    cronBtn.onclick = () => this.manageSchedulerCronDialog(disc, latestPhp, true);
                    wrapGuide.append(cronBtn);
                    guideCellContent = wrapGuide;
                }
                [
                    mk('strong', {}, feat),
                    mk('span', { class: `uniselv-badge ${ok ? 'badge-normal' : 'badge-warning'}` }, statusTxt),
                    guideCellContent
                ].forEach(v => {
                    const td = tr.insertCell();
                    td.append(v);
                });
            });
            permWrap.append(permTbl);
            lrvBox.append(permWrap);

            if (lrv.budget) {
                const b = lrv.budget;
                lrvBox.append(mk('div', { style: 'font-size:0.82rem;color:#475569;margin-bottom:10px;' },
                    `Account Plan (${b.plan_name}): Up to ${b.max_queue_workers} Workers · ${b.max_worker_memory_mb} MiB/Worker · Isolated Slice: ${b.expected_slice}`
                ));
            }

            const euOut = mk('div', { id: 'eu-lrv-output', style: 'margin-bottom:10px;' });
            lrvBox.append(euOut);
            if (this._euLaravelResult) this._renderPlatformStepBox(euOut, this._euLaravelResult, 'Worker Health & Logs');

            const svcs = lrv.services || [];
            if (svcs.length) {
                lrvBox.append(mk('div', { style: 'font-size:0.82rem;font-weight:700;color:#1e293b;margin:8px 0 6px 0;' }, 'Detected Active Workers (From Your Project Config)'));
                const sw = mk('div', { class: 'uniselv-table-wrap' });
                const st = mk('table', { class: 'uniselv-table' });
                const sh = st.createTHead().insertRow();
                ['Program / Service', 'Project Path', 'Workers / Port', 'State', 'Health Tools'].forEach(c => sh.append(mk('th', {}, c)));
                const sb = st.createTBody();
                svcs.forEach(s => {
                    const tr = sb.insertRow();
                    const acts = mk('div', { style: 'display:flex;gap:4px;flex-wrap:wrap;' });
                    const btns = [['restart', 'Restart'], ['test', 'Test'], ['logs', 'Logs']];
                    btns.push(['uninstall', s.orphaned ? 'Clean / Remove' : 'Remove']);
                    btns.forEach(([op, lbl]) => {
                        const b = mk('button', { class: `uniselv-btn btn-sm ${op === 'uninstall' ? 'btn-danger' : 'btn-outline'}`, type: 'button', style: 'padding:3px 7px;font-size:0.74rem;' }, lbl);
                        b.onclick = () => {
                            if (op === 'uninstall' && !confirm(`Are you sure you want to stop and remove worker "${s.service_slug}"?${s.source === 'project_dropin' ? ' This will delete its supervisor drop-in configuration.' : ''}`)) return;
                            this.controlLaravelService(s.id, op, true);
                        };
                        acts.append(b);
                    });
                    [
                        s.source === 'project_dropin' ? `SUPERVISOR (${s.service_slug})` : `${s.service_type.toUpperCase()} (${s.service_slug})`,
                        s.app_path,
                        s.service_type === 'reverb' ? `Port ${s.port || '-'}` : `${s.workers}w (${s.queues})`,
                        mk('span', { class: `uniselv-badge ${s.orphaned ? 'badge-critical' : (s.runtime_active ? 'badge-normal' : (s.active_state === 'failed' ? 'badge-critical' : 'badge-warning'))}` }, s.orphaned ? '⚠️ Orphaned (Missing Project)' : (s.active_state || 'inactive')),
                        acts
                    ].forEach(v => {
                        const td = tr.insertCell();
                        if (v instanceof Node) td.append(v);
                        else td.textContent = String(v ?? '-');
                    });
                });
                sw.append(st);
                lrvBox.append(sw);
            } else {
                lrvBox.append(mk('div', { style: 'background:#ffffff;border:1px solid #e2e8f0;border-radius:8px;padding:10px 12px;font-size:0.82rem;color:#64748b;' },
                    'No active background workers detected yet. Enable Queue/Horizon/Reverb/Supervisor directly inside your Laravel project settings or admin panel.'
                ));
            }
            host.append(lrvBox);

            // 2. Assigned Ports, Sockets & Proxy Snippet
            const pBox = mk('div', { style: 'background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:14px;margin-bottom:16px;' });
            pBox.append(mk('h6', { style: 'font-weight:700;margin:0 0 8px 0;' }, '2. Dedicated Ports, Private Sockets & Proxy Snippet'));
            const portsMap = alloc.ports || {};
            pBox.append(mk('div', { style: 'font-size:0.84rem;margin-bottom:8px;' },
                `Octane: ${portsMap.octane_port || '-'} · Reverb WS: ${portsMap.reverb_port || '-'} · Horizon: ${portsMap.horizon_metrics_port || '-'} · Node: ${portsMap.node_port || '-'} · Python: ${portsMap.python_port || '-'} · Socket Dir: ${alloc.socket_dir || '-'}`
            ));
            if (alloc.reverb_proxy_snippet) {
                pBox.append(mk('div', { style: 'font-size:0.78rem;color:#64748b;margin-bottom:6px;' }, 'Reverb WebSocket /domain vhost proxy template (apply in Webuzo custom vhost config or request support):'));
                const proxyRow = mk('div', { style: 'display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:8px;' });
                proxyRow.append(this._mkCodeCopyBox(alloc.reverb_proxy_snippet, 'Copy Proxy Config'));
                const proxyBtn = mk('button', { class: 'uniselv-btn btn-outline btn-sm', type: 'button', style: 'padding:4px 10px;font-size:0.78rem;' }, '🌐 Enable Proxy in Webuzo Apache VHost');
                proxyBtn.onclick = () => this.manageReverbProxyDialog(disc, portsMap.reverb_port);
                proxyRow.append(proxyBtn);
                pBox.append(proxyRow);
            }
            host.append(pBox);

            // 3. Optional Redis ACL Credentials (Read-Only Values for Project Settings)
            const rBox = mk('div', { style: 'background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:14px;margin-bottom:16px;' });
            const rHead = mk('div', { style: 'display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;margin-bottom:8px;' });
            rHead.append(mk('h6', { style: 'font-weight:700;margin:0;' }, '3. Isolated Redis ACL Credentials (Optional Project Settings)'));
            const redisGlobalOn = cfg.platform_redis_acl_enabled !== '0';
            const rBtns = mk('div', { style: 'display:flex;gap:6px;flex-wrap:wrap;' });
            if (redisGlobalOn) {
                const rp = mk('button', { class: 'uniselv-btn btn-primary btn-sm', type: 'button' }, (redis.accounts || []).length ? 'Rotate Redis Password' : 'Create My Redis ACL');
                rp.onclick = () => this.runEnduserRedisAction('provision');
                const rt = mk('button', { class: 'uniselv-btn btn-outline btn-sm', type: 'button' }, 'Test Isolation');
                rt.onclick = () => this.runEnduserRedisAction('test');
                rBtns.append(rp, rt);
            }
            rHead.append(rBtns);
            rBox.append(rHead);
            const euR = (redis.accounts || [])[0];
            if (!redisGlobalOn && !euR) {
                rBox.append(mk('div', { style: 'background:#fffbeb;border:1px solid #fcd34d;color:#92400e;border-radius:8px;padding:10px 12px;font-size:0.83rem;' }, 'Self-service Redis ACL provisioning is disabled by your server administrator.'));
            } else if (euR?.env_snippet) {
                rBox.append(this._mkCodeCopyBox(euR.env_snippet, 'Copy Settings'));
            } else {
                rBox.append(mk('p', { style: 'font-size:0.83rem;color:#64748b;margin:0;' }, 'Click "Create My Redis ACL" to generate dedicated prefix-locked Redis credentials for your Laravel queues & cache.'));
            }
            if (this._euRedisResult) {
                const ro = mk('div');
                this._renderPlatformStepBox(ro, this._euRedisResult, 'Redis ACL Isolation Test');
                rBox.append(ro);
            }
            host.append(rBox);

            // 4. App Logs Cleanup
            const lgBox = mk('div', { style: 'background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:14px;' });
            lgBox.append(mk('h6', { style: 'font-weight:700;margin:0 0 8px 0;' }, '4. Application Log Watchdog & Safe Trim'));
            const logSelfTrimOn = cfg.platform_log_watchdog_enabled !== '0';
            if (!logSelfTrimOn) {
                lgBox.append(mk('div', { style: 'font-size:0.81rem;color:#64748b;margin-bottom:8px;' }, 'Self-service log trimming is currently managed by your server administrator.'));
            }
            const lgRows = logsData.findings || [];
            if (lgRows.length) {
                const tw = mk('div', { class: 'uniselv-table-wrap' });
                const lt = mk('table', { class: 'uniselv-table' });
                const lh = lt.createTHead().insertRow();
                ['Log File', 'Size (MiB)', 'Status', 'Action'].forEach(c => lh.append(mk('th', {}, c)));
                const lb = lt.createTBody();
                lgRows.forEach(f => {
                    const tr = lb.insertRow();
                    const tb = mk('button', { class: 'uniselv-btn btn-outline btn-sm', type: 'button' }, logSelfTrimOn ? 'Trim (Keep 1000 Lines)' : 'Managed by Admin');
                    if (!logSelfTrimOn) tb.disabled = true;
                    else tb.onclick = () => this.truncateAppLog(d.username, f.log_path, true);
                    [f.log_path, `${f.size_mib} MiB`, f.over_threshold ? 'OVERSIZED' : 'OK', tb].forEach(v => {
                        const td = tr.insertCell();
                        if (v instanceof Node) td.append(v);
                        else td.textContent = String(v ?? '-');
                    });
                });
                tw.append(lt);
                lgBox.append(tw);
            } else {
                lgBox.append(mk('p', { style: 'margin:0;font-size:0.83rem;color:#64748b;' }, 'No log files detected yet inside storage/logs or .uniselv-logs.'));
            }
            host.append(lgBox);
        }, { timeoutMs: 20000 });
    },

    scanEnduserLogs: function() {
        this.callApi('scan_app_logs', {}, (err, res) => {
            const d = res?.data || res;
            if (err || !d?.success) UniselvNotify.error(err || d?.error || 'Could not scan logs');
            else {
                UniselvNotify.success(`Found ${(d.findings || []).length} log files.`);
                this.loadEnduserServices();
            }
        });
    },

    syncLaravelWorkers: function() {
        UniselvNotify.info('Scanning projects and auto-detecting workers...');
        this.callApi('sync_laravel_workers', { auto_prune: true }, (err, res) => {
            const d = res?.data || res;
            if (err || !d?.success) {
                UniselvNotify.error(err || d?.error || 'Worker auto-detection failed');
                return;
            }
            const synced = d.synced_count ?? (d.synced || []).length;
            const pruned = d.pruned_count ?? (d.pruned || []).length;
            UniselvNotify.success(`Auto-detection complete: ${synced} active worker(s) synced, ${pruned} orphaned config(s) cleaned up.`);
            this.loadEnduserServices();
        }, { timeoutMs: 35000 });
    },

    runEnduserRedisAction: function(operation) {
        this.callApi('enduser_redis_action', { operation }, (err, res) => {
            const d = res?.data || res;
            if (err || !d?.success) return UniselvNotify.error(err || d?.error || `Redis ${operation} failed`);
            if (operation === 'test') {
                this._euRedisResult = d;
            } else {
                UniselvNotify.success(`Redis ACL updated for ${d.redis_user || 'your account'}.`);
            }
            this.loadEnduserServices();
        }, { timeoutMs: 30000 });
    },

    killStuckCliTasks: function() {
        UniselvModal.confirm({
            title: 'Terminate Stuck Background CLI Processes?',
            message: 'This will safely terminate runaway or hanging CLI background tasks (artisan commands, queue workers, bash/python scripts) owned by your account. <strong>Web server processes (PHP-FPM, Apache/LiteSpeed) are strictly protected and will remain running uninterrupted.</strong>',
            icon: 'danger',
            confirmText: 'Kill Stuck CLI Tasks',
            isDanger: true,
            onConfirm: () => {
                UniselvNotify.info('Scanning and terminating stuck CLI processes...');
                this.callApi('kill_stuck_cli_processes', {}, (err, res) => {
                    const d = res?.data || res;
                    if (err || !d?.success) {
                        UniselvNotify.error(err || d?.error || 'Failed to terminate CLI tasks');
                    } else {
                        const count = d.killed_count || 0;
                        if (count > 0) {
                            UniselvNotify.success(`Successfully terminated ${count} stuck CLI process(es). Details: ${(d.killed_pids || []).join(', ')}`);
                        } else {
                            UniselvNotify.info('No runaway or stuck CLI processes were found.');
                        }
                        this.loadLiveProcesses();
                    }
                });
            }
        });
    },

    manageSchedulerCronDialog: function(disc, phpBranch, isEnduser) {
        const apps = disc || [];
        const appPath = apps[0]?.app_path || '';
        if (!appPath) {
            UniselvNotify.warning('No Laravel application directory detected yet. Once your project is created in your home folder, click here to manage its Webuzo Cron.');
            return;
        }

        this.callApi('manage_laravel_scheduler_cron', { operation: 'status', app_path: appPath, php_branch: phpBranch }, (err, res) => {
            const d = res?.data || res;
            if (err || !d?.success) {
                UniselvNotify.error(err || d?.error || 'Failed to check scheduler cron status');
                return;
            }
            const isInstalled = !!d.is_installed;
            const cronLine = d.cron_line || `* * * * * /usr/local/apps/${phpBranch}/bin/php ${appPath}/artisan schedule:run > /dev/null 2>&1`;

            UniselvModal.confirm({
                title: 'Laravel Scheduler Webuzo Cron Manager',
                message: isInstalled
                    ? `<div style="text-align:left;">
                        <p style="margin:0 0 8px 0;">The Laravel scheduler is currently <strong>active</strong> in your Webuzo system crontab:</p>
                        <pre style="background:#0f172a;color:#86efac;padding:10px;border-radius:6px;font-size:0.76rem;overflow-x:auto;">${this.escapeHtml(cronLine)}</pre>
                        <p style="margin:8px 0 0 0;font-size:0.82rem;color:#64748b;">Click below to safely remove it from crontab.</p>
                       </div>`
                    : `<div style="text-align:left;">
                        <p style="margin:0 0 8px 0;">Install the 1-minute Laravel scheduler job directly into your Webuzo account crontab:</p>
                        <pre style="background:#0f172a;color:#f8fafc;padding:10px;border-radius:6px;font-size:0.76rem;overflow-x:auto;">${this.escapeHtml(cronLine)}</pre>
                        <p style="margin:8px 0 0 0;font-size:0.82rem;color:#64748b;">Runs safely as tenant user without terminal access.</p>
                       </div>`,
                icon: isInstalled ? 'warning' : 'info',
                confirmText: isInstalled ? 'Remove Cron Job' : 'Install into Webuzo Cron',
                isDanger: isInstalled,
                onConfirm: () => {
                    const nextOp = isInstalled ? 'remove' : 'install';
                    UniselvNotify.info(`${isInstalled ? 'Removing' : 'Installing'} scheduler cron...`);
                    this.callApi('manage_laravel_scheduler_cron', { operation: nextOp, app_path: appPath, php_branch: phpBranch }, (cErr, cRes) => {
                        const cd = cRes?.data || cRes;
                        if (cErr || !cd?.success) {
                            UniselvNotify.error(cErr || cd?.error || `Failed to ${nextOp} scheduler cron`);
                        } else {
                            UniselvNotify.success(cd.message || `Scheduler cron successfully ${nextOp}ed!`);
                            this.loadEnduserServices();
                        }
                    });
                }
            });
        });
    },

    manageReverbProxyDialog: function(disc, reverbPort) {
        const apps = disc || [];
        const domain = apps[0]?.domain || (this.currentUser ? `${this.currentUser}.com` : '');
        if (!domain) {
            UniselvNotify.warning('No active domain detected for Reverb WebSocket reverse proxy.');
            return;
        }
        const port = reverbPort || 22241;

        this.callApi('manage_reverb_vhost_proxy', { operation: 'status', domain: domain, port: port }, (err, res) => {
            const d = res?.data || res;
            if (err || !d?.success) {
                UniselvNotify.error(err || d?.error || 'Failed to inspect Apache VHost proxy status');
                return;
            }
            const isInstalled = !!d.is_installed;
            UniselvModal.confirm({
                title: `Reverb Apache Reverse Proxy (${domain})`,
                message: isInstalled
                    ? `<div style="text-align:left;">
                        <p style="margin:0 0 8px 0;">A dedicated Apache reverse proxy include is currently <strong>active</strong> for domain <code>${this.escapeHtml(domain)}</code>:</p>
                        <pre style="background:#0f172a;color:#86efac;padding:10px;border-radius:6px;font-size:0.76rem;overflow-x:auto;">/usr/local/apps/apache2/etc/conf.d/uniselv-reverb-${this.escapeHtml(domain)}.conf\n\nRouting /app & /apps -> ws://127.0.0.1:${port}</pre>
                        <p style="margin:8px 0 0 0;font-size:0.82rem;color:#64748b;">Click below to safely remove this proxy configuration and reload Apache.</p>
                       </div>`
                    : `<div style="text-align:left;">
                        <p style="margin:0 0 8px 0;">Automatically configure Apache reverse proxy for <code>${this.escapeHtml(domain)}</code>:</p>
                        <pre style="background:#0f172a;color:#f8fafc;padding:10px;border-radius:6px;font-size:0.76rem;overflow-x:auto;">Include /usr/local/apps/apache2/etc/conf.d/uniselv-reverb-${this.escapeHtml(domain)}.conf\nProxyPass /app ws://127.0.0.1:${port}/app\nProxyPassReverse /app ws://127.0.0.1:${port}/app</pre>
                        <p style="margin:8px 0 0 0;font-size:0.82rem;color:#64748b;">This uses modular Apache include files without modifying your vhost files directly, performs an <code>apachectl configtest</code>, and reloads gracefully.</p>
                       </div>`,
                icon: isInstalled ? 'warning' : 'info',
                confirmText: isInstalled ? 'Remove Proxy Config' : 'Enable Reverse Proxy',
                isDanger: isInstalled,
                onConfirm: () => {
                    const nextOp = isInstalled ? 'remove' : 'install';
                    UniselvNotify.info(`${isInstalled ? 'Removing' : 'Enabling'} Reverb Apache proxy...`);
                    this.callApi('manage_reverb_vhost_proxy', { operation: nextOp, domain: domain, port: port }, (pErr, pRes) => {
                        const pd = pRes?.data || pRes;
                        if (pErr || !pd?.success) {
                            UniselvNotify.error(pErr || pd?.error || `Failed to ${nextOp} Reverb proxy`);
                        } else {
                            UniselvNotify.success(pd.message || `Reverb reverse proxy ${nextOp}ed successfully!`);
                            this.loadEnduserServices();
                        }
                    });
                }
            });
        });
    }
};

if (typeof window !== 'undefined') {
    window.UniselvResMan = UniselvResMan;
}

