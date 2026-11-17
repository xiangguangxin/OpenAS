# OpenAS GUI Agent Runtime

Independent optional Python package. Provides a bounded observe–decide–act loop, pluggable model, desktop and browser adapters, and resumable JSON checkpoints. It is **not** a daemon or independently verified autonomous agent.

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

## Artifact verification

Pass `--verifier` on the first run and resume to make completion depend on independent local file checks. Rule keys match the checkpoint's criteria, and artifact paths are relative to the configuration's root. The root defaults to the configuration's directory.

| Rule | Checks |
| --- | --- |
| `path` | A regular file inside the verifier root |
| `min_bytes` and `contains` | Minimum size (default 1) and optional UTF-8 substring |
| `fresh: true` | File is new or its SHA-256 differs from the pre-action baseline stored in the checkpoint |
| `json_fields` | A map of JSON Pointers to exact expected values |
| `run_id_pointer` | A JSON Pointer whose value must equal the checkpoint's `id` |

Use an isolated output directory for identical reproducible builds, or have the application record a run ID. An unchanged file with identical bytes fails a freshness check. Resume with the same root and rules after a baseline is captured. For `run_id_pointer`, the application must receive and write the ID returned by `openas-gui create` or `status`.

```sh
openas-gui run ./goal-state.json --nova /absolute/path/to/nova --verifier ./coverage-rules.json
openas-gui verify ./goal-state.json --verifier ./coverage-rules.json
```

`verify` uses no backend or model. It outputs one check per criterion and exits 1 for a failed check. [Legacy text rules](examples/coverage-verifier.json) and [structured coverage rules](examples/coverage-artifact-verifier.json) are available. With no verifier, the compatibility mode uses planner evidence.

## Browser goals

Install the optional browser dependencies and run the local fixture from the repository root. The fixture imitates a coverage GUI and produces a sample report.

```sh
python -m pip install -e 'packages/gui-agent-runtime[browser]'
python -m playwright install chromium
python -m http.server 8080 --bind 127.0.0.1 --directory packages/gui-agent-runtime/examples/coverage-web
```

In another shell, configure `OPENAS_GUI_API_KEY` and `OPENAS_GUI_MODEL`, then run:

```sh
work="$(mktemp -d)"
cp packages/gui-agent-runtime/examples/coverage-artifact-verifier.json "$work/rules.json"
openas-gui create "$work/state.json" \
  --goal "Build the instrumented SIL fixture, run cases, wait for success, and download the MC/DC report as coverage.json." \
  --criterion "New instrumented MC/DC report for the passed SIL cases"
openas-gui run "$work/state.json" --browser-url http://127.0.0.1:8080/ \
  --download-dir "$work" --verifier "$work/rules.json"
openas-gui verify "$work/state.json" --verifier "$work/rules.json"
```

The backend observes the current page's accessible tree. It offers semantic clicks and fills, bounded text waits, same-origin navigation and explicit downloads. Use authorized test pages and test data. The runtime uses a single Chromium page and an isolated, nonpersistent context. Browser request routing provides a same-origin filter for routed requests. It does not substitute for isolation from untrusted sites. Redirects can affect which requests the browser routes. Downloads require an existing directory, a new filename, and filesystem hard-link support for atomic publication.

Resume with the same URL, download directory, and verifier. Cookies, tabs and in-page form state are recreated. The checkpoint and downloaded artifacts survive. On an uncertain action, check its outcome and use `reconcile` before resuming. `--browser-executable` is available for a locally installed compatible Chromium.

## Token-efficient mode

The planner now sends a bounded tool summary (name, short description and argument schema), short UI summaries and a limited number of recent MCP text/image outputs. It does **not** cache schemas across stateless API requests, and it does **not** blindly batch GUI clicks: each action still requires a fresh observation and safety gating.

```sh
openas-gui run ./goal-state.json --nova /absolute/path/to/nova \
  --max-model-calls 30 --max-model-tokens 50000 \
  --max-ui-text-chars 3000 --max-images 1
```

`--max-model-calls` and `--max-model-tokens` are optional (0 means no limit). If a budget is reached, the agent **pauses** instead of retrying indefinitely. Model usage is saved in checkpoint `model_usage` and carries over to `resume`. When the provider reports `usage.prompt_tokens` and `usage.completion_tokens`, those are tracked as actual usage. If it omits usage, input is roughly estimated by character count, tracked separately, and output tokens are unknown. Token budgets are best-effort guards, not strict billing caps: a single request can overshoot a remaining budget, images have provider-specific costs, and requests that fail before returning usage may be unaccounted for. The model endpoint may bill for attempted requests.

The compact tool list currently includes the first 12 advertised MCP tools, so check tool ordering and availability before relying on less common Nova tools. For accurate before/after savings, compare `model_usage` across equivalent runs with the same model, UI, and goal. Real Nova Windows/macOS E2E testing is still outstanding.

## Agent Benchmark

```sh
openas-benchmark packages/gui-agent-runtime/examples/benchmark-suite.json \
  --repeat 3 --output ./offline-results.json
openas-benchmark packages/gui-agent-runtime/examples/live-coverage-suite.json \
  --browser-url http://127.0.0.1:8080/ --repeat 3 --output ./browser-results.json
openas-benchmark packages/gui-agent-runtime/examples/live-coverage-suite.json \
  --nova /absolute/path/to/nova --case produce-mcdc-report --output ./nova-results.json
```

Offline mode uses scripted actions, observations and token counts. The supplied suite also interrupts a run after writing its artifact and verifies that reconciliation resumes without another write. Live mode uses the configured model API and the selected backend. The Nova example requires an authorized, resettable desktop fixture with a matching workflow that can export to the directory in the goal. The included web fixture is for the browser command. Each trial starts with a new checkpoint and artifact directory. In a case's `goal`, use `{output_dir}` for that directory. The suite can set `initial_files` to seed stale artifacts, `expected_status` for the final outcome, and `expected_checks` for required Runtime check reasons.

`success_rate` is the fraction of cases matching their expected outcome. `completion_rate` counts independently verified completions among cases intended to finish. Expected rejections pass when their status and required check reasons match. The CLI returns 1 if any case fails. Live reports record calls, time, provider-reported tokens, missing usage and estimates. Scripted token counts serve only as fixtures.

Add `--experience-store PATH --experience-environment TAG` to the live command for paired baseline and experience-enabled trials. Keep the same application and model, make sure the store has relevant verified experiences, and reset any application state between trials. Trials report each variant and the number of model calls that received experience hints. Use isolated trial data and an application that resets between invocations. You can run individual cases with `--case`. Windows/macOS plus Nova verification requires a real interactive desktop.

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
