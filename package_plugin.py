import os
import zipfile
import hashlib
import json
import shutil
from pathlib import Path

TEXT_EXTENSIONS = {
    '.py', '.php', '.sh', '.conf', '.json', '.md', '.txt',
    '.css', '.js', '.svg', '.html', '.xml', '.yml', '.yaml'
}

def package():
    base_dir = Path(__file__).resolve().parent
    plugin_src = base_dir / 'plugin'
    zip_path = base_dir / 'uniselv-resman.zip'

    info_file = plugin_src / 'info.json'
    version = "1.1.15"
    if info_file.exists():
        try:
            info_data = json.loads(info_file.read_text(encoding='utf-8'))
            version = info_data.get('version', version)
        except Exception:
            pass

    if zip_path.exists():
        zip_path.unlink()

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Write root folder entry with 0755 directory permissions
        root_zinfo = zipfile.ZipInfo('uniselv-resman/')
        root_zinfo.date_time = (2026, 10, 20, 0, 0, 0)
        root_zinfo.external_attr = 0o40755 << 16
        zf.writestr(root_zinfo, '')

        for root, dirs, files in os.walk(plugin_src):
            dirs[:] = sorted([d for d in dirs if d != '__pycache__' and not d.startswith('.')])
            for d in dirs:
                full_dir = Path(root) / d
                rel_dir = full_dir.relative_to(plugin_src)
                d_arcname = 'uniselv-resman/' + rel_dir.as_posix() + '/'
                d_zinfo = zipfile.ZipInfo(d_arcname)
                d_zinfo.date_time = (2026, 10, 20, 0, 0, 0)
                d_zinfo.external_attr = 0o40755 << 16
                zf.writestr(d_zinfo, '')

            for file in sorted(files):
                if file.endswith('.pyc') or file.startswith('.'):
                    continue
                full_path = Path(root) / file
                rel_path = full_path.relative_to(plugin_src)
                arcname = 'uniselv-resman/' + rel_path.as_posix()

                raw_bytes = full_path.read_bytes()
                ext = full_path.suffix.lower()

                zinfo = zipfile.ZipInfo(arcname)
                # Use reproducible date: 2026-10-20 00:00:00
                zinfo.date_time = (2026, 10, 20, 0, 0, 0)
                zinfo.compress_type = zipfile.ZIP_DEFLATED

                # Set executable permissions for scripts
                if ext in {'.py', '.sh'} or file == 'install.php':
                    zinfo.external_attr = 0o100755 << 16
                else:
                    zinfo.external_attr = 0o100644 << 16

                if ext in TEXT_EXTENSIONS:
                    # Normalize all text files to Unix LF bytes
                    normalized = raw_bytes.replace(b'\r\n', b'\n')
                    zf.writestr(zinfo, normalized)
                else:
                    zf.writestr(zinfo, raw_bytes)

    sha256 = hashlib.sha256(zip_path.read_bytes()).hexdigest()
    size = zip_path.stat().st_size

    print(f"Package created: {zip_path}")
    print(f"Size: {size} bytes")
    print(f"SHA-256: {sha256}")

    ver_zip_path = base_dir / f'uniselv-resman-{version}.zip'
    shutil.copy2(zip_path, ver_zip_path)
    ver_sha256 = hashlib.sha256(ver_zip_path.read_bytes()).hexdigest()
    (base_dir / f'uniselv-resman-{version}.zip.sha256').write_text(f"{ver_sha256}  uniselv-resman-{version}.zip\n")
    print(f"Versioned package created: {ver_zip_path} (SHA256: {ver_sha256})")

    # Write checksum file for uniselv-resman.zip
    (base_dir / 'uniselv-resman.zip.sha256').write_text(f"{sha256}  uniselv-resman.zip\n")

    # Copy to vps-validation directory for convenience
    vps_val = base_dir.parent / 'vps-validation'
    if vps_val.is_dir():
        shutil.copy2(ver_zip_path, vps_val / f'uniselv-resman-{version}.zip')
        (vps_val / f'uniselv-resman-{version}.zip.sha256').write_text(f"{ver_sha256}  uniselv-resman-{version}.zip\n")
        print(f"Copied to validation workspace: {vps_val / f'uniselv-resman-{version}.zip'}")

if __name__ == '__main__':
    package()
