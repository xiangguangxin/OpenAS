<div align="center">

# OpenAS

**Open Agents & Skills**

Start AI-assisted development from clear requirements and deliver verifiable results.

[![CI](https://github.com/xiangguangxin/OpenAS/actions/workflows/ci.yml/badge.svg)](https://github.com/xiangguangxin/OpenAS/actions/workflows/ci.yml)
[![Agents](https://img.shields.io/badge/Agents-12-2563eb)](plugins/openas/agents)
[![Skills](https://img.shields.io/badge/Skills-47-7c3aed)](docs/skills.en.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-059669)](LICENSE)

[简体中文](README.md) | **English**

[Quick start](#quick-start) · [Language](#chinese-and-english) · [Roles](#roles) · [Skills](#skills) · [Workflows](#workflows) · [Installation](#installation-and-updates) · [Validation](#development-and-validation)

</div>

OpenAS provides composable methods for requirements, research, design, implementation, debugging, review and verification. Use **12 roles and 47 skills through a Claude Code plugin**, or the separate **Codex CLI workflow adapter** for explicitly configured stage execution and acceptance checks.

It adapts to web applications, services, libraries, CLI tools, native programs, data processing and documentation. It reads the target project's stack, conventions and existing checks rather than imposing another framework or mandatory OpenAS configuration.

## Quick start

Start Claude Code in your **target project**, substituting your local OpenAS path:

```bash
claude --plugin-dir /path/to/OpenAS/plugins/openas
```

Invoke skills in the session:

```text
/openas:solution-design Design a solution for these requirements, including contracts, failure behavior, and readiness. Respond in English.
/openas:bug-fix Investigate this failure and verify its cause with this project's logs and tests.
/openas:codebase-analysis Explain the entry points, modules, and main call path, citing source locations.
/openas:change-impact-analysis Assess consumers, compatibility risks, and checks affected by this change.
/openas:document-review Review this guide against the implementation. Report actual reader-blocking issues without editing files.
/openas:project-memory Extract reusable project knowledge supported by this task's evidence.
```

Skill/role IDs use the `openas:` namespace. Local `--plugin-dir` applies to that launch. After edits run `/reload-plugins` for subsequent invocations; it does not guarantee in-flight processes switch versions.

## Chinese and English

The same installation supports Chinese and English. No duplicate plugin, role or skill is needed.

- Explicit output-language instructions take priority; otherwise user-facing replies follow the current request language, rather than the language of code, logs or skill text.
- Existing documents, comments and UI copy retain their language unless translation is requested. New deliverables follow explicit language or project conventions, then the task language.
- Commands, paths, API symbols, skill IDs, JSON keys and enum values remain unchanged. Translate explanations, not machine-readable protocols.
- Handoffs preserve response and artifact language preferences.

Examples:

```text
/openas:architecture-design 设计这个模块，用中文解释。
/openas:architecture-design Design this module and explain it in English.
/openas:project-documentation 用中文说明改动，并编写英文 README。
/openas:document-review Review the Chinese guide. Respond in English and keep the document unchanged.
```

Read the [bilingual language policy](plugins/openas/references/language.md). Chinese discovery files remain in place; English skill companions are `SKILL.en.md`, and English role instructions are under `references/en/agents/`, outside role discovery. Both versions share the same authorization and verification requirements. Detailed references, historical evidence and third-party documents may retain their original language; English core guides link to these explicitly.

## Roles

| Role | Responsibility |
| --- | --- |
| [product-manager](plugins/openas/references/en/agents/product-manager.md) | User/market evidence, scope, priorities and testable requirements |
| [researcher](plugins/openas/references/en/agents/researcher.md) | Technical evidence, alternatives and PoCs |
| [cto](plugins/openas/references/en/agents/cto.md) | System understanding, impacts, contracts, architecture and executable tasks |
| [ux-designer](plugins/openas/references/en/agents/ux-designer.md) | User flows, information architecture and interface states |
| [developer](plugins/openas/references/en/agents/developer.md) | Scoped implementation, repairs and related tests |
| [test-engineer](plugins/openas/references/en/agents/test-engineer.md) | Risk-based test strategies, fixtures and cross-module regressions |
| [performance-engineer](plugins/openas/references/en/agents/performance-engineer.md) | Baselines, profiling and controlled optimization experiments |
| [it](plugins/openas/references/en/agents/it.md) | Environment, CI/CD, dependency/toolchain changes and recovery |
| [security-reviewer](plugins/openas/references/en/agents/security-reviewer.md) | Trust boundaries, security findings and repair verification |
| [red-team](plugins/openas/references/en/agents/red-team.md) | Evidence-backed design, code and document review |
| [tech-writer](plugins/openas/references/en/agents/tech-writer.md) | Source-grounded explanations, guides and diagrams |
| [verifier](plugins/openas/references/en/agents/verifier.md) | Independent acceptance checks of actual artifacts |

Use roles as needed, following the [team contract](plugins/openas/references/team-contract.en.md). Resources do not automatically launch teams. Independent review and tool use require real host support; do not claim them when responsibilities were performed in one session.

## Skills

The [complete English catalog](docs/skills.en.md) links every skill and explains when to use it. Common groups include:

| Task | Skills |
| --- | --- |
| Market and requirements | market-research, competitive-analysis, product-requirements |
| Research and selection | technical-research, technology-selection, github-skill-discovery |
| Architecture | solution-design, architecture-design, design-review |
| Existing-system understanding | codebase-analysis, change-impact-analysis, architecture-conformance, architecture-evolution |
| Plans and implementation | roadmap-planning, writing-plans, executing-plans, test-driven-development |
| CI and upgrades | ci-cd, dependency-upgrade |
| Testing and review | test-strategy, integration-testing, requesting-code-review, document-review |
| UX, performance and security | interaction-design, accessibility-review, performance-analysis, security-review, incident-response |
| Documents and presentations | project-documentation, technical-diagrams, presentation-creation |
| Orchestration and continuity | workflow-routing, task-orchestration, checkpoint-and-resume, failure-recovery, context-handoff, parallel-integration, acceptance-tracking |
| Knowledge and delivery | project-memory, verification-before-completion, finish-development-branch, git-worktrees |
| Specialized work | brainstorming, grilling, bug-fix, subagent-driven-development, reverse-engineer-anything |

Design depth follows risk, not document length. Settle costly cross-boundary decisions and failure behavior, leaving reversible local choices to developers. See [implementation readiness](plugins/openas/references/implementation-readiness.en.md) and [project adaptation](plugins/openas/references/project-context.en.md).

## Architecture and workflows

Claude discovers plugin roles/skills from standard directories. The optional Python Codex adapter explicitly loads role and domain resources and calls an existing authenticated CLI. The JS file is a separate host-injected template, not an SDK or directly executable agent runtime. These entry points share conventions but do not share every execution capability.

The default development sequence is requirements/design → design review → necessary docs → implementation → code review → host checks → verifier → final acceptance/scope checks. Simpler tasks may use a smaller route. The Python adapter supports `development`, `repair`, `direct`, `review`, `security-review`, `operations`, `documentation` and `research-design`.

Research/design delivery ends in design artifacts unless implementation is independently authorized. Sequential task graphs validate dependencies and block downstream failures; they do not provide automatic concurrency. Checkpoints validate task/rule/source fingerprints before reuse. Evidence includes command exit codes, outputs, coverage and gaps; no findings or a success summary alone is not product acceptance.

See the [English workflow guide](plugins/openas/workflows/README.en.md) for trusted task JSON, fixtures, scope, resumption, graph execution, memory and research modes. Real-client runs consume model quota and are separate from ordinary tests.

## Installation and updates

For local development, load with `--plugin-dir` and run `/reload-plugins` after edits. For persistent project installation, run in the target project:

```bash
claude plugin marketplace add /path/to/OpenAS
claude plugin install openas@openas-marketplace --scope project
```

Reload in the session. Management commands are:

```bash
claude plugin disable openas@openas-marketplace --scope project
claude plugin enable openas@openas-marketplace --scope project
claude plugin uninstall openas@openas-marketplace --scope project
```

Choose either local-directory or marketplace loading to avoid duplicates. Marketplace installations may use cached copies. After a maintainer increments the manifest version:

```bash
claude plugin marketplace update openas-marketplace
claude plugin update openas@openas-marketplace --scope project
```

Then run `/reload-plugins`. Actual supported flags come from your installed client's help; in-flight work is not guaranteed to reload.

## Optional MCP integrations

Roles define responsibilities, skills define methods, and MCP exposes tools. Core resources work without installing optional integrations. Reuse equivalent host tools where available.

- **Playwright:** UI structure and actual browser operations.
- **GitHub:** repositories, PRs, issues and CI evidence.
- **Context7:** version-appropriate library/framework documentation.
- **REA:** shipped binaries/packages/runtime evidence, not ordinary source analysis or diagram generation.

Detailed configuration/examples in the [integration guides](plugins/openas/integrations/README.md) currently retain Chinese, while upstream REA instructions are English. Reading a skill does not install a server, register tools or grant target execution. No automatic hooks or background listeners are shipped.

## Project memory

Runtime knowledge belongs to the consumer project's `.openas/memory/`, not the plugin. Evidence-backed candidates require semantic review before acceptance, and changed sources invalidate reuse. Task checkpoints are short-lived state, not authorization to resume. `--learn` adds explicit model-assisted extraction/review and candidate-skill lifecycle work; it is not background training or a permissions change.

See the [English memory skill](plugins/openas/skills/project-memory/SKILL.en.md). The detailed storage and learning references remain in their original language. They distinguish observation, candidate knowledge, trial, activation, feedback and rollback; do not infer verified knowledge from free-form model self-report.

## Development and validation

Use Python 3.10+ and Node.js 22 on Linux/WSL. Memory uses POSIX locks. From the repository root:

```bash
python3 scripts/check_plugin.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s plugins/openas/workflows/tests -p 'test_*.py' -v
node plugins/openas/workflows/tests/agent-team.test.mjs
```

Structure checks include relative links and bilingual companion coverage/fingerprints. They do not prove translation quality or real model behavior. Presentation generation tests need the pinned [requirements](plugins/openas/skills/presentation-creation/requirements.txt); real rendering additionally needs Office/LibreOffice and Poppler.

Optional behavior evaluation:

```bash
python3 scripts/evaluate_skills.py --case english-analysis --output /tmp/openas-english-evaluation
python3 scripts/evaluate_skills.py --case chinese-analysis --output /tmp/openas-chinese-evaluation
python3 scripts/evaluate_skills.py --case explicit-english --output /tmp/openas-language-override
```

These use existing client login/model settings, consume quota, require new output directories, and are not default CI. Language checks are basic signals, not proof of semantic translation quality. See [bilingual maintenance and evaluation](docs/bilingual.md). Native Claude discovery/reload and target-client acceptance must be tested separately; mocks are not native-client evidence.

## Sources, contribution and licensing

Use an independent branch, retain user changes and run relevant checks. Update both language editions when changing shared behavior; never refresh translation fingerprints without reviewing meaning. See [bilingual maintenance](docs/bilingual.md), [contribution guide](CONTRIBUTING.md), [compatibility history](docs/compatibility.md) and [changelog](CHANGELOG.md), whose older records retain Chinese.

OpenAS originated from a gem5 collaboration setup and is now project-independent; [migration records](docs/migration.json) preserve provenance, not default facts about new consumers. Project-owned material is [MIT](LICENSE), except explicitly identified content. The presentation skill uses Apache-2.0 with retained third-party MIT/Apache notices; upstream REA retains its own licensing. See [presentation NOTICE](plugins/openas/skills/presentation-creation/NOTICE.md) and [REA provenance](plugins/openas/integrations/rea/README.md).
