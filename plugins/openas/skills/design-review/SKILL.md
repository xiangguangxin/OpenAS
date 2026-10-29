---
name: design-review
description: "交叉评审需求、调研、技术决策和架构的一致性、可行性与可验收性，输出有依据的问题和设计就绪结论；用于实施前设计检查，不冒充代码或运行验收。 / Review consistency, feasibility, and acceptance across requirements, research, technical decisions, and architecture before implementation; report evidenced readiness gaps."
---

中文 | [English](SKILL.en.md)

语言 / Language: 按用户指定语言回复，否则跟随任务语言；编辑已有内容保留原语言。Honor explicit output language, otherwise follow the task language; preserve existing artifact language unless translation is requested. Keep machine-readable identifiers unchanged. See [语言约定 / language policy](../../references/language.md).

涉及事实回答、测试、评审或完成结论时，先读取并遵循 [结论与证据共享规则](../../references/evidence-policy.md)。

# 设计评审与实施就绪检查

读取实际产物及版本：市场/竞品证据、需求、方案、选型 ADR、架构、接口与验收。按本次范围评审，不因缺少不适用的模板章节判失败；用户只要求评审时保持只读。

## 交叉核对

- 关键需求是否对应设计、接口和验证方法，非目标是否被偷偷实现？
- 推荐技术是否满足硬约束，关键证据是否有来源、版本和适用条件？
- 模块、数据所有权、接口、图和部署说明是否一致？失败、边界、权限和恢复是否覆盖实际风险？
- 假设、性能目标和 PoC 计划是否被误写成已验证事实？
- 未决项是否影响后续实施，关键任务能否在现有资源与依赖下开始？

缺陷写明稳定 ID、位置、违反的需求/约束、具体反例或影响、建议责任阶段和关闭证据。只报告有依据的问题，不为了凑数量制造问题；证据不足时标待确认，不把措辞偏好升级成阻断缺陷。

## 实施就绪门槛

依据 [设计粒度与实施就绪](../../references/implementation-readiness.md) 检查：关键产品与契约决策有无阻断未决项、关键验收是否对应实现模块及验证方法、当前任务依赖是否满足。复述实现路径与失败行为，报告会导致合理实现互不兼容的具体歧义；不因缺少私有函数设计或文档页数不足阻断。

可逆局部选择交给 developer，可行性未知回交研究或 PoC。仅部分可实施时明确限定范围与进入其余部分的条件，不将整个产品实现宣布就绪。结论沿用宿主现有字段与 verdict。

## 回交与结论

将问题回交到需求、调研、选型或架构阶段；修订后核对原问题及受影响的关联项，保留接受风险的实际决定，不替用户批准产品取舍。只读评审不自行修订文件或启动模型团队。

交付覆盖范围、问题列表、未验证项和就绪结论：有阻断问题则不就绪；允许有限范围先行时明确可开始部分及条件；无发现只表示本轮范围内未发现阻断项。设计评审通过不等于代码通过测试、产品需求得到市场验证或获准发布。

跨阶段协作可用 [acceptance-tracking](../acceptance-tracking/SKILL.md) 追踪证据，阶段版本与回交遵循 [完整流程](../solution-design/references/research-to-design.md)。
