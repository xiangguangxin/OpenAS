"""Persistent, bounded GUI goal agent runtime (stdlib only).

Decision policy and desktop adapter are injected: a configured LLM or host must
provide the reasoning and a real, authorized MCP adapter must provide actions.
The runtime never invents desktop access or auto-approves sensitive operations.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol


class Desktop(Protocol):
    def observe(self) -> dict[str, Any]: ...
    def act(self, action: dict[str, Any]) -> dict[str, Any]: ...


class Planner(Protocol):
    def decide(self, state: dict[str, Any], observation: dict[str, Any]) -> dict[str, Any]: ...


SENSITIVE = {"delete", "overwrite", "send", "pay", "install", "permissions", "export", "commit"}
TERMINAL = {"completed", "failed", "blocked"}
ALLOWED = {"planning", "running", "paused", "blocked", "completed", "failed"}


def _save(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".goal-", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def create(path: Path, goal: str, criteria: list[str], *, max_steps: int = 40) -> dict[str, Any]:
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite checkpoint: {path}")
    if not goal.strip() or not criteria or max_steps < 1:
        raise ValueError("Goal, criteria and positive step budget required")
    state = {
        "version": 1, "id": str(uuid.uuid4()), "goal": goal,
        "criteria": criteria, "status": "planning", "steps": 0,
        "max_steps": max_steps, "failures": 0, "last_observation": None,
        "last_result": None, "pending_action": None, "pending_approval": None,
        "history": [], "created_at": time.time(), "updated_at": time.time(),
    }
    _save(path, state)
    return state


def load(path: Path) -> dict[str, Any]:
    state = json.loads(path.read_text(encoding="utf-8"))
    if state.get("version") != 1 or state.get("status") not in ALLOWED:
        raise ValueError("Unsupported or corrupt checkpoint")
    return state


def _persist(path: Path, state: dict[str, Any]) -> dict[str, Any]:
    state["updated_at"] = time.time()
    _save(path, state)
    return state


def _record(state: dict[str, Any], event: str, detail: Any = None) -> None:
    # No raw screenshots, control trees, credentials, or action payloads on disk.
    state["history"].append({"time": time.time(), "event": event,
                             "detail": str(detail or "")[:160]})
    state["history"] = state["history"][-100:]


def run(path: Path, desktop: Desktop, planner: Planner, *, approval: bool = False) -> dict[str, Any]:
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
        return _persist(path, state)
    if approval and state["pending_approval"]:
        # Approval applies only to the exact pending action, not future actions.
        state["approved_action"] = state["pending_approval"]
        state["pending_approval"] = None
    state["status"] = "running"
    _persist(path, state)
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
                if not isinstance(evidence, dict) or any(
                    not isinstance(evidence.get(c), str) or not evidence[c].strip()
                    for c in state["criteria"]
                ):
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
            impact = action.get("impact")
            if impact != "low" or action["name"].lower() in SENSITIVE:
                fingerprint = hashlib.sha256(json.dumps(action, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
                if state.pop("approved_action", None) != fingerprint:
                    state["pending_approval"] = fingerprint
                    state["status"] = "paused"
                    _record(state, "approval_required", action["name"])
                    break
            # Write-ahead checkpoint: after crash, never replay this action blindly.
            state["pending_action"] = {"name": action["name"], "since": time.time()}
            _persist(path, state)
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
            _persist(path, state)
    if state["status"] == "running":
        state["status"] = "paused" if state["steps"] >= state["max_steps"] else "blocked"
        _record(state, state["status"], "step budget exhausted")
    return _persist(path, state)


def main() -> None:
    parser = argparse.ArgumentParser(description="Persistent GUI goal runtime")
    sub = parser.add_subparsers(dest="command", required=True)
    start = sub.add_parser("create")
    start.add_argument("checkpoint", type=Path)
    start.add_argument("--goal", required=True)
    start.add_argument("--criterion", action="append", required=True)
    start.add_argument("--max-steps", type=int, default=40)
    status = sub.add_parser("status")
    status.add_argument("checkpoint", type=Path)
    args = parser.parse_args()
    if args.command == "create":
        state = create(args.checkpoint, args.goal, args.criterion, max_steps=args.max_steps)
    else:
        state = load(args.checkpoint)
    print(json.dumps(state, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
