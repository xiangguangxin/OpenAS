import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

PLUGIN = Path(__file__).parents[2]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


h = module('customer_harness', PLUGIN/'workflows/codex-team.py')
g = module('customer_graph', PLUGIN/'workflows/graph-runner.py')
w = module('customer_workspace', PLUGIN/'workflows/workspace-tools.py')
installer = module('customer_installer', PLUGIN/'integrations/codex_skills.py')
TASK = {'requirement': 'Produce good text', 'workflow': 'direct', 'scope': ['a.txt'],
        'acceptance': ['Text is good'], 'acceptance_checks': [[0]],
        'checks': [[sys.executable, '-c', "from pathlib import Path; assert Path('a.txt').read_text() == 'good'"]]}


class CustomerWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.workspace = self.root/'project'
        self.workspace.mkdir()
        (self.workspace/'a.txt').write_text('old')

    def call(self, runner, role, phase, context, allowed):
        if role == 'developer':
            (runner.workspace/'a.txt').write_text('good')
        return {'verdict': 'pass' if role == 'verifier' else 'complete',
                'summary': 'Simulated client', 'findings': [], 'evidence': ['fixture']}

    def test_same_project_workspace_keeps_memory_and_records_outcome(self):
        runner = h.Runner(TASK, self.workspace, self.root/'run', 'unused',
                          memory_enabled=True, project_root=self.workspace)
        with patch.object(runner, 'call', side_effect=lambda *args: self.call(runner, *args)):
            self.assertTrue(runner.run())
        self.assertTrue(runner.state['memory_status']['active'])
        self.assertIn('memory_record_id', runner.state)
        self.assertTrue((self.workspace/'.openas/memory/records.json').is_file())
        self.assertFalse(any('.openas/memory' in p for p in runner.snapshot()))
        self.assertEqual(runner.state['acceptance_summary']['status'], 'automated_checks_passed')
        (self.workspace/'outside.txt').write_text('bad')
        with self.assertRaises(h.HarnessError):
            runner.check_scope()

    def test_learning_can_start_with_colocated_memory(self):
        runner = h.Runner(TASK, self.workspace, self.root/'run', 'unused',
                          memory_enabled=True, project_root=self.workspace, learning_enabled=True)
        self.assertIsNotNone(runner.learning)

    def test_reserved_memory_cannot_hide_requested_source_changes(self):
        for scope in (['.openas/memory/a.py'], ['.openas/memory']):
            with self.assertRaises(h.HarnessError):
                h.validate_task({**TASK, 'scope': scope})

    def test_unmapped_criteria_are_visible_in_json_and_escaped_html(self):
        task = {**TASK, 'requirement': '<script>alert(1)</script>', 'acceptance': ['<img src=x>']}
        task.pop('acceptance_checks')
        runner = h.Runner(task, self.workspace, self.root/'run', 'unused')
        with patch.object(runner, 'call', side_effect=lambda *args: self.call(runner, *args)):
            self.assertTrue(runner.run())
        self.assertEqual(runner.state['acceptance_summary']['status'], 'needs_manual_review')
        report = (runner.output/'report.html').read_text()
        self.assertIn('&lt;script&gt;', report)
        self.assertNotIn('<script>', report)
        self.assertIn('needs_manual_review', report)

    def graph(self):
        other = self.root/'second'; other.mkdir(); (other/'a.txt').write_text('old')
        return g.plan_graph({'version': 1, 'nodes': [
            {'id': 'first', 'workspace': str(self.workspace), 'task': TASK},
            {'id': 'second', 'workspace': str(other), 'task': TASK, 'depends_on': ['first']}]}, self.root)

    def test_graph_resume_reuses_completed_node_and_runs_downstream(self):
        nodes = self.graph()
        calls = []
        fail = True
        def call(runner, *args):
            nonlocal fail
            calls.append((runner.workspace.name, args[0]))
            if runner.workspace.name == 'second' and fail:
                fail = False
                raise g.h.HarnessError('simulated disconnect', 'client_failure')
            return self.call(runner, *args)
        with patch.object(g.h.Runner, 'call', call):
            first = g.run_graph(nodes, self.root/'graph', 'unused')
            self.assertEqual(first['status'], 'stopped')
            first_count = sum(name == 'project' for name, _ in calls)
            resumed = g.run_graph(nodes, self.root/'graph', 'unused', resume=True)
        self.assertEqual(resumed['status'], 'verified')
        self.assertEqual(sum(name == 'project' for name, _ in calls), first_count)
        self.assertTrue(resumed['nodes']['second']['dependency_pass'])

    def test_graph_resume_rejects_modified_evidence_and_source(self):
        nodes = self.graph()
        with patch.object(g.h.Runner, 'call', lambda runner, *args: self.call(runner, *args)):
            g.run_graph(nodes, self.root/'graph', 'unused')
        (self.root/'graph/first/report.html').write_text('tampered')
        with self.assertRaisesRegex(g.h.HarnessError, 'evidence'):
            g.run_graph(nodes, self.root/'graph', 'unused', resume=True)
        (self.workspace/'outside.txt').write_text('tampered')
        with self.assertRaisesRegex(g.h.HarnessError, 'workspace changed'):
            g.run_graph(nodes, self.root/'graph', 'unused', resume=True)

    def test_graph_resume_rejects_changed_options_and_concurrent_writer(self):
        nodes = self.graph()
        with patch.object(g.h.Runner, 'call', lambda runner, *args: self.call(runner, *args)):
            g.run_graph(nodes, self.root/'graph', 'unused')
        with self.assertRaisesRegex(g.h.HarnessError, 'options'):
            g.run_graph(nodes, self.root/'graph', 'different-client', resume=True)
        with patch.object(g.h.MEMORY_MODULE.support, 'lock', side_effect=BlockingIOError):
            with self.assertRaisesRegex(g.h.HarnessError, 'already active'):
                g.run_graph(nodes, self.root/'graph', 'unused', resume=True)

    def test_graph_outputs_cannot_hide_another_nodes_source(self):
        first = {'id': 'first', 'workspace': str(self.workspace), 'task': {**TASK, 'artifacts': ['build']}}
        second = {'id': 'second', 'depends_on': ['first'], 'workspace': str(self.workspace),
                  'task': {**TASK, 'scope': ['build/source.py']}}
        with self.assertRaisesRegex(g.h.HarnessError, 'artifact'):
            g.plan_graph({'version': 1, 'nodes': [first, second]}, self.root)

    def test_prepare_omits_existing_outputs_and_does_not_modify_source(self):
        (self.workspace/'build').mkdir(); (self.workspace/'build/cache').write_text('old cache')
        (self.workspace/'.git').mkdir(); (self.workspace/'.git/config').write_text('private')
        task = {**TASK, 'artifacts': ['build']}
        self.assertFalse(w.inspect(self.workspace, task)['direct_run_ready'])
        output = self.root/'prepared'
        w.prepare(self.workspace, output, task)
        self.assertEqual((output/'workspace/a.txt').read_text(), 'old')
        self.assertFalse((output/'workspace/build').exists())
        self.assertFalse((output/'workspace/.git').exists())
        self.assertEqual((self.workspace/'build/cache').read_text(), 'old cache')

    @unittest.skipIf(sys.platform == 'win32', 'Creating symlinks requires Windows developer mode')
    def test_prepare_materializes_internal_links_and_rejects_escape_and_cycles(self):
        link = self.workspace/'alias.txt'
        link.symlink_to(self.workspace/'a.txt')
        w.prepare(self.workspace, self.root/'internal', TASK, materialize=True)
        self.assertFalse((self.root/'internal/workspace/alias.txt').is_symlink())
        link.unlink(); link.symlink_to(self.root)
        with self.assertRaisesRegex(ValueError, 'escapes'):
            w.prepare(self.workspace, self.root/'external', TASK, materialize=True)
        self.assertFalse((self.root/'external').exists())
        link.unlink(); link.symlink_to(self.workspace)
        with self.assertRaisesRegex(ValueError, 'cycle'):
            w.prepare(self.workspace, self.root/'cycle', TASK, materialize=True)

    def test_installer_preserves_resources_and_refuses_local_edit_overwrite(self):
        result = installer.install(self.workspace)
        self.assertEqual(len(result['skills']), 66)
        wrapper = self.workspace/'.agents/skills/openas-bug-fix/SKILL.md'
        self.assertIn('name: openas-bug-fix', wrapper.read_text())
        self.assertTrue((wrapper.parent/'../../openas/skills/bug-fix/SKILL.md').resolve().is_file())
        self.assertTrue(installer.install(self.workspace, 'check')['source_matches'])
        installer.install(self.workspace, 'update')
        wrapper.write_text('local edits')
        with self.assertRaisesRegex(ValueError, 'changed'):
            installer.install(self.workspace, 'update')
        with self.assertRaisesRegex(ValueError, 'changed'):
            installer.install(self.workspace, 'uninstall')
        self.assertEqual(wrapper.read_text(), 'local edits')

    def test_installer_uninstall_preserves_other_skills_and_project_memory(self):
        other = self.workspace/'.agents/skills/other/SKILL.md'
        other.parent.mkdir(parents=True); other.write_text('keep')
        memory = self.workspace/'.openas/memory/keep.txt'
        memory.parent.mkdir(parents=True); memory.write_text('keep')
        installer.install(self.workspace)
        installer.install(self.workspace, 'uninstall')
        self.assertEqual(other.read_text(), 'keep')
        self.assertEqual(memory.read_text(), 'keep')
        self.assertFalse((self.workspace/'.agents/openas').exists())


if __name__ == '__main__':
    unittest.main()
