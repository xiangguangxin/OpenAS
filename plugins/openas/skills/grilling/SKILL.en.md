---
name: grilling
description: Use explicit interviews or design pressure testing to clarify major tradeoffs; do not turn ordinary reviews or clear implementation requests into interviews.
---

[中文](SKILL.md) | English

Follow the [language policy](../../references/language.md).

# Design pressure testing

Help identify hidden assumptions, compare consequential tradeoffs and establish enough design for the next step. First read available code/docs and reuse confirmed decisions.

Use a dependency-aware interview only when the user explicitly requests detailed questioning, interviews or design exploration. Ordinary project review should investigate and report findings directly; clear authorized implementation continues without an extra approval ritual.

List goals, constraints, facts and the highest-impact unknowns. Investigate facts independently and ask only unavailable user choices. Prioritize decisions changing architecture, compatibility, cost or scope, not every possible branch. Ask a few answerable questions per round with alternatives, recommendation and tradeoffs; defer dependent questions.

Update decisions and excluded paths each round and continue independent analysis while awaiting replies. Stop when key risks/tradeoffs are sufficiently understood or the user ends discussion; deliver recommendation, rationale, assumptions and next actions. Do not claim exhaustive exploration or reconfirm settled choices. Review-only stays read-only; implementation and Git/deployment actions follow task authorization.
