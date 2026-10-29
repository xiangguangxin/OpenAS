---
name: design-review
description: Review consistency, feasibility, and acceptance across requirements, research, technical decisions, and architecture before implementation; report evidenced readiness gaps.
---

[中文](SKILL.md) | English

Follow the [language policy](../../references/language.md).

For factual answers, tests, reviews or completion claims, first read and follow the [shared evidence policy](../../references/evidence-policy.en.md).

# Design review and implementation readiness

Read actual versioned requirements, market/competitive evidence where relevant, solution, ADRs, architecture, interfaces and acceptance. Review only applicable scope; missing irrelevant template sections are not defects. Remain read-only for review requests.

Cross-check requirement-to-design/interface/verification mappings and non-goals; hard constraints, sources, versions and applicability of selected technologies; consistent boundaries, ownership, contracts, diagrams and deployment; relevant failures, permissions and recovery. Ensure hypotheses, targets and PoC plans are not presented as verified facts. Check dependencies, resources and blocking open decisions.

Use [implementation readiness](../../references/implementation-readiness.en.md). Reconstruct the implementation path and failure behavior to find concrete ambiguity that could produce incompatible reasonable implementations. Do not block on private-function detail or document length. Leave local reversible choices to developers; send feasibility unknowns to research/PoC. Define any independently ready subset and conditions for the rest.

Findings require stable ID, location, violated requirement/constraint, concrete counterexample/impact, responsible stage and closing evidence. Report evidence-based issues only; mark uncertain claims pending and do not turn wording preferences into blockers. Return issues to requirements, research, selection or architecture; retain IDs and reassess affected items after revision. Preserve real accepted-risk decisions without approving product tradeoffs for users.

Deliver coverage, findings, unverified items and readiness using existing host fields/verdicts. Blocking issues mean not ready; no findings means only no blockers found within this scope. Design approval is not runtime acceptance, market validation or release authorization. Use [acceptance tracking](../acceptance-tracking/SKILL.en.md) and the [full design flow](../solution-design/references/research-to-design.md) as needed. Do not automatically edit or start teams.
