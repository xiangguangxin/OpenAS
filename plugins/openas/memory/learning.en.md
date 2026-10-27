# Task reflection, lesson review, and project-skill evolution

[中文](learning.md) | English

The four stages are observation capture → extraction/independent review → candidate generation/validation → evaluation, disabling, and rollback. They reuse project-memory evidence checks without training model parameters or modifying bundled skills, roles, CLAUDE.md, or permissions.

Use Python 3.10+ on Linux/WSL. Model extraction, review, and trials require authenticated Codex CLI support for existing workflow arguments and consume quota. Only the Python single-task runner is automatically integrated; JS templates, graph runs, and ordinary chats have no background learning process.

## Stage 1: capture observations

With memory enabled, task completion captures success/failure observations: status, failure kind, check exit codes, recovery count, and input/output snapshot summaries. Raw logs, full conversations, task prose, and failure messages do not enter observations directly. Identical observations are deduplicated.

```bash
# Run from the OpenAS repository root; replace all example paths.
python3 plugins/openas/workflows/codex-team.py \
  --task /path/to/task.json \
  --workspace /path/to/task-worktree \
  --output /path/to/private-run-output \
  --project-root /path/to/consumer-project \
  --learn
```

`--learn` adds read-only model extraction/independent review after the task and drafts skills for accepted lessons. Omit it to capture machine observations without extra model calls. `--no-memory` disables memory, capture, and project-skill reuse and cannot combine with `--learn`.

Memory must be outside task workspace; learning output must be outside the entire consumer-project. Prefer independent worktrees/private run directories. Overlap disables memory under scope protection; explicit `--learn` fails before execution.

Timeout, interruption, scope violation, client/environment errors, or invalid output capture observations only, without further model calls. Other task failures may be reflected on, but an exit code proves failure, not its cause. Learning errors record `learning_warning` without changing task acceptance or undoing completed candidates.

Task and recent stage results are temporary model context; private prompts/results/logs remain in output. Long-term memory receives filtered candidates only. Observations/manual JSON are not tamper-proof and must come from trusted tasks.

Capture an existing trusted run:

```bash
python3 plugins/openas/skills/project-memory/scripts/learning.py \
  --root /path/to/consumer-project capture /path/to/private-run-output/state.json
```

Use the returned observation `id` for separate extraction with an already authenticated client:

```bash
python3 plugins/openas/workflows/learning_cycle.py \
  --root /path/to/consumer-project --output /path/to/new-private-reflection \
  reflect OBSERVATION_ID
```

## Stage 2: extract and independently review lessons

Candidates contain `key`, `scope`, `statement`, `trigger`, `cause`, `procedure`, `validation`, `limitations`, `tags`, `author`, `observation_ids`, and `evidence`. Unconfirmed causes remain hypotheses; retry success is not a general repair method.

- Validate required fields, lengths, project-local evidence, and source hashes; reject obvious token/private-key patterns. Pattern detection is incomplete, so semantic review must still check sensitive content.
- Identical proposals are idempotent. Same-scope keyword-set similarity above the threshold marks `similar` for review, not semantic deduplication.
- Existing accepted key/scope produces `conflict` rather than overwrite. Verify/retire old knowledge before accepting replacement.
- Author/reviewer identifiers must differ. Automatic mode uses separate ephemeral read-only sessions, and review checks originals rather than accepting author summaries.
- Accepted lessons enter existing records.json, with procedures/applicability in linked receipts. Changed evidence or explicit original sources exclude old knowledge later.

Automatic review requires all `supported`, `scoped`, `reusable`, `no_secrets`, and `conflicts_resolved` checks true. Distinct identifiers/sessions do not authenticate human identities; trust the caller.

Manual or other hosts may supply proposal/review JSON:

```bash
python3 plugins/openas/skills/project-memory/scripts/learning.py --root /path/to/consumer-project propose /path/to/proposal.json
python3 plugins/openas/skills/project-memory/scripts/learning.py --root /path/to/consumer-project review LESSON_ID /path/to/review.json
python3 plugins/openas/skills/project-memory/scripts/learning.py --root /path/to/consumer-project retire OLD_LESSON_ID --reason 'Source changed; replacement lesson checked'
```

Build `evidence` from actual project files via `Memory.evidence()`; see [project memory](README.en.md). Example review:

```json
{
  "verdict": "approve",
  "reviewer": "actual-independent-reviewer",
  "reason": "Original sources and reproduction checked; conclusion limited to declared scope",
  "checks": {
    "supported": true,
    "scoped": true,
    "reusable": true,
    "no_secrets": true,
    "conflicts_resolved": true
  }
}
```

This illustrates fields, not actual review evidence. Use reject with reasons when requirements are unmet.

## Stage 3: draft, trial, and activate skills

Automatic learning generates versioned project-local `SKILL.md` from reviewed lessons, including triggers, prerequisites, steps, checks, and limits. One accepted lesson suffices for a draft, not proven maturity; trials/review determine suitability rather than frequency.

Combine accepted same-scope lessons if appropriate:

```bash
python3 plugins/openas/skills/project-memory/scripts/learning.py \
  --root /path/to/consumer-project draft diagnose-average-input \
  --lessons LESSON_ID_1 LESSON_ID_2 --author actual-author
```

Drafts live at `.openas/memory/learning/skills/NAME/VERSION_ID/SKILL.md`. Generation does not register native client skills or generate/execute arbitrary scripts; it combines reviewed guidance as Markdown.

Trial before independent skill review. Trusted maintainers define trial commands; do not extract commands automatically from unreviewed candidate text:

```json
{
  "cases": [
    {
      "fixture": "learning-fixture",
      "task": "Diagnose the average empty-input behavior from the local contract. Explain the expected result.",
      "expected_applicable": true,
      "checks": [["python3", "-B", "validate_response.py", "yes"]]
    },
    {
      "fixture": "learning-fixture",
      "task": "Assess an unrelated CSS color change. Do not apply average-input guidance.",
      "expected_applicable": false,
      "checks": [["python3", "-B", "validate_response.py", "no"]]
    }
  ]
}
```

Copy the bundled [fixture](../workflows/examples/learning-fixture) into the consumer project's `learning-fixture/` and consult the [trial definition](../workflows/examples/learning-trial.json). These examples validate average-input diagnosis, not arbitrary skills; other behavior needs matching tests.

```bash
python3 plugins/openas/workflows/learning_cycle.py \
  --root /path/to/consumer-project --output /path/to/new-private-trial \
  trial SKILL_VERSION_ID /path/to/trial-spec.json

python3 plugins/openas/workflows/learning_cycle.py \
  --root /path/to/consumer-project --output /path/to/new-private-skill-review \
  review-skill SKILL_VERSION_ID --activate
```

Trials invoke real read-only clients in temporary fixture copies, check applicability/unchanged files, and execute trusted argv checks. Check scripts use `OPENAS_TRIAL_RESULT` for actual responses and `OPENAS_SKILL_FILE` for candidate text. `checks` execute with host permissions and require trusted definitions; temporary copies are not OS isolation.

Cover a positive and a non-triggering negative case. Results bind skill content hash, original fixture, definition, and responses. Independent review checks `supported`, `scoped`, `no_secrets`, `positive_case`, `negative_case`, and `behavior_checked`. Exit codes without meaningful behavioral assertions should be rejected. Current trials cover read-only diagnosis/process guidance, not code writing, deployment, or other side effects; those require project-specific behavior evaluation.

`--activate` writes the project activation registry only after approval; omitting it leaves approved but inactive. Trusted external evaluations may use learning.py `evaluate ID PROJECT_RELATIVE_REPORT`, `review-skill ID REVIEW_JSON`, and `activate ID --reason REASON`. Reports need exact skill_sha256, positive/negative cases, check exit codes, and sources; do not claim real-client execution without it.

## Stage 4: evaluate use, disable, and roll back

At subsequent single-task startup, keyword retrieval supplies at most three valid active skills as applicable context, recording versions. Inactive/retired/stale/modified skills or changed trial receipts are not reused. Ordinary Claude sessions may use project-memory's `context QUERY`; this does not create `.claude/skills` or change client configuration.

Task completion links supplied skill versions and outcomes. `inspect` reports successes, unclassified outcomes, feedback, and audit; non-implementation states such as reviewed do not count as failures. Context inclusion does not prove adoption, and task success does not prove benefit; causal judgment needs concrete feedback/comparison.

```bash
python3 plugins/openas/skills/project-memory/scripts/learning.py --root /path/to/consumer-project inspect
python3 plugins/openas/skills/project-memory/scripts/learning.py --root /path/to/consumer-project context 'average empty input'
python3 plugins/openas/skills/project-memory/scripts/learning.py --root /path/to/consumer-project outcome SKILL_VERSION_ID OBSERVATION_ID --useful no
python3 plugins/openas/skills/project-memory/scripts/learning.py --root /path/to/consumer-project disable SKILL_VERSION_ID --reason 'Regression observed; disable for investigation'
python3 plugins/openas/skills/project-memory/scripts/learning.py --root /path/to/consumer-project rollback OLD_SKILL_VERSION_ID --reason 'Return to verified version'
```

Repeated version/observation registration does not add samples; later useful feedback updates with audit history. Three consecutive task-failure or negative-feedback observations pause reuse conservatively, without attributing task failure directly to the skill. Reactivation needs new trial evidence and independent review.

New activation retains old versions/history. rollback requires a previously active version still satisfying evidence/trial/review conditions. It neither revives stale lessons nor rolls back product code.

## Storage, exit codes, and validation scope

records.json remains version=1. Separate `.openas/memory/learning/state.json` is also version=1, containing observations, lessons, skills, active, outcomes, audit. Subdirectories hold receipts, skills, trials, and responses. Consumers decide whether knowledge enters Git; do not distribute raw logs, locks, and checkpoints.

Writes use POSIX locks and atomic replacement. Knowledge and learning state are separate files; inspect both after abnormal exits. Inconsistent candidates/evidence/registry cannot activate. Hashes prove unchanged content, not truth or identity.

learning.py exits 0 on success and 2 on input/evidence errors. learning_cycle.py exits 1 for failed trials/rejected skill review and 2 for environment/format errors. reflect exits 0 after handling candidates even if all are rejected; inspect the report for actual decisions.

Automated tests cover state transitions, isolation, invalidation, conflicts/deduplication, real check subprocesses, model-output validation, runner integration, and rollback. Model calls use mocks, not proof of real accounts, model quality, or native discovery. Run real trials separately in the target environment.

A [real-client acceptance record](../workflows/evidence/2026-10-24-learning/README.md) exists for extraction, independent review, draft generation, positive/negative trials, and activation in one temporary project; its scope is limited to that minimal case.
