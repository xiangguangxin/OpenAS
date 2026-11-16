"""Package tests: run with python -m unittest discover -s packages/gui-agent-runtime/tests."""
import tempfile
import unittest
from pathlib import Path
from openas_gui_agent.state import create, load, _save
from openas_gui_agent.agent import run
from openas_gui_agent.policy import needs_approval

class Desktop:
    def __init__(self): self.calls = []
    def observe(self): return {"summary": "screen observed"}
    def act(self, action): self.calls.append(action["name"]); return {"ok": True}

class Planner:
    def decide(self, state, observation):
        if state["steps"]: return {"type": "complete", "evidence": {"done": "observed"}}
        return {"type": "act", "action": {"name": "click", "impact": "low"}}

class Reject:
    def verify(self, criteria, evidence, observation): return False

class Tests(unittest.TestCase):
    def test_legacy_checkpoint(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "state.json"; create(p, "goal", ["done"])
            desk = Desktop()
            self.assertEqual(run(p, desk, Planner())["status"], "completed")
            self.assertEqual(desk.calls, ["click"])
            self.assertEqual(load(p)["version"], 1)
    def test_pluggable_verifier(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "state.json"; create(p, "goal", ["done"])
            self.assertNotEqual(run(p, Desktop(), Planner(), verifier=Reject())["status"], "completed")
    def test_crash_blocks_replay(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "state.json"; state = create(p, "goal", ["done"])
            state["pending_action"] = {"name": "click", "since": 1}; _save(p, state)
            desk = Desktop(); self.assertEqual(run(p, desk, Planner())["status"], "blocked")
            self.assertEqual(desk.calls, [])
    def test_risky_names(self):
        self.assertTrue(needs_approval({"name": "file_delete", "impact": "low"}))
        self.assertTrue(needs_approval({"name": "click"}))
        self.assertFalse(needs_approval({"name": "click", "impact": "low"}))

if __name__ == "__main__": unittest.main()
