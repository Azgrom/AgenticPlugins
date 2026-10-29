"""Tests for links between skills within the portable package."""
from pathlib import Path
import importlib.util
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parent / 'validate_package.py'
spec = importlib.util.spec_from_file_location('package_validator', SCRIPT)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class SkillLinkTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.plugin = Path(self.directory.name)
        self.skill = self.plugin / 'skills/instructions'
        self.entry = self.skill / 'SKILL.md'
        self.style = self.skill / 'references/operations/response_style.md'
        self.language = self.plugin / 'skills/language/SKILL.md'
        for file in (self.entry, self.style, self.language):
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text('# Fixture\n', encoding='utf-8')

    def test_entry_can_route_to_sibling_skill(self):
        self.assertEqual(
            validator.resolve_link(self.entry, '../language/SKILL.md', self.skill),
            self.language.resolve())

    def test_nested_module_can_route_to_sibling_skill(self):
        self.assertEqual(
            validator.resolve_link(self.style, '../../../language/SKILL.md', self.skill),
            self.language.resolve())

    def test_missing_sibling_skill_is_rejected(self):
        with self.assertRaises(AssertionError):
            validator.resolve_link(self.entry, '../missing/SKILL.md', self.skill)

    def test_existing_file_outside_skills_is_rejected(self):
        (self.plugin / 'outside.md').write_text('# Outside\n', encoding='utf-8')
        with self.assertRaises(AssertionError):
            validator.resolve_link(self.entry, '../../outside.md', self.skill)


if __name__ == '__main__':
    unittest.main()
