"""Explicit, audited reconciliation of uncertain in-flight actions."""
from __future__ import annotations
from pathlib import Path
from .state import load, persist, _record
from .locking import checkpoint_lock

def reconcile(path: Path, *, outcome: str, note: str) -> dict:
    if outcome not in {"executed", "not-executed"}:
        raise ValueError("outcome must be executed or not-executed")
    if not note.strip():
        raise ValueError("A human reconciliation note is required")
    with checkpoint_lock(path):
        state = load(path)
        if state["status"] != "blocked" or not state.get("pending_action"):
            raise ValueError("Only blocked in-flight actions may be reconciled")
        # Even when the action was not executed, never replay the old command:
        # re-observe and ask the planner to choose a fresh action.
        action_name = state["pending_action"]["name"]
        state["pending_action"] = None
        state["pending_approval"] = None
        state.pop("approved_action", None)
        state["status"] = "paused"
        state["failures"] = 0
        state["steps"] += 1
        _record(state, "reconciled", f"{action_name}: {outcome}; {note[:100]}")
        return persist(path, state)
