# OpenAS Computer Use 使用手册

适用：Windows 10/11、macOS 14+；Claude Code、Codex CLI。 [English guide](USER-GUIDE.en.md)

> 本功能由 OpenAS 的 `computer-use` Skill + 用户自行安装的第三方 Nova MCP 实现。OpenAS **不会**自动安装、启动或授予桌面权限。Nova 采用 MIT 许可证，项目本身可免费使用；Claude/Codex 模型或订阅可能另行计费。不要把真实桌面权限授予不可信的 MCP。

## 1. 准备工作

- 已安装并能运行 Claude Code 或 Codex CLI；OpenAS 已按 [仓库安装说明](https://github.com/xiangguangxin/OpenAS#readme) 安装或更新到包含 `computer-use` 的版本。
- 从 [Nova 官方仓库](https://github.com/bigduu/Nova) 阅读说明，在 [Releases](https://github.com/bigduu/Nova/releases) 下载匹配操作系统和 CPU 架构的版本；核对发布资产的 SHA-256 后解压。
- 选择一个固定且可信的可执行文件路径，**下面所有路径只是示例**，必须替换成你自己的真实路径。
- 测试时关闭敏感窗口，用临时文件，保持屏幕解锁，避免人在旁边同时操作鼠标。

### Windows

例如将 `nova.exe` 解压到 `C:\Tools\nova\nova.exe`，打开 PowerShell：

```powershell
Test-Path 'C:\Tools\nova\nova.exe'
& 'C:\Tools\nova\nova.exe' --version
```

第一条应返回 `True`。若下载的未签名程序被 Windows SmartScreen 拦截，请先核对项目来源和哈希，不要盲目关闭系统安全功能。普通 GUI 操作需要在**已登录、未锁屏的交互式 Windows 桌面**运行；不要尝试绕过 UAC。

### macOS

可从官方发布页安装；或者在已信任 Homebrew tap 的前提下：

```sh
brew tap bigduu/tap
brew install bigduu/tap/nova
which nova
nova --version
```

Apple Silicon 的路径常见为 `/opt/homebrew/bin/nova`，Intel 常见为 `/usr/local/bin/nova`，以 `which nova` 实际输出为准。

进入 **系统设置 → 隐私与安全性 → 辅助功能**、**屏幕与系统音频录制**，授权实际启动 MCP 的终端、IDE 或 Nova 进程。重启客户端或重新连接 MCP 才能确认权限生效。Retina 和多显示器需要额外验证坐标映射。

## 2. 连接 MCP

**Nova 独立二进制采用 direct stdio 模式：直接运行可执行文件，不需要追加 `mcp` 参数。** 上游的 `nova mcp` 是另一种托管模式，macOS 上需要单独的 Nova.app；本手册默认不使用托管模式。

### Claude Code

Windows PowerShell：

```powershell
claude mcp add --scope user nova -- 'C:\Tools\nova\nova.exe'
```

macOS：

```sh
claude mcp add --scope user nova -- "$(which nova)"
```

重启 Claude Code 会话，输入 `/mcp`，检查 `nova` 是否连接。可使用 `claude mcp list` 检查已注册服务。也可以将 [Claude MCP 示例](claude.mcp.example.json) 中的条目合并到项目的 `.mcp.json`；**不要覆盖已有 MCP 配置**。

### Codex CLI

Windows PowerShell：

```powershell
codex mcp add nova -- 'C:\Tools\nova\nova.exe'
codex mcp list
```

macOS：

```sh
codex mcp add nova -- "$(which nova)"
codex mcp list
```

重启 Codex 会话，确认 Nova 工具在当前会话可见。也可以将 [Codex TOML 示例](codex.config.example.toml) 合并到 `~/.codex/config.toml`。Claude Code 和 Codex **必须分别注册**；OpenAS Skill 不会代替 MCP 注册。

### WSL 特别说明

如果 Codex/Claude Code 运行在 WSL，Linux 进程不会自动获得 Windows 的 GUI 会话。推荐先在 **Windows 原生 PowerShell** 完成 MCP 安装和测试。需要从 WSL 使用时，必须确保实际 MCP 进程运行在 Windows 会话、stdio 桥接可用且路径转换正确；不要把 Linux 的 Nova 当成 Windows 桌面控制器。此路径属于额外集成，需单独验证。

## 3. 确认 OpenAS Skill

OpenAS 包含：

- [computer-use 中文 Skill](../../skills/computer-use/SKILL.md)
- [computer-use English Skill](../../skills/computer-use/SKILL.en.md)

在 Claude Code 中按 OpenAS 插件安装方式加载后，可在提示词中明确要求“使用 OpenAS computer-use Skill”。在 Codex 中需要确认 OpenAS 的 Skill 适配器/加载方式已生效；**只注册 Nova MCP 不代表 Codex 已加载 OpenAS Skill**。如果客户端没有发现 Skill，先根据仓库安装说明修复 Skill 加载，不要假装 Skill 已启用。MCP 本身仍可单独测试。

## 多步骤 Goal 任务

使用 [gui-goal-executor Skill](../../skills/gui-goal-executor/SKILL.md) 配合 computer-use 和已连接的 Nova MCP，Agent 会持续执行“观察 → 判断 → 操作 → 验证 → 更新计划”，直到成功条件满足或安全停止。例如：“使用 gui-goal-executor 在指定测试工程生成覆盖率报告，构建和测试成功且报告存在可读才算完成；覆盖文件前先确认，最多 40 步，连续 3 次失败就停止。”这只是 Skill 编排，不是独立的持久运行服务。

## 4. 第一次安全测试（推荐）

在 Claude Code 或 Codex 输入：

> 使用 OpenAS 的 computer-use Skill，通过已连接的 Nova MCP 操作桌面。先列出窗口并读取当前 UI；打开一个新的记事本（Windows）或 TextEdit（macOS）临时文档，输入“OpenAS computer-use smoke test”，重新读取界面确认文本正确。不要覆盖、保存或发送任何现有文件。每一步先观察、后操作、再验证；若工具不可用、权限不足或目标不唯一就停止并告诉我。

验证时关注：能否列出窗口、是否优先定位 UIA/AX 控件、截图坐标是否正确、输入是否准确、操作后是否重新读取状态。工具显示“点击成功”不等于任务成功。

## 5. 实际使用示例

**VS Code GUI 排查：**

> 使用 computer-use Skill 和 Nova MCP 查看当前 VS Code 窗口，进入调试配置 GUI，检查 Launch/Attach 控件是否完整显示。优先读取控件树，必要时截图。只做检查和截图描述，不修改工程文件。

**浏览器操作：**

> 在已授权的测试页面填写非敏感测试表单并验证页面结果。优先使用已连接的 Playwright/DOM 工具；只有原生窗口或无法通过 DOM 操作的部分才使用桌面 MCP。

**覆盖率 GUI：**

> 打开我指定的覆盖率测试 GUI，检查构建、运行测试、生成报告三个步骤对应的按钮和状态。先只读取界面，不执行构建或覆盖任何报告文件。

## 6. 提高准确率的操作规则

1. **UIA/AX 优先**：按控件名称、角色、状态和唯一 ID 操作；找不到才截图/OCR。
2. **新鲜截图**：窗口变化后重新获取截图和坐标，禁止复用过期坐标。
3. **每步验证**：重新读取 UI 或文件/业务结果，区分“已发送操作”和“完成任务”。
4. **处理 DPI/Retina/多屏**：使用 MCP 返回的坐标系与显示器偏移；不要把截图像素直接当作屏幕逻辑坐标。
5. **有限重试**：失败重新观察，不盲目重复点击、提交或发送。
6. **敏感操作确认**：删除、覆盖、付款、消息发送、安装、权限变更和数据外发前先向用户明确确认。

## 7. 常见故障排查

| 现象 | 排查 |
| --- | --- |
| `nova` 未连接 | 检查绝对路径、二进制架构、CLI 注册与重启会话；确认 direct stdio **无 `mcp` 参数** |
| 无法截图（macOS） | 检查“屏幕与系统音频录制”权限是否授予实际宿主进程，重启并重试 |
| 无法点击（macOS） | 检查“辅助功能”权限，确认应用处于可交互会话 |
| 点击偏移 | 检查 Windows 缩放、macOS Retina、外接屏幕和截图坐标映射 |
| WSL 中无法操作 Windows | 在 Windows 原生进程运行 Nova 并建立正确桥接，或直接使用 Windows 原生 Claude/Codex |
| 只有 MCP 没有 Skill | 检查 OpenAS 是否更新并已在对应客户端加载 Skill；MCP 和 Skill 是两个独立组件 |
| UIA/AX 找不到按钮 | 截图、局部放大或 OCR 兜底；无法确认唯一目标就停止 |
| 操作被重复执行 | 禁止盲目重试非幂等动作，先检查是否已经生效 |

## 8. 安全、费用与卸载

Nova 的开源 MIT 许可证允许免费使用和修改，分发时遵守许可证声明。AI 模型的订阅/API 费用独立计算。屏幕内容和 UI 树可能包含密码、密钥、聊天记录；只对授权窗口操作，不把敏感截图提交到仓库。若不再使用，停止 MCP、从 Claude/Codex 中删除 `nova` 注册项，并按需撤销 macOS 系统权限。**OpenAS 不负责自动撤销系统权限。**

参考：[Nova 上游 README](https://github.com/bigduu/Nova) · [OpenAS MCP 集成说明](README.md) · [OpenAS Skill](../../skills/computer-use/SKILL.md)。本手册描述配置流程，不代表已在用户的真实 Windows/macOS 机器上完成端到端测试。

Codex 项目技能可使用 `python plugins/openas/integrations/codex_skills.py install --project /path/to/customer-project` 安装，再以同一脚本的 `check --native` 核对原生发现。命令在仓库根目录执行，详见[客户演示](https://github.com/xiangguangxin/OpenAS/blob/main/docs/customer-demo.md)。
