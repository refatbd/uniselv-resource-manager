#!/usr/bin/env python3
"""Owned, reversible FastCGI retry configuration for native Webuzo Apache."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path('/usr/local/apps/apache2')
CONF = ROOT / 'etc/conf.d/zz-uniselv-fcgi-retry.conf'
STATE = Path('/var/lib/uniselv-resource-manager/apache-fcgi-guard.json')
CONTENT = ('# Owned by UNISELV Resource Manager; remove through its uninstaller.\n'
           '# A transient full FastCGI queue must not disable its worker for 60 seconds.\n'
           '<IfModule proxy_fcgi_module>\n'
           '  <Proxy "fcgi://localhost">\n'
           '    ProxySet retry=0\n'
           '  </Proxy>\n'
           '</IfModule>\n')


def run(args):
    r = subprocess.run([str(a) for a in args], capture_output=True, text=True, timeout=30)
    if r.returncode:
        raise RuntimeError((r.stdout + r.stderr)[-1800:])
    return r.stdout + r.stderr


def atomic(path, content, mode):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        raise RuntimeError('Refusing symlink: ' + str(path))
    fd, name = tempfile.mkstemp(prefix='.uniselv-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        os.chmod(name, mode)
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def sha(content):
    return hashlib.sha256(content.encode()).hexdigest()


def check():
    if not CONF.is_file() or CONF.read_text() != CONTENT:
        raise RuntimeError('Managed FastCGI retry configuration missing or modified')
    run([ROOT / 'bin/httpd', '-t'])
    includes = run([ROOT / 'bin/httpd', '-t', '-D', 'DUMP_INCLUDES'])
    if str(CONF) not in includes:
        raise RuntimeError('Apache does not include the managed configuration')
    return {'configured': True, 'config': str(CONF), 'sha256': sha(CONTENT)}


def install():
    # Refuse unsupported stacks and pre-existing configuration errors before mutation.
    run([ROOT / 'bin/httpd', '-t'])
    if 'proxy_fcgi_module' not in run([ROOT / 'bin/httpd', '-M']):
        raise RuntimeError('Native Apache mod_proxy_fcgi is required')
    data = json.loads(STATE.read_text()) if STATE.exists() else None
    if CONF.exists():
        if not data or data.get('sha256') != sha(CONF.read_text()):
            raise RuntimeError('Unowned or modified FastCGI configuration; refusing overwrite')
    # Commit intent before creating configuration; retries recover this pending state.
    atomic(STATE, json.dumps({'sha256': sha(CONTENT), 'phase': 'pending'}, indent=2), 0o600)
    old = CONF.read_text() if CONF.exists() else None
    try:
        atomic(CONF, CONTENT, 0o644)
        result = check()
        run([ROOT / 'bin/apachectl', 'graceful'])
        atomic(STATE, json.dumps({'sha256': sha(CONTENT), 'phase': 'installed'}, indent=2), 0o600)
        return result
    except Exception:
        if old is None:
            CONF.unlink(missing_ok=True)
        else:
            atomic(CONF, old, 0o644)
        run([ROOT / 'bin/httpd', '-t'])
        run([ROOT / 'bin/apachectl', 'graceful'])
        raise


def uninstall():
    if not STATE.exists():
        if CONF.exists():
            raise RuntimeError('Configuration exists without ownership state; retained for review')
        return {'removed': False, 'reason': 'not installed'}
    data = json.loads(STATE.read_text())
    if CONF.exists():
        old = CONF.read_text()
        if data.get('sha256') != sha(old):
            raise RuntimeError('Managed configuration was modified; retained for review')
        CONF.unlink()
        try:
            run([ROOT / 'bin/httpd', '-t'])
            run([ROOT / 'bin/apachectl', 'graceful'])
        except Exception:
            atomic(CONF, old, 0o644)
            run([ROOT / 'bin/apachectl', 'graceful'])
            raise
    STATE.unlink()
    return {'removed': True}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['install', 'check', 'uninstall'])
    args = parser.parse_args()
    if os.geteuid() != 0:
        parser.error('Run through sudo')
    try:
        print(json.dumps({'install': install, 'check': check, 'uninstall': uninstall}[args.action]()))
    except Exception as exc:
        raise SystemExit(str(exc))
