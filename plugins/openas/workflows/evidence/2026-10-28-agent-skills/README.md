# 新技能行为验证 / New skill behavior evaluation

2026-10-28，Codex CLI 0.160.0，沿用已有登录与模型设置。完整合成输入、用户请求、结果与宿主检查见 [receipt.json](receipt.json)；没有使用真实项目数据。

| Case | Expected / observed skill | Result |
| --- | --- | --- |
| Agent 工具描述、约束和详情读取评估 | agent-experience | Passed |
| 只读维护负担简化调查 | code-simplification | Passed |
| 普通产品按钮文案 | interaction-design | Passed |
| 仅解释入口与数据流 | codebase-analysis | Passed |

每例建立独立临时工作区，写入 receipt 中的相同 fixtures。将完整 49 项技能的路径及 frontmatter 作为目录提供，要求客户端先选择并读取 SKILL.md，再完成请求。执行方式为 `codex exec --ephemeral --skip-git-repo-check --color never --json --sandbox read-only -C <fixture> --output-schema <schema.json> -o <result.json> -`，prompt 通过 stdin 输入，宿主超时为 180 秒。schema 沿用仓库 `scripts/evaluate_skills.py` 的 SCHEMA；未覆盖模型或审批配置。原始日志保留在本地临时目录，不随插件发布。

宿主核对客户端退出码、所选技能、成功读取对应技能的命令事件、问题列表为空，以及运行前后样例文件内容指纹不变。实现会话另行阅读了实际返回与成功命令记录：Agent 样例核对了分页/截断和详情文件，并明确未测量 token；简化样例指出冗余派生状态，同时保留公开 debug 参数、动态装载的插件及详情文件，还限定了行为对照的输入范围和异常时机风险。反向案例没有把产品 UX 或代码解释改成专项审计。

三个案例先尝试不存在的 `python`，退出 127 后改用 `python3 -B` 成功；receipt 保留各命令退出码，不把首次失败抹去。四个客户端任务均正常完成，无自动重试。客户端还输出过模型目录刷新超时等诊断，未阻止本次任务交付。

这些是四个单次合成样例，不是完整能力评测、独立人工验收或原生 Claude 插件发现证据。usage 如客户端提供则保留其原始口径，没有前后基线，不能推导 token 节省。输出中的 `${OPENAS_PLUGIN}` / `${EVALUATION_ROOT}` 是发布时替换的本机路径占位符。

## English

Four isolated, single-run synthetic tasks used Codex CLI 0.160.0 with existing authentication/model settings, ephemeral read-only sessions, a 180-second host timeout, and no automatic retry or model/approval override. The receipt contains fixtures, requests, observed results, usage when supplied, and host checks. All 49 skill paths/frontmatter entries were available; native command events confirmed reading the selected skill. Host checks also confirmed exit success, expected routing, no questions, and unchanged fixture content.

Implementation-session semantic review checked actual results and command records. The Agent case retained permissions, failure and pagination constraints and retrieved real detail data without claiming token savings. The simplification case preserved a public keyword, manifest-loaded plugin, and detail file while identifying unused derived state and qualifying comparison coverage and exception timing. Negative cases stayed with product interaction design and source explanation.

Three cases initially failed to find `python`, then succeeded with `python3 -B`; command exit codes remain in the receipt. Model-catalog refresh diagnostics did not prevent task completion. Raw logs remain local. This is not independent human acceptance, native Claude discovery, a comprehensive evaluation, or a before/after token benchmark. Published paths are normalized placeholders.
