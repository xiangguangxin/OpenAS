---
name: task-orchestration
description: "将多步骤开发任务组织为有依赖、产物、归属和验收的任务图，并按依赖执行与回交；不自动授予并行或发布权限。 / Represent multi-step work as dependency nodes with artifacts, ownership, routes, and acceptance, and execute with failure handoff; do not imply parallel or release authorization."
---

中文 | [English](SKILL.en.md)

语言 / Language: 按用户指定语言回复，否则跟随任务语言；编辑已有内容保留原语言。Honor explicit output language, otherwise follow the task language; preserve existing artifact language unless translation is requested. Keep machine-readable identifiers unchanged. See [语言约定 / language policy](../../references/language.md).

涉及事实回答、测试、评审或完成结论时，先读取并遵循 [结论与证据共享规则](../../references/evidence-policy.md)。

# 编排任务

将原始验收拆成能独立检查的节点，每项写明 ID、上游依赖、工作区、文件归属、输入、产物、执行路线和完成条件。保持用户范围，事实未知先调查，不以拆分任务为由增加产品要求。

先检查依赖环、缺失节点、工作区和共享文件。同一文件或共享状态有写入依赖时顺序执行；只有无依赖且资源独立、宿主支持并获授权时才并行。开始节点前检查上游实际产物和证据，不只看完成标记。

运行器 `graph-runner.py` 提供依赖图的顺序执行和失败阻断，不提供并发调度。先用 `--plan` 校验，再用 `--run` 执行可信任务；例子及格式见 [运行指南](../../workflows/README.md)。任一依赖未通过则阻断下游，独立节点仍可执行；review 返回 needs_fix 不能作为通过的上游。

单节点内部的反馈回环由其路线负责；不在任务图外悄悄创建无限修复链。保留完整反馈、责任节点、尝试次数与停止原因。图失败后支持逐节点检查，不自动重跑整个图或覆盖记录。
