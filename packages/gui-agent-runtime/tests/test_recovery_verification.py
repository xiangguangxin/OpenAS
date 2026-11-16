"""Phase 3/4: deterministic recovery, locking, independent verification and fake desktop E2E."""
import json
import tempfile
import unittest
from pathlib import Path
from openas_gui_agent.agent import run
from openas_gui_agent.state import create, load, _save
from openas_gui_agent.locking import checkpoint_lock
from openas_gui_agent.recovery import reconcile
from openas_gui_agent.verification import FileVerifier

class Desktop:
    def __init__(self, root):
        self.root = root
        self.actions = 0
    def observe(self):
        return {"summary": "ready"}
    def act(self, action):
        self.actions += 1
        out = self.root / "report.txt"
        out.write_text("COVERAGE: PASS", encoding="utf-8")
        return {"ok": True, "summary": "report written"}

class Planner:
    def decide(self, state, observation):
        if state["steps"]:
            return {"type": "complete", "evidence": {"Report": "claimed"}}
        return {"type": "act", "action": {"name": "click", "impact": "low"}}

class Tests(unittest.TestCase):
    def test_fake_desktop_full_goal(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); p = root / "state.json"
            create(p, "Create report", ["Report"])
            verifier = FileVerifier({"Report": {"path": "report.txt", "contains": "PASS", "min_bytes": 4}}, root)
            desktop = Desktop(root)
            result = run(p, desktop, Planner(), verifier=verifier)
            self.assertEqual(result["status"], "completed")
            self.assertEqual(desktop.actions, 1)

    def test_model_claim_cannot_pass_independent_verifier(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); p = root / "state.json"
            create(p, "Create report", ["Report"])
            verifier = FileVerifier({"Report": {"path": "missing.txt"}}, root)
            result = run(p, Desktop(root), Planner(), verifier=verifier)
            self.assertNotEqual(result["status"], "completed")

    def test_lock_refuses_concurrent_execution(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / "state.json"
            create(p, "goal", ["Report"])
            with checkpoint_lock(p):
                with self.assertRaises(RuntimeError):
                    run(p, Desktop(Path(temp)), Planner())

    def test_crash_requires_human_reconcile(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / "state.json"
            state = create(p, "goal", ["Report"])
            state["pending_action"] = {"name": "click", "since": 1}
            _save(p, state)
            desktop = Desktop(Path(temp))
            self.assertEqual(run(p, desktop, Planner())["status"], "blocked")
            self.assertEqual(desktop.actions, 0)
            with self.assertRaises(ValueError):
                reconcile(p, outcome="executed", note="")
            result = reconcile(p, outcome="executed", note="Verified click already happened")
            self.assertEqual(result["status"], "paused")
            self.assertEqual(result["steps"], 1)
            self.assertIsNone(result["pending_action"])

    def test_v1_checkpoint_migration(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / "state.json"
            state = create(p, "goal", ["Report"])
            state["version"] = 1
            _save(p, state)
            self.assertEqual(load(p)["version"], 2)
            self.assertEqual(json.loads(p.read_text())["version"], 1)

    def test_path_escape_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            verifier = FileVerifier({"Report": {"path": "../secret.txt"}}, root)
            self.assertFalse(verifier.verify(["Report"], {}, {}))

if __name__ == "__main__":
    unittest.main()
