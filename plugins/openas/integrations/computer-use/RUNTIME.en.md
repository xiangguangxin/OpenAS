# Praxis standalone GUI runtime and OpenAS integration

[中文](RUNTIME.md) · [Nova setup](USER-GUIDE.en.md) · [Customer demo](https://github.com/xiangguangxin/OpenAS/blob/main/docs/customer-demo.md)

The independent desktop/browser loop, checkpoints, approvals, recovery and artifact verification are maintained in [Praxis](https://github.com/xiangguangxin/Praxis). OpenAS retains orchestration skills, integration guidance and legacy wrappers, not the runtime implementation or its tests.

## Install and run

```sh
python -m pip install git+https://github.com/xiangguangxin/Praxis.git
praxis create ./goal-state.json --goal "Complete the authorized GUI task" --criterion "Independent artifact checks pass"
praxis run ./goal-state.json --nova /absolute/path/to/nova --verifier ./rules.json
praxis status ./goal-state.json
praxis resume ./goal-state.json --nova /absolute/path/to/nova --verifier ./rules.json
```

For a demo, pin the full commit actually tested using `@FULL_COMMIT_SHA` in the installation URL. Configure the model API and Nova separately: Claude/Codex subscriptions, MCP registrations and permissions are not inherited. Nova requires an unlocked native Windows/macOS interactive desktop. Restart commands explicitly; this is not a background daemon.

Legacy `python goal_runtime.py create/status/...` and `python live_goal_agent.py checkpoint --nova ...` entry points require Praxis installed. Prefer the `praxis` CLI for new tasks. Use [current Praxis documentation](https://github.com/xiangguangxin/Praxis/blob/main/RUNTIME.md) and local help for environment variables, LiteLLM and flags.

## Recovery and verification

Resume with the original checkpoint, backend configuration, download directory and verifier. Praxis owns interprocess locks, unknown-action reconciliation and approvals. Never bypass pauses or blindly replay actions.

```sh
praxis reconcile ./goal-state.json --outcome executed --note "Checked the actual outcome"
praxis verify ./goal-state.json --verifier ./rules.json
```

Verifier rules can check files, JSON fields, run IDs and freshness for each criterion. Model completion without a verifier is not independent business acceptance. See [artifact verification](https://github.com/xiangguangxin/Praxis/blob/main/RUNTIME.md#artifact-verification).

## Browser goals

```sh
python -m pip install 'praxis-agent-runtime[browser] @ git+https://github.com/xiangguangxin/Praxis.git'
python -m playwright install chromium
praxis run ./goal-state.json --browser-url http://127.0.0.1:8080 --download-dir ./downloads --verifier ./rules.json
```

Prepare a new download location; re-observe pages after recovery rather than assuming persistent tabs or login. The [customer guide](https://github.com/xiangguangxin/OpenAS/blob/main/docs/customer-demo.md) provides a runnable build/test/download fixture and opt-in real acceptance runner. Its test report is not a production coverage report.

## Evidence boundary

OpenAS local HTTP tests, mock clients and Windows workflow smoke cover their own contracts, not real browser/Nova/customer-application E2E. Run `scripts/customer_acceptance.py` in the target environment, retaining actual checkpoints, independent checks and human business review. See the [customer readiness receipt](../../workflows/evidence/2026-11-19-customer-readiness/receipt.json).
