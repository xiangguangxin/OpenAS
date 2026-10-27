# Project memory: separate plugin resources from project state

[中文](README.md) | English

## Paths

This directory contains guidance only; no records.json is distributed. Each consumer project independently stores:

| Project path | Purpose |
| --- | --- |
| `.openas/memory/records.json` | Facts, decisions, lessons, and audit history |
| `.openas/memory/evidence/*.json` | Minimal run or semantic-review receipts |
| `.openas/memory/current-task.json` | Latest task state, scope, and requirement hash; no automatic resumption |
| `.openas/memory/.lock` | POSIX write lock; do not commit |

Plugin updates/uninstallation do not change these files. Projects decide whether knowledge belongs in Git; ignore locks/checkpoints and do not delete existing knowledge by default. The plugin, possibly a read-only cache, is not the consumer project.

Memory scripts require `--root` rather than inferring projects from installation paths:

```bash
python3 /path/to/OpenAS/plugins/openas/skills/project-memory/scripts/project_memory.py \
  --root /path/to/consumer-project query 'harness verifier evidence'
python3 /path/to/OpenAS/plugins/openas/skills/project-memory/scripts/project_memory.py \
  --root /path/to/consumer-project inspect
```

## Evidence-backed lifecycle

- fact: observed project fact; decision: evidenced actual design choice; lesson: experience with applicability limits.
- Entries contain key, scope, kind, statement, tags, evidence. `propose` creates candidate; semantic `review approve` makes it accepted.
- Identical content/evidence reuses an ID. An existing accepted key/scope makes the new item conflict, without overwriting. Verify, retire the old item, then review the new one; reject/retire retain reasons.
- query returns only accepted, valid-evidence entries, at most 5 and about 5000 characters. Keyword search is not complete recall or a vector database.
- Evidence contains project-relative path, SHA-256, JSON pointer, and value. Paths cannot escape the project. Changed/missing files exclude old records without silently refreshing fingerprints.

Example evidence (derive hash/value from an actual file):

```json
{
  "path": "debug-proof.json",
  "sha256": "SHA-256 of the actual file",
  "pointer": "/result",
  "value": "actual JSON value"
}
```

For non-JSON originals, verify and save a receipt, then explicitly bind sources:

```python
evidence = memory.evidence('debug-proof.json', '/result', sources=['src/example.py', 'README.md'])
```

This adds `sources` containing real relative paths/hashes. Proposal, review, and query check receipt plus sources; changes, missing files, or escapes reject/exclude the record. Old evidence without `sources` checks only direct JSON, not arbitrary source-like fields in its body. Rebuild, repropose, and review old knowledge needing this binding. Fingerprints prove unchanged content, not truth or reviewer identity.

## Proposal, review, and harvesting

`propose proposal.json` accepts these fields; `Memory.evidence(path,pointer)` builds evidence. Prefix these examples with the script path and `--root` (replace descriptive placeholders):

```text
review RECORD_ID --verdict approve --reviewer ACTUAL_REVIEWER --reason WHY_THE_LIMITED_CONCLUSION_HOLDS
review RECORD_ID --verdict reject --reviewer ACTUAL_REVIEWER --reason REJECTION_REASON
retire RECORD_ID --reason RETIREMENT_REASON
harvest /path/to/trusted-run/state.json
```

review records caller-declared identity without authenticating it; no real semantic review means no approve. harvest requires done=true, status=verified, and all final_checks exit 0, accepting only the limited fact that this record reports a pass. Inputs must be trusted records, not treated as tamper-proof execution evidence; repeated harvesting is idempotent.

## Harness integration and limits

Use `--project-root /path/to/consumer-project` in the Codex adapter; `--no-memory` disables memory. CLI defaults project-root to current working directory, so specify it. Direct Python Runner defaults to memory disabled. Memory targets cannot be inside the plugin.

At task start retrieve relevant records as context, not instructions; state writes update short-lived checkpoints; verified runs harvest limited machine facts. Write failures become memory_warning without changing acceptance. If memory is inside task workspace, current scope protection skips memory I/O; use an independent worktree and external project-root.

Use the project-memory skill per task, or `--learn` in the single-task runner for extraction, independent review, and project-local candidates. Trials and skill review precede activation; outcomes, disabling, and rollback form the feedback loop. See [project learning](learning.en.md).

There is no background watcher or modification to roles, model parameters, or permissions. Writes use POSIX locks and atomic replacement. The short-lived checkpoint retains only the last writer, not a multi-task dashboard. Raw logs, cores, authentication, and full conversations do not go directly into long-term memory.
