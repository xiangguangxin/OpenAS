---
name: dependency-upgrade
description: Assess or implement scoped dependency and toolchain upgrades, including breaking changes, transitive resolution, lockfiles, call-site adaptation, regression checks, and recovery.
---

[中文](SKILL.md) | English

Follow the [language policy](../../references/language.md).

# Dependency upgrades

Confirm dependency, current/target versions, motivation, allowed scope and supported environments. Read manifests, lockfiles, resolved and installed versions, callers and build configuration; these versions may differ. Retain existing version-management tools, and remain read-only for assessment requests.

Compare official release notes, migration guides and support matrices, including intervening versions. Check APIs, behavior, defaults, configuration, runtime/build requirements and freshness through [technical research](../technical-research/SKILL.en.md); semantic versioning does not guarantee compatibility. For security upgrades verify official advisories, affected versions and reachable use, using [security review](../security-review/SKILL.en.md) when needed.

Inspect relevant direct/transitive dependencies, plugins, peer constraints, ABI, generation and runtime coupling. Respect licensing and deployment constraints. Identify necessary coordinated upgrades versus independent changes, retaining the smallest viable upgrade baseline; do not expand to a technology-stack replacement.

Record pre-change versions and a credible check baseline. Use the existing package manager/version to update manifests and locks; do not fabricate resolution by hand-editing lockfiles. Installation/download/generation needs existing authorization and lifecycle-script awareness. Investigate constraint conflicts instead of defaulting to forced installation, ignored peer errors or disabled integrity checks. Explain unexpected broad relocking through tool, registry or resolver differences.

Adapt affected calls, configuration and generated outputs without unrelated refactoring. Verify changed behavior through builds, import/startup, APIs, defaults, errors and integration on affected supported environments. Preserve failing compatibility cases where reproducible; do not create meaningless tests for pure version edits. Resolution, build and behavioral compatibility are separate evidence.

Recovery must restore coordinated manifests, locks, calls and configuration. Persistent-format or irreversible changes require [architecture evolution](../architecture-evolution/SKILL.en.md); reinstalling an old package does not prove it can read new data. Report version changes, adaptations, commands/results, recovery and gaps. Developers handle callers, IT environment, [CI/CD](../ci-cd/SKILL.en.md) matrices, and verifier independent acceptance.
