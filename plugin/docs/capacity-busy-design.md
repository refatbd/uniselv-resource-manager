# Neutral capacity fallback

The proxy now serves a self-contained animated HTML page with no product branding, remote fonts, scripts, images, PHP execution, or automatic retries. The retry link makes a user-initiated GET of the current URL; it does not replay submitted POST data. CSS respects reduced-motion preferences. HTTP 503 and Retry-After: 5 remain intact; Cache-Control: no-store prevents caching the temporary failure.

## Exact source placement and duplicate handling

- Preview/new file: `core/capacity-busy.html`, mirrored at `plugin/core/capacity-busy.html`. The complete document starts with `<!doctype html>` and ends with `</html>`; do not append it to an existing document.
- Proxy sources: `core/webuzo-isolation.py` and `plugin/core/webuzo-isolation.py`. The deployed destination is `/usr/local/sbin/webuzo-isolation.py`.
- Missing-directive insertion: one `CAPACITY_BUSY_HTML` bytes constant after `MARKER='# WEBUZO-ISOLATION MANAGED LAUNCHER'`, before `def execute(args,check=True,timeout=60):`. It contains the UTF-8 bytes of the complete HTML document. Replace an existing constant rather than inserting a duplicate.
- Replacement: inside `fastcgi_proxy()` > `unavailable()`, replace the single `content=...` statement. Paste after `if version!=1 or not rid:return` and before `def record(kind,payload):...`. Keep header reading, request IDs, record framing and all admission settings unchanged.

Replacement code (no surrounding context):

```python
        content=(b'Status: 503 Service Unavailable\r\nContent-Type: text/html; charset=utf-8\r\nRetry-After: 5\r\nCache-Control: no-store\r\nX-Content-Type-Options: nosniff\r\nContent-Security-Policy: default-src \'none\'; style-src \'unsafe-inline\'; base-uri \'none\'; frame-ancestors \'none\'\r\n\r\n'+CAPACITY_BUSY_HTML)
```

Illustrative AFTER-edit context (do not copy this as an extra block):

```python
        if version!=1 or not rid:return
        content=(b'Status: 503 Service Unavailable\r\nContent-Type: text/html; charset=utf-8\r\nRetry-After: 5\r\nCache-Control: no-store\r\nX-Content-Type-Options: nosniff\r\nContent-Security-Policy: default-src \'none\'; style-src \'unsafe-inline\'; base-uri \'none\'; frame-ancestors \'none\'\r\n\r\n'+CAPACITY_BUSY_HTML)
        def record(kind,payload):return struct.pack('!BBHHBB',1,kind,rid,len(payload),0,0)+payload
```

Save as UTF-8 with LF line endings. Run `python -m unittest test_capacity_busy_response.py` from the resource-manager directory and syntax-check both Python sources. Preview the HTML in a browser. The HTML is embedded so fallback requests require no file reads; editing only the preview will not change the embedded response.

## Validation and deployment boundary

Local checks cover Python syntax and actual FastCGI fallback framing with a fragmented request header, status, headers, UTF-8 document and END_REQUEST. Desktop preview was visually inspected. This change does not adjust capacity limits or certify workload capacity. Existing API/AJAX requests still receive 503, with an HTML body; this design does not add content negotiation. No production server installation, proxy restart, or new release archive is performed by these source edits. Live adoption requires a backed-up, reviewed update and controlled proxy restart because existing proxy processes keep their loaded code.
