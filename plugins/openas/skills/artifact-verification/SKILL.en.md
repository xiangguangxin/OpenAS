---
name: artifact-verification
description: "Independently verify freshness, structured results, and per-criterion evidence for generated, exported, or downloaded artifacts."
---

[中文](SKILL.md) | English

Follow the [language policy](../../references/language.md) and [shared evidence policy](../../references/evidence-policy.en.md).

# Artifact verification

1. Extract criteria, output paths, formats, and expected values before execution. Prefer a per-run output directory or capture pre-run content fingerprints at existing paths. If the application emits a run ID, match the report ID to the current run.
2. Choose an independent check per criterion. Parse the format and check build IDs, test results, metrics, and numeric values as applicable. Reject stale, unreadable, misattributed, or incorrect artifacts. Existence or readability alone can satisfy a criterion that only requests that property.
3. Configure the [runtime artifact verifier](../../integrations/computer-use/RUNTIME.en.md#artifact-verification). Enable `fresh` before the first `run`, reuse the same configuration on `resume`, and run `openas-gui verify` to recheck independently. Its checks can reject the model's completion claim.
4. Report criterion-level outcomes, rules used, versions, and open evidence gaps. Use [acceptance-tracking](../acceptance-tracking/SKILL.en.md) and [verification-before-completion](../verification-before-completion/SKILL.en.md) when accepting a whole development task.

For an MC/DC report, obtain the artifact in the run's working directory and check the instrumented build, passed cases, and metric. Check applicable counts and thresholds to establish whether coverage targets were met.
