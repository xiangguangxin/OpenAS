# Computer Use MCP: Windows/macOS × Claude Code/Codex

[中文](README.md) | English

**Optional, not installed, started, registered or granted OS permissions by OpenAS.** Pair with [computer-use skill](../../skills/computer-use/SKILL.en.md) for accessibility-first targeting, visual fallback and post-action verification. A desktop MCP can control real windows and read sensitive information: review provenance, checksums and permissions before opting in.

## Cross-platform provider options

Primary candidate: [Nova](https://github.com/bigduu/Nova), a third-party MIT-licensed Rust MCP implementing Windows UIA, macOS Accessibility (AX), screenshots/OCR, pointer/keyboard, windows, and screenshot coordinate mapping; upstream v0.3.x publishes binaries for macOS 14+ and Windows x64/ARM64. OpenAS neither bundles nor certifies its executable. Verify local compatibility and reliability. Alternatives include [Munim Computer Use](https://github.com/munimtechnologies/munim-computer-use) (Apache-2.0, both OSes and clients) and Windows-specific [Windows MCP](https://github.com/sbroenne/mcp-windows) (UIA-first).

Test first on a constrained desktop, test account and disposable files. Do not add an auto-enabled repo-wide MCP registration to OpenAS itself.

## Install on the actual desktop host

1. Review the upstream release/license; download the correct OS/architecture binary and verify its published SHA256, or build from reviewed source. Do not run unreviewed installation scripts.
2. Place `nova` (macOS) or `nova.exe` (Windows) at a trusted absolute path and run `nova --version` (or `nova.exe --version`).
3. On macOS allow the actual MCP-host process and terminal as required in System Settings → Privacy & Security → Accessibility and Screen & System Audio Recording. On Windows use an unlocked interactive session; never bypass UAC. Client and MCP must access the **same** desktop session. Launching a Linux `nova` under WSL does not give Windows desktop access.
4. Register per client using the examples below. Claude Code and Codex use different configurations and each path must be adapted to the real executable.

### Claude Code (project-scoped example)

Merge the `nova` entry from [claude.mcp.example.json](claude.mcp.example.json) into the target project's `.mcp.json`, replacing `/absolute/path/to/nova` with the actual macOS path or a properly escaped absolute Windows path such as `C:\\Tools\\nova\\nova.exe`. Preserve unrelated entries. Alternatively use `claude mcp add --help` to register. Reconnect and verify in `/mcp`.

### Codex CLI (user configuration example)

Merge the [codex.config.example.toml](codex.config.example.toml) section into `~/.codex/config.toml`, preserving other settings, or in compatible CLI versions run:

```sh
codex mcp add nova -- /absolute/path/to/nova
codex mcp list
```

For Windows use an actual path such as `C:\Tools\nova\nova.exe`. Confirm the CLI flags with `codex mcp add --help` and the provider invocation with `nova --help`. Codex and Claude registrations are independent; the OpenAS Codex workflow adapter does not inject MCP automatically.

## Observe–act–verify acceptance

Use only tool names and schemas discovered in the current session. Read the AX/UIA tree, uniquely identify a control, perform a semantic action, and verify a fresh state; if no accessible control exists, use screenshot with coordinate metadata, OCR/zoom and a calibrated action. Do not reuse stale element or screenshot references. Windows DPI, macOS Retina and multiple displays must be mapped correctly. **Tool acknowledged input does not prove task success.**

Smoke test: type `OpenAS computer-use smoke test` in a fresh Notepad (Windows) or TextEdit (macOS) test document, re-read and confirm, then exit without overwriting existing content. Also test lost focus, duplicate labels, scaling, multiple monitors, sparse accessibility and denied permissions. Record OS/client/MCP versions, actual tool outputs and verified outcomes without leaking sensitive captures. Do not claim tests passed unless run on real desktops.

## Safety and rollback

Screenshots and accessibility interfaces may expose secrets in signed-in apps. Restrict scope to authorized windows, use host approval and do not mistake prompts for a real OS sandbox. Explicitly confirm delete/overwrite/send/payment/install/exfiltration steps; bound retries and avoid concurrent desktop operation. Stop the process and remove only the entry added for this service; on macOS revoke TCC permissions if needed.

Sources: [Nova](https://github.com/bigduu/Nova), [Munim](https://github.com/munimtechnologies/munim-computer-use), [Windows MCP](https://github.com/sbroenne/mcp-windows). Public documentation reviewed 2026-11-16; **no real Windows/macOS MCP session was executed**.