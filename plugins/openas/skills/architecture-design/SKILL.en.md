---
name: architecture-design
description: Design system boundaries, modules, interfaces, data, deployment, and failure behavior from requirements and technical decisions; produce architecture and requirement mappings.
---

[中文](SKILL.md) | English

Follow the [language policy](../../references/language.md).

# Architecture design

Read requirement IDs, technical decisions, existing code and project conventions. New projects may start from requirements and constraints. State current and proposed architecture and the change scope. Prefer a simple structure for small systems; do not default to microservices or new infrastructure.

Define decisions whose ambiguity would make independent implementations incompatible: external and module boundaries, responsibilities, dependency direction, data ownership, update rules, interfaces and error semantics. Where relevant include inputs/outputs, units, idempotency, timeouts, retries and compatibility.

Describe core and failure flows, data movement, state changes and recovery ownership. Address consistency, concurrency, permissions, resource bounds, observability and deployment according to risk. A technology list is not an architecture. Use concrete quality scenarios connecting load/failure conditions, targets, mechanisms, verification and unknowns; do not claim unmeasured capacity or performance.

Apply [implementation readiness](../../references/implementation-readiness.en.md): settle cross-boundary contracts, state, invariants and recovery, while leaving local reversible choices to developers. Map key acceptance criteria to modules and verification; identify implementable scope and blocking unknowns.

Use [technical diagrams](../technical-diagrams/SKILL.en.md) only when useful, with consistent names and a distinction between logical and deployment relationships. Keep stable decision IDs, alternatives, tradeoffs and applicability, referencing [technology selection](../technology-selection/SKILL.en.md). Migration covers compatibility, cutover, rollback and irreversible data risk; return infeasible constraints upstream.

Deliver architecture, useful diagrams, contracts, requirement-to-design/check mappings, risks and open decisions. Use [design review](../design-review/SKILL.en.md), then [project documentation](../project-documentation/SKILL.en.md). Use [architecture evolution](../architecture-evolution/SKILL.en.md) for staged existing-system changes and [conformance](../architecture-conformance/SKILL.en.md) after implementation. Design alone does not authorize implementation.
