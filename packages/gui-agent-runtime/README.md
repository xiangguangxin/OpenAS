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
