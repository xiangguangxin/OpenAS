---
name: pr-review-feedback
description: "Triage existing PR review feedback against the current head, fix actionable findings, verify changes, and report a disposition for each thread."
---

[中文](SKILL.md) | English

Follow the [language policy](../../references/language.md) for response preferences and source text. Apply the [shared evidence policy](../../references/evidence-policy.en.md) to review and verification.

# Address PR review feedback

Identify the repository, PR, base, current head SHA, local branch, and requested scope. Use existing GitHub tools, `gh`, or supplied review material. Paginate unresolved threads and their replies as needed, and read review summaries containing actionable feedback. Keep thread links or IDs, original commits, and locations. Locate the same behavior in the current diff and code. Check whether a finding still applies when its comment is marked outdated.

## Triage and verify each finding

- Mark feedback as actionable, already addressed, duplicate, unsupported by evidence, or awaiting a decision. Cite current code, requirements, or tests. Link duplicates to the primary thread. Fix findings that still apply and fall within the authorized scope, linking threads that share a fix. For assessment-only requests, report dispositions.
- Preserve existing changes. Check the same triggering scenario before and after a fix, then run relevant regressions. Record gaps for scenarios that cannot be verified. Bind passing checks to the commit or local diff actually delivered.
- Recheck the head SHA and thread state before posting replies or resolving threads. If either changed, revisit affected conclusions and checks. Apply existing authorization separately to pushing, replying, resolving, and merging. Keep feedback awaiting a decision open.

Report each item's link, disposition, corresponding change or rationale, verification, and remaining decisions. Use [requesting-code-review](../requesting-code-review/SKILL.en.md) for ordinary code review and [finish-development-branch](../finish-development-branch/SKILL.en.md) for branch closeout.
