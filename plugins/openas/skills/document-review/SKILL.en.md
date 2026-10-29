---
name: document-review
description: Independently review documentation against code, requirements, design, and sources for accuracy, completeness, diagrams, and usable instructions; remain read-only.
---

[中文](SKILL.md) | English

Follow the [language policy](../../references/language.md).

For factual answers, tests, reviews or completion claims, first read and follow the [shared evidence policy](../../references/evidence-policy.en.md).

# Document review

Identify document version, readers, their task and review scope. Read actual text/diff/context and relevant code, configuration, tests, requirements or sources using [project adaptation](../../references/project-context.en.md). Default to read-only; suggested corrections do not authorize rewriting documents or implementation.

For existing features verify current implementation and applicable version. For proposed designs use confirmed requirements and decisions rather than demanding nonexistent code. Separate current capability, history, hypotheses, plans and unresolved issues. Check optional/default and proposed/measured distinctions. Report source conflicts rather than choosing convenient evidence.

Check facts and contracts: features, parameters, defaults, paths, units, errors and compatibility. Check task completeness: directory, prerequisites, configuration, inputs, expected output and relevant failure/recovery. Check diagrams: names, boundaries, edge direction/type, input/output, states and exceptions; source comparison is not visual rendering. Check comprehension through concrete ambiguous steps, missing prerequisites or unfinishable reader tasks, not stylistic preferences or mandatory template length.

Consult [document-type guidance](../project-documentation/references/document-types.md) when relevant. Use [design review](../design-review/SKILL.en.md) for feasibility/readiness and [code review](../requesting-code-review/SKILL.en.md) for implementation defects. Accurate documentation of an existing limitation is not itself a documentation defect.

Reuse link/build/example checks after inspecting side effects. Run relevant examples/rendering only in authorized isolated environments. Review does not authorize external writes, production operations or dependency installation. Record commands, directory, exit codes and results; disclose missing tools and credentials. File existence does not prove anchors or external links work.

Follow the [team contract](../../references/team-contract.en.md). Each finding needs stable ID, severity, document location, factual source, concrete error/reader counterexample, impact, suggested revision and closing evidence. Separate confirmed issues, pending items and optional advice. Empty findings are allowed. Report coverage, actual checks, gaps and `approve`/`needs_fix`; unresolved P0/P1 blocks, P2 depends on acceptance. Recheck original IDs and affected content. Document approval is not system acceptance.
