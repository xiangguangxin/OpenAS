---
name: subagent-driven-development
description: Coordinate authorized role handoffs, adversarial review, and independent verification for complex changes; do not require teams for simple questions or mechanical edits.
---

[中文](SKILL.md) | English

Follow the [language policy](../../references/language.md).

For factual answers, tests, reviews or completion claims, first read and follow the [shared evidence policy](../../references/evidence-policy.en.md).

# Team collaboration

Read the [team contract](../../references/team-contract.en.md) and actual [roles](../../agents). Claude roles use `openas:cto`, `openas:red-team`, etc.; other hosts dispatch differently. Confirm actual support and authorization before spawning. Otherwise perform necessary responsibilities sequentially and state that review was not independent; never fabricate agent execution.

Choose only needed roles: product management for market/scope; CTO and red-team for unclear or cross-component design; developers, reviewers and verifier for implementation; IT for environment/CI/operations; security for permission/data/network risk; technical writing plus relevant checks for docs. Prioritize concurrency, lifetimes, protocols and public contracts rather than diff size.

Every handoff preserves original requirements, authorization, acceptance, paths, initial state and full prior findings. Assign file ownership for independent tasks; shared files/dependencies execute sequentially. Follow actual host API rather than assuming a universal agent interface.

Typical dependency flow is design → design review → necessary docs → implementation → implementation review → verification. Return failures to responsible roles with counterexamples/commands. Empty, timed-out or invalid structured results cannot pass. Track findings by ID; implementers cannot accept their own blocking risks.

Default automatic revision is bounded to three rounds; unresolved issues return with evidence/decisions rather than proceeding. Re-review and verify affected changes. Publication/Git actions require existing authorization. The executor integrates files, behavior, evidence, limits and remaining items. `workflows/agent-team.js` is an optional host template, not an Agent SDK; simulated branch checks do not prove reports true.
