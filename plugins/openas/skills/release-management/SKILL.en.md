---
name: release-management
description: "Prepare, verify, or publish an authorized software release, reconciling versions, changelogs, tags, artifacts, smoke checks, and recovery."
---

[中文](SKILL.md) | English

Follow the [language policy](../../references/language.md) and the [shared evidence policy](../../references/evidence-policy.en.md).

# Manage a software release

Identify the release version, target commit SHA, channel, and established release process. Locate version sources, the previous release tag, release notes, and artifacts. Reconcile version fields using project conventions. Derive notes from actual changes between releases, including user-visible changes and necessary compatibility or upgrade steps. Inspect existing tags, releases, and package versions with matching names. When one already exists, verify its target and artifacts. For a conflict, preserve evidence and identify the decision needed.

## Verify and publish

- Bind required checks, the build run, and artifacts to the target commit. Verify package contents, platform, and any project-provided digests or signatures. Run relevant clean-install or upgrade smoke checks on the same artifact intended for distribution and record actual results.
- Create tags or releases, upload artifacts, or publish to a channel within existing authorization. Read back the tag target, published version, and artifact. Verify digests and installability where applicable. For preparation requests, deliver the release checklist and pending steps.
- After partial failure, inspect which steps took effect before retrying missing steps. Follow channel-supported promotion stops, withdrawal, or follow-up fixes. For conflicting tags or public artifacts, assess impact and preserve existing records. When data or format migrations are involved, verify whether the old version can read the new state.

Report the version, commit, tag, artifact and channel locations, check evidence, actual publication status, and recovery conditions. Use [ci-cd](../ci-cd/SKILL.en.md) for pipeline configuration and [finish-development-branch](../finish-development-branch/SKILL.en.md) for branch closeout.
