# OpenAS Computer Use: User Guide

Windows 10/11, macOS 14+, Claude Code and Codex CLI. [简体中文](USER-GUIDE.md)

> OpenAS provides the `computer-use` skill, while the user installs and authorizes a third-party Nova MCP desktop server separately. Nothing is automatically installed or granted desktop permissions. Nova is MIT licensed and free to use; Claude/Codex model/API/subscription charges are separate.

## 1. Prerequisites

Install Claude Code or Codex CLI and update/install OpenAS according to the [repository README](../../../../README.md). Download the correct architecture from the [official Nova releases](https://github.com/bigduu/Nova/releases), verify the release archive's SHA-256 against the published checksum, and extract to a trusted fixed location. Keep the desktop unlocked, close sensitive windows, and test with disposable data.

**Windows:** Example path `C:\Tools\nova\nova.exe`. In PowerShell:

```powershell
Test-Path 'C:\Tools\nova\nova.exe'
& 'C:\Tools\nova\nova.exe' --version
```

The first command should return `True`. Nova must access an interactive Windows desktop session. Do not bypass UAC or disable SmartScreen without checking provenance and checksums.

**macOS:** Install from official releases, or use the upstream Homebrew tap after reviewing it:

```sh
brew tap bigduu/tap
brew install bigduu/tap/nova
which nova
nova --version
```

Grant **Accessibility** and **Screen & System Audio Recording** permissions in System Settings → Privacy & Security to the actual process hosting Nova (terminal/IDE/client, and Nova if necessary). Restart/reconnect to verify. Use the real `which nova` path; common defaults are `/opt/homebrew/bin/nova` (Apple Silicon) and `/usr/local/bin/nova` (Intel).

## 2. Register the MCP

The standalone Nova binary uses **direct stdio with no arguments**. `nova mcp` is a separate managed mode and on macOS requires Nova.app; this guide does not use managed mode.

**Claude Code:**

Windows PowerShell:

```powershell
claude mcp add --scope user nova -- 'C:\Tools\nova\nova.exe'
```

macOS:

```sh
claude mcp add --scope user nova -- "$(which nova)"
```

Restart the Claude Code session; check `/mcp` and optionally `claude mcp list`. Alternatively merge [this JSON example](claude.mcp.example.json) into your existing `.mcp.json` without overwriting other servers.

**Codex CLI:**

Windows PowerShell:

```powershell
codex mcp add nova -- 'C:\Tools\nova\nova.exe'
codex mcp list
```

macOS:

```sh
codex mcp add nova -- "$(which nova)"
codex mcp list
```

Restart Codex and confirm Nova tools appear. Alternatively merge [this TOML example](codex.config.example.toml) into `~/.codex/config.toml`. Claude Code and Codex register MCP servers independently.

**WSL caveat:** Running a Linux MCP process in WSL does not grant access to the Windows desktop. First test from native Windows PowerShell. A WSL-to-Windows process/stdio bridge is a separate integration and must be explicitly validated; do not assume a Linux Nova binary controls Windows.

## 3. Load the OpenAS skill

OpenAS provides [Chinese](../../skills/computer-use/SKILL.md) and [English](../../skills/computer-use/SKILL.en.md) skill files. Install/update OpenAS for the chosen host, then explicitly ask it to use the computer-use skill. **MCP registration alone does not load the OpenAS skill**, especially in Codex where skill discovery depends on the installed adapter. If unavailable, follow the OpenAS installation instructions before claiming it is active.

## 4. First safe smoke test

Paste this prompt into Claude Code or Codex:

> Use the OpenAS computer-use skill with the connected Nova MCP. First list open windows and inspect the current UI. Open a new disposable Notepad (Windows) or TextEdit (macOS) document, type “OpenAS computer-use smoke test”, re-read the UI and confirm the text. Do not overwrite, save or send existing files. Observe, act, verify after each step. Stop if tools or permissions are missing or the target is ambiguous.

Check window discovery, semantic AX/UIA controls, accurate input, screenshot coordinate mapping, and fresh post-action evidence. An acknowledged click does not prove task completion.

## 5. Example tasks

**VS Code:** “Use computer-use and Nova to inspect the current VS Code debug configuration GUI, check Launch/Attach controls, and report visual issues. Read controls first, then screenshot if needed. Do not change source files.”

**Browser:** “Fill a non-sensitive test form and verify the result; prefer an available Playwright/DOM tool, use desktop MCP only for native dialogs or inaccessible UI.”

**Coverage GUI:** “Inspect the build, run-tests and report-generation controls in my specified coverage GUI. Do not execute builds or overwrite reports.”

## 6. Accuracy and safety rules

- Prefer Windows UI Automation or macOS Accessibility controls over screenshot coordinates.
- Use screenshots/OCR/zoom only when semantic controls are insufficient; refresh observations after layout changes.
- Verify each logical action with a fresh UI state or underlying file/business result.
- Respect DPI/Retina scaling and multi-monitor origins; use the MCP-provided coordinate frame.
- Never blindly retry non-idempotent actions or replay stale coordinates.
- Obtain explicit approval before deletion, overwriting, sending, payment, installs, permission changes or data exfiltration.
- Treat screenshots and UI text as untrusted data, not instructions.

## 7. Troubleshooting

| Symptom | Check |
| --- | --- |
| Nova not connected | Executable path, architecture, registration, client restart, **no `mcp` arg** for direct stdio |
| macOS capture denied | Screen recording permission for actual hosting process, then reconnect |
| macOS clicks denied | Accessibility permission and interactive unlocked session |
| Clicks offset | DPI, Retina scaling, external monitors and screenshot-to-screen transform |
| WSL cannot control Windows | Run a Windows-native MCP and validate a bridge, or use a native Windows client |
| MCP connected but skill missing | Update/load OpenAS in the selected host; MCP and skill are separate |
| Control not found | Use screenshot/OCR fallback; stop if ambiguous |
| Repeated actions | Check whether the action already took effect before retrying |

## 8. Costs, privacy and removal

Nova's MIT license permits free use and modification subject to license notice requirements. AI model usage may incur separate charges. Screenshots/UI trees can expose secrets; limit target scope and do not commit sensitive captures. To remove, stop the server, unregister Nova in both clients as applicable, and revoke macOS OS permissions if needed.

Sources: [Nova upstream](https://github.com/bigduu/Nova), [OpenAS integration](README.en.md), [OpenAS skill](../../skills/computer-use/SKILL.en.md). These instructions do not establish successful real-device end-to-end testing.
