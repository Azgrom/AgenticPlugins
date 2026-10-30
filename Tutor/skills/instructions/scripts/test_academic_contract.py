"""Contract tests: cite inspected text, resolve source links, retain unknowns."""
from pathlib import Path
from copy import deepcopy
import importlib.util
import json
import sys
import unittest

PACKAGE = Path(__file__).resolve().parents[3]
if __name__ == '__main__' and len(sys.argv) > 1 and not sys.argv[1].startswith('-'):
    PACKAGE = Path(sys.argv.pop(1)).resolve()
SCRIPT = PACKAGE / 'skills/instructions/scripts/validate_package.py'
spec = importlib.util.spec_from_file_location('package_validator', SCRIPT)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)

REVIEW = {
    'review_id': 'fixture.review', 'schema_version': '1.0',
    'question': 'O estudo sustenta causalidade?', 'mode': 'argument',
    'search_scope': {'kind': 'provided_material', 'queries': [], 'venues': [],
                     'searched_at': None, 'limitations': ['Material sintético; não é busca bibliográfica.']},
    'sources': [{
        'source_id': 'fixture.A', 'title': 'Fonte sintética A', 'authors': [],
        'year': None, 'identifier': None, 'source_ref': 'urn:fixture:A',
        'reading_level': 'FULL_TEXT', 'publication_status': 'UNVERIFIED',
        'integrity_status': 'NOT_CHECKED', 'status_check_ref': None,
        'status_checked_at': None, 'limitations': ['Não é publicação real.']
    }],
    'claims': [{
        'claim_id': 'fixture.claim', 'claim': 'O estudo identifica um efeito causal.',
        'verdict': 'contradicted', 'reason': 'Desenho antes/depois sem controle.',
        'links': [{'source_id': 'fixture.A', 'locator': 'Método, seção 2',
                   'basis': 'INSPECTED_TEXT', 'relation': 'contradicts'}],
        'limitations': ['Conclusão restrita ao material fornecido.']
    }],
    'conclusion': 'O desenho não sustenta a atribuição causal.'
}

class AcademicContract(unittest.TestCase):
    def setUp(self):
        self.check = getattr(validator, 'validate_academic_review', None)

    def test_academic_contract_can_run_without_exam_or_student_records(self):
        self.assertTrue(callable(self.check), 'Academic review contract is missing')
        self.check(deepcopy(REVIEW))

    def assert_rejected(self, mutate):
        if not callable(self.check):
            self.skipTest('Academic contract not implemented')
        review = deepcopy(REVIEW)
        mutate(review)
        with self.assertRaises((AssertionError, ValueError)):
            self.check(review)

    def test_unresolved_source_link_is_rejected(self):
        self.assert_rejected(lambda r: r['claims'][0]['links'][0].update(source_id='missing'))

    def test_metadata_cannot_back_a_claim_about_inspected_text(self):
        self.assert_rejected(lambda r: r['sources'][0].update(reading_level='METADATA_ONLY'))

    def test_inspected_claim_requires_a_locator(self):
        self.assert_rejected(lambda r: r['claims'][0]['links'][0].update(locator=None))

    def test_no_notice_found_requires_an_actual_status_check(self):
        self.assert_rejected(lambda r: r['sources'][0].update(integrity_status='NO_NOTICE_FOUND'))

    def test_retracted_source_cannot_support_an_unqualified_claim(self):
        def mutate(r):
            r['sources'][0].update(integrity_status='RETRACTED', status_check_ref='urn:fixture:notice', status_checked_at='2026-10-06T10:00:00Z')
            r['claims'][0].update(verdict='supported', limitations=[])
            r['claims'][0]['links'][0].update(relation='supports')
        self.assert_rejected(mutate)

    def test_duplicate_source_ids_are_rejected(self):
        self.assert_rejected(lambda r: r['sources'].append(deepcopy(r['sources'][0])))

    def test_bibliographic_search_requires_a_recoverable_scope(self):
        self.assert_rejected(lambda r: r['search_scope'].update(kind='targeted'))

    def test_unresolved_claim_is_valid_when_lack_of_evidence_is_explicit(self):
        if not callable(self.check):
            self.skipTest('Academic contract not implemented')
        review = deepcopy(REVIEW)
        review['sources'] = []
        review['claims'][0].update(verdict='unresolved', links=[], reason='Texto essencial indisponível.')
        self.check(review)

    def test_metadata_basis_requires_material_actually_consulted(self):
        def mutate(r):
            r['sources'][0]['reading_level'] = 'NONE'
            r['claims'][0]['verdict'] = 'unresolved'
            r['claims'][0]['links'][0].update(basis='METADATA', relation='context')
        self.assert_rejected(mutate)

    def test_partial_support_requires_some_supporting_evidence(self):
        self.assert_rejected(lambda r: r['claims'][0].update(verdict='partially_supported'))

if __name__ == '__main__':
    unittest.main()
