# Computer Use MCP：Windows/macOS × Claude Code/Codex

中文 | [English](README.en.md)

**可选集成，不随 OpenAS 自动安装、启动或授予权限。** 使用 [computer-use Skill](../../skills/computer-use/SKILL.md) 指导“先观察控件 → 视觉兜底 → 执行后验证”。桌面 MCP 会控制真实窗口并接触敏感信息；请先核对来源、下载校验和及权限，再明确启用。

## 推荐的跨平台服务

以 [Nova](https://github.com/bigduu/Nova) 作为首选候选：Rust 跨平台 MCP，支持 Windows UIA、macOS AX、截图/OCR、鼠标键盘、窗口和坐标映射，仓库 MIT；上游 v0.3.x 发布二进制支持 macOS 14+ 和 Windows x64/ARM64。它属于独立第三方项目，OpenAS **不捆绑或认证** 其二进制，兼容性和可靠性必须在本机测试。可对比 [Munim Computer Use](https://github.com/munimtechnologies/munim-computer-use)（Apache-2.0，支持两平台和两个客户端）及 Windows 专项 [Windows MCP](https://github.com/sbroenne/mcp-windows)（Windows UIA 优先）。

优先在用户授权的受限桌面、测试账户和可丢弃文件中进行验证。不要把 MCP 配置直接加入仓库级默认配置，避免未经授权让每个用户连接真实桌面。

## 安装与运行（在真实桌面主机上）

1. 阅读上游 release 与许可证，下载适合 OS/架构的 Nova 二进制并验证上游提供的 SHA256；也可按上游说明构建。**不要直接执行未经审查的安装脚本。**
2. 将 `nova`（macOS）或 `nova.exe`（Windows）放到可信的固定路径并运行 `nova --version`（Windows 可运行 `nova.exe --version`）。
3. macOS 在“系统设置 → 隐私与安全性”给实际 MCP 进程及必要的终端授权“辅助功能”与“屏幕和系统音频录制”；Windows 使用已解锁且有用户会话的桌面，不绕过 UAC。启动客户端和 MCP 必须能访问**同一个**图形会话；WSL 中的 `nova` 不等同于 Windows 桌面 MCP。
4. 根据下列示例注册；**两种客户端分别配置**，并使用实际可执行文件绝对路径。

### Claude Code（项目范围示例）

把 [claude.mcp.example.json](claude.mcp.example.json) 中的 `nova` 条目**合并**到目标项目 `.mcp.json`，把 `/absolute/path/to/nova` 改成 macOS 实际绝对路径；Windows 改成 `C:\\Tools\\nova\\nova.exe` 一类真实路径（JSON 中反斜线需转义）。保留已有服务，不要整文件覆盖。或者根据本机 `claude mcp add --help` 用 CLI 注册。重新连接并在 Claude Code 执行 `/mcp` 核对。

### Codex CLI（用户配置示例）

把 [codex.config.example.toml](codex.config.example.toml) 中的 `command` 改为本机绝对路径，**合并**到 `~/.codex/config.toml`，保留已有服务和设置。或在支持的版本使用：

```sh
codex mcp add nova -- /absolute/path/to/nova
codex mcp list
```

Windows 下将该路径替换为 `C:\Tools\nova\nova.exe` 形式；实际命令以本机 `codex mcp add --help` 与上游 `nova --help` 为准。Codex 与 Claude Code 不共享 MCP 注册。OpenAS Codex 工作流适配器也不会自动加载此服务。

## 精度优先验证

请在当前客户端实际发现的 MCP schema 中使用工具；不要根据 README 假定所有版本都暴露同样的操作。先 AX/UIA 读取控件（名称、状态、当前引用），后执行语义操作；失败才使用带坐标系的截图、OCR 或区域放大；每个动作后重新观察，核对状态及实际结果。鼠标坐标必须采用同次截图的映射，避免 Windows DPI、macOS Retina、负显示器坐标偏移。**MCP 返回已点击 ≠ GUI 结果正确。**

最小验收：Notepad（Windows）或 TextEdit（macOS）中输入 `OpenAS computer-use smoke test` 到新建测试文档 → 重新读取内容 → 确认正确，且不覆盖现有文件；再测失焦、同名按钮、缩放、多屏、无可读控件和权限拒绝。记录客户端/系统/MCP 版本、工具响应和行为，不记录密钥或私密截图。未运行不得声称已通过。

## 安全与撤销

截图与辅助功能接口可读取当前登录应用的敏感数据。只对授权窗口操作，使用宿主审批；不可用提示词代替操作系统沙箱。删除、覆盖、消息发送、支付、安装、外发数据等逐项确认。停止 MCP 进程并仅移除自己添加的条目，即可解除本次连接；macOS 可在系统设置撤销辅助功能/录屏权限。限制所有自动重试并避免在用户操作桌面时并发控制。

参考：[Nova](https://github.com/bigduu/Nova) · [Munim](https://github.com/munimtechnologies/munim-computer-use) · [Windows MCP](https://github.com/sbroenne/mcp-windows)。截至 2026-11-16 已核对公开文档；**尚未在目标 Windows/macOS 上运行 MCP**。