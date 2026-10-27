---
name: technology-selection
description: Compare feasible technology routes against requirements and hard constraints, preserving evidence, tradeoffs, PoC uncertainty, and architecture decision records.
---

[中文](SKILL.md) | English

Follow the [language policy](../../references/language.md).

# Technology selection

Start with requirements, quality goals, current system and resource bounds. Preserve specified technology; compare only open choices and do not reopen settled routes without a task reason.

Separate hard constraints from preferences. First check deployment, interfaces, data, licensing and team maintenance; then integration/operations cost, performance, ecosystem, upgrade and exit difficulty. Keep the current/simplest viable option as a baseline and compare only feasible candidates.

Use [technical research](../technical-research/SKILL.en.md) to verify current versions, support, pricing and maintenance from official material. Preserve source/version/conditions/unknowns per important dimension. Same features do not imply equal performance, and unknown is not zero. Explain weights/sensitivity if scoring, without letting totals hide a hard-constraint failure. State when advantages hold, sacrifices and evidence that would change the recommendation.

For route-changing hypotheses define a minimal comparable PoC with inputs/environment, controls, metrics/thresholds, resource bounds and stop conditions. Run only authorized experiments and record commands, versions and results; proposed experiments are not measured evidence.

Deliver matrix, recommendation, costs/limits, checks/unknowns and ADR status, context, alternatives, decision, rationale, consequences and reevaluation conditions. Keep required approvals pending rather than inventing people/dates. Handoff to [architecture design](../architecture-design/SKILL.en.md), returning infeasible requirements upstream instead of masking them with architecture prose. For library docs use available [Context7 guidance](../../integrations/context7/README.md), checking identity/version; retrieval is not a benchmark.
