---
name: checkpoint-and-resume
description: Validate task, workspace, rules, and evidence after interruption before reusing checkpoints; do not automatically resume unauthorized historical work.
---

[中文](SKILL.md) | English

Follow the [language policy](../../references/language.md).

For factual answers, tests, reviews or completion claims, first read and follow the [shared evidence policy](../../references/evidence-policy.en.md).

# Checkpoints and resumption

Confirm the task the user currently wants to continue. Read the original task, `state.json` and `handoff.json`; compare workspace, scope, acceptance and current files. Memory is not authorization to resume.

The Codex adapter supports `--resume` for versioned orchestration runs. It checks task/rule fingerprints, source content and permissions, and reuses valid completed phases. Host acceptance and verifier run again. A process lock prevents concurrent resumption of one run directory.

Source or rule changes reject reuse by default. Inspect whether they remain within original scope. With authorization to revalidate current changes, `--resume --restart-stages` invalidates reusable phases and restarts from design or the route entry, preserving the original baseline and logs. It does not expand scope or accept out-of-scope edits.

Inspect partial writes from interrupted phases before acting; do not automatically undo them. Old formats, changed task definitions, completed runs or corrupt records require a new run or manual handling. See the [workflow guide](../../workflows/README.md).
