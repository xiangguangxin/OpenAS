import importlib.util
from pathlib import Path
import unittest

SPEC = importlib.util.spec_from_file_location('ci_gate', Path(__file__).resolve().parents[1]/'scripts/configure_ci_gate.py')
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)


class GateTests(unittest.TestCase):
    def test_existing_protection_is_never_overwritten(self):
        calls = []
        def api(method, path, data=None):
            calls.append(method)
            return {'protected': True}
        with self.assertRaises(RuntimeError):
            gate.apply_gate(api, 'owner/repo', 'main')
        self.assertEqual(calls, ['GET'])

    def test_success_requires_readback_of_status_checks_and_admin_enforcement(self):
        methods = []
        def api(method, path, data=None):
            methods.append(method)
            if path.endswith('/protection'):
                return {'required_status_checks': {'strict': True, 'checks': [{'context': 'checks'}]},
                        'enforce_admins': {'enabled': True},
                        'required_pull_request_reviews': {'required_approving_review_count': 0}}
            return {'protected': False}
        gate.apply_gate(api, 'owner/repo', 'main')
        self.assertEqual(methods, ['GET', 'PUT', 'GET'])

    def test_incomplete_readback_is_not_reported_as_success(self):
        def api(method, path, data=None):
            return {'protected': False} if not path.endswith('/protection') else {}
        with self.assertRaises(RuntimeError):
            gate.apply_gate(api, 'owner/repo', 'main')
