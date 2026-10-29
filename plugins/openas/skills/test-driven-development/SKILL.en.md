---
name: test-driven-development
description: Use RED → GREEN → REFACTOR to express confirmed behavior as meaningful tests, implement minimally, and verify regression protection.
---

[中文](SKILL.md) | English

Follow the [language policy](../../references/language.md).

For factual answers, tests, reviews or completion claims, first read and follow the [shared evidence policy](../../references/evidence-policy.en.md).

# Test-driven development

Cycle through RED (a meaningful failing test), GREEN (minimum correct implementation), then REFACTOR while retaining checks. Tests derive correctness from confirmed requirements, contracts or trusted references, not current implementation output. Resolve scope/contract ambiguities before using tests to decide them for users.

For executable behavior changes construct normal/boundary cases that expose wrong behavior, confirm the failure is for the intended reason, implement minimally and run related regressions. Check outputs, state and failures rather than strings mirroring code.

Pure text, formatting and low-impact reversible edits use appropriate checks without invented unit tests. If the test environment is unavailable disclose the blocker rather than claiming RED/GREEN. Expand verification only for new changes or uncovered risk after relevant checks pass.
