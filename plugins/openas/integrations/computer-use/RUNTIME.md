# GUI Goal Agent 内置执行框架与跨会话恢复

[English](RUNTIME.en.md) · [Nova MCP 安装手册](USER-GUIDE.md)

OpenAS 新增了**可运行的 Python Agent Runtime**，不再仅靠 Skill 描述多轮循环。由模型负责每轮决策，Runtime 负责实际循环、状态持久化、步骤预算、审批和中断恢复，Nova MCP 负责桌面操作。

```text
Goal → Runtime → 观察 Nova MCP → 模型规划下一步
            ↑                      ↓
       持久化 JSON ← 操作 + 验证 ← Nova MCP
```

## 模块化安装（推荐）

独立 Runtime 已移到 [`packages/gui-agent-runtime`](https://github.com/xiangguangxin/OpenAS/tree/main/packages/gui-agent-runtime)，原脚本只保留兼容入口。先在仓库根目录安装：

```sh
python -m pip install -e packages/gui-agent-runtime
openas-gui create ./goal-state.json --goal "检查授权 GUI" --criterion "结果可见"
openas-gui status ./goal-state.json
# 配置模型环境变量后：
openas-gui run ./goal-state.json --nova /absolute/path/to/nova
openas-gui resume ./goal-state.json --nova /absolute/path/to/nova
```

`resume` 是重新启动并加载同一个 checkpoint，不是后台自动执行。下方旧命令仍可作为兼容入口使用，但**需要先安装独立 Python 包**。

## 使用前提

- Python 3.10+；Windows/macOS **原生交互式桌面**，已解锁；[Nova 官方可执行文件](https://github.com/bigduu/Nova/releases)。
- 一个支持 **OpenAI-compatible Chat Completions JSON 输出与多模态图片输入**的模型 API。**Claude Code/Codex 订阅和 MCP 注册不会自动继承到此独立 Runtime**，需要单独配置模型 API。
- 从 `plugins/openas/integrations/computer-use` 目录运行以下命令。WSL 不会自动控制 Windows GUI。
- 先用不含账号密码的临时桌面测试。截图会发给配置的模型 API，可能产生费用。

### 1. 创建任务 checkpoint

```sh
python goal_runtime.py create ./goal-state.json --goal "检查授权的测试 GUI 并验证测试结果" --criterion "预期测试结果已显示" --max-steps 40
```

### 2. 配置模型并执行

Windows PowerShell：

```powershell
$env:OPENAS_GUI_API_KEY="你的模型API密钥"
$env:OPENAS_GUI_MODEL="支持图片的模型ID"
python .\live_goal_agent.py .\goal-state.json --nova "C:\Tools\nova\nova.exe"
```

macOS Terminal：

```sh
export OPENAS_GUI_API_KEY="你的模型API密钥"
export OPENAS_GUI_MODEL="支持图片的模型ID"
python live_goal_agent.py ./goal-state.json --nova "$(which nova)"
```

如使用其他兼容服务，设置 `OPENAS_GUI_API_URL` 为完整 Chat Completions 接口地址。Nova 采用直接 stdio 模式，不追加 `mcp` 参数。运行时通过 MCP `tools/list` 获取真实工具名和参数 schema，不硬编码按钮坐标。

### 3. 跨会话恢复

程序中断或终端关闭后，在新终端使用**相同 checkpoint** 再运行上述命令。Runtime 从磁盘加载目标、步骤数和最近进度，并重新观察真实桌面；不会复用旧截图和坐标。

**重要：** 如果中断发生在某次操作发出之后、确认完成之前，Runtime 会标记为 `blocked`，要求人工核对是否已经执行，**不会自动重复可能产生副作用的操作**。完成、失败或阻塞的任务不会自动重启；人工核对后可以创建新任务。

高影响操作会暂停并生成 `pending_approval`。用户核对真实桌面并明确批准后，使用相同命令增加 `--approve-pending`，批准仅针对当前匹配动作。不要盲目批准。

### 4. 查看状态

```sh
python goal_runtime.py status ./goal-state.json
```

checkpoint 使用原子写入，只记录任务摘要、步骤计数、结果摘要、审批哈希与事件历史，不保存截图、工具参数和密钥；但任务目标也可能敏感，请放在私有目录。**暂不支持同一个 checkpoint 被多个进程同时写入**。

## 已实现与尚未实现

| 能力 | 状态 |
| --- | --- |
| 多轮观察 → 决策 → 操作 → 验证 | 已实现基础循环（依赖真实模型 API 与 Nova MCP） |
| 任务状态持久化 | 已实现 JSON 原子 checkpoint |
| 关闭终端后恢复 | 支持重启程序加载进度；不能自动后台续跑 |
| 步数限制与失败停止 | 已实现 |
| 高风险操作暂停审批 | 已实现基础防护，**不是安全沙箱** |
| 操作中崩溃后的自动无损续跑 | 不支持；保守阻塞等待人工核对 |
| 独立程序后台常驻 / 自动调度 | 未实现 |
| 模型给出的完成证据独立核验 | **未实现**，需要业务验证器 |
| Windows/macOS + Nova 真实端到端测试 | 尚未完成 |

请勿把模型声称的 `completed` 当成独立验证通过；在生产场景应加入文件检查、测试结果检查等外部验收器。模型可能判断错误，工具名和风险分类也不能覆盖全部危险操作。建议先在隔离测试桌面使用。

对应文件：[`goal_runtime.py`](goal_runtime.py)、[`live_goal_agent.py`](live_goal_agent.py)、[`gui-goal-executor` Skill](../../skills/gui-goal-executor/SKILL.md)。

## Phase 3 / Phase 4：恢复与独立验收

新版 checkpoint 为 **v2**，可以读取旧 v1 状态，并在写入时迁移。每个 checkpoint 增加跨进程互斥锁；如果中断发生在操作已发出但结果未知时，恢复后会阻塞，不会盲目重试。人工检查桌面后执行：

```sh
openas-gui reconcile ./goal-state.json --outcome executed --note "已核对操作执行成功"
openas-gui resume ./goal-state.json --nova /absolute/path/to/nova
```

也可指定 `--outcome not-executed`。两种结果都不会重放旧动作，而是重新观察并规划。手动核对是必要步骤。

**独立文件验收：** 通过 `--verifier ./coverage-verifier.json` 指定 JSON 验收规则，检查文件存在、最小大小、内容关键字。规则路径限定在指定目录下，防止简单目录穿越。没有提供 `--verifier` 时仍使用旧的模型证据检查，**不能视为独立验收**。新增模拟桌面完整流程测试，但尚未进行真实 Nova/Windows/macOS 端到端验证。


## 产物验收

`--verifier` 配置按 checkpoint 的验收条件逐项匹配。旧的 `path`、`min_bytes` 和 `contains` 仍可使用。新增 `json_fields` 按 JSON Pointer 匹配确切值，`run_id_pointer` 可核对报告内的 checkpoint ID，`fresh: true` 在首个动作前记录文件指纹。恢复用同一配置和根目录。若把同一文件原样再生成一遍，内容指纹无法区分两次生成，使用新目录或带运行 ID 的报告。

```sh
openas-gui verify ./goal-state.json --verifier ./coverage-rules.json
```

此命令无需启动桌面或模型，打印每一项的结果。缺失、旧产物、无效 JSON 或字段不符时返回非零。完整规则和样例见 [Runtime 包文档](https://github.com/xiangguangxin/OpenAS/tree/main/packages/gui-agent-runtime#artifact-verification)。

## 浏览器目标

安装可选依赖和 Chromium，再创建带验收条件的任务并指定测试页。

```sh
python -m pip install -e 'packages/gui-agent-runtime[browser]'
python -m playwright install chromium
openas-gui run ./goal-state.json --browser-url http://127.0.0.1:8080/ \
  --download-dir ./reports --verifier ./coverage-rules.json
```

下载目录需要存在，浏览器仅向新文件名写入。模型通过页面语义快照定位控件，可等待文本及下载结果。用相同启动地址、下载目录和 verifier 恢复。每次启动使用独立的 Chromium 会话，页面状态需重新观察，登录状态和标签页不持久化。具体能力和本地覆盖率夹具见 [Runtime 包文档](https://github.com/xiangguangxin/OpenAS/tree/main/packages/gui-agent-runtime#browser-goals)。

## LiteLLM 网关

已有 LiteLLM Proxy 时，给 OpenAS 进程设置 `LITELLM_API_KEY`，再传入网关地址和模型别名。

```sh
openas-gui run ./goal-state.json --nova /absolute/path/to/nova \
  --litellm-base-url http://127.0.0.1:4000 --model openas-planner
```

`resume` 和 `openas-benchmark` 的实机模式可使用同样的参数。也可用 `OPENAS_LITELLM_BASE_URL` 和 `OPENAS_GUI_MODEL` 配置。网关后面的模型需要支持 JSON 模式，使用截图时还需要支持图像输入。启动网关及浏览器用例见 [Runtime 包文档](https://github.com/xiangguangxin/OpenAS/tree/main/packages/gui-agent-runtime#litellm-gateway)。

## 任务评测

`openas-benchmark` 默认运行隔离的离线用例。传入 `--nova` 或 `--browser-url` 可调用实际后端与配置的模型。再指定 `--experience-store` 和 `--experience-environment` 可以对照开启和关闭经验检索的表现。真实评测需要测试环境和模型 API。报告单独统计预期阻止完成的用例、正向任务完成率、耗时及实际 usage。套件格式和命令见 [Runtime 包文档](https://github.com/xiangguangxin/OpenAS/tree/main/packages/gui-agent-runtime#agent-benchmark)。
