---
name: context-handoff
description: "为下一角色或新会话交接当前任务的目标、现场、决定、产物、证据和剩余项；用于任务连续性，不代替长期项目记忆。 / Transfer current task goals, authorization, state, decisions, artifacts, evidence, and remaining work to another role or session; keep it separate from long-term memory."
---

中文 | [English](SKILL.en.md)

语言 / Language: 按用户指定语言回复，否则跟随任务语言；编辑已有内容保留原语言。Honor explicit output language, otherwise follow the task language; preserve existing artifact language unless translation is requested. Keep machine-readable identifiers unchanged. See [语言约定 / language policy](../../references/language.md).

# 任务现场交接

保留原始目标与验收、当前授权、工作区/分支、文件范围和已有用户修改。说明已确认的事实与决定，区分推断和待确认问题，不通过精简丢失影响实现的约束。

交接包括：已完成阶段及其产物位置、最后可信快照、实际检查与覆盖、未关闭问题、失败类别和下一步。优先引用可读取文件与完整证据，不把角色自述作为唯一来源。不要复制无关聊天或认证信息。

Codex 适配器在运行目录生成 handoff.json，和 state.json 一起使用；快照只核对本地源码，实际工作区和规则仍需恢复时校验。接收方先核对状态再行动，文件存在不自动授予执行历史任务的权限。

当前任务现场属于短期状态；经过语义审查、能跨任务复用的事实才交给 [project-memory](../project-memory/SKILL.md)。
