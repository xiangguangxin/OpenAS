---
name: checkpoint-and-resume
description: "在工作流中断后核对任务、工作区和执行规则，恢复可信检查点或显式使旧结果失效；用于恢复已有运行，不用于自动继续未经授权的旧任务。 / Validate task, workspace, rules, and evidence after interruption before reusing checkpoints; do not automatically resume unauthorized historical work."
---

中文 | [English](SKILL.en.md)

语言 / Language: 按用户指定语言回复，否则跟随任务语言；编辑已有内容保留原语言。Honor explicit output language, otherwise follow the task language; preserve existing artifact language unless translation is requested. Keep machine-readable identifiers unchanged. See [语言约定 / language policy](../../references/language.md).

涉及事实回答、测试、评审或完成结论时，先读取并遵循 [结论与证据共享规则](../../references/evidence-policy.md)。

# 检查点与恢复

先取得用户当前希望继续的任务，读取原始任务、state.json 与 handoff.json。核对工作区、文件范围、原始验收和当前文件状态；记忆条目不等于恢复授权。

Codex 适配器可对带编排版本的运行使用 `--resume`。它核对任务与规则指纹、源文件内容和权限，并重用已完成的阶段结果；宿主验收和 verifier 在恢复后重新执行。相同运行目录有进程锁，不能并发恢复。

如果源码或规则发生变化，默认拒绝复用；先检查变化是否仍在原始范围内。用户授权重新验证当前修改后，可用 `--resume --restart-stages` 清空可复用阶段并从设计或本路线起点重新执行，原始基线和旧日志保留。不能用此选项扩大 scope 或恢复范围外改动。

正在执行阶段留下的部分修改可能未形成检查点；先检查，不自动撤销。旧格式运行、任务定义变化、已完成运行或损坏记录应新建运行或人工处理。详见 [恢复边界](../../workflows/README.md)。
