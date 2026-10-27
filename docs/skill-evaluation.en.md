# Skill behavior evaluation

[中文](skill-evaluation.md) | English

Format checks establish parseable resources. Behavior evaluation inspects how a real client selects skills and respects task boundaries.

`scripts/evaluate_skills.py` uses existing Codex authentication/model settings in isolated temporary workspaces for ten cases:

| Scenario | Host checks |
| --- | --- |
| Ordinary review | requesting-code-review, direct findings, no confirmation questions, unchanged files |
| Explicit interview | grilling, questions, unchanged files |
| Scoped repair | bug-fix, only specified implementation changed, tests preserved, host rerun passes |
| Minimal workflow | workflow-routing, no edits or extra confirmations |
| Handoff | context-handoff, read-only, current state separated from long-term memory |
| Acceptance tracking | acceptance-tracking, read-only, real evidence and limits |
| Chinese/English source analysis | english-analysis / chinese-analysis: routing, read-only scope, summary-language signal |
| Explicit language overrides | explicit-english / explicit-chinese: requested output language overrides main request language |

```bash
python3 scripts/evaluate_skills.py --output /tmp/openas-skill-evaluation
# Run one case; the output directory must still be new.
python3 scripts/evaluate_skills.py --case ordinary-review --output /tmp/openas-review-evaluation
```

These consume real-client quota, with a 180-second default timeout per case and no automatic retries, model changes, or dependency installation. Default CI tests evaluator failure detection only, without model calls. Output must not already exist.

Reports include structured client replies, host gates, and file changes. Exit 0 requires all relevant gates, but human review of finding meaning/evidence remains necessary. `selected_skill` and prose are client declarations; host checks independently validate file scope and repair tests. Limited cases do not validate every skill/model.

Native Claude discovery/reload is separate [integration acceptance](hot-reload-testing.en.md), not replaced by these cases.

## External skill discovery

github-skill-discovery has a separate [real-client candidate-comparison record](../plugins/openas/workflows/evidence/2026-10-24-skill-discovery/README.md): selecting from the full catalog, comparing supplied synthetic snapshots, reviewing content/dependencies/licenses/fit, and remaining recommendation-only without installation. It is outside the default evaluations and does not prove live GitHub search or native installation.

Local Git tests for import_skill.py cover pinned commits, licenses, review-bound fingerprints, adaptation, destination protection, provenance, and validation status. Mechanical checks do not replace semantic or license review.

## Presentation creation

The [synthesis/acceptance record](../plugins/openas/workflows/evidence/2026-10-24-presentation/README.md) includes an openable eight-slide PPTX, real LibreOffice/Poppler rendering, overview, and source. Separate real-client positive/negative cases generated a four-slide native-chart deck and created no file for outline-only requests. Receipts preserve a fixed-value gate's misclassification of Chinese status and its semantic correction.

These trials are outside default model evaluations. Ordinary tests with pinned dependencies check actual PPTX objects/mechanical boundaries without model calls; they do not establish target PowerPoint or accessibility acceptance.

See [bilingual maintenance/evaluation](bilingual.md) for language cases and detector limits. Summary character signals do not establish semantic correctness or the language of the entire delivery; manual review remains necessary.
