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


def evaluate(rules, trace):
    if (trace is None or trace["started_after_steps"] or trace["dropped"]
            or any(event["tool"] is None or event["outcome"] == "unknown" for event in trace["events"])):
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
