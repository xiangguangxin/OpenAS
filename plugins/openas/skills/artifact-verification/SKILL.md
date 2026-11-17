---
name: artifact-verification
description: "独立验收 Agent 生成、导出或下载的报告和文件，检查产物是否来自本次任务、结构化结果和逐项失败原因。 / Independently verify freshness, structured results, and per-criterion evidence for generated, exported, or downloaded artifacts."
---

中文 | [English](SKILL.en.md)

遵循[语言约定](../../references/language.md)和[结论与证据共享规则](../../references/evidence-policy.md)。

# 产物验收

1. 在执行前从原目标提取验收条件、产物路径、格式和预期值。优先使用本次任务独有的输出目录，或在原路径保存执行前的内容指纹。应用能写入运行 ID 时，将报告内的 ID 与本次运行匹配。
2. 为每项条件选用独立检查。使用格式解析器检查内容，优先核对构建标识、测试结果、指标和实际数值。拦截旧报告、不可解析的文件、错误来源和错误字段。只有用户明确只要求存在或可读取时才采用相应的最小检查。
3. 在 GUI Runtime 中配置[产物验收器](../../integrations/computer-use/RUNTIME.md#产物验收)，在首次 `run` 前开启 `fresh`，`resume` 沿用同一份配置。用 `openas-gui verify` 单独复核。独立检查可以拒绝模型报告的完成状态。
4. 交付逐项验收结果、使用的规则、版本和仍无法证明的条件。若要证明整个开发任务已满足原始需求，结合 [acceptance-tracking](../acceptance-tracking/SKILL.md) 和 [verification-before-completion](../verification-before-completion/SKILL.md)。

覆盖率示例中，在本次任务的目录获取报告，并核对测试结果为通过、采样的构建已插桩、指标为 MC/DC。判断覆盖是否达标需要再检查对应的计数和阈值。
