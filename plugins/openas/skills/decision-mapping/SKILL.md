---
name: decision-mapping
description: "将跨会话、关键决定尚未明确的复杂目标组织为决策地图、阻塞关系和证据记录；用于逐步消除方案未知，不替代明确任务的实施计划或自动创建远程 Issue。 / Map unresolved decisions for large ambiguous goals across sessions; track evidence and dependencies without automatically implementing or publishing issues."
---

中文 | [English](SKILL.en.md)

遵循[语言约定](../../references/language.md)、[证据规则](../../references/evidence-policy.md)与[项目适配](../../references/project-context.md)。复用已有目标和授权，仅对真正影响范围或高代价取舍的未知提问。

# 决策地图

先写清目标终点、非目标、现有决定和阻断未知。若路径已明确，直接交给 [writing-plans](../writing-plans/SKILL.md)，不额外建立地图。地图解决“需要决定什么”，实施任务解决“如何交付已决定的行为”。

## 建立和推进地图

使用项目已有 RFC/ADR/任务位置；没有约定时建议 `docs/decisions/<goal>/map.md`，仅在任务允许保存时写入。采用[模板](references/map-template.md)。为问题分配稳定 ID、标题、类型（research/prototype/decision/prerequisite）、依赖、负责人、状态、关闭条件与证据链接。边指向前置问题；检查缺失依赖和环。不能精确表述的问题保留在待明确区，不提前编造实现任务。

每轮选择依赖已关闭且未被认领的问题，先检查证据是否仍适用。研究调用 [technical-research](../technical-research/SKILL.md)，低成本实验记录假设和停止条件；涉及用户产品决定时保留真人答复，不代答。可自行处理的局部可逆选择由执行者决定。无需为了“一轮一张票”中断已获授权的连续工作。

关闭问题时保存结论、理由、证据与影响；地图仅保留摘要和详情链接。新证据推翻决定时标记 superseded 并重开受影响项，不能删除历史或继续消费旧结论。未知变清楚后再新增问题；超出目标的项放入非目标区。远程 Issue 的创建、评论、分配或关闭须在既有授权范围内；无跟踪器时使用本地记录，不安装服务。

## 交接与停止

交付目标、已决定事项、当前可推进项、阻断、证据和下一步。达到终点或预算/工具阻断时停止并说明缺口，地图清晰不代表实现完成。跨会话交给 [context-handoff](../context-handoff/SKILL.md)；决定就绪后交给实施计划。并行仍需宿主支持、资源独立与已有授权。

例如“将单机工作流扩展到团队”：先明确状态归属、凭据边界、冲突处理，再拆功能；“修复已复现的空输入错误”无需地图。

来源与适配范围见[方法来源](../../references/skill-methods/NOTICE.md)。
