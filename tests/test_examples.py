"""Exercise example contracts in temporary workspaces; never repair shipped fixtures."""
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT/'plugins/openas/workflows/examples'
SPEC = importlib.util.spec_from_file_location('example_harness', EXAMPLES.parent/'codex-team.py')
h = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(h)


class ExampleTests(unittest.TestCase):
    def exercise(self, name, repair, source):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); workspace = root/'workspace'
            shutil.copytree(EXAMPLES/f'{name}-fixture', workspace)
            task = json.loads((EXAMPLES/f'{name}-task.json').read_text())
            if task['checks'][0][0] == 'python3':
                task['checks'][0][0] = sys.executable
            r = h.Runner(task, workspace, root/'run', 'unused')
            self.assertNotEqual(r.checks('baseline')[0]['exit_code'], 0)
            original = {p.name: p.read_bytes() for p in workspace.iterdir() if p.name != source}
            (workspace/source).write_text(repair)
            result = r.checks('repaired')
            self.assertEqual(result[0]['exit_code'], 0, result[0]['stderr'])
            r.check_scope()
            for name, data in original.items():
                self.assertEqual((workspace/name).read_bytes(), data)

    def test_cli_contract(self):
        self.exercise('cli', '''import json, math, sys
def main():
    try:
        values = json.load(sys.stdin)
        if not isinstance(values, list) or any(type(x) not in (int, float) or not math.isfinite(x) for x in values):
            raise ValueError('Expected finite numbers')
        total = sum(values)
        if not math.isfinite(total):
            raise ValueError('Total is not finite')
    except (ValueError, TypeError, OverflowError):
        print('Invalid numeric input', file=sys.stderr)
        return 2
    print(json.dumps({'count': len(values), 'total': total}))
    return 0
if __name__ == '__main__':
    sys.exit(main())
''', 'report.py')

    @unittest.skipUnless(shutil.which('node'), 'Node is required for the frontend state example')
    def test_frontend_state_contract(self):
        self.exercise('selection', '''export function toggleSelection(ids, id) {
  return ids.includes(id) ? ids.filter(value => value !== id) : [...ids, id];
}
''', 'selection.mjs')
