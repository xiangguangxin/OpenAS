import importlib.util
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location('design_harness', Path(__file__).parents[1]/'codex-team.py')
h = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(h)
FILES = h.DESIGN.DEFAULT_OUTPUTS
TASK = {'workflow':'research-design', 'research_mode':'provided', 'requirement':'Design only from brief.md',
        'scope':list(FILES.values()), 'acceptance':['All six design documents exist; no product code'],
        'checks':[[sys.executable, '-B', '-c',
            'from pathlib import Path; assert all(Path(p).read_text().strip() for p in '+repr(list(FILES.values()))+')']],
        'acceptance_checks':[[0]]}


class ResearchDesignTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.w=self.root/'work';self.w.mkdir()
        (self.w/'brief.md').write_text('Local-only planning fixture, market demand unknown.')
        self.calls=[];self.prompts=[];self.fail=None;self.reject=0;self.target='architecture-design'
        self.empty=False;self.mutate=None;self.search=False;self.bad_target=False
        self.check_fail=False;self.verifier_fail=False;self.fail_revision=False;self.blocked=False
        self.real=h.execute
        fingerprint=patch.object(h.Runner,'resource_fingerprint',return_value='design-route-fixture')
        fingerprint.start();self.addCleanup(fingerprint.stop)

    def client(self, argv, cwd, timeout, stdout, stderr, stdin=None):
        if '-o' not in argv:
            if self.check_fail and all((cwd/p).exists() for p in FILES.values()):
                Path(stdout).write_text('');Path(stderr).write_text('fixture check failure');return 1
            return self.real(argv,cwd,timeout,stdout,stderr,stdin)
        path=Path(argv[argv.index('-o')+1]);phase=path.name.split('-',1)[1].removesuffix('.result.json')
        self.calls.append(phase);self.prompts.append((argv,stdin))
        Path(stdout).write_text(json.dumps({'type':'item.completed','item':{'type':'web_search'}})+'\n' if self.search else '')
        Path(stderr).write_text('')
        if phase==self.fail:self.fail=None;return 7
        verdict='complete';findings=[]
        if phase in FILES and not self.empty:
            f=cwd/FILES[phase];f.parent.mkdir(exist_ok=True);f.write_text('Design for '+phase)
        if self.mutate:(cwd/self.mutate).write_text('unauthorized')
        if phase=='design-gate':
            verdict='needs_fix' if self.reject else 'approve'
            if self.reject:
                self.reject-=1;findings=['R1 missing failure flow']
                if self.fail_revision:self.fail='design-documentation';self.fail_revision=False
        if phase in FILES and self.blocked:
            verdict='fail';findings=['Required product decision unavailable']
        if phase=='verification':
            verdict='fail' if self.verifier_fail else 'pass'
            if self.verifier_fail:findings=['A1 incomplete'];self.verifier_fail=False
        result={'verdict':verdict,'summary':'fixture','findings':findings,'evidence':['actual fixture']}
        if phase=='design-gate':result['revision_from']='invalid' if self.bad_target else self.target if verdict=='needs_fix' else 'none'
        path.write_text(json.dumps(result));return 0

    def runner(self, task=None, **kwargs):
        return h.Runner(task or TASK,self.w,self.root/'run','fake',rounds=2,**kwargs)

    def test_seven_stages_emit_files_then_checks_and_independent_verification(self):
        with patch.object(h,'execute',side_effect=self.client):
            r=self.runner();self.assertTrue(r.run())
        self.assertEqual(self.calls,[*FILES,'design-gate','verification'])
        self.assertEqual(r.state['verification_subject'],'design-artifacts')
        self.assertEqual(r.state['final_checks'][0]['exit_code'],0)
        self.assertEqual(r.state['baseline_checks'][0]['exit_code'],1)
        self.assertTrue((r.output/'design-review.json').is_file())
        self.assertEqual(set(json.loads((r.output/'design-artifacts.json').read_text())),set(FILES))
        self.assertEqual((self.w/'brief.md').read_text(),'Local-only planning fixture, market demand unknown.')
        self.assertEqual(r.state['budget_used']['architecture-design'],1)
        for argv,prompt in self.prompts:
            self.assertIn('web_search="disabled"',argv)
            self.assertIn('Domain skill',prompt) if 'verification' not in argv[argv.index('-o')+1] else None

    def test_review_rewinds_earliest_affected_stage_and_all_downstream(self):
        self.reject=1
        with patch.object(h,'execute',side_effect=self.client):
            r=self.runner();self.assertTrue(r.run())
        self.assertEqual(self.calls,[*FILES,'design-gate','architecture-design','design-documentation','design-gate','verification'])
        self.assertIn('missing failure flow',self.prompts[7][1])
        self.assertEqual(r.state['budget_used']['market-research'],1)

    def test_resume_reuses_artifacts_and_review_round_context(self):
        self.reject=1;self.fail='design-documentation'
        with patch.object(h,'execute',side_effect=self.client):
            self.assertFalse(self.runner().run())
            r=self.runner(resume=True);self.assertTrue(r.run())
        self.assertEqual(self.calls.count('market-research'),1)
        self.assertEqual(self.calls.count('design-documentation'),3) # failed, first success, revision

    def test_resume_after_interruption_in_review_revision(self):
        self.reject=1;self.fail_revision=True
        with patch.object(h,'execute',side_effect=self.client):
            self.assertFalse(self.runner().run())
            r=self.runner(resume=True);self.assertTrue(r.run())
        self.assertEqual(self.calls.count('market-research'),1)
        self.assertEqual(self.calls.count('architecture-design'),2)
        self.assertEqual(self.calls.count('design-documentation'),3)

    def test_author_can_stop_on_blocking_unknown(self):
        self.blocked=True
        with patch.object(h,'execute',side_effect=self.client):
            r=self.runner();self.assertFalse(r.run())
        self.assertEqual(r.state['failure']['kind'],'design_blocked')
        self.assertEqual(self.calls,['market-research'])

    def test_resume_does_not_reset_exhausted_revision_budget(self):
        self.reject=9
        with patch.object(h,'execute',side_effect=self.client):
            first=self.runner();self.assertFalse(first.run())
            resumed=self.runner(resume=True);self.assertFalse(resumed.run())
        self.assertEqual(self.calls.count('architecture-design'),2)
        self.assertEqual(resumed.state['failure']['kind'],'review_limit')

    def test_missing_document_cannot_be_replaced_with_success_claim(self):
        self.empty=True
        with patch.object(h,'execute',side_effect=self.client):
            r=self.runner();self.assertFalse(r.run())
        self.assertEqual(self.calls,['market-research'])
        self.assertEqual(r.state['failure']['kind'],'invalid_result')

    def test_each_phase_cannot_edit_other_outputs(self):
        (self.w/'design').mkdir();self.mutate=FILES['architecture-design']
        with patch.object(h,'execute',side_effect=self.client):
            r=self.runner();self.assertFalse(r.run())
        self.assertEqual(r.state['failure']['kind'],'scope_violation')

    def test_product_implementation_is_out_of_scope(self):
        self.mutate='app.py'
        with patch.object(h,'execute',side_effect=self.client):
            r=self.runner();self.assertFalse(r.run())
        self.assertEqual(r.state['failure']['kind'],'scope_violation')

    def test_live_market_research_requires_native_search_not_a_model_claim(self):
        with patch.object(h,'execute',side_effect=self.client):
            r=self.runner({**TASK,'research_mode':'live'});self.assertFalse(r.run())
        self.assertEqual(r.state['failure']['kind'],'research_unavailable')
        self.assertIn('web_search="live"',self.prompts[0][0])

    def test_live_search_evidence_is_recorded(self):
        self.search=True
        with patch.object(h,'execute',side_effect=self.client):
            r=self.runner({**TASK,'research_mode':'live'});self.assertTrue(r.run())
        self.assertEqual(r.state['history'][0]['native_search_count'],1)

    def test_invalid_review_target_fails_closed(self):
        self.bad_target=True
        with patch.object(h,'execute',side_effect=self.client):
            r=self.runner();self.assertFalse(r.run())
        self.assertEqual(r.state['failure']['kind'],'invalid_result')

    def test_host_failure_never_reaches_verifier_or_success(self):
        self.check_fail=True
        with patch.object(h,'execute',side_effect=self.client):
            r=self.runner();self.assertFalse(r.run())
        self.assertNotIn('verification',self.calls)
        self.assertFalse(r.state['done'])

    def test_failed_verifier_revises_pipeline_before_approval(self):
        self.verifier_fail=True
        with patch.object(h,'execute',side_effect=self.client):
            r=self.runner();self.assertTrue(r.run())
        self.assertEqual(self.calls.count('market-research'),2)
        self.assertEqual(self.calls.count('verification'),2)

    def test_validation_rejects_missing_mode_overlap_hidden_outputs_and_artifacts(self):
        for extra in ({'research_mode':'auto'},{'scope':['app.py']}, {'artifacts':['cache']},
                      {'design_outputs':{**FILES,'market-research':'.git/market.md'}},
                      {'design_outputs':{**FILES,'market-research':'.'}},
                      {'design_outputs':{**FILES,'market-research':'./market.md'}},
                      {'design_outputs':{**FILES,'market-research':'docs/../market.md'}},
                      {'design_outputs':{**FILES,'market-research':FILES['architecture-design']}},
                      {'design_outputs':{'market-research':'market.md'}}):
            with self.subTest(extra=extra),self.assertRaises(h.HarnessError):h.validate_task({**TASK,**extra})
        with self.assertRaises(h.HarnessError):h.validate_task({**TASK,'workflow':'direct'})

    def test_custom_output_mapping_is_used(self):
        files={k:'docs/'+Path(v).name for k,v in FILES.items()}
        self.assertEqual(h.DESIGN.outputs(h.validate_task({**TASK,'design_outputs':files,'scope':list(files.values())})),files)

    def test_graph_can_plan_a_dedicated_design_node(self):
        spec=importlib.util.spec_from_file_location('design_graph',Path(__file__).parents[1]/'graph-runner.py')
        graph=importlib.util.module_from_spec(spec);spec.loader.exec_module(graph)
        nodes=graph.plan_graph({'version':1,'nodes':[{'id':'design','workspace':str(self.w),'task':TASK}]},self.root)
        self.assertEqual(nodes[0]['task']['workflow'],'research-design')

    def test_search_claim_in_prose_is_not_native_evidence(self):
        p=self.root/'log';p.write_text('I used web_search\n'+json.dumps({'type':'item.completed','item':{'type':'agent_message','text':'web_search'}}))
        self.assertEqual(h.DESIGN.native_searches(p),0)
