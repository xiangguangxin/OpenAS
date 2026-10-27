# Changelog

## 0.14.1

- Combine the repository-root README editions into one file, showing English first with English / Simplified Chinese section links while preserving the Chinese content and existing section links.
- Remove the root README.en.md and update the bilingual maintenance guide, English skill catalog, and plugin entry references; subdirectory translations, skills, and roles remain unchanged.

## 0.14.0

- Add Chinese and English entry points and output-language conventions: an English README, English entry instructions for all 47 skills (including upstream English REA), 12 English role descriptions, and English collaboration, project-adaptation, and workflow guides.
- Add English descriptions and companion links to Chinese discovery entries while retaining the same 47 skill IDs, 12 roles, and execution routes; translation does not change machine-readable fields or authorization boundaries.
- Add translation coverage and fingerprint checks, plus optional behavior evaluations for Chinese/English requests and explicit language overrides; detailed technical references, historical evidence, and third-party originals retain their existing languages and licenses.

## 0.13.0

- Add codebase-analysis and change-impact-analysis for understanding current source, core call paths, consumer impacts, required coordinated changes, and verification scope, bringing the skill count to 47.
- Integrate these methods into cto and developer and update the skill map and routing; analysis is read-only by default, with no new roles or executor routes.

## 0.12.0

- Add ci-cd and dependency-upgrade for pipeline configuration and diagnosis, caches and artifacts, version differences, lockfiles, and compatibility verification, bringing the skill count to 45.
- Integrate these methods into it and developer and update the skill map and routing; add no roles, executor routes, or default publishing permissions.

## 0.11.0

- Add document-review to independently check documentation facts, reader tasks, diagram/text consistency, and example evidence, bringing the skill count to 43.
- Clarify red-team's separate document, code, and design review responsibilities, and update documentation handoffs, the skill map, and routing; add no roles or executor routes.

## 0.10.0

- Add architecture-conformance and architecture-evolution for post-implementation architecture checks and staged changes to existing systems, bringing the skill count to 42.
- Extend cto responsibilities to track architectural deviations, plan evolution, and reevaluate decisions; update the skill map and routing. Default to read-only checks or plan delivery, without adding executor routes.

## 0.9.1

- Extend github-skill-discovery with a multi-skill synthesis workflow: capability comparison, method extraction, conflict resolution, independent authoring, validation, and registration.
- Clarify multi-source commits, where adopted methods appear, licensing and modification records, and the boundaries of the single-source import script; the skill count remains 40.

## 0.9.0

- Add presentation-creation by synthesizing three sets of presentation methods from pinned, license-reviewed commits, retaining provenance, copyright, and modification records; the skill count reaches 40.
- Provide an independently implemented JSON-to-editable-PPTX tool supporting nine slide types, native charts/tables, Chinese fonts, speaker notes, and data sources, without requiring paid APIs.
- Add standard-library OOXML/geometry checks, local LibreOffice/Poppler rendering, per-slide previews, and an eight-slide example, distinguishing structural, rendering, visual, and native-client acceptance checks.
- Distribute the presentation skill directory under Apache-2.0 while retaining applicable upstream MIT/Apache terms; no proprietary presentation skills, upstream runtime scripts, fonts, or images were copied.

## 0.8.0

- Add github-skill-discovery for requirements-based search, content/dependency/license review, suitability comparison, installation or adaptation, and validation, bringing the skill count to 39.
- Add a companion script that stages skills from local Git objects at a full commit SHA, retaining applicable legal files, source manifests, and file fingerprints without executing candidate code or downloading dependencies.
- Bind installation to the reviewed package fingerprints without overwriting existing directories; distinguish file copying, host discovery, and invocation validation, recording adaptations and verification history.

## 0.7.0

- Add a four-stage project-learning loop: task observation capture, experience extraction and independent review, candidate-skill generation with positive/negative trials, and feedback evaluation with version rollback.
- Add `--learn` to the single-task adapter for on-demand read-only model extraction and review; by default, capture only limited observations without additional model calls.
- Bind project-skill versions to original lessons, sources, and trial fingerprints, reusing them only after explicit activation; pause after consecutive negative observations and allow rollback when an older version remains valid.
- Provide project-level auditing, manual feedback, read-only diagnostic trial fixtures, and automated tests without changing bundled skills, client permissions, or model parameters.
- Add guidance for merging client MCP configuration, checking the local environment, and validating integration item by item.

## 0.6.0

- Add the executable research-design route, progressing through research, requirements, solution, technology selection, architecture, design documentation, and independent design review, followed by host checks and verification.
- Use structured revision_from in design review to return to the earliest affected stage and rerun all downstream stages, preserving per-stage revision budgets across resumption.
- Explicitly distinguish live/provided research modes; live requires a native completed web_search event and stops if no actual search occurred.
- Restrict each stage to one explicitly designated Markdown file, produce design-review and documentation-handoff records, and reuse checkpoint resumption without proceeding to product implementation.

## 0.5.0

- Add five skills for technical research, solution design and selection, project documentation, competitive analysis, and roadmap planning.
- Add five separate entry points for market research, product requirements, technology selection, architecture design, and design review, bringing the total to 31; solution-design retains the solution and full-chain entry points to avoid duplicated methods.
- Establish handoff conventions connecting research evidence, solution decisions, documentation, roadmaps, and existing implementation plans, distinguishing implemented capabilities, assumptions, and future plans.
- Connect market/competitive research, solution design, technology selection, architecture design, and design documentation, adding stage handoffs and requirement/acceptance mappings.
- Add document-type review points and usage examples; the new skills introduce no tool dependencies or executor routes.

## 0.4.0

- Add seven skills for workflow routing, task orchestration, checkpoint resumption, failure recovery, context handoff, parallel-result integration, and acceptance tracking, bringing the total to 21.
- Support five explicit Python runner routes: development, repair, direct, review, and documentation.
- Introduce state_version=2 for explicit resumption after validating the task, source, rules, and stage artifacts, rerunning host checks and verification without resetting revision counts.
- Add sequential dependency-graph validation and execution, passing actual upstream results, blocking downstream nodes on failure, and allowing independent nodes to continue.
- Generate task.json, handoff.json, and acceptance.json to distinguish machine checks, model review, and items requiring human verification.
- Keep parallel integration as skill guidance, without claiming parallel scheduling or automatic recovery of the entire graph.

## 0.3.0

- Record file content, type, and POSIX permissions in snapshots so scope and acceptance checks detect chmod changes.
- Support original-file dependencies through `sources` in project-memory evidence; queries and reviews validate both receipts and dependency fingerprints.
- Narrow grilling triggers so ordinary reviews directly report investigation results; add executable guidance for worktree and planning skills.
- Allow Codex tasks to explicitly declare new build-artifact directories while keeping source checks enabled.
- Add CLI and frontend state-function examples, optional real-client skill behavior evaluations, and a merge-gate configuration script.
- Add a project-level MIT license, contribution guide, compatibility notes, and acceptance records.

Replace older string SHA-256 snapshots with objects containing `sha256`, `mode`, and `type`; tools consuming run records must adapt. Older memory remains readable, but evidence without `sources` validates only the direct JSON file and does not infer original-source dependencies. See [acceptance status](docs/review-remediation.md) for the scope of actual acceptance and outstanding external prerequisites.

## 0.2.0

- Update roles and skills to identify the stack, constraints, and acceptance methods from the target project.
- Add shared project-adaptation conventions and a pagination-repair example, removing default assumptions specific to the original project.

## 0.1.0

- Initially distribute roles, skills, workflows, and project-memory tools as a plugin.
- See [migration.json](docs/migration.json) for migration provenance and original fingerprints.
