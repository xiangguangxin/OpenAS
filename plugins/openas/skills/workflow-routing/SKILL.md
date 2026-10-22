---
name: workflow-routing
description: 根据任务目标、风险和依赖选择直接实现、调试、只读评审、文档或完整开发流程；用于决定怎样执行，不代替领域分析。
---

# 选择工作流

先读原始目标和 [项目适配约定](../../references/project-context.md)，复用已有授权与决定。按产物和风险选择最小足够流程：

| 任务 | 建议路线 | 必要边界 |
| --- | --- | --- |
| 小范围、验收明确的修改 | direct | 实现 → 宿主检查 → 验证 |
| 新功能、跨模块或兼容性变化 | development | 设计 → 设计评审 → 必要文档 → 实现 → 评审 → 检查与验证 |
| 已有故障 | repair | 完整闭环，并保留失败基线；定位方法用 bug-fix |
| 仅审查项目或 diff | review | 只读评审；发现问题仍可交付评审，但不称目标代码已通过验收 |
| 仅整理或修改文档 | documentation | 文档 → 评审 → 对应检查与验证 |

Codex 适配器通过任务 JSON 的 `workflow` 显式选择路线，省略时保持 development。不靠关键词猜测授权；direct 也必须有实际验收，不能用来绕开已要求的评审。只有明确需要采访时使用 grilling。

输出选择、理由、所需产物、实际检查和缺少的条件。简单任务无需生成图或启动团队。多任务依赖交给 [task-orchestration](../task-orchestration/SKILL.md)；路线与执行器边界见 [运行指南](../../workflows/README.md)。
