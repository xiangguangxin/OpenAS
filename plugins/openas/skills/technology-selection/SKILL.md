---
name: technology-selection
description: "依据需求和硬约束比较语言、框架、存储、通信及部署路线，输出有证据的技术选型与 ADR；用于决定用什么和为什么，不用技术栈清单代替架构。 / Compare feasible technology routes against requirements and hard constraints, preserving evidence, tradeoffs, PoC uncertainty, and architecture decision records."
---

中文 | [English](SKILL.en.md)

语言 / Language: 按用户指定语言回复，否则跟随任务语言；编辑已有内容保留原语言。Honor explicit output language, otherwise follow the task language; preserve existing artifact language unless translation is requested. Keep machine-readable identifiers unchanged. See [语言约定 / language policy](../../references/language.md).

# 技术路线选择

输入是产品需求、质量要求、现有系统与资源边界。尊重已指定技术，只对需要决策的部分比较；用户未要求重新选型时不推翻已有路线。

## 对齐候选与证据

将硬约束与偏好分开。先检查部署可用性、接口兼容、数据要求、许可证使用条件及团队维护能力，再比较集成/运维成本、性能、生态、升级和退出难度。保留现有方案或最简单可行方案作为基线；只比较真实可行候选。

需要当前版本、维护状态、价格或产品支持信息时使用 [technical-research](../technical-research/SKILL.md) 核对官方资料。每个关键维度保留来源、版本、条件和未知；相同功能不代表相同性能，未知不按零分处理。

若用评分，说明权重依据及敏感性，不能让总分覆盖硬约束失败。推荐需解释优势在哪些条件下成立、放弃了什么，以及什么新证据会改变决定。

## 关键未知用实验回答

针对可能推翻推荐的假设设计最小 PoC：对照方案、相同输入/环境、指标与阈值、资源上限和停止条件。仅执行已授权实验；记录命令、版本和结果。未运行时明确为实验计划，不把建议当实测。

输出选型矩阵、推荐路线、成本/限制、验证与未知，以及 ADR：状态、背景、备选、决定、理由、后果、重新评估条件。需要审批的决定保持待定，不伪造批准人或日期。

将选定技术及边界条件交给 [architecture-design](../architecture-design/SKILL.md)。技术路线无法满足需求时回交需求/方案，不能靠架构措辞掩盖不可行性。

需要库文档证据时按需参考 [Context7 MCP 指引](../../integrations/context7/README.md)，核对库身份和目标版本，检索结果不作为实测收益。
