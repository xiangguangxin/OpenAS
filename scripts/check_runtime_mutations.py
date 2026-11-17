#!/usr/bin/env python3
"""Verify that selected Runtime regressions fail when critical guards are weakened."""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

RUNTIME = Path(__file__).resolve().parents[1] / "packages/gui-agent-runtime"
MUTATIONS = (
    ("accept-stale-artifact", "verification.py", 'return "stale_artifact", evidence',
     'return "passed", evidence', "test_artifact_acceptance.CoverageAcceptanceTests.test_stale_report_cannot_pass"),
    ("ignore-action-count", "tool_trace.py", "if counts[tool] > maximum:", "if False:",
     "test_tool_trajectory.ToolTrajectoryTests.test_verified_file_does_not_hide_extra_dispatch"),
    ("skip-reconciliation", "agent.py", 'if state.get("pending_action"):', "if False:",
     "test_artifact_acceptance.CoverageAcceptanceTests.test_interrupted_action_preserves_baseline_and_does_not_repeat"),
)


def check(source, *tests):
    env = dict(os.environ, PYTHONPATH=os.pathsep.join((str(source), str(RUNTIME / "tests"))))
    return subprocess.run([sys.executable, "-B", "-m", "unittest", *tests], env=env, cwd=source.parent,
                          capture_output=True, text=True, timeout=30)


def main():
    try:
        baseline = check(RUNTIME / "src", *(case[-1] for case in MUTATIONS))
    except subprocess.TimeoutExpired:
        print("Baseline tests timed out", file=sys.stderr)
        return 1
    if baseline.returncode:
        sys.stderr.write(baseline.stderr)
        return 1

    outcomes = []
    for name, module, before, after, test in MUTATIONS:
        with tempfile.TemporaryDirectory(prefix="openas-mutation-") as folder:
            source = Path(folder) / "src"
            shutil.copytree(RUNTIME / "src", source, ignore=shutil.ignore_patterns("__pycache__"))
            path = source / "openas_gui_agent" / module
            original = path.read_text(encoding="utf-8")
            if original.count(before) != 1:
                outcomes.append({"mutation": name, "status": "anchor_changed"})
                continue
            path.write_text(original.replace(before, after, 1), encoding="utf-8")
            try:
                result = check(source, test)
            except subprocess.TimeoutExpired:
                outcomes.append({"mutation": name, "status": "timed_out"})
                continue

        if result.returncode == 0:
            status = "survived"
        elif result.returncode == 1 and re.search(r"^FAILED \(failures=1\)$", result.stderr, re.MULTILINE):
            status = "killed"
        else:
            status = "invalid_run"
            sys.stderr.write(result.stderr)
        outcomes.append({"mutation": name, "status": status})

    print(json.dumps(outcomes, indent=2))
    return 0 if all(case["status"] == "killed" for case in outcomes) else 1


if __name__ == "__main__":
    sys.exit(main())
