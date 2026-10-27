---
name: bug-fix
description: Investigate exceptions, crashes, wrong results, or hangs using evidence across requirements, design, implementation, and environment; verify the causal fix.
---

[中文](SKILL.md) | English

Follow the [language policy](../../references/language.md).

# Evidence-backed debugging

Explain which condition violated which contract and how that caused the symptom. Scale investigation to the problem and report hypotheses when evidence is insufficient. Use [project adaptation](../../references/project-context.en.md) to identify runtime and reproduction entry points; GDB is not mandatory for every project.

Record starting diff, expected/actual behavior, exact command and exit code, version/binary, input, configuration, seeds and frequency. Preserve user changes. Minimize the reproduction where possible; intermittent failures need failing samples and successful controls, not guaranteed reproduction. Distinguish pre-load, configuration/build, crash, wrong-result and progress-stall failures. Check expectations, data divergence or wait relationships rather than always starting from a crash stack.

Use [root-cause quadrants](references/root-cause.md): requirements, design, implementation, configuration/environment. Requirements, documentation and tests may also be wrong. Mark each hypothesis pending, supported or excluded; retain unknown when appropriate and distinguish primary causes, contributors and detection gaps.

Trace existing logs and pre-error context using actual correlation identifiers, timestamps and state changes. Follow erroneous data back to production, mutation and handoff; locate the last correct and first incorrect values and check boundary contracts. Use [logs and GDB](references/logs-gdb.md) for relevant native runtime evidence. Each experiment should separate candidate causes with hypothesis, expected observation, actual result and conclusion. Prefer changing one condition; instrumentation can alter races.

Fix the demonstrated causal chain. Design defects require contract/design updates plus code and tests. Check related callers, ownership, boundaries and ordering. Do not hide defects by deleting assertions, swallowing errors, loosening expectations or arbitrary sleeps. Where possible demonstrate failure before and success after on the same input, with meaningful regressions. Start with related checks and expand by impact. For intermittent issues report sample counts, seeds and residual uncertainty; non-recurrence is not proof of cure. Missing tools do not authorize installation.

Deliver symptom/impact, classification/confidence, causal evidence with locations, fix, commands/exit codes and residual risks. If unresolved, state excluded causes and the next discriminating experiment. Reusable lessons go through [project memory](../project-memory/SKILL.en.md): candidate then semantic review, with minimal redacted evidence. Do not retain raw core dumps, full logs or secrets, or automatically commit, push or spawn agents.
