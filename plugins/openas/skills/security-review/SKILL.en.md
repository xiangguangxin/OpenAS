---
name: security-review
description: Trace actual trust boundaries and exploitable security issues in code, configuration, and data flows, with prerequisites and verification; do not automatically scan external systems.
---

[中文](SKILL.md) | English

Follow the [language policy](../../references/language.md).

# Security review

Confirm authorized target/version, entry points, assets/data, runtime and review scope. Read actual design, configuration and callers. Review-only stays read-only; generic risk lists do not expand scanning scope.

Trace untrusted input across process, network, identity, permission and storage boundaries, stating attacker control. Inspect authentication/authorization, parsing, data/credentials, logs/network and risk-relevant dependencies/build origin. Authentication is not object authorization; frontend checks do not replace server controls. Verify runtime defaults and deployment overrides before declaring a missing local setting exploitable.

Each candidate needs entry, prerequisites, missing control, impact and existing mitigations. Prefer static tracing and minimal isolated experiments within authorization; do not read/output secrets or contact unrelated systems. Mark unconfirmed inferences and missing evidence. Verify current official advisories, installed versions, reachable use and configuration for vulnerability claims; version matches alone do not prove exploitability. Disclose unavailable freshness and do not invent advisory IDs.

Follow the [team contract](../../references/team-contract.en.md) for IDs, locations, evidence, severity, advice and regressions. No findings is allowed with scope/gaps/residual risk, not absolute safety. Security reviewers assess; developers/IT repair. Rechecks must show attacks blocked and legitimate paths preserved, not merely new validation strings.
