# Persistent GUI Goal Agent Runtime

[中文说明](RUNTIME.md) · [Nova MCP user guide](USER-GUIDE.en.md)

This is an **opt-in, executable Python agent loop**, separate from the instructional `gui-goal-executor` skill. It includes an LLM decision adapter, Nova MCP stdio transport, an observe–decide–act–verify cycle, atomic on-disk checkpoints, step budgets, approval pauses and conservative crash handling.

**Important limitations:** this is an initial runtime, not a production-hardened autonomous desktop controller. It requires a trusted Nova binary, a separately configured OpenAI-compatible multimodal chat-completions endpoint, an interactive unlocked desktop and user authorization. It does **not** automatically inherit Claude Code/Codex subscriptions or their MCP registrations. It does not run in the background after the host process exits; restart the command to resume. There are no real Windows/macOS end-to-end tests yet.

## Modular package installation (recommended)

The runtime is now maintained separately in [Praxis](https://github.com/xiangguangxin/Praxis). These OpenAS scripts remain compatibility wrappers requiring Praxis to be installed first:

```sh
python -m pip install git+https://github.com/xiangguangxin/Praxis.git
praxis create ./goal-state.json --goal "Inspect authorized GUI" --criterion "Expected result visible"
praxis status ./goal-state.json
# Configure model credentials, then:
praxis run ./goal-state.json --nova /absolute/path/to/nova
praxis resume ./goal-state.json --nova /absolute/path/to/nova
```

## Setup

Use Python 3.10+ and a [trusted Nova executable](https://github.com/bigduu/Nova/releases). In a native Windows PowerShell or macOS terminal, navigate to `plugins/openas/integrations/computer-use`. WSL is not an automatic bridge to the Windows GUI.

Create a checkpoint (once):

```sh
python goal_runtime.py create ./goal-state.json --goal "Inspect the authorized GUI and verify the expected test result" --criterion "Expected test result visible" --max-steps 40
```

Set credentials **in your local terminal**, never in the repo:

```sh
# macOS / POSIX:
export PRAXIS_API_KEY="your-model-api-key"
export PRAXIS_MODEL="your-multimodal-model-id"
# Optional: export PRAXIS_API_URL="https://your-provider.example/v1/chat/completions"
python live_goal_agent.py ./goal-state.json --nova /absolute/path/to/nova
```

```powershell
# Windows PowerShell:
$env:PRAXIS_API_KEY="your-model-api-key"
$env:PRAXIS_MODEL="your-multimodal-model-id"
python .\live_goal_agent.py .\goal-state.json --nova "C:\Tools\nova\nova.exe"
```

The model endpoint must support **chat completions JSON response format and multimodal image inputs**. An API model may incur fees. The runtime discovers Nova tools through `tools/list`; it does not assume a particular tool schema.

## Cross-session recovery

After the process exits, run the same `live_goal_agent.py` command with the **same checkpoint**. The runtime reads progress and re-observes the desktop. No stale screen coordinates are persisted. If a crash happened with an action in flight, the checkpoint becomes **blocked** for manual reconciliation rather than replaying an uncertain click. A completed or blocked task cannot be restarted automatically; start a new checkpoint after reviewing the real-world state.

When a high-impact action is requested, execution pauses with `pending_approval`. Review the intended operation and current UI independently; if you explicitly approve that exact action, rerun with `--approve-pending`. This approval applies only to the matching next action. Do not approve a task you cannot independently inspect.

The checkpoint stores summaries and action names, not screenshots, tool arguments or API keys. It may still reveal the goal and progress: store it in a private directory. **Do not run two processes against the same checkpoint concurrently.** No process lock is implemented yet.

## Safety and verification

- The LLM may make mistakes; evidence returned by the planner is **not independently validated by the runtime**. Treat goal completion as a model assertion until independently checked.
- High-risk actions are paused by an impact classifier and tool-name checks; these are defense-in-depth, **not a complete security sandbox**. Use a disposable test desktop with no sensitive accounts.
- Screenshot images are sent to the configured model API. Do not expose private screens or credentials.
- No UAC bypass, CAPTCHA bypass or security prompt automation.
- Default budget is 40 successful/failed tool calls and 3 consecutive failures. MCP calls have a 30-second response timeout; the model call has a 90-second timeout.
- The Python tests use fake desktop/model adapters. They do not demonstrate that a particular Nova release works on your machine.

## Files

- `goal_runtime.py`: generic state machine, atomic checkpointing, approvals, resume rules and CLI create/status.
- `live_goal_agent.py`: real MCP stdio transport and LLM planner adapter.
- `tests/test_gui_goal_runtime.py`: mocked regression tests.

This runtime complements, but does not replace, [gui-goal-executor Skill](../../skills/gui-goal-executor/SKILL.en.md).

## Phase 3 / Phase 4: recovery and verification

Version 2 checkpoints migrate v1 on write. A cross-process lock prevents two runners from using one checkpoint. Uncertain in-flight actions remain blocked until explicitly reconciled:

```sh
praxis reconcile ./goal-state.json --outcome executed --note "Checked desktop state"
praxis resume ./goal-state.json --nova /absolute/path/to/nova
```

Use `--outcome not-executed` when appropriate; neither option blindly replays the old action. Add `--verifier ./coverage-verifier.json` for independent local file checks. Without it, completion still relies on model-supplied evidence. Fake-desktop E2E and unit tests exist, but no real Nova/Windows/macOS E2E has been run.


## Artifact verification

`--verifier` maps checkpoint criteria to local rules. Existing `path`, `min_bytes`, and `contains` rules remain usable. `json_fields` asserts exact values by JSON Pointer, `run_id_pointer` matches the checkpoint ID inside a report, and `fresh: true` captures the artifact fingerprint before the first action. Keep the same configuration and root on resume. Identical regenerated bytes cannot be distinguished from a stale report with freshness alone. Use a new output directory or include a per-run ID.

```sh
praxis verify ./goal-state.json --verifier ./coverage-rules.json
```

This command prints criterion-level outcomes without invoking either a model or a desktop backend. Missing or stale artifacts, invalid JSON, and field mismatches yield a nonzero exit. See the [runtime package guide](https://github.com/xiangguangxin/Praxis/blob/main/RUNTIME.md#artifact-verification) for rules and examples.

## Browser goals

Install the optional dependency and Chromium, then create a checkpoint with criteria and start on a test page.

```sh
python -m pip install 'praxis-agent-runtime[browser] @ git+https://github.com/xiangguangxin/Praxis.git'
python -m playwright install chromium
praxis run ./goal-state.json --browser-url http://127.0.0.1:8080/ \
  --download-dir ./reports --verifier ./coverage-rules.json
```

The download directory must already exist. The runtime publishes downloads under new filenames and uses semantic page snapshots, locators, and bounded waits. Resume with the same start URL, download directory, and verifier. Each invocation uses a fresh Chromium context, so reobserve page state. Login state and tabs are not persisted. See the [runtime package guide](https://github.com/xiangguangxin/Praxis/blob/main/RUNTIME.md#browser-goals) for scope and the local coverage fixture.

## LiteLLM gateway

Set `LITELLM_API_KEY` in the OpenAS process and pass the gateway URL and configured model alias.

```sh
praxis run ./goal-state.json --nova /absolute/path/to/nova \
  --litellm-base-url http://127.0.0.1:4000 --model openas-planner
```

These options also apply to `resume` and live `praxis-benchmark` runs. You can use `PRAXIS_LITELLM_BASE_URL` and `PRAXIS_MODEL` instead of the flags. Use a gateway model with JSON mode support and image input support for screenshot tasks. See the [runtime package guide](https://github.com/xiangguangxin/Praxis/blob/main/RUNTIME.md#litellm-gateway) for gateway setup and browser examples.

## Task evaluation

`praxis-benchmark` defaults to isolated offline cases. Select `--nova` or `--browser-url` for a real backend and the configured model. Add `--experience-store` with `--experience-environment` for paired trials with retrieval off and on. Live evaluation requires a test environment and a model API. The report includes expected rejections, positive-goal completion, elapsed time, and reported usage. See the [runtime package guide](https://github.com/xiangguangxin/Praxis/blob/main/RUNTIME.md#agent-benchmark) for the suite format and commands.


> Compatibility: Praxis accepts the previous `OPENAS_GUI_*` environment variables and `openas-gui` command aliases. OpenAS no longer owns or tests the independent Runtime package.
