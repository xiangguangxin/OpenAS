---
name: workflow-routing
description: Choose the smallest adequate implementation, repair, review, documentation, operations, or research-design route from task goals, risk, and dependencies.
---

[中文](SKILL.md) | English

Follow the [language policy](../../references/language.md).

# Workflow routing

Read goals and [project adaptation](../../references/project-context.en.md), reusing authorization and settled choices. Choose a minimal adequate route:

| Task | Route | Boundary |
| --- | --- | --- |
| Small explicit change | direct | Implementation → host checks → verification |
| Cross-module/new/compatibility behavior | development | Design → review → necessary docs → implementation → review → checks/verification |
| Existing defect | repair | Full bounded repair loop with failure baseline and bug-fix |
| Review only | review | Read-only findings, without claiming product acceptance |
| Security assessment | security-review | Read-only security role, no automatic repairs |
| Environment/CI/deployment configuration | operations | IT edits declared workspace files, then review/checks/verifier; no online operations |
| Market research through design | research-design | Research → requirements → solution → selection → architecture → docs → review/revisions → verification |
| Documentation edits | documentation | Write → review → relevant checks/verification |

The Codex adapter chooses `workflow` explicitly; omission defaults to development. Keywords do not infer authorization and direct cannot bypass required review. Use grilling only for explicit interviews. Explain route, rationale, artifacts, checks and missing conditions; simple work needs neither diagram nor team. Use [task orchestration](../task-orchestration/SKILL.en.md) for dependencies; see [runner guide](../../workflows/README.md) for real capabilities.

Choose domain skills rather than adding executor routes: market-research, product-requirements, competitive-analysis, roadmap-planning, technical-research, solution-design, technology-selection, architecture-design and design-review. Load the [full chain](../solution-design/references/research-to-design.md) only as requested. Pure investigation delivers a report; saving docs may use documentation without code implementation.

Use [document-review](../document-review/SKILL.en.md) for read-only documents or red-team's documentation stage, [architecture-conformance](../architecture-conformance/SKILL.en.md) for implemented constraints and [architecture-evolution](../architecture-evolution/SKILL.en.md) for staged plans. [CI/CD](../ci-cd/SKILL.en.md) config follows operations; [dependency upgrades](../dependency-upgrade/SKILL.en.md) involving product behavior use direct/development according to risk. [Codebase](../codebase-analysis/SKILL.en.md) and [impact](../change-impact-analysis/SKILL.en.md) analysis remain read-only by default and need no defect verdict or implementation phase. None automatically grants remote publication.

Use [agent-experience](../agent-experience/SKILL.en.md) for agent-facing tool descriptions, skill discovery, context loading, and handoff information interfaces. Use [code-simplification](../code-simplification/SKILL.en.md) to reduce duplicate state, ineffective interfaces, or maintenance obligations. Surveys remain read-only and deliver evidence directly; edits use direct/development according to existing authorization, scope, and risk, or documentation for skill/prose-only work. Neither adds an executor route or requires an extra audit for ordinary product UX, repairs, or reviews.
