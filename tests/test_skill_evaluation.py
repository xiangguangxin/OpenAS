import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location('skill_eval', Path(__file__).resolve().parents[1]/'scripts/evaluate_skills.py')
evaluation = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(evaluation)


class SkillEvaluationTests(unittest.TestCase):
    def test_language_signal_checks_implicit_and_explicit_preferences(self):
        for name, summary, expected in (
            ('english-analysis', 'The module exposes average and two tests.', True),
            ('english-analysis', '模块提供 average 函数。', False),
            ('chinese-analysis', '模块提供 average 函数。', True),
            ('chinese-analysis', 'The module exposes average.', False),
            ('explicit-english', 'The tests call the public average function.', True),
            ('explicit-english', '测试调用 average。', False),
            ('explicit-chinese', '测试调用公开函数 average。', True),
            ('explicit-chinese', '', False),
        ):
            with self.subTest(case=name, summary=summary):
                def execute(argv, cwd, timeout, stdout, stderr, stdin=None):
                    Path(argv[argv.index('-o') + 1]).write_text(json.dumps({
                        'selected_skill': 'codebase-analysis', 'summary': summary,
                        'findings': [], 'questions': [], 'evidence': ['average.py:1'],
                    }))
                    return 0
                with tempfile.TemporaryDirectory() as tmp, patch.object(evaluation.h, 'execute', side_effect=execute):
                    receipt = evaluation.evaluate(name, 'fake', Path(tmp), 10)
                self.assertEqual(receipt['gates']['summary_language_signal'], expected)
                self.assertEqual(receipt['passed'], expected)

    def test_review_that_interviews_user_does_not_pass(self):
        def execute(argv, cwd, timeout, stdout, stderr, stdin=None):
            result = {'selected_skill': 'requesting-code-review', 'summary': 'review',
                      'findings': ['empty input fails'], 'questions': ['Please confirm before I review'],
                      'evidence': ['fixture']}
            Path(argv[argv.index('-o') + 1]).write_text(json.dumps(result))
            return 0
        with tempfile.TemporaryDirectory() as tmp, patch.object(evaluation.h, 'execute', side_effect=execute):
            receipt = evaluation.evaluate('ordinary-review', 'fake', Path(tmp), 10)
        self.assertFalse(receipt['passed'])
        self.assertFalse(receipt['gates']['question_policy'])

    def test_success_claim_cannot_hide_out_of_scope_change(self):
        def execute(argv, cwd, timeout, stdout, stderr, stdin=None):
            if '-o' in argv:
                (cwd/'average.py').write_text('def average(items): return 0 if not items else sum(items)/len(items)\n')
                (cwd/'unrequested.txt').write_text('scope violation')
                Path(argv[argv.index('-o') + 1]).write_text(json.dumps({
                    'selected_skill': 'bug-fix', 'summary': 'fixed', 'findings': [],
                    'questions': [], 'evidence': ['claimed pass']}))
            return 0
        with tempfile.TemporaryDirectory() as tmp, patch.object(evaluation.h, 'execute', side_effect=execute):
            receipt = evaluation.evaluate('repair', 'fake', Path(tmp), 10)
        self.assertFalse(receipt['passed'])
        self.assertFalse(receipt['gates']['scope_preserved'])
