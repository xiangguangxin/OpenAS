"""Architecture boundaries, injected failures and metamorphic relations."""
import ast
from pathlib import Path
import tempfile
import unittest

from openas_gui_agent.agent import run
from openas_gui_agent.state import create
from openas_gui_agent.tool_trace import compare_checkpoints, evaluate

SOURCE = Path(__file__).resolve().parents[1] / "src/openas_gui_agent"


class EngineeringMethodsTests(unittest.TestCase):
    def test_runtime_core_does_not_depend_on_provider_or_gui_adapters(self):
        forbidden = {"adapters", "executor", "session", "model_connection", "litellm", "playwright"}
        core = ("agent", "state", "recovery", "verification", "tool_trace")
        for module in core:
            path = SOURCE / f"{module}.py"
            for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"), filename=str(path))):
                if isinstance(node, ast.Import):
                    imports = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom):
                    imports = [node.module] if node.module else [alias.name for alias in node.names]
                else:
                    continue
                for name in imports:
                    self.assertFalse(forbidden.intersection(name.split(".")), f"{path.name} imports {name}")

    def test_timeout_before_or_after_dispatch_has_distinct_recovery_behavior(self):
        class Backend:
            calls = 0

            def observe(self):
                return {"tools": [{"name": "download_report"}]}

            def act(self, action):
                self.calls += 1
                raise TimeoutError("adapter response lost")

        class Planner:
            def __init__(self, before_dispatch):
                self.before_dispatch = before_dispatch

            def decide(self, state, observation):
                if self.before_dispatch:
                    raise TimeoutError("model response lost")
                return {"type": "act", "action": {"name": "download_report", "impact": "low"}}

        for before in (True, False):
            with self.subTest(before_dispatch=before), tempfile.TemporaryDirectory() as temp:
                path = Path(temp) / "state.json"
                backend = Backend()
                planner = Planner(before)
                create(path, "Create report", ["report"])
                state = run(path, backend, planner, trace_tools=True)
                self.assertEqual(state["status"], "blocked")
                self.assertEqual(backend.calls, int(not before))
                self.assertEqual(state["pending_action"] is None, before)
                again = run(path, backend, planner)
                self.assertEqual(again["status"], "blocked")
                self.assertEqual(backend.calls, int(not before))

    def test_inserting_read_only_observation_preserves_ordered_trajectory_verdict(self):
        rule = {"match": "in_order", "tools": ["prepare", "emit"], "max_counts": {"emit": 1}}

        def trace(*tools):
            return {"started_after_steps": 0, "dropped": 0,
                    "events": [{"tool": tool, "outcome": "ok"} for tool in tools]}

        original = evaluate(rule, trace("prepare", "emit"))
        self.assertEqual(evaluate(rule, trace("prepare", "observe", "emit")), original)
        self.assertFalse(evaluate(rule, trace("emit", "observe", "prepare"))["passed"])
        self.assertFalse(evaluate(rule, trace("prepare", "observe", "emit", "emit"))["passed"])

    def test_trace_comparison_reports_first_semantic_difference(self):
        def checkpoint(events, artifact):
            return {"status": "completed", "tool_trace": {"started_after_steps": 0, "dropped": 0, "events": events},
                    "artifact_verification": {"checks": {"report": {"status": artifact}}}}

        action = {"tool": "download", "outcome": "ok", "duration_ms": 1}
        baseline = checkpoint([action], "passed")
        slowed = {**action, "duration_ms": 12}
        self.assertEqual(compare_checkpoints(baseline, checkpoint([slowed], "passed"))["status"], "match")
        self.assertEqual(compare_checkpoints(baseline, checkpoint([slowed], "stale_artifact"))["stage"], "artifact")
        duplicate = compare_checkpoints(baseline, checkpoint([slowed, slowed], "passed"))
        self.assertEqual((duplicate["stage"], duplicate["action"]), ("tool", 2))
        uncertain = checkpoint([{**action, "outcome": "unknown"}], "stale_artifact")
        self.assertEqual(compare_checkpoints(baseline, uncertain),
                         {"status": "inconclusive", "incomplete": ["candidate"]})
