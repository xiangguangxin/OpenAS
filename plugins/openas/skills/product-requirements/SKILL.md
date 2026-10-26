---
name: product-requirements
description: "将用户问题、调研与业务约束转成产品简报或 PRD，定义范围、用户流程、可检验需求与成功指标；用于需求定稿，不代替技术选型或架构设计。 / Turn user problems, research, and constraints into a brief or PRD with scope, user flows, testable requirements, and success metrics; keep technology decisions separate."
---

中文 | [English](SKILL.en.md)

语言 / Language: 按用户指定语言回复，否则跟随任务语言；编辑已有内容保留原语言。Honor explicit output language, otherwise follow the task language; preserve existing artifact language unless translation is requested. Keep machine-readable identifiers unchanged. See [语言约定 / language policy](../../references/language.md).

# 产品简报与需求规格

读取已有调研、用户决定和项目约束。按协作需要选择简短产品简报或 PRD，不强制小任务写长篇文档；保留用户指定格式和路径。输入很薄时先形成带假设标记的草案，仅对影响范围的关键缺口提问。

## 把问题转成可验收需求

定义目标用户、问题、价值、目标与非目标；描述核心用户流程及错误/边界状态。每项需求用稳定 ID，包含触发条件、输入/前提、期望行为和可检查的完成条件；避免“支持高性能”“体验友好”等不可验证措辞。

将用户确认的需求、研究推断和建议分别标记，关联来源。为非功能要求给出场景、指标、阈值与测量方法；没有依据的数字保留为建议目标，不写成已达成性能。

区分产品成功指标与开发完成检查：成功指标写基线、目标、测量方式和观察窗口，未知项标待确认。按价值与依赖确定 MVP 和排除范围；多阶段排序交给 [roadmap-planning](../roadmap-planning/SKILL.md)。

## 交接契约

产物包含背景与来源、用户/流程、功能及质量需求、范围与优先级、约束、依赖、验收、假设与未决项。冲突按原始来源和用户最新决定处理，不能默默折中。

PRD 描述要达到的行为，已有指定技术作为约束保留，其他技术决定交给 [technology-selection](../technology-selection/SKILL.md)。需求有新增或删除时记录受影响 ID，通知下游更新；文档草案不代表需求已批准。
