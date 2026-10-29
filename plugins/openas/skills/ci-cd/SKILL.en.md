---
name: ci-cd
description: Configure or diagnose CI/CD triggers, build matrices, caches, artifacts, permissions, and failure evidence; do not automatically deploy or change remote repository settings.
---

[中文](SKILL.md) | English

Follow the [language policy](../../references/language.md).

For factual answers, tests, reviews or completion claims, first read and follow the [shared evidence policy](../../references/evidence-policy.en.md).

# Continuous integration and delivery

Read [project adaptation](../../references/project-context.en.md), existing pipelines, local build/test commands, runner constraints and acceptance. Distinguish configuration, diagnosis and authorized delivery execution. Retain the current platform and tools; local changes do not authorize remote publishing, installation or branch-protection changes.

Map checkout, environment, dependency resolution, build, tests and artifacts to jobs with explicit failures. Reuse local entry points and verify directory, versions, environment and exit-code propagation. Define events, filters, branches and cancellation. Cancelling obsolete side-effect-free checks may be appropriate; deployments or data changes must not be interrupted into unknown states.

Limit matrices to supported combinations, distinguishing required from experimental jobs. Align skipped/filtered/allowed-failure behavior with required checks. Aggregation must handle failure, cancellation and skipped jobs without claiming unexecuted acceptance passed.

Cache keys reflect compatible toolchain, platform and lockfile inputs; a miss must permit a full rebuild. Cache hits do not replace integrity checks or tests. Distinguish disposable cache from traceable delivery artifacts. Record commit, environment, checksums and retention; validate and deliver the same artifact rather than rebuilding under an old approval.

Check untrusted PRs, third-party steps, self-hosted runners and credential boundaries. Minimize job permissions; do not execute untrusted code with secrets or promote untrusted artifacts without verifying origin/version. Keep secrets out of logs and artifacts. Confirm platform syntax, permission defaults and action versions from version-appropriate official sources via [technical research](../technical-research/SKILL.en.md).

Diagnose the exact commit/event/job/step, distinguishing parsing, runner, network, dependency, build and test failures. Compare local/CI versions, paths, permissions and environment. Retry only evidenced transient failures with bounded attempts and original error preserved. Run relevant configuration/local checks and, when authorized and available, inspect actual remote results. Local success cannot prove remote triggers, credentials or deployment.

Delivery needs a named environment, entry conditions, same-environment concurrency control, success checks and failure recovery. Without online authorization provide configuration or a plan. IT handles pipelines/environment; developers handle product build/test defects. Report changes, triggers, job relationships, artifact origin, evidence and gaps. Use [branch completion](../finish-development-branch/SKILL.en.md) for Git actions and [incident response](../incident-response/SKILL.en.md) for active outages; distinguish configured, CI-passed and released.
