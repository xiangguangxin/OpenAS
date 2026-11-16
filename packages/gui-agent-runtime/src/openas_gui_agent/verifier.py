"""Pluggable acceptance checks."""
from typing import Protocol
class Verifier(Protocol):
    def verify(self, criteria, evidence, observation) -> bool: ...
class EvidenceOnlyVerifier:
    """Compatibility fallback; model evidence is NOT independent proof."""
    def verify(self, criteria, evidence, observation):
        return isinstance(evidence, dict) and all(isinstance(evidence.get(c), str) and evidence[c].strip() for c in criteria)
