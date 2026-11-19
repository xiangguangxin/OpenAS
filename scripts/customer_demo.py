#!/usr/bin/env python3
"""Prepare a repeatable repair + downstream review demo without changing source fixtures."""
import argparse
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT/'plugins/openas/workflows/examples'


def prepare(output):
    output = output.absolute()
    if output == ROOT or ROOT in output.parents or any(p.is_symlink() for p in (output, *output.parents)):
        raise ValueError('Prepare the demo outside the source repository without symlinks')
    if output.exists() or output.is_symlink():
        raise ValueError('Demo output must be new')
    output.mkdir(parents=True)
    shutil.copytree(EXAMPLES/'pagination-fixture', output/'workspace')
    task = json.loads((EXAMPLES/'pagination-task.json').read_text())
    task['checks'][0][0] = sys.executable
    (output/'pagination-task.json').write_text(json.dumps(task, indent=2), encoding='utf-8')
    graph = json.loads((EXAMPLES/'workflow-graph.json').read_text())
    graph['nodes'][1]['task']['checks'][0][0] = sys.executable
    (output/'graph.json').write_text(json.dumps(graph, indent=2), encoding='utf-8')
    return {'fixture': str(output/'workspace'), 'graph': str(output/'graph.json'),
            'run_command': [sys.executable, str(ROOT/'plugins/openas/workflows/graph-runner.py'),
                            '--graph', str(output/'graph.json'), '--run', '--output', str(output/'run')],
            'resume': 'Repeat the run command with --resume after inspecting the interrupted run.',
            'model_started': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(prepare(args.output), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
