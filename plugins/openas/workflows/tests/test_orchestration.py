import importlib.util
import fcntl
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest
from unittest.mock import patch

SPEC=importlib.util.spec_from_file_location('orchestration_harness',Path(__file__).parents[1]/'codex-team.py')
h=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(h)
TASK={'requirement':'Repair a.txt', 'scope':['a.txt'], 'acceptance':['a.txt contains good'],
      'checks':[[sys.executable,'-c',"from pathlib import Path; assert Path('a.txt').read_text()=='good'"]],
      'acceptance_checks':[[0]]}


class OrchestrationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.workspace=self.root/'work';self.workspace.mkdir()
        (self.workspace/'a.txt').write_text('old')
        self.calls=[];self.fail_phase='code-review';self.failed=False
        self.real_execute=h.execute

    def client(self, argv, cwd, timeout, stdout, stderr, stdin=None):
        if '-o' not in argv:
            return self.real_execute(argv,cwd,timeout,stdout,stderr,stdin)
        role=re.search(r'^name: (.+)$',stdin,re.M).group(1)
        output=Path(argv[argv.index('-o')+1])
        phase=output.name.split('-',1)[1].removesuffix('.result.json')
        self.calls.append((role,phase))
        Path(stdout).write_text('');Path(stderr).write_text('')
        if phase==self.fail_phase and not self.failed:
            self.failed=True;return 7
        if role=='developer':(cwd/'a.txt').write_text('good')
        verdict='approve' if role=='red-team' else 'pass' if role=='verifier' else 'complete'
        output.write_text(json.dumps({'verdict':verdict,'summary':'fixture','findings':[], 'evidence':['fixture']}))
        return 0

    def runner(self, task=None, **kwargs):
        return h.Runner(task or TASK,self.workspace,self.root/'run','fake',rounds=2,**kwargs)

    def test_resume_skips_completed_roles_but_reruns_host_checks_and_verifier(self):
        with patch.object(h,'execute',side_effect=self.client):
            first=self.runner();self.assertFalse(first.run())
            self.assertEqual(first.state['failure']['kind'],'client_failure')
            resumed=self.runner(resume=True);self.assertTrue(resumed.run())
        self.assertEqual(self.calls.count(('cto','design')),1)
        self.assertEqual(self.calls.count(('developer','implementation')),1)
        self.assertEqual(self.calls.count(('red-team','code-review')),2)
        self.assertEqual(resumed.state['baseline_checks'][0]['exit_code'],1)
        self.assertEqual(resumed.state['acceptance_report'][0]['status'],'passed')
        self.assertTrue((self.root/'run/handoff.json').is_file())
        self.assertTrue((self.root/'run/acceptance.json').is_file())

    def test_changed_source_requires_explicit_restart(self):
        with patch.object(h,'execute',side_effect=self.client):
            first=self.runner();self.assertFalse(first.run())
            (self.workspace/'a.txt').write_text('manual change')
            original=(self.root/'run/state.json').read_bytes()
            with self.assertRaises(h.HarnessError):self.runner(resume=True)
            self.assertEqual((self.root/'run/state.json').read_bytes(),original)
            resumed=self.runner(resume=True,restart_stages=True)
            self.assertTrue(resumed.run())
        self.assertEqual(self.calls.count(('cto','design')),2)

    def test_resume_never_accepts_changed_task_or_out_of_scope_changes(self):
        with patch.object(h,'execute',side_effect=self.client):
            self.assertFalse(self.runner().run())
        with self.assertRaises(h.HarnessError):
            self.runner({**TASK,'acceptance':['different']},resume=True)
        (self.workspace/'other.txt').write_text('external change')
        with self.assertRaises(h.HarnessError):self.runner(resume=True,restart_stages=True)

    def test_rules_changed_since_checkpoint_are_not_reused(self):
        with patch.object(h,'execute',side_effect=self.client):self.assertFalse(self.runner().run())
        with patch.object(h.Runner,'resource_fingerprint',return_value='different'):
            with self.assertRaises(h.HarnessError):self.runner(resume=True)

    def test_deleted_phase_evidence_is_rerun(self):
        with patch.object(h,'execute',side_effect=self.client):
            first=self.runner();self.assertFalse(first.run())
            Path(first.state['steps'][0]['result_file']).unlink()
            resumed=self.runner(resume=True);self.assertTrue(resumed.run())
        self.assertEqual(self.calls.count(('cto','design')),2)

    def test_active_run_lock_prevents_state_mutation(self):
        r=self.runner();original=(r.output/'state.json').read_bytes()
        with (r.output/'.run.lock').open('a') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            with self.assertRaises(h.HarnessError):r.run()
        self.assertEqual((r.output/'state.json').read_bytes(),original)

    def test_final_check_failure_resume_reexecutes_verifier(self):
        self.fail_phase=None
        original=h.Runner.checks;failed=[]
        def checks(r,label):
            records=original(r,label)
            if label=='final' and not failed:
                failed.append(True);records[0]['exit_code']=9
            return records
        with patch.object(h,'execute',side_effect=self.client),patch.object(h.Runner,'checks',checks):
            first=self.runner();self.assertFalse(first.run())
            resumed=self.runner(resume=True);self.assertTrue(resumed.run())
        self.assertEqual(self.calls.count(('verifier','verification')),2)

    def test_direct_route_does_not_dispatch_design_or_review(self):
        self.fail_phase=None
        with patch.object(h,'execute',side_effect=self.client):
            r=self.runner({**TASK,'workflow':'direct'});self.assertTrue(r.run())
        self.assertEqual([r for r,p in self.calls],['developer','verifier'])

    def test_documentation_route_does_not_dispatch_developer(self):
        self.fail_phase=None
        task={**TASK,'workflow':'documentation','checks':[[sys.executable,'-c','print("document check")']]}
        with patch.object(h,'execute',side_effect=self.client):
            r=self.runner(task);self.assertTrue(r.run())
        self.assertEqual([r for r,p in self.calls],['tech-writer','red-team','verifier'])

    def test_review_reports_findings_without_claiming_target_verified(self):
        def reviewer(argv,cwd,timeout,stdout,stderr,stdin=None):
            if '-o' not in argv:return self.real_execute(argv,cwd,timeout,stdout,stderr,stdin)
            Path(argv[argv.index('-o')+1]).write_text(json.dumps({'verdict':'needs_fix','summary':'found issue',
                'findings':['a.txt is old'],'evidence':['actual file']}));return 0
        with patch.object(h,'execute',side_effect=reviewer):
            r=self.runner({**TASK,'workflow':'review'});self.assertTrue(r.run())
        self.assertEqual(r.state['status'],'reviewed')
        self.assertEqual(r.state['acceptance_report'][0]['status'],'reported')
        self.assertEqual((self.workspace/'a.txt').read_text(),'old')

    def test_acceptance_mapping_is_explicit_and_validated(self):
        for values in ([[1]],[[True]],[],['bad']):
            with self.subTest(values=values),self.assertRaises(h.HarnessError):
                h.validate_task({**TASK,'acceptance_checks':values})
        self.fail_phase=None
        task={k:v for k,v in TASK.items() if k!='acceptance_checks'}
        with patch.object(h,'execute',side_effect=self.client):
            r=self.runner(task);self.assertTrue(r.run())
        self.assertEqual(r.state['acceptance_report'][0]['status'],'reviewed')

    def test_completed_run_is_not_resumed_as_new_work(self):
        self.fail_phase=None
        with patch.object(h,'execute',side_effect=self.client):self.assertTrue(self.runner().run())
        with self.assertRaises(h.HarnessError):self.runner(resume=True)

    def test_resume_cannot_reset_revision_budget_when_check_output_changes(self):
        self.fail_phase=None;checks=[]
        def broken_client(argv,cwd,timeout,stdout,stderr,stdin=None):
            if '-o' in argv and re.search(r'^name: developer$',stdin,re.M):
                self.calls.append(('developer','implementation'))
                Path(argv[argv.index('-o')+1]).write_text(json.dumps({'verdict':'complete','summary':'no repair',
                    'findings':[],'evidence':['fixture']}));return 0
            result=self.client(argv,cwd,timeout,stdout,stderr,stdin)
            if '-o' not in argv:
                checks.append(True)
                Path(stderr).write_text(Path(stderr).read_text()+'\ncheck attempt '+str(len(checks)))
            return result
        with patch.object(h,'execute',side_effect=broken_client):
            first=self.runner();self.assertFalse(first.run())
            resumed=self.runner(resume=True);self.assertFalse(resumed.run())
        self.assertEqual(self.calls.count(('developer','implementation')),2)
        self.assertEqual(resumed.state['budget_used']['implementation'],2)
        self.assertEqual(resumed.state['failure']['kind'],'acceptance_limit')
