# Claude 客户端热加载自动回归

入口是 [test_claude_hot_reload.py](../tests/test_claude_hot_reload.py)，由 Python unittest 运行，属于**依赖真实外部客户端的集成测试**。默认单元测试会显式 skip，不把模拟测试的成功记作真实加载成功。

## 如何运行

在 Linux/WSL/macOS 中准备已登录、支持流式输入和插件命令的 Claude CLI（至少 2.1.268），然后在 OpenAS 根目录执行：

```bash
OPENAS_RUN_CLAUDE_TESTS=1 PYTHONDONTWRITEBYTECODE=1 \
  python3 -m unittest discover -s tests -p 'test_claude_hot_reload.py' -v
```

测试会调用真实模型，消耗当前账户额度；不自动安装客户端、登录或改全局配置。显式启用后，CLI 缺失、版本过旧、认证/网络错误或协议不兼容都会失败，不转用 mock，也不再转为 skip。

可选参数：

| 环境变量 | 默认值 | 用途 |
|---|---|---|
| `OPENAS_CLAUDE_BIN` | `claude` | 指定现有可执行程序名称或完整路径 |
| `OPENAS_CLAUDE_TIMEOUT` | `120` 秒 | 每个协议请求/回合的超时；超时终止测试进程组 |
| `OPENAS_CLAUDE_BUDGET_USD` | `1.00` | 传给 CLI 的单次运行预算上限；触顶导致失败，不能放宽断言 |
| `OPENAS_CLAUDE_REPORT` | 不落盘 | 成功后写精简 JSON 回执；目标父目录须存在、文件须不存在 |

需要保留一次真实验收记录时：

```bash
OPENAS_RUN_CLAUDE_TESTS=1 \
OPENAS_CLAUDE_REPORT=/tmp/openas-native-reload-receipt.json \
PYTHONDONTWRITEBYTECODE=1 \
  python3 -m unittest discover -s tests -p 'test_claude_hot_reload.py' -v
```

回执仅在全部断言完成后生成，含客户端版本、会话 ID、新旧探针标记和原生命令标识；不含认证信息、原始提示或完整日志。失败或跳过不生成“passed”回执，已有回执不覆盖。不要把复制来的回执当作当前版本已实测。

## 本次执行结果 · 2026-10-21

- 普通测试：`tests/` 中 14 项通过、1 项原生用例跳过；工作流回归另有 25 项通过。
- 显式设置 `OPENAS_RUN_CLAUDE_TESTS=1` 后，该用例退出 1，原因是找不到真实 Claude CLI。它没有进入模型调用或生成成功回执。
- 因此目前是“测试代码和本地防误判检查已完成，原生热加载尚未验证”，不能将上述 39 项通过计作原生通过。

## 测试固定了哪些行为

1. 在临时目录复制**当前 OpenAS 插件**，增加一个只输出随机标记的 `reload-probe` Skill。源插件、用户项目和 marketplace 配置不修改。
2. 执行真实 `claude plugin validate`，再以 `--plugin-dir` 启动**唯一一个长期存活的 Claude CLI 进程**，使用 stream-json 双向输入输出。
3. 调用 `/openas:reload-probe`，只接受最终成功结果中精确匹配的旧标记。请求本身不包含期望标记，用户消息回显、日志或模型解释都不能作为通过依据。
4. 原子替换临时 Skill 的内容，发送 `/reload-plugins`；要求结果带原生 `local_command=reload-plugins` 证据，并有成功加载插件的摘要。缓存阻断、加载错误或模型声称“已重载”都失败；测试不自动加 `--force`。
5. 再次调用同名 Skill，精确核对新标记。三回合必须具有同一个非空 session ID，客户端 PID 不变，最后仍存活。
6. 无论通过或失败，都清理测试进程组和临时目录。无真实客户端时，不以另起进程或手写文件重读模拟热加载。

禁用文件发现来源、工具和外部 MCP，仅测试明确传入的插件；不使用绕过权限的选项。认证沿用现有客户端，不启用会跳过订阅认证的 bare 模式。不指定模型，沿用客户端可用默认选择。该用例不需要模型读写文件或运行命令。

## 测试层次与覆盖限制

[test_claude_stream.py](../tests/test_claude_stream.py) 的 5 项本地测试验证错误结果拒绝、旧内容拒绝、模型冒充重载拒绝、会话更换拒绝，以及管道读取/超时/进程清理；其子进程是假协议端点，**不证明 Claude 已实测**。

真实用例验证 headless 会话内的 Skill 内容重载，不覆盖终端 UI、Agent 更新、MCP 连接、启停或卸载。主动自动发现文件更新的客户端也可能已刷新内容；测试证明执行原生 reload 后同一会话可使用新版，不证明只有 reload 才能刷新。

CLI 流式协议和命令结果字段可能随版本变化。无法识别时应失败并核对本地版本，而不是删除原生命令或会话连续性断言。`scripts/claude_stream.py` 是小范围测试驱动，不是通用 SDK。

官方依据：[无终端会话的 reload](https://code.claude.com/docs/en/plugins/cli-reference)、[程序化 CLI](https://code.claude.com/docs/en/headless)、[CLI 参数](https://code.claude.com/docs/en/cli-reference)、[SDK 控制协议实现](https://github.com/anthropics/claude-agent-sdk-python/blob/main/src/claude_agent_sdk/_internal/query.py)。

## 独立的原生安装生命周期测试

`test_claude_lifecycle.py` 在临时项目和独立 `CLAUDE_CONFIG_DIR` / 插件缓存中验证本地 marketplace 安装、禁用、启用和卸载，并检查目标项目记忆未被删除。它只执行插件管理命令，不调用模型，不需要复用用户的认证配置，也不代表会话内热加载通过。

```bash
OPENAS_RUN_CLAUDE_LIFECYCLE=1 \
  python3 -m unittest discover -s tests -p 'test_claude_lifecycle.py' -v
```

可用 `OPENAS_CLAUDE_BIN` 指定客户端，`OPENAS_CLAUDE_LIFECYCLE_REPORT` 保存独立收据（目标文件不能已存在）。当前环境没有 Claude CLI，测试仍未获得真实通过记录；默认 CI 跳过。
命令与 JSON 列表格式依据 [Claude 插件命令参考](https://code.claude.com/docs/en/plugins/cli-reference)，配置隔离依据 [环境变量说明](https://code.claude.com/docs/en/env-vars)。
