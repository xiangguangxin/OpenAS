# 可选 MCP 集成

中文 | [English](README.en.md)

OpenAS 提供配置示例和按需使用指引，不随插件加载自动注册或启动这些服务。宿主已有等价工具时优先复用；工具名、参数和角色可见性以当前会话实际工具列表与 schema 为准。

| 集成 | 角色与技能 | 配置前提 |
| --- | --- | --- |
| [Playwright](playwright/README.md) | test-engineer、verifier、ux-designer；integration-testing、accessibility-review | Node/npm、浏览器及其系统依赖 |
| [GitHub](github/README.md) | product-manager、developer、red-team、it；需求与评审工作流 | 官方服务端二进制、GitHub token 和网络 |
| [Context7](context7/README.md) | researcher、cto、developer；technical-research、technology-selection | 网络与服务 API key |

## 配置与启用

客户首次接入请从 [统一接入指南](QUICKSTART.md) 开始：选择服务 → 合并配置 → 提供自己的凭据 → 本地预检 → 客户端连接与逐项验收。随插件交付的 [配置与检查工具](setup_mcp.py) 需要 Python 3.9+，支持按需合并三个服务，保留其他配置，同名冲突时停止，不写入真实凭据。

```bash
python3 plugins/openas/integrations/setup_mcp.py configure --project /path/to/customer-project --services all
python3 plugins/openas/integrations/setup_mcp.py check --project /path/to/customer-project --services all
```

以上命令从 OpenAS 仓库根目录执行；安装副本请使用实际脚本路径。只选择部分服务可用 `--services github context7`。检查不启动服务或验证网络与凭据有效性，必须继续完成指南中的真实任务验收。

各目录的 `claude.mcp.example.json` 是 Claude Code 项目范围模板。只选择本次需要的服务，将对应 `mcpServers` 条目合并到目标项目的 `.mcp.json`；保留已有配置，不整文件覆盖。环境变量由启动客户端的进程提供，不提交实际凭据。Claude Code 的变量引用规则见 [官方 MCP 文档](https://code.claude.com/docs/en/mcp)。Windows 原生终端与 WSL 是不同环境，命令、浏览器和环境变量需在实际宿主环境可用。

重连目标项目会话，在 `/mcp` 查看连接和工具可见性；也可运行 `claude mcp list`。项目配置可能要求宿主信任确认。角色有工具白名单时，需要在目标宿主中显式允许相应 MCP 工具；本包不扩大角色现有权限。仅安装示例不保证子 agent 能调用工具。

Codex 等其他客户端须按其配置格式单独注册；此处 JSON 不直接用于 Codex。现有 Codex 工作流适配器不解析这些模板、不自动注入 MCP 配置，也不扩大任务 scope 或联网模式。阶段是否有工具须在真实会话确认。

撤销时删除目标项目中本次加入的服务条目并重连，保留其他服务。停止仍在运行的对应进程；撤销注册不等于撤销服务端凭据，必要时在对应服务管理凭据。

## 证据与验收

配置静态检查只证明 JSON 和引用结构可读；`/mcp` 显示连接只证明发现服务。真正可用需在目标宿主完成各集成的最小只读任务，保留工具名、对象、版本或时间、结果和限制。失败分别定位为启动、认证、工具可见性或业务行为，不循环重装。

当前交付状态：统一配置工具、本地预检、配置示例、角色/技能路由与逐项验收步骤已提供；运行 configure 后才写入目标项目配置，不自动安装服务，未使用客户凭据执行真实 MCP 验收。托管服务的额度和权限以账号及服务当前规则为准。

上游配置核对日期：2026-10-23。固定 npm 包版本只约束客户端包，不固定远程服务行为；升级时重新检查配置、工具 schema 和最小任务。
