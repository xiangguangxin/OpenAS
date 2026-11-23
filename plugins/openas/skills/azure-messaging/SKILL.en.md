---
name: azure-messaging
description: Diagnose Azure Event Hubs and Service Bus SDK connectivity, authentication, lock, duplication, and checkpoint failures.
---

[中文](SKILL.md) | English

Follow the [language policy](../../references/language.md), [evidence policy](../../references/evidence-policy.en.md), and [project context](../../references/project-context.en.md). See [Microsoft MIT attribution and adaptations](../../references/skill-methods/NOTICE.md).

# Azure messaging SDK diagnosis

Read the actual service, SDK language/version, namespace, queue/topic/consumer group, deployment, error code, and time window. Retain only redacted resource identifiers, logs, and relevant configuration; do not expose connection strings, tokens, or private message contents. Diagnose directly when context is sufficient.

Check authorized service health and telemetry before comparing SDK errors, authentication, network/AMQP, entity names, and SDK settings. Use connected Azure MCP, CLI, logs, or equivalent tools with their actual schema/help. Do not assume a particular MCP tool exists on every host. Missing access limits certainty but does not prevent source/documentation analysis.

Distinguish Service Bus locks, renewal, settlement, sessions, and dead letters from Event Hubs partitions, consumer groups, processor ownership, offsets, and checkpoints. Check idempotency and retries against actual delivery guarantees; increasing retries must not hide duplicate side effects. Relate prefetch, batch, and timeout changes to throughput, lock duration, and processing latency.

Prefer configuration and reproducible local evidence. Test sends/receives, dead-letter replay, checkpoint movement, consumer restarts, and cloud configuration changes have real effects and require existing target-specific authorization. Diagnosis alone does not authorize production operations.

Deliver error, evidence, root cause or hypothesis, minimal fix, and regression checks. Verify normal, duplicate/failure, and offset/lock behavior after repair; retain server-side validation gaps. Verify current guidance at [Microsoft's troubleshooting entry](https://learn.microsoft.com/en-us/azure/developer/azure-skills/skills/azure-messaging).
