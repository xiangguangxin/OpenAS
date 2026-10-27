# MCP integration quick start for Claude Code

[中文](QUICKSTART.md) | English

Use `setup_mcp.py` in this directory with Python 3.9+; it uses only the standard library and works from source or an installed plugin. It reads the three adjacent service templates without installing dependencies or registering other clients. Other clients require their own configuration formats, not the generated Claude Code configuration.

## 1. Select services and prepare the environment

| Service | Preparation | Details |
| --- | --- | --- |
| `playwright` | Node/npm, a runnable browser and system dependencies; network for initial package download | [Playwright](playwright/README.en.md) |
| `github` | Official `github-mcp-server` binary on PATH and your own repository-read token | [GitHub](github/README.en.md) |
| `context7` | Remote-service access and your own Context7 API key | [Context7](context7/README.en.md) |

Configure and check in the same environment that starts Claude Code. Native Windows and WSL have independent PATHs, dependencies, and variables. Python may be `python3`, `python`, or `py -3`; examples use `python3`.

## 2. Merge project configuration

From the OpenAS repository root, replace `/path/to/customer-project` with the actual project. For an installed plugin use the actual location of its `integrations/setup_mcp.py`.

```bash
python3 plugins/openas/integrations/setup_mcp.py configure --project /path/to/customer-project --services all
```

Replace `all` with selected names such as `--services github context7` if needed.

The tool merges selected entries into `.mcp.json`, retaining unrelated services and top-level fields. Repeating identical configuration does not rewrite it. Different same-name entries, invalid JSON, or symlinks stop processing for manual inspection. Existing custom services are not overwritten, and real credentials are not written. Inspect the generated file in an editor.

## 3. Supply credentials in the current environment

Playwright needs neither credential below. Set variables only for selected services. Never place actual values in JSON, commits, or acceptance reports. The tool does not load `.env` automatically.

Bash / WSL hidden input avoids placing values directly in shell history:

```bash
read -r -s -p 'GitHub token: ' OPENAS_GITHUB_TOKEN
export OPENAS_GITHUB_TOKEN
read -r -s -p 'Context7 API key: ' OPENAS_CONTEXT7_API_KEY
export OPENAS_CONTEXT7_API_KEY
```

PowerShell can use interactive input and process environment variables:

```powershell
$githubSecret = Read-Host 'GitHub token' -AsSecureString
$env:OPENAS_GITHUB_TOKEN = [System.Net.NetworkCredential]::new('', $githubSecret).Password
$context7Secret = Read-Host 'Context7 API key' -AsSecureString
$env:OPENAS_CONTEXT7_API_KEY = [System.Net.NetworkCredential]::new('', $context7Secret).Password
Remove-Variable githubSecret, context7Secret
```

These settings affect only this terminal and subsequently started processes. Start Claude Code from this terminal; an already running client does not inherit new variables. For long-term use, supply them through your credential-management process.

## 4. Run local preflight

```bash
python3 plugins/openas/integrations/setup_mcp.py check --project /path/to/customer-project --services all
```

Preflight checks selected-template configuration, Claude Code and required executables on PATH, Playwright's minimum Node version, and nonempty required variables. It runs only `node --version`, without starting services, downloading packages, exposing credentials, or validating credentials/network access.

Exit `0` means automated preflight passed, `1` means failed checks, and `2` means argument/configuration processing failed. Complete `MANUAL` checks in the actual client; preflight success is not an MCP connection. Custom configurations differing from templates need manual review, not an assumption that they are unusable.

## 5. Connect and validate each service

Enter the customer project and start/restart `claude` from the credential-configured terminal. Complete requested trust confirmation and inspect `/mcp`; `claude mcp list` can assist diagnosis. Existing role allowlist/permission rules still apply.

Replace example targets with actual authorized objects:

| Service | Acceptance task for the assistant | Pass criteria |
| --- | --- | --- |
| Playwright | Use Playwright MCP to open my running local test page, read its title and one visible button, perform a side-effect-free action, verify the result, and close the browser. | Real browser operation with expected/actual results; missing browser/dependencies do not pass. |
| GitHub | Read metadata for my authorized owner/repo and its README at a specified commit. Verify identity, path, and commit, and confirm the connection exposes read-only tools. Do not modify remote content. | Correct objects read with explicit source/ref; the project template remains read-only. |
| Context7 | Find a public library used by the project, confirm library ID, query one specific API, and report source and applicable version, explicitly noting unavailable versions. | Relevant documentation retrieved with version coverage; missing versions are not called verified. |

Connection status alone does not replace these tasks. Record each service separately:

```text
Service / client and version:
Server version or hosted-query time:
Target (URL, repository/ref, library/target version):
Actual tools called:
Steps, expected result, actual result:
Result: passed / failed / not run
Limitations and remaining work (no credentials):
```

## Troubleshooting and removal

| Symptom | Investigation |
| --- | --- |
| Command not found | Prepare dependencies and PATH in the actual client environment; distinguish Windows from WSL. |
| Missing variables/authentication failure | Start from the configured terminal, then check token/key validity and permissions. |
| HTTP timeout/npm download failure | Inspect network, proxy, and service reachability in the customer environment. |
| Connected service but no role tools | Inspect actual tools/toolsets, client policies, and role allowlists. |
| Playwright startup failure | Check browser/system dependencies against the pinned package's upstream guidance. |
| Repository read failure | Check owner/repo, private-repository access, and organization requirements. |

Remove only service entries added to the target `.mcp.json`, preserving other configuration. Restart the client and stop corresponding processes. Revoke credentials with the service if necessary; removing configuration does not revoke tokens/keys.

Configuration reference: [Claude Code MCP documentation](https://code.claude.com/docs/en/mcp). This guide describes configuration and acceptance; no real connections have been tested using customer credentials.
