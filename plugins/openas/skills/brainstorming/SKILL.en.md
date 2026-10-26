---
name: brainstorming
description: Clarify goals, constraints, existing architecture, and verification before coding when requirements are new or unclear.
---

[中文](SKILL.md) | English

Follow the [language policy](../../references/language.md).

# Requirements exploration

Understand the real problem before coding: requirements → necessary clarification → constraints → alternatives → sufficient design.

Establish the goal, constraints, existing architecture and how results will be verified. Read available implementation and commands using [project adaptation](../../references/project-context.en.md), and investigate facts yourself before asking users.

When requirements and authorization are already clear, produce an implementable design directly; do not request repeated approval for routine details. For example, a batch import may need input format, partial-failure behavior, reuse of existing APIs and normal/error acceptance samples. Derive questions from the actual project rather than assuming a language, framework or hardware.
