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
                <div class="uniselv-toast-title">${title}</div>
                <div class="uniselv-toast-msg">${message}</div>
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
        }
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

    bindTabs: function() {
        const tabs = document.querySelector('.uniselv-tabs');
        if (tabs && !document.getElementById('uniselv-mobile-section')) {
            const label = document.createElement('label');
            label.className = 'uniselv-mobile-navigation';
            label.textContent = 'Section';
            const select = document.createElement('select');
            select.id = 'uniselv-mobile-section';
            select.className = 'uniselv-select';
            select.setAttribute('aria-label', 'Section');
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
        document.querySelectorAll('.uniselv-tab-btn').forEach(btn => {
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

        document.querySelectorAll('.uniselv-tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.uniselv-tab-content').forEach(c => c.classList.remove('active'));

        btn.classList.add('active');
        content.classList.add('active');
        const mobileSelect = document.getElementById('uniselv-mobile-section');
        if (mobileSelect) mobileSelect.value = resolved;

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
            } else if (resolved === 'health') {
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
            } else if (resolved === 'snapshots') {
                this.loadEnduserSnapshotsIndex();
            } else if (resolved === 'notifications') {
                this.loadEnduserNotifications();
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

    refreshLiveTelemetry: function() {
        if (!this.isLiveTelemetryVisible()) return;
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
        const dotClass = stale ? 'dot-danger' : 'dot-normal';
        if (stale) el.classList.add('badge-stale');
        else el.classList.remove('badge-stale');
        const msg = failed ? 'Telemetry Offline (values retained)' :
            (age === null ? 'Waiting for telemetry sample...' : `${stale ? 'Stale Telemetry' : 'Live Telemetry'}: ${age}s ago (refresh: 10s)`);
        el.innerHTML = `<span class="uniselv-live-dot ${dotClass}"></span> <span>${msg}</span>`;
        el.setAttribute('role', stale ? 'alert' : 'status');
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

        updateGaugeCard: function(cardType, percent) {
        const validPct = Math.max(0, Math.min(100, parseFloat(percent) || 0));
        const arc = document.getElementById('uniselv-arc-' + cardType);
        if (arc) {
            arc.style.strokeDashoffset = 477.5 * (1 - validPct / 100);
        }
        const thumb = document.getElementById('uniselv-thumb-rot-' + cardType);
        if (thumb) {
            thumb.style.transform = `rotate(${validPct * 3.6}deg)`;
        }
        const wave = document.getElementById('uniselv-wave-' + cardType);
        if (wave) {
            // Full 0% to 100% dynamic height - at 100% fills completely to the top
            const waveHeight = validPct <= 0 ? 0 : Math.max(6, Math.min(100, validPct));
            wave.style.height = `${waveHeight}%`;
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

    updateAdminSparkline: function(wrapId, val) {
        const wrap = document.getElementById(wrapId);
        if (!wrap) return;
        if (!this.adminSparkSamples) this.adminSparkSamples = {};
        if (!this.adminSparkSamples[wrapId]) {
            const initVal = parseFloat(val) || 20;
            this.adminSparkSamples[wrapId] = [
                { t: Date.now() - 30000, v: Math.max(5, initVal * 0.9) },
                { t: Date.now() - 20000, v: Math.max(5, initVal * 1.05) },
                { t: Date.now() - 10000, v: Math.max(5, initVal * 0.95) }
            ];
        }
        const arr = this.adminSparkSamples[wrapId];
        arr.push({ t: Date.now(), v: parseFloat(val) || 0 });
        if (arr.length > 20) arr.shift();
        if (arr.length < 2) return;
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
            if (document.getElementById('storage-bar-fill')) document.getElementById('storage-bar-fill').style.width = Math.min(100, st.used_percent || 0) + '%';
            if (document.getElementById('storage-used-pct')) document.getElementById('storage-used-pct').innerText = (st.used_percent || 0) + '%';
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

    renderChartsToContainer: function(chartContainer, points) {
        chartContainer.innerHTML = '';
        const cpuData = points.map(p => ({ x: Number(p.t) || 0, y: Number(p.cpu) || 0, limit: Number(p.limit_cpu) || 0 }));
        chartContainer.appendChild(this.renderSvgChart('CPU Usage (% Core Equivalent)', cpuData, '%', '#2563eb'));

        const memData = points.map(p => ({ x: Number(p.t) || 0, y: Math.round((Number(p.mem) || 0) / 1024 / 1024), limit: Math.round((Number(p.limit_mem) || 0) / 1024 / 1024) }));
        chartContainer.appendChild(this.renderSvgChart('Memory Usage (MiB Accounted)', memData, 'MiB', '#059669'));

        const taskData = points.map(p => ({ x: Number(p.t) || 0, y: Number(p.tasks) || 0, limit: Number(p.limit_tasks) || 0 }));
        chartContainer.appendChild(this.renderSvgChart('Active Tasks & Threads', taskData, 'tasks', '#7c3aed'));

        const ioData = points.map(p => ({ x: Number(p.t) || 0, y: Math.round(((Number(p.read_bw) || 0) + (Number(p.write_bw) || 0)) / 1024), limit: 0 }));
        chartContainer.appendChild(this.renderSvgChart('Total Disk Throughput (KiB/s)', ioData, 'KiB/s', '#d97706'));
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

        if (totalTbody) totalTbody.innerHTML = '<tr><td colspan="4" style="text-align:center; color:#64748b; padding:20px;">Loading account totals...</td></tr>';
        if (gridEl) gridEl.innerHTML = '<div style="grid-column: 1 / -1; text-align:center; color:#64748b; padding:40px; background:#fff; border:1px solid var(--uniselv-border); border-radius:8px;">Loading resource charts...</div>';
        if (rollupTbody) rollupTbody.innerHTML = '<tr><td colspan="20" style="text-align:center; color:#64748b; padding:24px;">Loading hourly usage records...</td></tr>';

        this.callApi('history', { range: timeframe, username: this.currentUser }, (err, res) => {
            if (err || res.error) {
                if (gridEl) gridEl.innerHTML = `<div style="grid-column: 1 / -1; color:#b91c1c; padding:20px; background:#fff; border-radius:8px;">Error loading telemetry: ${err || res.error}</div>`;
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
                    gridEl.appendChild(this.renderUsage8Chart('CPU (SPEED)', cpuData, '%', '#2563eb', `Plotted avg: ${cpuAvg}% | max: ${cpuMax}%`));

                    // Chart 2: Virtual memory (RAM + Swap)
                    const vmemData = pts.map(p => ({ x: p.t, y: p.vmem, limit: p.limit_vmem }));
                    const vmemMax = Math.max(...vmemData.map(p => p.y)).toFixed(1);
                    gridEl.appendChild(this.renderUsage8Chart('Virtual memory (RAM + Swap)', vmemData, 'MiB', '#6366f1', `Plotted max: ${vmemMax} MiB; historical limit unavailable`));

                    // Chart 3: Physical memory
                    const pmemData = pts.map(p => ({ x: p.t, y: p.pmem, limit: p.limit_pmem }));
                    const pmemMax = Math.max(...pmemData.map(p => p.y)).toFixed(1);
                    const pmemAvg = (pmemData.reduce((s, p) => s + p.y, 0) / pmemData.length).toFixed(1);
                    gridEl.appendChild(this.renderUsage8Chart('Physical memory', pmemData, 'MiB', '#059669', `Plotted avg: ${pmemAvg} MiB | max: ${pmemMax} MiB`));

                    // Chart 4: IO
                    const ioData = pts.map(p => ({ x: p.t, y: p.io, limit: p.limit_io }));
                    const ioMax = Math.max(...ioData.map(p => p.y)).toFixed(1);
                    gridEl.appendChild(this.renderUsage8Chart('IO', ioData, 'KiB/s', '#d97706', `Plotted max: ${ioMax} KiB/s`));

                    // Chart 5: IOPS
                    const iopsData = pts.map(p => ({ x: p.t, y: p.iops, limit: p.limit_iops }));
                    const iopsMax = Math.max(...iopsData.map(p => p.y)).toFixed(0);
                    gridEl.appendChild(this.renderUsage8Chart('IOPS', iopsData, 'iops', '#0891b2', `Max: ${iopsMax} iops`));

                    // Chart 6: Entry processes
                    const epData = pts.map(p => ({ x: p.t, y: p.ep, limit: p.limit_ep }));
                    const hasEp = pts.some(p => p.ep !== null && p.ep !== undefined);
                    const epStat = hasEp ? `Max: ${Math.max(...epData.filter(p => p.y !== null).map(p => p.y)).toFixed(1)} EP` : 'N/A (Governed via NPROC)';
                    gridEl.appendChild(this.renderUsage8Chart('Entry processes', epData, 'EP', '#7c3aed', epStat));

                    // Chart 7: Processes
                    const nprocData = pts.map(p => ({ x: p.t, y: p.nproc, limit: p.limit_nproc }));
                    const nprocMax = Math.max(...nprocData.map(p => p.y));
                    gridEl.appendChild(this.renderUsage8Chart('Processes', nprocData, 'procs', '#4f46e5', `Max: ${nprocMax}`));

                    // Chart 8: Faults
                    const faultData = pts.map(p => ({ x: p.t, y: p.faults, limit: 0 }));
                    const faultTot = faultData.reduce((s, p) => s + p.y, 0);
                    gridEl.appendChild(this.renderUsage8Chart('Faults', faultData, 'events', '#dc2626', `Total: ${faultTot} events`));
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

        this.callApi('history', { range: range, username: this.currentUser }, (err, res) => {
            if (err || res.error) {
                chartContainer.innerHTML = `<div class="uniselv-card" style="color: #b91c1c;">Failed to load history: ${err || res.error}</div>`;
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

        if (totalTbody) totalTbody.innerHTML = '<tr><td colspan="4" style="text-align:center; color:#64748b; padding:20px;">Loading account totals for ' + this.escapeHtml(targetUser) + '...</td></tr>';
        if (gridEl) gridEl.innerHTML = '<div style="grid-column: 1 / -1; text-align:center; color:#64748b; padding:40px; background:#fff; border:1px solid var(--uniselv-border); border-radius:8px;">Loading 8 resource telemetry charts...</div>';
        if (rollupTbody) rollupTbody.innerHTML = '<tr><td colspan="20" style="text-align:center; color:#64748b; padding:24px;">Loading hourly usage records...</td></tr>';

        this.callApi('history', { range: timeframe, username: targetUser }, (err, res) => {
            if (err || res.error) {
                if (gridEl) gridEl.innerHTML = `<div style="grid-column: 1 / -1; color:#b91c1c; padding:20px; background:#fff; border-radius:8px;">Error loading telemetry: ${err || res.error}</div>`;
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
                    gridEl.appendChild(this.renderUsage8Chart('CPU (SPEED)', cpuData, '%', '#2563eb', `Plotted avg: ${cpuAvg}% | max: ${cpuMax}%`));

                    // Chart 2: Virtual memory (RAM + Swap)
                    const vmemData = pts.map(p => ({ x: p.t, y: p.vmem, limit: p.limit_vmem }));
                    const vmemMax = Math.max(...vmemData.map(p => p.y)).toFixed(1);
                    gridEl.appendChild(this.renderUsage8Chart('Virtual memory (RAM + Swap)', vmemData, 'MiB', '#6366f1', `Plotted max: ${vmemMax} MiB; historical limit unavailable`));

                    // Chart 3: Physical memory
                    const pmemData = pts.map(p => ({ x: p.t, y: p.pmem, limit: p.limit_pmem }));
                    const pmemMax = Math.max(...pmemData.map(p => p.y)).toFixed(1);
                    const pmemAvg = (pmemData.reduce((s, p) => s + p.y, 0) / pmemData.length).toFixed(1);
                    gridEl.appendChild(this.renderUsage8Chart('Physical memory', pmemData, 'MiB', '#059669', `Plotted avg: ${pmemAvg} MiB | max: ${pmemMax} MiB`));

                    // Chart 4: IO
                    const ioData = pts.map(p => ({ x: p.t, y: p.io, limit: p.limit_io }));
                    const ioMax = Math.max(...ioData.map(p => p.y)).toFixed(1);
                    gridEl.appendChild(this.renderUsage8Chart('IO', ioData, 'KiB/s', '#d97706', `Plotted max: ${ioMax} KiB/s`));

                    // Chart 5: IOPS
                    const iopsData = pts.map(p => ({ x: p.t, y: p.iops, limit: p.limit_iops }));
                    const iopsMax = Math.max(...iopsData.map(p => p.y)).toFixed(0);
                    gridEl.appendChild(this.renderUsage8Chart('IOPS', iopsData, 'iops', '#0891b2', `Max: ${iopsMax} iops`));

                    // Chart 6: Entry processes
                    const epData = pts.map(p => ({ x: p.t, y: p.ep, limit: p.limit_ep }));
                    const hasEp = pts.some(p => p.ep !== null && p.ep !== undefined);
                    const epStat = hasEp ? `Max: ${Math.max(...epData.filter(p => p.y !== null).map(p => p.y)).toFixed(1)} EP` : 'N/A (Governed via NPROC)';
                    gridEl.appendChild(this.renderUsage8Chart('Entry processes', epData, 'EP', '#7c3aed', epStat));

                    // Chart 7: Processes
                    const nprocData = pts.map(p => ({ x: p.t, y: p.nproc, limit: p.limit_nproc }));
                    const nprocMax = Math.max(...nprocData.map(p => p.y));
                    gridEl.appendChild(this.renderUsage8Chart('Processes', nprocData, 'procs', '#4f46e5', `Max: ${nprocMax}`));

                    // Chart 8: Faults
                    const faultData = pts.map(p => ({ x: p.t, y: p.faults, limit: 0 }));
                    const faultTot = faultData.reduce((s, p) => s + p.y, 0);
                    gridEl.appendChild(this.renderUsage8Chart('Faults', faultData, 'events', '#dc2626', `Total: ${faultTot} events`));
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

        this.callApi('processes', { username: targetUser }, (err, res) => {
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
            text.setAttribute('fill', '#94a3b8');
            text.textContent = gridVal;
            svg.appendChild(text);
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

        this.callApi('snapshots_index', params, (err, res) => {
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

        this.callApi('snapshot_detail', { username: username, snapshot_id: snapId }, (err, res) => {
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
        pageItems.forEach(e => {
            const badge = (e.severity === 'critical') ? 'badge-critical' : ((e.severity === 'warning') ? 'badge-warning' : 'badge-normal');
            const st = (e.status || 'unread').toLowerCase();
            const statusBadge = (st === 'unread')
                ? '<span class="uniselv-badge badge-warning">UNREAD</span>'
                : ((st === 'dismissed') ? '<span class="uniselv-badge badge-outline">DISMISSED</span>' : '<span class="uniselv-badge badge-normal">READ</span>');

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

            const dt = new Date(e.timestamp * 1000).toLocaleString();
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
                    if (err || res.error) {
                        UniselvNotify.error(`Sync failed: ${err || res.error}`);
                    } else {
                        UniselvNotify.success(`Successfully synchronized ${res.synced_plans.length} native resource plans.`);
                        setTimeout(() => location.reload(), 1200);
                    }
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
            const hwCpuEl = document.getElementById('admin-card-hw-cpu');
            if (hwCpuEl && (host.cpu_cores || host.cpu_count)) {
                hwCpuEl.textContent = (host.cpu_cores || host.cpu_count) + ' vCPUs';
            }
            const hwRamEl = document.getElementById('admin-card-hw-ram');
            if (hwRamEl && (host.total_ram_formatted || host.mem_total_formatted)) {
                hwRamEl.textContent = 'Physical RAM: ' + (host.total_ram_formatted || host.mem_total_formatted);
            }

            // 2. Shared CPU Headroom
            const cpuHeadroomEl = document.getElementById('admin-card-cpu-headroom');
            if (cpuHeadroomEl) {
                const cCpu = shield.customer_cpu_percent ?? calc.customerCpuPercent ?? 'Unavailable';
                cpuHeadroomEl.textContent = cCpu + '% Hosting';
            }
            const cpuSubEl = document.getElementById('admin-card-cpu-sub');
            if (cpuSubEl) {
                const rCpu = shield.reserved_cpu_percent ?? calc.reservedCpuPercent ?? 'Unavailable';
                cpuSubEl.textContent = rCpu + '% System Headroom (No fixed core dedicated)';
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
            const load1El = document.getElementById('admin-card-load-1');
            if (load1El && host.load1 !== undefined && host.load1 !== null) {
                load1El.textContent = Number(host.load1).toFixed(2);
            }
            const loadSubEl = document.getElementById('admin-card-load-sub');
            if (loadSubEl && host.load5 !== undefined && host.load15 !== undefined) {
                loadSubEl.textContent = '5m: ' + Number(host.load5).toFixed(2) + ' | 15m: ' + Number(host.load15).toFixed(2);
            }
            // Update Admin Gauges & Dynamic Live Footers
            if (typeof this.updateGaugeCard === 'function') {
                const cores = host.cpu_cores || host.cpu_count || 4;
                const load1 = (host.load1 !== undefined && host.load1 !== null) ? parseFloat(host.load1) : 1.0;
                const loadPct = Math.min(100, Math.max(5, (load1 / cores) * 100));
                const cCpuPct = shield.customer_cpu_percent ?? calc.customerCpuPercent ?? 85;
                const ramPct = shield.golden_mem_percent || 45;

                this.updateGaugeCard('admin-hw', 60);
                this.updateGaugeCard('admin-cpu', cCpuPct);
                this.updateGaugeCard('admin-ram', ramPct);
                this.updateGaugeCard('admin-load', loadPct);

                // Update Dynamic Footers (Sparklines & Equalizers)
                if (typeof this.updateAdminSparkline === 'function') {
                    this.updateAdminSparkline('admin-sparkline-hw', loadPct);
                    this.updateAdminSparkline('admin-sparkline-cpu', cCpuPct);
                }
                if (typeof this.updateEqualizer === 'function') {
                    this.updateEqualizer('admin-eq-ram', ramPct, true);
                    this.updateEqualizer('admin-eq-load', loadPct, true);
                }
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
            if (cpuSoldSub) cpuSoldSub.textContent = `Sold: ${sold.total_sold_cpu_pct || 0}% across ${res.total_accounts || 0} accounts`;

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
                body.innerHTML = '<tr><td colspan="7" style="text-align: center; color: #64748b; padding: 30px;">No scheduled reports stored yet. Click "Dispatch Report Now" to trigger immediate evaluation.</td></tr>';
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
                    <td><span class="uniselv-badge badge-normal">${r.status || 'stored'}</span></td>
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
                UniselvNotify.error(`Dispatch failed: ${err || res.error}`);
                return;
            }
            UniselvNotify.success(`Report #${res.report_id} generated and dispatched successfully.`);
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
                console.error("Failed to load report schedule:", err || res.error);
                return;
            }
            const cadenceSel = document.getElementById('report-schedule-cadence');
            if (cadenceSel && res.schedule) {
                cadenceSel.value = res.schedule;
            }
            const recipInput = document.getElementById('report-schedule-recipient');
            if (recipInput && res.recipient) {
                recipInput.value = res.recipient;
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
        const recipient = (document.getElementById('report-schedule-recipient') || {}).value || 'system_admin';

        this.callApi('save_report_schedule', { schedule: cadence, recipient: recipient }, (err, res) => {
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
    }
};

if (typeof window !== 'undefined') {
    window.UniselvResMan = UniselvResMan;
}

