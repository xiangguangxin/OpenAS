---
name: spec-driven-development
description: Maintain testable specifications and trace requirements through implementation and acceptance for significant changes without imposing paperwork on small fixes.
---

[中文](SKILL.md) | English

Follow the [language policy](../../references/language.md), [evidence policy](../../references/evidence-policy.en.md), and [readiness rules](../../references/implementation-readiness.en.md). Preserve existing specification tools and authorization.

# Specification driven development

Read current requirements, code, and effective decisions. Maintain existing OpenSpec/RFC/design artifacts in place rather than creating a competing source of truth. A clear local repair only needs inputs, expected behavior, and checks in its task.

1. If a goal contains independently verifiable capabilities, first map stable capability IDs, responsibilities, consumers, dependencies, and interface ownership. Resolve dependency cycles and specify each boundary separately. Skip the map for one capability.
2. Use the [template](references/spec-template.md) for goals/exclusions, current/expected behavior, inputs/outputs/failure states, compatibility, actual build/check commands, and testable criteria. Record unknowns, effects, and closure evidence. Route feasibility questions to [decision-mapping](../decision-mapping/SKILL.en.md) or research.
3. Trace stable requirement IDs through capability/module, task, check, and current evidence. Specifications own behavioral contracts; implementers own local function structure. Use [writing-plans](../writing-plans/SKILL.en.md); descriptive specifications do not prove execution.
4. Review readiness and product decisions according to risk. Continue sufficiently specified, authorized implementation without mandatory end-of-turn gates or repeated approval. Design-only requests remain design-only.
5. For shipped behavior, record a delta linked to its effective baseline, changed behavior, migration/recovery, regression, and new acceptance. Defer new ideas during implementation unless scope is explicitly changed. After delivery, update the current specification from actual results and mark the delta implemented while retaining history.

Use [acceptance-tracking](../acceptance-tracking/SKILL.en.md) to distinguish passed, failed, unexecuted, and blocked criteria. Revalidate mappings/evidence after specifications, code, or checks change. For import preview, define whether preview writes data, how invalid rows appear, and how confirmation prevents duplicate import.

See [provenance](../../references/skill-methods/NOTICE.md).
