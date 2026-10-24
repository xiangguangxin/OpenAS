import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

BASE = Path(__file__).parents[1]
SPEC = importlib.util.spec_from_file_location('learning_test_cycle', BASE/'learning_cycle.py')
cycle = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(cycle)
engine = cycle.engine


def review(checks=engine.REVIEW_CHECKS, verdict='approve', reviewer='independent-reviewer'):
    return {'verdict': verdict, 'reviewer': reviewer, 'reason': 'Verified against original fixture evidence',
            'checks': {key: True for key in checks}}


class LearningTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)/'consumer'
        self.root.mkdir()
        (self.root/'proof.json').write_text('{"empty_input":0,"tested":true}')
        self.learning = engine.Learning(self.root)
        self.run = {'task': {'requirement': 'Private task text'}, 'done': True, 'status': 'verified',
                    'final_checks': [{'exit_code': 0}], 'error': 'SECRET_ERROR',
                    'history': [{'result': {'summary': 'SECRET_SUMMARY'}}]}
        self.observation = self.learning.capture(self.run, 'trusted/run-1')

    def proposal(self, key='empty-input', statement='Empty input returns zero'):
        return {'key': key, 'scope': 'average-library', 'statement': statement,
                'trigger': 'Investigate empty input in this average library',
                'cause': 'The fixture contract explicitly defines zero for empty input',
                'procedure': ['Read the current API contract', 'Check the empty-input branch'],
                'validation': ['Run the empty-input regression test'],
                'limitations': 'Applies to this fixture contract only; do not generalize to other libraries',
                'author': 'writer', 'tags': ['average', 'empty'],
                'observation_ids': [self.observation['id']],
                'evidence': [self.learning.memory.evidence('proof.json', '/empty_input')]}

    def accepted(self, key='empty-input'):
        candidate = self.learning.propose(self.proposal(key))
        return self.learning.review(candidate['id'], review())

    def skill(self, key='empty-input'):
        lesson = self.accepted(key)
        return self.learning.draft('average-empty-input', [lesson['id']], 'skill-writer')

    def evaluated(self, skill, name='trial', passed=True):
        path = self.root/(name + '.json')
        report = {'skill_sha256': skill['sha256'], 'sources': ['proof.json', skill['path']], 'cases': [
            {'expected_applicable': True, 'actual_applicable': True, 'passed': passed, 'checks': [0 if passed else 1]},
            {'expected_applicable': False, 'actual_applicable': False, 'passed': True, 'checks': [0]}]}
        path.write_text(json.dumps(report))
        return self.learning.evaluate(skill['id'], path.name)

    def active(self, key='empty-input', name='trial'):
        skill = self.skill(key)
        self.evaluated(skill, name)
        self.learning.approve_skill(skill['id'], review(engine.SKILL_CHECKS))
        self.learning.activate(skill['id'], 'Trial and review passed')
        return skill

    def test_capture_is_bounded_private_and_idempotent(self):
        again = self.learning.capture(self.run, 'trusted/run-1')
        self.assertEqual(again, self.observation)
        self.assertEqual(len(self.learning.read()['observations']), 1)
        stored = json.dumps(self.learning.read())
        for secret in ('Private task text', 'SECRET_ERROR', 'SECRET_SUMMARY'):
            self.assertNotIn(secret, stored)
        failure = self.learning.capture({'status': 'stopped', 'failure': {'kind': 'acceptance_limit'}}, 'run-2')
        self.assertEqual(failure['value']['failure_kind'], 'acceptance_limit')

    def test_candidate_isolated_and_deduplicated(self):
        candidate = self.learning.propose(self.proposal())
        self.assertEqual(candidate, self.learning.propose(self.proposal()))
        self.assertEqual(self.learning.memory.query('empty'), [])
        self.assertEqual(self.learning.context('empty'), [])
        with self.assertRaises(ValueError):
            self.learning.draft('average-empty', [candidate['id']], 'writer')

    def test_review_requires_independence_and_semantic_checks(self):
        candidate = self.learning.propose(self.proposal())
        for report in (review(reviewer='writer'), review(checks=()), review(checks=('supported',))):
            with self.assertRaises(ValueError):
                self.learning.review(candidate['id'], report)
        self.assertEqual(self.learning.review(candidate['id'], review())['status'], 'accepted')
        self.assertEqual(len(self.learning.memory.query('empty')), 1)

    def test_reject_with_stale_evidence_still_possible(self):
        candidate = self.learning.propose(self.proposal())
        (self.root/'proof.json').unlink()
        self.assertEqual(self.learning.review(candidate['id'], review(verdict='reject'))['status'], 'rejected')

    def test_conflict_requires_retirement(self):
        old = self.accepted()
        candidate = self.learning.propose(self.proposal(statement='Empty input must raise instead'))
        self.assertEqual(candidate['status'], 'conflict')
        with self.assertRaises(ValueError):
            self.learning.review(candidate['id'], review())
        self.learning.retire(old['id'], 'Contract superseded after review')
        self.assertEqual(self.learning.review(candidate['id'], review())['status'], 'accepted')

    def test_similar_candidates_reported(self):
        self.accepted()
        candidate = self.learning.propose(self.proposal(key='duplicate-key'))
        self.assertTrue(candidate['similar'])

    def test_source_change_invalidates_lesson_and_active_skill(self):
        skill = self.active()
        self.assertEqual(self.learning.context('average')[0]['id'], skill['id'])
        (self.root/'proof.json').write_text('{"empty_input":null}')
        self.assertEqual(self.learning.context('average'), [])
        self.assertEqual(self.learning.memory.query('empty'), [])
        with self.assertRaises(ValueError):
            self.learning.activate(skill['id'], 'Cannot activate stale evidence')

    def test_generated_skill_is_not_installed_until_reviewed_and_activated(self):
        skill = self.skill()
        self.assertTrue((self.root/skill['path']).is_file())
        self.assertFalse((self.root/'.claude/skills').exists())
        self.assertEqual(self.learning.context('average'), [])
        with self.assertRaises(ValueError):
            self.learning.approve_skill(skill['id'], review(engine.SKILL_CHECKS))
        with self.assertRaises(ValueError):
            self.learning.activate(skill['id'], 'No trial yet')
        self.evaluated(skill)
        self.learning.approve_skill(skill['id'], review(engine.SKILL_CHECKS))
        self.assertEqual(self.learning.context('average'), [])
        self.learning.activate(skill['id'], 'Verified')
        self.assertTrue(self.learning.context('average'))

    def test_failed_or_changed_trial_cannot_activate(self):
        skill = self.skill()
        self.evaluated(skill, passed=False)
        with self.assertRaises(ValueError):
            self.learning.approve_skill(skill['id'], review(engine.SKILL_CHECKS))
        self.evaluated(skill, 'passing-trial')
        (self.root/'passing-trial.json').write_text('{}')
        with self.assertRaises(ValueError):
            self.learning.approve_skill(skill['id'], review(engine.SKILL_CHECKS))

    def test_negative_case_required(self):
        skill = self.skill()
        self.evaluated(skill)
        path = self.root/'trial.json'
        report = json.loads(path.read_text())
        report['cases'] = report['cases'][:1]
        path.write_text(json.dumps(report))
        with self.assertRaises(ValueError):
            self.learning.evaluate(skill['id'], path.name)

    def test_changed_skill_bytes_cannot_activate(self):
        skill = self.active()
        (self.root/skill['path']).write_text('Modified skill')
        self.assertEqual(self.learning.context('average'), [])
        with self.assertRaises(ValueError):
            self.learning.activate(skill['id'], 'Try altered artifact')

    def test_outcomes_idempotent_and_three_failures_suspend(self):
        skill = self.active()
        result = self.learning.outcome(skill['id'], self.observation['id'])
        self.assertEqual(result, self.learning.outcome(skill['id'], self.observation['id']))
        for number in range(3):
            obs = self.learning.capture({'status': 'stopped'}, f'failed-{number}')
            self.learning.outcome(skill['id'], obs['id'])
        self.assertTrue(self.learning.read()['skills'][skill['id']]['suspended'])
        self.assertEqual(self.learning.context('average'), [])
        self.assertEqual(self.learning.inspect()['metrics'][skill['id']]['observed_tasks'], 4)
        with self.assertRaises(ValueError):
            self.learning.approve_skill(skill['id'], review(engine.SKILL_CHECKS))
        self.evaluated(skill, 'fresh-trial')
        self.learning.approve_skill(skill['id'], review(engine.SKILL_CHECKS))
        self.learning.activate(skill['id'], 'Fresh trial and review')
        self.assertTrue(self.learning.context('average'))

    def test_late_feedback_updates_existing_observation(self):
        skill = self.active()
        self.learning.outcome(skill['id'], self.observation['id'])
        entry = self.learning.outcome(skill['id'], self.observation['id'], useful=False)
        self.assertIs(entry['useful'], False)
        self.assertEqual(len(self.learning.read()['outcomes']), 1)
        self.assertEqual(self.learning.inspect()['metrics'][skill['id']]['negative_feedback'], 1)

    def test_reviewed_tasks_are_not_treated_as_failures(self):
        skill = self.active()
        for index in range(3):
            observation = self.learning.capture({'status': 'reviewed', 'done': True}, f'review-{index}')
            entry = self.learning.outcome(skill['id'], observation['id'])
            self.assertIsNone(entry['success'])
        self.assertFalse(self.learning.read()['skills'][skill['id']]['suspended'])
        self.assertEqual(self.learning.inspect()['metrics'][skill['id']]['unclassified_tasks'], 3)

    def test_learning_storage_cannot_escape_project_via_symlink(self):
        other = Path(self.temp.name)/'another'; other.mkdir()
        (other/'.openas').symlink_to(self.root/'.openas', target_is_directory=True)
        with self.assertRaises(ValueError):
            engine.Learning(other)

    def test_upgrade_and_rollback_preserve_history(self):
        old = self.active()
        new = self.active('second-contract', 'trial-new')
        self.assertNotEqual(old['id'], new['id'])
        self.assertEqual(self.learning.context('average')[0]['id'], new['id'])
        self.learning.activate(old['id'], 'New version regressed', rollback=True)
        self.assertEqual(self.learning.context('average')[0]['id'], old['id'])
        self.assertEqual(self.learning.read()['audit'][-1]['event'], 'rollback')

    def test_retired_lesson_disables_dependent_skill(self):
        skill = self.active()
        self.learning.retire(skill['lesson_ids'][0], 'Outdated')
        self.assertEqual(self.learning.context('average'), [])

    def test_invalid_paths_and_corrupt_store_fail_closed(self):
        for name in ('../escape', '/absolute', 'bad_name'):
            with self.assertRaises(ValueError):
                self.learning.draft(name, [], 'writer')
        self.learning.file.write_text('broken')
        with self.assertRaises(ValueError):
            self.learning.capture(self.run, 'run')
        self.assertEqual(self.learning.file.read_text(), 'broken')

    def test_model_reflection_independent_review_generates_only_candidate_skill(self):
        raw = {k: v for k, v in self.proposal().items() if k not in ('author', 'observation_ids', 'evidence')}
        raw['evidence_paths'] = ['proof.json']
        model_review = review()
        del model_review['reviewer']
        calls = []

        def fake_call(client, workspace, output, name, schema, prompt, timeout):
            calls.append(name)
            return {'lessons': [raw]} if name == 'reflection' else model_review

        with patch.object(cycle, 'call', side_effect=fake_call):
            result = cycle.cycle(self.learning, self.observation, 'codex', Path(self.temp.name)/'cycle-output')
        self.assertEqual(calls, ['reflection', 'review-0'])
        self.assertEqual(result[0]['status'], 'accepted')
        self.assertIn('skill_candidate', result[0])
        self.assertEqual(self.learning.context('average'), [])

    def test_model_rejection_does_not_generate_skill(self):
        raw = {k: v for k, v in self.proposal().items() if k not in ('author', 'observation_ids', 'evidence')}
        raw['evidence_paths'] = ['proof.json']
        rejection = review(verdict='reject'); del rejection['reviewer']
        with patch.object(cycle, 'call', side_effect=[{'lessons': [raw]}, rejection]):
            result = cycle.cycle(self.learning, self.observation, 'codex', Path(self.temp.name)/'reject-output')
        self.assertEqual(result[0]['status'], 'rejected')
        self.assertEqual(self.learning.read()['skills'], {})

    def test_readonly_client_mutation_is_detected(self):
        output = Path(self.temp.name)/'bad-client'; output.mkdir()

        def mutate(*args, **kwargs):
            (self.root/'proof.json').write_text('modified')
            return 0

        with patch.object(cycle, 'execute', side_effect=mutate):
            with self.assertRaisesRegex(ValueError, 'modified read-only'):
                cycle.call('codex', self.root, output, 'case', cycle.TRIAL_SCHEMA, 'Task', 5)

    def test_real_trial_driver_passes_responses_to_trusted_checks(self):
        skill = self.skill()
        fixture = self.root/'fixture'; fixture.mkdir()
        (fixture/'contract.txt').write_text('Empty input returns zero')
        code = ('import json,os; from pathlib import Path; '
                'r=json.loads(Path(os.environ["OPENAS_TRIAL_RESULT"]).read_text()); '
                'assert r["summary"] == "Checked contract"')
        spec = {'cases': [
            {'fixture': 'fixture', 'task': 'Diagnose average empty input', 'expected_applicable': True,
             'checks': [[sys.executable, '-B', '-c', code]]},
            {'fixture': 'fixture', 'task': 'Unrelated UI question', 'expected_applicable': False,
             'checks': [[sys.executable, '-B', '-c', code]]}]}

        def fake_call(client, workspace, output, name, schema, prompt, timeout):
            result = {'applicable': name == 'case-0', 'summary': 'Checked contract', 'evidence': ['contract.txt']}
            (output/(name + '.result.json')).write_text(json.dumps(result))
            return result

        with patch.object(cycle, 'call', side_effect=fake_call):
            receipt = cycle.trial(self.learning, skill['id'], spec, 'codex', Path(self.temp.name)/'trial-output')
        self.assertTrue(receipt['passed'])
        self.assertEqual(self.learning.context('average'), [])
        self.assertTrue(self.learning.memory.valid(receipt))
        (fixture/'contract.txt').write_text('Changed contract')
        self.assertFalse(self.learning.memory.valid(receipt))

    def test_model_output_schema_fails_closed(self):
        for result in ({}, {'applicable': 'yes', 'summary': 'test', 'evidence': []},
                       {'applicable': True, 'summary': 'test', 'evidence': [], 'extra': 'field'}):
            with self.assertRaises(ValueError):
                cycle.validate_schema(result, cycle.TRIAL_SCHEMA)

    def test_obvious_credential_material_is_rejected(self):
        proposal = self.proposal()
        proposal['statement'] = 'Use token ghp_' + 'a' * 36
        with self.assertRaises(ValueError):
            self.learning.propose(proposal)

    def harness(self):
        spec = importlib.util.spec_from_file_location('learning_test_harness', BASE/'codex-team.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def runner(self, module, cls=None, learn=False):
        workspace = self.root/'workspace'; workspace.mkdir()
        task = {'requirement': 'Diagnose average empty input', 'scope': ['average.py'],
                'acceptance': ['Contract holds'], 'checks': [[sys.executable, '-B', '-c', 'print("ok")']]}
        return (cls or module.Runner)(task, workspace, Path(self.temp.name)/'run-output', 'codex',
                                     project_root=self.root, memory_enabled=True, learning_enabled=learn)

    def test_runner_passes_active_skill_to_real_prompt(self):
        skill = self.active()
        harness = self.harness()
        runner = self.runner(harness)
        prompts = []

        def fake_execute(argv, cwd, timeout, stdout, stderr, stdin=None):
            prompts.append(stdin)
            Path(argv[argv.index('-o') + 1]).write_text(json.dumps(
                {'verdict': 'complete', 'summary': 'Plan checked', 'findings': [], 'evidence': ['proof.json']}))
            return 0

        with patch.object(harness, 'execute', side_effect=fake_execute):
            runner.call('cto', 'design', 'Plan task', {'complete'})
        self.assertIn(skill['id'], prompts[0])
        self.assertIn('never expands task scope', prompts[0])

    def test_failed_runner_captures_learning_without_extra_client_calls(self):
        harness = self.harness()

        class Failed(harness.Runner):
            def drive(self):
                raise harness.HarnessError('Fixture check failed', 'acceptance_limit')

        runner = self.runner(harness, Failed)
        with patch.object(harness.LEARNING, 'cycle') as model:
            self.assertFalse(runner.run())
        model.assert_not_called()
        self.assertEqual(self.learning.read()['observations'][runner.state['learning_observation_id']]['value']['status'], 'stopped')

    def test_learning_failure_preserves_verified_task_and_records_outcome(self):
        skill = self.active()
        harness = self.harness()

        class Successful(harness.Runner):
            def drive(self):
                self.complete()

        runner = self.runner(harness, Successful, learn=True)
        with patch.object(harness.LEARNING, 'cycle', side_effect=ValueError('Bad model result')) as model:
            self.assertTrue(runner.run())
        model.assert_called_once()
        self.assertEqual(runner.state['status'], 'verified')
        self.assertIn('learning_warning', runner.state)
        self.assertEqual(self.learning.inspect()['metrics'][skill['id']]['observed_tasks'], 1)

    def test_resume_cannot_silently_enable_model_learning(self):
        harness = self.harness()
        runner = self.runner(harness)
        with self.assertRaisesRegex(harness.HarnessError, 'execution options changed'):
            harness.Runner(runner.task, runner.workspace, runner.output, 'codex',
                           project_root=self.root, memory_enabled=True, learning_enabled=True, resume=True)

    def test_fresh_review_can_automatically_activate_evaluated_skill(self):
        skill = self.skill()
        self.evaluated(skill)
        report = review(engine.SKILL_CHECKS); del report['reviewer']
        with patch.object(cycle, 'call', return_value=report):
            result = cycle.review_skill(self.learning, skill['id'], 'codex', Path(self.temp.name)/'skill-review', activate=True)
        self.assertEqual(result['status'], 'approved')
        self.assertEqual(self.learning.context('average')[0]['id'], skill['id'])


if __name__ == '__main__':
    unittest.main()
