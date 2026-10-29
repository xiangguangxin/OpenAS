---
name: finish-development-branch
description: "开发完成后核对 diff、验收与评审，按既有授权提交、推送或合并，并保留未完成项。 / Check final diff, acceptance, and reviews, then commit, push, or merge within existing authorization while preserving unfinished work."
---

中文 | [English](SKILL.en.md)

语言 / Language: 按用户指定语言回复，否则跟随任务语言；编辑已有内容保留原语言。Honor explicit output language, otherwise follow the task language; preserve existing artifact language unless translation is requested. Keep machine-readable identifiers unchanged. See [语言约定 / language policy](../../references/language.md).

涉及事实回答、测试、评审或完成结论时，先读取并遵循 [结论与证据共享规则](../../references/evidence-policy.md)。

# 开发分支收尾

先核对当前分支、起始改动归属、目标基线和工作区状态。读取实际变更，确认用户已有修改没有被覆盖，生成文件、临时日志和认证信息没有混入待提交内容。

运行与最终变更相关的检查，并处理尚未关闭的评审问题。外部环境不可用时说明具体未验证项，不将 CI 成功等同于所有客户端或产品验收通过。

提交按实际问题和行为组织，描述触发场景及结果，例如 `Handle duplicate records during import`。只暂存本次任务明确涉及的文件；不要用重置、清理或强制推送处理不理解的变化。

提交、推送、创建 PR、合并和发布分别遵循用户已有授权，不重复请求已经授予的权限，也不因进入收尾流程自动扩大授权。获准合并时先核对 PR 最新提交和必需检查，合并后确认目标分支与自动检查结果。

交付说明最终文件与行为、验证、提交或 PR 位置，以及剩余限制。清理临时 worktree 之前检查未保存内容，保留仍需审查的现场。
