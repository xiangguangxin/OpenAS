---
name: architecture-evolution
description: Plan staged refactoring and interface or data migration for existing systems, including compatibility, cutover, recovery, and retirement; do not automatically execute migrations.
---

[中文](SKILL.md) | English

Follow the [language policy](../../references/language.md).

For factual answers, tests, reviews or completion claims, first read and follow the [shared evidence policy](../../references/evidence-policy.en.md).

# Architecture evolution

Read implementation, callers, effective ADRs, deviations and original goals. Identify the observable problem, constraints and non-goals, separating demonstrated problems from hoped-for benefits. Retain the status quo or local repair as a baseline; imperfect structure is not a reason for an automatic rewrite. Default to a plan within existing authorization.

Identify affected modules, dependencies, consumers, data owners and deployment units, including coordinated versus independent changes. Use [architecture design](../architecture-design/SKILL.en.md) for target boundaries and failures. Retain decision IDs, assumptions and reevaluation triggers. Resolve feasibility unknowns through research or PoC first.

Compare one-time cutover with gradual replacement. Use adapters, compatible interfaces or coexistence only when justified; do not mechanically add dual writes, microservices or feature flags. Define compatibility windows, supported version combinations and exit criteria. Uncontrolled external consumers remain dependencies or blockers.

For each phase specify initial state, scope, dependencies, public behavior, invariants, verification, next-phase conditions and failure handling. Leave a coherent runnable system after each phase, or explain necessary downtime. Do not postpone all value and checking until the end.

For persistent data, define format compatibility, conversion/backfill order, read/write authority, partial-failure handling and consistency checks. Dual writes require a convergence strategy. Distinguish code rollback from data recovery; irreversible writes may require restoration or forward repair, not just an old executable.

Before cutover define success measures, observation scope and stop/rollback triggers. Retire old paths only with consumer migration, data checks and relevant observation evidence, then remove temporary adapters, flags and dependencies. Observation duration follows actual load and release cycles, not arbitrary fixed days.

Deliver baseline, target, tradeoffs, phases, compatibility/recovery, retirement conditions and open risks. Use [design review](../design-review/SKILL.en.md), [writing plans](../writing-plans/SKILL.en.md), and post-change [conformance](../architecture-conformance/SKILL.en.md). Approval for one phase does not automatically approve later ones.
