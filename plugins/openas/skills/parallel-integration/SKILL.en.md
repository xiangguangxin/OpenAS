---
name: parallel-integration
description: Integrate already authorized independent work, inspect overlapping changes and contracts, and verify combined behavior; do not provide or automatically start parallel scheduling.
---

[中文](SKILL.md) | English

Follow the [language policy](../../references/language.md).

For factual answers, tests, reviews or completion claims, first read and follow the [shared evidence policy](../../references/evidence-policy.en.md).

# Integrate independent results

Inspect each workspace/branch's original goal, baseline, actual diff, scope, upstream contracts and verification. Completion labels do not establish merge safety; preserve uncommitted or unclear-origin work.

Check overlapping files, interfaces, configuration, generated artifacts and shared runtime resources. Integrate dependent changes sequentially; a clean textual merge still needs semantic review. Do not blindly choose an entire side to resolve conflicts.

Apply results within authorization in an isolated integration workspace, checking affected components before cross-component behavior. Passing tests on original branches do not replace integrated checks. Record conflicts, sources and responsible tasks on failure; preserve both results rather than force-pushing or clearing workspaces.

OpenAS task graphs currently schedule sequentially. This skill consumes results supplied by an authorized host, not a scheduler. Use [worktrees](../git-worktrees/SKILL.en.md) for isolation; merges and releases follow task authorization.
