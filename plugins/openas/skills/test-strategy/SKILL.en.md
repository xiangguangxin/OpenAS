---
name: test-strategy
description: Plan risk-based test levels, scenarios, data, environments, and execution with acceptance mappings; do not confuse a test plan with implemented tests or final acceptance.
---

[中文](SKILL.md) | English

Follow the [language policy](../../references/language.md).

# Test strategy

Read original requirements/acceptance, actual interfaces/change scope, existing tests and environment/resource limits using [project adaptation](../../references/project-context.en.md). Do not assume a framework.

Map requirement IDs to observable behavior and failure impact. Select relevant normal, boundary, invalid-input, recovery, compatibility and cross-module scenarios; add state/concurrency/persistence checks only when involved. Distinguish current, proposed and unavailable coverage. Counts and line coverage do not replace behavior.

Use the smallest credible layer: unit tests for pure logic, integration for boundary contracts, necessary end-to-end tests for critical paths. Avoid repeating every assertion at every layer and explain behavior hidden by mocks. Without infrastructure propose a minimal executable setup rather than a large framework.

Test oracles come from requirements/specifications/trusted references, not copied implementation results. Define input, pre-state, action, expected output/effects, cleanup and evidence for key scenarios. Record data origin/redaction and avoid shared production data. Order checks by dependency/cost and record environment differences/blockers/stopping conditions. Missing required environment remains unverified; skips or mock passes are not substitutes. Expand checking only for new changes or unresolved risks.

Deliver a matrix of requirement/risk, scenario, layer, data/environment, test locations/entry, pass criteria and gaps. Planning means verification methods or explicit gaps, not execution success. Use [integration testing](../integration-testing/SKILL.en.md), [TDD](../test-driven-development/SKILL.en.md) and [completion verification](../verification-before-completion/SKILL.en.md). Test engineering builds coverage; verifier independently checks acceptance.
