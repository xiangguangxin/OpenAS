---
name: requesting-code-review
description: Review actual code, diffs, or repository state for evidenced defects in requirements, boundaries, compatibility, and validation; investigate directly rather than interviewing.
---

[中文](SKILL.md) | English

Follow the [language policy](../../references/language.md).

# Code and project review

Confirm object and acceptance, then read actual diff, callers, tests and constraints. Do not rely only on developer summaries or turn ordinary review into a design interview. Investigate repository facts independently.

Review relevant input/output, failures, state/resource lifetime, compatibility and coverage according to risk. Use temporary directories for minimal discriminating experiments, without editing product implementation or user configuration merely to reproduce. Mark static inferences as unexecuted.

Findings need severity, file location, trigger, actual/expected behavior, evidence, impact and repair advice. P0/P1 concern critical correctness or acceptance blockers; assess P2 by impact and treat P3 as optional. Do not promote style preferences or manufacture findings.

Separate confirmed defects, disclosed limitations and future enhancements. No substantial defects may approve, with scope and gaps. Retain IDs during rechecks, checking repairs and new consequences. Modify implementation only when repair is authorized. Use the [GitHub guide](../../integrations/github/README.md) for remote PR/CI objects when available; otherwise use local evidence and state remote gaps.
