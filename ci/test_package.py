"""Exercise package selection and distribution boundaries through the CLI."""

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile


REPOSITORY = Path(__file__).resolve().parent.parent
PACKAGE = REPOSITORY / 'ci/package.py'


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)

    def run_package(self, *args, script=PACKAGE):
        return subprocess.run([sys.executable, '-B', str(script), *map(str, args)],
                              cwd=self.directory, capture_output=True, text=True)

    def test_default_packages_only_tutor_from_another_working_directory(self):
        output = self.directory / 'tutor.zip'
        result = self.run_package(output)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        with zipfile.ZipFile(output) as archive:
            names = archive.namelist()
            self.assertIn('.codex-plugin/plugin.json', names)
            self.assertIn('skills/instructions/SKILL.md', names)
            self.assertNotIn('skills/planning-a-large-project/SKILL.md', names)
            self.assertFalse(any(name.startswith(('src/', 'DevBacklog/', 'ci/')) for name in names))

    def test_devbacklog_archive_runs_without_the_source_installation(self):
        output = self.directory / 'devbacklog.zip'
        result = self.run_package('--plugin', 'devbacklog', output)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        unpacked = self.directory / 'unpacked'
        with zipfile.ZipFile(output) as archive:
            names = archive.namelist()
            manifest = json.loads(archive.read('.codex-plugin/plugin.json'))
            self.assertEqual(manifest['name'], 'devbacklog')
            self.assertIn('plugin.json', names)
            self.assertNotIn('skills/instructions/SKILL.md', names)
            self.assertFalse(any(name.startswith(('src/', 'DevBacklog/', 'ci/')) for name in names))
            archive.extractall(unpacked)
        validator = subprocess.run([sys.executable, '-B', str(unpacked / 'scripts/validate_package.py')],
                                   cwd=self.directory, capture_output=True, text=True)
        self.assertEqual(validator.returncode, 0, validator.stdout + validator.stderr)
        ledger = unpacked / 'skills/planning-a-large-project/scripts/ledger.py'
        created = subprocess.run(
            [sys.executable, '-B', str(ledger), 'init', '--profile', 'directory',
             '--name', 'archive-check', '--path', str(self.directory / 'ledger'),
             '--objective', 'Verify the distributed package'],
            cwd=self.directory, capture_output=True, text=True,
        )
        self.assertEqual(created.returncode, 0, created.stdout + created.stderr)
        protocol = (self.directory / 'ledger/PROTOCOL.md').read_text(encoding='utf-8')
        self.assertIn(str(ledger), protocol)
        self.assertNotIn(str(REPOSITORY), protocol)

    def test_rejects_destinations_in_any_plugin_and_non_zip_outputs(self):
        cases = (
            ('tutor', REPOSITORY / 'src/rejected.zip'),
            ('tutor', REPOSITORY / 'DevBacklog/rejected.zip'),
            ('devbacklog', REPOSITORY / 'src/rejected.zip'),
            ('devbacklog', REPOSITORY / 'DevBacklog/rejected.zip'),
            ('devbacklog', self.directory / 'rejected.tar'),
        )
        for plugin, output in cases:
            with self.subTest(plugin=plugin, output=output):
                result = self.run_package('--plugin', plugin, output)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertFalse(output.exists())

    def test_missing_dependency_prevents_replacing_an_archive(self):
        copy = self.directory / 'repository'
        (copy / 'ci').mkdir(parents=True)
        shutil.copy2(PACKAGE, copy / 'ci/package.py')
        shutil.copytree(REPOSITORY / 'DevBacklog', copy / 'DevBacklog')
        (copy / 'DevBacklog/skills/planning-a-large-project/assets/templates/task.md').unlink()
        output = self.directory / 'existing.zip'
        output.write_bytes(b'previous distribution')
        result = self.run_package('--plugin', 'devbacklog', output, script=copy / 'ci/package.py')
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn('assets/templates/task.md', result.stdout)
        self.assertEqual(output.read_bytes(), b'previous distribution')


if __name__ == '__main__':
    unittest.main()
