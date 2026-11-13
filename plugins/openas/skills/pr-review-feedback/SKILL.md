---
name: pr-review-feedback
description: "处理已有 PR 评审意见，逐条核对当前提交、修复有效问题、验证改动并记录每条意见的结果；用于收到评审后的跟进。 / Triage existing PR review feedback against the current head, fix actionable findings, verify changes, and report a disposition for each thread."
---

中文 | [English](SKILL.en.md)

按[语言约定](../../references/language.md)保留回复偏好和原文。涉及评审或验证时，遵循[结论与证据共享规则](../../references/evidence-policy.md)。

# 跟进 PR 评审意见

确认仓库、PR 编号、基线、当前 head SHA、本地分支和用户要求的处理范围。使用现有 GitHub 工具、`gh` 或用户提供的评审内容。按需分页读取未解决的线程与回复，以及包含可执行反馈的评审总结。保留线程链接或 ID、原始提交和位置；用当前 diff 与相关代码定位同一行为。评论标记为 outdated 时仍核对问题是否存在。

当宿主缺少完整线程工具、且已有可用的 GitHub CLI 时，可运行 `python3 scripts/read_threads.py OWNER/REPO PR_NUMBER`（脚本路径相对于本技能）。它读取全部内联线程及回复，并在输出中绑定 head SHA。评审总结和普通 PR 评论按需另行读取。[方法来源](FUSION_SOURCES.json)。

## 逐条判断与验证

- 将反馈标为待修复、已修复、重复、有证据可驳回或需要决定。引用当前代码、需求或测试；重复项关联主线程。先修仍然成立且在授权范围内的问题，关联需要同步修复的线程。只做评估时交付结论。
- 保留已有改动。修复前后核对同一触发场景，按风险运行回归。不能验证的场景保留证据缺口；测试通过的提交或本地改动需和当前交付对象对应。
- 发布回复或关闭线程前重新核对 head SHA 和线程状态。发生变化时，重查受影响的结论与检查。按已有授权分别处理推送、回复、关闭线程和合并；保留待确认意见的线程。

交付每条意见的链接、处理结果、对应改动或理由、验证结果和待决项。普通代码评审用 [requesting-code-review](../requesting-code-review/SKILL.md)，开发分支收尾用 [finish-development-branch](../finish-development-branch/SKILL.md)。
