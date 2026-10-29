---
name: solution-design
description: "形成解决问题的候选方案与取舍，或串联市场调研、需求、技术选型、架构及设计文档的完整流程；具体选型与架构使用相应专门技能，不默认进入开发。 / Compare solution alternatives and tradeoffs or coordinate research, requirements, selection, architecture, and design documentation without automatically starting development."
---

中文 | [English](SKILL.en.md)

语言 / Language: 按用户指定语言回复，否则跟随任务语言；编辑已有内容保留原语言。Honor explicit output language, otherwise follow the task language; preserve existing artifact language unless translation is requested. Keep machine-readable identifiers unchanged. See [语言约定 / language policy](../../references/language.md).

涉及事实回答、测试、评审或完成结论时，先读取并遵循 [结论与证据共享规则](../../references/evidence-policy.md)。

# 方案设计与完整设计流程

从用户目标、[当前项目](../../references/project-context.md) 和已确认约束出发。区分问题、需求和解法，保留用户指定技术与产品决定；已有明确输入时直接形成足够评审的方案，不重复采访。

## 形成解决方案

写清目标用户、问题、目标与非目标、核心流程、功能边界、质量要求和验收。需求需要正式交接时用 [product-requirements](../product-requirements/SKILL.md)。以当前方式或最简单可行方式为基线，比较有实质差异的解决路径，不凑候选数量。

先排除不满足硬约束的方案，再比较用户价值、可行性、交付/维护成本、风险和退出难度。保留证据与假设，推荐说明成立条件、代价及可能改变结论的未知；小任务可只解释一个可行方案。

## 控制设计粒度

按 [设计粒度与实施就绪](../../references/implementation-readiness.md) 决定所需深度：优先确定跨模块边界和失败行为，局部可逆细节交给开发者。会影响可行性的未知先形成研究或 PoC，不以模糊措辞直接交给产品实现。

## 按任务需要交接

- 完整链路或从零设计：读取 [市场调研到设计文档](references/research-to-design.md)，核对各阶段输入与产物，复用已有有效成果。
- 市场机会与竞品：[market-research](../market-research/SKILL.md) 与 [competitive-analysis](../competitive-analysis/SKILL.md)。
- 技术事实与选型：[technical-research](../technical-research/SKILL.md) 与 [technology-selection](../technology-selection/SKILL.md)。
- 系统设计：[architecture-design](../architecture-design/SKILL.md)。
- 实施前核对与整理：[design-review](../design-review/SKILL.md) 与 [project-documentation](../project-documentation/SKILL.md)。

方案产物沿用项目 RFC/设计说明位置，保留状态、候选、理由、取舍、风险和下一步。没有代码的新项目以需求和拟议设计为来源。只需某一阶段时不加载整套方法；完整设计默认交付到文档，不自动实现。需要排期用 [roadmap-planning](../roadmap-planning/SKILL.md)，已授权实施时才交给 [writing-plans](../writing-plans/SKILL.md)。

需要专用自动执行时使用 Codex 适配器 `workflow: research-design`，任务示例和命令见 [运行指南](../../workflows/README.md)。普通 `/openas:solution-design` 调用仍是技能入口，不会自行启动外部进程；任务具备目标工作区、输入、范围和检查命令后才执行可信任务 JSON。
