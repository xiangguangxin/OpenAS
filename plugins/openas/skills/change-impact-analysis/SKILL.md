---
name: change-impact-analysis
description: "围绕拟议变更或实际 diff 追踪调用方、接口、数据、配置、构建、测试和文档的影响，明确兼容风险、必要联动及验证范围；用于修改前影响分析或变更范围核对，不自动实施修改或代替代码评审。 / Trace proposed changes or diffs through consumers, contracts, data, configuration, builds, tests, and documentation to identify compatibility risks and verification scope."
---

中文 | [English](SKILL.en.md)

语言 / Language: 按用户指定语言回复，否则跟随任务语言；编辑已有内容保留原语言。Honor explicit output language, otherwise follow the task language; preserve existing artifact language unless translation is requested. Keep machine-readable identifiers unchanged. See [语言约定 / language policy](../../references/language.md).

# 变更影响分析

确认原始目标、当前与目标行为、变更基线及允许范围；分析实际 diff 时明确比较的提交或工作区状态，分析尚未实施的方案时区分拟议位置与已存在代码。缺少系统现状且影响跨模块时按需使用 [codebase-analysis](../codebase-analysis/SKILL.md)，不要求每次修改先做全仓分析。默认只读。

## 从变更点向两侧追踪

列出改变的公共行为、符号、配置、数据格式或构建输入，分别追踪其依赖和消费者。除直接调用方外，按实际机制检查再导出、继承、注册、动态加载、配置注入、生成产物及外部协议；文本命中只是候选，需要结合真实路径确认关联。动态边界不可解析时记录不确定性，不把零搜索结果当作没有影响。

按与本次变更的关系覆盖：

- 公共接口、返回值、错误、默认值、单位及支持版本是否变化；谁依赖旧语义。
- 数据所有权、持久格式、状态转换、资源生命周期及相关失败恢复是否受影响。
- 构建脚本、依赖、配置、部署和生成入口是否需要同步调整。
- 测试预期、夹具、示例、文档和相关验收是否需要更新；避免只修改断言来迎合新实现。

区分必须联动、需要验证、待确认及有证据不受影响的对象，并给出传播路径或行为依据。发现已超出授权范围的必要依赖时标明阻断及所需决定，不自动改写外部消费者。只读任务仍可交付完整影响报告。

## 将风险转为验证与实施边界

对每项关键风险给出触发条件、实际影响、对应消费者和验证方式。优先复用已有测试，并说明哪些受影响行为尚无覆盖；按影响选择检查，不因改动行数少就忽略公共默认值变化，也不因跨文件就机械扩大为全量测试。

兼容性取决于实际消费者与支持约束，不能仅由类型检查或编译通过推断。涉及跨版本、不可逆数据或长期迁移时交给 [architecture-evolution](../architecture-evolution/SKILL.md)；需要实施任务时用 [writing-plans](../writing-plans/SKILL.md) 整理依赖和开始条件，不把影响报告当作已经完成实现或验证。

交付基线与变更摘要、影响清单（对象、传播证据、联动或验证动作）、兼容风险、建议改动范围、验收检查及未知项。实际代码正确性评审使用 [requesting-code-review](../requesting-code-review/SKILL.md)。变更修订后核对新增或失效的影响结论，未执行的检查保持未验证。
