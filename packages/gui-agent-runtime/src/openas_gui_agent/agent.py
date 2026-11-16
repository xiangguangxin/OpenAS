"""Bounded stateful agent execution."""
from __future__ import annotations
import time
from pathlib import Path
from typing import Any
from .state import load, persist, _record, TERMINAL
from .policy import needs_approval, fingerprint
from .verifier import EvidenceOnlyVerifier
from .locking import checkpoint_lock
def run(path: Path, desktop, planner, *, approval: bool = False, verifier=None) -> dict[str, Any]:
    with checkpoint_lock(path):
        return _run_locked(path, desktop, planner, approval=approval, verifier=verifier)


def _run_locked(path: Path, desktop, planner, *, approval: bool = False, verifier=None) -> dict[str, Any]:
    state = load(path)
    if state["status"] in TERMINAL:
        return state
    if state["status"] == "paused" and state["pending_approval"] and not approval:
        return state
    if state.get("pending_action"):
        # A crash may have happened after a non-idempotent action was executed.
        # Never automatically replay it; require operator reconciliation.
        state["status"] = "blocked"
        _record(state, "reconciliation_required", state["pending_action"]["name"])
        return persist(path, state)
    if approval and state["pending_approval"]:
        # Approval applies only to the exact pending action, not future actions.
        state["approved_action"] = state["pending_approval"]
        state["pending_approval"] = None
    state["status"] = "running"
    persist(path, state)
    while state["steps"] < state["max_steps"]:
        # Recover pending action conservatively: observe before any retry.
        try:
            observation = desktop.observe()
            if not isinstance(observation, dict):
                raise TypeError("Desktop observation must be a dict")
            state["last_observation"] = {"observed_at": time.time(),
                                         "summary": str(observation.get("summary", ""))[:200]}
            decision = planner.decide(state.copy(), observation)
            if not isinstance(decision, dict):
                raise TypeError("Planner decision must be a dict")
            kind = decision.get("type")
            if kind == "complete":
                # A planner must supply explicit per-criterion evidence; no self-certification.
                evidence = decision.get("evidence", {})
                if not (verifier or EvidenceOnlyVerifier()).verify(state["criteria"], evidence, observation):
                    raise ValueError("Missing acceptance evidence for one or more criteria")
                state["status"] = "completed"
                _record(state, "completed", "all criteria have evidence")
                state["pending_action"] = None
                break
            if kind == "pause":
                state["status"] = "paused"
                _record(state, "paused", decision.get("reason"))
                break
            if kind != "act" or not isinstance(decision.get("action"), dict):
                raise ValueError("Planner must choose act, complete or pause")
            action = decision["action"]
            if not isinstance(action.get("name"), str) or not action["name"]:
                raise ValueError("Action name required")
            # Planner must explicitly classify impact. Unclassified actions require approval.
            if needs_approval(action):
                action_fingerprint = fingerprint(action)
                if state.pop("approved_action", None) != action_fingerprint:
                    state["pending_approval"] = action_fingerprint
                    state["status"] = "paused"
                    _record(state, "approval_required", action["name"])
                    break
            # Write-ahead checkpoint: after crash, never replay this action blindly.
            state["pending_action"] = {"name": action["name"], "since": time.time()}
            persist(path, state)
            result = desktop.act(action)
            if not isinstance(result, dict):
                raise TypeError("Desktop action result must be a dict")
            state["steps"] += 1
            state["pending_action"] = None
            state["last_result"] = {"ok": result.get("ok") is True,
                                    "summary": str(result.get("summary", ""))[:200]}
            state["failures"] = 0 if result.get("ok") is True else state["failures"] + 1
            _record(state, "action", f"{action['name']}: {state['last_result']['ok']}")
            if state["failures"] >= 3:
                state["status"] = "blocked"
                _record(state, "blocked", "three consecutive failed actions")
                break
        except Exception as exc:
            state["failures"] += 1
            _record(state, "error", type(exc).__name__)
            # No automatic retry of a potentially already-executed action.
            if state["pending_action"] or state["failures"] >= 3:
                state["status"] = "blocked"
                break
        finally:
            persist(path, state)
    if state["status"] == "running":
        state["status"] = "paused" if state["steps"] >= state["max_steps"] else "blocked"
        _record(state, state["status"], "step budget exhausted")
    return persist(path, state)


