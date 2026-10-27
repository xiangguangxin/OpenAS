---
name: writing-plans
description: Turn sufficiently clear design into executable, dependency-aware tasks with scope, project constraints, and acceptance; separate blockers from implementable work.
---

[中文](SKILL.md) | English

Follow the [language policy](../../references/language.md).

# Implementation planning

Start from user goals, existing code and confirmed decisions without requesting routine authorized choices again. Use [project adaptation](../../references/project-context.en.md) for actual paths and checks.

Apply [implementation readiness](../../references/implementation-readiness.en.md) to separate ready scope from blocking unknowns. Plan research/PoC for uncertain feasibility instead of hiding architectural guesses in implementation. Split by verifiable behavior or cohesive change, not fixed lines, duration or helper functions.

Each task specifies target behavior, actual files/modules, upstream results, implementation constraints and proving checks. Add ordering, parallel ownership, compatibility and failures when warranted; do not impose a large template on small tasks. For example duplicate-record import requires identification/expected behavior, changes to actual import entry/tests and normal/duplicate/invalid cases using existing commands.

Separate product decisions needing users from local implementation choices. Specify the impact of missing dependencies or unavailable checks; do not use vague 'implement and test' tasks. Preserve original acceptance and unresolved issues in handoff.
