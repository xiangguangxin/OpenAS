# Persistent GUI Goal Agent Runtime

[中文说明](RUNTIME.md) · [Nova MCP user guide](USER-GUIDE.en.md)

This is an **opt-in, executable Python agent loop**, separate from the instructional `gui-goal-executor` skill. It includes an LLM decision adapter, Nova MCP stdio transport, an observe–decide–act–verify cycle, atomic on-disk checkpoints, step budgets, approval pauses and conservative crash handling.

**Important limitations:** this is an initial runtime, not a production-hardened autonomous desktop controller. It requires a trusted Nova binary, a separately configured OpenAI-compatible multimodal chat-completions endpoint, an interactive unlocked desktop and user authorization. It does **not** automatically inherit Claude Code/Codex subscriptions or their MCP registrations. It does not run in the background after the host process exits; restart the command to resume. There are no real Windows/macOS end-to-end tests yet.

## Modular package installation (recommended)

The runtime is now in [`packages/gui-agent-runtime`](../../../../packages/gui-agent-runtime/README.md). The old scripts are compatibility wrappers requiring the package to be installed first:

```sh
python -m pip install -e packages/gui-agent-runtime
openas-gui create ./goal-state.json --goal "Inspect authorized GUI" --criterion "Expected result visible"
openas-gui status ./goal-state.json
# Configure model credentials, then:
openas-gui run ./goal-state.json --nova /absolute/path/to/nova
openas-gui resume ./goal-state.json --nova /absolute/path/to/nova
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
export OPENAS_GUI_API_KEY="your-model-api-key"
export OPENAS_GUI_MODEL="your-multimodal-model-id"
# Optional: export OPENAS_GUI_API_URL="https://your-provider.example/v1/chat/completions"
python live_goal_agent.py ./goal-state.json --nova /absolute/path/to/nova
```

```powershell
# Windows PowerShell:
$env:OPENAS_GUI_API_KEY="your-model-api-key"
$env:OPENAS_GUI_MODEL="your-multimodal-model-id"
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
