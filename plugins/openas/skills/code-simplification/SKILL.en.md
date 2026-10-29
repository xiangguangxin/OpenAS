---
name: code-simplification
description: Find or implement evidence-backed simplifications of code, APIs, configuration, and state; preserve compatibility and keep surveys read-only.
---

[中文](SKILL.md) | English

Follow explicit language preferences, otherwise the task language. Preserve existing artifact language unless translation is requested; keep machine-readable identifiers unchanged. See the [language policy](../../references/language.md).

For factual answers, tests, reviews or completion claims, first read and follow the [shared evidence policy](../../references/evidence-policy.en.md).

# Code and system simplification

Reduce long-term maintenance obligations: synchronized state, public interfaces, branches, configuration surfaces, dependencies, or lifecycle machinery, rather than chasing deleted lines. Read [project adaptation](../../references/project-context.en.md), the implementation, effective decisions, and requested scope. Distinguish surveys, proposal assessment, and authorized implementation. A survey does not authorize deletion; clear implementation requests do not require renewed approval for every reversible local choice.

## Find obligations that can actually disappear

Look for duplicate state, unread fields, unreachable branches, shadowed configuration forwarding, speculative extension points, and duplicated infrastructure. Ask whether a distinction or mechanism is necessary before deciding where it belongs. Moving complexity into a shared layer or adding synchronization checks does not remove its maintenance cost. Prefer a few supported candidates over a repository-wide deletion inventory.

Use `rg` for symbols, reads/writes, constructors, event names, configuration keys, and exports, then read the matches. Trace producer → transformation/override → registration/loading → consumer → observable effect. Cover manifest-driven loading, reflection, generated code, CLI/configuration precedence, shipped entry points, and declared external extension contracts. Tests or declarations do not establish production use; zero internal call sites do not establish that a public capability is useless.

Before replacing caches or copies with authoritative reads, establish the required observation time: current values, historical snapshots, and durable audit records can serve different purposes. An event is not redundant merely because the UI does not render it; current values cannot replace evidence that must remain frozen.

## Form assessable candidates

For each worthwhile candidate, provide source locations, current owner, actual call/data path, what disappears, remaining machinery, maintenance benefit, compatibility effects, and the strongest retention argument. Distinguish unreachable behavior removal, narrowed supported behavior, and insufficient evidence. Report no reliable candidates when appropriate instead of meeting a quota.

Count a replacement dependency's adapters, platform requirements, upgrades, and validation costs. Covering a generic protocol while rebuilding the same state machine is not a net simplification. An interface with one built-in implementation may still own a real external extension contract; implementation count alone does not justify deletion.

For asynchronous or durable changes, identify resource ownership, cancellation, first terminal outcome, completed cleanup, partial writes, and recovery semantics. Prove states express the same fact before merging them; trace trust boundaries and the next owner before removing validation. Use [architecture-evolution](../architecture-evolution/SKILL.en.md) for staged compatibility/migration decisions and [change-impact-analysis](../change-impact-analysis/SKILL.en.md) when impacts need deeper analysis. Read [evidence and tradeoff examples](references/evidence.md) for complex candidates.

## Implement and validate

Implement selected candidates within existing authorization and update affected consumers, configuration, documentation, and necessary tests. If a change requires giving up a capability the user requires, finish independently deliverable work and surface that decision rather than silently dropping the contract. Use [bug-fix](../bug-fix/SKILL.en.md) for ordinary defects and [requesting-code-review](../requesting-code-review/SKILL.en.md) for ordinary reviews without forcing a simplification audit.

Select the smallest checks for retained behavior: normal/error paths, configuration precedence, dynamic loading, or cancellation/restart/compatibility relevant to this change. Compare behavior and actual artifacts for behavior-preserving refactors; disclose intentional before/after differences separately. Tests should establish retained contracts or intended regressions; assertions mirroring implementation, new retries, or deleted failing tests do not prove simplification.

Deliver survey scope, adopted and meaningful rejected/deferred candidates, net benefit and capability costs, actual edits, and check results. A static search with no calls establishes search scope, not complete runtime proof; unexecuted checks remain unverified. Adapted from DSH; see the pinned [provenance and license record](../../references/dsh-skills-provenance.md).
