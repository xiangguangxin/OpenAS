---
name: codebase-analysis
description: Explain repository entry points, modules, dependencies, core call paths, and extension mechanisms from source evidence; do not default to audits or binary reverse engineering.
---

[中文](SKILL.md) | English

Follow the [language policy](../../references/language.md).

For factual answers, tests, reviews or completion claims, first read and follow the [shared evidence policy](../../references/evidence-policy.en.md).

# Codebase analysis

Establish the question, version, subsystem and available source using [project adaptation](../../references/project-context.en.md). Default to read-only; write a requested report only at its designated path. For large repositories select relevant entry points and representative flows and disclose coverage rather than reading everything.

Read project overview, build manifests, runtime configuration and directories, then verify executable entries, public APIs, tests and boundaries in code. Distinguish production, fixtures, examples, generated and third-party code. Documentation is a lead; names and file counts do not establish responsibility or importance.

Trace a real entry through input, calls, state/data transfer and output. Add relevant failures, initialization and resource cleanup, citing core symbols and callers. Distinguish source/build dependencies from runtime interactions. A static reference is not execution order, and a helper's existence does not prove reachability.

For plugins, reflection, generation and injection inspect registration, discovery and binding. Identify candidate or unresolved edges rather than inventing paths. Only run focused checks with existing authorization/tools, recording environment, input and observations; reading source is not runtime verification.

Deliver boundaries, responsibilities, key paths, ownership, external dependencies and extension points relevant to the question. Cite files and symbols for key conclusions and separate code facts, documented claims, inferences and unknowns. Extension points require actual registration/call mechanisms and examples.

Use [technical diagrams](../technical-diagrams/SKILL.en.md) when helpful with consistent names. Avoid source dumps and directory-only lists. Report version, coverage, explanation, evidence index and unresolved items, without implying a comprehensive audit. Use [change impact analysis](../change-impact-analysis/SKILL.en.md) for proposed edits, [conformance](../architecture-conformance/SKILL.en.md) for constraints, [evolution](../architecture-evolution/SKILL.en.md) for redesign and [documentation](../project-documentation/SKILL.en.md) for reader-facing output. Finding structure issues does not authorize edits.
