"""Trusted synthetic observer: execute the candidate; never read its success claims."""
import importlib.util
import json
from pathlib import Path
import sys

path = Path(sys.argv[1])/'app.py'
spec = importlib.util.spec_from_file_location('candidate_total', path)
candidate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(candidate)
results = {}
for name, value in [('empty', []), ('numbers', [1, 2.5, -1]), ('boolean', [True]), ('text', ['1'])]:
    try:
        result = candidate.total(value)
    except ValueError:
        result = {'error': 'ValueError'}
    results[name] = {'value': result}
print(json.dumps({'cases': results}, allow_nan=False))
