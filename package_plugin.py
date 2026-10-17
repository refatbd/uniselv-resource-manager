import os
import zipfile
import hashlib
from pathlib import Path

def package():
    base_dir = Path(__file__).resolve().parent
    plugin_src = base_dir / 'plugin'
    zip_path = base_dir / 'uniselv-resman.zip'

    if zip_path.exists():
        zip_path.unlink()

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(plugin_src):
            dirs[:] = [d for d in dirs if d != '__pycache__' and not d.startswith('.')]
            for file in files:
                if file.endswith('.pyc') or file.startswith('.'):
                    continue
                full_path = Path(root) / file
                rel_path = full_path.relative_to(plugin_src)
                arcname = Path('uniselv-resman') / rel_path
                zf.write(full_path, arcname)

    sha256 = hashlib.sha256(zip_path.read_bytes()).hexdigest()
    size = zip_path.stat().st_size

    print(f"Package created: {zip_path}")
    print(f"Size: {size} bytes")
    import json
    info_file = plugin_src / 'info.json'
    version = "1.1.2"
    if info_file.exists():
        try:
            info_data = json.loads(info_file.read_text(encoding='utf-8'))
            version = info_data.get('version', version)
        except Exception:
            pass

    ver_zip_path = base_dir / f'uniselv-resman-{version}.zip'
    import shutil
    shutil.copy2(zip_path, ver_zip_path)
    ver_sha256 = hashlib.sha256(ver_zip_path.read_bytes()).hexdigest()
    (base_dir / f'uniselv-resman-{version}.zip.sha256').write_text(f"{ver_sha256}  uniselv-resman-{version}.zip\n")
    print(f"Versioned package created: {ver_zip_path} (SHA256: {ver_sha256})")

    # Write checksum file
    (base_dir / 'uniselv-resman.zip.sha256').write_text(f"{sha256}  uniselv-resman.zip\n")

if __name__ == '__main__':
    package()
