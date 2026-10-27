# Compatibility and record formats

[中文](compatibility.md) | English

| Component | Requirements / scope |
| --- | --- |
| Python scripts | Python 3.10+; CI uses 3.10. Memory locks/process groups require POSIX, targeting Linux / WSL. |
| JavaScript tests/examples | Node.js 22, standard modules, no project npm dependency installation. |
| Native Claude plugin | Follow installed CLI plugin commands. The documented environment lacked Claude; no full lifecycle pass was claimed. |
| Claude reload integration | CLI >= 2.1.268, native reload evidence in the same process/session, separate login/quota. |
| Codex adapter | Authenticated CLI supporting `exec --ephemeral --output-schema -o --sandbox`. Version 0.162.0-alpha.17.2 completed pagination and three skill evaluations on 2026-10-22. |
| GitHub gate script | Authenticated `gh` with repository Administration permission; default prints a plan only. |

Client observations apply to their recorded versions, not all past/future clients. Tests do not log in, upgrade clients, or expand sandbox permissions automatically.

## Upgrade to 0.14.2

Add English companions for six integration guides, two memory guides, and five architecture/CI/compatibility/evaluation guides. Preserve Chinese editions and provide language links. Plugin-local translation coverage increases from 63 to 71 pairs. Component IDs, task fields, runtime dependencies, routes, and record formats do not change. Resource changes invalidate old checkpoint evidence under existing resumption rules; translations do not constitute new native-client or MCP acceptance.

## Upgrade to 0.14.1

Root README.en.md is merged into README.md, with English first, `README.md#english` and `README.md#chinese` entry anchors. GitHub uses section navigation rather than hidden language switching. Subdirectory README.en.md files remain; components, IDs, task fields, and routes are unchanged.

## Upgrade to 0.14.0

Add bilingual entry points, English skill/role companions, and shared language rules. Keep 47 skills and 12 roles; SKILL.en.md and references/en/agents/ are not extra registrations. No runtime dependency, route, or JSON field is added; preferences may use requirement/constraints, with schema/enums unchanged. Rule changes invalidate old checkpoint reuse under existing recovery conventions. Detailed references, third-party files, and historical records need not all be translated.

## Upgrade to 0.13.0

Add codebase-analysis and change-impact-analysis, reaching 47 skills with existing discovery and cto/developer. No runtime dependencies, routes, or record migrations. Source analysis does not require reverse-engineering tools or automatically edit/execute targets.

## Upgrade to 0.12.0

Add ci-cd and dependency-upgrade, reaching 45 skills through existing discovery and it/developer. No runtime dependencies, routes, or migrations. Choose consumer package managers, pipeline platforms, and checks from the actual project; reading skills does not install dependencies or deploy remotely.

## Upgrade to 0.11.0

Add document-review, reaching 43 skills through existing discovery/red-team. No dependencies or migrations. It is a document-review method, not a new route or automatic document rewrite/external operation.

## Upgrade to 0.10.0

Add architecture-conformance and architecture-evolution, reaching 42 skills through existing discovery, without dependencies/routes/migrations. CTO gains deviation tracking/evolution planning, remaining read-only by default. Codex does not automatically migrate or check architecture because skills were added.

## Upgrade to 0.9.0

Add presentation-creation, reaching 40 skills. Generation needs Python 3.10+ and pinned requirements.txt; structural checks use the standard library. Actual rendering needs local LibreOffice/Poppler, not automatically installed. CI installs generation dependencies for native-object tests without models or system Office.

JSON source version=1 supports wide / standard and nine concise slide types. The generator creates from JSON, without lossless arbitrary corporate templates, animations, or SmartArt. Verify fonts in target environments; none are distributed. Code/synthesis docs use Apache-2.0 with retained source terms/notices.

## Upgrade to 0.8.0

Add github-skill-discovery, reaching 39 skills with existing discovery/namespaces. No routes/default networking permissions are added. Use actual host search tools; local import scripts require Python 3.10+ and git, without third-party Python dependencies.

Stage/review/test external skills before installation into explicitly new destinations. Do not execute candidate code, install dependencies automatically, or overwrite existing skills. OPENAS_SOURCE.json version=1 records full commits, files/modes, legal files, adaptations, and caller-reported verification history. Standard GitHub.com HTTPS/SSH origin is supported; handle enterprise/special layouts manually.

## Upgrade to 0.7.0

Existing records.json and state_version=2 remain compatible. Add `.openas/memory/learning/state.json` version=1, versioned candidates, and independent trials; these are not created when memory is unused.

Single-task `--learn` explicitly enables read-only extraction, independent review, and drafts, using additional quota. Valid active guidance enters subsequent role context. Old checkpoints missing learned_context treat it as empty; changed resources still need explicit restart-stages or a new run. JS/graph defaults do not change.

Learning/trials need POSIX locks/process groups and existing Codex exec flags. Automated regressions cover output checks, positive/negative trials, and rollback; real model quality, account access, and native discovery require target acceptance. See [learning guide](../plugins/openas/memory/learning.en.md).

## Upgrade to 0.3.0

Apply resources through marketplace version updates or local reload; project memory is preserved.

- **Snapshots:** replace SHA-256 strings with `{ "type": "file", "mode": 420, "sha256": "…" }`. `mode` is decimal POSIX permission (420 = 0644). Preserve historical records; consumers must distinguish shapes.
- **Memory evidence:** old JSON evidence validates its direct file. Explicitly bind non-JSON originals through `sources`, repropose/review; do not refresh old hashes as a substitute for revalidation.
- **Artifacts:** optional relative `artifacts` directories default empty, must not exist initially, and cannot overlap scope/source/Git metadata. Use clean task workspaces for new runs; old artifacts are not automatically deleted.
- **Recovery:** state from 0.3.0 and earlier remains audit material; 0.4.0 adds explicit resumption below.

## Upgrade to 0.6.0

Add `workflow: research-design`, requiring `research_mode: live` or `provided` and scope containing exactly six stage Markdown files. Reviews add `revision_from`; other route structures remain unchanged. Records stay state_version=2, with the new module in rule hashes. Cross-version unfinished runs need inspected differences and explicit restart with budgets preserved, or a new directory.

Live requires `-c web_search="live"`, `--json`, and `item.completed`/`web_search` events. Provided disables native search but does not isolate all networking tools. verified means checked/reviewed design delivery, not implementation, market value, or measured performance; inspect verification_subject.

## Upgrade to 0.5.0

Reach 31 skills across research/design, including market, requirements, technical research, solutions, selection, architecture/review, docs, competition, and roadmap. Retain discovery without dependencies, formats, or routes. Retrieval/experiments depend on actual host capability; the plugin does not install/connect services automatically.

## Upgrade to 0.4.0

Reach 21 skills with seven orchestration methods and five explicit Python single-task routes. JS remains unchanged. `reviewed` is read-only delivery, not implementation verified or automatically harvested implementation success.

state_version=2 adds step cache, rule hashes, checkpoints, and recovery history for the same task/options only. Old state does not automatically migrate. Host checks/verifier rerun; source/rule changes explicitly invalidate stages without changing scope. Graph version=1 is independent; no automatic whole-graph resumption or concurrency is provided.
