---
name: coverage-analysis
description: "Diagnose code coverage reports and gaps in statement, branch, condition, or MC/DC coverage, including instrumentation, collection, and source mapping."
---

[中文](SKILL.md) | English

Follow the [language policy](../../references/language.md) and the [shared evidence policy](../../references/evidence-policy.en.md).

# Analyze code coverage

Identify the required metric, measured scope, exclusion rules, and detail supported by the tool. Bind the source commit, executed binary or module, build and instrumentation options, scenarios, raw data, and reporting tool versions. Generate reports from matching objects and data. Record how data from multiple processes, shared libraries, or scenarios was combined. For missing reports or mismatched versions, locate the break in instrumentation, profile output, merging, or source mapping before drawing conclusions at statement, branch, or decision level.

## Identify and verify gaps

- Record gaps by file, function, source location, and available decision or branch IDs. Distinguish unexecuted paths, missing instrumentation, missing data, incorrect mapping, documented exclusions, and insufficient evidence. Check measurement rules for generated code, macros, and multiple build configurations.
- Design minimal tests around observable behavior to distinguish missing paths. Specify inputs, preconditions, expected results, and target locations. For MC/DC, use the project's and tool's decision criteria. Identify pairs demonstrating that the target condition independently changes the decision outcome, accounting for short-circuiting and coupled conditions. True/false counts support the corresponding count conclusions.
- Run selected cases when authorized. Compare reports with consistent metrics, scope, and build configuration. Check behavioral assertions and relevant regressions alongside coverage counts. Record evidence for unreachable paths and exclusions, leaving uncertain items pending.

Report sources and commands, tool and metric definitions, per-item gaps with evidence, suggested or verified tests, and remaining limits. Use [test-strategy](../test-strategy/SKILL.en.md) for broader planning and [verification-before-completion](../verification-before-completion/SKILL.en.md) for delivery acceptance.
