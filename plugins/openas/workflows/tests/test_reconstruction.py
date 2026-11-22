"""Native reconstruction: actual subprocess observers, synthetic references and mock model phases."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

PLUGIN = Path(__file__).parents[2]
SOURCE = PLUGIN/'skills/software-reconstruction/scripts/reconstruction.py'
EXAMPLE = PLUGIN/'workflows/examples/reconstruction'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


m = load('reconstruction_tests', SOURCE)
h = load('reconstruction_test_harness', PLUGIN/'workflows/codex-team.py')
GOOD = '''def total(items):
    if any(type(x) not in (int, float) for x in items):
        raise ValueError('Numeric items required')
    return sum(items)
'''


class ReconstructionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.brief = json.loads((EXAMPLE/'brief.json').read_text(encoding='utf-8'))
        self.brief['collector'][0] = sys.executable
        shutil.copyfile(EXAMPLE/'observer.py', self.root/'observer.py')
        self.path = self.root/'brief.json'
        self.project = self.root/'project'

    def prepare(self):
        self.path.write_text(json.dumps(self.brief), encoding='utf-8')
        return m.prepare(self.path, self.project)

    def test_prepare_is_offline_and_pins_its_observer_outside_candidate(self):
        result = self.prepare()
        project = m.load_project(self.project)
        self.assertEqual(result['case_count'], 4)
        self.assertEqual(result['mode'], 'clean-room')
        self.assertTrue(all(r['authority'] == 'provided-artifact' for r in project['observations']))
        self.assertEqual(list((self.project/'workspace').iterdir()), [])
        self.assertTrue(project['collector'][1].startswith(str(self.project/'capture')))
        self.assertFalse((self.project/'run').exists())

    def test_modes_fail_closed_and_do_not_invent_deep_authorization(self):
        for kind in ('source', 'binary', 'network', 'new-unknown-tool'):
            brief = deepcopy(self.brief)
            brief['observations'][0]['kind'] = kind
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                m.validate(brief)
        self.brief['mode'] = 'deep'
        self.brief['observations'][0]['kind'] = 'source'
        self.assertEqual(m.validate(self.brief)['mode'], 'deep')
        self.brief['authorization'] = ''
        with self.assertRaises(ValueError):
            m.validate(self.brief)

    def test_only_inferred_reference_cannot_ground_a_comparison(self):
        self.brief['observations'][0]['confidence'] = 'inferred'
        with self.assertRaisesRegex(ValueError, 'inferred'):
            m.validate(self.brief)

    def test_reference_or_observer_changes_invalidate_the_study(self):
        self.prepare()
        observer = self.project/m.load_project(self.project)['collector_files'][0]
        observer.write_text('print("forged pass")')
        with self.assertRaisesRegex(ValueError, 'changed'):
            m.load_project(self.project)

    def test_seal_cannot_omit_the_observer_and_relocated_projects_cannot_execute_old_paths(self):
        self.prepare()
        relocated = self.root/'relocated'
        shutil.copytree(self.project, relocated)
        with self.assertRaisesRegex(ValueError, 'relocation'):
            m.check(relocated, relocated/'workspace')
        seal = m.read(self.project/'seal.json')
        observer = m.load_project(self.project)['collector_files'][0]
        del seal['files'][observer]
        m.atomic(self.project/'seal.json', seal)
        with self.assertRaisesRegex(ValueError, 'omitted'):
            m.load_project(self.project)

    def test_browse_is_bounded_and_reports_only_stored_coverage(self):
        self.prepare()
        first = m.browse(self.project, 0, 2)
        self.assertEqual(first['coverage']['status'], 'partial')
        self.assertEqual(first['coverage']['next_offset'], 2)
        self.assertEqual(m.browse(self.project, 2, 2)['coverage']['status'], 'complete')
        for offset, limit in ((-1, 1), (0, 51), (False, 2)):
            with self.assertRaises(ValueError):
                m.browse(self.project, offset, limit)

    def test_unknowns_need_supported_evidence_and_current_revision(self):
        self.brief['unknowns'][0]['severity'] = 'high'
        self.prepare()
        blocked = m.check(self.project, self.project/'workspace')
        self.assertFalse(blocked['passed'])
        self.assertFalse(blocked['collector_started'])
        with self.assertRaises(ValueError):
            m.resolve(self.project, 'U1', 1, 'guess', [])
        row = m.resolve(self.project, 'U1', 1, 'Checked the bounded fixture contract', ['empty'])
        self.assertEqual(row['revision'], 2)
        with self.assertRaisesRegex(ValueError, 'stale'):
            m.resolve(self.project, 'U1', 1, 'old update', ['empty'])
        ledger = m.read(self.project/'questions.json')
        ledger['questions'][0]['evidence'] = []
        m.atomic(self.project/'questions.json', ledger)
        with self.assertRaisesRegex(ValueError, 'evidence'):
            m.questions(self.project)

    def test_behavior_checks_execute_candidate_and_replace_stale_success(self):
        self.prepare()
        app = self.project/'workspace/app.py'
        app.write_text(GOOD)
        result = m.check(self.project, self.project/'workspace')
        self.assertTrue(result['passed'])
        app.write_text('def total(items): return True\n')
        result = m.check(self.project, self.project/'workspace')
        self.assertFalse(result['passed'])
        self.assertFalse(m.read(self.project/'workspace/reconstruction-results/comparison.json')['passed'])
        app.write_text('raise RuntimeError("cannot start")\n')
        self.assertFalse(m.check(self.project, self.project/'workspace')['passed'])

    def test_strict_json_missing_case_and_context_type_fail(self):
        self.prepare()
        project = m.load_project(self.project)
        project['cases'] = [{'id': 'one', 'kind': 'behavior', 'expected': 1, 'evidence': ['empty'], 'context': {'width': 1}}]
        for cases in ({}, {'one': {'value': True, 'context': {'width': 1}}},
                      {'one': {'value': 1, 'context': {'width': True}}}):
            self.assertFalse(m.compare(project, {'cases': cases}, self.project/'workspace', self.project)['passed'])

    def fake_harness(self, name, path):
        return h if name in ('reconstruction_run_harness', 'reconstruction_check_harness') else load(name, path)

    def test_timeout_cannot_leave_an_old_pass_receipt(self):
        self.prepare()
        folder = self.project/'workspace/reconstruction-results'
        folder.mkdir()
        m.atomic(folder/'comparison.json', {'passed': True})
        with patch.object(m, 'module', self.fake_harness), patch.object(h, 'execute', side_effect=h.HarnessError('timeout', 'timeout')):
            result = m.check(self.project, self.project/'workspace')
        self.assertFalse(result['passed'])
        self.assertFalse(m.read(folder/'comparison.json')['passed'])

    def test_real_host_comparisons_drive_mock_builder_refinement(self):
        self.prepare()
        calls = []
        def call(runner, role, phase, context, allowed):
            calls.append(role)
            if role == 'developer':
                count = calls.count('developer')
                (runner.workspace/'app.py').write_text('def total(items): return -1\n' if count == 1 else GOOD)
            verdict = 'approve' if role == 'red-team' else 'pass' if role == 'verifier' else 'complete'
            self.assertIn('Study data:', context)
            return {'verdict': verdict, 'summary': 'Synthetic model phase', 'findings': [], 'evidence': ['Fixture phase; actual observer runs separately']}
        with patch.object(m, 'module', self.fake_harness), patch.object(h.Runner, 'call', call), patch.object(m.shutil, 'which', return_value=sys.executable):
            result = m.run(self.project)
        self.assertTrue(result['done'], result)
        self.assertEqual(calls.count('developer'), 2)
        state = m.read(self.project/'run/state.json')
        self.assertNotEqual(state['baseline_checks'][0]['exit_code'], 0)
        self.assertTrue(state['rigor_gate']['passed'])
        self.assertTrue(m.read(self.project/'workspace/reconstruction-results/comparison.json')['passed'])

    def test_idle_builder_stops_and_resume_does_not_reset_progress_budget(self):
        self.prepare()
        calls = []
        def call(runner, role, phase, context, allowed):
            calls.append(role)
            return {'verdict': 'approve' if role == 'red-team' else 'pass' if role == 'verifier' else 'complete',
                    'summary': 'Idle synthetic model', 'findings': [], 'evidence': ['No actual implementation']}
        with patch.object(m, 'module', self.fake_harness), patch.object(h.Runner, 'call', call), patch.object(m.shutil, 'which', return_value=sys.executable):
            first = m.run(self.project)
            self.assertFalse(first['done'])
            self.assertEqual(first['failure']['kind'], 'no_progress')
            self.assertEqual(calls.count('developer'), 2)
            second = m.run(self.project, resume=True)
            self.assertFalse(second['done'])
            self.assertEqual(calls.count('developer'), 2)

    def test_manual_check_results_are_archived_before_first_run(self):
        self.prepare()
        (self.project/'workspace/app.py').write_text(GOOD)
        self.assertTrue(m.check(self.project, self.project/'workspace')['passed'])
        original = (self.project/'workspace/reconstruction-results/comparison.json').read_bytes()
        def call(runner, role, phase, context, allowed):
            return {'verdict': 'approve' if role == 'red-team' else 'pass' if role == 'verifier' else 'complete',
                    'summary': 'Synthetic verification of an existing candidate', 'findings': [], 'evidence': ['Fixture model phase']}
        with patch.object(m, 'module', self.fake_harness), patch.object(h.Runner, 'call', call), patch.object(m.shutil, 'which', return_value=sys.executable):
            self.assertTrue(m.run(self.project)['done'])
        archives = list((self.project/'check-history').glob('*/comparison.json'))
        self.assertEqual(len(archives), 1)
        self.assertEqual(archives[0].read_bytes(), original)

    def test_screenshot_comparison_checks_viewport_and_context(self):
        try:
            from PIL import Image
        except ImportError:
            self.skipTest('Optional Pillow is not installed')
        Image.new('RGB', (100, 60), 'white').save(self.root/'reference.png')
        self.brief['cases'] = [{'id': 'desktop', 'kind': 'screenshot', 'reference': 'reference.png',
            'viewport': [100, 60], 'context': {'state': 'menu-open'}, 'max_mean_error': 0.01, 'evidence': ['empty']}]
        self.prepare()
        folder = self.project/'workspace/reconstruction-results'; folder.mkdir()
        actual = {'cases': {'desktop': {'path': 'reconstruction-results/desktop.png', 'context': {'state': 'menu-open'}}}}
        project = m.load_project(self.project)
        Image.new('RGB', (100, 60), 'white').save(folder/'desktop.png')
        self.assertTrue(m.compare(project, actual, self.project/'workspace', self.project)['passed'])
        Image.new('RGB', (100, 60), 'black').save(folder/'desktop.png')
        self.assertFalse(m.compare(project, actual, self.project/'workspace', self.project)['passed'])
        Image.new('RGB', (50, 60), 'white').save(folder/'desktop.png')
        self.assertEqual(m.compare(project, actual, self.project/'workspace', self.project)['cases'][0]['reason'], 'viewport_or_image_size_mismatch')


if __name__ == '__main__':
    unittest.main()
