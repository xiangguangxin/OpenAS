#!/usr/bin/env python3
"""Opt-in real-client behavior checks. Uses existing Codex login and model settings."""
import argparse
import importlib.util
import json
import re
from pathlib import Path
import shutil
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
MAINTENANCE_SPEC = importlib.util.spec_from_file_location('maintenance_cases', Path(__file__).with_name('maintenance_cases.py'))
maintenance = importlib.util.module_from_spec(MAINTENANCE_SPEC)
MAINTENANCE_SPEC.loader.exec_module(maintenance)

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
    'workflow-routing': ('先不要实现。请为这个小项目选择最小足够的工作流路线并说明阶段：修复 average 的空输入，接口和测试要求已经明确。',
                         'workflow-routing', False, False),
    'context-handoff': ('仅整理当前任务交接，不实现、不修复。目标是让下一会话修复 README 约定的空输入行为；目前尚未修改源码。请核对实际文件，区分已知事实、未验证项与下一步。',
                        'context-handoff', False, False),
    'acceptance-tracking': ('仅做逐项验收追踪，不修改文件。把 README 的每条接口约定关联到实际现有测试，区分已验证、失败与未覆盖；不能把模型判断写成宿主测试已通过。',
                            'acceptance-tracking', False, False),
    'english-analysis': ('Explain this small codebase: its entry points, data flow, and how tests exercise the public function. Cite actual files. Analysis only; do not edit or ask for confirmation.',
                         'codebase-analysis', False, False),
    'chinese-analysis': ('只读分析这个小项目：解释入口、数据流及测试如何调用公开函数，引用实际文件。不要修改或修复，不要询问确认。',
                         'codebase-analysis', False, False),
    'explicit-english': ('只读分析这个小项目的入口、数据流和测试调用关系，引用实际文件，不修改、不修复、不提问。Respond in English.',
                         'codebase-analysis', False, False),
    'explicit-chinese': ('Analyze the entry points, data flow, and test calls in this small codebase. Cite files, do not edit or repair, and do not ask confirmation questions. 请用中文回复。',
                         'codebase-analysis', False, False),
}
CASE_LANGUAGES = {'english-analysis': 'en', 'chinese-analysis': 'zh',
                  'explicit-english': 'en', 'explicit-chinese': 'zh'}
SCHEMA = {'type': 'object', 'additionalProperties': False, 'properties': {
    'selected_skill': {'type': 'string'}, 'summary': {'type': 'string'},
    'findings': {'type': 'array', 'items': {'type': 'string'}},
    'questions': {'type': 'array', 'items': {'type': 'string'}},
    'evidence': {'type': 'array', 'items': {'type': 'string'}},
}, 'required': ['selected_skill', 'summary', 'findings', 'questions', 'evidence']}


def evaluate(name, client, output, timeout, plugin=PLUGIN):
    fixture = ''
    expectations = ()
    if name in maintenance.CASES:
        request, expected_skill, fixture, expectations = maintenance.CASES[name]
        writable = expect_questions = False
    else:
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
        if fixture:
            (workspace/'fixture.txt').write_text(fixture + '\n')
        before = h.snapshot(workspace)
        catalog = []
        for skill in sorted((plugin/'skills').glob('*/SKILL.md')):
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
        started = time.monotonic()
        rc = h.execute(command, workspace, timeout, case_output/'stdout.log', case_output/'stderr.log', prompt)
        elapsed = time.monotonic() - started
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
        if expectations:
            response = '\n'.join([result.get('summary', ''), *result.get('findings', []), *result.get('evidence', [])])
            gates['fixture_signals'] = all(re.search(pattern, response, re.IGNORECASE) for pattern in expectations)
        if name == 'ordinary-review':
            gates['findings_present'] = bool(result.get('findings'))
        language = CASE_LANGUAGES.get(name)
        if language:
            summary = result.get('summary', '')
            has_han = bool(re.search(r'[\u3400-\u9fff]', summary))
            gates['summary_language_signal'] = (has_han if language == 'zh' else
                                                bool(re.search(r'[A-Za-z]', summary)) and not has_han)
        if writable:
            check = h.execute([sys.executable, '-B', '-m', 'unittest', '-v'], workspace, 30,
                              case_output/'checks.stdout.log', case_output/'checks.stderr.log')
            gates['host_tests_pass'] = check == 0
            gates['implementation_changed'] = changed == ['average.py']
        receipt = {'case': name, 'gates': gates, 'passed': all(gates.values()),
                   'changed_files': changed, 'result': result, 'elapsed_seconds': round(elapsed, 3),
                   'expected_language': language,
                   'limits': 'Routing is client-reported. Filesystem scope and repair tests are host-checked. Text signals require semantic review.'}
        (case_output/'receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2))
        return receipt


def compare(names, client, output, timeout, baseline, candidate):
    checker_spec = importlib.util.spec_from_file_location('eval_plugin_check', ROOT/'scripts/check_plugin.py')
    checker = importlib.util.module_from_spec(checker_spec)
    checker_spec.loader.exec_module(checker)
    versions = {label: checker.check(path)['sha256']
                for label, path in (('baseline', baseline), ('candidate', candidate))}
    if versions['baseline'] == versions['candidate']:
        raise ValueError('Baseline and candidate plugin contents are identical')
    (output/'baseline').mkdir()
    (output/'candidate').mkdir()
    comparisons = []
    for name in names:
        old = evaluate(name, client, output/'baseline', timeout, baseline)
        new = evaluate(name, client, output/'candidate', timeout, candidate)
        comparisons.append({
            'case': name,
            'baseline': old,
            'candidate': new,
            'improved_gates': [key for key, passed in new['gates'].items()
                               if passed and not old['gates'][key]],
            'regressed_gates': [key for key, passed in old['gates'].items()
                                if passed and not new['gates'][key]],
        })
    for label, path in (('baseline', baseline), ('candidate', candidate)):
        if checker.check(path)['sha256'] != versions[label]:
            raise ValueError(f'{label} plugin changed during comparison')
    ready = all(item['baseline']['gates']['client_success'] and item['candidate']['passed']
                and not item['regressed_gates'] for item in comparisons)
    return {'status': 'passed' if ready else 'failed', 'plugin_sha256': versions,
            'comparisons': comparisons,
            'limits': 'Paired probes use the same executable and inherited settings. Passing gates require semantic review and do not by themselves prove improvement.'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--client', default='codex')
    selection = p.add_mutually_exclusive_group()
    selection.add_argument('--case', choices=(*CASES, *maintenance.CASES))
    selection.add_argument('--maintenance-suite', choices=maintenance.SUITES)
    p.add_argument('--baseline-plugin', type=Path, help='Path to a complete baseline plugins/openas directory')
    p.add_argument('--candidate-plugin', type=Path, default=PLUGIN)
    p.add_argument('--output', required=True, type=Path)
    p.add_argument('--timeout', type=int, default=180)
    args = p.parse_args()
    client = shutil.which(args.client)
    if not client or args.timeout <= 0:
        p.error('An installed client and a positive timeout are required')
    names = (args.case,) if args.case else maintenance.SUITES[args.maintenance_suite] if args.maintenance_suite else CASES
    candidate = args.candidate_plugin.resolve()
    baseline = args.baseline_plugin.resolve() if args.baseline_plugin else None
    output = args.output.resolve()
    if any(path == output or path in output.parents for path in (candidate, baseline) if path):
        p.error('Output must be outside the plugin directories')
    output.mkdir(parents=True, exist_ok=False)
    try:
        if baseline:
            report = compare(names, client, output, args.timeout, baseline, candidate)
        else:
            receipts = [evaluate(name, client, output, args.timeout, candidate) for name in names]
            report = {'status': 'passed' if all(r['passed'] for r in receipts) else 'failed', 'cases': receipts}
    except (h.HarnessError, OSError, ValueError) as exc:
        (output/'error.json').write_text(json.dumps({'status': 'failed', 'error': str(exc)}))
        print(str(exc), file=sys.stderr)
        return 1
    (output/'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(json.dumps({'status': report['status'], 'report': str(output/'report.json')}))
    return 0 if report['status'] == 'passed' else 1


if __name__ == '__main__':
    sys.exit(main())
