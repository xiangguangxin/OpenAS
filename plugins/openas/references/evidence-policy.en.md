# Shared policy for claims and evidence

[中文](evidence-policy.md) | English

Applies to OpenAS factual answers, analysis, reviews, tests, handoffs and completion claims. User, system and host authorization take precedence; this policy grants no tools, execution or external actions. Ordinary conceptual explanations do not mechanically require experiments, and proposals/recommendations may be given directly while distinguished from observations. Confidence and scope must not exceed evidence.

## 1. Bind claims to evidence

Before material factual, passing, fixed, compatible, performance or completion claims, obtain evidence appropriate to that claim. Cite actual files/symbols for source facts, version-appropriate primary material for external capabilities, and real execution/output/state observations for runtime behavior. Documentation does not automatically establish implementation; source inspection is not execution, and successful execution does not establish every acceptance criterion.

Related claims may share a locatable evidence block instead of sentence-by-sentence citations. Distinguish sourced facts, observations, inference, recommendations and unknowns; explain inference and gaps. Unreadable paths, unsupported assertions, role/model self-reports, screenshot existence or the word pass do not independently establish the claimed property. User-supplied material can be a source without being independently verified.

## 2. Bind evidence to object versions

Key evidence must identify its target, checked scope and relevant conditions:

- Source: repository/path, commit and relevant symbols. For uncommitted changes, include actual file hashes, a diff or equivalent workspace identity; HEAD alone does not identify a dirty tree.
- Files/data: actual artifact/input locations and version/content hashes. An artifact modified after inspection is a different checked object.
- Execution: command, working directory, exit code, significant output/log location, actual coverage, and inputs/configuration/dependencies/platform/client versions that affect the conclusion.
- External material: original link/readable reference, applicable version and access date. Access time alone does not establish continued applicability.

Use the minimum information needed to identify the object at the task's risk level, without full-repository snapshots for ordinary answers. Evidence locations must remain readable for the agreed retention period. Follow existing privacy handling instead of disclosing credentials, private logs or unrelated data as proof.

## 3. Mark unverified claims explicitly

Use natural language or existing report fields to distinguish verified, inferred, unverified, blocked or stale claims, without mandatory new protocol enums. Say when work was not run and why missing conditions affect acceptance. Separate failing tests, environment blockers, skips and missing coverage; skips are not passes, and missing tools do not directly establish product defects.

Label mock, static, historical, real local execution, remote CI and native-client observations separately. A summary that tests passed covers only the executed passing set, with skips/failures and acceptance gaps disclosed. Parseable structure, file creation, successful conversion, visual inspection and business correctness are different properties; verify the required level.

Deliver evidenced subsets and continue independent useful work when possible. Required acceptance without proof cannot support verified completion of the whole task. Self-checking by the same executor is not independent review.

## 4. Never reuse stale evidence

Before reuse, check that the object and relevant dependencies still apply. Changes to implementation, tests/assertions, inputs, rules, artifacts or conclusion-relevant environments invalidate old evidence for the changed target pending affected-scope review. Old tests, reviews or images do not prove changed artifacts; the same filename, commit summary or historical pass is insufficient.

Trace evidence dependencies and perform the smallest necessary revalidation: reread affected source, rerun relevant tests, regenerate/check changed artifacts or obtain current material. Unrelated changes do not require every regression; evidence may remain usable when unaffected dependencies and object bindings are established. Preserve old records as historical/stale and bind new evidence to current objects rather than pretending revalidation through status edits, hash refreshes or budget resets.

Handoffs retain claims, object versions, evidence locations, invalidation reasons and pending checks. Memory/checkpoints provide candidate context rather than current authorization or proof.

## Application and execution limits

Short answers may give a conclusion, source/observation and necessary limits. Complex delivery may map claim/criterion → status → object version → evidence → gaps, without mandatory tables or full logs. Use [verification-before-completion](../skills/verification-before-completion/SKILL.en.md), [acceptance-tracking](../skills/acceptance-tracking/SKILL.en.md) and [checkpoint-and-resume](../skills/checkpoint-and-resume/SKILL.en.md) for their respective methods.

Reuse an already supplied current policy body rather than rereading the same file; reread after policy changes.

This is a shared behavioral policy, not automatic evidence authentication. The Python adapter embeds its body in role prompts; existing host checks still inspect commands, scope and checkpoints. The JS template references this file and needs real host reading capability. Native roles/skills must read references as directed; structural checks do not establish compliance by arbitrary sessions. Nonempty evidence in the current result schema does not prove truth, sufficiency or target binding.
