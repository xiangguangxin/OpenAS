---
name: release-management
description: "准备、核验或按授权发布软件版本，核对版本、变更日志、标签、制品、安装或升级验证及失败恢复。 / Prepare, verify, or publish an authorized software release, reconciling versions, changelogs, tags, artifacts, smoke checks, and recovery."
---

中文 | [English](SKILL.en.md)

遵循[语言约定](../../references/language.md)和[结论与证据共享规则](../../references/evidence-policy.md)。

# 软件版本发布

确定发布版本、目标提交 SHA、渠道与现有发布流程。识别版本号来源、上一发布标签、发布说明和制品，按项目约定核对版本字段。用两个发布点之间的实际变更编写说明，列出用户可见变更及必要的兼容或升级步骤。核对同名标签、Release 和包版本的现有状态。已存在时确认指向和制品；遇到冲突，保留现场并明确需要的决策。

## 验证和发布

- 将必需检查、构建任务和制品绑定到目标提交。核对打包内容、平台和项目已有的摘要或签名。对将要分发的同一制品执行与变更相关的干净安装或升级冒烟检查，并记录实际结果。
- 按已有授权创建标签、Release、上传制品或执行渠道发布。发布后读回标签指向、渠道中的版本和制品，按需核对摘要及可安装性。准备任务交付发布清单和待执行步骤。
- 发布中断时先检查哪些步骤已生效，再重试缺失步骤。沿用渠道支持的停止推广、撤回或后续修复流程。已有标签或公开制品出现冲突时先查清影响，保留原记录。涉及数据或格式迁移时单独核对旧版本能否读取新状态。

交付版本、提交、标签、制品与渠道位置、检查证据、实际发布状态和恢复条件。流水线配置用 [ci-cd](../ci-cd/SKILL.md)，开发分支收尾用 [finish-development-branch](../finish-development-branch/SKILL.md)。
