---
name: agent-evaluation
description: "评估 Agent 真实任务的完成率、误报、恢复、调用次数与 token，对照记忆开关或版本。 / Benchmark agent outcomes, false completion, recovery, calls, and tokens on matched tasks and configurations."
---

中文 | [English](SKILL.en.md)

遵循[语言约定](../../references/language.md)和[结论与证据共享规则](../../references/evidence-policy.md)。

# Agent 评测

1. 冻结任务、环境、输入、可用工具、预算和期望状态。准备成功、错误产物及中断恢复用例。用 [artifact-verification](../artifact-verification/SKILL.md) 独立确认产物条件。预期阻止完成的任务以正确状态和失败原因为通过条件。
2. 评估 GUI 任务时，用 [Runtime 评测入口](../../integrations/computer-use/RUNTIME.md#任务评测)。离线模式检查循环和验收逻辑。实机模式显式指定应用环境和模型。保持相同模型与版本，重置待测应用状态，使用匹配样本比较经验检索开启与关闭。
3. 报告逐例状态、验收判据、用例通过率、正向任务的已核验完成率、调用次数、耗时和实际 token。供应商缺少 usage 时标明缺失，单独列估算。按模拟桌面、真实浏览器、原生桌面和真实模型区分证据。
4. 修订已有技能触发或行为时沿用 [skill-maintenance](../skill-maintenance/SKILL.md) 的旧版、候选版和独立验收方法。评测发现问题后记录复现条件，只有真实结果能支持增益判断。

固定操作顺序的用例可加 `expected_trajectory`，按工具名核对顺序、禁用项和最大调用次数。中断后区分未知动作和人工确认已执行的动作。用报告的 `provenance` 对齐用例指纹、Runtime 和浏览器版本，再比较结果。工具轨迹只证明调用过程，业务结果继续看产物验收。
