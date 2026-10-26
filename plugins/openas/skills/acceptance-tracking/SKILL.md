---
name: acceptance-tracking
description: "将每条原始验收关联到实现和真实检查证据，区分已验证、模型评审与待人工核对；用于交付前确认需求覆盖。 / Map each original acceptance criterion to implementation and real check evidence; distinguish verified, reviewed, and pending items."
---

中文 | [English](SKILL.en.md)

语言 / Language: 按用户指定语言回复，否则跟随任务语言；编辑已有内容保留原语言。Honor explicit output language, otherwise follow the task language; preserve existing artifact language unless translation is requested. Keep machine-readable identifiers unchanged. See [语言约定 / language policy](../../references/language.md).

# 逐项验收追踪

保留每条原始验收及其含义，为其关联实现位置、适用输入、检查方法、执行对象和结果。区分自动检查、模型评审、人工观察和未验证，不把“命令退出 0”自动推广为所有需求都满足。

任务 JSON 可用 `acceptance_checks` 给每条 acceptance 关联 checks 的零基索引列表，长度必须与 acceptance 一致。一项可以关联多个检查，空列表表示没有机器检查映射；不要用无关测试填充。

Codex 适配器生成 acceptance.json：已映射的条目同时要求相关宿主检查成功和 verifier 通过；未映射条目最多记录为 reviewed，保留人工核对提示。review 路线记录为 reported，不宣称被评审实现已经正确。

验收失败保留输入、命令、目录、退出码及关键输出，交回责任阶段。源码或验收变化后旧证据需重新确认。与 [verification-before-completion](../verification-before-completion/SKILL.md) 配合，交付时明确覆盖缺口。
