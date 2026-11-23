"""Synthetic audit consistency checks; no target scanning or model calls."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT/'plugins/openas/skills/security-review/scripts/check_audit.py'
EXAMPLE = ROOT/'plugins/openas/skills/security-review/references/audit-example.json'


def checker():
    spec = importlib.util.spec_from_file_location('audit_checker', SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class AuditRecordTests(unittest.TestCase):
    def setUp(self):
        self.check = checker().validate
        self.data = json.loads(EXAMPLE.read_text())

    def confirmed(self):
        data = copy.deepcopy(self.data)
        data['run_status'] = 'complete'
        del data['incomplete_reason']
        data['coverage'][0]['status'] = 'checked'
        finding = data['findings'][0]
        finding['status'] = 'confirmed'
        del finding['blocker'], finding['validation_plan']
        finding.update(severity='high', author='source-reviewer', verified_by='independent-reviewer',
                       verification_evidence=['Synthetic two-tenant regression result'],
                       fix='Enforce tenant ownership', regression_plan='Verify both allowed and denied access')
        return data

    def test_example_is_explicitly_incomplete(self):
        result = self.check(self.data)
        self.assertEqual(result['run_status'], 'incomplete')
        self.assertEqual(result['needs_validation'], 1)
        self.assertIn('not evidence authenticity', result['authority'])

    def test_confirmed_requires_independent_record_and_checked_unit(self):
        data = self.confirmed()
        self.assertEqual(self.check(data)['confirmed'], 1)
        for field in ('author', 'verified_by', 'verification_evidence', 'fix', 'regression_plan', 'severity'):
            bad = copy.deepcopy(data); bad['findings'][0].pop(field)
            with self.subTest(field=field), self.assertRaises(ValueError): self.check(bad)
        data['findings'][0]['verified_by'] = data['findings'][0]['author']
        with self.assertRaises(ValueError): self.check(data)
        data = self.confirmed(); data['coverage'][0]['status'] = 'blocked'
        data['run_status'] = 'incomplete'; data['incomplete_reason'] = 'blocked'
        with self.assertRaises(ValueError): self.check(data)

    def test_partial_coverage_cannot_claim_complete(self):
        data = copy.deepcopy(self.data); data['run_status'] = 'complete'
        data.pop('incomplete_reason')
        with self.assertRaises(ValueError): self.check(data)
        data = copy.deepcopy(self.data); data.pop('incomplete_reason')
        with self.assertRaises(ValueError): self.check(data)

    def test_unconfirmed_has_no_severity_and_requires_validation_plan(self):
        for edit in ('severity', 'blocker', 'validation_plan'):
            bad = copy.deepcopy(self.data)
            if edit == 'severity': bad['findings'][0]['severity'] = 'low'
            else: bad['findings'][0].pop(edit)
            with self.subTest(edit=edit), self.assertRaises(ValueError): self.check(bad)

    def test_references_fingerprints_and_boundary_are_consistent(self):
        for edit in ('missing_unit', 'duplicate_fingerprint', 'duplicate_id', 'boundary', 'empty_evidence'):
            bad = copy.deepcopy(self.data)
            if edit == 'missing_unit': bad['findings'][0]['unit_id'] = 'absent'
            if edit == 'duplicate_fingerprint':
                item = copy.deepcopy(bad['findings'][0]); item['id'] = 'F-02'; bad['findings'].append(item)
            if edit == 'duplicate_id': bad['coverage'].append(copy.deepcopy(bad['coverage'][0]))
            if edit == 'boundary': bad['findings'][0]['boundary'] = 'unrelated boundary'
            if edit == 'empty_evidence': bad['findings'][0]['evidence'] = []
            with self.subTest(edit=edit), self.assertRaises(ValueError): self.check(bad)

    def test_rejected_requires_reason_and_out_of_scope_is_not_checked(self):
        data = copy.deepcopy(self.data); data['findings'][0]['status'] = 'rejected'
        with self.assertRaises(ValueError): self.check(data)
        data['findings'][0]['reason'] = 'No boundary violation'
        self.assertEqual(self.check(data)['rejected'], 1)
        data['coverage'][0]['status'] = 'out_of_scope'
        with self.assertRaises(ValueError): self.check(data)

    def test_malformed_types_fail_cleanly(self):
        for bad in ([], None, {'version': True}, {**self.data, 'coverage': [None]},
                    {**self.data, 'findings': [None]}, {**self.data, 'scope': 'path'}):
            with self.subTest(bad=bad), self.assertRaises(ValueError): self.check(bad)

    def test_cli_is_readonly_and_invalid_records_return_nonzero(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'audit.json'; path.write_text(json.dumps(self.data))
            before = path.read_bytes()
            run = subprocess.run([sys.executable, '-B', str(SCRIPT), str(path)], capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(path.read_bytes(), before)
            self.assertEqual(set(Path(tmp).iterdir()), {path})
            path.write_text('{"version":1,"version":1}')
            run = subprocess.run([sys.executable, '-B', str(SCRIPT), str(path)], capture_output=True, text=True)
            self.assertNotEqual(run.returncode, 0)
            self.assertNotIn('Traceback', run.stderr)


if __name__ == '__main__':
    unittest.main()
