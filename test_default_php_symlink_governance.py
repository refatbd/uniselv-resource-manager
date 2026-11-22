"""Unit & security tests for Autonomous Webuzo Default PHP OS Symlink Governance."""
import os
import pathlib
import sys
import tempfile
import types
import unittest
from unittest import mock

if sys.platform == 'win32':
    for _mod_name in ('pwd', 'grp', 'fcntl'):
        if _mod_name not in sys.modules:
            _stub = types.ModuleType(_mod_name)
            _stub.getpwnam = lambda name: None
            _stub.getpwuid = lambda uid: None
            _stub.getgrnam = lambda name: None
            _stub.getgrgid = lambda gid: None
            _stub.flock = lambda *a, **k: None
            _stub.LOCK_EX = 2
            _stub.LOCK_NB = 4
            _stub.LOCK_UN = 8
            sys.modules[_mod_name] = _stub

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'agent'))
sys.path.insert(0, str(ROOT / 'core'))

import runtime_governance as gov


class DefaultPhpSymlinkGovernanceTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base = pathlib.Path(self.temp_dir.name)
        self.apps = self.base / 'usr/local/apps'
        self.webuzo = self.base / 'usr/local/webuzo'
        self.bin_local = self.base / 'usr/local/bin'
        self.bin_usr = self.base / 'usr/bin'

        # Create mock PHP 8.2 and 8.4 installations
        for ver in ('php82', 'php84', 'php83'):
            p_bin = self.apps / ver / 'bin'
            p_bin.mkdir(parents=True, exist_ok=True)
            for b in ('php', 'php-cgi', 'phar', 'phpize', 'php-config'):
                b_file = p_bin / b
                b_file.write_text(f"#!/bin/sh\necho {ver}-{b}\n", encoding='utf-8')
                try:
                    os.chmod(str(b_file), 0o755)
                except OSError:
                    pass

        self.webuzo.mkdir(parents=True, exist_ok=True)
        self.bin_local.mkdir(parents=True, exist_ok=True)
        self.bin_usr.mkdir(parents=True, exist_ok=True)
        self.universal = self.webuzo / 'universal.php'

        self.use_mock_symlinks = False
        if os.name == 'nt':
            test_link = self.base / 'test_symlink_probe'
            try:
                test_link.symlink_to(self.webuzo)
                test_link.unlink()
            except OSError:
                self.use_mock_symlinks = True

        if self.use_mock_symlinks:
            self._mock_links = {}
            orig_replace = os.replace
            orig_unlink = os.unlink

            def _fake_symlink(target, path, *args, **kwargs):
                p_path = pathlib.Path(path)
                p_path.parent.mkdir(parents=True, exist_ok=True)
                p_path.write_text(f"SYMLINK->{target}", encoding='utf-8')
                self._mock_links[str(p_path.resolve())] = str(target)
                self._mock_links[str(p_path)] = str(target)

            def _fake_readlink(path):
                p = pathlib.Path(path)
                for k in (str(p.resolve()), str(p)):
                    if k in self._mock_links:
                        return self._mock_links[k]
                raise OSError(f"[Errno 22] Invalid argument: '{path}'")

            def _fake_is_symlink(p_self):
                p = pathlib.Path(p_self)
                return str(p.resolve()) in self._mock_links or str(p) in self._mock_links

            def _fake_replace(src, dst):
                p_src = pathlib.Path(src)
                p_dst = pathlib.Path(dst)
                val = self._mock_links.pop(str(p_src.resolve()), None) or self._mock_links.pop(str(p_src), None)
                if val:
                    self._mock_links[str(p_dst.resolve())] = val
                    self._mock_links[str(p_dst)] = val
                return orig_replace(src, dst)

            def _fake_unlink(path, missing_ok=False):
                p = pathlib.Path(path)
                self._mock_links.pop(str(p.resolve()), None)
                self._mock_links.pop(str(p), None)
                return orig_unlink(path)

            self._patchers = [
                mock.patch('os.symlink', side_effect=_fake_symlink),
                mock.patch('os.readlink', side_effect=_fake_readlink),
                mock.patch('os.replace', side_effect=_fake_replace),
                mock.patch('os.unlink', side_effect=_fake_unlink),
                mock.patch.object(pathlib.Path, 'is_symlink', _fake_is_symlink),
            ]
            for p in self._patchers:
                p.start()

    def tearDown(self):
        if self.use_mock_symlinks:
            for p in self._patchers:
                try:
                    p.stop()
                except Exception:
                    pass
        self.temp_dir.cleanup()

    def _create_symlink(self, link: pathlib.Path, target: pathlib.Path):
        if self.use_mock_symlinks:
            link.parent.mkdir(parents=True, exist_ok=True)
            link.write_text(f"SYMLINK->{target}", encoding='utf-8')
            self._mock_links[str(link.resolve())] = str(target)
            self._mock_links[str(link)] = str(target)
        else:
            link.symlink_to(target)

    def _resolve_link(self, link: pathlib.Path):
        if self.use_mock_symlinks:
            val = self._mock_links.get(str(link.resolve())) or self._mock_links.get(str(link))
            return pathlib.Path(val) if val else link
        return link.resolve()

    def test_detect_webuzo_default_php_from_universal(self):
        self.universal.write_text("<?php\n$globals['WU_DEFAULT_PHP'] = 'php84';\n", encoding='utf-8')
        detected = gov.detect_webuzo_default_php(universal_path=self.universal, apps_dir=self.apps)
        self.assertEqual(detected, 'php84')

    def test_detect_webuzo_default_php_fallback_to_highest_installed(self):
        if self.universal.exists():
            self.universal.unlink()
        detected = gov.detect_webuzo_default_php(universal_path=self.universal, apps_dir=self.apps)
        self.assertEqual(detected, 'php84')

    def test_sync_default_php_symlinks_creates_missing_symlinks(self):
        self.universal.write_text("<?php\n$globals['WU_DEFAULT_PHP'] = 'php84';\n", encoding='utf-8')
        result = gov.sync_default_php_symlinks(
            universal_path=self.universal,
            apps_dir=self.apps,
            bin_dirs=[self.bin_local, self.bin_usr]
        )
        self.assertTrue(result['success'])
        self.assertEqual(result['defaultVersion'], 'php84')
        self.assertGreater(len(result['synced']), 0)

        target_php = self.apps / 'php84/bin/php'
        for b_dir in (self.bin_local, self.bin_usr):
            link = b_dir / 'php'
            self.assertTrue(link.is_symlink())
            self.assertEqual(self._resolve_link(link), target_php)

    def test_sync_default_php_symlinks_heals_drifted_symlinks(self):
        old_target = self.apps / 'php82/bin/php'
        for b_dir in (self.bin_local, self.bin_usr):
            link = b_dir / 'php'
            self._create_symlink(link, old_target)
            self.assertEqual(self._resolve_link(link), old_target)

        # Webuzo default is php84
        self.universal.write_text("<?php\n$globals['WU_DEFAULT_PHP'] = 'php84';\n", encoding='utf-8')

        result = gov.sync_default_php_symlinks(
            universal_path=self.universal,
            apps_dir=self.apps,
            bin_dirs=[self.bin_local, self.bin_usr]
        )
        self.assertTrue(result['success'])
        self.assertGreater(len(result['drifts']), 0)

        new_target = self.apps / 'php84/bin/php'
        for b_dir in (self.bin_local, self.bin_usr):
            link = b_dir / 'php'
            self.assertTrue(link.is_symlink())
            self.assertEqual(self._resolve_link(link), new_target)

    def test_sync_default_php_symlinks_heals_dangling_broken_symlinks(self):
        # Point to nonexistent path
        for b_dir in (self.bin_local, self.bin_usr):
            link = b_dir / 'php'
            self._create_symlink(link, self.apps / 'php99_missing/bin/php')

        self.universal.write_text("<?php\n$globals['WU_DEFAULT_PHP'] = 'php84';\n", encoding='utf-8')
        result = gov.sync_default_php_symlinks(
            universal_path=self.universal,
            apps_dir=self.apps,
            bin_dirs=[self.bin_local, self.bin_usr]
        )
        self.assertTrue(result['success'])
        target_php = self.apps / 'php84/bin/php'
        for b_dir in (self.bin_local, self.bin_usr):
            link = b_dir / 'php'
            self.assertTrue(link.is_symlink())
            self.assertEqual(self._resolve_link(link), target_php)

    def test_sync_default_php_symlinks_idempotent_no_unnecessary_drifts(self):
        self.universal.write_text("<?php\n$globals['WU_DEFAULT_PHP'] = 'php84';\n", encoding='utf-8')
        # First sync
        res1 = gov.sync_default_php_symlinks(
            universal_path=self.universal,
            apps_dir=self.apps,
            bin_dirs=[self.bin_local, self.bin_usr]
        )
        self.assertTrue(res1['success'])

        # Second sync
        res2 = gov.sync_default_php_symlinks(
            universal_path=self.universal,
            apps_dir=self.apps,
            bin_dirs=[self.bin_local, self.bin_usr]
        )
        self.assertTrue(res2['success'])
        self.assertEqual(len(res2['drifts']), 0)

    def test_sync_default_php_symlinks_dynamic_version_switch(self):
        # 1. Start with php84
        self.universal.write_text("<?php\n$globals['WU_DEFAULT_PHP'] = 'php84';\n", encoding='utf-8')
        res1 = gov.sync_default_php_symlinks(
            universal_path=self.universal,
            apps_dir=self.apps,
            bin_dirs=[self.bin_local, self.bin_usr]
        )
        self.assertEqual(res1['defaultVersion'], 'php84')
        self.assertEqual(self._resolve_link(self.bin_local / 'php'), self.apps / 'php84/bin/php')

        # 2. Admin switches Default PHP in Webuzo to php83
        self.universal.write_text("<?php\n$globals['WU_DEFAULT_PHP'] = 'php83';\n", encoding='utf-8')
        res2 = gov.sync_default_php_symlinks(
            universal_path=self.universal,
            apps_dir=self.apps,
            bin_dirs=[self.bin_local, self.bin_usr]
        )
        self.assertTrue(res2['success'])
        self.assertEqual(res2['defaultVersion'], 'php83')
        self.assertEqual(self._resolve_link(self.bin_local / 'php'), self.apps / 'php83/bin/php')
        self.assertEqual(self._resolve_link(self.bin_usr / 'php'), self.apps / 'php83/bin/php')


if __name__ == '__main__':
    unittest.main()
