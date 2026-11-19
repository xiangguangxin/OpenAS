#!/usr/bin/env python3
"""Validate and sequentially execute a trusted task dependency graph. No parallel scheduling."""
import argparse
import hashlib
import time
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
        if isinstance(task,str):task=json.loads((base/task).read_text(encoding='utf-8'))
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
                first, second = Path(previous['workspace']), Path(node['workspace'])
                if first != second:
                    if first in second.parents or second in first.parents:
                        raise h.HarnessError('Node workspaces must be equal or disjoint, not nested')
                    continue
                for source_task, output_task in ((previous['task'], node['task']), (node['task'], previous['task'])):
                    for artifact in map(Path, output_task.get('artifacts', [])):
                        if any(source == artifact or artifact in source.parents or source in artifact.parents
                               for source in map(Path, source_task['scope'])):
                            raise h.HarnessError('Graph artifact directories must not overlap any node source scope')
                overlap=any(a==b or a in b.parents or b in a.parents
                            for a in map(Path,previous['task']['scope']) for b in map(Path,node['task']['scope']))
                if overlap and previous['id'] not in ancestors[ident]:
                    raise h.HarnessError('Shared write scope requires an explicit dependency or separate workspace')
            ordered.append(node)
    return ordered


def evidence_digest(directory):
    entries = {}
    if not (directory/'state.json').is_file():
        raise h.HarnessError('Completed node has no state evidence; inspect the node and start a new graph')
    for path in sorted(directory.rglob('*')):
        if path.is_symlink():
            raise h.HarnessError('Node evidence must not contain symlinks')
        if path.is_file() and path.name != '.run.lock':
            entries[path.relative_to(directory).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return entries


def workspace_snapshots(nodes):
    workspaces = {}
    for node in nodes:
        workspaces.setdefault(node['workspace'], set()).update(map(Path, node['task'].get('artifacts', [])))
    return {workspace: h.snapshot(Path(workspace), tuple(artifacts)) for workspace, artifacts in workspaces.items()}


def run_graph(nodes, output, client, timeout=180, rounds=3, runner_class=None, backend=None,
              resume=False, restart_stages=False):
    runner_class = runner_class or h.Runner
    raw_output = Path(output).absolute()
    if any(p.is_symlink() for p in (raw_output, *raw_output.parents)):
        raise h.HarnessError('Graph output must not traverse symlinks')
    output = raw_output.resolve()
    for node in nodes:
        workspace = Path(node['workspace'])
        if output == workspace or workspace in output.parents:
            raise h.HarnessError('Graph output must be outside all node workspaces')
    if restart_stages and not resume:
        raise h.HarnessError('restart-stages requires resume')
    options = {'client': client, 'timeout': timeout, 'rounds': rounds,
               'backend': (backend or h.BACKENDS.CodexBackend()).identity()}
    resources = hashlib.sha256((h.Runner.resource_fingerprint()+Path(__file__).read_text(encoding='utf-8')).encode()).hexdigest()
    if not resume:
        output.mkdir(parents=True, exist_ok=False)
    if (output/'.graph.lock').is_symlink() or (output/'graph.json').is_symlink():
        raise h.HarnessError('Graph state and lock must not be symlinks')
    with (output/'.graph.lock').open('a+', encoding='utf-8') as lock:
        try:
            h.MEMORY_MODULE.support.lock(lock, blocking=False)
        except BlockingIOError as exc:
            raise h.HarnessError('Graph already active; concurrent resume is forbidden') from exc
        try:
            if resume:
                state = json.loads((output/'graph.json').read_text(encoding='utf-8'))
                if (not isinstance(state, dict) or state.get('version') != 2
                        or not isinstance(state.get('nodes'), dict)
                        or any(not isinstance(v, dict) for v in state.get('nodes', {}).values())
                        or set(state.get('nodes', {})) - {n['id'] for n in nodes}
                        or state.get('plan') != nodes
                        or state.get('execution') != options or state.get('resources_sha256') != resources):
                    raise h.HarnessError('Graph plan, execution options or rules changed; start a new graph')
                current = workspace_snapshots(nodes)
                previous = state.get('workspace_checkpoints', {})
                if current != previous:
                    allowed = {}
                    for node in nodes:
                        if not state['nodes'].get(node['id'], {}).get('dependency_pass'):
                            allowed.setdefault(node['workspace'], set()).update(node['task']['scope'])
                    for workspace, files in current.items():
                        old = previous.get(workspace, {})
                        changed = {p for p in old.keys() | files.keys() if old.get(p) != files.get(p)}
                        if not restart_stages or changed - allowed.get(workspace, set()):
                            raise h.HarnessError('Graph workspace changed; inspect in-scope changes and use --resume --restart-stages')
                for ident, record in state['nodes'].items():
                    if record.get('dependency_pass'):
                        if not record.get('evidence_sha256') or evidence_digest(output/ident) != record['evidence_sha256']:
                            raise h.HarnessError('Completed node evidence changed or is missing; start a new graph')
                state.setdefault('recoveries', []).append({'at': time.time()})
            else:
                state = {'version': 2, 'status': 'running', 'plan': nodes, 'nodes': {},
                         'execution': options, 'resources_sha256': resources,
                         'workspace_checkpoints': workspace_snapshots(nodes), 'recoveries': []}

            def save():
                temporary = output/'graph.tmp'
                temporary.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')
                temporary.replace(output/'graph.json')

            state['status'] = 'running'
            save()
            interrupted = False
            for node in nodes:
                ident = node['id']
                if state['nodes'].get(ident, {}).get('dependency_pass'):
                    continue
                if interrupted:
                    state['nodes'][ident] = {'status': 'blocked', 'dependency_pass': False, 'reason': 'graph interrupted'}
                    save(); continue
                blocked = [d for d in node['depends_on'] if not state['nodes'][d]['dependency_pass']]
                if blocked:
                    state['nodes'][ident] = {'status': 'blocked', 'dependency_pass': False, 'blocked_by': blocked}
                    save(); continue
                state['nodes'][ident] = {'status': 'running', 'dependency_pass': False}
                save()
                try:
                    task = {**node['task'], 'upstream_results': [
                        {'id': dep, **state['nodes'][dep]} for dep in node['depends_on']]}
                    node_output = output/ident
                    recovering = resume and node_output.exists()
                    kwargs = {'timeout': timeout, 'rounds': rounds}
                    if backend is not None:
                        kwargs['backend'] = backend
                    if recovering:
                        kwargs.update(resume=True, restart_stages=restart_stages)
                    runner = runner_class(task, Path(node['workspace']), node_output, client, **kwargs)
                    done = runner.run()
                    review_checks = runner.state.get('last_checks', [])
                    passed = done and (runner.state['status'] == 'verified' or
                        (runner.state['status'] == 'reviewed' and runner.state['review']['verdict'] == 'approve'
                         and review_checks and all(c['exit_code'] == 0 for c in review_checks)))
                    record = {'status': runner.state['status'], 'dependency_pass': bool(passed),
                              'failure': runner.state.get('failure'),
                              'acceptance_report': runner.state.get('acceptance_report', [])}
                    for name in ('state', 'handoff'):
                        if (node_output/(name+'.json')).is_file():
                            record[name+'_file'] = str(node_output/(name+'.json'))
                    if passed and (node_output/'state.json').is_file():
                        record['evidence_sha256'] = evidence_digest(node_output)
                    state['nodes'][ident] = record
                except (h.HarnessError, OSError, ValueError, KeyboardInterrupt) as exc:
                    state['nodes'][ident] = {'status': 'stopped', 'dependency_pass': False,
                        'failure': {'kind': getattr(exc, 'kind', 'interrupted' if isinstance(exc, KeyboardInterrupt) else 'environment'),
                                    'message': str(exc)}}
                interrupted = (state['nodes'][ident].get('failure') or {}).get('kind') == 'interrupted'
                state['workspace_checkpoints'] = workspace_snapshots(nodes)
                save()
            state['status'] = 'verified' if all(n['dependency_pass'] for n in state['nodes'].values()) else 'stopped'
            save()
            return state
        finally:
            h.MEMORY_MODULE.support.unlock(lock)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--graph',type=Path,required=True)
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--plan',action='store_true');mode.add_argument('--run',action='store_true')
    parser.add_argument('--resume', action='store_true')
    parser.add_argument('--restart-stages', action='store_true')
    parser.add_argument('--output',type=Path);parser.add_argument('--client',default='codex')
    parser.add_argument('--timeout',type=int,default=180);parser.add_argument('--rounds',type=int,choices=range(1,4),default=3)
    args=parser.parse_args()
    try:
        if (args.resume or args.restart_stages) and not args.run:
            raise h.HarnessError('Recovery options require --run')
        nodes=plan_graph(json.loads(args.graph.read_text(encoding='utf-8')),args.graph.resolve().parent)
        if args.plan:
            print(json.dumps({'mode':'plan-only','execution':'sequential','nodes':nodes},ensure_ascii=False,indent=2));return 0
        if not args.output or args.timeout<=0:raise h.HarnessError('Run requires output and positive timeout')
        client=shutil.which(args.client)
        if not client:raise h.HarnessError('Codex CLI executable not found')
        state=run_graph(nodes,args.output,client,args.timeout,args.rounds,
                        resume=args.resume, restart_stages=args.restart_stages)
        print(json.dumps({'status':state['status'],'state':str(args.output.resolve()/'graph.json')}))
        return 0 if state['status']=='verified' else 1
    except (h.HarnessError,OSError,ValueError) as exc:
        print(str(exc),file=sys.stderr);return 2


if __name__=='__main__':sys.exit(main())
