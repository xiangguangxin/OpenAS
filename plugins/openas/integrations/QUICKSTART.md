# 客户 MCP 接入指南（Claude Code）

统一入口是本目录的 `setup_mcp.py`。需要 Python 3.9+，仅使用标准库；从源码或已安装插件目录均可运行。它读取同目录的三个服务模板，不自动安装依赖或注册到其他客户端。其他客户端按其配置格式接入，不能直接复用生成的 Claude Code 配置。

## 1. 选择服务并准备环境

| 服务名 | 准备事项 | 详细说明 |
| --- | --- | --- |
| `playwright` | Node/npm、可运行的浏览器及系统依赖；首次下载包需要网络 | [Playwright](playwright/README.md) |
| `github` | 官方 `github-mcp-server` 二进制加入 PATH；客户自己的仓库读取 token | [GitHub](github/README.md) |
| `context7` | 可访问远程服务；客户自己的 Context7 API key | [Context7](context7/README.md) |

请在启动 Claude Code 的同一环境执行配置与检查。Windows 原生环境和 WSL 的 PATH、依赖和环境变量各自独立。Python 命令可能是 `python3`、`python` 或 `py -3`，以下示例使用 `python3`。

## 2. 合并项目配置

在 OpenAS 仓库根目录运行以下命令，将 `/path/to/customer-project` 替换为客户实际项目目录。如果使用安装后的插件，将脚本路径替换为插件内 `integrations/setup_mcp.py` 的实际位置。

```bash
python3 plugins/openas/integrations/setup_mcp.py configure --project /path/to/customer-project --services all
```

只启用部分服务时，将 `all` 替换为名称列表，例如 `--services github context7`。

工具将所选条目合并到目标项目的 `.mcp.json`，保留其他服务和顶层字段。相同配置重复执行不改写；同名配置有差异、JSON 无效或文件为符号链接时停止，需人工核对。不会覆盖已有自定义服务，也不会写入真实凭据。请在编辑器中检查生成文件。

## 3. 在当前环境提供凭据

Playwright 无需这两个凭据。只为启用的服务设置相应变量，不要将实际值填入 JSON、提交到仓库或粘贴到验收报告。工具不自动加载 `.env`。

Bash / WSL 可用隐藏输入，避免将值直接写入 shell 历史：

```bash
read -r -s -p 'GitHub token: ' OPENAS_GITHUB_TOKEN
export OPENAS_GITHUB_TOKEN
read -r -s -p 'Context7 API key: ' OPENAS_CONTEXT7_API_KEY
export OPENAS_CONTEXT7_API_KEY
```

PowerShell 使用交互输入，再设置当前进程环境变量：

```powershell
$githubSecret = Read-Host 'GitHub token' -AsSecureString
$env:OPENAS_GITHUB_TOKEN = [System.Net.NetworkCredential]::new('', $githubSecret).Password
$context7Secret = Read-Host 'Context7 API key' -AsSecureString
$env:OPENAS_CONTEXT7_API_KEY = [System.Net.NetworkCredential]::new('', $context7Secret).Password
Remove-Variable githubSecret, context7Secret
```

这些设置仅对当前终端及其后启动的进程生效。在该终端中启动 Claude Code；已经运行的客户端不会自动继承新变量。长期使用可通过客户自己的凭据管理流程提供变量。

## 4. 执行本地预检

```bash
python3 plugins/openas/integrations/setup_mcp.py check --project /path/to/customer-project --services all
```

检查内容：配置是否与所选模板一致、Claude Code 和相关可执行命令是否在 PATH、Playwright 的 Node 最低版本、所需环境变量是否非空。只执行 `node --version`，不启动服务、不下载包、不输出凭据、不验证凭据有效性或网络。

退出码：`0` 表示自动预检项通过，`1` 表示有失败项，`2` 表示参数或配置处理失败。`MANUAL` 项必须继续在实际客户端中验收；预检通过不等于 MCP 已连接。自定义配置不匹配模板时需人工核对，失败提示不表示该自定义配置必然不可用。

## 5. 连接并逐项验收

进入客户项目目录，从已设置变量的终端启动或重启 `claude`。按客户端提示完成项目配置的信任确认，运行 `/mcp` 查看服务与工具状态；也可用 `claude mcp list` 辅助排查。角色有工具白名单时，仍需按现有权限规则允许相应工具。

逐项发送以下任务，将示例中的地址、仓库和库名替换为真实测试对象：

| 服务 | 可发送给 AI 的验收任务 | 通过标准 |
| --- | --- | --- |
| Playwright | “使用 Playwright MCP 打开我已启动的本地测试页面，读取标题与一个可见按钮，执行一个无副作用操作，检查结果并关闭浏览器。” | 真实浏览器操作完成，记录实际结果与预期；浏览器或依赖缺失时标记未通过 |
| GitHub | “使用 GitHub MCP 读取我授权的 owner/repo 元数据和指定提交中的 README，核对仓库、路径与提交，并确认当前连接只暴露只读工具；不要修改远程内容。” | 成功读取指定对象，来源与 ref 明确；本项目模板保持只读 |
| Context7 | “使用 Context7 查找项目正在使用的一个公开库，确认 library ID，查询一个明确 API 的文档，注明来源及适用版本；找不到目标版本时明确说明。” | 成功检索相关资料并报告版本覆盖情况；版本缺失时不宣称该版本已验证 |

仅 `/mcp` 显示连接成功不能代替上述任务。以下信息可复制到客户自己的验收记录中，每个服务单独填写：

```text
服务 / 客户端与版本：
服务端版本或托管查询时间：
目标对象（URL、仓库与 ref、库与目标版本）：
实际调用的工具：
操作步骤、预期与实际结果：
结果：通过 / 失败 / 未执行
限制与待处理项（不得包含凭据）：
```

## 常见问题与撤销

| 现象 | 处理方向 |
| --- | --- |
| 找不到命令 | 在实际启动客户端的环境安装依赖并检查 PATH；特别核对 WSL 与 Windows |
| 缺少变量或认证失败 | 确认客户端从已设置变量的终端启动；再核对 key/token 有效性和权限 |
| HTTP 超时或无法下载 npm 包 | 检查客户环境中的网络、代理与服务可达性 |
| 服务连接但角色没有工具 | 查看实际工具列表、工具组、客户端策略和角色白名单 |
| Playwright 启动失败 | 按固定包对应的上游指引检查浏览器与系统依赖 |
| 读取仓库失败 | 核对 owner/repo、私有仓库授权及组织访问要求 |

撤销时只删除目标项目 `.mcp.json` 中本次加入的服务，保留其他配置，重启客户端并停止相应进程。必要时在服务方撤销凭据；删除配置不会自动撤销 token 或 key。

客户端配置依据：[Claude Code MCP 官方文档](https://code.claude.com/docs/en/mcp)。本指南提供配置和验收流程，未使用客户凭据执行真实连接测试。
