---
name: integration-testing
description: Build or investigate tests across module, database, or service boundaries with explicit real dependencies, isolated fixtures, cleanup, and behavioral evidence.
---

[中文](SKILL.md) | English

Follow the [language policy](../../references/language.md).

For factual answers, tests, reviews or completion claims, first read and follow the [shared evidence policy](../../references/evidence-policy.en.md).

# Integration testing

Read call paths, contracts, existing tests and authorized changes. Define which collaborations must be demonstrated, which dependencies must be real, which may be replaced and what replacements cannot prove.

Choose relevant protocol/behavior risks: transformations, errors, commit/rollback, retries, idempotency and compatibility. Assertions come from contracts, requirements or trusted references and check both responses and relevant state/effects. Use matching real databases for database semantics or disclose differences; mock success does not establish transactions, networking or deployment. Reserve end-to-end tests for critical combinations.

Reuse existing tools. Isolate namespaces, data, ports and temporary directories per test; use minimal fixtures and cleanup registered for failures as well as success, removing only created resources. Parallel tests must not share mutable defaults. Use bounded readiness probes, not fixed sleeps, and retain stage-specific failure logs.

External services follow authorization; do not connect to unspecified production or install dependencies automatically. Align retries/timeouts with contracts and avoid infinite retry. Prefer controlled clocks/events for timing checks; document unavoidable environment dependence.

For regressions show old behavior failing before verifying repair. Classify fixture, environment, assertion and product failures with commands/input/logs; do not modify product code to make tests pass. Deliver files, real/substitute dependencies/versions, isolation/cleanup, commands/exit codes, covered assertions and unverified properties. Follow [completion verification](../verification-before-completion/SKILL.en.md). Test engineers build tests, developers fix products, verifier independently accepts. Use available [Playwright tools](../../integrations/playwright/README.en.md) for real UI interactions; operation traces do not replace native regression tests.
