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
