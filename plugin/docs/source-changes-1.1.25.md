# Exact source changes — 1.1.25

Already-applied release source changes relative to 1.1.24; not extra post-install paste steps. Prefer the reviewed complete package.

- Back up existing files and ownership/restoration manifests together.
- Use UTF-8/LF. Replace existing files; do not append duplicate imports, functions or directives. New files start at their first line and end at their final line.
- Install through the reviewed privileged deployment workflow. Restore root ownership and installer execution modes.
- Run Python/PHP/JavaScript syntax, regression, service/API/HTTP and ZIP closure checks. Configuration values and full workload/lifecycle readiness remain distinct.

## uniselv-resman/agent/ipc_server.py

Installed paths: /usr/local/webuzo/plugins/uniselv-resman/agent/ipc_server.py; ALSO /usr/local/uniselv-resman/agent/ipc_server.py

Replace the full file; never append duplicate functions/directives. New files run from first through final line.

### Block 1 — insert

Existing anchor AFTER which:
```text
        except (OSError, ValueError):
            aggregate_mem = None
```

Existing anchor BEFORE which:
```text
        gs_status['golden_mem_current_bytes'] = aggregate_mem
        gs_status['golden_mem_current_formatted'] = format_bytes(aggregate_mem) if aggregate_mem is not None else 'Unavailable'
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
        try:
            aggregate_max = int(pathlib.Path('/sys/fs/cgroup/golden.slice/memory.max').read_text().strip())
        except (OSError, ValueError):
            aggregate_max = None
        gs_status['golden_mem_max_bytes'] = aggregate_max
        gs_status['golden_mem_percent'] = aggregate_mem / aggregate_max * 100 if aggregate_mem is not None and aggregate_max is not None and aggregate_max > 0 else None
        if aggregate_max is not None: gs_status['golden_mem_max_formatted'] = format_bytes(aggregate_max)
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
        except (OSError, ValueError):
            aggregate_mem = None
        try:
            aggregate_max = int(pathlib.Path('/sys/fs/cgroup/golden.slice/memory.max').read_text().strip())
        except (OSError, ValueError):
            aggregate_max = None
        gs_status['golden_mem_max_bytes'] = aggregate_max
        gs_status['golden_mem_percent'] = aggregate_mem / aggregate_max * 100 if aggregate_mem is not None and aggregate_max is not None and aggregate_max > 0 else None
        if aggregate_max is not None: gs_status['golden_mem_max_formatted'] = format_bytes(aggregate_max)
        gs_status['golden_mem_current_bytes'] = aggregate_mem
        gs_status['golden_mem_current_formatted'] = format_bytes(aggregate_mem) if aggregate_mem is not None else 'Unavailable'
```

## uniselv-resman/assets/app.js

Installed paths: /usr/local/webuzo/plugins/uniselv-resman/assets/app.js

Replace the full file; never append duplicate functions/directives. New files run from first through final line.

### Block 1 — replace

Existing anchor AFTER which:
```text
    },

```

Existing anchor BEFORE which:
```text
        const arc = document.getElementById('uniselv-arc-' + cardType);
        if (arc) {
```

Existing content to replace/remove (not copied):
```text
        updateGaugeCard: function(cardType, percent) {
        const validPct = Math.max(0, Math.min(100, parseFloat(percent) || 0));
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
    metricNumber: function(value) {
        if (!['number','string'].includes(typeof value) || (typeof value==='string' && value.trim()==='')) return null;
        const number = Number(value);
        return Number.isFinite(number) ? number : null;
    },

    adminGaugePercentages: function(host, shield) {
        const calc = shield.configured_policy || {};
        const cores = this.metricNumber(host.cpu_cores ?? host.cpu_count);
        const quota = this.metricNumber(shield.customer_cpu_percent ?? calc.customerCpuPercent);
        const load = this.metricNumber(host.load1);
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
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
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
        const load = this.metricNumber(host.load1);
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
```

### Block 2 — replace

Existing anchor AFTER which:
```text
        const arc = document.getElementById('uniselv-arc-' + cardType);
        if (arc) {
```

Existing anchor BEFORE which:
```text
        }
        const thumb = document.getElementById('uniselv-thumb-rot-' + cardType);
```

Existing content to replace/remove (not copied):
```text
            arc.style.strokeDashoffset = 477.5 * (1 - validPct / 100);
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
            // SVG pathLength normalizes circle circumference to 100 units.
            arc.setAttribute('pathLength','100');
            arc.setAttribute('stroke-dasharray','100');
            arc.style.strokeDashoffset = String(100-validPct);
            arc.style.opacity = known && validPct>0 ? '1' : '0';
            arc.dataset.percent = known ? String(validPct) : '';
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
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
```

### Block 3 — replace

Existing anchor AFTER which:
```text
        const thumb = document.getElementById('uniselv-thumb-rot-' + cardType);
        if (thumb) {
```

Existing anchor BEFORE which:
```text
        }
        const wave = document.getElementById('uniselv-wave-' + cardType);
```

Existing content to replace/remove (not copied):
```text
            thumb.style.transform = `rotate(${validPct * 3.6}deg)`;
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
            thumb.style.transform = `rotate(${validPct*3.6}deg)`;
            thumb.style.opacity = known && validPct>0 ? '1':'0';
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
        const thumb = document.getElementById('uniselv-thumb-rot-' + cardType);
        if (thumb) {
            thumb.style.transform = `rotate(${validPct*3.6}deg)`;
            thumb.style.opacity = known && validPct>0 ? '1':'0';
        }
        const wave = document.getElementById('uniselv-wave-' + cardType);
```

### Block 4 — replace

Existing anchor AFTER which:
```text
        }
        const wave = document.getElementById('uniselv-wave-' + cardType);
```

Existing anchor BEFORE which:
```text
        }
    },
```

Existing content to replace/remove (not copied):
```text
        if (wave) {
            // Full 0% to 100% dynamic height - at 100% fills completely to the top
            const waveHeight = validPct <= 0 ? 0 : Math.max(6, Math.min(100, validPct));
            wave.style.height = `${waveHeight}%`;
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
        if (wave) wave.style.height = `${validPct}%`;
        const wrap = arc?.closest('.uniselv-gauge-wrap');
        if (wrap) {
            wrap.dataset.metricState = known ? 'measured':'unavailable';
            wrap.title = known ? `${number.toFixed(1)}% of this metric boundary${number>100 ? ' (visual fill capped at 100%)':''}` : 'No usage percentage is represented.';
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
        }
        const wave = document.getElementById('uniselv-wave-' + cardType);
        if (wave) wave.style.height = `${validPct}%`;
        const wrap = arc?.closest('.uniselv-gauge-wrap');
        if (wrap) {
            wrap.dataset.metricState = known ? 'measured':'unavailable';
            wrap.title = known ? `${number.toFixed(1)}% of this metric boundary${number>100 ? ' (visual fill capped at 100%)':''}` : 'No usage percentage is represented.';
        }
    },
```

### Block 5 — replace

Existing anchor AFTER which:
```text
    },

```

Existing anchor BEFORE which:
```text
        const minVal = Math.min(...arr.map(p => p.v));
        const maxVal = Math.max(1, ...arr.map(p => p.v));
```

Existing content to replace/remove (not copied):
```text
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
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
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
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
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
```

### Block 6 — replace

Existing anchor AFTER which:
```text
            // Update Admin Gauges & Dynamic Live Footers
            if (typeof this.updateGaugeCard === 'function') {
```

Existing anchor BEFORE which:
```text
                // Update Dynamic Footers (Sparklines & Equalizers)
                if (typeof this.updateAdminSparkline === 'function') {
```

Existing content to replace/remove (not copied):
```text
                const cores = host.cpu_cores || host.cpu_count || 4;
                const load1 = (host.load1 !== undefined && host.load1 !== null) ? parseFloat(host.load1) : 1.0;
                const loadPct = Math.min(100, Math.max(5, (load1 / cores) * 100));
                const cCpuPct = shield.customer_cpu_percent ?? calc.customerCpuPercent ?? 85;
                const ramPct = shield.golden_mem_percent || 45;

                this.updateGaugeCard('admin-hw', 60);
                this.updateGaugeCard('admin-cpu', cCpuPct);
                this.updateGaugeCard('admin-ram', ramPct);
                this.updateGaugeCard('admin-load', loadPct);

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                const metrics = this.adminGaugePercentages(host,shield);
                const loadPct=metrics.load, cCpuPct=metrics.cpu, ramPct=metrics.ram;
                this.updateGaugeCard('admin-hw',null);
                this.updateGaugeCard('admin-cpu',cCpuPct);
                this.updateGaugeCard('admin-ram',ramPct);
                this.updateGaugeCard('admin-load',loadPct);
                const cpuGauge=document.getElementById('uniselv-arc-admin-cpu')?.closest('.uniselv-gauge-wrap');
                if(cpuGauge && cCpuPct!==null)cpuGauge.title=`Configured hosting allocation: ${cCpuPct.toFixed(1)}% of total visible CPU capacity. This is a policy share, not live CPU usage.`;
                const loadGauge=document.getElementById('uniselv-arc-admin-load')?.closest('.uniselv-gauge-wrap');
                if(loadGauge && loadPct!==null)loadGauge.title=`One-minute load divided by vCPU count: ${loadPct.toFixed(1)}%. Load is not CPU utilization; visual fill is capped at 100%.`;
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
            // Update Admin Gauges & Dynamic Live Footers
            if (typeof this.updateGaugeCard === 'function') {
                const metrics = this.adminGaugePercentages(host,shield);
                const loadPct=metrics.load, cCpuPct=metrics.cpu, ramPct=metrics.ram;
                this.updateGaugeCard('admin-hw',null);
                this.updateGaugeCard('admin-cpu',cCpuPct);
                this.updateGaugeCard('admin-ram',ramPct);
                this.updateGaugeCard('admin-load',loadPct);
                const cpuGauge=document.getElementById('uniselv-arc-admin-cpu')?.closest('.uniselv-gauge-wrap');
                if(cpuGauge && cCpuPct!==null)cpuGauge.title=`Configured hosting allocation: ${cCpuPct.toFixed(1)}% of total visible CPU capacity. This is a policy share, not live CPU usage.`;
                const loadGauge=document.getElementById('uniselv-arc-admin-load')?.closest('.uniselv-gauge-wrap');
                if(loadGauge && loadPct!==null)loadGauge.title=`One-minute load divided by vCPU count: ${loadPct.toFixed(1)}%. Load is not CPU utilization; visual fill is capped at 100%.`;
                // Update Dynamic Footers (Sparklines & Equalizers)
                if (typeof this.updateAdminSparkline === 'function') {
```

### Block 7 — replace

Existing anchor AFTER which:
```text
                // Update Dynamic Footers (Sparklines & Equalizers)
                if (typeof this.updateAdminSparkline === 'function') {
```

Existing anchor BEFORE which:
```text
                }
                if (typeof this.updateEqualizer === 'function') {
```

Existing content to replace/remove (not copied):
```text
                    this.updateAdminSparkline('admin-sparkline-hw', loadPct);
                    this.updateAdminSparkline('admin-sparkline-cpu', cCpuPct);
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                    this.updateAdminSparkline('admin-sparkline-hw', loadPct,host.last_sample_epoch);
                    this.updateAdminSparkline('admin-sparkline-cpu', cCpuPct,host.last_sample_epoch);
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                // Update Dynamic Footers (Sparklines & Equalizers)
                if (typeof this.updateAdminSparkline === 'function') {
                    this.updateAdminSparkline('admin-sparkline-hw', loadPct,host.last_sample_epoch);
                    this.updateAdminSparkline('admin-sparkline-cpu', cCpuPct,host.last_sample_epoch);
                }
                if (typeof this.updateEqualizer === 'function') {
```

## uniselv-resman/assets/style.css

Installed paths: /usr/local/webuzo/plugins/uniselv-resman/assets/style.css

Replace the full file; never append duplicate functions/directives. New files run from first through final line.

### Block 1 — insert

Existing anchor AFTER which:
```text
#uniselv-runtime-governance p,.uniselv-governance-note{overflow-wrap:anywhere;font-size:.9rem;line-height:1.6}
#uniselv-runtime-governance td{white-space:normal;overflow-wrap:anywhere;max-width:420px;min-width:100px}
```

Existing anchor BEFORE which:
```text
<END OF FILE>
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text

/* Liquid level represents the actual percentage; waves decorate only its surface. */
.uniselv-wave-container .uniselv-wave{top:0;bottom:auto;height:10px}
.theme-cpu .uniselv-wave-container{background:rgba(59,130,246,.18)}
.theme-mem .uniselv-wave-container{background:rgba(139,92,246,.18)}
.theme-io .uniselv-wave-container{background:rgba(16,185,129,.18)}
.theme-tasks .uniselv-wave-container{background:rgba(245,158,11,.18)}
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
#uniselv-runtime-governance p,.uniselv-governance-note{overflow-wrap:anywhere;font-size:.9rem;line-height:1.6}
#uniselv-runtime-governance td{white-space:normal;overflow-wrap:anywhere;max-width:420px;min-width:100px}

/* Liquid level represents the actual percentage; waves decorate only its surface. */
.uniselv-wave-container .uniselv-wave{top:0;bottom:auto;height:10px}
.theme-cpu .uniselv-wave-container{background:rgba(59,130,246,.18)}
.theme-mem .uniselv-wave-container{background:rgba(139,92,246,.18)}
.theme-io .uniselv-wave-container{background:rgba(16,185,129,.18)}
.theme-tasks .uniselv-wave-container{background:rgba(245,158,11,.18)}
```

## uniselv-resman/info.json

Installed paths: /usr/local/webuzo/plugins/uniselv-resman/info.json

Replace the full file; never append duplicate functions/directives. New files run from first through final line.

### Block 1 — replace

Existing anchor AFTER which:
```text
  "name": "UNISELV Resource Manager",
  "slug": "uniselv-resman",
```

Existing anchor BEFORE which:
```text
  "author": "<a href=\"https://refat.ovh\" target=\"_blank\">Refat Rahman</a>",
  "developer": {
```

Existing content to replace/remove (not copied):
```text
  "version": "1.1.24",
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
  "version": "1.1.25",
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
  "name": "UNISELV Resource Manager",
  "slug": "uniselv-resman",
  "version": "1.1.25",
  "author": "<a href=\"https://refat.ovh\" target=\"_blank\">Refat Rahman</a>",
  "developer": {
```

## uniselv-resman/uniselv-resman.php

Installed paths: /usr/local/webuzo/plugins/uniselv-resman/uniselv-resman.php

Replace the full file; never append duplicate functions/directives. New files run from first through final line.

### Block 1 — replace

Existing anchor AFTER which:
```text
/*
Plugin Name: UNISELV Resource Manager
```

Existing anchor BEFORE which:
```text
Description: Enterprise Resource Management, Cgroups v2 Isolation, Real-Time Monitoring & Telemetry for Webuzo.
Author: Refat Rahman
```

Existing content to replace/remove (not copied):
```text
Version: 1.1.24
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
Version: 1.1.25
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
/*
Plugin Name: UNISELV Resource Manager
Version: 1.1.25
Description: Enterprise Resource Management, Cgroups v2 Isolation, Real-Time Monitoring & Telemetry for Webuzo.
Author: Refat Rahman
```

### Block 2 — replace

Existing anchor AFTER which:
```text
    $i18n_dict = uniselv_get_i18n_dict();

```

Existing anchor BEFORE which:
```text
    echo '<style>:root { --uniselv-primary: ' . $brand_color . '; --primary-color: ' . $brand_color . '; }</style>';
    echo '<script>
```

Existing content to replace/remove (not copied):
```text
    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '-1.1.24r2' . '">';
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '-1.1.25r2' . '">';
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
    $i18n_dict = uniselv_get_i18n_dict();

    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '-1.1.25r2' . '">';
    echo '<style>:root { --uniselv-primary: ' . $brand_color . '; --primary-color: ' . $brand_color . '; }</style>';
    echo '<script>
```

### Block 3 — replace

Existing anchor AFTER which:
```text
window.UNISELV_TRANSLATIONS = ' . json_encode($i18n_dict[$locale] ?? $i18n_dict['en']) . ';
</script>';
```

Existing anchor BEFORE which:
```text

    echo '<div class="uniselv-container">';
```

Existing content to replace/remove (not copied):
```text
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '-1.1.24r2' . '"></script>';
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '-1.1.25r2' . '"></script>';
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
window.UNISELV_TRANSLATIONS = ' . json_encode($i18n_dict[$locale] ?? $i18n_dict['en']) . ';
</script>';
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '-1.1.25r2' . '"></script>';

    echo '<div class="uniselv-container">';
```

### Block 4 — replace

Existing anchor AFTER which:
```text
                    <circle class="uniselv-gauge-ticks" fill="none" cx="100" cy="100" r="86" />
                    <circle class="uniselv-gauge-track" fill="none" cx="100" cy="100" r="76" />
```

Existing anchor BEFORE which:
```text
                        <circle cx="100" cy="24" r="5" fill="#3b82f6"/>
                    </g>
```

Existing content to replace/remove (not copied):
```text
                    <circle class="uniselv-gauge-arc arc-cpu" id="uniselv-arc-admin-hw" fill="none" cx="100" cy="100" r="76" stroke-dasharray="477.5" stroke-dashoffset="190" transform="rotate(-90 100 100)" />
                    <g class="uniselv-gauge-thumb-rot" id="uniselv-thumb-rot-admin-hw" style="transform: rotate(216deg);">
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                    <circle class="uniselv-gauge-arc arc-cpu" id="uniselv-arc-admin-hw" fill="none" cx="100" cy="100" r="76" pathLength="100" stroke-dasharray="100" stroke-dashoffset="100" transform="rotate(-90 100 100)" />
                    <g class="uniselv-gauge-thumb-rot" id="uniselv-thumb-rot-admin-hw" style="opacity:0; transform: rotate(0deg);">
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                    <circle class="uniselv-gauge-ticks" fill="none" cx="100" cy="100" r="86" />
                    <circle class="uniselv-gauge-track" fill="none" cx="100" cy="100" r="76" />
                    <circle class="uniselv-gauge-arc arc-cpu" id="uniselv-arc-admin-hw" fill="none" cx="100" cy="100" r="76" pathLength="100" stroke-dasharray="100" stroke-dashoffset="100" transform="rotate(-90 100 100)" />
                    <g class="uniselv-gauge-thumb-rot" id="uniselv-thumb-rot-admin-hw" style="opacity:0; transform: rotate(0deg);">
                        <circle cx="100" cy="24" r="5" fill="#3b82f6"/>
                    </g>
```

### Block 5 — replace

Existing anchor AFTER which:
```text
                <div class="uniselv-particles"><span class="particle p-1"></span><span class="particle p-2"></span><span class="particle p-3"></span></div>
                <div class="uniselv-liquid-circle">
```

Existing anchor BEFORE which:
```text
                        <div class="uniselv-wave wave-back"></div>
                        <div class="uniselv-wave wave-front"></div>
```

Existing content to replace/remove (not copied):
```text
                    <div class="uniselv-wave-container" id="uniselv-wave-admin-hw" style="height: 52%;">
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                    <div class="uniselv-wave-container" id="uniselv-wave-admin-hw" style="height: 0%;">
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                <div class="uniselv-particles"><span class="particle p-1"></span><span class="particle p-2"></span><span class="particle p-3"></span></div>
                <div class="uniselv-liquid-circle">
                    <div class="uniselv-wave-container" id="uniselv-wave-admin-hw" style="height: 0%;">
                        <div class="uniselv-wave wave-back"></div>
                        <div class="uniselv-wave wave-front"></div>
```

### Block 6 — replace

Existing anchor AFTER which:
```text
                    <div class="uniselv-gauge-center">
                        <span class="uniselv-metric-big" id="admin-card-hw-cpu">' . $cpu_cores . ' vCPUs</span>
```

Existing anchor BEFORE which:
```text
                    </div>
                </div>
```

Existing content to replace/remove (not copied):
```text
                        <span class="uniselv-metric-core">Virtual CPUs</span>
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                        <span class="uniselv-metric-core">Virtual CPUs · inventory</span>
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                    <div class="uniselv-gauge-center">
                        <span class="uniselv-metric-big" id="admin-card-hw-cpu">' . $cpu_cores . ' vCPUs</span>
                        <span class="uniselv-metric-core">Virtual CPUs · inventory</span>
                    </div>
                </div>
```

### Block 7 — replace

Existing anchor AFTER which:
```text
                    <circle class="uniselv-gauge-ticks" fill="none" cx="100" cy="100" r="86" />
                    <circle class="uniselv-gauge-track" fill="none" cx="100" cy="100" r="76" />
```

Existing anchor BEFORE which:
```text
                        <circle cx="100" cy="24" r="5" fill="#8b5cf6"/>
                    </g>
```

Existing content to replace/remove (not copied):
```text
                    <circle class="uniselv-gauge-arc arc-mem" id="uniselv-arc-admin-cpu" fill="none" cx="100" cy="100" r="76" stroke-dasharray="477.5" stroke-dashoffset="120" transform="rotate(-90 100 100)" />
                    <g class="uniselv-gauge-thumb-rot" id="uniselv-thumb-rot-admin-cpu" style="transform: rotate(270deg);">
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                    <circle class="uniselv-gauge-arc arc-mem" id="uniselv-arc-admin-cpu" fill="none" cx="100" cy="100" r="76" pathLength="100" stroke-dasharray="100" stroke-dashoffset="100" transform="rotate(-90 100 100)" />
                    <g class="uniselv-gauge-thumb-rot" id="uniselv-thumb-rot-admin-cpu" style="opacity:0; transform: rotate(0deg);">
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                    <circle class="uniselv-gauge-ticks" fill="none" cx="100" cy="100" r="86" />
                    <circle class="uniselv-gauge-track" fill="none" cx="100" cy="100" r="76" />
                    <circle class="uniselv-gauge-arc arc-mem" id="uniselv-arc-admin-cpu" fill="none" cx="100" cy="100" r="76" pathLength="100" stroke-dasharray="100" stroke-dashoffset="100" transform="rotate(-90 100 100)" />
                    <g class="uniselv-gauge-thumb-rot" id="uniselv-thumb-rot-admin-cpu" style="opacity:0; transform: rotate(0deg);">
                        <circle cx="100" cy="24" r="5" fill="#8b5cf6"/>
                    </g>
```

### Block 8 — replace

Existing anchor AFTER which:
```text
                <div class="uniselv-particles"><span class="particle p-1"></span><span class="particle p-2"></span><span class="particle p-3"></span></div>
                <div class="uniselv-liquid-circle">
```

Existing anchor BEFORE which:
```text
                        <div class="uniselv-wave wave-back"></div>
                        <div class="uniselv-wave wave-front"></div>
```

Existing content to replace/remove (not copied):
```text
                    <div class="uniselv-wave-container" id="uniselv-wave-admin-cpu" style="height: 60%;">
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                    <div class="uniselv-wave-container" id="uniselv-wave-admin-cpu" style="height: 0%;">
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                <div class="uniselv-particles"><span class="particle p-1"></span><span class="particle p-2"></span><span class="particle p-3"></span></div>
                <div class="uniselv-liquid-circle">
                    <div class="uniselv-wave-container" id="uniselv-wave-admin-cpu" style="height: 0%;">
                        <div class="uniselv-wave wave-back"></div>
                        <div class="uniselv-wave wave-front"></div>
```

### Block 9 — replace

Existing anchor AFTER which:
```text
                    <circle class="uniselv-gauge-ticks" fill="none" cx="100" cy="100" r="86" />
                    <circle class="uniselv-gauge-track" fill="none" cx="100" cy="100" r="76" />
```

Existing anchor BEFORE which:
```text
                        <circle cx="100" cy="24" r="5" fill="#10b981"/>
                    </g>
```

Existing content to replace/remove (not copied):
```text
                    <circle class="uniselv-gauge-arc arc-io" id="uniselv-arc-admin-ram" fill="none" cx="100" cy="100" r="76" stroke-dasharray="477.5" stroke-dashoffset="260" transform="rotate(-90 100 100)" />
                    <g class="uniselv-gauge-thumb-rot" id="uniselv-thumb-rot-admin-ram" style="transform: rotate(160deg);">
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                    <circle class="uniselv-gauge-arc arc-io" id="uniselv-arc-admin-ram" fill="none" cx="100" cy="100" r="76" pathLength="100" stroke-dasharray="100" stroke-dashoffset="100" transform="rotate(-90 100 100)" />
                    <g class="uniselv-gauge-thumb-rot" id="uniselv-thumb-rot-admin-ram" style="opacity:0; transform: rotate(0deg);">
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                    <circle class="uniselv-gauge-ticks" fill="none" cx="100" cy="100" r="86" />
                    <circle class="uniselv-gauge-track" fill="none" cx="100" cy="100" r="76" />
                    <circle class="uniselv-gauge-arc arc-io" id="uniselv-arc-admin-ram" fill="none" cx="100" cy="100" r="76" pathLength="100" stroke-dasharray="100" stroke-dashoffset="100" transform="rotate(-90 100 100)" />
                    <g class="uniselv-gauge-thumb-rot" id="uniselv-thumb-rot-admin-ram" style="opacity:0; transform: rotate(0deg);">
                        <circle cx="100" cy="24" r="5" fill="#10b981"/>
                    </g>
```

### Block 10 — replace

Existing anchor AFTER which:
```text
                <div class="uniselv-particles"><span class="particle p-1"></span><span class="particle p-2"></span><span class="particle p-3"></span></div>
                <div class="uniselv-liquid-circle">
```

Existing anchor BEFORE which:
```text
                        <div class="uniselv-wave wave-back"></div>
                        <div class="uniselv-wave wave-front"></div>
```

Existing content to replace/remove (not copied):
```text
                    <div class="uniselv-wave-container" id="uniselv-wave-admin-ram" style="height: 45%;">
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                    <div class="uniselv-wave-container" id="uniselv-wave-admin-ram" style="height: 0%;">
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                <div class="uniselv-particles"><span class="particle p-1"></span><span class="particle p-2"></span><span class="particle p-3"></span></div>
                <div class="uniselv-liquid-circle">
                    <div class="uniselv-wave-container" id="uniselv-wave-admin-ram" style="height: 0%;">
                        <div class="uniselv-wave wave-back"></div>
                        <div class="uniselv-wave wave-front"></div>
```

### Block 11 — replace

Existing anchor AFTER which:
```text
                    <circle class="uniselv-gauge-ticks" fill="none" cx="100" cy="100" r="86" />
                    <circle class="uniselv-gauge-track" fill="none" cx="100" cy="100" r="76" />
```

Existing anchor BEFORE which:
```text
                        <circle cx="100" cy="24" r="5" fill="#f59e0b"/>
                    </g>
```

Existing content to replace/remove (not copied):
```text
                    <circle class="uniselv-gauge-arc arc-tasks" id="uniselv-arc-admin-load" fill="none" cx="100" cy="100" r="76" stroke-dasharray="477.5" stroke-dashoffset="360" transform="rotate(-90 100 100)" />
                    <g class="uniselv-gauge-thumb-rot" id="uniselv-thumb-rot-admin-load" style="transform: rotate(88deg);">
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                    <circle class="uniselv-gauge-arc arc-tasks" id="uniselv-arc-admin-load" fill="none" cx="100" cy="100" r="76" pathLength="100" stroke-dasharray="100" stroke-dashoffset="100" transform="rotate(-90 100 100)" />
                    <g class="uniselv-gauge-thumb-rot" id="uniselv-thumb-rot-admin-load" style="opacity:0; transform: rotate(0deg);">
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                    <circle class="uniselv-gauge-ticks" fill="none" cx="100" cy="100" r="86" />
                    <circle class="uniselv-gauge-track" fill="none" cx="100" cy="100" r="76" />
                    <circle class="uniselv-gauge-arc arc-tasks" id="uniselv-arc-admin-load" fill="none" cx="100" cy="100" r="76" pathLength="100" stroke-dasharray="100" stroke-dashoffset="100" transform="rotate(-90 100 100)" />
                    <g class="uniselv-gauge-thumb-rot" id="uniselv-thumb-rot-admin-load" style="opacity:0; transform: rotate(0deg);">
                        <circle cx="100" cy="24" r="5" fill="#f59e0b"/>
                    </g>
```

### Block 12 — replace

Existing anchor AFTER which:
```text
                <div class="uniselv-particles"><span class="particle p-1"></span><span class="particle p-2"></span><span class="particle p-3"></span></div>
                <div class="uniselv-liquid-circle">
```

Existing anchor BEFORE which:
```text
                        <div class="uniselv-wave wave-back"></div>
                        <div class="uniselv-wave wave-front"></div>
```

Existing content to replace/remove (not copied):
```text
                    <div class="uniselv-wave-container" id="uniselv-wave-admin-load" style="height: 32%;">
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                    <div class="uniselv-wave-container" id="uniselv-wave-admin-load" style="height: 0%;">
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                <div class="uniselv-particles"><span class="particle p-1"></span><span class="particle p-2"></span><span class="particle p-3"></span></div>
                <div class="uniselv-liquid-circle">
                    <div class="uniselv-wave-container" id="uniselv-wave-admin-load" style="height: 0%;">
                        <div class="uniselv-wave wave-back"></div>
                        <div class="uniselv-wave wave-front"></div>
```

### Block 13 — replace

Existing anchor AFTER which:
```text
    $i18n_dict = uniselv_get_i18n_dict();

```

Existing anchor BEFORE which:
```text
    echo '<style>:root { --uniselv-primary: ' . $brand_color . '; --primary-color: ' . $brand_color . '; }</style>';
    echo '<script>
```

Existing content to replace/remove (not copied):
```text
    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '-1.1.24r2' . '">';
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '-1.1.25r2' . '">';
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
    $i18n_dict = uniselv_get_i18n_dict();

    echo '<link rel="stylesheet" href="' . $panel_url . '/uniselv-resman/assets/style.css?v=' . filemtime(__DIR__ . '/assets/style.css') . '-1.1.25r2' . '">';
    echo '<style>:root { --uniselv-primary: ' . $brand_color . '; --primary-color: ' . $brand_color . '; }</style>';
    echo '<script>
```

### Block 14 — replace

Existing anchor AFTER which:
```text
window.UNISELV_TRANSLATIONS = ' . json_encode($i18n_dict[$locale] ?? $i18n_dict['en']) . ';
</script>';
```

Existing anchor BEFORE which:
```text

    echo '<div class="uniselv-container">';
```

Existing content to replace/remove (not copied):
```text
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '-1.1.24r2' . '"></script>';
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '-1.1.25r2' . '"></script>';
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
window.UNISELV_TRANSLATIONS = ' . json_encode($i18n_dict[$locale] ?? $i18n_dict['en']) . ';
</script>';
    echo '<script src="' . $panel_url . '/uniselv-resman/assets/app.js?v=' . filemtime(__DIR__ . '/assets/app.js') . '-1.1.25r2' . '"></script>';

    echo '<div class="uniselv-container">';
```

### Block 15 — replace

Existing anchor AFTER which:
```text
                    <circle class="uniselv-gauge-ticks" fill="none" cx="100" cy="100" r="86" />
                    <circle class="uniselv-gauge-track" fill="none" cx="100" cy="100" r="76" />
```

Existing anchor BEFORE which:
```text
                    <g class="uniselv-gauge-thumb-rot" id="uniselv-thumb-rot-cpu" style="transform: rotate(' . (min(100, max(0, $cpu_allowance)) * 3.6) . 'deg);">
                        <circle cx="100" cy="24" r="5" fill="#3b82f6" filter="url(#glow-cpu)"/>
```

Existing content to replace/remove (not copied):
```text
                    <circle class="uniselv-gauge-arc arc-cpu" id="uniselv-arc-cpu" fill="none" cx="100" cy="100" r="76" stroke-dasharray="477.5" stroke-dashoffset="' . (477.5 * (1 - min(100, max(0, $cpu_allowance)) / 100)) . '" transform="rotate(-90 100 100)" />
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                    <circle class="uniselv-gauge-arc arc-cpu" id="uniselv-arc-cpu" fill="none" cx="100" cy="100" r="76" pathLength="100" stroke-dasharray="100" stroke-dashoffset="' . (100 * (1 - min(100, max(0, $cpu_allowance)) / 100)) . '" transform="rotate(-90 100 100)" />
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                    <circle class="uniselv-gauge-ticks" fill="none" cx="100" cy="100" r="86" />
                    <circle class="uniselv-gauge-track" fill="none" cx="100" cy="100" r="76" />
                    <circle class="uniselv-gauge-arc arc-cpu" id="uniselv-arc-cpu" fill="none" cx="100" cy="100" r="76" pathLength="100" stroke-dasharray="100" stroke-dashoffset="' . (100 * (1 - min(100, max(0, $cpu_allowance)) / 100)) . '" transform="rotate(-90 100 100)" />
                    <g class="uniselv-gauge-thumb-rot" id="uniselv-thumb-rot-cpu" style="transform: rotate(' . (min(100, max(0, $cpu_allowance)) * 3.6) . 'deg);">
                        <circle cx="100" cy="24" r="5" fill="#3b82f6" filter="url(#glow-cpu)"/>
```

### Block 16 — replace

Existing anchor AFTER which:
```text
                </div>
                <div class="uniselv-liquid-circle">
```

Existing anchor BEFORE which:
```text
                        <div class="uniselv-wave wave-back"></div>
                        <div class="uniselv-wave wave-front"></div>
```

Existing content to replace/remove (not copied):
```text
                    <div class="uniselv-wave-container" id="uniselv-wave-cpu" style="height: ' . ($cpu_allowance <= 0 ? 0 : max(6, min(100, $cpu_allowance))) . '%;">
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                    <div class="uniselv-wave-container" id="uniselv-wave-cpu" style="height: ' . max(0, min(100, $cpu_allowance)) . '%;">
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                </div>
                <div class="uniselv-liquid-circle">
                    <div class="uniselv-wave-container" id="uniselv-wave-cpu" style="height: ' . max(0, min(100, $cpu_allowance)) . '%;">
                        <div class="uniselv-wave wave-back"></div>
                        <div class="uniselv-wave wave-front"></div>
```

### Block 17 — replace

Existing anchor AFTER which:
```text
                    <circle class="uniselv-gauge-ticks" fill="none" cx="100" cy="100" r="86" />
                    <circle class="uniselv-gauge-track" fill="none" cx="100" cy="100" r="76" />
```

Existing anchor BEFORE which:
```text
                    <g class="uniselv-gauge-thumb-rot" id="uniselv-thumb-rot-mem" style="transform: rotate(' . (min(100, max(0, $mem_pct)) * 3.6) . 'deg);">
                        <circle cx="100" cy="24" r="5" fill="#8b5cf6" filter="url(#glow-mem)"/>
```

Existing content to replace/remove (not copied):
```text
                    <circle class="uniselv-gauge-arc arc-mem" id="uniselv-arc-mem" fill="none" cx="100" cy="100" r="76" stroke-dasharray="477.5" stroke-dashoffset="' . (477.5 * (1 - min(100, max(0, $mem_pct)) / 100)) . '" transform="rotate(-90 100 100)" />
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                    <circle class="uniselv-gauge-arc arc-mem" id="uniselv-arc-mem" fill="none" cx="100" cy="100" r="76" pathLength="100" stroke-dasharray="100" stroke-dashoffset="' . (100 * (1 - min(100, max(0, $mem_pct)) / 100)) . '" transform="rotate(-90 100 100)" />
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                    <circle class="uniselv-gauge-ticks" fill="none" cx="100" cy="100" r="86" />
                    <circle class="uniselv-gauge-track" fill="none" cx="100" cy="100" r="76" />
                    <circle class="uniselv-gauge-arc arc-mem" id="uniselv-arc-mem" fill="none" cx="100" cy="100" r="76" pathLength="100" stroke-dasharray="100" stroke-dashoffset="' . (100 * (1 - min(100, max(0, $mem_pct)) / 100)) . '" transform="rotate(-90 100 100)" />
                    <g class="uniselv-gauge-thumb-rot" id="uniselv-thumb-rot-mem" style="transform: rotate(' . (min(100, max(0, $mem_pct)) * 3.6) . 'deg);">
                        <circle cx="100" cy="24" r="5" fill="#8b5cf6" filter="url(#glow-mem)"/>
```

### Block 18 — replace

Existing anchor AFTER which:
```text
                </div>
                <div class="uniselv-liquid-circle">
```

Existing anchor BEFORE which:
```text
                        <div class="uniselv-wave wave-back"></div>
                        <div class="uniselv-wave wave-front"></div>
```

Existing content to replace/remove (not copied):
```text
                    <div class="uniselv-wave-container" id="uniselv-wave-mem" style="height: ' . ($mem_pct <= 0 ? 0 : max(6, min(100, $mem_pct))) . '%;">
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                    <div class="uniselv-wave-container" id="uniselv-wave-mem" style="height: ' . max(0, min(100, $mem_pct)) . '%;">
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                </div>
                <div class="uniselv-liquid-circle">
                    <div class="uniselv-wave-container" id="uniselv-wave-mem" style="height: ' . max(0, min(100, $mem_pct)) . '%;">
                        <div class="uniselv-wave wave-back"></div>
                        <div class="uniselv-wave wave-front"></div>
```

### Block 19 — replace

Existing anchor AFTER which:
```text
                    <circle class="uniselv-gauge-ticks" fill="none" cx="100" cy="100" r="86" />
                    <circle class="uniselv-gauge-track" fill="none" cx="100" cy="100" r="76" />
```

Existing anchor BEFORE which:
```text
                    <g class="uniselv-gauge-thumb-rot" id="uniselv-thumb-rot-io" style="transform: rotate(' . (min(100, max(0, $io_pct)) * 3.6) . 'deg);">
                        <circle cx="100" cy="24" r="5" fill="#10b981" filter="url(#glow-io)"/>
```

Existing content to replace/remove (not copied):
```text
                    <circle class="uniselv-gauge-arc arc-io" id="uniselv-arc-io" fill="none" cx="100" cy="100" r="76" stroke-dasharray="477.5" stroke-dashoffset="' . (477.5 * (1 - min(100, max(0, $io_pct)) / 100)) . '" transform="rotate(-90 100 100)" />
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                    <circle class="uniselv-gauge-arc arc-io" id="uniselv-arc-io" fill="none" cx="100" cy="100" r="76" pathLength="100" stroke-dasharray="100" stroke-dashoffset="' . (100 * (1 - min(100, max(0, $io_pct)) / 100)) . '" transform="rotate(-90 100 100)" />
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                    <circle class="uniselv-gauge-ticks" fill="none" cx="100" cy="100" r="86" />
                    <circle class="uniselv-gauge-track" fill="none" cx="100" cy="100" r="76" />
                    <circle class="uniselv-gauge-arc arc-io" id="uniselv-arc-io" fill="none" cx="100" cy="100" r="76" pathLength="100" stroke-dasharray="100" stroke-dashoffset="' . (100 * (1 - min(100, max(0, $io_pct)) / 100)) . '" transform="rotate(-90 100 100)" />
                    <g class="uniselv-gauge-thumb-rot" id="uniselv-thumb-rot-io" style="transform: rotate(' . (min(100, max(0, $io_pct)) * 3.6) . 'deg);">
                        <circle cx="100" cy="24" r="5" fill="#10b981" filter="url(#glow-io)"/>
```

### Block 20 — replace

Existing anchor AFTER which:
```text
                </div>
                <div class="uniselv-liquid-circle">
```

Existing anchor BEFORE which:
```text
                        <div class="uniselv-wave wave-back"></div>
                        <div class="uniselv-wave wave-front"></div>
```

Existing content to replace/remove (not copied):
```text
                    <div class="uniselv-wave-container" id="uniselv-wave-io" style="height: ' . ($io_pct <= 0 ? 0 : max(6, min(100, $io_pct))) . '%;">
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                    <div class="uniselv-wave-container" id="uniselv-wave-io" style="height: ' . max(0, min(100, $io_pct)) . '%;">
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                </div>
                <div class="uniselv-liquid-circle">
                    <div class="uniselv-wave-container" id="uniselv-wave-io" style="height: ' . max(0, min(100, $io_pct)) . '%;">
                        <div class="uniselv-wave wave-back"></div>
                        <div class="uniselv-wave wave-front"></div>
```

### Block 21 — replace

Existing anchor AFTER which:
```text
                    <circle class="uniselv-gauge-ticks" fill="none" cx="100" cy="100" r="86" />
                    <circle class="uniselv-gauge-track" fill="none" cx="100" cy="100" r="76" />
```

Existing anchor BEFORE which:
```text
                    <g class="uniselv-gauge-thumb-rot" id="uniselv-thumb-rot-tasks" style="transform: rotate(' . (min(100, max(0, $task_pct)) * 3.6) . 'deg);">
                        <circle cx="100" cy="24" r="5" fill="#f59e0b" filter="url(#glow-tasks)"/>
```

Existing content to replace/remove (not copied):
```text
                    <circle class="uniselv-gauge-arc arc-tasks" id="uniselv-arc-tasks" fill="none" cx="100" cy="100" r="76" stroke-dasharray="477.5" stroke-dashoffset="' . (477.5 * (1 - min(100, max(0, $task_pct)) / 100)) . '" transform="rotate(-90 100 100)" />
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                    <circle class="uniselv-gauge-arc arc-tasks" id="uniselv-arc-tasks" fill="none" cx="100" cy="100" r="76" pathLength="100" stroke-dasharray="100" stroke-dashoffset="' . (100 * (1 - min(100, max(0, $task_pct)) / 100)) . '" transform="rotate(-90 100 100)" />
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                    <circle class="uniselv-gauge-ticks" fill="none" cx="100" cy="100" r="86" />
                    <circle class="uniselv-gauge-track" fill="none" cx="100" cy="100" r="76" />
                    <circle class="uniselv-gauge-arc arc-tasks" id="uniselv-arc-tasks" fill="none" cx="100" cy="100" r="76" pathLength="100" stroke-dasharray="100" stroke-dashoffset="' . (100 * (1 - min(100, max(0, $task_pct)) / 100)) . '" transform="rotate(-90 100 100)" />
                    <g class="uniselv-gauge-thumb-rot" id="uniselv-thumb-rot-tasks" style="transform: rotate(' . (min(100, max(0, $task_pct)) * 3.6) . 'deg);">
                        <circle cx="100" cy="24" r="5" fill="#f59e0b" filter="url(#glow-tasks)"/>
```

### Block 22 — replace

Existing anchor AFTER which:
```text
                </div>
                <div class="uniselv-liquid-circle">
```

Existing anchor BEFORE which:
```text
                        <div class="uniselv-wave wave-back"></div>
                        <div class="uniselv-wave wave-front"></div>
```

Existing content to replace/remove (not copied):
```text
                    <div class="uniselv-wave-container" id="uniselv-wave-tasks" style="height: ' . (18 + min(100, max(0, $task_pct)) * 0.65) . '%;">
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                    <div class="uniselv-wave-container" id="uniselv-wave-tasks" style="height: ' . min(100, max(0, $task_pct)) . '%;">
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
                </div>
                <div class="uniselv-liquid-circle">
                    <div class="uniselv-wave-container" id="uniselv-wave-tasks" style="height: ' . min(100, max(0, $task_pct)) . '%;">
                        <div class="uniselv-wave wave-back"></div>
                        <div class="uniselv-wave wave-front"></div>
```

## uniselv-resman/views/admin_help.php

Installed paths: /usr/local/webuzo/plugins/uniselv-resman/views/admin_help.php

Replace the full file; never append duplicate functions/directives. New files run from first through final line.

### Block 1 — replace

Existing anchor AFTER which:
```text
            <h4 class="uniselv-help-card-title">Runtime Operations, Exact Source Placement &amp; Validation Scope</h4>
            <div class="uniselv-help-card-desc">Release <?php echo $uniselvHelpEscape($uniselvHelpVersion); ?>. These technical guides describe already-applied changes; they are not additional post-install paste steps.</div>
```

Existing anchor BEFORE which:
```text
        </div>

```

Existing content to replace/remove (not copied):
```text
            <details><summary>Operations, expected profile and verification scope</summary><pre style="white-space:pre-wrap;overflow-wrap:anywhere"><?php echo htmlspecialchars(file_get_contents(__DIR__ . '/../docs/release-1.1.24.md'), ENT_QUOTES, 'UTF-8'); ?></pre></details>
            <details><summary>Exact source replacement and insertion guide</summary><pre style="white-space:pre-wrap;overflow-wrap:anywhere"><?php echo htmlspecialchars(file_get_contents(__DIR__ . '/../docs/source-changes-1.1.24.md'), ENT_QUOTES, 'UTF-8'); ?></pre></details>
```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
            <details><summary>Operations, expected profile and verification scope</summary><pre style="white-space:pre-wrap;overflow-wrap:anywhere"><?php echo htmlspecialchars(file_get_contents(__DIR__ . '/../docs/release-1.1.25.md'), ENT_QUOTES, 'UTF-8'); ?></pre></details>
            <details><summary>Exact source replacement and insertion guide</summary><pre style="white-space:pre-wrap;overflow-wrap:anywhere"><?php echo htmlspecialchars(file_get_contents(__DIR__ . '/../docs/source-changes-1.1.25.md'), ENT_QUOTES, 'UTF-8'); ?></pre></details>
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
            <h4 class="uniselv-help-card-title">Runtime Operations, Exact Source Placement &amp; Validation Scope</h4>
            <div class="uniselv-help-card-desc">Release <?php echo $uniselvHelpEscape($uniselvHelpVersion); ?>. These technical guides describe already-applied changes; they are not additional post-install paste steps.</div>
            <details><summary>Operations, expected profile and verification scope</summary><pre style="white-space:pre-wrap;overflow-wrap:anywhere"><?php echo htmlspecialchars(file_get_contents(__DIR__ . '/../docs/release-1.1.25.md'), ENT_QUOTES, 'UTF-8'); ?></pre></details>
            <details><summary>Exact source replacement and insertion guide</summary><pre style="white-space:pre-wrap;overflow-wrap:anywhere"><?php echo htmlspecialchars(file_get_contents(__DIR__ . '/../docs/source-changes-1.1.25.md'), ENT_QUOTES, 'UTF-8'); ?></pre></details>
        </div>

```

### Block 2 — insert

Existing anchor AFTER which:
```text
            <h4 class="uniselv-help-card-title">Resource Metrics & Allowance Mathematics</h4>
            <div class="uniselv-help-card-desc">
```

Existing anchor BEFORE which:
```text
                <strong>1. CPU % (Core Equivalent):</strong> 100% CPU represents one logical CPU/vCPU worth of scheduled execution time; it does not guarantee a dedicated physical core. On a 4 vCPU server, 400% represents total machine capacity.<br>
                <strong>Allowance Percentage Example:</strong> If an account is assigned a 200% CPU quota (2 cores) and consumes 150% CPU, its allowance usage is:
```

Existing content to replace/remove (not copied):
```text

```

Generated replacement/insertion code (copy only this block when manually applying this specific change):
```text
                <strong>Gauge fill:</strong> 0% is empty, 50% half and 100% full. Missing data is neutral. Hardware Detection is inventory; its ring does not represent usage. Admin Shared CPU Headroom shows configured hosting share (340% / 400% = 85% on four vCPUs). RAM is aggregate memory usage / enforced cap; System Load is load1 / vCPU count, not CPU utilization.<br>
```

Illustrative AFTER-edit context (do not paste in addition to generated code):
```text
            <h4 class="uniselv-help-card-title">Resource Metrics & Allowance Mathematics</h4>
            <div class="uniselv-help-card-desc">
                <strong>Gauge fill:</strong> 0% is empty, 50% half and 100% full. Missing data is neutral. Hardware Detection is inventory; its ring does not represent usage. Admin Shared CPU Headroom shows configured hosting share (340% / 400% = 85% on four vCPUs). RAM is aggregate memory usage / enforced cap; System Load is load1 / vCPU count, not CPU utilization.<br>
                <strong>1. CPU % (Core Equivalent):</strong> 100% CPU represents one logical CPU/vCPU worth of scheduled execution time; it does not guarantee a dedicated physical core. On a 4 vCPU server, 400% represents total machine capacity.<br>
                <strong>Allowance Percentage Example:</strong> If an account is assigned a 200% CPU quota (2 cores) and consumes 150% CPU, its allowance usage is:
```
