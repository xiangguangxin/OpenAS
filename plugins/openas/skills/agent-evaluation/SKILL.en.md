---
name: agent-evaluation
description: "Benchmark agent outcomes, false completion, recovery, calls, and tokens on matched tasks and configurations."
---

[中文](SKILL.md) | English

Follow the [language policy](../../references/language.md) and [shared evidence policy](../../references/evidence-policy.en.md).

# Agent evaluation

1. Freeze tasks, environments, inputs, tools, budgets, and expected statuses. Include success, invalid artifacts, and interruption recovery. Use [artifact-verification](../artifact-verification/SKILL.en.md) to check the artifacts independently. Expected rejections pass when the specified status and check reasons match.
2. For GUI goals, use the [runtime benchmark](../../integrations/computer-use/RUNTIME.en.md#task-evaluation). Offline cases exercise the execution loop and acceptance logic. Live mode takes an explicit application environment and model. Reset the application between trials and compare matched cases with experience retrieval off and on using the same model and version.
3. Report case outcomes, required checks, scenario pass rate, verified completion rate for positive goals, calls, elapsed time, and reported provider tokens. Label missing usage and track estimates separately. Identify the actual desktop, browser, model, or test substitutes exercised.
4. When changing an existing skill, reuse [skill-maintenance](../skill-maintenance/SKILL.en.md) for baseline, candidate, and held-out behavior comparisons. Preserve the conditions that reproduced each failure and base improvement claims on measured results.
