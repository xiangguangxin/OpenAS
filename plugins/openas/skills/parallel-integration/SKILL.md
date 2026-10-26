---
name: parallel-integration
description: "整合已授权独立任务的成果，核对文件与接口冲突并验证组合结果；不提供或自动启动并行调度。 / Integrate already authorized independent work, inspect overlapping changes and contracts, and verify combined behavior; do not provide or automatically start parallel scheduling."
---

中文 | [English](SKILL.en.md)

语言 / Language: 按用户指定语言回复，否则跟随任务语言；编辑已有内容保留原语言。Honor explicit output language, otherwise follow the task language; preserve existing artifact language unless translation is requested. Keep machine-readable identifiers unchanged. See [语言约定 / language policy](../../references/language.md).

# 整合独立成果

先核对各工作区或分支的原始目标、基线、实际 diff、范围、上游接口和验证记录。分支标记完成不代表可以安全合并；来源不明或含未保存修改时先保留现场。

检查文件重叠、公共接口、配置、生成产物及共享运行资源。相同文件的修改按依赖顺序整合；文本自动合并成功后仍检查组合语义。不要用选择整边文件的方式盲目解决冲突。

在独立集成工作区中按已有授权应用成果，先验证受影响组件，再验证跨组件调用。原分支通过的测试不能替代集成后的结果。失败时记录具体冲突、来源和责任任务，保留双方成果，不自动强推或清空工作区。

当前 OpenAS 任务图只顺序调度；该技能用于宿主已经提供的并行成果。创建或清理隔离工作区见 [git-worktrees](../git-worktrees/SKILL.md)，发布与合并遵循当前任务授权。
