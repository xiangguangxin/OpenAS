# Skill 方法接入 / Skill method integration

中文与 English 使用同一套 72 个技能。新增 6 个入口，另外 4 项能力融入现有技能。上游不作为子模块或默认依赖。

| 候选 / Candidate | OpenAS 落点 / Entry | 处理 / Integration |
| --- | --- | --- |
| Wayfinder | [decision-mapping](../plugins/openas/skills/decision-mapping/SKILL.md) | 新增决策地图 / New decision map |
| To Tickets | [writing-plans](../plugins/openas/skills/writing-plans/SKILL.md), [task-orchestration](../plugins/openas/skills/task-orchestration/SKILL.md) | 纵向切片与兼容迁移 / Vertical slices and compatible migration |
| Research | [technical-research](../plugins/openas/skills/technical-research/SKILL.md) | 一手资料与研究记录 / Primary-source notes |
| spec-driven-development | [spec-driven-development](../plugins/openas/skills/spec-driven-development/SKILL.md) | 新增规格追踪 / New specification trace |
| security-audit | [security-review](../plugins/openas/skills/security-review/SKILL.md) | 按需深度审计与记录检查 / Optional deep audit and record validation |
| animate | [interaction-design](../plugins/openas/skills/interaction-design/SKILL.md) | 动效、中断及可访问性 / Motion, interruption, accessibility |
| vercel-composition-patterns | [react-composition](../plugins/openas/skills/react-composition/SKILL.md) | 官方文档独立编写 / Independent official-documentation implementation |
| remotion-render | [remotion-render](../plugins/openas/skills/remotion-render/SKILL.md) | 官方文档独立编写 / Independent official-documentation implementation |
| neon-postgres | [neon-postgres](../plugins/openas/skills/neon-postgres/SKILL.md) | 按实际 Neon 使用启用 / Only for actual Neon projects |
| azure-messaging | [azure-messaging](../plugins/openas/skills/azure-messaging/SKILL.md) | 按实际 Azure 服务启用 / Only for actual Azure services |

固定来源提交、许可、弃用项、方法映射和文件指纹见 [NOTICE](../plugins/openas/references/skill-methods/NOTICE.md) 与 [FUSION_SOURCES.json](../plugins/openas/references/skill-methods/FUSION_SOURCES.json)。六个新增入口均有英文配套，现有 ID 保持不变。

## 使用 / Usage

原生会话按需调用：

```text
/openas:decision-mapping 为跨会话的大目标整理未决问题和证据
/openas:spec-driven-development 将当前行为变化映射到任务和验收
/openas:writing-plans 将明确规格拆成可独立验收的任务
/openas:security-review 对指定源码做深度审计，保留覆盖缺口
/openas:react-composition 重构已有 React 组件的状态与组合接口
/openas:remotion-render 导出已有 composition 并验证媒体
/openas:neon-postgres 排查本项目的 Neon 连接和迁移
/openas:azure-messaging 排查指定 Service Bus SDK 的消息锁问题
```

机器路由只返回建议。示例不执行项目或云操作：

```bash
python3 plugins/openas/workflows/task_router.py --task plugins/openas/workflows/examples/specialist-task.json
python3 plugins/openas/skills/security-review/scripts/check_audit.py plugins/openas/skills/security-review/references/audit-example.json
```

专项 `capabilities` 接受 decision-mapping/task-slicing/spec/research/security-audit/react/animation/video/neon/azure-messaging。未设置时保留默认组合，未知或重复项报错。该字段不改变风险等级、执行路线、角色或权限，也不安装工具；实际范围和风险仍必须正确填写。直接执行 Codex 任务还需现有 requirement/acceptance/checks/acceptance_checks 字段；仅规划请求不要启动执行器。

Use native entries on demand. Machine `capabilities` only add matching method recommendations to an existing tiered task. They never change rigor, route, roles, authorization, or tool availability. The sample is planning-only. Executing a Codex task still requires its normal requirement, acceptance, checks, and acceptance mappings. Use actual scope/risks; do not execute a planning-only request.

## 依赖与边界 / Dependencies and limits

- 决策、规格、任务与研究方法无新增运行依赖；深度审计记录检查仅需 Python 标准库。
- React、Remotion、Neon 和 Azure 使用目标项目已有依赖及宿主工具，不安装上游工具集，不自动连接云服务。
- 渲染需要实际 Remotion 项目与媒体检查工具；Neon/Azure 实测需要对应环境及已有授权。缺少条件时保留未验证状态。
- 结构与路由通过不等于模型遵循技能、原生客户端发现、视觉质量或云服务业务正确。

Planning/research instructions add no runtime dependencies; audit consistency uses Python's standard library. Domain entries reuse target-project dependencies and host tools. Remotion media and Neon/Azure live acceptance need their real environments. Structural/routing success is not native discovery, visual quality, or business correctness.

## 验证记录 / Validation record

本次本地检查：

| Check | Actual result | Evidence scope |
| --- | --- | --- |
| `python3 -B scripts/check_plugin.py` | Passed: 72 skills, 99 translation pairs, 12 roles | Metadata, local links, registration, reviewed translation hashes |
| `python3 -B -m unittest discover -s tests -v` | 134 tests, 2 skipped, no failures | Includes 8 audit consistency cases and specialist routing/negative cases |
| `python3 -B -m unittest discover -s plugins/openas/workflows/tests -p 'test_*.py' -v` | 160 tests passed | Local and mocked workflow behavior; includes skill installation integrity |
| `node plugins/openas/workflows/tests/agent-team.test.mjs` | 8 checks passed | Mocked orchestration only |
| Specialist router example and audit example CLI | Passed | Router selects React/motion; audit example remains explicitly incomplete |
| Two isolated agent probes | Reviewed, scope preserved | Decision map on a synthetic team-build goal; rendering plan without files/dependencies/execution |
| Native Codex CLI probes: decision-map, remotion-plan-only | Blocked before model execution | Codex 0.172.0-alpha.2 failed to initialize its app-server in the read-only runtime; not counted as behavioral passes |

隔离代理试用只读所需技能与共享规则，未修改目标或执行外部操作。决策地图保留产品/费用/凭据未知、依赖与证据缺口；视频方案保留入口/CLI 缺口、同一 props、有条件的后续命令与实际媒体验收。两例是当前代理的有限行为试用，不是 Codex/Claude 原生发现或服务端集成证据。视频技能随后明确补充同一 props 的 composition 配置核对，结构检查重新执行。

Optional native cases are available without changing the default evaluation suite:

```bash
python3 scripts/evaluate_skills.py --case decision-map --output /tmp/openas-decision-map
python3 scripts/evaluate_skills.py --case spec-delta --output /tmp/openas-spec-delta
python3 scripts/evaluate_skills.py --case remotion-plan-only --output /tmp/openas-remotion-plan
python3 scripts/evaluate_skills.py --case local-storage-no-neon --output /tmp/openas-local-storage
```

每次输出目录必须是新目录，需可写的已登录客户端；这些命令消耗客户端额度。本次仅尝试前述两例，另两例未运行。未验证：原生技能发现/热加载、真实 React 浏览器交互、Remotion 媒体导出、Neon/Azure 服务端行为、实际目标安全审计与报告。合成审计记录不能代表已审计 OpenAS 或任何线上对象。

The local suites above passed within their stated scope. Two current-agent read-only probes were reviewed; native Codex probes were blocked at startup and provide no model-behavior result. Other native cases, Claude discovery/reload, real React/Remotion behavior, live Neon/Azure operations, and actual security audits remain unverified. Synthetic records do not represent an audit of OpenAS or a deployed target.
