#!/usr/bin/env python3
"""Opt-in real-client behavior checks. Uses existing Codex login and model settings."""
import argparse
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT/'plugins/openas'
SPEC = importlib.util.spec_from_file_location('eval_harness', PLUGIN/'workflows/codex-team.py')
h = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(h)
CASES = {
    'ordinary-review': ('评审这个小项目，按 README 中的接口约定找实际问题，直接给出结论。仅评审，不修改文件。',
                        'requesting-code-review', False, False),
    'explicit-grilling': ('我希望你用采访方式，对“批量导入文件，遇到错误就继续”的方案持续追问，先帮助我明确关键取舍。不要实现。',
                          'grilling', False, True),
    'repair': ('修复 average.py 的空输入异常，遵循 README 约定并运行现有测试。只允许修改 average.py，不修改测试，不安装依赖。',
               'bug-fix', True, False),
}
SCHEMA = {'type': 'object', 'additionalProperties': False, 'properties': {
    'selected_skill': {'type': 'string'}, 'summary': {'type': 'string'},
    'findings': {'type': 'array', 'items': {'type': 'string'}},
    'questions': {'type': 'array', 'items': {'type': 'string'}},
    'evidence': {'type': 'array', 'items': {'type': 'string'}},
}, 'required': ['selected_skill', 'summary', 'findings', 'questions', 'evidence']}


def evaluate(name, client, output, timeout):
    request, expected_skill, writable, expect_questions = CASES[name]
    case_output = output/name
    case_output.mkdir()
    schema = case_output/'schema.json'
    schema.write_text(json.dumps(SCHEMA))
    with tempfile.TemporaryDirectory(prefix='openas-skill-eval-') as tmp:
        workspace = Path(tmp)
        (workspace/'README.md').write_text('average(items) returns the arithmetic mean; an empty list must return 0.\n')
        (workspace/'average.py').write_text('def average(items):\n    return sum(items) / len(items)\n')
        (workspace/'test_average.py').write_text('''import unittest
from average import average
class AverageTests(unittest.TestCase):
    def test_empty(self): self.assertEqual(average([]), 0)
    def test_numbers(self): self.assertEqual(average([2, 4]), 3)
if __name__ == '__main__': unittest.main()
''')
        before = h.snapshot(workspace)
        catalog = []
        for skill in sorted((PLUGIN/'skills').glob('*/SKILL.md')):
            header = skill.read_text().split('---', 2)[1]
            catalog.append({'path': str(skill), 'metadata': header.strip()})
        prompt = ('Select the relevant skill from the available catalog and read its SKILL.md before performing the task. '
                  'Use actual files and checks, not just a proposed answer. Preserve task scope. '
                  'Do not install dependencies, commit, push, access external services or spawn agents. '
                  'This is a disposable local fixture; all checks must use Python -B or PYTHONDONTWRITEBYTECODE=1. '
                  'Return only the requested final JSON.\n'
                  f'Available skills:\n{json.dumps(catalog, ensure_ascii=False)}\n'
                  f'Task:\n{request}\n')
        (case_output/'prompt.txt').write_text(prompt)
        command = [client, 'exec', '--ephemeral', '--skip-git-repo-check', '--color', 'never',
                   '--sandbox', 'workspace-write' if writable else 'read-only', '-C', str(workspace),
                   '--output-schema', str(schema), '-o', str(case_output/'result.json'), '-']
        print(f'Evaluating {name}', flush=True)
        rc = h.execute(command, workspace, timeout, case_output/'stdout.log', case_output/'stderr.log', prompt)
        after = h.snapshot(workspace)
        changed = sorted(x for x in before.keys() | after.keys() if before.get(x) != after.get(x))
        result = json.loads((case_output/'result.json').read_text()) if rc == 0 else {}
        gates = {
            'client_success': rc == 0,
            'skill_routing': result.get('selected_skill') == expected_skill,
            'scope_preserved': set(changed) <= ({'average.py'} if writable else set()),
            'question_policy': bool(result.get('questions')) == expect_questions,
            'evidence_present': bool(result.get('evidence')),
        }
        if name == 'ordinary-review':
            gates['findings_present'] = bool(result.get('findings'))
        if writable:
            check = h.execute([sys.executable, '-B', '-m', 'unittest', '-v'], workspace, 30,
                              case_output/'checks.stdout.log', case_output/'checks.stderr.log')
            gates['host_tests_pass'] = check == 0
            gates['implementation_changed'] = changed == ['average.py']
        receipt = {'case': name, 'gates': gates, 'passed': all(gates.values()),
                   'changed_files': changed, 'result': result,
                   'limits': 'Routing and filesystem/test behavior are host-checked; human review of prose and findings is still required.'}
        (case_output/'receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2))
        return receipt


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--client', default='codex')
    p.add_argument('--case', choices=CASES)
    p.add_argument('--output', required=True, type=Path)
    p.add_argument('--timeout', type=int, default=180)
    args = p.parse_args()
    client = shutil.which(args.client)
    if not client or args.timeout <= 0:
        p.error('An installed client and a positive timeout are required')
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    receipts = []
    try:
        for name in ([args.case] if args.case else CASES):
            receipts.append(evaluate(name, client, output, args.timeout))
    except (h.HarnessError, OSError, ValueError) as exc:
        (output/'error.json').write_text(json.dumps({'status': 'failed', 'error': str(exc)}))
        print(str(exc), file=sys.stderr)
        return 1
    report = {'status': 'passed' if all(r['passed'] for r in receipts) else 'failed', 'cases': receipts}
    (output/'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(json.dumps({'status': report['status'], 'report': str(output/'report.json')}))
    return 0 if report['status'] == 'passed' else 1


if __name__ == '__main__':
    sys.exit(main())
