---
name: decision-mapping
description: Map unresolved decisions for large ambiguous goals across sessions; track evidence and dependencies without automatically implementing or publishing issues.
---

[中文](SKILL.md) | English

Follow the [language policy](../../references/language.md), [evidence policy](../../references/evidence-policy.en.md), and [project context](../../references/project-context.en.md). Reuse goals and authorization; ask only about unresolved scope or costly tradeoffs.

# Decision mapping

Define the destination, exclusions, current decisions, and blocking unknowns. If the route is clear, use [writing-plans](../writing-plans/SKILL.en.md) directly. A map resolves what must be decided; implementation tasks deliver already decided behavior.

## Build and advance the map

Use existing RFC/ADR/tracker conventions. Without one, suggest `docs/decisions/<goal>/map.md`; write only when saving is in scope. Use the [template](references/map-template.md). Give each question a stable ID, title, type (research/prototype/decision/prerequisite), prerequisites, owner, status, closure condition, and evidence links. Dependencies point to prerequisites; reject missing references and cycles. Keep questions that cannot yet be stated precisely in an unresolved area rather than inventing implementation tasks.

Choose an unclaimed question whose dependencies are closed. Check evidence freshness first. Use [technical-research](../technical-research/SKILL.en.md) for research and record hypotheses and limits for prototypes. Preserve actual human answers to product decisions; never impersonate them. Let implementers settle local reversible choices. Do not interrupt authorized continuous work just to enforce one ticket per session.

On closure, retain the decision, rationale, evidence, and consequences; keep only a summary and detail link in the map. Mark invalidated decisions superseded and reopen affected work; do not erase history or consume stale conclusions. Add precise questions as uncertainty clears; move work beyond the destination out of scope. Remote issue creation, comments, assignment, and closure require existing authorization. Local records are sufficient without installing a tracker.

## Handoff and stopping

Return the destination, decisions, available frontier, blockers, evidence, and next steps. Stop at the destination or budget/tool limits, disclosing gaps. A clear route is not a completed implementation. Use [context-handoff](../context-handoff/SKILL.en.md) across sessions and implementation planning after decisions are ready. Parallel work still requires independent resources, host support, and authorization.

For example, team execution first needs decisions about state ownership, credentials, and conflicts. A reproduced empty-input defect needs no decision map.

See [provenance](../../references/skill-methods/NOTICE.md).
