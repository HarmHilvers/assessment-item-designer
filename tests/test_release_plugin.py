import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import urllib.error
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('release_plugin', ROOT / 'scripts/release_plugin.py')
release = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(release)


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'source'
        self.root.mkdir()
        for relative in ['plugin.json', '.codex-plugin', 'assets', 'skills', 'LICENSE']:
            source, target = ROOT / relative, self.root / relative
            if source.is_dir():
                shutil.copytree(source, target, ignore=shutil.ignore_patterns('__pycache__'))
            else:
                shutil.copyfile(source, target)
        self.output = Path(self.temp.name) / 'output'

    def build(self):
        return release.build_package(self.root, self.output)

    def test_zip_contains_only_upload_files_and_is_repeatable(self):
        cache = self.root / 'skills/assessment-item-designer/__pycache__'
        cache.mkdir()
        (cache / 'cache.pyc').write_bytes(b'exclude me')
        _, archive = self.build()
        original = archive.read_bytes()
        with zipfile.ZipFile(archive) as bundle:
            paths = bundle.namelist()
            self.assertEqual(len(paths), 11)
            self.assertFalse(any('__pycache__' in p or p.endswith('.svg') for p in paths))
            self.assertEqual(bundle.read('assessment-item-designer/assets/AID.png'),
                             (ROOT / 'assets/AID.png').read_bytes())
        self.build()
        self.assertEqual(original, archive.read_bytes())

    def test_missing_icon_blocks_package(self):
        (self.root / 'assets/AID.png').unlink()
        with self.assertRaisesRegex(ValueError, 'Missing icon'):
            self.build()

    def test_corrupt_icon_blocks_package(self):
        icon = self.root / 'assets/AID.png'
        data = bytearray(icon.read_bytes())
        data[50] ^= 1
        icon.write_bytes(data)
        with self.assertRaises(ValueError):
            self.build()

    def test_manifest_only_version_bump_is_rejected(self):
        path = self.root / 'plugin.json'
        data = json.loads(path.read_text())
        data['version'] = '2026.13.0'
        path.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, 'out of sync'):
            self.build()

    def test_symlinks_are_rejected(self):
        (self.root / 'skills/assessment-item-designer/leak.txt').symlink_to(ROOT / 'README.md')
        with self.assertRaisesRegex(ValueError, 'Symlink'):
            self.build()

    def test_old_validator_version_is_rejected(self):
        path = self.root / 'skills/assessment-item-designer/scripts/validate_audit.py'
        path.write_text(path.read_text().replace('RELEASE = "2026.12"', 'RELEASE = "2026.11"'))
        with self.assertRaisesRegex(ValueError, 'Audit validator version'):
            self.build()


class PublicationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.manifest, self.archive = release.build_package(ROOT, Path(self.temp.name))
        env = patch.dict(os.environ, {'GITHUB_REF': 'refs/heads/main', 'GITHUB_SHA': 'abc',
                                     'GITHUB_REPOSITORY': 'owner/repo', 'GH_TOKEN': 'test'})
        env.start()
        self.addCleanup(env.stop)

    def test_published_version_is_left_unchanged(self):
        with patch.object(release, 'get_release', return_value={'draft': False, 'html_url': 'url'}), \
                patch.object(release.subprocess, 'run') as run:
            release.publish(ROOT, self.manifest, self.archive)
            run.assert_not_called()

    def test_tag_at_another_commit_is_not_overwritten(self):
        tag = subprocess.CompletedProcess([], 0, stdout='different\n')
        with patch.object(release, 'get_release', return_value=None), \
                patch.object(release.subprocess, 'check_output', return_value='abc\n'), \
                patch.object(release.subprocess, 'run', return_value=tag) as run:
            with self.assertRaisesRegex(ValueError, 'another commit'):
                release.publish(ROOT, self.manifest, self.archive)
            self.assertEqual(run.call_count, 1)

    def test_upload_failure_leaves_release_as_draft(self):
        missing = subprocess.CompletedProcess([], 1, stdout='')
        with patch.object(release, 'get_release', return_value=None), \
                patch.object(release.subprocess, 'check_output', return_value='abc\n'), \
                patch.object(release.subprocess, 'run', side_effect=[missing,
                    subprocess.CalledProcessError(1, ['gh', 'release', 'create'])]) as run:
            with self.assertRaises(subprocess.CalledProcessError):
                release.publish(ROOT, self.manifest, self.archive)
            self.assertFalse(any('edit' in call.args[0] for call in run.call_args_list))

    def test_first_release_is_uploaded_before_publication(self):
        missing = subprocess.CompletedProcess([], 1, stdout='')
        saved = {'draft': False, 'html_url': 'url', 'assets': [{'name': self.archive.name}]}
        with patch.object(release, 'get_release', side_effect=[None, saved]), \
                patch.object(release.subprocess, 'check_output', return_value='abc\n'), \
                patch.object(release.subprocess, 'run', return_value=missing) as run:
            release.publish(ROOT, self.manifest, self.archive)
            commands = [call.args[0] for call in run.call_args_list]
            self.assertIn('create', commands[1])
            self.assertIn(str(self.archive), commands[1])
            self.assertIn('--draft', commands[1])
            self.assertIn('edit', commands[2])
            self.assertIn('--draft=false', commands[2])

    def test_api_permission_failure_is_not_treated_as_missing_release(self):
        error = urllib.error.HTTPError('url', 403, 'Forbidden', {}, None)
        with patch.object(release.urllib.request, 'urlopen', side_effect=error):
            with self.assertRaises(urllib.error.HTTPError):
                release.get_release('owner/repo', 'v2026.12.0')

    def test_retry_resumes_draft_without_overwriting_assets(self):
        missing = subprocess.CompletedProcess([], 1, stdout='')
        draft = {'draft': True, 'target_commitish': 'abc', 'assets': []}
        saved = {'draft': False, 'html_url': 'url', 'assets': [{'name': self.archive.name}]}
        with patch.object(release, 'get_release', side_effect=[draft, saved]), \
                patch.object(release.subprocess, 'check_output', return_value='abc\n'), \
                patch.object(release.subprocess, 'run', return_value=missing) as run:
            release.publish(ROOT, self.manifest, self.archive)
            commands = [call.args[0] for call in run.call_args_list]
            self.assertIn('upload', commands[1])
            self.assertNotIn('--clobber', commands[1])
            self.assertIn('edit', commands[2])

    def test_different_draft_asset_is_not_replaced(self):
        tag = subprocess.CompletedProcess([], 0, stdout='abc\n')
        draft = {'draft': True, 'assets': [{'name': self.archive.name, 'digest': 'sha256:different'}]}
        with patch.object(release, 'get_release', return_value=draft), \
                patch.object(release.subprocess, 'check_output', return_value='abc\n'), \
                patch.object(release.subprocess, 'run', return_value=tag) as run:
            with self.assertRaisesRegex(ValueError, 'refusing to overwrite'):
                release.publish(ROOT, self.manifest, self.archive)
            self.assertEqual(run.call_count, 1)

    def test_non_main_publish_is_rejected(self):
        with patch.dict(os.environ, {'GITHUB_REF': 'refs/heads/feature'}):
            with self.assertRaisesRegex(ValueError, 'restricted to main'):
                release.publish(ROOT, self.manifest, self.archive)


if __name__ == '__main__':
    unittest.main()
