"""Local adapter-call evidence and declarative trajectory checks."""
from collections import Counter
import re

TRACE_LIMIT = 128
_TOOL_NAME = re.compile(r"[A-Za-z0-9_.:-]{1,128}")
_EXECUTED = {"ok", "reconciled_executed"}


def enable(state):
    state.setdefault("tool_trace", {"started_after_steps": state["steps"], "dropped": 0, "events": []})


def begin(state, name, advertised):
    trace = state.get("tool_trace")
    if trace is None:
        return None
    known = (isinstance(advertised, (list, tuple)) and _valid_name(name)
             and any(isinstance(tool, dict) and tool.get("name") == name for tool in advertised))
    event = {"tool": name if known else None, "outcome": "unknown"}
    events = trace["events"]
    if len(events) >= TRACE_LIMIT:
        del events[0]
        trace["dropped"] += 1
    events.append(event)
    return event


def reconcile_last(state, outcome):
    events = state.get("tool_trace", {}).get("events", [])
    if events and events[-1]["outcome"] == "unknown":
        events[-1]["outcome"] = ("reconciled_executed" if outcome == "executed"
                                 else "reconciled_not_executed")


def _valid_name(name):
    return isinstance(name, str) and _TOOL_NAME.fullmatch(name) is not None


def validate_expectation(rules):
    if not isinstance(rules, dict) or not rules or rules.keys() - {"match", "tools", "forbidden", "max_counts"}:
        raise ValueError("Invalid expected_trajectory object")
    if rules.get("match", "in_order") not in ("exact", "in_order", "any_order"):
        raise ValueError("expected_trajectory.match must be exact, in_order or any_order")
    if "match" in rules and "tools" not in rules:
        raise ValueError("expected_trajectory.match requires tools")
    for field in ("tools", "forbidden"):
        names = rules.get(field, [])
        if not isinstance(names, list) or not all(_valid_name(name) for name in names):
            raise ValueError(f"expected_trajectory.{field} must be a list of tool names")
    limits = rules.get("max_counts", {})
    if not isinstance(limits, dict) or any(not _valid_name(name) or type(limit) is not int or limit < 0
                                           for name, limit in limits.items()):
        raise ValueError("expected_trajectory.max_counts must map tool names to nonnegative counts")


def _complete(trace):
    return (bool(trace) and not trace["started_after_steps"] and not trace["dropped"]
            and all(event["tool"] is not None and event["outcome"] != "unknown"
                    for event in trace["events"]))


def evaluate(rules, trace):
    if not _complete(trace):
        return {"passed": False, "reasons": ["incomplete_trace"]}

    events = trace["events"]
    attempted = [event["tool"] for event in events]
    executed = [event["tool"] for event in events if event["outcome"] in _EXECUTED]
    reasons = []
    if "tools" in rules:
        expected = rules["tools"]
        match = rules.get("match", "in_order")
        if match == "exact":
            matches = attempted == executed == expected
        elif match == "any_order":
            available = Counter(executed)
            matches = all(available[tool] >= count for tool, count in Counter(expected).items())
        else:
            remaining = iter(executed)
            matches = all(any(candidate == tool for candidate in remaining) for tool in expected)
        if not matches:
            reasons.append("sequence_mismatch")

    counts = Counter(attempted)
    for tool in sorted(set(rules.get("forbidden", [])) & counts.keys()):
        reasons.append(f"forbidden_tool:{tool}")
    for tool, maximum in rules.get("max_counts", {}).items():
        if counts[tool] > maximum:
            reasons.append(f"count_exceeded:{tool}")
    return {"passed": not reasons, "reasons": reasons}


def compare_checkpoints(baseline, candidate):
    """Locate the first difference visible in two checkpoints' recorded evidence."""
    sides = [(label, checkpoint.get("tool_trace"))
             for label, checkpoint in (("baseline", baseline), ("candidate", candidate))]
    incomplete = [label for label, trace in sides if not _complete(trace)]
    if incomplete:
        return {"status": "inconclusive", "incomplete": incomplete}

    sequences = [[{"tool": event["tool"], "outcome": event["outcome"]}
                  for event in trace["events"]] for _, trace in sides]
    for index in range(max(map(len, sequences))):
        left, right = (events[index] if index < len(events) else None for events in sequences)
        if left != right:
            return {"status": "different", "stage": "tool", "action": index + 1,
                    "baseline": left, "candidate": right}

    def artifact_checks(state):
        report = state.get("artifact_verification", {})
        return {criterion: result["status"] for criterion, result in report.get("checks", {}).items()}

    left, right = map(artifact_checks, (baseline, candidate))
    different = [criterion for criterion in sorted(left.keys() | right.keys())
                 if left.get(criterion) != right.get(criterion)]
    if different:
        criterion = different[0]
        return {"status": "different", "stage": "artifact", "criterion": criterion,
                "baseline": left.get(criterion), "candidate": right.get(criterion)}
    if baseline["status"] != candidate["status"]:
        return {"status": "different", "stage": "runtime", "baseline": baseline["status"],
                "candidate": candidate["status"]}
    return {"status": "match", "actions_compared": len(sequences[0])}
