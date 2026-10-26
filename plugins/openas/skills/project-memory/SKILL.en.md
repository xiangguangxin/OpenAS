---
name: project-memory
description: Extract, review, and reuse evidence-backed project knowledge and manage candidate skill trials, activation, feedback, and rollback; do not retain whole conversations or expand permissions.
---

[中文](SKILL.md) | English

Follow the [language policy](../../references/language.md).

# Evidence-backed project memory

Read the [memory guide](../../memory/README.md). Keep memory project-scoped; reflection does not change model parameters or become executable truth.

At task start query a few relevant `accepted` entries and confirm source validity. Current user requests/source take precedence. `current-task.json` is a checkpoint, not resumption authorization. Use [learning.py](scripts/learning.py) with `--root PROJECT context QUERY` for active project guidance only when its applicability holds; it does not install into host skill directories.

Extract minimal specific `fact`, `decision` or `lesson` entries with scope. Do not infer unapproved product decisions from code. Provide key, scope, tags and real evidence: project JSON, SHA-256, JSON pointer and value. For Markdown/code, create a receipt and explicitly bind sources, e.g. `Memory.evidence('receipt.json', '/result', sources=['src/example.py'])`. Queries validate receipts and declared sources. Old records without sources check direct JSON only, not arbitrary fields recursively; repropose important conclusions with sources rather than inventing evidence.

`propose` stays candidate and is not reused across tasks. Semantic review checks support, scope, staleness, duplicates and sensitive content; independent agents or explicit human review may be used when authorized. `review approve` accepts, `reject` preserves reasons. Same key/scope conflicts do not overwrite; verify sources, retire old knowledge and review again. Store only necessary knowledge, not credentials, full chats, raw client logs or execution targets. Knowledge may enter Git; checkpoints/locks should not.

Use [project_memory.py](scripts/project_memory.py) with explicit `--root /path/to/consumer-project`; write `.openas/memory/` in that project, not the plugin. Consult its help and memory guide. Harness phases update short-lived checkpoints, retrieve valid reviewed context and derive only limited verified run facts from host fields. Model self-report/failure prose is not automatically verified knowledge.

Memory-enabled single-task runs capture observations; `--learn` adds independent read-only extraction/review and candidate generation. Follow [learning lifecycle](../../memory/learning.md). Generated skills remain candidates until positive/negative trials and independent review; trusted tasks supply evaluation commands. Record versions/feedback and disable/roll back as needed. Changed sources require renewed extraction/review, not silently updated fingerprints.

These are task-triggered workflows, not background watchers. Rule or permission changes are separate work. `inspect` exposes `evidence_valid`; queries exclude missing/changed evidence, while `retire` retains reasons/history. Fingerprints prove unchanged content, not a conclusion's truth.
