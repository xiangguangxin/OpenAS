# 方法来源、许可与取舍 / Method provenance, terms, and decisions

Reviewed: 2026-11-23. Full source commits, normalized-text SHA-256 values, adopted/excluded methods, and target paths are recorded in [FUSION_SOURCES.json](FUSION_SOURCES.json). New and revised OpenAS instructions are adaptations, not upstream runtime integrations or submodules. Original execution scripts, remote setup, hooks, templates, and service registrations are not bundled.

| Source | Adopted OpenAS method | Terms retained |
| --- | --- | --- |
| mattpocock/skills: wayfinder, to-tickets, research | Decision destination/frontier, evidence-linked resolutions, vertical slices, compatible batch migration, primary-source research notes | [Matt Pocock MIT](licenses/matt-LICENSE.txt) |
| addyosmani/agent-skills: spec-driven-development | Capability boundaries, versioned behavioral contracts, requirement/task/check trace, deferred scope and shipped deltas | [Addy Osmani MIT](licenses/addy-LICENSE.txt) |
| cloudflare/security-audit-skill | Coverage ledger, root-cause fingerprints, independent confirmation, separate certainty and severity | [Cloudflare MIT](licenses/security-LICENSE.txt) |
| emilkowalski/skills: animate | Motion purpose/tool selection, interruption, exit, reduced motion and device checks | [Emil Kowalski MIT](licenses/animate-LICENSE.txt) |
| neondatabase/agent-skills: neon-postgres | Existing project/ORM reuse, connection context, migrations, branches and diagnostics | [Apache-2.0](licenses/neon-LICENSE.txt) |
| microsoft/azure-skills: azure-messaging | SDK/version/health/configuration diagnosis, distinct lock/checkpoint failures, evidence-driven repair | [Microsoft MIT](licenses/azure-LICENSE.txt) |

## 中文

以上方法均已按 OpenAS 重新组织、改写并补充中文和英文说明。适配保留已有授权、按需加载、项目工具和证据规则；不继承默认后台代理、每票强制结束会话、所有阶段重复审批、全局安装、自动付费/生产操作或某一宿主专属工具名。任务切片保留实际修改范围；动效允许按需求关闭；独立确认不可由单人自报代替。

Neon 改写文件为 `skills/neon-postgres/SKILL.md` 与 `SKILL.en.md`，已显著标记改写及来源，Apache-2.0 条款继续适用其衍生方法；新增 OpenAS 内容的根 MIT 许可不覆盖上游条款。审查快照未发现 Neon 的额外 NOTICE 文件；未引入其其他资源。

Vercel 与 Remotion 候选在所审快照中没有找到完整适用的分发条款；Vercel frontmatter 中的 MIT 标签不代替完整许可核对。二者排除为融合输入，不复制或摘要引入其文本、代码、规则表和资源。对应 `react-composition` 与 `remotion-render` 是依据 React/Remotion 官方产品文档独立编写的 OpenAS 操作指引；来源链接列在清单中。不据此宣称获得产品、素材或商业使用许可。

深度审计的 Python 检查器为 OpenAS 独立实现，仅核对本地 JSON 的记录关系和字段，不复用 Cloudflare schema/校验器，不执行扫描、模型编排或 OS 隔离。技能、检查器和路由均不能证明原生客户端发现、模型行为或云服务已通过验收。实际检查与限制见[接入记录](https://github.com/xiangguangxin/OpenAS/blob/main/docs/skill-methods.md)。

## English

Methods above were reorganized, rewritten, and paired in Chinese/English for OpenAS. Adaptations retain existing authorization, conditional loading, actual project tools, and evidence rules. They exclude default background agents, forced session stops, repeated phase approvals, global installation, automatic paid/production actions, and assumed host-specific tools. Task slices retain actual edit scope, motion may be disabled, and self-report cannot establish independent verification.

The modified Neon derivatives are `skills/neon-postgres/SKILL.md` and `SKILL.en.md`, prominently marked as adaptations. Retained Apache-2.0 terms apply; OpenAS's root MIT does not replace third-party terms. No additional Neon NOTICE was found in the reviewed snapshot; other Neon resources are not included.

Complete applicable redistribution terms were not established for the Vercel and Remotion candidate snapshots. A frontmatter MIT label alone is insufficient. Both are excluded as fusion inputs; their prose, examples, rule tables, and assets are neither copied nor summarized into the deliverable. Corresponding React/Remotion entries were independently written from official product documentation listed in the manifest. This grants no product, asset, or commercial-use license.

The OpenAS Python audit checker is independently implemented for local JSON consistency; it does not reuse Cloudflare schemas/validators or perform scanning, agent orchestration, or OS isolation. Packaging and record validation do not establish native discovery, model behavior, or live-service acceptance. See the [integration record](https://github.com/xiangguangxin/OpenAS/blob/main/docs/skill-methods.md) for actual checks and limits.
