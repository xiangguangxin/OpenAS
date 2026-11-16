"""Independent, local, declarative file checks; no arbitrary code execution."""
from __future__ import annotations
import json
from pathlib import Path

class FileVerifier:
    """Checks an allowlisted set of local files, ignoring model claims.

    Rules map exact criterion strings to {path, min_bytes?, contains?}.
    Paths must be within root; symlink escapes are rejected.
    """
    def __init__(self, rules: dict, root: Path):
        self.rules = rules
        self.root = root.resolve(strict=True)

    @classmethod
    def from_json(cls, config: Path):
        config = config.resolve(strict=True)
        data = json.loads(config.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or not isinstance(data.get("criteria"), dict):
            raise ValueError("Verifier JSON must contain criteria object")
        root = (config.parent / data.get("root", ".")).resolve(strict=True)
        return cls(data["criteria"], root)

    def verify(self, criteria, evidence, observation):
        for criterion in criteria:
            rule = self.rules.get(criterion)
            if not isinstance(rule, dict) or not isinstance(rule.get("path"), str):
                return False
            relative = Path(rule["path"])
            if relative.is_absolute() or ".." in relative.parts:
                return False
            path = (self.root / relative).resolve()
            if not path.is_relative_to(self.root) or not path.is_file():
                return False
            minimum = rule.get("min_bytes", 1)
            if type(minimum) is not int or minimum < 0 or path.stat().st_size < minimum:
                return False
            if "contains" in rule:
                if not isinstance(rule["contains"], str) or len(rule["contains"]) > 4096:
                    return False
                if path.stat().st_size > 2_000_000:
                    return False
                if rule["contains"] not in path.read_text(encoding="utf-8"):
                    return False
        return True
