---
name: context-handoff
description: Transfer current task goals, authorization, state, decisions, artifacts, evidence, and remaining work to another role or session; keep it separate from long-term memory.
---

[中文](SKILL.md) | English

Follow the [language policy](../../references/language.md).

For factual answers, tests, reviews or completion claims, first read and follow the [shared evidence policy](../../references/evidence-policy.en.md).

# Context handoff

Preserve original goals and acceptance, authorization, workspace/branch, file scope and existing user changes. Distinguish established facts, decisions, inferences and pending questions. Do not omit implementation-relevant constraints for brevity.

Include completed phases and artifact locations, last trusted snapshot, actual checks and coverage, unresolved issues, failure category and next steps. Prefer readable files and complete relevant evidence over role self-reports. Exclude unrelated conversations and authentication information.

The Codex adapter writes `handoff.json` beside `state.json`. Snapshots check local source only; the receiving session must revalidate actual workspace and rules before acting. File existence does not authorize historical actions. Current state is short-lived; only reviewed reusable knowledge belongs in [project memory](../project-memory/SKILL.en.md).
