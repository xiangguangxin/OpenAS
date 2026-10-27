# OpenAS plugin resources

[中文](README.md) | English

Load this directory from your target project with `claude --plugin-dir /absolute/path/to/OpenAS/plugins/openas`. Its manifest is [.claude-plugin/plugin.json](.claude-plugin/plugin.json). Run `/reload-plugins` after local edits. Installation and update commands are in the English section of repository-root `README.md`.

- **12 roles:** [English role instructions](references/en/agents), with original registration files in [agents](agents). Claude uses names such as `openas:cto`; adding roles does not automatically add them to Codex routes.
- **47 skills:** repository-root `docs/skills.en.md`, with `SKILL.md` discovery entry points and `SKILL.en.md` companions in [skills](skills). IDs/commands do not change by language. Upstream REA already uses English and is preserved.
- [Language policy](references/language.md): explicit preference first, otherwise the task language; preserve existing artifact language unless translation is requested. Machine-readable identifiers stay unchanged.
- [Team contract](references/team-contract.en.md), [project adaptation](references/project-context.en.md), and [implementation readiness](references/implementation-readiness.en.md).
- [Workflow guide](workflows/README.en.md): optional sequential Codex CLI adapter and separate JS host template.
- [Memory](memory/README.md): consumer-project `.openas/memory/`, with reviewed evidence and lifecycle boundaries; detailed reference remains Chinese.

Available optional integrations include Playwright, GitHub and Context7; their detailed [guides](integrations/README.md) retain the original language. No automatic hooks, MCP servers or background watchers are installed. Reading a skill does not install tools or grant execution rights. Reuse the target project's stack, layout and checks; examples/historical reports do not become project facts.
