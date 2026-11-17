"""Independent, declarative acceptance checks for local artifacts."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

MAX_TEXT_BYTES = 2_000_000


def _digest(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(128 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _json_pointer(document, pointer):
    if pointer == "":
        return document
    if not isinstance(pointer, str) or not pointer.startswith("/"):
        raise ValueError("Expected a JSON Pointer")
    for token in pointer[1:].split("/"):
        token = token.replace("~1", "/").replace("~0", "~")
        if isinstance(document, list):
            if not token.isascii() or not token.isdecimal() or (len(token) > 1 and token[0] == "0"):
                raise ValueError("Invalid JSON array index")
            document = document[int(token)]
        else:
            document = document[token]
    return document


class FileVerifier:
    """Bind fresh artifact rules to the first execution of a checkpoint."""

    def __init__(self, rules: dict, root: Path):
        self.rules = rules
        self.root = root.resolve(strict=True)
        spec = json.dumps([str(self.root), rules], sort_keys=True, ensure_ascii=False)
        self.identity = hashlib.sha256(spec.encode()).hexdigest()

    @classmethod
    def from_json(cls, config: Path):
        config = config.resolve(strict=True)
        data = json.loads(config.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or not isinstance(data.get("criteria"), dict):
            raise ValueError("Verifier JSON must contain criteria object")
        return cls(data["criteria"], config.parent / data.get("root", "."))

    def _path(self, rule):
        if not isinstance(rule, dict) or not isinstance(rule.get("path"), str):
            raise ValueError("Missing artifact rule or path")
        relative = Path(rule["path"])
        if relative.anchor or ".." in relative.parts:
            raise ValueError("Artifact path must stay within the verifier root")
        path = (self.root / relative).resolve()
        if not path.is_relative_to(self.root):
            raise ValueError("Artifact path must stay within the verifier root")
        return path

    def prepare(self, state):
        """Save the pre-action fingerprints once, including files that do not exist."""
        fresh = {criterion: rule for criterion in state["criteria"]
                 if isinstance(rule := self.rules.get(criterion), dict)
                 and rule.get("fresh") is True}
        existing = state.get("artifact_baseline")
        if existing is not None:
            if existing["verifier"] != self.identity:
                raise ValueError("Resume requires the original artifact verifier rules and root")
            return
        if not fresh:
            return
        if state["steps"] or state.get("pending_action") or state.get("last_result"):
            raise ValueError("Fresh artifacts require a baseline before the first action")
        baseline = {}
        for criterion, rule in fresh.items():
            path = self._path(rule)
            try:
                baseline[criterion] = _digest(path)
            except FileNotFoundError:
                baseline[criterion] = None
        state["artifact_baseline"] = {"verifier": self.identity, "sha256": baseline}

    def _check_rule(self, rule, baseline, checkpoint_id):
        try:
            path = self._path(rule)
        except (ValueError, OSError, RuntimeError):
            return "invalid_rule_or_path", {}
        minimum = rule.get("min_bytes", 1)
        contains = rule.get("contains")
        fields = rule.get("json_fields", {})
        run_pointer = rule.get("run_id_pointer")
        if (type(minimum) is not int or minimum < 0
                or ("fresh" in rule and type(rule["fresh"]) is not bool)
                or ("contains" in rule and (not isinstance(contains, str) or len(contains) > 4096))
                or not isinstance(fields, dict)
                or ("run_id_pointer" in rule and not isinstance(run_pointer, str))):
            return "invalid_rule", {}
        try:
            if not path.is_file():
                return "missing_file", {}
            size = path.stat().st_size
            if size < minimum:
                return "file_too_small", {"size": size}
            evidence = {"size": size}
            payload = None
            if contains is not None or fields or run_pointer is not None:
                with path.open("rb") as stream:
                    payload = stream.read(MAX_TEXT_BYTES + 1)
                if len(payload) > MAX_TEXT_BYTES:
                    return "text_limit_exceeded", evidence
                evidence["size"] = len(payload)
                if len(payload) < minimum:
                    return "file_too_small", evidence
            if rule.get("fresh"):
                if baseline is ...:
                    return "missing_baseline", evidence
                evidence["sha256"] = (_digest(path) if payload is None
                                      else hashlib.sha256(payload).hexdigest())
                if evidence["sha256"] == baseline:
                    return "stale_artifact", evidence
            if payload is not None:
                text = payload.decode("utf-8")
                if contains is not None and contains not in text:
                    return "text_mismatch", evidence
                if fields or run_pointer is not None:
                    data = json.loads(text)
                    for pointer, expected in fields.items():
                        actual = _json_pointer(data, pointer)
                        if json.dumps(actual, sort_keys=True) != json.dumps(expected, sort_keys=True):
                            return "json_field_mismatch", evidence
                    if run_pointer is not None and (
                            checkpoint_id is None or _json_pointer(data, run_pointer) != checkpoint_id):
                        return "run_id_mismatch", evidence
            return "passed", evidence
        except (OSError, UnicodeError, ValueError, TypeError, KeyError, IndexError, RecursionError):
            return "unreadable_or_invalid_content", {}

    def evaluate(self, state):
        baseline = state.get("artifact_baseline") or {}
        hashes = baseline.get("sha256", {}) if baseline.get("verifier") == self.identity else {}
        checks = {}
        for criterion in state["criteria"]:
            reason, evidence = self._check_rule(self.rules.get(criterion), hashes.get(criterion, ...),
                                                state.get("id"))
            checks[criterion] = {"status": reason, **evidence}
        return {"passed": bool(checks) and all(value["status"] == "passed" for value in checks.values()),
                "checks": checks}

    def verify(self, criteria, evidence, observation):
        return self.evaluate({"criteria": criteria})["passed"]
