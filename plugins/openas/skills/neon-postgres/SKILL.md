---
name: neon-postgres
description: "在实际使用 Neon Postgres 的项目中处理连接池、迁移、隔离分支和数据库诊断；复用已有项目与 ORM，不为普通 PostgreSQL 或本地存储问题强制接入 Neon。 / Work with Neon Postgres connections, migrations, isolated branches, and diagnostics in projects that actually use Neon."
---

中文 | [English](SKILL.en.md)

遵循[语言约定](../../references/language.md)、[证据规则](../../references/evidence-policy.md)及[项目适配](../../references/project-context.md)。本文件改写了 Neon 上游方法，保留 [Apache-2.0 条款及来源](../../references/skill-methods/NOTICE.md)。

# Neon Postgres

先确认现有项目、branch、database、环境与操作范围；优先复用已有连接引用和 ORM，不打印 `DATABASE_URL` 或另建项目。读取现有环境文件后才做必要修改，不覆盖其他值；没有实际 Neon 使用证据时回到通用数据库调查。

## 连接与迁移

按驱动、运行环境与当前官方文档选择连接方式。短生命周期应用请求可用池化连接；迁移、备份、逻辑复制或依赖会话状态的操作核对是否需要直连，不能把两类 URL 无条件互换。TLS、连接预算、事务行为和 session 限制随实际驱动/版本核对。

Schema 变更保存在项目既有迁移系统中；先在适当隔离环境验证正常数据、边界、锁影响、兼容与恢复。分支可含真实数据，不能把创建分支当作脱敏。分支创建、重置、删除、恢复和生产切换按已有授权与目标身份执行；开发请求不自动许可生产写入或付费扩容。

## 诊断与验证

复用已有 CLI/MCP/SQL 工具，先检查版本/help 和授权资源；没有工具时给出具体计划，不安装父 Skill 或服务。按症状选择连接、锁、查询计划、统计窗口和 compute 状态；区分冷启动、数据库执行与客户端等待，不能用平台特性推导本项目性能。

优先只读检查。`EXPLAIN ANALYZE` 会执行 SQL，不能对写语句当作无副作用诊断；索引“未使用”依赖观察窗口，不能据此自动删除。修改后用相同输入、环境与指标复验，并检查应用读写和迁移状态。交付脱敏目标、差异、命令、证据及未验证环境。

当前行为查阅：[连接池](https://neon.com/docs/connect/connection-pooling)、[分支](https://neon.com/docs/introduction/branching)、[连接方式](https://neon.com/docs/connect/choose-connection)。方案和性能问题可交给 [change-impact-analysis](../change-impact-analysis/SKILL.md) 与 [performance-analysis](../performance-analysis/SKILL.md)。
