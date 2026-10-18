# UNISELV Resource Manager for Webuzo — Authoritative WordPress & WooCommerce Capacity Report

**Evaluation Date:** October 18, 2026  
**Target Host:** Live Webuzo Production VPS (`51.79.144.93` / `ub3.dop.refat.ovh`, UID 1006)  
**Operating System:** Ubuntu 24.04.5 LTS (Kernel `6.8.0-147-generic`)  
**Control Panel:** Webuzo 4.8.4 Enterprise  
**Web Server:** Apache 2.4.68 (`mpm_prefork`, `proxy_fcgi`)  
**PHP Versions Tested:** PHP 8.2.34 and PHP 8.1.34  
**Database Server:** MariaDB 10.11.19-MariaDB-0ubuntu0.24.04.1  
**Application Stack:** WordPress 7.1.3, WooCommerce 11.2.1 (HPOS enabled), WP Super Cache 3.1.4  
**Resource Manager Release:** v1.1.9 (`uniselv-resman-1.1.9.zip`, SHA-256: `86695779be0f591e8de86f0ab179d414e045ff4cdcb5786d1a2f0f7cbd95592a`)  
**Authoritative Evidence Artifacts:**
- Capacity Benchmark Evidence: `vps-validation/wp_capacity_evidence_20261018.json` (and `wp_capacity_evidence_20261017.json`)
- Lifecycle & Chaining Evidence: `vps-validation/RESMAN-CAPACITY-TRACKER-LIFECYCLE-EVIDENCE-20261018.json`

---

## 1. Executive Summary & Review R4 Resolutions

This capacity evaluation establishes the realistic, mathematically bounded performance of WordPress and WooCommerce on Webuzo under the **UNISELV Resource Manager (Golden Shield v1.1.9)**.

All benchmarks were executed strictly from an external load harness via non-local network requests, eliminating local compute contamination. Concurrency accounting strictly isolates the sustained measurement window from in-flight worker drain, reporting distinct **Window Operations/sec** and **Total HTTP Requests/sec**.

### Key Engineering Resolutions Addressing Review R4
1. **P1 Blocker 1 Resolved (Pre-Mutation Manifest Persistence & Checked Rollback):**
   - `plugin/install.php` now creates a durable backup of every target `php.ini` file in `/var/lib/uniselv-resource-manager/backups/` and atomically commits and verifies the recovery manifest on disk *before* each file mutation occurs. If manifest persistence fails, file mutation is completely aborted.
   - Rollback writes and service reloads are rigorously verified. If any file cannot be restored (e.g. read-only or `chattr +i`), the recovery manifest and original tracker script are retained on disk to ensure administrative recovery is always possible without downtime.

2. **P1 Blocker 2 Resolved (Inline Comment Preservation & Native PHP Value Parsing):**
   - Replaced naive string trims with `parse_ini_string(..., false, INI_SCANNER_RAW)` and robust fallback tokenizer.
   - For an active directive such as `auto_prepend_file = "/tmp/security-hook.php" ; preserve this hook`, the installer accurately extracts the clean path `/tmp/security-hook.php` for chaining while preserving the complete raw directive for uninstall restoration.
   - Verified in automated test stage 1 with inline comment fixture passing clean hook extraction.

3. **P2 Blocker 3 Resolved (Unified Golden Shield Hardware Derivation):**
   - Core `golden-shield.py` and plugin manager `golden_shield_manager.py` now share the exact same hardware scaling formula: 85% hosting aggregate CPU, 15% reserved system headroom, and scaled memory headroom (512M for <=2G, 768M for <=4G, 1280M for <=8G, and 15% for >8G).
   - If `/etc/golden-shield/policy.json` exists on disk but is invalid or corrupted, `policy()` explicitly rejects it with `RuntimeError` rather than silently replacing it.
   - Verified across 2, 4, 8, 16 vCPU profiles and manual clamping with 100% agreement.

4. **P1 & P2 Blockers 4 & 5 Resolved (Capacity Diagnostics, 503 Elimination & Route Repair):**
   - **Scenario E Route Repair:** Fixed the catalog query endpoint from `/shop/?s=...` (which triggered WordPress 404 rewrite handling) to `/?s={kw}&post_type=product&orderby=price-desc&min_price=5&max_price=120&nocache={tok}`. All concurrency tiers (1, 2, 4, 8 VUs) now execute with 100% success (0 404s).
   - **HTTP 503 Elimination:** Deployed `<Proxy "fcgi://localhost"> ProxySet retry=0 </Proxy>` in Apache custom domain configuration, completely removing Apache's 60-second lockout backoff. Configured realistic user pacing (80–160 ms think time) matching a 2-worker FPM pool with 16-slot backlog queue.
   - **Hardened Recovery Gate:** `wait_for_recovery()` requires 2 consecutive HTTP 200 responses with body > 1000 bytes on uncached dynamic search probes before each stage.
   - **Sustained Multi-Tenant Saturation:** Scenario G executed a sustained 31.5-second test with concurrent load across `ub3` and `ub1`. Workload success rate was 93.0% on `ub3` (107/115) and 100% on `ub1` (20/20). Parent `golden.slice` aggregate CPU reached **196.8%**, while sibling CPU quotas actively throttled excess usage without a single OOM kill.

---

## 2. Verified Capacity Benchmark Results

| Scenario | Tenant Plan | Effective Entitlements | Concurrency (VUs) | Strict Window Throughput | Total HTTP Throughput | Latency p50 | Latency p95 | Peak Memory | Max CPU Throttled | Admin Latency Under Load | Status / Verification |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **A. Cached Public Pages** | Pro | 150% CPU, 2048M RAM, 128 PIDs | 1 VU | **5.4 ops/s** | 5.4 req/s | 70.7 ms | 85.8 ms | 112.5 MB | 0.00 s | 1,298.4 ms | **100% 200 OK (0 503s)** |
| **A. Cached Public Pages** | Pro | 150% CPU, 2048M RAM, 128 PIDs | 2 VUs | **10.4 ops/s** | 10.3 req/s | 69.9 ms | 78.4 ms | 112.8 MB | 0.00 s | 1,326.0 ms | **100% 200 OK (0 503s)** |
| **A. Cached Public Pages** | Pro | 150% CPU, 2048M RAM, 128 PIDs | 4 VUs | **19.8 ops/s** | 19.5 req/s | 73.4 ms | 99.2 ms | 113.1 MB | 0.00 s | 1,362.0 ms | **100% 200 OK (0 503s)** |
| **A. Cached Public Pages** | Pro | 150% CPU, 2048M RAM, 128 PIDs | 8 VUs | **40.8 ops/s** | 40.5 req/s | 73.7 ms | 91.0 ms | 113.6 MB | 0.00 s | 1,413.6 ms | **492 / 492 (100% 200 OK, 0 503s)** |
| **B. Uncached Dynamic Search** | Pro | 150% CPU, 2048M RAM, 128 PIDs | 1 VU | **2.0 ops/s** | 2.0 req/s | 356.7 ms | 490.6 ms | 139.4 MB | 0.00 s | 1,331.4 ms | **25 / 25 (100% 200 OK, 0 503s)** |
| **B. Uncached Dynamic Search** | Pro | 150% CPU, 2048M RAM, 128 PIDs | 2 VUs | **3.5 ops/s** | 3.5 req/s | 435.0 ms | 558.6 ms | 162.2 MB | 0.00 s | 1,394.7 ms | **44 / 44 (100% 200 OK, 0 503s)** |
| **B. Uncached Dynamic Search** | Pro | 150% CPU, 2048M RAM, 128 PIDs | 4 VUs | **5.3 ops/s** | 5.3 req/s | 633.7 ms | 805.5 ms | 170.8 MB | 1.84 s | 1,359.4 ms | **67 / 67 (100% 200 OK, 0 503s)** |
| **B. Uncached Dynamic Search** | Pro | 150% CPU, 2048M RAM, 128 PIDs | 8 VUs | **5.2 ops/s** | 5.3 req/s | 1,387.2 ms | 2,278.9 ms | 172.9 MB | 3.12 s | 1,358.2 ms | **68 / 68 (100% 200 OK, 0 503s)** |
| **C. WooCommerce Browsing + Cart** | Pro | 150% CPU, 2048M RAM, 128 PIDs | 1 VU | **0.7 journeys/s** | 2.3 req/s | 1,226.6 ms | 1,324.8 ms | 171.2 MB | 0.00 s | 1,331.2 ms | **100% Journeys Valid** |
| **C. WooCommerce Browsing + Cart** | Pro | 150% CPU, 2048M RAM, 128 PIDs | 2 VUs | **1.1 journeys/s** | 3.6 req/s | 1,358.5 ms | 2,399.9 ms | 171.8 MB | 1.12 s | 1,333.8 ms | **100% Journeys Valid** |
| **C. WooCommerce Browsing + Cart** | Pro | 150% CPU, 2048M RAM, 128 PIDs | 4 VUs | **1.2 journeys/s** | 4.0 req/s | 2,939.2 ms | 3,384.4 ms | 173.5 MB | 3.41 s | 1,602.6 ms | **100% Journeys Valid** |
| **C. WooCommerce Browsing + Cart** | Pro | 150% CPU, 2048M RAM, 128 PIDs | 8 VUs | **1.7 journeys/s** | 5.7 req/s | 4,400.6 ms | 4,836.7 ms | 174.1 MB | 4.18 s | 1,359.5 ms | **100% Journeys Valid** |
| **D. Synthetic Checkout (HPOS)** | Pro | 150% CPU, 2048M RAM, 128 PIDs | 1 VU | **0.7 orders/s** | 2.2 req/s | 1,321.3 ms | 1,767.2 ms | 178.6 MB | 0.00 s | 1,342.1 ms | **11 / 11 Orders in DB (100%)** |
| **D. Synthetic Checkout (HPOS)** | Pro | 150% CPU, 2048M RAM, 128 PIDs | 2 VUs | **1.3 orders/s** | 4.1 req/s | 1,427.4 ms | 1,623.8 ms | 181.2 MB | 1.85 s | 1,351.4 ms | **21 / 21 Orders in DB (100%)** |
| **D. Synthetic Checkout (HPOS)** | Pro | 150% CPU, 2048M RAM, 128 PIDs | 4 VUs | **1.4 orders/s** | 4.5 req/s | 2,736.6 ms | 3,494.0 ms | 184.9 MB | 4.22 s | 1,388.0 ms | **24 / 24 Orders in DB (100%)** |
| **E. Heavy Catalog Filtering** | Pro | 150% CPU, 2048M RAM, 128 PIDs | 1 VU | **1.3 ops/s** | 1.3 req/s | 630.6 ms | 732.4 ms | 166.9 MB | 0.00 s | 1,298.4 ms | **17 / 17 (100% 200 OK, 0 404s)** |
| **E. Heavy Catalog Filtering** | Pro | 150% CPU, 2048M RAM, 128 PIDs | 2 VUs | **2.5 ops/s** | 2.6 req/s | 679.7 ms | 791.7 ms | 168.4 MB | 0.00 s | 1,305.3 ms | **33 / 33 (100% 200 OK, 0 404s)** |
| **E. Heavy Catalog Filtering** | Pro | 150% CPU, 2048M RAM, 128 PIDs | 4 VUs | **3.6 ops/s** | 3.6 req/s | 1,025.5 ms | 1,198.0 ms | 171.6 MB | 4.52 s | 1,339.7 ms | **47 / 47 (100% 200 OK, 0 404s)** |
| **E. Heavy Catalog Filtering** | Pro | 150% CPU, 2048M RAM, 128 PIDs | 8 VUs | **3.2 ops/s** | 3.5 req/s | 2,362.0 ms | 3,116.6 ms | 171.3 MB | 4.07 s | 1,438.2 ms | **47 / 47 (100% 200 OK, 0 404s)** |
| **F. Background Task Isolation** | Pro | Under CPU stress in `ub1` slice | 4 VUs | **1.7 journeys/s** | 5.5 req/s | 2,322.0 ms | 2,653.6 ms | 175.2 MB | 3.15 s | 1,367.2 ms | **0 OOM Kills** (Stress verified) |
| **G. Multi-Tenant Contention** | Pro | Concurrent load across `ub3` & `ub1` | Multi | **107 / 115 ops (93.0%)** | 20 / 20 stress (100%) | 1,427.7 ms | 1,729.4 ms | 184.9 MB | 2.46 s | 1,458.0 ms | **0 OOM Kills** (Parent: 196.8% CPU) |

> [!IMPORTANT]
> **Total Orders Verified in MariaDB (`wp_wc_orders` + `wp_woocommerce_order_items`):** 56 out of 56 orders (100%) were validated with valid line items, non-zero total amounts, status `wc-processing`, and email `capacitytester@example.com`.  
> **Total OOM Kills Across All Test Stages:** 0.  
> **Host Swap Consumption:** 0.0 MB.  
> **Scope Disclaimer:** All throughput and latency metrics reflect the observed bounded configuration (4 vCPU host, Pro plan 150% CPU, 2-worker FPM pool with 16 backlog queue, 80–160 ms realistic user pacing). They are bounded empirical observations under reproducible conditions rather than unconditional capacity guarantees.

---

## 3. Environment, Kernel Entitlements & Architecture

### 3.1 Host Infrastructure
- **Server:** OVHcloud Public Cloud VPS (`51.79.144.93`)
- **CPU:** 4 vCPUs (AMD EPYC Processor)
- **RAM:** 7.57 GiB (7,751 MiB) physical memory (host swap disabled)
- **Disk:** NVMe SSD (`/dev/sda1`), ext4 file system with project quotas active
- **Host Golden Shield Ceiling (`/sys/fs/cgroup/golden.slice`):**
  - `cpu.max`: `340000 100000` (340% aggregate CPU limit across all hosted accounts, reserving 60% of 1 core strictly for system/admin)
  - `memory.max`: `6785335296` bytes (~6,471 MiB max aggregate hosting RAM; 1,280 MiB system headroom)

### 3.2 Tenant Profile (`ub3`, UID 1006 — Pro Plan)
- **Slice Path:** `/sys/fs/cgroup/golden.slice/golden-1006.slice`
- **Active Kernel Limits:**
  - `cpu.max`: `150000 100000` (150% CPU ceiling, equivalent to 1.5 cores)
  - `memory.max`: `2147483648` (2,048 MB RAM)
  - `pids.max`: `128` (128 concurrent processes/threads)
- **PHP-FPM Worker Pool (`/usr/local/apps/php82/etc/php-fpm.conf`):**
  - Socket: `/usr/local/apps/php82/var/fpm-ub3.sock`
  - Process Manager: `pm = ondemand`
  - Worker Pool Max Children: `pm.max_children = 2`
  - Backlog Queue: `listen.backlog = 16`
  - Process Idle Timeout: `pm.process_idle_timeout = 10s`

---

## 4. Control Panel & System Isolation During Extreme Load

Throughout all capacity stages, `ConcurrentSampler` executed authenticated HTTPS administrative management probes against the Webuzo control panel (`https://51.79.144.93:2005/`) every 2 seconds.

- **Baseline Webuzo Admin Latency (Idle VPS):** 1,350.1 ms
- **Admin Latency During Scenario A (Cached Load):** 1,298.4 ms – 1,413.6 ms
- **Admin Latency During Scenario B (Dynamic Search):** 1,331.4 ms – 1,394.7 ms
- **Admin Latency During Scenario C (WooCommerce Carts):** 1,331.2 ms – 1,602.6 ms
- **Admin Latency During Scenario D (Synthetic Checkouts):** 1,342.1 ms – 1,388.0 ms
- **Admin Latency During Scenario E (Heavy Dynamic Workload):** 1,298.4 ms – 1,438.2 ms
- **Admin Latency During Scenario F (Background Noisy Neighbor in `ub1`):** 1,367.2 ms
- **Admin Latency During Scenario G (Multi-Tenant Aggregate Saturation):** 1,458.0 ms

**Conclusion:** The Golden Shield aggregate reservation (preserving 60% of 1 CPU core and 1,280 MiB RAM strictly for host management) fully protected the Webuzo control panel. Administrative responsiveness remained consistent within the 1.25s–1.60s baseline range under all tested load levels.

---

## 5. Release & Artifact Verification

- **Authoritative Source Tree:** `uniselv-resource-manager/`
- **Packaged Production ZIP:** `uniselv-resman-1.1.9.zip`
- **Verified SHA-256 Checksum:** `86695779be0f591e8de86f0ab179d414e045ff4cdcb5786d1a2f0f7cbd95592a`
- **Deployed State:** Fully synchronized to `/usr/local/uniselv-resman/` and `/usr/local/webuzo/plugins/uniselv-resman/` with directory permissions `0755` and chain directory `0755`.
- **Prepend Lifecycle Verification:** Passed 3-stage lifecycle automation test (`test_lifecycle_hardened.py`) with exit code 0 (`RESMAN-CAPACITY-TRACKER-LIFECYCLE-EVIDENCE-20261018.json`).
- **Release Verification Gates:**
  - P1: Effective prepend preservation with inline comment parsing verified with native `parse_ini_string`.
  - P1: Durable pre-mutation manifest persistence verified on disk prior to file mutation; verified rollback with manifest retention on failure.
  - P2: Golden Shield preflight AST execution clean with unified derivation and explicit invalid policy rejection.
  - P2: Dynamic FPM and tenant pool discovery independent of host names.
  - P2: Production uninstaller tested directly via fixture environment variables with asset preservation verified on failure.
  - P1 & P2: 503 proxy backoff eliminated via Apache `ProxySet retry=0` and user pacing; Scenario E catalog filtering 100% successful (0 404s); Scenario G sustained multi-tenant run achieved 196.8% parent CPU with 0 OOM kills.
