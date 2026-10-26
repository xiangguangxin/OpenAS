---
name: finish-development-branch
description: Check final diff, acceptance, and reviews, then commit, push, or merge within existing authorization while preserving unfinished work.
---

[中文](SKILL.md) | English

Follow the [language policy](../../references/language.md).

# Finish a development branch

Check branch, ownership of starting edits, target baseline and workspace. Read actual changes, preserving user work and excluding accidental generated files, temporary logs and authentication data.

Run checks relevant to the final change and close outstanding review issues. Identify unavailable external validation; CI success is not proof of all client/product acceptance.

Organize commits around the actual problem and behavior. Stage only task-related files. Do not reset, clean or force-push changes you do not understand.

Commit, push, PR creation, merge and release each follow existing authorization. Do not request permission again when granted, or expand authorization merely because work is finishing. Before authorized merge inspect the latest PR commit and required checks; afterwards confirm target branch and automated results.

Deliver changed files/behavior, validation, commit or PR locations and limits. Before removing temporary worktrees inspect unsaved content and retain anything still needing review.
