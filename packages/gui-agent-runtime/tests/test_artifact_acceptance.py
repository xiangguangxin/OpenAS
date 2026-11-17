import json
from pathlib import Path
import tempfile
import unittest

from openas_gui_agent.agent import run
from openas_gui_agent.experience import ExperienceStore
from openas_gui_agent.recovery import reconcile
from openas_gui_agent.state import create, load
from openas_gui_agent.verification import FileVerifier

CRITERION = "New MC/DC report"
DATA = {"suite": "fixture", "build": "instrumented", "tests": "passed", "metric": "MC/DC"}
RULES = {CRITERION: {"path": "coverage.json", "fresh": True, "json_fields": {
    "/build": "instrumented", "/tests": "passed", "/metric": "MC/DC"}}}


class CoverageAcceptanceTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.root = Path(folder.name)
        self.checkpoint = self.root / "state.json"
        self.report = self.root / "coverage.json"
        create(self.checkpoint, "Build and run SIL tests", [CRITERION])
        self.verifier = FileVerifier(RULES, self.root)

    def test_stale_report_cannot_pass(self):
        self.report.write_text(json.dumps(DATA), encoding="utf-8")
        state = run(self.checkpoint, self, self, verifier=self.verifier)
        self.assertEqual(state["status"], "blocked")
        self.assertEqual(state["artifact_verification"]["checks"][CRITERION]["status"], "stale_artifact")

    def test_interrupted_action_preserves_baseline_and_does_not_repeat(self):
        self.report.write_text(json.dumps({**DATA, "tests": "failed"}), encoding="utf-8")

        class CrashAfterWriting:
            def observe(inner):
                return {}

            def act(inner, action):
                self.report.write_text(json.dumps(DATA), encoding="utf-8")
                raise KeyboardInterrupt

        class FirstAction:
            def decide(inner, state, observation):
                return {"type": "act", "action": {"name": "run_tests", "impact": "low"}}

        with self.assertRaises(KeyboardInterrupt):
            run(self.checkpoint, CrashAfterWriting(), FirstAction(), verifier=self.verifier)
        baseline = load(self.checkpoint)["artifact_baseline"]
        self.assertEqual(run(self.checkpoint, self, self, verifier=self.verifier)["status"], "blocked")
        reconcile(self.checkpoint, outcome="executed", note="Checked the report after interruption")
        with self.assertRaisesRegex(ValueError, "original artifact verifier"):
            run(self.checkpoint, self, self)
        state = run(self.checkpoint, self, self, verifier=self.verifier)
        self.assertEqual(state["status"], "completed")
        self.assertEqual(state["artifact_baseline"], baseline)
        self.assertEqual(state["steps"], 1)
        item = ExperienceStore(self.root / "memory.json").add_verified(
            self.checkpoint, verifier=self.verifier, environment="test", note="Verified after recovery")
        self.assertEqual(item["id"], state["id"])

    def test_structural_json_and_run_id_checks(self):
        state = load(self.checkpoint)
        verifier = FileVerifier({CRITERION: {"path": "coverage.json", "run_id_pointer": "/run",
                                             "json_fields": {"/cases/0/a~1b": True}}}, self.root)
        for value, run_id, status in (
                (1, state["id"], "json_field_mismatch"),
                (True, "earlier-run", "run_id_mismatch"),
                (True, state["id"], "passed")):
            with self.subTest(status=status):
                self.report.write_text(json.dumps({"cases": [{"a/b": value}], "run": run_id}), encoding="utf-8")
                self.assertEqual(verifier.evaluate(state)["checks"][CRITERION]["status"], status)
        self.report.write_text("{", encoding="utf-8")
        self.assertEqual(verifier.evaluate(state)["checks"][CRITERION]["status"],
                         "unreadable_or_invalid_content")

    def observe(self):
        return {}

    def decide(self, state, observation):
        return {"type": "complete"}

    def act(self, action):
        self.fail("The verified artifact should require no additional action")
