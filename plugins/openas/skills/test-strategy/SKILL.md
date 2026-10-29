---
name: test-strategy
description: "依据需求和风险制定测试层级、场景、数据与执行计划；用于功能或系统测试规划，不代替具体测试实现或最终验收。 / Plan risk-based test levels, scenarios, data, environments, and execution with acceptance mappings; do not confuse a test plan with implemented tests or final acceptance."
---

中文 | [English](SKILL.en.md)

语言 / Language: 按用户指定语言回复，否则跟随任务语言；编辑已有内容保留原语言。Honor explicit output language, otherwise follow the task language; preserve existing artifact language unless translation is requested. Keep machine-readable identifiers unchanged. See [语言约定 / language policy](../../references/language.md).

涉及事实回答、测试、评审或完成结论时，先读取并遵循 [结论与证据共享规则](../../references/evidence-policy.md)。

# 测试策略

输入包括原始需求与验收、实际接口和变更范围、已有测试、执行环境与资源限制。按 [项目适配约定](../../references/project-context.md) 确认项目，不默认采用某种框架。

## 从风险选择场景

将需求 ID 对应到可观察行为与失败影响。按实际风险选择正常、边界、非法输入、错误恢复、兼容或跨模块场景；只在涉及共享状态、时序或持久化时增加对应检查。区分已有覆盖、需要新增和无法验证，不以测试数量或行覆盖率代替行为覆盖。

优先在最小且可信的层级验证行为：纯逻辑用单元测试，边界契约用集成测试，关键用户路径用必要的端到端测试。避免在每一层重复所有断言；说明 mock 隐藏了哪些真实依赖行为。没有测试基础设施时，先给最小可执行方案，不默认引入大型框架。

## 数据、环境与执行

明确测试预言来自需求、规范还是可信参考，不直接复制实现结果。为关键场景定义输入、前置状态、动作、预期输出与副作用、清理方式和证据。记录数据来源与脱敏要求，避免依赖共享生产数据。

根据依赖和成本安排快速反馈、集成回归及必要长任务；记录环境差异、阻碍与停止条件。必需验收缺环境时标为未验证，不能用跳过或 mock 通过代替。已有检查通过后，仅因新修改或未覆盖风险扩大测试。

## 交付与核对

交付测试矩阵：需求/风险、场景、层级、数据与环境、现有或新增测试位置、执行入口、通过标准、覆盖缺口。规划完成表示关键验收均有验证方法或明确缺口，不表示已运行通过。

编写跨模块测试时使用 [integration-testing](../integration-testing/SKILL.md)，行为开发可用 [test-driven-development](../test-driven-development/SKILL.md)，交付证据使用 [verification-before-completion](../verification-before-completion/SKILL.md)。测试工程由 [test-engineer](../../agents/test-engineer.md) 承担，独立验收由 verifier 核对。
