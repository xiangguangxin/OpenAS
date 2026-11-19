---
name: workflow-routing
description: "按任务类别、范围与风险选择最小技能组合和轻/标准/重流程；用于新功能、修 Bug、重构评估、文档汇报的入口选择，不授予工具或生产操作权限。 / Select minimal skill bundles and light/standard/heavy rigor for features, bug fixes, refactoring, or documents from explicit scope and risk."
---

中文 | [English](SKILL.en.md)

遵循[语言约定](../../references/language.md)、[证据规则](../../references/evidence-policy.md)与[项目适配](../../references/project-context.md)。复用已有授权，不用关键词猜测生产操作权限。

# 先选组合，再选强度

| 高频任务 | 默认最小组合 | 按条件补充 |
| --- | --- | --- |
| 新功能开发 | solution-design → test-driven-development → verification-before-completion | 跨模块加设计/代码评审；接口变化加影响分析 |
| 已有 Bug | bug-fix → verification-before-completion | 线上事故、认证/数据问题升重；先确认失败基线 |
| 重构与影响评估 | change-impact-analysis → code-simplification → verification-before-completion | 架构边界变化加 architecture-conformance 与设计评审 |
| 文档/汇报 | project-documentation → verification-before-completion | 标准级加 document-review；仅特定载体启用 Office、图表或 PDF 技能 |

默认不加载其他技能。完整机器清单在 [task-routing.json](../../references/task-routing.json)，每个技能记录 owner、类别、core/conditional/specialized 与触发条件。只读评估直接交付报告，不自动进入修改路线。

## 根据风险选择 Tiered Rigor

- **light**：明确、单文件、无已知敏感风险。保留范围、真实命令、目录、退出码与对象指纹；Bug 还需失败基线。跳过单独设计稿、模型评审和独立验收会话，不把宿主自检称独立评审。
- **standard**：多文件/模块、风险未知或 Office/浏览器/桌面载体。保留适用设计、独立评审与验收；不强制无关产物。
- **heavy**：认证/权限、公共接口、持久数据迁移、生产事故、核心性能、并发或大范围修改。增加影响分析、设计评审及适用的安全/性能评审，不能用 light 绕过。

风险信息缺失按 standard；显式 `risk_factors: []` 只表示调用方确认没有列出的风险，不是自动证明安全。声明与真实 diff 不符时重新分级；机器检查不能从所有代码自动推断风险。用户明确要求更严格流程时保留，不擅自降级。

```bash
python3 /path/to/OpenAS/plugins/openas/workflows/task_router.py --task task.json
```

任务字段：`task_kind` 为 feature/bugfix/refactor/documentation，`rigor` 为 auto/light/standard/heavy；提供实际 `scope`、`risk_factors`、可选 `module_count` 与 `carrier`。执行器的任务还需 requirement、acceptance、checks 及逐项 `acceptance_checks`。规划命令只返回建议，不执行任务或安装工具。

Codex 适配器对含 `rigor` 的任务执行分级门禁；缺少该字段时保持旧路线，省略 workflow 仍为 development。新分级任务的显式 workflow 必须与规划结果一致。使用 [运行指南](../../workflows/README.md) 中的原有命令执行；不凭任务标签增加授权。

<details>
<summary>仅在特定风险或载体下启用</summary>

- security → security-review；performance-critical → performance-analysis；production-incident → incident-response。
- Office → [office](../office/SKILL.md)；浏览器 → [browser-goal-executor](../browser-goal-executor/SKILL.md)；桌面 → [gui-goal-executor](../gui-goal-executor/SKILL.md)；图形 → [technical-diagrams](../technical-diagrams/SKILL.md)。
- 技术/市场/架构专项：technical-research、market-research、product-requirements、technology-selection、architecture-design、architecture-evolution；完整前期链使用 research-design。
- 只读 review/security-review、环境 operations、任务图 task-orchestration、已有 PR 反馈 pr-review-feedback 等保留原有入口，不套用新的四类修改任务以扩大范围。
- 技能维护用 skill-maintenance；记忆提炼用 project-memory。它们不是所有小任务的收尾必选项。

</details>

输出：选中的组合、强度与理由、实际检查、结果与未覆盖项。简单任务无需团队或图；复杂依赖才用 [task-orchestration](../task-orchestration/SKILL.md)。
