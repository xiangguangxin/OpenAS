---
name: browser-goal-executor
description: "Execute authorized multi-step web goals with semantic browser actions, observable waits, downloads, and acceptance."
---

[中文](SKILL.md) | English

Follow the [language policy](../../references/language.md) and [shared evidence policy](../../references/evidence-policy.en.md).

# Browser goal execution

1. Identify the target URL, test session, allowed actions, and success criteria. If the host exposes Playwright, use its actual tools following the [integration guide](../../integrations/playwright/README.en.md). To run or resume independently, follow the [browser runtime guide](../../integrations/computer-use/RUNTIME.en.md#browser-goals) to select Chromium and a download directory.
2. Read a fresh page snapshot and locate a unique visible role/name or field label. Observe again after actions. Wait for visible conditions on asynchronous work. Use authorized test values, and recheck the page if navigation is outside scope or the target is ambiguous.
3. Define the destination and acceptance rules before downloading. Save to a new filename and apply [artifact-verification](../artifact-verification/SKILL.en.md) to the downloaded artifact. Confirm the specified page state and artifact checks before completing.
4. Resume with the original start URL, download directory, and checkpoint. Reobserve from the new browser session. Reconcile uncertain in-flight actions before proceeding. Use [gui-goal-executor](../gui-goal-executor/SKILL.en.md) for native desktop windows.
