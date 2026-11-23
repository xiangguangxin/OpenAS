"""Synthetic routing, executed host checks and negative machine-gate regressions."""
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT/'plugins/openas'


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


policy = load(PLUGIN/'workflows/workflow_policy.py', 'tier_policy_tests')
h = load(PLUGIN/'workflows/codex-team.py', 'tier_harness_tests')
checker = load(ROOT/'scripts/check_plugin.py', 'tier_plugin_tests')
pm = load(PLUGIN/'skills/project-memory/scripts/project_memory.py', 'tier_memory_tests')


def profile(kind='feature', **extra):
    return {'task_kind': kind, 'rigor': 'auto', 'risk_factors': [], 'scope': ['a.txt'], **extra}


class RoutingTests(unittest.TestCase):
    def test_explicit_capabilities_select_only_requested_specialists(self):
        choices = {'decision-mapping': 'decision-mapping', 'task-slicing': 'writing-plans',
                   'spec': 'spec-driven-development', 'research': 'technical-research',
                   'security-audit': 'security-review', 'react': 'react-composition',
                   'animation': 'interaction-design', 'video': 'remotion-render',
                   'neon': 'neon-postgres', 'azure-messaging': 'azure-messaging'}
        baseline = policy.plan(profile())
        for capability, skill in choices.items():
            result = policy.plan(profile(capabilities=[capability]))
            with self.subTest(capability=capability):
                self.assertIn(skill, result['skills'])
                self.assertEqual(result['capabilities'], [capability])
                self.assertEqual(result['tier'], baseline['tier'])
                self.assertEqual(result['roles'], baseline['roles'])
                self.assertEqual(result['workflow'], baseline['workflow'])
        self.assertNotIn('neon-postgres', baseline['skills'])
        self.assertNotIn('remotion-render', baseline['skills'])

    def test_capability_validation_and_deduplication(self):
        for value in (None, 'react', ['unknown'], ['react', 'react'], [None], [{}]):
            with self.subTest(value=value), self.assertRaises(ValueError):
                policy.plan(profile(capabilities=value))
        result = policy.plan(profile(capabilities=['task-slicing', 'spec']))
        self.assertEqual(len(result['skills']), len(set(result['skills'])))
        self.assertIn('spec-driven-development', result['skills'])

    def test_specialization_registry_rejects_invalid_skill_references(self):
        with tempfile.TemporaryDirectory() as tmp:
            plugin = Path(tmp)/'plugin'; shutil.copytree(PLUGIN, plugin)
            registry = plugin/'references/task-routing.json'
            original = json.loads(registry.read_text())
            for names in ([], ['missing'], [None], [{}], ['bug-fix', 'bug-fix']):
                data = copy.deepcopy(original); data['specializations']['fixture'] = names
                registry.write_text(json.dumps(data))
                with self.subTest(names=names), self.assertRaises(ValueError):
                    policy.validate_registry(plugin)

    def test_runner_rejects_capabilities_without_explicit_rigor(self):
        task = {'requirement': 'fixture', 'acceptance': ['fixture'],
                'checks': [[sys.executable, '-c', 'pass']], 'capabilities': ['react']}
        with self.assertRaises(h.HarnessError): h.validate_task(task)

    def test_four_defaults_are_small_and_only_required_methods_load(self):
        for kind in ('feature','bugfix','refactor','documentation'):
            result = policy.plan(profile(kind))
            self.assertEqual(result['tier'], 'light')
            self.assertLessEqual(len(result['skills']), 3)
            self.assertEqual(len(result['roles']), 1)
            self.assertNotIn('office', result['skills'])
            self.assertNotIn('security-review', result['skills'])

    def test_unknown_multi_file_and_carrier_raise_floor(self):
        for task in (profile(risk_factors=['unknown']), profile(scope=['a','b']), profile(carrier='office')):
            self.assertEqual(policy.plan(task)['tier'], 'standard')
        task = profile(); del task['risk_factors']
        self.assertEqual(policy.plan(task)['tier'], 'standard')

    def test_sensitive_single_file_cannot_force_light(self):
        for risk in ('security','public-api','data-migration','production-incident','performance-critical','concurrency'):
            task = profile(risk_factors=[risk])
            self.assertEqual(policy.plan(task)['tier'], 'heavy')
            with self.assertRaises(ValueError): policy.plan({**task,'rigor':'light'})

    def test_conditional_carrier_is_selected_without_unrelated_methods(self):
        result = policy.plan(profile('documentation', carrier='office'))
        self.assertIn('office', result['skills'])
        self.assertNotIn('computer-use', result['skills'])
        self.assertNotIn('security-review', result['skills'])

    def test_explicit_route_and_invalid_scope_do_not_bypass_floor(self):
        for task in (profile(risk_factors=['security'], workflow='direct'), profile(scope=['../secret']), profile(scope=['a','a'])):
            with self.assertRaises(ValueError): policy.plan(task)

    def test_catalog_requires_all_metadata_and_existing_roles_skills(self):
        with tempfile.TemporaryDirectory() as tmp:
            plugin = Path(tmp)/'plugin'; shutil.copytree(PLUGIN, plugin)
            registry = plugin/'references/task-routing.json'
            original = json.loads(registry.read_text())
            for edit in ('missing_skill','unknown_role','unknown_skill','missing_when'):
                data = copy.deepcopy(original)
                if edit=='missing_skill': del data['skills']['bug-fix']
                if edit=='unknown_role': data['skills']['bug-fix']['owner']='nonexistent'
                if edit=='unknown_skill': data['bundles']['feature']['base'].append('nonexistent')
                if edit=='missing_when': del data['skills']['bug-fix']['when']
                registry.write_text(json.dumps(data))
                with self.subTest(edit=edit), self.assertRaises(ValueError): policy.validate_registry(plugin)

    def test_machine_metadata_detects_unknown_workflow_role(self):
        with tempfile.TemporaryDirectory() as tmp:
            plugin=Path(tmp)/'plugin';shutil.copytree(PLUGIN,plugin)
            path=plugin/'workflows/codex-team.py'
            path.write_text(path.read_text().replace("self.stage('cto',", "self.stage('unknown-role',",1))
            with self.assertRaises(ValueError):policy.validate_registry(plugin)

    def test_frontmatter_duplicate_keys_fail_before_translation_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'SKILL.md'
            path.write_text('---\nname: a\nname: b\ndescription: fixture\n---\n')
            with self.assertRaises(ValueError): checker.metadata(path)

    def test_router_cli_is_readonly_and_relocatable(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); plugin = root/'renamed-plugin'; shutil.copytree(PLUGIN, plugin)
            task = root/'task.json'; task.write_text(json.dumps(profile('bugfix')))
            before = {p.relative_to(plugin): p.read_bytes() for p in plugin.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
            result = subprocess.run([sys.executable, '-B', str(plugin/'workflows/task_router.py'), '--task', str(task)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)['workflow'], 'repair')
            self.assertTrue(all(p.read_bytes()==data for rel,data in before.items() for p in [plugin/rel]))


class RigorExecutionTests(unittest.TestCase):
    def execute_task(self, tmp, tier, risks=None, scope=None, kind='bugfix'):
        root = Path(tmp); workspace = root/'workspace'; workspace.mkdir()
        scope = scope or ['a.txt']
        for name in scope: (workspace/name).write_text('old')
        task = {**profile(kind, rigor=tier, risk_factors=risks or [], scope=scope),
                'requirement':'Fix the bounded fixture', 'acceptance':['fixture is fixed'], 'acceptance_checks':[[0]],
                'checks':[[sys.executable,'-c',"from pathlib import Path; raise SystemExit(Path('a.txt').read_text() != 'fixed')"]]}
        runner = h.Runner(task, workspace, root/'run', 'fixture-client')
        phases = []
        def stage(role, phase, context, allowed):
            phases.append((role,phase))
            if role == 'developer': (workspace/'a.txt').write_text('fixed')
            verdict='approve' if role in ('red-team','security-reviewer','performance-engineer') else 'pass' if role=='verifier' else 'complete'
            return {'verdict':verdict,'summary':'synthetic model fixture','findings':[], 'evidence':['fixture-only model result; real host checks recorded separately']}
        with patch.object(runner,'call',side_effect=stage): self.assertTrue(runner.run(),runner.state.get('error'))
        return runner, phases

    def test_light_executes_one_model_stage_and_real_host_checks(self):
        with tempfile.TemporaryDirectory() as tmp:
            runner, phases=self.execute_task(tmp,'light')
            self.assertEqual(phases,[('developer','light-implementation')])
            self.assertNotEqual(runner.state['baseline_checks'][0]['exit_code'],0)
            self.assertEqual(runner.state['final_checks'][0]['exit_code'],0)
            self.assertNotIn('verification',runner.state)
            self.assertTrue(runner.state['rigor_gate']['passed'])
            receipt=json.loads((runner.output/'rigor-evidence.json').read_text())
            self.assertTrue(policy.check_evidence(receipt)['passed'])

    def test_standard_preserves_independent_stage_and_rejects_missing_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            runner, phases=self.execute_task(tmp,'standard',scope=['a.txt','b.txt'])
            self.assertIn(('red-team','code-review'),phases)
            self.assertIn(('verifier','verification'),phases)
            for field in ('verification','final_checks','final_snapshot','workspace'):
                altered=copy.deepcopy(runner.state);altered.pop(field)
                with self.subTest(field=field),self.assertRaises(ValueError):policy.check_evidence(altered)
            for field,value in (('steps',[None]),('verification',[]),('verification',{'verdict':'pass'})):
                altered=copy.deepcopy(runner.state);altered[field]=value
                with self.subTest(field=field),self.assertRaises(ValueError):policy.check_evidence(altered)
            altered=copy.deepcopy(runner.state);altered['steps']=[s for s in altered['steps'] if s['role']!='red-team']
            with self.assertRaises(ValueError):policy.check_evidence(altered)

    def test_heavy_adds_impact_design_and_security_gates(self):
        with tempfile.TemporaryDirectory() as tmp:
            runner, phases=self.execute_task(tmp,'heavy',risks=['security'])
            for phase in (('cto','impact-analysis'),('red-team','rigor-design-review'),('security-reviewer','risk-review-security')):
                self.assertIn(phase,phases)
            altered=copy.deepcopy(runner.state);altered['steps']=[s for s in altered['steps'] if s['role']!='security-reviewer']
            with self.assertRaises(ValueError):policy.check_evidence(altered)

    def test_light_nonbug_task_uses_one_host_check_and_no_baseline_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            runner, phases=self.execute_task(tmp,'light',kind='feature')
            self.assertEqual(runner.state['baseline_checks'],[])
            self.assertEqual(runner.state['check_attempt'],1)
            self.assertEqual(len(phases),1)

    def test_tier_requires_host_mappings_and_real_failure_baseline(self):
        task={**profile('bugfix'), 'requirement':'fixture','acceptance':['works'],'checks':[[sys.executable,'-c','print(1)']]}
        with self.assertRaises(h.HarnessError):h.validate_task(task)
        with tempfile.TemporaryDirectory() as tmp:
            workspace=Path(tmp)/'w';workspace.mkdir();(workspace/'a.txt').write_text('old')
            runner=h.Runner({**task,'acceptance_checks':[[0]]},workspace,Path(tmp)/'run','unused')
            with patch.object(runner,'call',side_effect=AssertionError('No model call before reproduction')) as called:
                self.assertFalse(runner.run())
            called.assert_not_called()
            self.assertEqual(runner.state['failure']['kind'],'premise_unverified')

    def test_legacy_task_validation_keeps_original_route(self):
        task={'requirement':'legacy','scope':['a'],'acceptance':['works'],'checks':[['python3','check.py']]}
        self.assertEqual(h.validate_task(task),task)
        self.assertNotIn('rigor',h.validate_task(task))


class MemoryGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.memory=pm.Memory(self.root)
        (self.root/'proof.json').write_text('{"value":1}')
        item=self.memory.propose('fixture','fact','Fixture value is numeric',['fixture'],[self.memory.evidence('proof.json','/value')])
        self.memory.review(item['id'],'approve','fixture-reviewer','checked this fixture only')
        self.original=self.memory.read()

    def test_invalid_memory_schema_review_and_audit_are_not_overwritten(self):
        for kind in ('field','status','duplicate_id','review','transition','reason','sha256'):
            data=copy.deepcopy(self.original)
            if kind=='field':del data['records'][0]['scope']
            if kind=='status':data['records'][0]['status']=None
            if kind=='duplicate_id':data['records'].append(data['records'][0])
            if kind=='review':data['records'][0]['review']=None
            if kind=='transition':data['audit'].reverse()
            if kind=='reason':del data['audit'][-1]['reason']
            if kind=='sha256':data['records'][0]['evidence'][0]['sha256']='bad'
            raw=json.dumps(data);self.memory.file.write_text(raw)
            with self.subTest(kind=kind),self.assertRaises(ValueError):self.memory.read()
            self.assertEqual(self.memory.file.read_text(),raw)

    def test_accepted_content_cannot_change_without_new_proposal(self):
        data=copy.deepcopy(self.original)
        data['records'][0]['statement']='Unreviewed replacement claim'
        with self.assertRaises(ValueError):pm.validate_store(data)

    def test_evidence_boolean_is_not_numeric_one(self):
        evidence=self.memory.evidence('proof.json','/value');evidence['value']=True
        with self.assertRaises(ValueError):self.memory.propose('typed','fact','wrong type',[],[evidence])

    def test_retire_is_idempotent_and_cannot_return_to_accepted(self):
        ident=self.original['records'][0]['id'];self.memory.retire(ident,'superseded')
        count=len(self.memory.read()['audit']);self.memory.retire(ident,'again')
        self.assertEqual(len(self.memory.read()['audit']),count)
        data=self.memory.read();data['audit'].append({'id':ident,'at':pm.now(),'event':'accepted','reason':'forged'})
        data['records'][0]['status']='accepted'
        with self.assertRaises(ValueError):pm.validate_store(data)


if __name__=='__main__':unittest.main()
