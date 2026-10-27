# REA integration with OpenAS

[中文](README.md) | English

REA (Reverse Engineer Anything) analyzes shipped binaries, packages, and application behavior; it is not a diagram engine. This directory provides upstream-skill provenance and optional environment checks without changing consumer builds or automatically installing upstream projects/runtimes.

## Included resources and unconfigured capabilities

| Item | Status |
| --- | --- |
| Official reverse-engineer-anything skill and six on-demand references | Included in plugin skills/ |
| Target routing and evidence conventions | Provided below |
| Environment checker | Provided; no downloads or target execution |
| Node/npm, REA CLI, native engines | Not installed by this integration |
| MCP runtime connection | Not registered; skill presence does not establish tools are connected |

Availability depends on the actual consumer terminal/session. Skill files alone do not establish REA readiness.

## When to use REA

| Task | Preferred approach |
| --- | --- |
| Explain available source, APIs, state machines | rg/source and normal documentation methods, without starting REA |
| Analyze source-unavailable executables/libraries or compare binaries | REA binary flow with task-appropriate Ghidra/Hopper/IDA engines |
| Inspect shipped JS/Electron packages | REA JavaScript flow, without requiring native decompilation engines |
| Draw architecture/state diagrams | technical-diagrams; REA supplies evidence, not drawing |
| Observe source-program runtime behavior | Existing logs/debuggers/profilers, not automatic decompilation |

Targets may use different architectures, systems, or devices. Verify format/platform before assuming they can run locally. Target execution, debugger attachment, and external services remain within explicit task authorization.

## Procedure

1. Read the [upstream skill](../../skills/reverse-engineer-anything/SKILL.md), loading only target-relevant references.
2. Read source directly for ordinary source questions. Choose REA only for necessary shipped-artifact/runtime evidence.
3. Use connected tools and actual schemas, not assumptions based on skill prose.
4. Record absolute target path, SHA-256, architecture, REA version, and engine. Separate observation, inference, and unknowns; cite source locations or Evidence IDs.
5. Pass established components/transactions to technical-diagrams. Static inference is not an observed runtime fact.

Example:

> Use skills/reverse-engineer-anything/SKILL.md to statically analyze functions and dependencies in this shipped program. Report evidence and limits; do not run it.

## Local environment check

From the OpenAS plugin root:

```bash
python3 integrations/rea/check_environment.py
```

Output is JSON. Exit 0 means the checker completed, not that REA/MCP is ready. Inspect runtime_prerequisites_found, node_version_supported, and individual results. It checks PATH, versions, and ps compatibility without downloading npm packages, scanning all client configuration, or running targets.

## Optional local-scope MCP registration

These are instructions, **not operations performed by this integration**. Prepare Node/npm and Claude Code and check the pinned package.json engines. At synchronization, upstream version 6.7.0 required Node ^22.19.0, ^24.11.0, or >=26.0.0; the major version alone is insufficient.

Run upstream's local-scope registration from the intended target project:

```bash
claude mcp add --scope local rea -- npx -y rea-agents@6.7.0 mcp
claude mcp list
```

This downloads npm content and changes the current user's project-local Claude registration. Execute only when activation is requested. It does not require committing MCP credentials/.mcp.json or automatically install Ghidra. Native Windows needs upstream's cmd.exe wrapper; WSL uses Linux commands.

After restarting/reconnecting the project, verify actual visible tools. User-level doctor results do not establish local-scope readiness; upstream states doctor/uninstall do not manage this project-local registration.

To remove registration when requested, run in the same project:

```bash
claude mcp remove --scope local rea
```

Do not run all-client setup that changes user-level configuration merely to connect a project. For CLI diagnosis/engines follow the upstream skill's on-demand recovery flow rather than unconditional setup/doctor for normal source questions.

## Sources, licensing, and updates

- Upstream: https://github.com/morluto/rea
- Pinned source commit: a5f982de8dbe4b092cc20ab89d492b7e7028b758
- Upstream package.json: 6.7.0; skill metadata.version: 44
- Synchronization date: 2026-10-21
- Copied subtree: `.agents/skills/reverse-engineer-anything/`, preserved verbatim, with separate local integration notes/checker.
- Upstream MIT terms remain in [LICENSE](LICENSE). Tool names/constraints reflect that commit; npm releases and main are not necessarily identical.

References: [pinned installation guide](https://github.com/morluto/rea/blob/a5f982de8dbe4b092cc20ab89d492b7e7028b758/docs/installation.md), [version/runtime requirements](https://github.com/morluto/rea/blob/a5f982de8dbe4b092cc20ab89d492b7e7028b758/package.json).

For updates fetch the specified commit in a temporary directory, compare/synchronize only the skill subtree, and retain local integration guidance. Recheck licensing, tools, and references before updating provenance. Do not overwrite client configuration or install unrelated upstream development skills. Upstream CI/changelog/tool-design skills are specific to developing REA and were not imported.
