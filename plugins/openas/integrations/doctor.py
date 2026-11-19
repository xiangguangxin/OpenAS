#!/usr/bin/env python3
"""Read-only customer preflight. Checks never install tools or start model tasks."""
import argparse
import importlib.util
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys

SPEC = importlib.util.spec_from_file_location('doctor_skills', Path(__file__).with_name('codex_skills.py'))
skills = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(skills)


def check(project, client='codex', nova=None, native=False):
    checks = []
    def add(name, ok, detail):
        checks.append({'name': name, 'status': 'passed' if ok else 'failed', 'detail': detail})
    add('Python >=3.10', sys.version_info >= (3, 10), platform.python_version())
    add('project directory', Path(project).is_dir(), 'Existing project required')
    executable = shutil.which(client)
    add('client executable', bool(executable), client)
    if executable:
        try:
            version = subprocess.run([executable, '--version'], capture_output=True, text=True, timeout=10)
            add('client starts', version.returncode == 0, version.stdout.strip()[:120])
            if client == 'codex':
                help_result = subprocess.run([executable, 'exec', '--help'], capture_output=True, text=True, timeout=10)
                required = ('--ephemeral', '--output-schema', '--sandbox')
                add('workflow CLI flags', help_result.returncode == 0 and all(x in help_result.stdout for x in required),
                    'Requires '+', '.join(required))
        except (OSError, subprocess.TimeoutExpired):
            add('client starts', False, 'Client launch failed or timed out; inspect locally')
    if client == 'codex':
        try:
            installed = skills.install(project, 'check')
            add('OpenAS skill integrity', True, str(len(installed['skills']))+' managed skills')
            add('OpenAS skill version', installed['source_matches'], 'Run update when source differs')
            if native and executable:
                discovery = skills.native_check(project, installed['skills'], executable)
                add('native skill discovery', discovery['native_discovery'] == 'passed',
                    'Missing: '+', '.join(discovery['missing']))
        except (OSError, ValueError) as exc:
            add('OpenAS skill installation', False, str(exc))
    if nova:
        executable = shutil.which(str(nova))
        add('Nova executable', bool(executable), 'Use an executable in the interactive desktop session')
        add('native desktop platform', platform.system() in ('Windows', 'Darwin'), platform.system())
        if executable:
            try:
                result = subprocess.run([executable, '--version'], capture_output=True, text=True, timeout=10)
                add('Nova starts', result.returncode == 0, 'Version command only; desktop permissions not tested')
            except (OSError, subprocess.TimeoutExpired):
                add('Nova starts', False, 'Cannot start Nova')
    return {'ready_for_next_check': all(x['status'] == 'passed' for x in checks), 'checks': checks,
            'not_checked': ['Client authentication and available quota', 'MCP live connections and permissions',
                            'Real application task and business acceptance', 'Windows/macOS Nova E2E'],
            'model_turn_started': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--client', choices=('codex', 'claude'), default='codex')
    parser.add_argument('--nova', type=Path)
    parser.add_argument('--native-skills', action='store_true')
    args = parser.parse_args()
    result = check(args.project, args.client, args.nova, args.native_skills)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['ready_for_next_check'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
