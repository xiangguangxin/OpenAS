---
name: writing-plans
description: "将足够明确的设计拆为可执行任务，保留范围、依赖、项目约束和验收；用于实现前规划或复杂任务交接。 / Turn sufficiently clear design into executable, dependency-aware tasks with scope, project constraints, and acceptance; separate blockers from implementable work."
---

中文 | [English](SKILL.en.md)

语言 / Language: 按用户指定语言回复，否则跟随任务语言；编辑已有内容保留原语言。Honor explicit output language, otherwise follow the task language; preserve existing artifact language unless translation is requested. Keep machine-readable identifiers unchanged. See [语言约定 / language policy](../../references/language.md).

涉及事实回答、测试、评审或完成结论时，先读取并遵循 [结论与证据共享规则](../../references/evidence-policy.md)。

# 实施计划

从用户目标、现有实现和已经确认的决定出发，不为已授权的常规技术选择重新索要批准。先按 [项目适配约定](../../references/project-context.md) 查明相关路径与检查入口。

按 [设计粒度与实施就绪](../../references/implementation-readiness.md) 先区分可实施范围与阻断未知；不满足条件的部分先拆研究或 PoC，不将架构猜测藏进实现任务。以一个可验证的行为或内聚变更拆分，不按固定行数、时长或逐个辅助函数切分。

每项任务至少写清：要改变的行为、实际文件或模块、依赖的上游结果、实现要点，以及能证明完成的检查。复杂任务补充顺序、并行文件归属、兼容性与失败处理；小任务不套大型模板。

例如“导入时处理重复记录”：先确认识别规则与期望结果，再修改已有导入入口与测试，覆盖正常、重复和无效输入。使用项目已有命令，不假设语言、目录或测试框架。

将必须由用户决定的范围取舍与可自行处理的实现细节分开。依赖未满足、检查不可执行时列出具体影响；不要用“完成开发并测试”代替可检查的任务。交接保留原始验收和仍未解决的问题。
