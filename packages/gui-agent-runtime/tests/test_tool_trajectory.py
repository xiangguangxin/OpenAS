"""Regression checks for host-observed tool trajectory gates."""
import json
from pathlib import Path
import tempfile
import unittest

from openas_gui_agent import tool_trace
from openas_gui_agent.agent import run
from openas_gui_agent.benchmark import benchmark
from openas_gui_agent.benchmark_provenance import manifest
from openas_gui_agent.state import create, load

EXAMPLES = Path(__file__).resolve().parents[1] / "examples"


class ToolTrajectoryTests(unittest.TestCase):
    def test_verified_file_does_not_hide_extra_dispatch(self):
        case = {
            "name": "verified-but-duplicate", "outputs": {"report.json": "{}"}, "actions": 2,
            "rules": {"report": {"path": "report.json"}},
            "expected_trajectory": {"tools": ["synthetic_click"], "max_counts": {"synthetic_click": 1}},
        }
        report = benchmark([case])
        record = report["records"][0]
        self.assertTrue(record["completed_and_verified"])
        self.assertFalse(record["passed"])
        self.assertEqual(report["trajectory_pass_rate"], 0)
        self.assertEqual(record["trajectory"]["reasons"], ["count_exceeded:synthetic_click"])

    def test_restored_checkpoint_keeps_reconciled_action_once(self):
        cases = json.loads((EXAMPLES / "benchmark-suite.json").read_text())["scenarios"]
        recovery = next(case for case in cases if case.get("interrupt_after_write"))
        record = benchmark([recovery])["records"][0]
        self.assertTrue(record["passed"])
        self.assertEqual(record["trajectory"]["trace"]["events"],
                         [{"tool": "synthetic_click", "outcome": "reconciled_executed"}])

    def test_exact_order_multiplicity_and_forbidden_attempt(self):
        trace = {"started_after_steps": 0, "dropped": 0, "events": [
            {"tool": "read", "outcome": "ok"}, {"tool": "write", "outcome": "ok"},
            {"tool": "read", "outcome": "ok"}, {"tool": "publish", "outcome": "error"},
        ]}
        for rules, reasons in (
            ({"match": "exact", "tools": ["read", "write", "read"]}, ["sequence_mismatch"]),
            ({"match": "in_order", "tools": ["write", "read"]}, []),
            ({"match": "any_order", "tools": ["read", "read", "write"]}, []),
            ({"match": "any_order", "tools": ["read", "read", "read"]}, ["sequence_mismatch"]),
            ({"forbidden": ["publish"]}, ["forbidden_tool:publish"]),
        ):
            with self.subTest(rules=rules):
                tool_trace.validate_expectation(rules)
                result = tool_trace.evaluate(rules, trace)
                self.assertEqual(result, {"passed": not reasons, "reasons": reasons})

    def test_late_and_truncated_traces_are_incomplete(self):
        state = {"steps": 2}
        tool_trace.enable(state)
        rules = {"forbidden": ["publish"]}
        self.assertFalse(tool_trace.evaluate(rules, state["tool_trace"])["passed"])
        state = {"steps": 0}
        tool_trace.enable(state)
        for _ in range(tool_trace.TRACE_LIMIT + 1):
            event = tool_trace.begin(state, "read", [{"name": "read"}])
            event["outcome"] = "ok"
        self.assertEqual(len(state["tool_trace"]["events"]), tool_trace.TRACE_LIMIT)
        self.assertEqual(state["tool_trace"]["dropped"], 1)
        self.assertFalse(tool_trace.evaluate(rules, state["tool_trace"])["passed"])

    def test_trace_contains_only_known_names_and_host_outcomes(self):
        class Desktop:
            def observe(self):
                return {"tools": [{"name": "visible_tool"}]}

            def act(self, action):
                return {"ok": True, "content": ["private-content"]}

        class Planner:
            def decide(self, state, observation):
                if state["steps"] >= 2:
                    return {"type": "complete", "evidence": {"result": "observed"}}
                name = "visible_tool" if state["steps"] == 0 else "private-unknown-action"
                return {"type": "act", "action": {"name": name, "impact": "low",
                                                  "arguments": {"token": "private-argument"}}}

        with tempfile.TemporaryDirectory() as folder:
            checkpoint = Path(folder) / "state.json"
            create(checkpoint, "Test a tool", ["result"])
            run(checkpoint, Desktop(), Planner(), trace_tools=True)
            trace = load(checkpoint)["tool_trace"]

        self.assertEqual([event["tool"] for event in trace["events"]], ["visible_tool", None])
        self.assertGreaterEqual(trace["events"][0]["duration_ms"], 0)
        self.assertNotIn("private", json.dumps(trace))
        self.assertEqual(tool_trace.evaluate({"tools": ["visible_tool"]}, trace)["reasons"], ["incomplete_trace"])

    def test_run_manifest_pins_suite_inputs_and_runtime(self):
        base = manifest([{"name": "a", "rules": {"first": {}, "second": {}}}], 1)
        changed = manifest([{"name": "a", "rules": {"second": {}, "first": {}}}], 1)
        self.assertNotEqual(base["suite_sha256"], changed["suite_sha256"])
        self.assertEqual(base["runtime_source_sha256"], changed["runtime_source_sha256"])
        self.assertEqual(len(base["runtime_source_sha256"]), 64)
        self.assertEqual(base["repeat"], 1)
