---
name: task-orchestration
description: Represent multi-step work as dependency nodes with artifacts, ownership, routes, and acceptance, and execute with failure handoff; do not imply parallel or release authorization.
---

[中文](SKILL.md) | English

Follow the [language policy](../../references/language.md).

For factual answers, tests, reviews or completion claims, first read and follow the [shared evidence policy](../../references/evidence-policy.en.md).

# Task orchestration

Split original acceptance into independently checkable nodes with ID, dependencies, workspace, file ownership, inputs, outputs, route and completion criteria. Retain user scope and investigate unknown facts rather than inventing requirements.

Validate cycles, missing nodes, workspaces and shared files/state. Sequence dependent writes; parallelism requires independent resources, real host support and authorization. Before each node inspect upstream artifacts/evidence, not just labels.

`graph-runner.py` provides sequential scheduling and dependency failure blocking, not concurrency. Validate with `--plan`, then execute trusted definitions with `--run`; see [workflow guide](../../workflows/README.md). Failed prerequisites block downstream while independent nodes may continue. Review `needs_fix` is not a passing dependency.

Each node's route owns revision loops. Do not create an unbounded repair chain outside the graph. Preserve full feedback, responsible node, attempts and stop reasons. Inspect failed nodes individually; do not automatically rerun the whole graph or overwrite records.
