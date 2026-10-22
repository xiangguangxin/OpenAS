import importlib.util
from pathlib import Path
import tempfile
import unittest

SPEC=importlib.util.spec_from_file_location('graph_runner',Path(__file__).parents[1]/'graph-runner.py')
g=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(g)
TASK={'requirement':'test','scope':['a.txt'],'acceptance':['test'],'checks':[['unused']]}


class GraphTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        for name in ('a','b','c'):(self.root/name).mkdir()

    def node(self,name,deps=None,workspace=None):
        return {'id':name,'task':TASK,'workspace':workspace or name,'depends_on':deps or []}

    def plan(self,nodes):return g.plan_graph({'version':1,'nodes':nodes},self.root)

    def test_topological_order_uses_dependencies_not_input_order(self):
        nodes=self.plan([self.node('b',['a']),self.node('a')])
        self.assertEqual([x['id'] for x in nodes],['a','b'])

    def test_missing_cycle_and_duplicate_dependencies_are_rejected(self):
        cases=[[self.node('a',['missing'])],[self.node('a',['b']),self.node('b',['a'])],
               [self.node('a'),self.node('a')]]
        for nodes in cases:
            with self.subTest(nodes=nodes),self.assertRaises(g.h.HarnessError):self.plan(nodes)

    def test_shared_scope_requires_explicit_order(self):
        with self.assertRaises(g.h.HarnessError):self.plan([self.node('a'),self.node('b',workspace='a')])
        self.assertEqual(len(self.plan([self.node('a'),self.node('b',['a'],workspace='a')])),2)

    def test_failed_dependency_blocks_only_downstream(self):
        calls=[]
        class Fake:
            def __init__(self,task,workspace,output,client,**kwargs):self.name=workspace.name
            def run(self):
                calls.append(self.name);self.state={'status':'stopped' if self.name=='a' else 'verified'}
                return self.name!='a'
        state=g.run_graph(self.plan([self.node('a'),self.node('b',['a']),self.node('c')]),
                          self.root/'run','unused',runner_class=Fake)
        self.assertEqual(calls,['a','c'])
        self.assertEqual(state['nodes']['b']['status'],'blocked')
        self.assertEqual(state['status'],'stopped')

    def test_review_findings_are_not_a_passing_dependency(self):
        class Fake:
            def __init__(self,*args,**kwargs):pass
            def run(self):self.state={'status':'reviewed','review':{'verdict':'needs_fix'}};return True
        state=g.run_graph(self.plan([self.node('a'),self.node('b',['a'])]),self.root/'run','unused',runner_class=Fake)
        self.assertFalse(state['nodes']['a']['dependency_pass'])
        self.assertEqual(state['nodes']['b']['status'],'blocked')

    def test_graph_records_cannot_be_written_into_any_workspace(self):
        with self.assertRaises(g.h.HarnessError):
            g.run_graph(self.plan([self.node('a')]),self.root/'a/run','unused')

    def test_downstream_receives_actual_upstream_receipts(self):
        tasks=[]
        class Fake:
            def __init__(self,task,*args,**kwargs):tasks.append(task)
            def run(self):self.state={'status':'verified','acceptance_report':[{'status':'passed'}]};return True
        g.run_graph(self.plan([self.node('a'),self.node('b',['a'])]),self.root/'run','unused',runner_class=Fake)
        self.assertEqual(tasks[1]['upstream_results'][0]['id'],'a')
        self.assertTrue(tasks[1]['upstream_results'][0]['dependency_pass'])
        self.assertEqual(tasks[1]['upstream_results'][0]['acceptance_report'],[{'status':'passed'}])
        self.assertNotIn('upstream_results',TASK)

    def test_review_approval_cannot_override_failed_host_checks(self):
        class Fake:
            def __init__(self,*args,**kwargs):pass
            def run(self):
                self.state={'status':'reviewed','review':{'verdict':'approve'},'last_checks':[{'exit_code':1}]}
                return True
        state=g.run_graph(self.plan([self.node('a'),self.node('b',['a'])]),self.root/'run','unused',runner_class=Fake)
        self.assertFalse(state['nodes']['a']['dependency_pass'])
        self.assertEqual(state['nodes']['b']['status'],'blocked')

    def test_interruption_does_not_start_independent_nodes(self):
        calls=[]
        class Fake:
            def __init__(self,task,workspace,*args,**kwargs):calls.append(workspace.name)
            def run(self):self.state={'status':'stopped','failure':{'kind':'interrupted'}};return False
        state=g.run_graph(self.plan([self.node('a'),self.node('b')]),self.root/'run','unused',runner_class=Fake)
        self.assertEqual(calls,['a'])
        self.assertEqual(state['nodes']['b']['reason'],'graph interrupted')
