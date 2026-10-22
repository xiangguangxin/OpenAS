---
name: failure-recovery
description: 工作流失败时根据实现、环境、客户端、验收、范围或格式问题选择修复、有限重试或交回条件；避免重复执行与无界重试。
---

# 失败恢复

读取 failure、原始命令、退出码和上下文，核对是否已有部分产物或外部副作用。以实际证据分类；未知原因保持 unknown，不把所有失败都称为网络问题。

| 类型 | 下一步 |
| --- | --- |
| environment | 核对可执行文件、依赖、路径和权限；不要改业务逻辑来掩盖环境缺失 |
| timeout / client_failure | 检查日志和进程结束状态，确认当前文件后再恢复；不自动切换模型、账号或放宽沙箱 |
| invalid_result | 检查客户端结构化输出和兼容性；空结果或格式错误不当作通过 |
| scope_violation | 停止并列出范围外变化，不自动撤销用户文件，也不扩大授权 |
| review_limit / acceptance_limit | 保留反例和完整反馈，解决原因后开始新的修订任务，不重置轮数绕过上限 |
| interrupted | 检查最后成功检查点与部分修改，再按 checkpoint-and-resume 恢复 |

只有明确可重试且副作用可控的步骤才重试，并记录次数、结果和停止条件。当前运行器没有后台自动重试；显式恢复也不能绕过范围和规则核对。交接使用 [context-handoff](../context-handoff/SKILL.md)。
