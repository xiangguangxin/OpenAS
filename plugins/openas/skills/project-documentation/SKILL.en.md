---
name: project-documentation
description: Write or update README, onboarding, design, API, deployment, operations, and troubleshooting documentation from code and evidence without presenting proposals as implemented features.
---

[中文](SKILL.md) | English

Follow the [language policy](../../references/language.md).

For factual answers, tests, reviews or completion claims, first read and follow the [shared evidence policy](../../references/evidence-policy.en.md).

# Project documentation

Confirm readers, task and requested paths. Read [project conventions](../../references/project-context.en.md), existing docs, relevant source and CI. Preserve language, structure and style unless translation is requested. Editing wording is not a reason to reorganize the entire documentation set.

New projects may document proposed designs from requirements/research/decisions, clearly labeled. For a full research-to-design handoff use the [design flow](../solution-design/references/research-to-design.md), preserving unknowns and conflicts. Read [document-type guidance](references/document-types.md) only as needed.

Lead with what readers need to do. For design documents place an overview architecture diagram after goals/scope, reusing an accurate existing one. Show boundaries, components and semantic relationships, arranged by responsibility/layer. Static dependencies are not execution order. Use [technical diagrams](../technical-diagrams/SKILL.en.md), including maintainable SVG when precise layout is needed. After the diagram explain responsibilities and input → processing/transfer → output, with relevant states, branches and failure/retry/end handling. Keep names consistent and prose understandable without the diagram.

Use short explanations, define necessary terms and put detailed constraints/tradeoffs in prose rather than crowded figures. Ground features, parameters, defaults and limits in source/config/tests/trusted material. Distinguish current, optional, experimental and future capabilities. Commands need directory, prerequisites, input and expected result; use placeholders, not credentials or local machine paths. Interfaces need units, ownership, errors and compatibility. Operations cover configuration, startup, health, diagnosis and applicable recovery. Prefer relative links and stable symbols rather than large copied implementations.

Run existing documentation checks for links, fences, examples/arguments, diff and diagram/text consistency. Check component/edge types, states, exceptions and reader comprehension. Verify examples in isolation according to risk; documentation checks alone do not authorize destructive actions, external writes or credentials. Disclose unexecuted checks.

Deliver changed sections/locations, sources, diagrams, actual verification and gaps. Tech writers author, executors/verifiers run checks; use [document review](../document-review/SKILL.en.md) for independent review, without turning every edit into a full team workflow.
