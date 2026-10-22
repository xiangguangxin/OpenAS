import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location('codex_team', Path(__file__).parents[1]/'codex-team.py')
h = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(h)

TASK = {'requirement':'Fix file','scope':['a.txt'],'acceptance':['correct'],
        'checks':[[sys.executable,'-c','print("ok")']]}


def result(verdict, findings=None):
    return {'verdict':verdict, 'summary':'fixture', 'findings':findings or [], 'evidence':['fixture only']}


class RunnerTests(unittest.TestCase):
    def test_task_validation(self):
        for task in [{}, {**TASK,'scope':['../a']}, {**TASK,'scope':['/tmp/a']},
                     {**TASK,'checks':['echo ok']}, {**TASK,'acceptance':'yes'}]:
            with self.subTest(task=task), self.assertRaises(h.HarnessError):
                h.validate_task(task)

    def test_result_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'result.json'
            for r in [None,{},result('approve',['defect']),{**result('pass'),'evidence':[]},
                      result('needs_fix'),{**result('pass'),'extra':'untrusted'}]:
                p.write_text(json.dumps(r))
                with self.subTest(r=r),self.assertRaises(h.HarnessError):
                    h.response(p,{'approve','pass','needs_fix'})
            p.write_text(json.dumps(result('pass')))
            self.assertEqual(h.response(p,{'pass'})['verdict'],'pass')

    def runner(self, tmp, task=None):
        w=Path(tmp)/'workspace';w.mkdir();(w/'a.txt').write_text('old')
        return h.Runner(task or TASK,w,Path(tmp)/'run','codex',timeout=5,rounds=1)

    def test_out_of_scope_stops(self):
        with tempfile.TemporaryDirectory() as tmp:
            r=self.runner(tmp);(r.workspace/'b.txt').write_text('bad')
            with self.assertRaises(h.HarnessError):r.check_scope()

    def test_out_of_scope_permission_change_stops(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = self.runner(tmp)
            other = r.workspace/'other.sh'
            other.write_text('#!/bin/sh\nexit 0\n')
            other.chmod(0o644)
            r.initial = h.snapshot(r.workspace)
            other.chmod(0o755)
            with self.assertRaises(h.HarnessError):
                r.check_scope()

    def test_acceptance_permission_change_stops(self):
        with tempfile.TemporaryDirectory() as tmp:
            task = {**TASK, 'checks': [[sys.executable, '-c',
                    "from pathlib import Path; Path('a.txt').chmod(0o755)"]]}
            r = self.runner(tmp, task)
            (r.workspace/'a.txt').chmod(0o644)
            with self.assertRaises(h.HarnessError):
                r.checks('chmod')

    def test_declared_artifacts_allow_build_without_hiding_source_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            task = {**TASK, 'artifacts': ['build', '.test-cache'], 'checks': [[sys.executable, '-c',
                    "from pathlib import Path; Path('build').mkdir(exist_ok=True); Path('build/result').write_text('ok')"]]}
            r = self.runner(tmp, task)
            self.assertEqual(r.checks('build')[0]['exit_code'], 0)
            r.check_scope()
            (r.workspace/'outside.txt').write_text('not an artifact')
            with self.assertRaises(h.HarnessError):
                r.check_scope()

    def test_artifact_declarations_cannot_hide_existing_files_or_scope(self):
        for artifacts in [['.'], ['../out'], ['/tmp/out'], ['.git'], ['a.txt'], ['a.txt/sub'], ['cache/../src'], 'build']:
            with self.subTest(artifacts=artifacts), self.assertRaises(h.HarnessError):
                h.validate_task({**TASK, 'artifacts': artifacts})
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); w = root/'w'; w.mkdir(); (w/'build').mkdir()
            (w/'build/source.py').write_text('existing source')
            with self.assertRaises(h.HarnessError):
                h.Runner({**TASK, 'artifacts': ['build']}, w, root/'run', 'codex')

    def test_artifact_checks_still_reject_source_mutations(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = self.runner(tmp, {**TASK, 'artifacts': ['build'], 'checks': [[sys.executable, '-c',
                    "from pathlib import Path; Path('a.txt').write_text('changed')"]]})
            with self.assertRaises(h.HarnessError):
                r.checks('source-mutation')

    def test_state_outside_workspace(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)
            with self.assertRaises(h.HarnessError):h.Runner(TASK,p,p/'run','codex')

    def test_failed_checks_never_verify(self):
        class Fake(h.Runner):
            def call(self,role,phase,context,allowed):
                self.state['history'].append({'role':role})
                return result('approve' if role=='red-team' else 'complete')
        with tempfile.TemporaryDirectory() as tmp:
            w=Path(tmp)/'w';w.mkdir()
            r=Fake({**TASK,'checks':[[sys.executable,'-c','raise SystemExit(7)']]},w,Path(tmp)/'r','codex',rounds=1)
            self.assertFalse(r.run())
            self.assertFalse(any(x['role']=='verifier' for x in r.state['history']))
            self.assertEqual(json.loads((r.output/'state.json').read_text())['status'],'stopped')

    def test_nonzero_client_persisted(self):
        with tempfile.TemporaryDirectory() as tmp:
            r=self.runner(tmp);r.client='/bin/false'
            self.assertFalse(r.run());self.assertIn('Client failed',r.state['error'])
            self.assertEqual(r.state['history'][0]['exit_code'],1)

    def test_checks_must_not_mutate(self):
        with tempfile.TemporaryDirectory() as tmp:
            r=self.runner(tmp,{**TASK,'checks':[[sys.executable,'-c',"open('a.txt','w').write('changed')"]]})
            with self.assertRaises(h.HarnessError):r.checks('mutating')

    def test_readonly_role_change_rejected_even_inside_scope(self):
        with tempfile.TemporaryDirectory() as tmp:
            r=self.runner(tmp)
            def fake_exec(argv,cwd,timeout,stdout,stderr,stdin=None):
                (cwd/'a.txt').write_text('changed by reviewer')
                Path(argv[argv.index('-o')+1]).write_text(json.dumps(result('approve')))
                return 0
            with patch.object(h,'execute',side_effect=fake_exec):
                with self.assertRaisesRegex(h.HarnessError,'Read-only role'):
                    r.call('red-team','review','review fixture',{'approve'})

    def test_design_review_checks_plan_not_unimplemented_files(self):
        class Fake(h.Runner):
            def call(self,role,phase,context,allowed):
                self.state['history'].append({'role':role,'phase':phase,'context':context})
                if role=='red-team':return result('approve')
                if role=='verifier':return result('pass')
                return result('complete')
        with tempfile.TemporaryDirectory() as tmp:
            w=Path(tmp)/'w';w.mkdir()
            r=Fake(TASK,w,Path(tmp)/'r','codex',rounds=1)
            self.assertTrue(r.run())
            review=next(x for x in r.state['history'] if x['phase']=='design-review')
            self.assertIn('not expected yet',review['context'])
            self.assertIn('known baseline',review['context'])

    def test_verifier_receives_host_baseline_and_fingerprints(self):
        class Fake(h.Runner):
            def call(self,role,phase,context,allowed):
                if role=='developer':
                    (self.workspace/'a.txt').write_text('good')
                if role=='verifier':
                    payload=json.loads(context)
                    evidence=payload['host_evidence']
                    if evidence['baseline_checks'][0]['exit_code']==0:
                        raise AssertionError('baseline should fail')
                    if evidence['initial_snapshot']['a.txt']==evidence['current_snapshot']['a.txt']:
                        raise AssertionError('expected before/after fingerprints')
                    self.state['verified_host_evidence']=True
                    return result('pass')
                return result('approve' if role=='red-team' else 'complete')
        with tempfile.TemporaryDirectory() as tmp:
            w=Path(tmp)/'w';w.mkdir();(w/'a.txt').write_text('bad')
            command=[sys.executable,'-c',"from pathlib import Path;assert Path('a.txt').read_text()=='good'"]
            r=Fake({**TASK,'checks':[command]},w,Path(tmp)/'r','codex',rounds=1)
            self.assertTrue(r.run())
            self.assertTrue(r.state['verified_host_evidence'])
            self.assertEqual(r.state['final_checks'][0]['exit_code'],0)

    def test_memory_retrieval_reaches_real_call_prompt(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);w=root/'w';w.mkdir();(w/'a.txt').write_text('old')
            memory=h.MEMORY_MODULE.Memory(root)
            (root/'proof.json').write_text('{"valid":true}')
            item=memory.propose('fixture','lesson','Fix file using fixture proof',['Fix'],[memory.evidence('proof.json','/valid')])
            memory.review(item['id'],'approve','test reviewer','fixture evidence')
            with patch.object(h.MEMORY_MODULE,'Memory',return_value=memory):
                r=h.Runner(TASK,w,root/'run','codex',memory_enabled=True)
            captured=[]
            def fake_exec(argv,cwd,timeout,stdout,stderr,stdin=None):
                captured.append(stdin)
                Path(argv[argv.index('-o')+1]).write_text(json.dumps(result('complete')))
                return 0
            with patch.object(h,'execute',side_effect=fake_exec):
                r.call('cto','design','plan only',{'complete'})
            self.assertIn(item['id'],captured[0])
            self.assertIn('not instructions',captured[0])
            self.assertTrue((memory.directory/'current-task.json').exists())

    def test_successful_runner_harvests_memory(self):
        class Fake(h.Runner):
            def call(self,role,phase,context,allowed):
                return result('approve' if role=='red-team' else 'pass' if role=='verifier' else 'complete')
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);w=root/'w';w.mkdir()
            memory=h.MEMORY_MODULE.Memory(root)
            with patch.object(h.MEMORY_MODULE,'Memory',return_value=memory):
                r=Fake(TASK,w,root/'run','codex',memory_enabled=True)
            self.assertTrue(r.run())
            self.assertIn('memory_record_id',r.state)
            self.assertEqual(memory.read()['records'][0]['status'],'accepted')

    def test_operations_routes_through_it_review_and_verification(self):
        class Fake(h.Runner):
            def call(self,role,phase,context,allowed):
                self.state['history'].append({'role':role,'phase':phase})
                if role=='it':(self.workspace/'a.txt').write_text('configured')
                return result('approve' if role=='red-team' else 'pass' if role=='verifier' else 'complete')
        with tempfile.TemporaryDirectory() as tmp:
            w=Path(tmp)/'w';w.mkdir();(w/'a.txt').write_text('old')
            task={**TASK,'workflow':'operations','checks':[[sys.executable,'-c',
                "from pathlib import Path;assert Path('a.txt').read_text()=='configured'"]]}
            r=Fake(task,w,Path(tmp)/'run','codex',rounds=1)
            self.assertTrue(r.run())
            self.assertEqual([(x['role'],x['phase']) for x in r.state['history'] if 'role' in x],
                [('it','operations'),('red-team','operations-review'),('verifier','verification')])

    def test_security_review_is_read_only_and_reports_reviewed(self):
        class Fake(h.Runner):
            def call(self,role,phase,context,allowed):
                self.state['history'].append({'role':role,'phase':phase})
                return result('needs_fix',['S1 exposed credential'])
        with tempfile.TemporaryDirectory() as tmp:
            w=Path(tmp)/'w';w.mkdir();(w/'a.txt').write_text('old')
            r=Fake({**TASK,'workflow':'security-review'},w,Path(tmp)/'run','codex',rounds=1)
            self.assertTrue(r.run())
            self.assertEqual(r.state['status'],'reviewed')
            self.assertEqual(r.state['history'][0]['role'],'security-reviewer')
            self.assertEqual((w/'a.txt').read_text(),'old')

    def test_new_roles_use_expected_sandbox(self):
        with tempfile.TemporaryDirectory() as tmp:
            r=self.runner(tmp)
            observed=[]
            def fake_exec(argv,cwd,timeout,stdout,stderr,stdin=None):
                observed.append((argv[argv.index('--sandbox')+1],stdin))
                Path(argv[argv.index('-o')+1]).write_text(json.dumps(result('complete')))
                return 0
            with patch.object(h,'execute',side_effect=fake_exec):
                r.call('product-manager','product-requirements','fixture',{'complete'})
                r.call('it','operations','fixture',{'complete'})
                r.call('security-reviewer','security-review','fixture',{'complete'})
            self.assertEqual([x[0] for x in observed],['workspace-write','workspace-write','read-only'])

    def test_timeout(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)
            with self.assertRaises(h.HarnessError):
                h.execute([sys.executable,'-c','import time;time.sleep(10)'],p,0.05,p/'out',p/'err')


if __name__=='__main__':unittest.main()
