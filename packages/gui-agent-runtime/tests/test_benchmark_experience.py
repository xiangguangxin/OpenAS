import tempfile
import unittest
from pathlib import Path
from openas_gui_agent.benchmark import benchmark
from openas_gui_agent.experience import ExperienceStore
from openas_gui_agent.state import create, persist
from openas_gui_agent.verification import FileVerifier

class Tests(unittest.TestCase):
    def test_benchmark_success_and_failure(self):
        suite = [
            {"name": "ok", "outputs": {"out.txt": "PASS"}, "rules": {"done": {"path": "out.txt", "contains": "PASS"}}},
            {"name": "missing", "outputs": {}, "rules": {"done": {"path": "out.txt", "contains": "PASS"}}},
        ]
        result = benchmark(suite, repeat=2)
        self.assertEqual(result["kind"], "offline-synthetic")
        self.assertEqual(result["runs"], 4)
        self.assertEqual(result["success_rate"], 0.5)
        self.assertGreater(result["avg_model_calls"], 0)

    def test_only_verified_experiences(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            checkpoint = root / "goal.json"
            state = create(checkpoint, "Generate coverage report", ["report"])
            state["status"] = "completed"
            persist(checkpoint, state)
            verifier = FileVerifier({"report": {"path": "report.txt", "contains": "PASS"}}, root)
            store = ExperienceStore(root / "experiences.json")
            with self.assertRaises(ValueError):
                store.add_verified(checkpoint, verifier=verifier, environment="win11", note="confirmed")
            (root / "report.txt").write_text("PASS")
            item = store.add_verified(checkpoint, verifier=verifier, environment="win11", note="confirmed")
            self.assertEqual(item["source"], "independently-verified")
            self.assertEqual(len(store.search("coverage report", environment="win11")), 1)
            self.assertEqual(store.search("coverage report", environment="macos"), [])
            with self.assertRaises(ValueError):
                store.add_verified(checkpoint, verifier=verifier, environment="win11", note="duplicate")

if __name__ == "__main__":
    unittest.main()
