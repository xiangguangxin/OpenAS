import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/minimize_repro.py"


class MinimizeReproTests(unittest.TestCase):
    def test_reduce_json_fixture_without_accepting_a_different_failure(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            check = folder / "check.py"
            check.write_text(
                "import json,sys\n"
                "items=json.load(open(sys.argv[1]))\n"
                "if 'A' in items and 'B' in items:\n"
                "    print('TARGET_FAILURE')\n"
                "    sys.exit(1)\n"
                "if 'decoy' in items: sys.exit(1)\n",
                encoding="utf-8",
            )
            original = folder / "original.json"
            output = folder / "reduced.json"
            original.write_text(json.dumps(["unused", "A", "decoy", "B", "unused"]), encoding="utf-8")
            command = [sys.executable, str(SCRIPT), str(original), "--output", str(output),
                       "--failure-marker", "TARGET_FAILURE", "--", sys.executable, str(check), "{input}"]
            result = subprocess.run(command, capture_output=True, text=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8")), ["A", "B"])
            self.assertEqual(json.loads(result.stdout)["reduced_items"], 2)
            self.assertEqual(len(json.loads(original.read_text(encoding="utf-8"))), 5)
