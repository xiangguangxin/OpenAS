---
name: change-impact-analysis
description: Trace proposed changes or diffs through consumers, contracts, data, configuration, builds, tests, and documentation to identify compatibility risks and verification scope.
---

[中文](SKILL.md) | English

Follow the [language policy](../../references/language.md).

# Change impact analysis

Confirm original goal, current/target behavior, baseline and authorized scope. Identify exact compared commits or working-tree state for a diff, and distinguish proposed locations from existing implementation. Use [codebase analysis](../codebase-analysis/SKILL.en.md) where cross-module context is missing, without making every local change a whole-repository survey. Default to read-only.

List changed public behavior, symbols, configuration, formats or build inputs. Trace dependencies and consumers in both directions. As relevant inspect re-exports, inheritance, registration, dynamic loading, injection, generated artifacts and external protocols. Text matches are candidates, not proof; unresolved dynamic boundaries remain uncertain and zero matches do not establish no impact.

Check affected interfaces, return values, errors, defaults, units and supported versions; identify consumers of old semantics. Consider data ownership, persistent formats, state, resource lifetime and recovery, plus build/dependency/configuration/deployment/generated entry points. Include test expectations, fixtures, examples, documentation and acceptance. Do not merely change assertions to fit implementation.

Classify objects as requiring coordinated changes, requiring verification, uncertain, or demonstrably unaffected, with propagation paths or behavioral evidence. Necessary out-of-scope dependencies become blockers or decisions, not automatic edits.

Turn each risk into triggering conditions, affected consumers, impact and verification. Reuse relevant tests, naming uncovered behavior. Small diffs may change public defaults; multiple files do not automatically require every test. Compilation or type checks alone do not establish consumer compatibility.

Use [architecture evolution](../architecture-evolution/SKILL.en.md) for multi-version or irreversible migrations and [writing plans](../writing-plans/SKILL.en.md) for ready work. Deliver baseline, change summary, impact list with evidence/actions, compatibility risks, suggested scope, checks and unknowns. Use [code review](../requesting-code-review/SKILL.en.md) for correctness. Revisit conclusions after revisions; an impact report is neither implementation nor executed validation.
