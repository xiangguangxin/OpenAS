"""Bounded stateful agent execution."""
from __future__ import annotations
import time
from pathlib import Path
from typing import Any
from .state import load, persist, _record, TERMINAL
from .policy import needs_approval, fingerprint
from .verifier import EvidenceOnlyVerifier
from .verification import FileVerifier
from .locking import checkpoint_lock
from .planner import TokenBudgetExceeded
from . import tool_trace


def run(path: Path, desktop, planner, *, approval: bool = False, verifier=None,
        backend_scope=None, trace_tools: bool = False) -> dict[str, Any]:
    with checkpoint_lock(path):
        return _run_locked(path, desktop, planner, approval=approval, verifier=verifier,
                           backend_scope=backend_scope, trace_tools=trace_tools)


def _run_locked(path: Path, desktop, planner, *, approval: bool, verifier,
                backend_scope, trace_tools: bool) -> dict[str, Any]:
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
    saved_scope = state.get("backend_scope")
    if saved_scope is not None and backend_scope != saved_scope:
        raise ValueError("Resume requires the original browser settings")
    if backend_scope is not None and saved_scope is None:
        if state["steps"] or state.get("last_result") or state.get("pending_approval"):
            raise ValueError("Start browser execution with a fresh checkpoint")
        state["backend_scope"] = backend_scope
    if isinstance(verifier, FileVerifier):
        verifier.prepare(state)
    elif state.get("artifact_baseline") is not None:
        raise ValueError("Resume requires the original artifact verifier")

    if approval and state["pending_approval"]:
        # Approval applies only to the exact pending action, not future actions.
        state["approved_action"] = state["pending_approval"]
        state["pending_approval"] = None
    state["status"] = "running"
    if trace_tools:
        tool_trace.enable(state)
    if hasattr(planner, "usage"):
        planner.usage.update(state.get("model_usage", {}))
    persist(path, state)
    while state["steps"] < state["max_steps"]:
        # Recover pending action conservatively: observe before any retry.
        try:
            observation = desktop.observe()
            if not isinstance(observation, dict):
                raise TypeError("Desktop observation must be a dict")
            state["last_observation"] = {"observed_at": time.time(),
                                         "summary": str(observation.get("summary", ""))[:200]}
            try:
                decision = planner.decide(state.copy(), observation)
            finally:
                if hasattr(planner, "usage"):
                    state["model_usage"] = dict(planner.usage)
            if not isinstance(decision, dict):
                raise TypeError("Planner decision must be a dict")
            kind = decision.get("type")
            if kind == "complete":
                if isinstance(verifier, FileVerifier):
                    state["artifact_verification"] = verifier.evaluate(state)
                    accepted = state["artifact_verification"]["passed"]
                    if not accepted:
                        _record(state, "artifact_rejected", ", ".join(
                            check["status"] for check in state["artifact_verification"]["checks"].values()))
                else:
                    accepted = (verifier or EvidenceOnlyVerifier()).verify(
                        state["criteria"], decision.get("evidence", {}), observation)
                if not accepted:
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
                scope = observation.get("action_scope") if backend_scope is not None else None
                action_fingerprint = fingerprint({"scope": scope, "action": action} if scope else action)
                if state.pop("approved_action", None) != action_fingerprint:
                    state["pending_approval"] = action_fingerprint
                    state["status"] = "paused"
                    _record(state, "approval_required", action["name"])
                    break
            # Write-ahead checkpoint: after crash, never replay this action blindly.
            state["pending_action"] = {"name": action["name"], "since": time.time()}
            event = tool_trace.begin(state, action["name"], observation.get("tools"))
            persist(path, state)
            started = time.monotonic() if event is not None else None
            result = desktop.act(action)
            if not isinstance(result, dict):
                raise TypeError("Desktop action result must be a dict")
            if event is not None:
                event["outcome"] = "ok" if result.get("ok") is True else "error"
                event["duration_ms"] = round((time.monotonic() - started) * 1000, 3)
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
        except TokenBudgetExceeded:
            state["status"] = "paused"
            _record(state, "paused", "model token/call budget exhausted")
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


