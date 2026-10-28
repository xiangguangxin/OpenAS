import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

SPEC = importlib.util.spec_from_file_location('backend_harness', Path(__file__).parents[1]/'codex-team.py')
h = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(h)
b = h.BACKENDS
TASK = {'workflow': 'direct', 'requirement': 'Repair a.txt', 'scope': ['a.txt'],
        'acceptance': ['good content'], 'checks': [[sys.executable, '-c',
        "from pathlib import Path; assert Path('a.txt').read_text() == 'good'"]]}


class FixtureBackend(b.AgentBackend):
    name = 'fixture'
    capabilities = frozenset({'read-only', 'workspace-write', 'structured-output', 'timeout', 'cancellation'})

    def prepare(self, request):
        self.validate(request)
        return b.AgentInvocation(request, ('fixture-agent',))

    def run(self, invocation, execute):
        request = invocation.request
        if request.access == 'workspace-write':
            (request.workspace/'a.txt').write_text('good')
        request.stdout_file.write_text('fixture output')
        request.stderr_file.write_text('')
        request.result_file.write_text(json.dumps({
            'verdict': 'complete' if request.access == 'workspace-write' else 'pass',
            'summary': 'fixture', 'findings': [], 'evidence': ['actual host check still required']}))
        return b.AgentResult(0)


class BackendTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.workspace = self.root/'work'
        self.workspace.mkdir()
        (self.workspace/'a.txt').write_text('old')
        self.output = self.root/'run'

    def request(self, **changes):
        request = b.AgentRequest('codex-fixture', self.workspace, 'fixture prompt', 'read-only', 5,
                                 self.root/'schema.json', self.root/'result.json',
                                 self.root/'stdout.log', self.root/'stderr.log')
        return request._replace(**changes)

    def runner(self, **changes):
        return h.Runner(TASK, self.workspace, self.output, 'unused', rounds=1, **changes)

    def test_codex_preserves_sandbox_schema_and_process_contract(self):
        backend = b.CodexBackend()
        for access in ('read-only', 'workspace-write'):
            request = self.request(access=access)
            invocation = backend.prepare(request)
            argv = list(invocation.argv)
            self.assertEqual(argv[:3], ['codex-fixture', 'exec', '--ephemeral'])
            self.assertEqual(argv[argv.index('--sandbox') + 1], access)
            self.assertEqual(argv[argv.index('--output-schema') + 1], str(request.schema_file))
            self.assertEqual(argv[argv.index('-o') + 1], str(request.result_file))
            execute = Mock(return_value=7)
            self.assertEqual(backend.run(invocation, execute).exit_code, 7)
            execute.assert_called_once_with(argv, request.workspace, request.timeout,
                                            request.stdout_file, request.stderr_file, request.prompt)

    def test_search_controls_and_native_evidence_are_provider_owned(self):
        backend = b.CodexBackend()
        for mode in ('disabled', 'live'):
            request = self.request(search_mode=mode, execution_events=True)
            invocation = backend.prepare(request)
            self.assertIn('--json', invocation.argv)
            self.assertIn('web_search="' + mode + '"', invocation.argv)
            request.stdout_file.write_text('\n'.join([
                'model claims it searched', '{}',
                json.dumps({'type': 'item.started', 'item': {'type': 'web_search'}}),
                json.dumps({'type': 'item.completed', 'item': {'type': 'web_search'}})]))
            result = backend.run(invocation, Mock(return_value=0))
            self.assertEqual(result.native_search_count, 1 if mode == 'live' else 0)

    def test_invalid_request_modes_never_launch(self):
        backend = b.CodexBackend()
        for changes in ({'access': 'unrestricted'}, {'search_mode': 'invented'}, {'timeout': 0}):
            with self.subTest(changes=changes), self.assertRaises(b.BackendError):
                backend.prepare(self.request(**changes))

    def test_missing_capabilities_fail_before_output_or_host_checks(self):
        for capability in FixtureBackend.capabilities:
            backend = FixtureBackend()
            backend.capabilities = FixtureBackend.capabilities - {capability}
            with self.subTest(capability=capability), patch.object(h, 'execute') as execute:
                with self.assertRaisesRegex(h.HarnessError, capability):
                    self.runner(backend=backend)
                execute.assert_not_called()
                self.assertFalse(self.output.exists())

    def test_readonly_workflow_does_not_require_write_capability(self):
        backend = FixtureBackend()
        backend.capabilities -= {'workspace-write'}
        task = {**TASK, 'workflow': 'review'}
        runner = h.Runner(task, self.workspace, self.output, 'unused', backend=backend)
        self.assertEqual(runner.backend.identity(), backend.identity())

    def test_custom_backend_runs_workflow_with_host_acceptance_and_event_identity(self):
        backend = FixtureBackend()
        runner = self.runner(backend=backend)
        self.assertTrue(runner.run())
        self.assertEqual(runner.state['status'], 'verified')
        self.assertEqual(runner.state['backend']['name'], 'fixture')
        self.assertEqual(runner.state['final_checks'][0]['exit_code'], 0)
        events = [json.loads(line) for line in (self.output/'events.jsonl').read_text().splitlines()]
        self.assertEqual(events[0]['data']['backend'], backend.identity())
        self.assertEqual(runner.state['history'][0]['argv'], ['fixture-agent'])

    def test_custom_backend_cannot_bypass_result_validation(self):
        backend = FixtureBackend()
        original = backend.run
        def invalid(invocation, execute):
            result = original(invocation, execute)
            invocation.request.result_file.write_text('{}')
            return result
        backend.run = invalid
        runner = self.runner(backend=backend)
        self.assertFalse(runner.run())
        self.assertEqual(runner.state['failure']['kind'], 'invalid_result')

    def test_custom_backend_cannot_bypass_scope_checks(self):
        backend = FixtureBackend()
        original = backend.run
        def outside(invocation, execute):
            result = original(invocation, execute)
            (self.workspace/'outside.txt').write_text('bad')
            return result
        backend.run = outside
        runner = self.runner(backend=backend)
        self.assertFalse(runner.run())
        self.assertEqual(runner.state['failure']['kind'], 'scope_violation')

    def test_backend_identity_and_capability_changes_block_resume(self):
        backend = FixtureBackend()
        backend.run = Mock(side_effect=b.BackendError('fixture unavailable', 'backend_failure'))
        runner = self.runner(backend=backend)
        self.assertFalse(runner.run())
        self.assertEqual(runner.state['failure']['kind'], 'backend_failure')
        for attribute, value in (('name', 'other'), ('version', 2),
                                 ('capabilities', FixtureBackend.capabilities | {'extra'})):
            changed = FixtureBackend()
            setattr(changed, attribute, value)
            with self.subTest(attribute=attribute), self.assertRaisesRegex(h.HarnessError, 'Backend identity'):
                self.runner(backend=changed, resume=True)

    def test_research_design_requires_search_capabilities_before_start(self):
        task = {**TASK, 'workflow': 'research-design', 'research_mode': 'live',
                'scope': list(h.DESIGN.DEFAULT_OUTPUTS.values())}
        for capability in ('search-control', 'execution-events', 'native-search-evidence'):
            backend = FixtureBackend()
            backend.capabilities = b.CodexBackend.capabilities - {capability}
            with self.subTest(capability=capability), self.assertRaisesRegex(h.HarnessError, capability):
                h.Runner(task, self.workspace, self.output, 'unused', backend=backend)
            self.assertFalse(self.output.exists())

    def test_malformed_backend_execution_result_stops_workflow(self):
        backend = FixtureBackend()
        backend.run = Mock(return_value=b.AgentResult(None))
        runner = self.runner(backend=backend)
        self.assertFalse(runner.run())
        self.assertEqual(runner.state['failure']['kind'], 'invalid_result')

    def test_default_backend_resumes_checkpoint_without_identity_field(self):
        runner = self.runner()
        with patch.object(h, 'execute', side_effect=h.HarnessError('fixture timeout', 'timeout')):
            self.assertFalse(runner.run())
        path = self.output/'state.json'
        state = json.loads(path.read_text())
        state.pop('backend')
        path.write_text(json.dumps(state))
        resumed = self.runner(resume=True)
        with patch.object(h, 'execute', side_effect=h.HarnessError('fixture timeout', 'timeout')):
            self.assertFalse(resumed.run())
        self.assertEqual(resumed.state['backend'], b.CodexBackend().identity())

    def test_graph_nodes_accept_same_backend_interface(self):
        spec = importlib.util.spec_from_file_location('backend_graph', Path(__file__).parents[1]/'graph-runner.py')
        graph = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(graph)
        nodes = [{'id': 'repair', 'depends_on': [], 'workspace': str(self.workspace), 'task': TASK}]
        state = graph.run_graph(nodes, self.root/'graph', 'unused', rounds=1, backend=FixtureBackend())
        self.assertEqual(state['status'], 'verified')
        node_state = json.loads((self.root/'graph/repair/state.json').read_text())
        self.assertEqual(node_state['backend']['name'], 'fixture')

    def test_model_learning_rejects_unsupported_provider(self):
        with self.assertRaisesRegex(h.HarnessError, 'learning currently requires'):
            self.runner(backend=FixtureBackend(), learning_enabled=True)
        self.assertFalse(self.output.exists())


if __name__ == '__main__':
    unittest.main()
