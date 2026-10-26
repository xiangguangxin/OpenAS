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
| 认证、权限或敏感数据专项评审 | security-review | security-reviewer 只读检查实际文件和信任边界，不自动修复 |
| 环境、CI 或部署配置修改 | operations | it 仅修改任务声明的工作区文件，经评审、宿主检查和验证；不操作在线环境 |
| 市场调研至完整设计交付 | research-design | 调研 → 需求 → 方案 → 选型 → 架构 → 文档 → 评审回交 → 检查与验证 |
| 仅整理或修改文档 | documentation | 文档 → 评审 → 对应检查与验证 |

Codex 适配器通过任务 JSON 的 `workflow` 显式选择路线，省略时保持 development。不靠关键词猜测授权；direct 也必须有实际验收，不能用来绕开已要求的评审。只有明确需要采访时使用 grilling。

输出选择、理由、所需产物、实际检查和缺少的条件。简单任务无需生成图或启动团队。多任务依赖交给 [task-orchestration](../task-orchestration/SKILL.md)；路线与执行器边界见 [运行指南](../../workflows/README.md)。

调研与规划先选择领域技能：[技术调研](../technical-research/SKILL.md)、[方案设计](../solution-design/SKILL.md)、[竞品分析](../competitive-analysis/SKILL.md)、[路线图](../roadmap-planning/SKILL.md)。编写或润色文档使用 [project-documentation](../project-documentation/SKILL.md)。这些领域技能不各自新增执行器路线；仅调查不修改仓库时直接交付报告，需写入文档时可走 documentation，不默认进入代码实现。

用户要求“市场竞品调研 → 方案 → 技术路线 → 架构 → 设计文档”时使用 [完整设计流程](../solution-design/references/research-to-design.md)，复用已有产物；路线图规划用于需要阶段排期的任务，不代替技术路线选型。

细分前期任务：市场机会用 [market-research](../market-research/SKILL.md)，PRD 用 [product-requirements](../product-requirements/SKILL.md)，选型用 [technology-selection](../technology-selection/SKILL.md)，架构用 [architecture-design](../architecture-design/SKILL.md)，实施前设计评审用 [design-review](../design-review/SKILL.md)。完整链路可使用 `research-design` 专用路线，阶段单独调用仍为技能方法。

实施后检查架构边界、依赖和契约偏差使用 [architecture-conformance](../architecture-conformance/SKILL.md)，只读任务沿用 review 路线；已有系统分阶段改造规划使用 [architecture-evolution](../architecture-evolution/SKILL.md)，只写方案时沿用 documentation，实施需按已有授权选择对应路线。两者不新增执行器路线。
