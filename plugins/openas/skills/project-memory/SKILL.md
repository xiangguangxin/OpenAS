---
name: project-memory
description: "从项目任务和验证记录中提炼、审查与复用经验，并将成熟经验生成项目候选技能，管理试用、启用、使用反馈和回滚；用于跨任务知识积累，不用于保存全部聊天或修改核心权限。 / Extract, review, and reuse evidence-backed project knowledge and manage candidate skill trials, activation, feedback, and rollback; do not retain whole conversations or expand permissions."
---

中文 | [English](SKILL.en.md)

语言 / Language: 按用户指定语言回复，否则跟随任务语言；编辑已有内容保留原语言。Honor explicit output language, otherwise follow the task language; preserve existing artifact language unless translation is requested. Keep machine-readable identifiers unchanged. See [语言约定 / language policy](../../references/language.md).

涉及事实回答、测试、评审或完成结论时，先读取并遵循 [结论与证据共享规则](../../references/evidence-policy.md)。

# 有证据的项目记忆

先读 [项目记忆说明](../../memory/README.md)。默认项目范围，不修改模型参数，不将反思文字直接升级为真理或可执行指令。

## 任务开始

用脚本 query 检索本次任务关键词，最多读取少量相关 accepted 条目。检查来源仍有效，当前源码和用户要求优先；记忆只是有来源的上下文。current-task.json 是最近任务检查点，不是自动恢复指令，也不授予继续执行旧任务的权限。

需要复用已启用项目技能时，用 [learning.py](scripts/learning.py) 的 `--root 项目目录 context 查询词` 获取当前有效指导；它不会自动安装到宿主技能目录。返回内容仅在适用条件成立时使用，不能扩大任务或权限。

## 任务结束或出现可复用经验

1. 提取最小、具体结论，标明适用范围：fact（观察到的项目事实）、decision（已经作出的设计决定及取舍）、lesson（失败/成功案例的经验）。不要从实现代码反推用户从未批准的产品决策。
2. 给出可读 key、scope、tags 和真实 evidence。证据为项目内 JSON 文件、SHA-256、JSON pointer 和对应值。来源是 Markdown/源码时先建立证据收据，并通过 `Memory.evidence('receipt.json', '/result', sources=['src/example.py'])` 显式关联原始文件；查询会同时校验收据和来源。没有 sources 的旧记录只校验其直接 JSON 证据，不会递归解释收据中的任意字段；重要旧结论应补充来源后重新提议。不能杜撰 JSON 来源。
3. propose 后停在 candidate，不用于其他任务。评审应核对结论是否由证据支持，是否范围过大、过期、重复或包含敏感内容；可用独立 Agent 或明确的人工评审。
4. review approve 才进入 accepted；reject 保留理由。同 key/scope 已有有效条目时进入 conflict，不覆盖旧知识。解决冲突需核对来源、退役旧条目并重新评审冲突项。
5. 只沉淀必要字段，不保存认证信息、全量聊天、原始客户端日志或执行目标。记忆目录中的知识可入 Git，运行检查点和锁文件不入库。

脚本：[project_memory.py](scripts/project_memory.py)。必须用 `--root /path/to/consumer-project` 明确项目根目录，记录写入该项目 `.openas/memory/`，不写插件目录。用 `--help` 查看命令，示例和字段见 memory/README.md。

## 自动化边界

Harness 默认在每个阶段更新短期检查点；开始时检索通过评审且证据未变的相关记忆；成功后只从宿主 verified/exit_code 字段自动生成有限的运行事实。自由文本、模型自评和失败原因不会自动获得“已验证经验”的资格。

单任务运行器启用记忆时会采集成功/失败观察；`--learn` 额外使用独立只读模型会话提炼和评审，再为通过的经验生成候选技能。涉及复杂经验、技能生成或反馈维护时读取 [项目学习与技能演进](../../memory/learning.md)，使用其中字段和命令，不能把模型自评直接当作通过。

生成技能先留在项目候选区，核对触发条件、步骤、验证和边界；通过对应正例、反例试用及独立技能评审后才启用。评测命令来自可信任务定义，不从候选技能自动执行。记录使用版本和反馈，必要时停用或回滚；来源变化后重新提炼，不更新指纹冒充验证。

这些是按任务触发的工作流，不是安装 Skill 后自动出现后台观察器。修改 CLAUDE.md、Agent 约束或放宽权限仍属于独立变更。

## 维护

inspect 查看 evidence_valid。来源改变或缺失，query 自动排除该条，不静默更新证据指纹。需要保留的新结论重新提议；retire 保留历史原因。来源指纹只能证明内容一致，不能证明结论正确，语义评审不可省略。
