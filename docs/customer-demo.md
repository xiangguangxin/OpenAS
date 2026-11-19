# 客户演示与接入验收

这些入口从 OpenAS 仓库根目录运行，Python 3.10+。将路径替换为客户的实际路径；Windows 使用 `python`，输出目录必须新建。独立桌面/浏览器执行属于 [Praxis](https://github.com/xiangguangxin/Praxis)，不继承 Codex/Claude 的订阅或工具注册。

## 1. 安装与预检

```sh
python plugins/openas/integrations/codex_skills.py install --project /path/to/customer-project
python plugins/openas/integrations/codex_skills.py check --project /path/to/customer-project --native
python plugins/openas/integrations/doctor.py --project /path/to/customer-project --native-skills
```

安装器将完整插件资源复制到客户项目 `.agents/openas/`，在 `.agents/skills/openas-*` 创建带命名空间的入口。入口先读取原始技能，保留其相对脚本与参考链接。没有符号链接，不改客户 AGENTS.md 或全局配置。`check --native` 调用当前 Codex 的 `skills/list`，核对实际发现的路径与启用状态，不启动模型任务。客户端必须能写入自己的状态目录；检查失败不能当作已加载。

更新仓库后运行相同脚本的 `update`；`uninstall` 只移除已登记的 OpenAS 文件。两者先核对指纹，发现本地编辑会停止，保留客户改动；其他技能、MCP 和 `.openas/memory` 保留。`check` 的源版本不同会返回非零。不要同时安装同一能力的其他副本来掩盖发现失败。

依据：[Codex 技能位置](https://developers.openai.com/codex/skills)、[客户端发现接口](https://developers.openai.com/codex/app-server)。原生发现不是模型行为验收。Claude Code 继续使用原插件入口；MCP 实际连接按[接入指南](../plugins/openas/integrations/QUICKSTART.md)逐项验收。

## 2. 客户工程预检与隔离

```sh
python plugins/openas/workflows/workspace-tools.py inspect --source /path/to/source --task /path/to/task.json
python plugins/openas/workflows/workspace-tools.py prepare --source /path/to/source --task /path/to/task.json --output /path/to/new-prepared --materialize-symlinks
```

预检报告文件数量/大小、符号链接、特殊文件、已有产物目录与没有机器检查映射的验收项。`prepare` 新建 `workspace/` 和来源指纹 `preparation.json`，不修改原工程；省略 `.git`、`.openas`、任务声明的构建产物。可重复指定 `--include src --include tests` 缩小复制范围，或用 `--exclude` 排除明确目录，不能排除 scope。所有构建输入和测试依赖都必须包含。

只有显式传 `--materialize-symlinks` 才复制工程内部链接的内容；越出工程、指向已排除目录或形成环时拒绝。直接执行仍拒绝符号链接。使用隔离工作区后，审查 diff 再将结果带回原工程；准备工具不自动合并或提交。

项目记忆现在允许 `--project-root` 与 `--workspace` 相同；仅固定 `.openas/memory/` 被视为运行元数据，从源码快照中剪枝，不能作为源码 scope 或 artifacts。记忆不会再静默关闭。运行记录中的 `memory_status` 和报告显示实际状态；`--no-memory` 仍可显式关闭。

## 3. 缺陷修复、下游评审与中断恢复

```sh
python scripts/customer_demo.py --output /path/to/new-demo
python plugins/openas/workflows/graph-runner.py --graph /path/to/new-demo/graph.json --plan
python plugins/openas/workflows/graph-runner.py --graph /path/to/new-demo/graph.json --run --output /path/to/new-demo/run
```

准备命令只复制故意失败的分页 fixture，使用当前 Python 路径，不启动模型；`--run` 才消耗已登录 Codex 的额度。演示失败基线、实现修改、宿主测试、独立 verifier 和下游只读评审。不要直接修改仓库内的训练源文件。

在阶段执行期间按 Ctrl+C，核对保存的现场，再以相同参数增加 `--resume`。图恢复校验计划、客户端选项、规则、工作区与已完成节点的证据指纹；复用已通过节点，恢复中断节点并推进下游，保留原有日志和修订预算。图级互斥锁拒绝同时恢复。已完成节点的产物或范围外源码变化会阻断恢复。

已检查且属于原授权的未完成节点源码变化，可显式增加 `--restart-stages`。若未改变输入，则沿用单节点规则拒绝用它重置预算。已经完成但给出 `needs_fix` 的评审不是可继续的中断会话；修订任务后创建新图。旧 version=1 图记录保留审计，不能直接升级恢复。

打开节点 `report.html` 展示交付。`verified` 仍是兼容的工作流状态；顶层 `acceptance_summary.status` 才汇总机器验收：

| 状态 | 含义 |
| --- | --- |
| `automated_checks_passed` | 所有验收项都有映射且相关宿主检查通过；仍需核对映射是否覆盖业务语义 |
| `needs_manual_review` | 工作流交付，但含未映射、仅评审或尚需人工核对的要求 |
| `in_progress` / `failed` | 尚未交付 / 已停止或存在失败 |

HTML 无外部资源与脚本，所有任务和模型文本均转义。页面在检查点写入时刷新，重载可查看进度；分享前检查其中的源码、路径和业务信息。

## 4. 真实 GUI / 浏览器演示

先按 Praxis 文档单独安装 Runtime、配置支持 JSON/图片的模型；浏览器入口还需 Playwright/Chromium。固定测试过的 Runtime 提交和工具版本，演示前重做预检，不使用未验证的更新。

```sh
praxis create /path/to/goal-state.json --goal "打开 http://127.0.0.1:8080，构建工程、运行测试，并将 test-report.json 下载到指定演示下载目录" --criterion "构建和测试通过，下载的本次测试报告通过独立核验"
python plugins/openas/workflows/examples/customer-gui/demo_app.py --checkpoint /path/to/goal-state.json --output /path/to/new-gui-demo
```

保持应用进程运行，在另一个终端执行：

```sh
python scripts/customer_acceptance.py --checkpoint /path/to/goal-state.json --verifier /path/to/new-gui-demo/verifier.json --browser-url http://127.0.0.1:8080 --download-dir /path/to/new-gui-demo/downloads --output /path/to/new-e2e-evidence
```

网页实际编译 Python 示例并运行四项测试；测试未成功不能导出，重新构建会使上次测试失效。报告只通过浏览器附件下载产生，服务端不会提前替浏览器写入报告。独立验收核对下载文件、测试结果、当前 checkpoint ID 和新鲜度。**此 fixture 不测量覆盖率，不代表 CTC++/LLVM 或客户生产工具已被验证。**

在 Windows/macOS 上用 Nova 操作真实浏览器时，将 `--browser-url/--download-dir` 换为 `--nova /absolute/path/to/nova`，并在 Goal 中明确实际 URL、另存为路径和验收条件。运行前用 `doctor.py --nova ...` 检查平台与可执行文件，再确认截图、辅助功能和窗口权限。它们不由预检自动授予。

中断 Agent 后，检查 checkpoint 和当前应用状态，以新证据目录重跑 `customer_acceptance.py --resume`。未知副作用仍需按 Praxis 的 reconcile 流程人工核对，不能绕过审批。用旧 run ID 的报告、错误结果或缺少下载文件时，独立验证必须失败，模型的 `completed` 不足以放行。

收据保留实际进程退出码、checkpoint 状态、验证结果和指纹；暂停、缺依赖、超时、旧报告都不会记为通过。业务语义仍需人工确认。当前仓库 CI 只验证本地 HTTP fixture、恢复逻辑与拒绝误报行为，真实浏览器和 Nova 的执行需要现场运行上述命令。

## 5. 发布前核对

本地 Python 回归、Windows 工作流 smoke、原生客户端技能发现、真实浏览器和原生 Nova 是不同证据等级。参见 [CI](ci.md) 和 [本次记录](../plugins/openas/workflows/evidence/2026-11-19-customer-readiness/receipt.json)。Windows smoke 不覆盖全部第三方 Office 工具，更不能代替 Windows 桌面 E2E。
