# Adapt to the target project

[中文](project-context.md) | English

Follow the [language policy](language.md). OpenAS supplies collaboration methods, not a predetermined domain, language, build system or platform. Commands and paths are examples; the target repository and task determine actual choices.

Reuse established context, then read relevant README, applicable AGENTS.md/CLAUDE.md, dependencies, build/CI configuration and source. Small changes do not require a whole-repository scan.

- **Goal/scope:** requested behavior, compatibility, acceptance, allowed files and existing edits.
- **Structure:** related modules, callers and tests; distinguish plugin installation, consumer project and runtime workspace.
- **Execution:** actual runtime/version, platform, package manager and build/start/check commands. Do not assume npm, pytest, CMake or a directory layout.
- **Domain contracts:** confirm units, ownership, errors, data and external dependencies from current code/docs, without importing another project's vocabulary or protocols.
- **Evidence/capabilities:** identify checks available here versus those needing real clients, hardware, data or services; disclose missing tools rather than inventing results.

Investigate repository facts independently. Ask only implementation-relevant user choices that cannot be inferred. Do not require extra OpenAS configuration or rewrite project rules for adoption.

Choose checks by task: UI interactions/states, API input/output/errors and relevant persistence/retries, library/CLI boundaries/exit codes/effects, native target resources/timing, data schemas/duplicates/reproducibility, or documentation sources/links/configuration. These are selection aids, not a universal checklist; do not invent builds or database transactions where absent.

Handoffs preserve established constraints, real commands, language preferences and gaps. Read memory only from the consumer project. Historical examples are not current project facts or permission to resume old work.
