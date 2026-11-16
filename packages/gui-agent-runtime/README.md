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

## Token-efficient mode

The planner now sends a bounded tool summary (name, short description and argument schema), short UI summaries and a limited number of recent MCP text/image outputs. It does **not** cache schemas across stateless API requests, and it does **not** blindly batch GUI clicks: each action still requires a fresh observation and safety gating.

```sh
openas-gui run ./goal-state.json --nova /absolute/path/to/nova \
  --max-model-calls 30 --max-model-tokens 50000 \
  --max-ui-text-chars 3000 --max-images 1
```

`--max-model-calls` and `--max-model-tokens` are optional (0 means no limit). If a budget is reached, the agent **pauses** instead of retrying indefinitely. Model usage is saved in checkpoint `model_usage` and carries over to `resume`. When the provider reports `usage.prompt_tokens` and `usage.completion_tokens`, those are tracked as actual usage. If it omits usage, input is roughly estimated by character count, tracked separately, and output tokens are unknown. Token budgets are best-effort guards, not strict billing caps: a single request can overshoot a remaining budget, images have provider-specific costs, and requests that fail before returning usage may be unaccounted for. The model endpoint may bill for attempted requests.

The compact tool list currently includes the first 12 advertised MCP tools, so check tool ordering and availability before relying on less common Nova tools. For accurate before/after savings, compare `model_usage` across equivalent runs with the same model, UI, and goal. Real Nova Windows/macOS E2E testing is still outstanding.

## Offline Agent Benchmark (first stage)

```sh
openas-benchmark packages/gui-agent-runtime/examples/benchmark-suite.json \
  --repeat 3 --output ./benchmark-results.json
```

Runs deterministic **synthetic** desktop/model scenarios using the actual agent loop and local verifier. Reports per-case pass/fail, actions, synthetic model calls/tokens, duration and aggregate success rate. Synthetic token counts are **fixtures**, not measured API usage or evidence of real-world savings. Scenarios execute in isolated temporary directories; do not put secrets in fixtures. Real Nova/Windows/macOS benchmarks require a separate runner and authorized environment.

## Experience Memory (first stage)

Experiences are **explicitly curated** from completed checkpoints only after a trusted local file verifier passes again. They contain a short goal, criteria, environment tag and human note; **no raw screenshots, model prompts, tool payloads, credentials or action replay scripts**. Search returns hints, never commands for automatic execution.

```sh
openas-experience --store ./experiences.json add ./goal-state.json \
  --verifier ./coverage-verifier.json --environment win11-coverage-v1 \
  --note "Coverage report independently inspected"
openas-experience --store ./experiences.json search "coverage report" \
  --environment win11-coverage-v1
```

Only use verifier configurations you trust. The store is a local file with no multi-process locking, access control, or encryption; keep it in a trusted directory and do not share it with untrusted users. Environment tags are exact matches and retrieval is simple word overlap (not embeddings). By default experiences are **not injected into the planner**, and success in one environment does not authorize replay in another.

## Opt-in experience-assisted planning and lifecycle

```sh
openas-gui run ./goal-state.json --nova /absolute/path/to/nova \
  --experience-store ./experiences.json --experience-environment win11-coverage-v1
```

When both flags are supplied, the planner automatically searches the **local** store for up to two relevant, independently verified experiences in the exact environment. Hints are bounded and explicitly marked as **untrusted historical context**; the model must reobserve and independently verify current outcomes. No actions are replayed from memory. Omitting the flags disables retrieval.

Experience confidence decays exponentially (default 30-day half-life), and experiences become ineligible after 90 days. Search automatically excludes expired, invalidated, or low-confidence records; `expire` persists their invalidated status without deleting audit history. These are conservative policy defaults, not measured reliability probabilities. Two **explicitly recorded, independently verified** failures invalidate an experience; runtime planner errors alone do not count as verified failures.

```sh
openas-experience --store ./experiences.json feedback EXPERIENCE_ID \
  --outcome failure --note "Independent acceptance failed in matching environment"
openas-experience --store ./experiences.json invalidate EXPERIENCE_ID \
  --reason "GUI version changed"
openas-experience --store ./experiences.json expire
```

The CLI cannot independently establish that feedback is true: operators must check their evidence before submitting feedback. Environment tags should include relevant OS, app and workflow versions. The store remains single-writer local JSON; avoid concurrent writers. Hints may include operator notes, so do not store secrets. This is a first-stage retrieval/lifecycle implementation, not autonomous experience learning or real-world success-rate proof.
