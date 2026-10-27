# Native Claude hot-reload regression

[中文](hot-reload-testing.md) | English

[test_claude_hot_reload.py](../tests/test_claude_hot_reload.py) is a Python unittest **integration test requiring a real external client**. Ordinary tests explicitly skip it; mocked success is not native loading success.

## Run the test

On Linux/WSL/macOS, prepare an authenticated Claude CLI supporting streaming input/plugin commands (at least 2.1.268), then run from the OpenAS root:

```bash
OPENAS_RUN_CLAUDE_TESTS=1 PYTHONDONTWRITEBYTECODE=1 \
  python3 -m unittest discover -s tests -p 'test_claude_hot_reload.py' -v
```

This invokes a real model and consumes quota. It does not install/login/configure the client. Once enabled, missing/old CLI, authentication/network failures, or protocol incompatibility fail rather than switching to mocks or skip.

| Variable | Default | Purpose |
| --- | --- | --- |
| `OPENAS_CLAUDE_BIN` | `claude` | Existing executable name/path |
| `OPENAS_CLAUDE_TIMEOUT` | `120` seconds | Timeout per protocol request/turn; terminates the process group |
| `OPENAS_CLAUDE_BUDGET_USD` | `1.00` | CLI per-run budget; hitting it fails rather than weakening assertions |
| `OPENAS_CLAUDE_REPORT` | No file | Minimal success receipt; parent must exist and file must not exist |

To retain a real receipt:

```bash
OPENAS_RUN_CLAUDE_TESTS=1 \
OPENAS_CLAUDE_REPORT=/tmp/openas-native-reload-receipt.json \
PYTHONDONTWRITEBYTECODE=1 \
  python3 -m unittest discover -s tests -p 'test_claude_hot_reload.py' -v
```

Only completed assertions produce a receipt, containing client version, session ID, old/new markers, and native command identity, not authentication, prompts, or full logs. Failure/skip produces no passed receipt, existing files are not overwritten, and copied receipts do not prove current-version execution.

## Recorded execution: 2026-10-21

- Ordinary tests: 14 passed and 1 native case skipped in tests/; another 25 workflow regressions passed.
- Explicit `OPENAS_RUN_CLAUDE_TESTS=1` exited 1 because the real Claude CLI was unavailable. No model was called and no success receipt was written.
- Thus local test implementation and false-positive defenses were checked, while native reload remained unverified. The 39 passing tests did not constitute a native pass.

These are historical observations, not new results from translating this guide.

## Required behavior

1. Copy the current plugin into a temporary directory and add a random-marker-only `reload-probe` skill. Do not modify source plugin, consumer projects, or marketplace configuration.
2. Run real `claude plugin validate`, then start exactly one long-lived `--plugin-dir` Claude process with bidirectional stream-json.
3. Invoke `/openas:reload-probe` and accept only the exact old marker in a successful final result. Requests omit expected markers; echoed messages/logs/model explanations cannot pass.
4. Atomically replace temporary skill content and send `/reload-plugins`. Require native `local_command=reload-plugins` evidence and a successful plugin-loading summary. Cache blocks, loading errors, and model claims alone fail; do not automatically add `--force`.
5. Invoke the same skill and check the new marker. All three turns need the same nonempty session ID, unchanged PID, and a process still alive at the end.
6. Clean process group/temp files on success or failure. Without a real client, do not simulate reload through another process or manual file rereading.

Disable file-discovered sources, tools, and external MCP, testing only the explicit plugin. Do not bypass permissions. Reuse existing authentication rather than bare mode that skips subscription authentication. Retain the client's default available model. The case needs no model file writes or command execution.

## Layers and limits

Five local [stream tests](../tests/test_claude_stream.py) check rejection of errors, stale content, fake model reload, changed sessions, plus pipe/timeouts/cleanup. Their subprocesses are fake protocol endpoints, not real Claude validation.

The native case covers skill-content reload in a headless session, not terminal UI, agent updates, MCP, enable/disable, or uninstall. Automatic file discovery may already refresh content; the test establishes same-session availability after native reload, not that reload is the only mechanism.

Protocol/result fields may change. Unknown fields should fail for version investigation, not removal of native-command/session-continuity assertions. `scripts/claude_stream.py` is a focused test driver, not a general SDK.

Sources: [headless reload](https://code.claude.com/docs/en/plugins/cli-reference), [programmatic CLI](https://code.claude.com/docs/en/headless), [CLI flags](https://code.claude.com/docs/en/cli-reference), [SDK control protocol](https://github.com/anthropics/claude-agent-sdk-python/blob/main/src/claude_agent_sdk/_internal/query.py).

## Separate native installation lifecycle test

`test_claude_lifecycle.py` uses a temporary project, isolated `CLAUDE_CONFIG_DIR` and plugin cache to validate local marketplace installation, disable/enable/uninstall, and preservation of project memory. It runs management commands without model calls or reusing user authentication, and does not establish session reload.

```bash
OPENAS_RUN_CLAUDE_LIFECYCLE=1 \
  python3 -m unittest discover -s tests -p 'test_claude_lifecycle.py' -v
```

Use `OPENAS_CLAUDE_BIN` for the client and `OPENAS_CLAUDE_LIFECYCLE_REPORT` for a new receipt path. The documented environment lacked Claude CLI, so native success remained unavailable and default CI skips it. Command/JSON format sources: [plugin commands](https://code.claude.com/docs/en/plugins/cli-reference); isolation: [environment variables](https://code.claude.com/docs/en/env-vars).
