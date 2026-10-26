---
name: incident-response
description: Contain and recover an active service or environment incident, preserve evidence, and verify recovery; hand deeper causal investigation to debugging.
---

[中文](SKILL.md) | English

Follow the [language policy](../../references/language.md).

# Incident response

Confirm environment, symptoms, start time/timezone, affected users/services, recent changes and allowed actions. Prefer existing runbooks. When restoration is the goal, causal investigation should not obstruct evidenced reversible recovery.

Separate confirmed impact, alerts and hypotheses. Use minimal checks to determine failure layer, scope and growth. Preserve relevant logs, metrics, versions, configuration differences and timeline before destructive restarts/cleanup, without delaying necessary containment to collect everything.

Record each action's time, rationale, target, expected effect and rollback. Coordinate shared-state operations rather than changing many things simultaneously. Send notifications only with authorization; exclude credentials and raw sensitive data.

Choose rollback, isolation, degradation, traffic adjustment or existing runbook steps from evidence, not automatic restart. Check targets, impact, data compatibility and recovery conditions first. Continue routine authorized recovery; identify missing decisions for out-of-scope or uncertain destructive effects. Recheck metrics/user paths after each action and stop or revert ineffective actions within predefined limits. Old code may not work after data migration.

Without target access provide executable steps and unexecuted status, not restoration claims. Verify representative requests, errors, latency, data and backlog as applicable, with observation window and residual impact; one health check is insufficient.

Deliver impact, timeline, evidence, actions/results, status, rollback and follow-up. Use [bug fixing](../bug-fix/SKILL.en.md) for deeper causality, separating triggers, causes and amplifiers. IT handles environment, developers code, and verifier recovery/acceptance.
