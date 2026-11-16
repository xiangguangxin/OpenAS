"""Experience lifecycle and planner hint integration regression tests."""
import json
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch
from openas_gui_agent.experience import ExperienceStore, DAY
from openas_gui_agent.planner import ModelPlanner
from openas_gui_agent.state import create, persist
from openas_gui_agent.verification import FileVerifier

class Response:
    def __enter__(self): return self
    def __exit__(self, *args): pass
    def read(self):
        return json.dumps({"choices": [{"message": {"content": '{"type":"pause","reason":"done"}'}}],
                           "usage": {"prompt_tokens": 10, "completion_tokens": 5}}).encode()

class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        cp = self.root / "state.json"
        state = create(cp, "Generate coverage report", ["report"])
        state["status"] = "completed"
        persist(cp, state)
        (self.root / "report.txt").write_text("PASS")
        verifier = FileVerifier({"report": {"path": "report.txt", "contains": "PASS"}}, self.root)
        self.store = ExperienceStore(self.root / "store.json")
        self.item = self.store.add_verified(cp, verifier=verifier, environment="win11", note="Worked after build")

    def test_decay_and_expiry(self):
        now = self.item["recorded_at"]
        fresh = self.store.search("coverage report", environment="win11", now=now)
        older = self.store.search("coverage report", environment="win11", now=now + 30*DAY)
        self.assertGreater(fresh[0]["effective_score"], older[0]["effective_score"])
        self.assertEqual(self.store.search("coverage report", environment="win11", now=now + 91*DAY), [])
        self.assertEqual(self.store.expire(now=now + 91*DAY), 1)
        self.assertEqual(self.store.expire(now=now + 91*DAY), 0)

    def test_verified_failure_invalidates(self):
        key = self.item["id"]
        self.store.feedback(key, outcome="failure", note="artifact verifier failed")
        self.assertTrue(self.store.search("coverage report", environment="win11"))
        self.store.feedback(key, outcome="failure", note="second independent failure")
        self.assertFalse(self.store.search("coverage report", environment="win11"))
        with self.assertRaises(ValueError):
            self.store.feedback(key, outcome="success", note="should not reactivate")

    def test_environment_and_manual_invalidation(self):
        self.assertEqual(self.store.search("coverage report", environment="macos"), [])
        self.store.invalidate(self.item["id"], reason="application upgraded")
        self.assertEqual(self.store.search("coverage report", environment="win11"), [])

    def test_planner_receives_bounded_hints(self):
        captured = []
        def fake_urlopen(request, timeout):
            captured.append(json.loads(request.data))
            return Response()
        planner = ModelPlanner("fake", "key", "https://invalid",
                               experience_store=self.store, experience_environment="win11")
        with patch("openas_gui_agent.planner.urllib.request.urlopen", side_effect=fake_urlopen):
            planner.decide({"goal": "Generate coverage report", "criteria": ["report"],
                            "steps": 0, "max_steps": 5}, {"summary": "screen"})
        serialized = json.dumps(captured[0])
        self.assertIn("untrusted_prior_experience_hints", serialized)
        self.assertIn("Worked after build", serialized)
        self.assertNotIn("report.txt", serialized)
        self.store.invalidate(self.item["id"], reason="stale")
        with patch("openas_gui_agent.planner.urllib.request.urlopen", side_effect=fake_urlopen):
            planner.decide({"goal": "Generate coverage report", "criteria": ["report"],
                            "steps": 0, "max_steps": 5}, {"summary": "screen"})
        self.assertNotIn("untrusted_prior_experience_hints", json.dumps(captured[-1]))

if __name__ == "__main__":
    unittest.main()
