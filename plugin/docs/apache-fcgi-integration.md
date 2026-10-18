# Apache FastCGI retry integration

Version 1.1.10 installs this component automatically during plugin activation. It supports the native Webuzo Apache layout at `/usr/local/apps/apache2` with `mod_proxy_fcgi`. Unsupported layouts and pre-existing Apache syntax errors block installation with an explicit error.

No additional manual configuration is required. The plugin creates the new file `/usr/local/apps/apache2/etc/conf.d/zz-uniselv-fcgi-retry.conf`. It verifies Apache includes that file, runs a syntax check, and requests a graceful reload. The complete file is generated; it is not inserted into an existing file and has no before/after anchors.

Illustrative complete generated file:

```apache
# Owned by UNISELV Resource Manager; remove through its uninstaller.
# A transient full FastCGI queue must not disable its worker for 60 seconds.
<IfModule proxy_fcgi_module>
  <Proxy "fcgi://localhost">
    ProxySet retry=0
  </Proxy>
</IfModule>
```

This removes the default retry exclusion interval after a failed backend connection. It does not add PHP workers, increase account limits, or guarantee successful requests during overload. A full PHP queue can still refuse requests; capacity and recovery must be measured separately.

Version 1.1.10 also fixes the bundled isolation proxy itself: it starts a private PHP backend only when cold, serializes that start, releases admission slots on FastCGI END_REQUEST, and handles thread-creation pressure without killing the entire proxy. This removes a source of backend resets that a retry setting alone cannot fix. Native account CPU/RAM/task limits and proxy TasksMax remain unchanged.

The existing Apache `Include etc/conf.d/*.conf` loads this file independently of generated customer vhosts. An old manually configured per-domain rule is not removed automatically; review it before removal. Do not paste duplicate rules into individual domains.

Admin verification, if needed:

```sh
sudo python3 /usr/local/uniselv-resman/core/apache-fcgi-guard.py check
```

Expected: JSON with `configured: true`, and no Apache syntax or missing-include error. Then open an uncached PHP page for a hosting account. A syntax check alone does not verify application behavior.

Normal plugin uninstall calls this component's removal action before deleting its program files. Only the recorded, unchanged owned file is removed. Apache is syntax-checked and gracefully reloaded. If reload fails the file is restored; if an administrator modified it, removal stops and preserves it for review. The ownership record is `/var/lib/uniselv-resource-manager/apache-fcgi-guard.json`.

Advanced standalone rollback (restores the normal Apache retry policy; it does not remove Golden Shield or the plugin):

```sh
sudo python3 /usr/local/uniselv-resman/core/apache-fcgi-guard.py uninstall
```

After rollback, verify Apache and real PHP pages. To re-enable the component run the same command with `install`, followed by `check`. Do not use rollback during a load test. Normal plugin deactivation retains this Apache safety setting; full uninstall removes it.
