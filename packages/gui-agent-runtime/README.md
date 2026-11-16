# OpenAS GUI Agent Runtime

Independent optional Python package. Provides a bounded observe–decide–act loop, pluggable model/desktop adapters and v1 JSON checkpoint recovery. It is **not** a daemon or independently verified autonomous agent.

```sh
python -m pip install -e packages/gui-agent-runtime
openas-gui create ./goal-state.json --goal "Check authorized GUI" --criterion "Expected result visible"
openas-gui status ./goal-state.json
# After setting OPENAS_GUI_API_KEY and OPENAS_GUI_MODEL:
openas-gui run ./goal-state.json --nova /absolute/path/to/nova
openas-gui resume ./goal-state.json --nova /absolute/path/to/nova
```

Restart with the same checkpoint to resume. A crash during an in-flight action blocks until manual reconciliation; never blindly replays. Risky actions pause for explicit approval. Model evidence is **not independent verification**: inject a custom verifier when calling `run()` for reliable artifact checks. Existing checkpoint v1 remains readable. Existing scripts under `plugins/openas/integrations/computer-use` remain compatibility wrappers. No Windows/macOS end-to-end test has been completed.

## Phase 3: recover safely

Version 2 checkpoints migrate version 1 on write. A process-level lock prevents concurrent runs on the same checkpoint. If a process dies after dispatching a potentially non-idempotent action, the next run becomes blocked. Inspect the desktop and reconcile manually:

```sh
openas-gui reconcile ./goal-state.json --outcome executed --note "Checked the UI and confirmed the action happened"
openas-gui resume ./goal-state.json --nova /absolute/path/to/nova
```

`--outcome not-executed` is also supported. Reconciliation never replays an old action: the planner observes again and chooses a new step. This is not crash-proof external transactionality, and it does not automatically restart a process.

## Phase 4: independent local file verification

Use a JSON verifier configuration (example: [coverage-verifier.json](examples/coverage-verifier.json)). Each criterion must have an exact rule; paths are constrained to the configured root, and rules can require a minimum byte count and a UTF-8 substring.

```sh
openas-gui run ./goal-state.json --nova /absolute/path/to/nova --verifier ./coverage-verifier.json
```

Without `--verifier`, the old evidence-only verifier remains for compatibility and is **not independent**. With a verifier, the model cannot mark success until the local file rules pass. Do not use this for untrusted filesystem paths or as a security sandbox. A local report check does not establish that the GUI itself was correctly operated.

Automated tests include a **fake desktop full-goal integration test**, lock/recovery/migration cases and negative verifier tests. **No real Nova/Windows/macOS E2E test has been run**. Those still require authorized hardware and desktop access.
