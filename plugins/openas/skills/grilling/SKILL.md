---
name: grilling
description: "用户明确希望通过采访、连续追问或设计压力测试澄清关键取舍时使用。普通代码审查、项目评审和已经明确的实施任务使用对应评审或开发流程。 / Use explicit interviews or design pressure testing to clarify major tradeoffs; do not turn ordinary reviews or clear implementation requests into interviews."
---

中文 | [English](SKILL.en.md)

语言 / Language: 按用户指定语言回复，否则跟随任务语言；编辑已有内容保留原语言。Honor explicit output language, otherwise follow the task language; preserve existing artifact language unless translation is requested. Keep machine-readable identifiers unchanged. See [语言约定 / language policy](../../references/language.md).

涉及事实回答、测试、评审或完成结论时，先读取并遵循 [结论与证据共享规则](../../references/evidence-policy.md)。

# 设计压力测试

帮助用户识别隐藏假设、比较关键取舍，并形成足够支持下一步的设计。先读取可获得的代码和文档，复用会话中已经确认的决定。

## 何时使用

用户明确要求深入追问、采访或对设计逐步推演时，组织有依赖顺序的问题。普通“评审一下这个项目”应直接调查并给出发现，不自动转成采访。已经授权的明确实施任务继续执行；本技能不增加额外确认流程。

## 讨论方法

- 先列目标、约束、已知事实和最有影响的不确定项；事实自行查证，只询问无法从现有材料确定的用户选择。
- 优先讨论会改变架构、兼容性、成本或交付范围的决定，不展开与当前任务无关的所有分支。
- 一轮集中提出少量可回答的问题，给出选择、推荐及取舍；依赖尚未确定的问题留到后续。
- 每轮更新已经确定的决定和被排除的分支。可在合理假设下继续分析的内容不因等待回答而停止。

## 完成与交接

当关键风险与取舍已足够清楚，或用户要求结束讨论时，给出推荐方案、依据、尚存假设和后续行动。无需声称已遍历所有设计可能，也不要求再次确认已经明确的决定。

仅请求评审时保持只读。用户已要求实现时按现有授权推进；提交、推送、部署等操作遵循任务本身的授权范围。
