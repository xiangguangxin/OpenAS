"""Evaluate synthetic, real Nova, or real Playwright goals with independent checks."""
from __future__ import annotations

import argparse
import json
import os
import statistics
import tempfile
import time
from pathlib import Path

from .agent import run
from .benchmark_provenance import manifest, package_version
from . import tool_trace
from .experience import ExperienceStore
from .planner import ModelPlanner
from .recovery import reconcile
from .session import browser_scope, open_session
from .state import ALLOWED, create
from .verification import FileVerifier


def _write_fixture(root, files):
    for filename, content in files.items():
        target = (root / filename).resolve()
        if not target.is_relative_to(root) or target == root:
            raise ValueError("Unsafe fixture output path")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")


class ScriptedInterruption(KeyboardInterrupt):
    pass


class ScriptedDesktop:
    def __init__(self, root, scenario):
        self.root, self.scenario = root, scenario
        self.calls = 0

    def observe(self):
        return {"summary": "synthetic desktop", "step": self.calls,
                "tools": [{"name": "synthetic_click"}]}

    def act(self, action):
        self.calls += 1
        if self.scenario.get("fail_action"):
            return {"ok": False, "summary": "injected failure"}
        _write_fixture(self.root, self.scenario.get("outputs", {}))
        if self.calls == 1 and self.scenario.get("interrupt_after_write"):
            raise ScriptedInterruption()
        return {"ok": True, "summary": "synthetic action"}


class ScriptedPlanner:
    def __init__(self, scenario):
        self.scenario = scenario
        self.usage = {"calls": 0, "input_tokens": 0, "output_tokens": 0}

    def decide(self, state, observation):
        self.usage["calls"] += 1
        self.usage["input_tokens"] += self.scenario.get("input_tokens_per_call", 100)
        self.usage["output_tokens"] += self.scenario.get("output_tokens_per_call", 20)
        if state["steps"] >= self.scenario.get("actions", 1):
            return {"type": "complete", "evidence": {c: "claimed" for c in state["criteria"]}}
        return {"type": "act", "action": {"name": "synthetic_click", "impact": "low"}}


def _record(case, index, variant, state, verifier, actions, elapsed):
    expected = case.get("expected_status", "completed")
    actual = verifier.evaluate(state)
    recorded = state.get("artifact_verification", {}).get("checks", {})
    confirmed = state["status"] == "completed" and actual["passed"]
    passed = state["status"] == expected and (confirmed if expected == "completed" else not actual["passed"])
    passed = passed and all(recorded.get(criterion, {}).get("status") == reason
                            for criterion, reason in case.get("expected_checks", {}).items())
    usage = state.get("model_usage", {})
    recovered = any(event["event"] == "reconciled" for event in state["history"])
    if case.get("interrupt_after_write"):
        passed = passed and recovered and actions == 1
    trajectory = {}
    if "expected_trajectory" in case:
        trace = state.get("tool_trace")
        expected_trajectory = case["expected_trajectory"]
        evaluation = tool_trace.evaluate(expected_trajectory, trace)
        passed = passed and evaluation["passed"]
        trajectory = {"trajectory": {**evaluation, "expected": expected_trajectory, "trace": trace}}
    return {
        "scenario": case["name"], "iteration": index + 1, "variant": variant,
        "passed": passed, "completed_and_verified": confirmed, "status": state["status"],
        "expected_status": expected, "checks": {name: check["status"] for name, check in actual["checks"].items()},
        "actions": actions, "reconciled": recovered, "model_calls": usage.get("calls", 0),
        "input_tokens": usage.get("input_tokens", 0), "output_tokens": usage.get("output_tokens", 0),
        "usage_missing_calls": usage.get("usage_missing_calls", 0),
        "experience_hint_calls": usage.get("experience_hint_calls", 0),
        "estimated_input_tokens": usage.get("estimated_input_tokens", 0),
        "elapsed_seconds": round(elapsed, 4),
        **trajectory,
    }


def _metrics(records, synthetic):
    positive = [item for item in records if item["expected_status"] == "completed"]
    usage_complete = all(item["usage_missing_calls"] == 0
                         and (synthetic or item["model_calls"] > 0) for item in records)
    trajectories = [item["trajectory"]["passed"] for item in records if "trajectory" in item]
    return {
        "trajectory_pass_rate": statistics.mean(trajectories) if trajectories else None,
        "runs": len(records), "success_rate": statistics.mean(item["passed"] for item in records),
        "completion_rate": statistics.mean(item["completed_and_verified"] for item in positive) if positive else None,
        "avg_model_calls": statistics.mean(item["model_calls"] for item in records),
        "avg_tokens": statistics.mean(item["input_tokens"] + item["output_tokens"] for item in records)
        if usage_complete else None,
        "usage_missing_calls": sum(item["usage_missing_calls"] for item in records),
        "experience_hint_calls": sum(item["experience_hint_calls"] for item in records),
    }


def _report(kind, records, provenance):
    synthetic = kind == "offline-synthetic"
    names = dict.fromkeys(item["variant"] for item in records)
    return {"kind": kind, "provenance": provenance, **_metrics(records, synthetic),
            "variants": {name: _metrics([item for item in records if item["variant"] == name], synthetic)
                         for name in names}, "records": records}


def _validate(scenarios, repeat):
    if not isinstance(scenarios, list) or not scenarios or repeat < 1:
        raise ValueError("Nonempty scenarios and positive repeat required")
    names = set()
    for case in scenarios:
        if not isinstance(case, dict) or not isinstance(case.get("name"), str) or not case["name"].strip():
            raise ValueError("Every benchmark case needs a name")
        if case["name"] in names:
            raise ValueError("Benchmark case names must be unique")
        names.add(case["name"])
        if not isinstance(case.get("rules"), dict) or not case["rules"]:
            raise ValueError(f"{case['name']}: expected at least one artifact rule")
        if case.get("expected_status", "completed") not in ALLOWED - {"planning", "running"}:
            raise ValueError(f"{case['name']}: unsupported expected status")
        if "expected_trajectory" in case:
            tool_trace.validate_expectation(case["expected_trajectory"])


def benchmark(scenarios: list[dict], *, repeat: int = 1) -> dict:
    _validate(scenarios, repeat)
    provenance = manifest(scenarios, repeat)
    records = []
    for case in scenarios:
        for index in range(repeat):
            with tempfile.TemporaryDirectory() as folder:
                root = Path(folder).resolve()
                _write_fixture(root, case.get("initial_files", {}))
                path = root / "state.json"
                create(path, case["name"], list(case["rules"]), max_steps=case.get("max_steps", 10))
                desktop = ScriptedDesktop(root, case)
                verifier = FileVerifier(case["rules"], root)
                planner = ScriptedPlanner(case)
                start = time.perf_counter()
                trace_tools = "expected_trajectory" in case
                try:
                    state = run(path, desktop, planner, verifier=verifier, trace_tools=trace_tools)
                except ScriptedInterruption:
                    run(path, desktop, planner, verifier=verifier)
                    reconcile(path, outcome="executed", note="Scripted crash after writing the fixture")
                    state = run(path, desktop, planner, verifier=verifier)
                records.append(_record(case, index, "scripted", state, verifier, desktop.calls,
                                       time.perf_counter() - start))
    return _report("offline-synthetic", records, provenance)


def live_benchmark(scenarios, args, key):
    _validate(scenarios, args.repeat)
    for case in scenarios:
        if not isinstance(case.get("goal"), str) or not case["goal"].strip():
            raise ValueError(f"{case['name']}: live scenarios require a goal")
        if {"outputs", "fail_action", "interrupt_after_write"} & case.keys():
            raise ValueError(f"{case['name']}: scripted outputs, actions and interruption are offline only")
    experience = ExperienceStore(args.experience_store) if args.experience_store else None
    provenance = manifest(scenarios, args.repeat)
    provenance["model_budget"] = {"max_calls": args.max_model_calls, "max_tokens": args.max_model_tokens}
    if args.browser_url:
        provenance["playwright_version"] = package_version("playwright")
    records = []
    for case in scenarios:
        for index in range(args.repeat):
            variants = ["baseline", "experience"] if experience is not None else ["baseline"]
            # Alternate which run sees the application first within each pair.
            if index % 2:
                variants.reverse()
            for variant in variants:
                with tempfile.TemporaryDirectory() as folder:
                    root = Path(folder).resolve()
                    output = root / "artifacts"
                    output.mkdir()
                    _write_fixture(output, case.get("initial_files", {}))
                    path = root / "state.json"
                    goal = case["goal"].replace("{output_dir}", str(output))
                    create(path, goal, list(case["rules"]), max_steps=case.get("max_steps", 25))
                    verifier = FileVerifier(case["rules"], output)
                    planner = ModelPlanner(args.model, key, args.endpoint, max_calls=args.max_model_calls,
                                           max_tokens=args.max_model_tokens,
                                           experience_store=experience if variant == "experience" else None,
                                           experience_environment=args.experience_environment)
                    scope = browser_scope(args.browser_url, output) if args.browser_url else None
                    start = time.perf_counter()
                    with open_session(planner, nova=args.nova, browser_url=args.browser_url,
                                      download_dir=output if args.browser_url else None,
                                      browser_executable=args.browser_executable) as target:
                        state = run(path, target, planner, verifier=verifier, backend_scope=scope,
                                    trace_tools="expected_trajectory" in case)
                        backend_version = getattr(target, "backend_version", None)
                    record = _record(case, index, variant, state, verifier, state["steps"],
                                     time.perf_counter() - start)
                    record["backend_version"] = backend_version
                    records.append(record)
    result = _report("live-browser" if args.browser_url else "live-nova", records, provenance)
    result["model"] = args.model
    return result


def main():
    parser = argparse.ArgumentParser(description="Evaluate OpenAS goal execution")
    parser.add_argument("suite", type=Path)
    parser.add_argument("--case", help="Only run this scenario")
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--output", type=Path)
    backend = parser.add_mutually_exclusive_group()
    backend.add_argument("--nova", help="Run a live suite against the specified Nova executable")
    backend.add_argument("--browser-url", help="Run a live suite in isolated Playwright Chromium")
    parser.add_argument("--browser-executable")
    parser.add_argument("--model", default=os.getenv("OPENAS_GUI_MODEL"))
    parser.add_argument("--endpoint", default=os.getenv(
        "OPENAS_GUI_API_URL", "https://api.openai.com/v1/chat/completions"))
    parser.add_argument("--max-model-calls", type=int, default=35)
    parser.add_argument("--max-model-tokens", type=int, default=50_000)
    parser.add_argument("--experience-store", type=Path)
    parser.add_argument("--experience-environment", default="")
    args = parser.parse_args()
    try:
        suite = json.loads(args.suite.read_text(encoding="utf-8"))["scenarios"]
        if args.case:
            suite = [case for case in suite if case["name"] == args.case]
        if args.nova or args.browser_url:
            key = os.getenv("OPENAS_GUI_API_KEY")
            if not key or not args.model:
                raise ValueError("Live mode requires OPENAS_GUI_API_KEY and a model")
            if args.browser_executable and not args.browser_url:
                raise ValueError("--browser-executable requires --browser-url")
            if bool(args.experience_store) != bool(args.experience_environment):
                raise ValueError("--experience-store and --experience-environment must be used together")
            if min(args.max_model_calls, args.max_model_tokens) < 0:
                raise ValueError("Model limits must be nonnegative")
            result = live_benchmark(suite, args, key)
        else:
            if args.experience_store or args.experience_environment or args.browser_executable:
                raise ValueError("Experience and browser options require a live backend")
            result = benchmark(suite, repeat=args.repeat)
        output = json.dumps(result, ensure_ascii=False, indent=2)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(output + "\n", encoding="utf-8")
    except (OSError, ValueError, KeyError, TypeError, RuntimeError) as exc:
        parser.error(str(exc))
    print(output)
    if result["success_rate"] != 1:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
