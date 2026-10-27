---
name: executing-plans
description: Implement and verify an existing sufficiently clear plan step by step, respecting dependencies, scope, feedback, and evidence.
---

[中文](SKILL.md) | English

Follow the [language policy](../../references/language.md).

# Execute plans

Check original acceptance, branch and starting diff; preserve existing edits and confirmed design. Proceed on unblocked authorized work without repeated approval for routine choices.

Choose the next dependency-ready task, inspect actual files/callers, implement and run the project's relevant checks. Follow existing artifact/cache conventions and keep generated output out of source changes. Documentation needs source, link and format checks, not invented build steps.

On failure preserve command, directory, exit code and output. Distinguish product defects, missing environment and incorrect acceptance. Return to the responsible task rather than deleting tests, weakening assertions or bypassing gates.

When facts differ from the plan, adjust steps within authorization. Prepare reviewable alternatives for new product tradeoffs, irreversible or out-of-scope changes and obtain only the missing decision. Changes sharing files or dependencies execute sequentially.

Record behavior, evidence and remaining items after each step. Do not repeat unrelated full regressions without new changes or risks. Deliver when original acceptance is evidenced or remaining unmet conditions are explicit.
