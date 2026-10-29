---
name: verification-before-completion
description: Verify acceptance with real evidence appropriate to the change, distinguishing unexecuted, static, mock, historical, and runtime checks.
---

[中文](SKILL.md) | English

Follow the [language policy](../../references/language.md).

For factual answers, tests, reviews or completion claims, first read and follow the [shared evidence policy](../../references/evidence-policy.en.md).

# Verification before completion

Confirm acceptance, changed objects and existing evidence. Use the [team contract](../../references/team-contract.en.md) for reports/classification.

For docs check source, links, fences, diff and available diagram previews. For behavior run tests and necessary builds covering the change; fixes need the original failing scenario or reproducible evidence. For apps/services/data check actual output, state and effects beyond exit codes, with protocol/timing traces only where relevant.

Record command, working directory, exit code, significant output and coverage. Mark unexecuted work and concrete tool gaps. Required acceptance without evidence cannot pass. Separate mock, historical, static and actual runtime evidence.

Before reuse, check actual target versions and relevant dependencies under the shared policy, obtaining affected-scope evidence again after changes. Map each claim to evidence instead of using a passing subset to prove whole-task completion.

Return failures to the implementer. Once checks pass, do not repeat unrelated full regressions without new changes or risk. Role assertions, script completion and user silence do not replace evidence.
