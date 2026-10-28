# DSH 技能方法来源 / DSH skill-method provenance

Reviewed: 2026-10-28. Upstream: deepseek-ai/deepseek-harness. Pinned commit: `f3803c96974ad4a94195fb97e5c637e9c2a3afe3`.

| OpenAS | Upstream skill at the reviewed commit | Source SHA-256 |
| --- | --- | --- |
| agent-experience | [packages/preset/agent-preset/skills/agent-experience/SKILL.md](https://github.com/deepseek-ai/deepseek-harness/blob/f3803c96974ad4a94195fb97e5c637e9c2a3afe3/packages/preset/agent-preset/skills/agent-experience/SKILL.md) | `1244928710cb7e399325c416e80312037d4da249559a09fe289515cc66ee1752` |
| code-simplification | [.agents/skills/dsh-find-simplifications/SKILL.md](https://github.com/deepseek-ai/deepseek-harness/blob/f3803c96974ad4a94195fb97e5c637e9c2a3afe3/.agents/skills/dsh-find-simplifications/SKILL.md) | `0287165e16f482bc197bc36a40e66a2eee3d47479bb0dfc1836602a96052befe` |

## 中文

两项技能基于上述固定版本的方法重新组织并改写，保留 DeepSeek 的 [MIT 许可与版权声明](licenses/deepseek-harness-MIT.txt)。对应 [上游许可](https://github.com/deepseek-ai/deepseek-harness/blob/f3803c96974ad4a94195fb97e5c637e9c2a3afe3/LICENSE) 已核对；此次未复制脚本、依赖或上游参考资料。

- agent-experience 采用渐进披露、可检索入口、操作前约束、有限输出和总工作量评估；补充 OpenAS 的宿主能力边界、交接路由、正反触发场景和测量限制。
- code-simplification 采用维护责任净减少、生产者/消费者证据、最强保留理由、完整替换成本和状态/生命周期约束；补充通用配置优先级、动态加载、只读调查与授权实施的区分，以及 OpenAS 的演进/影响分析路由。
- 未移植 DSH 的固定架构保护项、Cordis 目录、Agent Notes 制度、仓库命令、分支/PR 流程或自动多 Agent 分工。这些是上游项目约定，不能成为其他项目的通用要求。正文不是上游工具注册或运行时能力的实现。

本记录保存来源与适配范围，不代表真实客户端已发现技能、行为已通过评测或 token 已减少。实际验证范围在本次变更的验证记录中单独报告。

## English

Both skills reorganize and adapt methods from the pinned sources above, retaining DeepSeek's [MIT license and copyright notice](licenses/deepseek-harness-MIT.txt). The [upstream license](https://github.com/deepseek-ai/deepseek-harness/blob/f3803c96974ad4a94195fb97e5c637e9c2a3afe3/LICENSE) was reviewed. No upstream scripts, dependencies, or reference files were copied.

- agent-experience adopts progressive disclosure, retrievable entry points, constraints before action, bounded output, and total-work evaluation. OpenAS adds host capability boundaries, handoff routing, positive/negative discovery scenarios, and measurement limits.
- code-simplification adopts net removal of maintenance obligations, producer/consumer evidence, strongest retention arguments, full replacement costs, and state/lifecycle constraints. OpenAS adds generic configuration precedence, dynamic loading, survey-versus-implementation boundaries, and evolution/impact routing.
- DSH-specific protected architecture choices, Cordis paths, Agent Notes policies, repository commands, branch/PR procedures, and automatic multi-agent work division were not ported. They are upstream conventions rather than general project requirements. Instructions do not implement upstream tool registration or runtime capabilities.

This record establishes provenance and adaptation scope, not native discovery, behavioral acceptance, or token savings. Report actual validation separately for this change.
