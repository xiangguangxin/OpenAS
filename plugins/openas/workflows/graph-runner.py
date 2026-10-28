#!/usr/bin/env python3
"""Validate and sequentially execute a trusted task dependency graph. No parallel scheduling."""
import argparse
import importlib.util
import json
from pathlib import Path
import re
import shutil
import sys

SPEC=importlib.util.spec_from_file_location('graph_codex_team',Path(__file__).with_name('codex-team.py'))
h=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(h)


def plan_graph(doc, base):
    if not isinstance(doc, dict) or doc.get('version') != 1 or not isinstance(doc.get('nodes'), list) or not doc['nodes']:
        raise h.HarnessError('Graph version 1 requires nonempty nodes')
    nodes={}
    for item in doc['nodes']:
        if not isinstance(item, dict) or not isinstance(item.get('id'), str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}',item['id']):
            raise h.HarnessError('Each graph node requires a safe unique id')
        ident=item['id'];deps=item.get('depends_on',[])
        if ident in nodes or not isinstance(deps,list) or any(not isinstance(x,str) for x in deps):
            raise h.HarnessError('Duplicate node or invalid dependencies')
        if len(set(deps)) != len(deps):raise h.HarnessError('Duplicate dependency')
        task=item.get('task')
        if isinstance(task,str):task=json.loads((base/task).read_text())
        h.validate_task(task)
        if not isinstance(item.get('workspace'),str) or not item['workspace']:
            raise h.HarnessError('Node workspace is required')
        workspace=(base/item['workspace']).resolve()
        if not workspace.is_dir():raise h.HarnessError(f'Workspace missing for {ident}')
        nodes[ident]={'id':ident,'depends_on':deps,'workspace':str(workspace),'task':task}
    for node in nodes.values():
        if any(dep not in nodes for dep in node['depends_on']):raise h.HarnessError('Graph references missing dependency')
    ordered=[];ancestors={}
    while len(ordered)<len(nodes):
        ready=[n for n in nodes.values() if n['id'] not in ancestors and all(d in ancestors for d in n['depends_on'])]
        if not ready:raise h.HarnessError('Dependency cycle detected')
        for node in ready:
            ident=node['id']
            ancestors[ident]=set(node['depends_on'])
            for dep in node['depends_on']:ancestors[ident].update(ancestors[dep])
            for previous in ordered:
                if previous['workspace']!=node['workspace']:continue
                overlap=any(a==b or a in b.parents or b in a.parents
                            for a in map(Path,previous['task']['scope']) for b in map(Path,node['task']['scope']))
                if overlap and previous['id'] not in ancestors[ident]:
                    raise h.HarnessError('Shared write scope requires an explicit dependency or separate workspace')
            ordered.append(node)
    return ordered


def run_graph(nodes, output, client, timeout=180, rounds=3, runner_class=None, backend=None):
    runner_class=runner_class or h.Runner
    output=output.resolve()
    for node in nodes:
        workspace=Path(node['workspace'])
        if output==workspace or workspace in output.parents:
            raise h.HarnessError('Graph output must be outside all node workspaces')
    output.mkdir(parents=True,exist_ok=False)
    state={'version':1,'status':'running','plan':nodes,'nodes':{}}
    def save():
        tmp=output/'graph.tmp';tmp.write_text(json.dumps(state,ensure_ascii=False,indent=2));tmp.replace(output/'graph.json')
    save()
    interrupted = False
    for node in nodes:
        ident=node['id']
        if interrupted:
            state['nodes'][ident]={'status':'blocked','dependency_pass':False,'reason':'graph interrupted'}
            save();continue
        blocked=[d for d in node['depends_on'] if not state['nodes'][d]['dependency_pass']]
        if blocked:
            state['nodes'][ident]={'status':'blocked','dependency_pass':False,'blocked_by':blocked}
            save();continue
        state['nodes'][ident]={'status':'running','dependency_pass':False};save()
        try:
            task={**node['task'], 'upstream_results':[{ 'id':dep, **state['nodes'][dep]} for dep in node['depends_on']]}
            runner=runner_class(task,Path(node['workspace']),output/ident,client,timeout=timeout,rounds=rounds,
                                **({'backend': backend} if backend is not None else {}))
            done=runner.run()
            review_checks=runner.state.get('last_checks',[])
            passed=done and (runner.state['status']=='verified' or
                            (runner.state['status']=='reviewed' and runner.state['review']['verdict']=='approve'
                             and review_checks and all(c['exit_code']==0 for c in review_checks)))
            record={'status':runner.state['status'],'dependency_pass':bool(passed),'failure':runner.state.get('failure')}
            record['acceptance_report']=runner.state.get('acceptance_report',[])
            if (output/ident/'state.json').is_file():record['state_file']=str(output/ident/'state.json')
            if (output/ident/'handoff.json').is_file():record['handoff_file']=str(output/ident/'handoff.json')
            state['nodes'][ident]=record
        except (h.HarnessError,OSError,ValueError) as exc:
            state['nodes'][ident]={'status':'stopped','dependency_pass':False,
                                  'failure':{'kind':getattr(exc,'kind','environment'),'message':str(exc)}}
        interrupted = (state['nodes'][ident].get('failure') or {}).get('kind') == 'interrupted'
        save()
    state['status']='verified' if all(n['dependency_pass'] for n in state['nodes'].values()) else 'stopped'
    save();return state


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--graph',type=Path,required=True)
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--plan',action='store_true');mode.add_argument('--run',action='store_true')
    parser.add_argument('--output',type=Path);parser.add_argument('--client',default='codex')
    parser.add_argument('--timeout',type=int,default=180);parser.add_argument('--rounds',type=int,choices=range(1,4),default=3)
    args=parser.parse_args()
    try:
        nodes=plan_graph(json.loads(args.graph.read_text()),args.graph.resolve().parent)
        if args.plan:
            print(json.dumps({'mode':'plan-only','execution':'sequential','nodes':nodes},ensure_ascii=False,indent=2));return 0
        if not args.output or args.timeout<=0:raise h.HarnessError('Run requires output and positive timeout')
        client=shutil.which(args.client)
        if not client:raise h.HarnessError('Codex CLI executable not found')
        state=run_graph(nodes,args.output,client,args.timeout,args.rounds)
        print(json.dumps({'status':state['status'],'state':str(args.output.resolve()/'graph.json')}))
        return 0 if state['status']=='verified' else 1
    except (h.HarnessError,OSError,ValueError) as exc:
        print(str(exc),file=sys.stderr);return 2


if __name__=='__main__':sys.exit(main())
