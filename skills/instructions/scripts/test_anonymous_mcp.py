"""Deployment contract: academic retrieval must not request student credentials."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest
import tempfile

PACKAGE = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location(
    'package_validator', PACKAGE / 'skills/instructions/scripts/validate_package.py')
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)

CONFIG = {
    '$schema': 'https://agent-plugins.org/schemas/1.0.0/mcp.schema.json',
    'mcpServers': {'firecrawl-keyless': {
        'type': 'streamable-http', 'url': 'https://mcp.firecrawl.dev/v2/mcp'}}}


class AnonymousMCPContract(unittest.TestCase):
    def setUp(self):
        if self._testMethodName.endswith('_is_rejected') and not callable(
                getattr(validator, 'validate_anonymous_mcp', None)):
            self.skipTest('Rejection checks await the missing validator')

    def validate(self, config):
        check = getattr(validator, 'validate_anonymous_mcp', None)
        self.assertTrue(callable(check), 'Anonymous MCP validation is missing')
        return check(config)

    def test_published_connection_has_no_student_authentication(self):
        path = PACKAGE / 'mcp.json'
        self.assertTrue(path.is_file(), 'Verified keyless connection is not configured')
        self.validate(json.loads(path.read_text()))

    def test_anonymous_remote_configuration_is_accepted(self):
        self.assertTrue(self.validate(deepcopy(CONFIG)))

    def test_bearer_header_is_rejected(self):
        config = deepcopy(CONFIG)
        config['mcpServers']['firecrawl-keyless']['headers'] = {
            'Authorization': 'Bearer ${FIRECRAWL_API_KEY}'}
        with self.assertRaises(AssertionError):
            validator.validate_anonymous_mcp(config)

    def test_credential_environment_is_rejected(self):
        config = deepcopy(CONFIG)
        config['mcpServers']['firecrawl-keyless']['env'] = {'API_KEY': 'fixture'}
        with self.assertRaises(AssertionError):
            validator.validate_anonymous_mcp(config)

    def test_oauth_endpoint_is_rejected(self):
        config = deepcopy(CONFIG)
        config['mcpServers']['firecrawl-keyless']['url'] += '-oauth'
        with self.assertRaises(AssertionError):
            validator.validate_anonymous_mcp(config)

    def test_key_in_url_is_rejected(self):
        config = deepcopy(CONFIG)
        config['mcpServers']['firecrawl-keyless']['url'] += '?api_key=fixture'
        with self.assertRaises(AssertionError):
            validator.validate_anonymous_mcp(config)

    def test_unverified_provider_endpoint_is_rejected(self):
        config = deepcopy(CONFIG)
        config['mcpServers']['crossref'] = {
            'type': 'streamable-http', 'url': 'https://example.invalid/mcp'}
        with self.assertRaises(AssertionError):
            validator.validate_anonymous_mcp(config)

    def test_publisher_generated_empty_headers_are_equivalent(self):
        check = getattr(validator, 'validate_mcp_package', None)
        self.assertTrue(callable(check), 'Publisher normalization is not handled')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'mcp.json').write_text(json.dumps(CONFIG))
            legacy = {'mcpServers': deepcopy(CONFIG['mcpServers'])}
            legacy['mcpServers']['firecrawl-keyless']['headers'] = {}
            (root / '.mcp.json').write_text(json.dumps(legacy))
            self.assertTrue(check(root, {'mcpServers': './.mcp.json'}))

    def test_publisher_configuration_with_credentials_is_rejected(self):
        check = getattr(validator, 'validate_mcp_package', None)
        if not callable(check):
            self.skipTest('Normalization validator is missing')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'mcp.json').write_text(json.dumps(CONFIG))
            legacy = {'mcpServers': deepcopy(CONFIG['mcpServers'])}
            legacy['mcpServers']['firecrawl-keyless']['headers'] = {
                'Authorization': 'Bearer fixture'}
            (root / '.mcp.json').write_text(json.dumps(legacy))
            with self.assertRaises(AssertionError):
                check(root, {'mcpServers': './.mcp.json'})

    def test_missing_publisher_configuration_is_rejected(self):
        check = getattr(validator, 'validate_mcp_package', None)
        if not callable(check):
            self.skipTest('Normalization validator is missing')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'mcp.json').write_text(json.dumps(CONFIG))
            with self.assertRaises((AssertionError, OSError)):
                check(root, {'mcpServers': './.mcp.json'})


if __name__ == '__main__':
    unittest.main()
