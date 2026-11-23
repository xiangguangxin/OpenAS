---
name: spec-driven-development
description: "为跨模块功能或已交付系统变更维护可测试规格、能力边界和需求到验收的追踪；用于规格缺失、歧义或漂移，不为小修复强制新增文档或重复审批。 / Maintain testable specifications and trace requirements through implementation and acceptance for significant changes without imposing paperwork on small fixes."
---

中文 | [English](SKILL.en.md)

遵循[语言约定](../../references/language.md)、[证据规则](../../references/evidence-policy.md)和[实施就绪](../../references/implementation-readiness.md)。沿用项目已有规格系统和用户授权。

# 规格驱动开发

先读取当前需求、代码和有效决定。已有 OpenSpec、RFC 或设计文档时在原位置维护，不建立竞争的事实源。局部明确修复只需在任务中保留输入、预期结果和验证，不强制创建完整规格。

1. 若目标含多个可独立验收的能力，先列能力 ID、职责、消费者、依赖与接口归属；消除循环依赖后按边界分别写规格。单一能力跳过此表。
2. 使用[规格模板](references/spec-template.md)记录目标/非目标、当前/预期行为、输入输出和失败状态、兼容要求、真实构建检查入口与可测试标准。未知标明影响及关闭证据；架构可行性未知先交给 [decision-mapping](../decision-mapping/SKILL.md) 或研究。
3. 为需求分配稳定 ID，建立 `需求 → 能力/模块 → 任务 → 检查 → 当前证据` 的映射。规格负责行为契约；局部函数组织留给实现者。计划使用 [writing-plans](../writing-plans/SKILL.md)，不得用描述性规格冒充执行证据。
4. 按风险核对就绪和确需用户决定的取舍；已有充分授权和明确契约时继续实施，不强制每阶段结束会话或重复审批。仅要求设计时交付设计，不自动编码。
5. 已交付功能变化建立增量记录：引用有效基线、只描述行为差异、迁移/回退、回归与新增验收。实现中出现新点子放入延期区；正式调整范围后再进入当前任务。交付后用实际结果更新现状并标记增量已实施，保留历史。

验收使用 [acceptance-tracking](../acceptance-tracking/SKILL.md)，逐项区分通过、失败、未运行和阻断。规格、代码或检查变化后重新核对映射与证据。例如新增导入预览必须明确预览是否写库、无效行如何呈现、确认时如何防止重复导入。

来源见[方法来源](../../references/skill-methods/NOTICE.md)。
