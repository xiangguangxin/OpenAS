---
name: accessibility-review
description: Review keyboard use, focus, semantics, labels, contrast, and dynamic feedback; report reproducible barriers without claiming full compliance from scans.
---

[中文](SKILL.md) | English

Follow the [language policy](../../references/language.md).

# Accessibility review

Identify whether the target is a design or running interface, its platform, key user tasks, and any required standard version or level. Focus on operational barriers unless formal compliance is requested. Verify official standard clauses before citing them; disclose unavailable evidence.

Walk through key tasks. Check keyboard reachability and operation, order, visible focus, modal focus entry and restoration, and keyboard traps. Inspect actual accessible names, roles, states, form labels, error associations, and feedback. As relevant, check text and non-text contrast, zoom/reflow, non-color cues, alternative text, and dynamic announcements. Assess animation, dragging, touch, or timed alternatives only where present.

Record platform, tools, page version, measurement conditions, and reproduction steps. Screenshots cannot establish DOM semantics, keyboard behavior, or screen-reader results. Automated checks cover only part of accessibility; manually test key operations. Source-only or design-only review must identify runtime gaps, without inventing assistive-technology observations.

For each issue provide location, steps, actual/expected behavior, affected task or users, evidence, severity, and suggested correction using the [team contract](../../references/team-contract.en.md). Recheck the original operation and related states after changes. Report static and executed coverage separately. UX revises specifications, developers fix implementation, and test engineers add suitable regressions. Use the [Playwright guide](../../integrations/playwright/README.md) only when corresponding host tools are available.
