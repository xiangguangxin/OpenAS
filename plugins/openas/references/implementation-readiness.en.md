# Design depth and implementation readiness

[中文](implementation-readiness.md) | English

Follow the [language policy](language.md). Design should let implementers identify tasks, correct behavior and verification without inventing key product, interface or data-safety decisions. Settle expensive cross-boundary decisions early; leave reversible local choices to developers. Page count, file count and pseudocode length do not establish readiness.

## Depth follows risk

| Change | Sufficient design |
| --- | --- |
| Copy, formatting, simple configuration | Goal, scope and check method |
| Local feature or clear defect | Current/expected behavior, entry, boundaries and regressions |
| Cross-module feature | Responsibilities, contracts, data flow, errors and task dependencies |
| Concurrency, persistence, protocols, migration | Relevant states, invariants, ordering, retries/idempotency, recovery, compatibility and focused validation |

Do not require every category for every project. Private helper names, loops and local decomposition normally belong to implementation, unless choices alter public interfaces, data semantics or resource lifetime.

## Remove consequential ambiguity

Requirements must translate to inputs/actions/expected outcomes with non-goals. Define relevant I/O, units, errors and ownership, plus observable success/failure states. For example, large-file upload needs size-limit source, identity, ID/duplicate-name rules, success/errors/cleanup and whether chunking/resumption is excluded. If filesystem and database update together, define order and partial-failure recovery; do not invent these mechanisms when irrelevant.

Tasks represent a verifiable behavior or cohesive change, not fixed time/line/file quotas. Preserve original acceptance, target behavior/non-goals, upstream inputs/dependencies/start conditions, allowed modules/files (label proposed new paths), deliverables/contracts/local discretion, proving checks and missing environment. Shared files/state or unsatisfied dependencies prevent automatic parallelism.

## Readiness and unknowns

Ready means no blocking open decision affecting scope, public contracts, persistent meaning or core correctness; key acceptance maps to modules and executable verification; and the ready subset has dependencies and necessary environment, or explicit nonblocking limits.

Leave reversible local unknowns to developers. Route feasibility-changing unknowns to bounded research/PoC with hypotheses, experiments, thresholds and stop conditions. Return only real product/irreversible user choices for decisions. Research readiness is not product implementation readiness.

Review by reconstructing paths, boundaries and acceptance. Name concrete ambiguities that could yield incompatible reasonable implementations; do not block merely because prose is short. No actual multi-agent run is needed for this reasoning. Report ready, limited-scope ready or not ready with permitted scope, blockers and closing evidence. Translate explanatory prose according to user preference while preserving existing schema/verdict values. Technical readiness is not authorization or passed runtime tests.
