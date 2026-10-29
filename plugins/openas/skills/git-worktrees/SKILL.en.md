---
name: git-worktrees
description: Create, inspect, and clean isolated Git worktrees for independent features or experiments; do not require one for every simple edit.
---

[中文](SKILL.md) | English

Follow the [language policy](../../references/language.md).

For factual answers, tests, reviews or completion claims, first read and follow the [shared evidence policy](../../references/evidence-policy.en.md).

# Git worktrees

Start with `git status --short` and `git worktree list`. Confirm existing edits, worktrees and task branches. Follow repository placement conventions; otherwise choose an explicit directory outside the repository to avoid recursive scans/builds.

After checking availability, an example is `git worktree add -b feature/import ../project-import HEAD`, then `git -C ../project-import status --short`. For an existing branch use `git worktree add ../project-import existing-branch`. Reuse or choose another branch if already checked out; do not force through protection.

Worktrees share Git objects/refs, not uncommitted edits, dependencies or project memory. Prepare environment per target project. Databases, ports, services and caches may still be shared and need isolation. Handoff includes workspace, branch, edit ownership and acceptance commands.

Before cleanup inspect diff, untracked files and saved commits. Remove only authorized clean worktrees no longer needed using `git worktree remove ../project-import`, then list again. On refusal inspect unsaved work rather than force-delete. For moved/deleted directories inspect `git worktree list --porcelain` and repair paths or confirm stale records before pruning. Do not automatically delete task branches.
