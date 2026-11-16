"""Deterministic, offline GUI agent benchmark; no real desktop or model API."""
from __future__ import annotations
import argparse
import json
import statistics
import tempfile
import time
from pathlib import Path
from .agent import run
from .state import create
from .verification import FileVerifier

class ScriptedDesktop:
    def __init__(self, root: Path, scenario: dict):
        self.root, self.scenario = root, scenario
        self.calls = 0
    def observe(self):
        return {"summary": "synthetic desktop", "step": self.calls}
    def act(self, action):
        self.calls += 1
        if self.scenario.get("fail_action"):
            return {"ok": False, "summary": "injected failure"}
        for filename, content in self.scenario.get("outputs", {}).items():
            target = (self.root / filename).resolve()
            if not target.is_relative_to(self.root):
                raise ValueError("Unsafe output path")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
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

def benchmark(scenarios: list[dict], *, repeat: int = 1) -> dict:
    if not scenarios or repeat < 1:
        raise ValueError("Nonempty scenarios and positive repeat required")
    records = []
    for case in scenarios:
        for index in range(repeat):
            with tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                path = root / "state.json"
                criteria = list(case["rules"])
                create(path, case["name"], criteria, max_steps=case.get("max_steps", 10))
                desktop = ScriptedDesktop(root, case)
                planner = ScriptedPlanner(case)
                verifier = FileVerifier(case["rules"], root)
                start = time.perf_counter()
                result = run(path, desktop, planner, verifier=verifier)
                elapsed = time.perf_counter() - start
                passed = result["status"] == "completed" and verifier.verify(criteria, {}, {})
                records.append({
                    "scenario": case["name"], "iteration": index + 1,
                    "passed": passed, "status": result["status"],
                    "actions": desktop.calls, "model_calls": planner.usage["calls"],
                    "input_tokens": planner.usage["input_tokens"],
                    "output_tokens": planner.usage["output_tokens"],
                    "elapsed_seconds": round(elapsed, 4),
                })
    return {
        "kind": "offline-synthetic", "runs": len(records),
        "success_rate": sum(r["passed"] for r in records) / len(records),
        "avg_model_calls": statistics.mean(r["model_calls"] for r in records),
        "avg_tokens": statistics.mean(r["input_tokens"] + r["output_tokens"] for r in records),
        "records": records,
    }

def main():
    parser = argparse.ArgumentParser(description="Offline deterministic OpenAS benchmark")
    parser.add_argument("suite", type=Path)
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    cases = json.loads(args.suite.read_text(encoding="utf-8"))["scenarios"]
    result = benchmark(cases, repeat=args.repeat)
    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output + "\n", encoding="utf-8")
    print(output)
if __name__ == "__main__":
    main()
