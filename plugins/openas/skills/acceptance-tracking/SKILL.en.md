---
name: acceptance-tracking
description: Map each original acceptance criterion to implementation and real check evidence; distinguish verified, reviewed, and pending items.
---

[中文](SKILL.md) | English

Follow the [language policy](../../references/language.md).

# Acceptance tracking

Preserve each original criterion and its meaning. Associate it with implementation locations, relevant inputs, check methods, the checked version, and results. Distinguish automated checks, model review, human observation, and unverified claims. A zero exit code does not prove every requirement.

In task JSON, `acceptance_checks` maps each `acceptance` item to a list of zero-based `checks` indices. The lists must have equal lengths; multiple checks are allowed, and an empty list means no machine-check mapping. Do not fill gaps with unrelated tests.

The Codex adapter writes `acceptance.json`. Mapped items require both successful related host checks and verifier approval. Unmapped items are at most `reviewed`, with a human-check reminder. The review route reports items as `reported`, without asserting the reviewed implementation is correct.

For failures, retain input, command, directory, exit code, and relevant output, then return the issue to its responsible stage. Reconfirm evidence after source or acceptance changes. Use [verification-before-completion](../verification-before-completion/SKILL.en.md) and disclose coverage gaps.
