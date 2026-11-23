---
name: workflow-routing
description: "Select minimal skill bundles and light/standard/heavy rigor for features, bug fixes, refactoring or documentation from explicit scope and risk; routing does not authorize tools or production operations."
---

English | [中文](SKILL.md)

Follow the [language policy](../../references/language.md), [evidence policy](../../references/evidence-policy.en.md) and [project context](../../references/project-context.en.md). Reuse existing authorization; never infer production permissions from keywords.

# Choose a bundle, then rigor

| Frequent task | Minimal default bundle | Add only when needed |
| --- | --- | --- |
| Feature | solution-design → test-driven-development → verification-before-completion | Design/code review for multiple modules; impact analysis for API changes |
| Bug fix | bug-fix → verification-before-completion | Escalate incidents, authentication and data risks; establish the failing baseline |
| Refactor / impact | change-impact-analysis → code-simplification → verification-before-completion | Architecture conformance and design review for boundary changes |
| Documents / reports | project-documentation → verification-before-completion | document-review at standard rigor; Office/PDF/diagram methods only for their carriers |

Do not load all other skills by default. The machine registry [task-routing.json](../../references/task-routing.json) records each skill's owner, category, activation and trigger. Read-only analysis delivers a report without automatically entering modification workflows.

## Tiered Rigor

- **light**: Explicit, single-file change without declared sensitive risks. Retain scope, real command, working directory, exit status and object fingerprints. Bug fixes also require a failing baseline. Skip separate design artifacts, model reviews and independent acceptance sessions; label host self-checks accurately.
- **standard**: Multiple files/modules, unknown risk or Office/browser/desktop work. Preserve applicable design, independent review and acceptance; do not mandate unrelated artifacts.
- **heavy**: Security, public APIs, persistent data migration, production incidents, critical performance, concurrency or broad changes. Require impact analysis, design review and relevant security/performance reviews. Light rigor cannot bypass these floors.

Missing risk information defaults to standard. An explicit empty risk list is a caller declaration, not proof of safety. Reclassify when the actual diff changes scope or risk; the machine gate cannot infer every semantic risk. Preserve stricter user requirements.

```bash
python3 /path/to/OpenAS/plugins/openas/workflows/task_router.py --task task.json
```

Use task_kind feature/bugfix/refactor/documentation and rigor auto/light/standard/heavy with actual scope, risk_factors, optional module_count and carrier. Executable tasks also require requirement, acceptance, checks and explicit acceptance_checks mappings. The planner only returns a route; it executes no task or installation.

The Codex adapter enforces tiers only when rigor is present. Existing tasks retain legacy workflows and the development default. An explicit workflow in a tiered task must agree with the planned route. Use the existing commands in the [runtime guide](../../workflows/README.en.md); task labels add no permissions.

<details>
<summary>Enable only for matching risks or carriers</summary>

- Security: security-review. Critical performance: performance-analysis. Production incident: incident-response.
- Office: [office](../office/SKILL.en.md). Browser: [browser-goal-executor](../browser-goal-executor/SKILL.en.md). Desktop: [gui-goal-executor](../gui-goal-executor/SKILL.en.md). Diagrams: [technical-diagrams](../technical-diagrams/SKILL.en.md).
- Research/product/architecture specialists remain conditional; use research-design for the full preliminary design chain.
- Read-only review/security-review, operations, task graphs and PR feedback retain their original entry points. Do not force them into a modification bundle.
- Skill maintenance and project-memory are not mandatory closing steps for every small task.

</details>

Report the selected bundle, tier and reasons, actual checks, result and limits. Simple tasks need no team or diagram; use [task-orchestration](../task-orchestration/SKILL.en.md) for real dependencies.

## Explicit specialist selection

Add `capabilities` only when needed: decision-mapping, task-slicing, spec, research, security-audit, react, animation, video, neon, azure-messaging. The registry's `specializations` maps them to skills. Omission preserves the four minimal bundles; unknown or duplicate values fail.

This field only adds skill recommendations; it does not change rigor, route, roles, or authorization. Keep actual scope/risks; a specialist label cannot lower the tier. security-audit selects security-review's deep reference. Planning/research does not become implementation through this field. The Codex runner requires explicit rigor; native `/openas:<skill>` calls remain available.

For example an actual React change may add `"capabilities": ["react", "animation"]` alongside its real scope/risks, without selecting Neon, Azure, or video tools. See [provenance and tradeoffs](../../references/skill-methods/NOTICE.md).
