---
name: executing-plans
description: "按已有计划分步实施并验证，处理依赖和反馈；用于设计足够明确、需要持续落地的任务。 / Implement and verify an existing sufficiently clear plan step by step, respecting dependencies, scope, feedback, and evidence."
---

中文 | [English](SKILL.en.md)

语言 / Language: 按用户指定语言回复，否则跟随任务语言；编辑已有内容保留原语言。Honor explicit output language, otherwise follow the task language; preserve existing artifact language unless translation is requested. Keep machine-readable identifiers unchanged. See [语言约定 / language policy](../../references/language.md).

涉及事实回答、测试、评审或完成结论时，先读取并遵循 [结论与证据共享规则](../../references/evidence-policy.md)。

# 执行计划

先核对原始验收、当前分支和起始 diff，保留已有修改。复用已经确定的设计；先完成无外部阻碍的任务，不为常规实现选择重复请示。

按依赖选择下一项工作，定位实际文件与调用方后修改，再用目标项目已有检查确认本步行为。构建、缓存和临时输出沿用项目约定，不让生成文件混入源码变更。纯文档任务使用来源、链接与格式检查，无需制造编译步骤。

检查失败时保留命令、目录、退出码和关键输出，区分实现失败、环境缺失与验收错误。回到相应任务修复，不通过删测试、放宽断言或跳过门禁宣称完成。

发现计划与当前事实不符时说明差异：已授权范围内调整步骤；涉及新的产品取舍、不可逆操作或范围外修改时先准备可评审的方案，再请求所缺决定。相互依赖或写同一文件的任务顺序执行。

每步完成记录行为变化、相关证据和剩余项。已有检查通过后，无新变化不重复无关全量回归。所有原始验收有证据或明确列出未完成条件后再交付。
