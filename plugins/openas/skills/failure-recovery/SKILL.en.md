---
name: failure-recovery
description: Classify workflow failures and choose repair, bounded retry, or handoff; preserve partial effects and avoid endless retries or reset limits.
---

[中文](SKILL.md) | English

Follow the [language policy](../../references/language.md).

For factual answers, tests, reviews or completion claims, first read and follow the [shared evidence policy](../../references/evidence-policy.en.md).

# Failure recovery

Read failure, original command, exit code and context. Check partial artifacts and external effects. Classify from evidence, retaining unknown when necessary rather than calling every failure a network issue.

- `environment`: inspect executables, dependencies, paths and permissions; do not change product logic to hide missing prerequisites.
- `timeout` / `client_failure`: inspect logs, process termination and current files before resuming; do not automatically switch accounts/models or relax sandboxing.
- `invalid_result`: inspect structured output and compatibility; empty/malformed results cannot pass.
- `scope_violation`: stop and list extra changes; do not undo user files or expand authorization.
- `review_limit` / `acceptance_limit`: retain counterexamples and feedback, resolve the cause, then start a new revision task; do not reset counters to bypass limits.
- `interrupted`: inspect last trusted checkpoint and partial edits, then use [checkpoint-and-resume](../checkpoint-and-resume/SKILL.en.md).

Retry only clearly retryable steps with controlled effects, recording attempts, outcomes and stop conditions. The current runner has no background automatic retry; explicit resumption still validates scope and rules. Use [context handoff](../context-handoff/SKILL.en.md).
