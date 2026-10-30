"""Packaging contract: Tutor distributes skills without server connections."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

PACKAGE = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location(
    'package_validator', PACKAGE / 'skills/instructions/scripts/validate_package.py')
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class SkillsOnlyPackageContract(unittest.TestCase):
    def test_current_package_has_no_server_declarations(self):
        root = json.loads((PACKAGE / 'plugin.json').read_text())
        overlay = json.loads((PACKAGE / '.codex-plugin/plugin.json').read_text())
        self.assertTrue(validator.validate_skills_only_package(PACKAGE, root, overlay))

    def test_package_without_connections_is_accepted(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertTrue(validator.validate_skills_only_package(
                Path(directory), {'extensions': {'com.openai': {}}}, {'skills': './skills'}))

    def test_autodiscovered_configuration_files_are_rejected(self):
        for filename in ('mcp.json', '.mcp.json'):
            with self.subTest(filename=filename), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                (root / filename).write_text('{}')
                with self.assertRaisesRegex(AssertionError, 'configuration file'):
                    validator.validate_skills_only_package(root, {}, {})

    def test_manifest_server_declarations_are_rejected(self):
        for location in ('portable', 'openai', 'codex'):
            for declaration in ('./connections.json', {'example': {'url': 'https://example.invalid'}}, {}):
                with self.subTest(location=location, declaration=declaration):
                    root = {'extensions': {'com.openai': {}}}
                    overlay = {}
                    target = {'portable': root, 'openai': root['extensions']['com.openai'],
                              'codex': overlay}[location]
                    target['mcpServers'] = declaration
                    with tempfile.TemporaryDirectory() as directory:
                        with self.assertRaisesRegex(AssertionError, 'server declaration'):
                            validator.validate_skills_only_package(Path(directory), root, overlay)


if __name__ == '__main__':
    unittest.main()
