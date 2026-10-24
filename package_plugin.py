"""Compatibility entry point; all release ZIPs are built by native PHP ZipArchive."""
from pathlib import Path
import shutil,subprocess
if __name__ == '__main__':
    php=shutil.which('php')
    if not php:raise SystemExit('PHP with ZipArchive is required')
    raise SystemExit(subprocess.call([php,str(Path(__file__).with_suffix('.php'))]))
