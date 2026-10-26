---
name: architecture-conformance
description: Compare actual code with effective architecture decisions, boundaries, dependencies, ownership, and contracts; report deviations without replacing design review or runtime acceptance.
---

[中文](SKILL.md) | English

Follow the [language policy](../../references/language.md).

# Architecture conformance

Confirm target version, scope, effective architecture, ADRs, contracts, and accepted exceptions. Read actual code, build configuration, and callers. Without an agreed baseline, distinguish observed structure from unconfirmed intent; directory names and preferences are not constraints. Remain read-only by default.

Map constraints to implementation locations. Check dependency direction, prohibited cross-layer calls, cycles and public entry points; distinguish source, build and runtime relationships. Inspect data write authority, state ownership, resource lifetime, inputs/outputs, units, errors, compatibility, and relevant timeout/retry/idempotency semantics.

Static references establish visible dependencies, not runtime behavior. Investigate relevant registration or binding for dynamic loading, generated code, reflection and configuration injection. Missing static edges do not prove absent calls. Reuse existing checkers or focused code tracing; do not automatically install tools or execute targets.

Each finding needs a stable ID, violated constraint and source, implementation location, concrete dependency path or behavioral counterexample, impact, and suggested handling. Distinguish unauthorized deviations, valid exceptions, and stale designs; disagreement with documentation does not automatically make code wrong. Mark insufficient evidence as pending and check exception scope and reevaluation conditions.

Recommend automated rules only for real constraints, without freezing all current directory relationships. Send ordinary defects to [code review](../requesting-code-review/SKILL.en.md), and boundary changes to [architecture evolution](../architecture-evolution/SKILL.en.md). Deliver baseline, coverage, constraint mapping, deviations, exceptions, unchecked areas and advice. No findings does not establish an optimal design, runtime correctness, or release authorization.
