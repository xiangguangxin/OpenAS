---
name: neon-postgres
description: Work with Neon Postgres connections, migrations, isolated branches, and diagnostics in projects that actually use Neon.
---

[中文](SKILL.md) | English

Follow the [language policy](../../references/language.md), [evidence policy](../../references/evidence-policy.en.md), and [project context](../../references/project-context.en.md). This file adapts Neon methods; retain [Apache-2.0 terms and provenance](../../references/skill-methods/NOTICE.md).

# Neon Postgres

Identify the existing project, branch, database, environment, and operation scope. Reuse connection references and ORM; never print `DATABASE_URL` or create a replacement project. Read environment files before necessary edits and preserve unrelated values. Without actual Neon use, return to general database investigation.

## Connections and migrations

Choose connections using the actual driver, runtime, and current official documentation. Pooled connections can suit short-lived requests; check direct-connection requirements for migrations, backups, logical replication, and session-dependent operations. Do not interchange URLs blindly. Verify TLS, connection budgets, transaction behavior, and session limits for the installed version.

Keep schema changes in the existing migration system. First validate data, boundaries, locking, compatibility, and recovery in an appropriate isolated environment. Branches may contain real data; branching does not sanitize it. Creation, reset, deletion, restoration, and production cutover require existing authorization and correct target identity. Development work does not authorize production writes or paid scaling.

## Diagnostics and verification

Use available CLI/MCP/SQL tools after checking versions/help and authorized resources. Without tools, give a concrete plan rather than installing parent skills or services. Select connection, locking, plan, statistics-window, and compute checks from actual symptoms. Separate cold start, database execution, and client waiting; platform features do not prove project performance.

Prefer read-only checks. `EXPLAIN ANALYZE` executes SQL; it is not a side-effect-free check for writes. Index-use statistics depend on their observation window and do not authorize deletion. Recheck changes with matching inputs, environment, and metrics, including application access and migration state. Deliver redacted targets, diffs, commands, evidence, and environment gaps.

Verify current behavior using [pooling](https://neon.com/docs/connect/connection-pooling), [branching](https://neon.com/docs/introduction/branching), and [connection methods](https://neon.com/docs/connect/choose-connection). Use [impact analysis](../change-impact-analysis/SKILL.en.md) and [performance analysis](../performance-analysis/SKILL.en.md) when needed.
