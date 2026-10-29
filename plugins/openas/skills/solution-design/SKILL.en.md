---
name: solution-design
description: Compare solution alternatives and tradeoffs or coordinate research, requirements, selection, architecture, and design documentation without automatically starting development.
---

[中文](SKILL.md) | English

Follow the [language policy](../../references/language.md).

For factual answers, tests, reviews or completion claims, first read and follow the [shared evidence policy](../../references/evidence-policy.en.md).

# Solution design and full design flow

Start with user goals, [current project](../../references/project-context.en.md) and confirmed constraints. Separate problem, requirement and solution. Preserve chosen technologies/product decisions and proceed on clear inputs without repeated interviews.

State users, problem, goals/non-goals, flows, scope, quality and acceptance; use [product requirements](../product-requirements/SKILL.en.md) when formal handoff is needed. Compare meaningfully different paths against the status quo or simplest viable baseline, without manufacturing alternatives. Eliminate hard-constraint failures first, then compare value, feasibility, delivery/maintenance cost, risks and exit difficulty. Keep evidence/assumptions and explain conditions, costs and unknowns that could change the recommendation. A small task may need only one feasible approach.

Use [implementation readiness](../../references/implementation-readiness.en.md): settle cross-module/failure behavior, leave local reversible details, and send feasibility unknowns to research/PoC rather than hiding them in implementation tasks.

Read the [full design flow](references/research-to-design.md) only for end-to-end work and reuse valid artifacts. Use market-research/competitive-analysis for opportunities, technical-research/technology-selection for evidence and choices, architecture-design for boundaries, design-review for readiness, and project-documentation for delivery. Preserve project RFC locations, state, alternatives, rationale, risks and next steps. New projects use requirements/proposed designs. Default full design ends in documentation; [roadmaps](../roadmap-planning/SKILL.en.md) handle phases and [plans](../writing-plans/SKILL.en.md) handle authorized implementation.

The optional Codex `research-design` route requires a trusted task with workspace, inputs, scope and checks; see [workflow guide](../../workflows/README.md). Calling `/openas:solution-design` itself does not start an external process.
