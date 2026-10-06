"""Tests for the informational inventory of dated citations."""
from pathlib import Path
import importlib.util
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parent / 'validate_package.py'
spec = importlib.util.spec_from_file_location('package_validator', SCRIPT)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class DatedCitationTests(unittest.TestCase):
    def inventory(self, text):
        with tempfile.TemporaryDirectory() as root:
            module = Path(root) / 'references/operations/example.md'
            module.parent.mkdir(parents=True)
            module.write_text(text, encoding='utf-8')
            return validator.dated_citations(Path(root))

    def test_finds_consulted_dates_with_location(self):
        found = self.inventory('Linha.\nEvidência consultada em 2026-10-05: fonte.\nConsulta: 2026-10-06\n')
        self.assertEqual(found, [('references/operations/example.md', 2, '2026-10-05'),
                                 ('references/operations/example.md', 3, '2026-10-06')])

    def test_ignores_dates_outside_citation_lines(self):
        self.assertEqual(self.inventory('Prazo fictício 2026-10-05 sem relação.\n'), [])

    def test_malformed_date_is_reported_not_ignored(self):
        with self.assertRaises(AssertionError):
            self.inventory('Consultado em 2026-13-45.\n')

    def test_package_reports_its_known_citations(self):
        found = validator.dated_citations(SCRIPT.parent.parent)
        self.assertTrue({'2026-10-05', '2026-10-06'} <= {date for _, _, date in found})


if __name__ == '__main__':
    unittest.main()
