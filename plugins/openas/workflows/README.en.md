# Executable Codex workflows

[中文](README.md) | English

The Python adapter calls an installed, authenticated Codex CLI through the standard library. It does not install an SDK or configure client login. Commands below run from `/path/to/OpenAS/plugins/openas`; resources resolve relative to the script, while memory belongs to the explicitly named consumer project.

Follow the [language policy](../references/language.md). Chinese and English use identical task keys, routes and result enums. Put response/artifact preferences in `requirement` or the existing `constraints` list, for example `"Write reports in English; preserve the language of existing documents."` No new language-specific route or configuration is required.

## Prerequisites and development flow

Check `codex --version`, `codex login status`, and `python3 --version`. The client must support `exec`, `--ephemeral`, `--output-schema`, `-o` and the sandbox options used by the adapter. It follows existing client model settings without hard-coding a model.

The default chain is baseline/snapshots → CTO → design review → technical writing → developer → code review → host checks → verifier → final checks/scope validation. Sessions are independent and sequential. Reviews use read-only; designated authors use workspace-write. Role metadata is not a native Codex tool whitelist. Invalid output, client failure or timeout stops work; revisions are bounded to three rounds by default. The runner does not automatically install dependencies, commit, push, merge or spawn nested agents.

Use the intentional failing fixture only in a temporary copy:

```bash
harness_example=$(mktemp -d /tmp/openas-harness-example-XXXXXX)
cp -R workflows/examples/pagination-fixture "$harness_example/workspace"
python3 workflows/codex-team.py \
  --task workflows/examples/pagination-task.json \
  --workspace "$harness_example/workspace" \
  --output "$harness_example/run" \
  --timeout 240 --rounds 3 --no-memory
```

This invokes real model sessions and consumes quota. Never repair shipped fixtures in place or run real-client trials in unconditional CI. Success requires exit 0, `done=true`, `status=verified` and successful final checks, not just an optimistic summary. Set English requirements/constraints in a copied task JSON when trying English output.

## Task contract

Required keys are `requirement`, `scope`, `acceptance`, and `checks`.

- `scope` lists exact relative files, including new documents; no directory globs.
- `acceptance` preserves original user criteria.
- `checks` contains trusted argv arrays, not shell strings. Commands must not mutate source, install dependencies or operate production.
- `constraints` optionally records project and response/artifact language requirements.
- `workflow` explicitly selects a route; omission means `development`.
- `acceptance_checks` optionally maps each acceptance criterion to zero-based check indices; lengths must match and empty lists mean no machine mapping.
- `artifacts` optionally permits newly created output directories, such as `build`. They must not already exist or overlap source/scope/Git metadata; only declared artifacts are excluded from source snapshots.

Checks execute with main-process permissions; argv avoids shell parsing but does not make arbitrary commands safe. Scope is post-execution detection, not per-file access control. Do not treat it as complete isolation on valuable shared workspaces. Output must be a new directory outside the workspace, without symlinks. Snapshots include source content and POSIX modes; this is intended for small independent workspaces rather than repeated whole-repository scanning.

## Routes

| `workflow` | Execution | Delivered status |
| --- | --- | --- |
| development / repair | Full development loop; repair requires causal hypotheses/failure baseline | verified |
| direct | Developer → checks → verifier → final checks | verified |
| operations | IT edits scoped workspace configuration → review → checks/verifier | verified for configuration, not live deployment |
| documentation | Technical writer → document review → checks/verifier | verified |
| research-design | Research/requirements → solution/selection/architecture/docs → design review/revisions → checks/verifier | verified design artifacts |
| review | Host checks → read-only red-team, without repairs | reviewed |
| security-review | Host checks → read-only security review | reviewed |

`reviewed` may contain `needs_fix` and is not proof that the target is correct. Graph pass-dependencies require approval. Direct does not bypass explicitly required design review. The JS template does not automatically inherit Python routes.

## Records, failures and resumption

Outputs include versioned `state.json`, task/check logs and stage results, fingerprints, `handoff.json`, and per-criterion `acceptance.json`. Mapped acceptance passes only with related host checks and verifier approval; unmapped items remain at most reviewed, and review-route items are reported. Language changes apply to explanatory prose, never JSON keys or verdicts.

Failure kinds distinguish environment, timeout, interrupted, client failure, invalid result, scope violation, review/acceptance limits and validation. Keep logs and partial edits; no background automatic retry or automatic rollback is provided.

Resume with the original task, workspace, client, rounds and memory options:

```bash
python3 workflows/codex-team.py \
  --task /path/to/run/task.json --workspace /path/to/task-workspace \
  --output /path/to/run --resume --no-memory --rounds 3
```

Versioned resumption checks task/rules/memory and source content/permissions, reuses valid stage evidence and reruns host checks/verifier. A lock prevents simultaneous resumption. Changed rules/source reject reuse by default. After confirming changes remain authorized, `--resume --restart-stages` invalidates stage results without resetting original revision budgets or allowing changed tasks/out-of-scope edits. Old/corrupt/completed runs need a new output or manual handling. Local snapshots do not include external services or prove record authenticity.

## Graphs, memory and research/design

`graph-runner.py` validates version-1 nodes with IDs, dependencies, workspaces and tasks; `--plan` checks cycles/missing dependencies/shared writes and `--run` executes sequentially. Failed dependencies block downstream while independent nodes may continue. There is no automatic concurrency, whole-graph recovery or graph memory. `upstream_results` carries evidence, not expanded permissions.

Memory uses `--project-root` (otherwise current directory); specify the actual consumer project to avoid plugin storage. Use `--no-memory` to disable. Reviewed valid evidence can be reused; candidates cannot. `--learn` additionally consumes model quota for extraction, independent review and candidate generation, with trial/activation/feedback lifecycle described in the [memory guide](../memory/README.en.md) and [learning guide](../memory/learning.en.md). Both detailed guides are available in Chinese and English.

For `research-design`, `research_mode` must be `live` or `provided`. Live requires native completed web-search evidence and stops if unavailable; provided uses supplied material and discloses freshness gaps. The product manager writes market research and requirements; the technical writer authors four later stages with domain skills; reviewers/verifier stay read-only. It does not implement products. Exactly six declared Markdown outputs are required, with optional `design_outputs`; no artifacts directories. Review returns `revision_from` to redo the earliest affected stage and all downstream, preserving bounded per-stage budgets across resumption. See [live task](examples/research-design-task.json), [provided-material task](examples/research-design-provided-task.json) and [input brief](examples/research-design-fixture/brief.md).

`done=true/status=verified` with `verification_subject=design-artifacts` means design delivery only, not product implementation, market validation or achieved performance. The [Chinese workflow reference](README.md) contains detailed examples and historical records.

## Regression checks

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover \
  -s workflows/tests -p 'test_*.py' -v
node workflows/tests/agent-team.test.mjs
```

These use fixtures/mocks and do not establish real-client behavior. The JS file itself is a host template requiring injected functions, not an executable Agent SDK.

## Event log

Each workflow run appends `events.jsonl` in its output directory, with one UTF-8 JSON object per line. Graph workflows produce logs in each node's output directory, without a graph-wide aggregate log. No extra flag is required.

Each record contains `version` (currently 1), a consecutive `seq`, UTC ISO 8601 `time`, event `type`, and structured `data`. Event types are:

- `run.started` / `run.resumed`: workflow start or validated resume, including the route and whether stages restart.
- `stage.started` / `stage.completed` / `stage.failed`: role execution, including role, phase, step index, and completion verdict / result file or failure kind.
- `stage.reused`: a validated cached stage result was reused without calling the client again.
- `check.started` / `check.completed` / `check.failed`: host acceptance command execution, including group label, attempt number, check index, output log paths, and normal exit_code or exception kind. A nonzero exit is still completed; the workflow decides acceptance.
- `run.completed` / `run.stopped`: core workflow termination, including final status, failure information, and state/acceptance file references. Subsequent optional memory harvesting and learning are outside this log's coverage.

Only host-observed events are recorded, without model-internal tool calls, full prompts, or command output; existing evidence files retain output. Path references are relative to the run output directory, except stage result paths retain the existing absolute format. `seq` defines append order; timestamps do not define ordering or causality.

The log uses single-writer append with flush/fsync after each record; the run lock prevents concurrent resume. `--resume` preserves history and continues numbering. An existing checkpoint without a log starts at `run.resumed`, without inventing past events. Damaged or truncated logs refuse resume and remain unchanged; inspect the workspace and use a new run directory. Abrupt process loss can leave unmatched started events, and disk errors can truncate records; starts are not guaranteed to have matching ends.

`state.json` remains the recovery authority. Log appends and checkpoints are not one transaction; events never bypass source, rule, evidence, or authorization checks. Logs contain failure information and should be reviewed for sensitive content alongside other evidence before sharing. This feature does not change the native Claude plugin or JS host template.

## Backend interface and capabilities

`agent_backend.py` defines `AgentBackend`, `AgentRequest`, `AgentInvocation`, and `AgentResult`. The workflow owns prompt assembly, role access requirements, result schema validation, scope checks, and acceptance. The backend prepares execution arguments, executes one Agent request, and returns an exit code plus a normalized native-search evidence count. Host acceptance commands do not pass through the Agent backend.

The built-in `CodexBackend` preserves existing Codex CLI arguments and execution behavior. The single-task CLI accepts explicit `--backend codex` (also the default); `--client` selects an executable path, not a model or another backend. There is no built-in dsh backend, and other clients are not assumed to implement the Codex command line.

Capability IDs are `read-only`, `workspace-write`, `structured-output`, `timeout`, `cancellation`, `search-control`, `execution-events`, and `native-search-evidence`. Before startup, route requirements are checked: read-only review does not require write access; routes producing changes require write access; research-design requires search control and execution events, with native-search evidence additionally required in live mode. Missing capabilities fail without silent downgrade or permission expansion. Each actual request also validates its access mode and capabilities.

Declarations describe adapter execution contracts, not automatic client-version detection or stronger access guarantees than the client's actual sandbox. The host process executor still handles timeout and interruption by terminating the process group. Unsupported client arguments, invalid structured output, and nonzero exits remain failures.

Trusted Python callers can inject implementations through `Runner(..., backend=provider)` or `run_graph(..., backend=provider)`; ordinary task JSON cannot load backend code. Providers supply stable `name` / `version` / `capabilities` and implement `prepare(request)` and `run(invocation, execute)`. The executor requires an `AgentResult`, with final JSON and process logs written to the requested paths. Increment the provider version when execution semantics change. The `execute` callback retains host timeout/interruption handling; model prose cannot substitute for native evidence.

Backend identity and capabilities are recorded in `state.json` and run start/resume events. Resume rejects provider, version, or capability changes, including with `--restart-stages`. Older checkpoints without a backend field assume the default Codex identity but must still pass source, rule, and evidence checks. The separate optional `--learn` executor currently supports only the built-in Codex backend; enabling it with another provider fails before startup. This interface does not change the native Claude plugin or JS host template.
