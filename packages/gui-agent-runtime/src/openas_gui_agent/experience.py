"""Local, explicitly curated task experience store.

Never store raw screenshots, prompts, credentials or action arguments.
Experiences are hints, NOT commands to replay automatically.
"""
from __future__ import annotations
import json
import os
import tempfile
import time
from pathlib import Path
from .state import load

class ExperienceStore:
    def __init__(self, path: Path):
        self.path = path

    def _read(self):
        if not self.path.exists():
            return {"version": 1, "experiences": []}
        data = json.loads(self.path.read_text(encoding="utf-8"))
        if data.get("version") != 1 or not isinstance(data.get("experiences"), list):
            raise ValueError("Unsupported experience store")
        return data

    def _write(self, data):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, name = tempfile.mkstemp(prefix=".experience-", dir=self.path.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                json.dump(data, stream, ensure_ascii=False, indent=2)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(name, self.path)
        finally:
            if os.path.exists(name):
                os.unlink(name)

    def add_verified(self, checkpoint: Path, *, verifier, environment: str, note: str) -> dict:
        state = load(checkpoint)
        if state["status"] != "completed":
            raise ValueError("Only completed tasks can become experiences")
        if not environment.strip() or not note.strip():
            raise ValueError("Environment and operator note required")
        # Re-check the current artifact; do not trust model-provided evidence.
        if not verifier.verify(state["criteria"], {}, {}):
            raise ValueError("Independent verifier did not pass")
        item = {
            "id": state["id"], "goal": state["goal"][:1000],
            "criteria": state["criteria"][:20],
            "environment": environment[:200], "note": note[:500],
            "steps": state["steps"], "recorded_at": time.time(),
            "source": "independently-verified",
        }
        data = self._read()
        if any(existing["id"] == item["id"] for existing in data["experiences"]):
            raise ValueError("Experience already recorded")
        data["experiences"].append(item)
        self._write(data)
        return item

    def search(self, query: str, *, environment: str, limit: int = 5) -> list[dict]:
        if not query.strip() or not environment.strip() or limit < 1:
            return []
        terms = set(query.casefold().split())
        items = [x for x in self._read()["experiences"]
                 if x.get("environment") == environment and x.get("source") == "independently-verified"]
        scored = [(len(terms & set(x["goal"].casefold().split())), x) for x in items]
        return [item for score, item in sorted(scored, key=lambda x: x[0], reverse=True)
                if score > 0][:limit]
