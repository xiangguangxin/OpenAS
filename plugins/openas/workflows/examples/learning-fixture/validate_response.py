"""Trusted sample check: inspect actual trial response, not the model's pass claim."""
import json
import os
from pathlib import Path
import re
import sys

result = json.loads(Path(os.environ['OPENAS_TRIAL_RESULT']).read_text())
expected = sys.argv[1] == 'yes'
assert result['applicable'] is expected, 'Wrong skill applicability'
if expected:
    assert re.search(r'\bzero\b|\b0\b|零', result['summary'], re.I), 'Missing expected empty-input result'
    assert result['evidence'], 'Missing evidence for diagnosis'
    assert 'zero' in Path('README.md').read_text(), 'Fixture contract changed'
