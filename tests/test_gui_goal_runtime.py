import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "plugins/openas/integrations/computer-use/goal_runtime.py"
spec = importlib.util.spec_from_file_location("goal_runtime", MODULE)
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)


class FakeDesktop:
    def __init__(self):
        self.actions = []
    def observe(self):
        return {"summary": f"{len(self.actions)} actions completed"}
    def act(self, action):
        self.actions.append(action["name"])
        return {"ok": True, "summary": "observed"}


class FakePlanner:
    def decide(self, state, observation):
        if state["steps"]:
            return {"type": "complete", "evidence": {"task finished": "UI state verified"}}
        return {"type": "act", "action": {"name": "click", "impact": "low"}}


class GoalRuntimeTests(unittest.TestCase):
    def test_create_run_resume_completed(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "state.json"
            runtime.create(path, "Test", ["task finished"])
            desktop = FakeDesktop()
            result = runtime.run(path, desktop, FakePlanner())
            self.assertEqual(result["status"], "completed")
            self.assertEqual(desktop.actions, ["click"])
            self.assertEqual(runtime.run(path, desktop, FakePlanner())["steps"], 1)

    def test_sensitive_action_pauses_without_execution(self):
        class Sensitive:
            def decide(self, state, observation):
                return {"type": "act", "action": {"name": "delete", "impact": "low"}}
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "state.json"
            runtime.create(path, "Test", ["task finished"])
            desktop = FakeDesktop()
            result = runtime.run(path, desktop, Sensitive())
            self.assertEqual(result["status"], "paused")
            self.assertEqual(desktop.actions, [])
            self.assertTrue(result["pending_approval"])

    def test_crash_recovery_does_not_replay(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "state.json"
            state = runtime.create(path, "Test", ["task finished"])
            state["pending_action"] = {"name": "click", "since": 1}
            runtime._save(path, state)
            desktop = FakeDesktop()
            result = runtime.run(path, desktop, FakePlanner())
            self.assertEqual(result["status"], "blocked")
            self.assertEqual(desktop.actions, [])

    def test_missing_evidence_never_completes(self):
        class Premature:
            def decide(self, state, observation):
                return {"type": "complete", "evidence": {}}
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "state.json"
            runtime.create(path, "Test", ["task finished"])
            result = runtime.run(path, FakeDesktop(), Premature())
            self.assertNotEqual(result["status"], "completed")


if __name__ == "__main__":
    unittest.main()
