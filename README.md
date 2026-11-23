<a id="chinese"></a>

<div align="center">

# OpenAS

**Open Agents & Skills**

**从需求到交付，让 AI 开发有方法、有证据、可验收。**

[![CI](https://github.com/xiangguangxin/OpenAS/actions/workflows/ci.yml/badge.svg)](https://github.com/xiangguangxin/OpenAS/actions/workflows/ci.yml)
[![Agents](https://img.shields.io/badge/Agents-12-2563eb)](plugins/openas/agents)
[![Skills](https://img.shields.io/badge/Skills-72-7c3aed)](plugins/openas/skills)
[![License: MIT](https://img.shields.io/badge/License-MIT-059669)](LICENSE)

**简体中文** · [English](#english)

[快速开始](#快速开始) · [按任务选技能](#按任务选择技能) · [工作流程](#工作流程) · [专项能力](#专项能力) · [进阶文档](#进阶文档) · [验证与贡献](#验证与贡献)

</div>

OpenAS 是面向 **Claude Code / Codex** 的可组合 Agent 与 Skill 工具集。它把需求澄清、决策、开发、调试、评审和验收组织成可复用的方法，帮助你在已有项目中按任务选择技能，并保留可追溯的交付证据。

**12 个角色 · 72 个技能 · 按需组合 · 中英文共用同一套技能。** 独立桌面/浏览器执行引擎由 [Praxis](https://github.com/xiangguangxin/Praxis) 维护；OpenAS 提供工程方法、角色、技能与可选工作流。

<a id="安装与集成"></a>
<a id="运行方式"></a>

## 快速开始

### 1. 获取源码

```bash
git clone https://github.com/xiangguangxin/OpenAS.git
cd OpenAS
```

准备已安装并完成登录的 Claude Code 或 Codex。以下路径替换为本机绝对路径；Python 示例使用 `python3`，Windows 可使用 `python`。

### 2. 选择客户端接入

**Claude Code：** 在你的目标项目中加载插件。

```bash
cd /path/to/your-project
claude --plugin-dir /absolute/path/to/OpenAS/plugins/openas
```

<details>
<summary>需要持久安装 Claude Code 插件？</summary>

```bash
claude plugin marketplace add /absolute/path/to/OpenAS
claude plugin install openas@openas-marketplace --scope project
```

本地插件修改后可用 `/reload-plugins` 重新加载。实际命令以已安装客户端的帮助为准，版本与验收范围见[兼容说明](docs/compatibility.md)。

</details>

**Codex：** 从 OpenAS 仓库根目录安装到目标项目，再检查文件完整性。

```bash
python3 plugins/openas/integrations/codex_skills.py install --project /path/to/your-project
python3 plugins/openas/integrations/codex_skills.py check --project /path/to/your-project
cd /path/to/your-project
codex
```

安装器将完整资源放入目标项目 `.agents/openas/`，创建 `.agents/skills/openas-*` 入口，保留项目其他技能和配置。需要核对真实客户端发现时，在 OpenAS 仓库根目录运行：

```bash
python3 plugins/openas/integrations/codex_skills.py check --project /path/to/your-project --native
```

`check` 检查安装完整性与源版本；`--native` 另检查客户端发现，不启动模型任务。已有安装使用 `update`；更新和卸载规则见[客户接入指南](docs/customer-demo.md#1-安装与预检)。

### 3. 开始第一个任务

不确定用哪个技能时，先让路由选择最小组合。以下内容发给客户端，**不是终端命令**：

| 客户端 | 示例任务 |
| --- | --- |
| Claude Code | `/openas:workflow-routing 为当前项目的修复任务选择最小技能组合：先复现空输入异常，再修改并运行现有测试。` |
| Codex | `$openas-workflow-routing 为当前项目的修复任务选择最小技能组合：先复现空输入异常，再修改并运行现有测试。` |

明确知道任务时可直接调用对应技能。Claude Code 使用 `/openas:<技能ID>`；项目安装后的 Codex 使用 `$openas-<技能ID>`，也可通过 `/skills` 选择。接入方式依据[本地安装器](plugins/openas/integrations/codex_skills.py)、[Codex 技能说明](https://developers.openai.com/codex/skills)与[兼容说明](docs/compatibility.md)。

<a id="核心能力"></a>
<a id="技能与角色"></a>
<a id="技能地图"></a>
<a id="常见任务先选组合再选强度"></a>

## 按任务选择技能

表中使用通用技能 ID，客户端调用时加上对应前缀。按当前任务取用，无需一次加载全部技能。

| 你想做什么 | 推荐入口 | 预期交付 |
| --- | --- | --- |
| 不确定从哪里开始 | [workflow-routing](plugins/openas/skills/workflow-routing/SKILL.md) | 最小技能组合、流程强度与理由 |
| 想法很大，关键决定还不清楚 | [decision-mapping](plugins/openas/skills/decision-mapping/SKILL.md) | 决策地图、依赖、证据与下一步 |
| 为跨模块功能或已有功能变更约定行为 | [spec-driven-development](plugins/openas/skills/spec-driven-development/SKILL.md) | 规格、范围、需求到验收的映射 |
| 新功能从方案走到实现 | [solution-design](plugins/openas/skills/solution-design/SKILL.md) → [test-driven-development](plugins/openas/skills/test-driven-development/SKILL.md) | 足够明确的方案、实现与回归证据 |
| 拆分明确方案、组织多步任务 | [writing-plans](plugins/openas/skills/writing-plans/SKILL.md) · [task-orchestration](plugins/openas/skills/task-orchestration/SKILL.md) | 可独立验收的任务与阻塞关系 |
| 修复异常或错误结果 | [bug-fix](plugins/openas/skills/bug-fix/SKILL.md) | 复现、根因、最小修复与回归检查 |
| 理解代码或评估重构影响 | [codebase-analysis](plugins/openas/skills/codebase-analysis/SKILL.md) · [change-impact-analysis](plugins/openas/skills/change-impact-analysis/SKILL.md) | 真实入口、调用链、影响与兼容风险 |
| 调研技术、比较可行方案 | [technical-research](plugins/openas/skills/technical-research/SKILL.md) · [technology-selection](plugins/openas/skills/technology-selection/SKILL.md) | 有来源的结论、取舍与未解问题 |
| 评审代码、核对最终交付 | [requesting-code-review](plugins/openas/skills/requesting-code-review/SKILL.md) · [acceptance-tracking](plugins/openas/skills/acceptance-tracking/SKILL.md) | 可复核的问题与逐项验收状态 |
| 写文档、交接或保留经验 | [project-documentation](plugins/openas/skills/project-documentation/SKILL.md) · [context-handoff](plugins/openas/skills/context-handoff/SKILL.md) · [project-memory](plugins/openas/skills/project-memory/SKILL.md) | 可信文档、当前现场或可复用知识 |

[查看全部技能](plugins/openas/skills) · [完整英文索引](docs/skills.en.md) · [新增方法与来源](docs/skill-methods.md)

## 工作流程

从目标和验收条件出发，**选择技能 → 实施并收集证据 → 按风险评审与验收 → 交付和交接**。决策不清楚时先调查；输入已经明确时直接进入对应任务。

| 流程强度 | 适用任务 | 保留什么 |
| --- | --- | --- |
| **light** | 明确、单文件、无已知敏感风险的变更 | 范围、实际检查、退出码和对象指纹；修 Bug 还需失败基线 |
| **standard** | 多文件/模块、风险未知或 Office/浏览器/桌面任务 | 适用设计、独立评审与验收 |
| **heavy** | 大范围修改，或安全、接口、迁移、并发、生产事故、核心性能风险 | 影响分析、设计评审与相应专项检查 |

角色按需参与：产品与研究、架构与交互、开发与测试、性能与运维、安全与评审、文档与验收。职责见 [12 个角色](plugins/openas/agents)及[团队契约](plugins/openas/references/team-contract.md)。

需要命令行执行、任务图或中断恢复时使用 [Codex 工作流适配器](plugins/openas/workflows/README.md)。只查看路由建议可在仓库根目录运行：

```bash
python3 plugins/openas/workflows/task_router.py --task plugins/openas/workflows/examples/tiered-light-task.json
```

Skill 提供工作方法，实际工具与操作范围由客户端和任务授权决定。只读路由不执行任务；检查通过只覆盖实际执行的范围，未运行项保留为未验证。

<a id="gui-agent"></a>
<a id="软件重建"></a>
<a id="决策规格与专项扩展--decisions-specifications-and-specialists"></a>

## 专项能力

只在项目和任务需要时启用；依赖目标项目已有工具或另行配置的集成。

| 场景 | 入口 | 使用条件与详细文档 |
| --- | --- | --- |
| React 组件与交互动效 | [react-composition](plugins/openas/skills/react-composition/SKILL.md) · [interaction-design](plugins/openas/skills/interaction-design/SKILL.md) | 已有 React 项目或明确界面任务，保留现有设计系统 |
| 视频或静帧导出 | [remotion-render](plugins/openas/skills/remotion-render/SKILL.md) | 已有 Remotion 项目、素材与渲染依赖 |
| 数据库与消息服务 | [neon-postgres](plugins/openas/skills/neon-postgres/SKILL.md) · [azure-messaging](plugins/openas/skills/azure-messaging/SKILL.md) | 实际使用 Neon / Azure 的项目与对应访问条件 |
| 深度安全审计 | [security-review](plugins/openas/skills/security-review/SKILL.md) | 按需加载覆盖台账与独立复核，记录检查器不代替真实审计 |
| Office、PDF 与演示文稿 | [office](plugins/openas/skills/office/SKILL.md) · [pdf-extraction](plugins/openas/skills/pdf-extraction/SKILL.md) · [presentation-creation](plugins/openas/skills/presentation-creation/SKILL.md) | 按格式准备依赖，详见各技能 |
| 浏览器与桌面目标 | [browser-goal-executor](plugins/openas/skills/browser-goal-executor/SKILL.md) · [gui-goal-executor](plugins/openas/skills/gui-goal-executor/SKILL.md) | 已连接的浏览器/桌面工具；[Nova 指南](plugins/openas/integrations/computer-use/USER-GUIDE.md) |
| 软件重建与行为对比 | [software-reconstruction](plugins/openas/skills/software-reconstruction/SKILL.md) | 获授权的观测、独立规格与可信比较；[重建指南](docs/reconstruction.md) |

React、动效、视频、Neon、Azure 等支持的专项可通过任务的 `capabilities` 显式选择，见[路由说明](plugins/openas/skills/workflow-routing/SKILL.md)。需要独立的桌面/浏览器 Agent Loop 时使用 [Praxis](https://github.com/xiangguangxin/Praxis)，其模型、工具和权限单独配置。

<a id="客户展示与工程接入"></a>

## 进阶文档

| 你需要了解 | 文档 |
| --- | --- |
| 客户演示、环境预检、隔离工作区与交付报告 | [客户接入与演示](docs/customer-demo.md) |
| 阶段执行、任务图、检查点与失败恢复 | [工作流指南](plugins/openas/workflows/README.md) |
| 浏览器、GitHub、文档检索与桌面工具接入 | [MCP 集成总览](plugins/openas/integrations/README.md) · [配置与验收](plugins/openas/integrations/QUICKSTART.md) |
| 经验保存、审查、复用与技能演进 | [项目记忆](plugins/openas/memory/README.md) · [学习生命周期](plugins/openas/memory/learning.md) |
| 客户端支持、语言约定与升级 | [兼容说明](docs/compatibility.md) · [双语维护](docs/bilingual.md) · [CHANGELOG](CHANGELOG.md) |
| 测试与完成声明能证明什么 | [证据规则](plugins/openas/references/evidence-policy.md) · [技能评测](docs/skill-evaluation.md) · [验收记录](docs/validation.md) |

## 验证与贡献

仓库检查使用 Python 3.10+、Node.js 22；Windows smoke 与真实桌面 E2E 分别验收。以下命令在仓库根目录运行，测试依赖见 [CI 配置](.github/workflows/ci.yml)：

```bash
python3 scripts/check_plugin.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s plugins/openas/workflows/tests -p 'test_*.py' -v
node plugins/openas/workflows/tests/agent-team.test.mjs
```

结构检查、模拟测试、原生客户端发现与真实业务验收分开记录；具体范围见 [CI](docs/ci.md)和[贡献指南](CONTRIBUTING.md)。

自有内容主要采用 [MIT](LICENSE)。第三方条款按各自声明保留，参见 [REA](plugins/openas/integrations/rea/README.md)、[演示文稿](plugins/openas/skills/presentation-creation/NOTICE.md)、[DSH 方法](plugins/openas/references/dsh-skills-provenance.md)及[新增方法来源](plugins/openas/references/skill-methods/NOTICE.md)。

---

<a id="english"></a>

<div align="center">

# OpenAS · English

**Open Agents & Skills**

**From requirements to verifiable AI-assisted delivery.**

[简体中文](#chinese) · **English**

[Quick start](#quick-start) · [Choose skills](#choose-skills-by-task) · [Workflow](#workflow) · [Specialists](#specialist-capabilities) · [Documentation](#documentation) · [Validation](#validation-and-contributing)

</div>

OpenAS provides **12 roles and 72 composable skills for Claude Code and Codex**. Choose methods for requirements, decisions, implementation, debugging, review, and acceptance within your existing project, retaining evidence for delivered results. Chinese and English use the same skill IDs. The standalone desktop/browser engine is maintained in [Praxis](https://github.com/xiangguangxin/Praxis).

<a id="setup-and-integrations"></a>
<a id="execution-modes"></a>

## Quick start

### 1. Get the source

```bash
git clone https://github.com/xiangguangxin/OpenAS.git
cd OpenAS
```

Use an installed, authenticated Claude Code or Codex client. Substitute actual absolute paths. Python commands use `python3`; on Windows use `python` if appropriate.

### 2. Connect your client

**Claude Code:** load the plugin from your target project.

```bash
cd /path/to/your-project
claude --plugin-dir /absolute/path/to/OpenAS/plugins/openas
```

For persistent project installation, run `claude plugin marketplace add /absolute/path/to/OpenAS` and `claude plugin install openas@openas-marketplace --scope project`. Local plugin changes can be reloaded with `/reload-plugins`; check installed-client support in the [compatibility guide](docs/compatibility.en.md).

**Codex:** install from the OpenAS repository root, then launch in the target project.

```bash
python3 plugins/openas/integrations/codex_skills.py install --project /path/to/your-project
python3 plugins/openas/integrations/codex_skills.py check --project /path/to/your-project
cd /path/to/your-project
codex
```

The installer copies resources to `.agents/openas/` and creates `.agents/skills/openas-*` entries, preserving unrelated skills/settings. From the OpenAS root, use `python3 plugins/openas/integrations/codex_skills.py check --project /path/to/your-project --native` to check actual client discovery without a model turn. Plain `check` verifies integrity/source version. Existing installs use `update`; see [installation and maintenance](docs/customer-demo.md#1-安装与预检).

### 3. Send your first task

These are **client prompts, not shell commands**:

| Client | Example |
| --- | --- |
| Claude Code | `/openas:workflow-routing Choose the minimal skill bundle to reproduce an empty-input failure, fix it, and run the existing tests.` |
| Codex | `$openas-workflow-routing Choose the minimal skill bundle to reproduce an empty-input failure, fix it, and run the existing tests.` |

Call a known skill directly using `/openas:<id>` in Claude Code or `$openas-<id>` after Codex project installation. Codex also provides `/skills`. See the [local installer](plugins/openas/integrations/codex_skills.py), [Codex skill documentation](https://developers.openai.com/codex/skills), and [compatibility guide](docs/compatibility.en.md).

<a id="capabilities"></a>
<a id="roles-and-skills"></a>

## Choose skills by task

Use generic IDs below with your client's prefix. Load only methods needed now.

| Your task | Entry | Expected output |
| --- | --- | --- |
| Choose where to start | [workflow-routing](plugins/openas/skills/workflow-routing/SKILL.en.md) | Minimal bundle, rigor, and rationale |
| Resolve a large ambiguous goal | [decision-mapping](plugins/openas/skills/decision-mapping/SKILL.en.md) | Decision map, dependencies, evidence, next steps |
| Specify cross-module or shipped-behavior changes | [spec-driven-development](plugins/openas/skills/spec-driven-development/SKILL.en.md) | Contracts, scope, requirement-to-acceptance trace |
| Design and implement a feature | [solution-design](plugins/openas/skills/solution-design/SKILL.en.md) → [test-driven-development](plugins/openas/skills/test-driven-development/SKILL.en.md) | Sufficient design, implementation, regression evidence |
| Slice and coordinate a clear plan | [writing-plans](plugins/openas/skills/writing-plans/SKILL.en.md) · [task-orchestration](plugins/openas/skills/task-orchestration/SKILL.en.md) | Verifiable slices and real blocking edges |
| Fix a defect | [bug-fix](plugins/openas/skills/bug-fix/SKILL.en.md) | Reproduction, cause, minimal fix, regression checks |
| Understand code or assess refactoring | [codebase-analysis](plugins/openas/skills/codebase-analysis/SKILL.en.md) · [change-impact-analysis](plugins/openas/skills/change-impact-analysis/SKILL.en.md) | Actual paths, dependencies, impact, compatibility risks |
| Research and compare technologies | [technical-research](plugins/openas/skills/technical-research/SKILL.en.md) · [technology-selection](plugins/openas/skills/technology-selection/SKILL.en.md) | Sourced findings, tradeoffs, unknowns |
| Review code and verify delivery | [requesting-code-review](plugins/openas/skills/requesting-code-review/SKILL.en.md) · [acceptance-tracking](plugins/openas/skills/acceptance-tracking/SKILL.en.md) | Review findings and criterion-level acceptance |
| Document, hand off, or retain knowledge | [project-documentation](plugins/openas/skills/project-documentation/SKILL.en.md) · [context-handoff](plugins/openas/skills/context-handoff/SKILL.en.md) · [project-memory](plugins/openas/skills/project-memory/SKILL.en.md) | Grounded documentation, current state, reusable knowledge |

[Full skill catalog](docs/skills.en.md) · [Method integration and sources](docs/skill-methods.md)

<a id="frequent-bundles-and-tiered-rigor"></a>

## Workflow

Start with the goal and acceptance criteria: **choose methods → implement and collect evidence → review and verify according to risk → deliver and hand off**. Investigate blocking decisions first; proceed directly when inputs are clear.

| Rigor | Suitable work | Retained evidence |
| --- | --- | --- |
| **light** | Explicit single-file changes without known sensitive risks | Scope, actual checks, exit codes, object hashes; bug fixes also need a failing baseline |
| **standard** | Multiple files/modules, unknown risk, or Office/browser/desktop work | Applicable design, independent review and verification |
| **heavy** | Broad changes, security, interfaces, migrations, concurrency, incidents, core performance | Impact/design review and matching specialist checks |

The [12 roles](plugins/openas/agents) cover product/research, architecture/interaction, development/testing, performance/operations, security/review, and documentation/verification. Follow the [team contract](plugins/openas/references/team-contract.en.md) and involve roles as needed.

Use the [Codex workflow adapter](plugins/openas/workflows/README.en.md) for stage execution, task graphs, and explicit resume. To inspect routing only, run from the repository root:

```bash
python3 plugins/openas/workflows/task_router.py --task plugins/openas/workflows/examples/tiered-light-task.json
```

Skills provide methods; actual tools and authorization come from the host and task. Routing alone executes nothing. Passing checks cover only their actual scope; unexecuted items remain unverified.

<a id="gui-agent-runtime"></a>
<a id="software-reconstruction"></a>

## Specialist capabilities

Activate specialists only for matching projects/tasks with their actual dependencies.

| Scenario | Entry | Conditions and guide |
| --- | --- | --- |
| React composition and motion | [react-composition](plugins/openas/skills/react-composition/SKILL.en.md) · [interaction-design](plugins/openas/skills/interaction-design/SKILL.en.md) | Existing React or explicit UI work; preserve the design system |
| Video/still export | [remotion-render](plugins/openas/skills/remotion-render/SKILL.en.md) | Existing Remotion project, assets, rendering dependencies |
| Database/messaging | [neon-postgres](plugins/openas/skills/neon-postgres/SKILL.en.md) · [azure-messaging](plugins/openas/skills/azure-messaging/SKILL.en.md) | Actual Neon/Azure use and appropriate access |
| Deep security audit | [security-review](plugins/openas/skills/security-review/SKILL.en.md) | Optional coverage and independent validation; record checks are not audits |
| Office, PDF, presentations | [office](plugins/openas/skills/office/SKILL.en.md) · [pdf-extraction](plugins/openas/skills/pdf-extraction/SKILL.en.md) · [presentation-creation](plugins/openas/skills/presentation-creation/SKILL.en.md) | Format-specific dependencies documented in each entry |
| Browser/desktop goals | [browser-goal-executor](plugins/openas/skills/browser-goal-executor/SKILL.en.md) · [gui-goal-executor](plugins/openas/skills/gui-goal-executor/SKILL.en.md) | Connected browser/desktop tools; [Nova setup](plugins/openas/integrations/computer-use/USER-GUIDE.en.md) |
| Software reconstruction | [software-reconstruction](plugins/openas/skills/software-reconstruction/SKILL.en.md) | Authorized observations, independent specification, trusted comparisons; [guide](docs/reconstruction.md#english) |

Explicit task `capabilities` select supported specialist methods; see [routing](plugins/openas/skills/workflow-routing/SKILL.en.md). For a standalone browser/desktop agent loop, use [Praxis](https://github.com/xiangguangxin/Praxis), with separately configured model, tools, and permissions.

<a id="customer-demos"></a>

## Documentation

| Topic | Guide |
| --- | --- |
| Customer demos, preflight, isolated workspaces, delivery reports | [Customer readiness](docs/customer-demo.md) |
| Stages, task graphs, checkpoints, recovery | [Workflow guide](plugins/openas/workflows/README.en.md) |
| Browser, GitHub, documentation, desktop integrations | [MCP overview](plugins/openas/integrations/README.en.md) · [configuration and acceptance](plugins/openas/integrations/QUICKSTART.en.md) |
| Reviewed knowledge, reuse, skill evolution | [Project memory](plugins/openas/memory/README.en.md) · [learning lifecycle](plugins/openas/memory/learning.en.md) |
| Client support, languages, upgrades | [Compatibility](docs/compatibility.en.md) · [bilingual maintenance](docs/bilingual.md) · [changelog](CHANGELOG.md) |
| Claims and evidence limits | [Evidence policy](plugins/openas/references/evidence-policy.en.md) · [skill evaluation](docs/skill-evaluation.en.md) · [validation record](docs/validation.md) |

## Validation and contributing

Repository checks use Python 3.10+ and Node.js 22; Windows smoke and real desktop E2E are distinct. Run from the repository root; test dependencies are listed in [CI configuration](.github/workflows/ci.yml):

```bash
python3 scripts/check_plugin.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s plugins/openas/workflows/tests -p 'test_*.py' -v
node plugins/openas/workflows/tests/agent-team.test.mjs
```

Report structure checks, mocked tests, native discovery, and real business acceptance separately; see [CI](docs/ci.en.md) and [contributing](CONTRIBUTING.md). Project-owned content primarily uses [MIT](LICENSE); retain third-party [REA](plugins/openas/integrations/rea/README.en.md), [presentation](plugins/openas/skills/presentation-creation/NOTICE.md), [DSH](plugins/openas/references/dsh-skills-provenance.md), and [method-source](plugins/openas/references/skill-methods/NOTICE.md) terms.
