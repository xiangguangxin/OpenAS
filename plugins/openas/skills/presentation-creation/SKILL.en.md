---
name: presentation-creation
description: Create audience-appropriate editable PowerPoint presentations from trusted material, with native text/charts/tables, notes, source, previews, and explicit validation stages.
license: Apache-2.0
---

[中文](SKILL.md) | English

Follow the [language policy](../../references/language.md).

# Presentation creation

This OpenAS method was rewritten and synthesized on 2026-10-24. Preserve [NOTICE](NOTICE.md), [source records](FUSION_SOURCES.json) and applicable Apache-2.0/MIT terms. Generator/check code is independent; upstream runtime scripts, fonts and images were not copied.

Reuse confirmed audience, goal, language, duration, brand, materials and format. Proceed on clear requests, using a stated simple business-style assumption for missing preferences. Do not invent clients, authors, measurements, citations or benefits. Outline-only requests get outlines; PPTX requests need actual files. Default new decks to 16:9 and choose page count by speaking budget and complexity, including transitions/questions.

Organize a few core messages into context, approach, evidence, limits and action as appropriate, rather than moving every report paragraph to a slide. Each slide needs a main point, evidence, visual expression and notes. Keep sources/quantitative conditions in short annotations/notes, mark example data, and retain original scientific data, units, samples and uncertainty rather than replacing measurements with generated imagery.

Use consistent canvas, margins, hierarchy, colors and available fonts; split or simplify overloaded slides instead of shrinking text indefinitely. Preserve image ratio and labels, with non-color cues. Use native text and editable charts/tables with underlying data; page-sized images are not equivalent editable output. Use [technical diagrams](../technical-diagrams/SKILL.en.md) where needed, checking actual editability.

For new decks the JSON/python-pptx tools are described in [authoring](references/authoring.md); existing suitable tools are allowed. Do not import environment-specific upstream tool mandates or upload materials/use paid decoration services automatically. Inspect copies of existing templates and masters first. The generator creates new decks and does not promise lossless template, SmartArt, macro, animation or embedded-object round trips.

Use authorized directories and isolated dependencies within existing authorization. Verify content/units/sources/notes/timing, then actual PPTX parsing/native objects/data/geometries. Render with a real local Office/LibreOffice renderer to PDF/images and inspect each slide for fonts, wrapping, overflow, alignment, contrast and labels. A hand-drawn preview or successful renderer exit is not visual approval. Fix actual findings, regenerate/recheck, and distinguish creation, structure, rendering, visual inspection and target-client/accessibility acceptance. See [validation](references/validation.md). Missing tools permit source work, not claims that JSON is PPTX.

Deliver PPTX, reproducible JSON/source, required assets, previews and concise check records, including notes, budget, sources and gaps. Preserve original decks and exclude environments, installers, caches, credentials and full private logs.

For image/PDF-only operations on saved decks, use [office-render](../office-render/SKILL.en.md) or [office-export-pdf](../office-export-pdf/SKILL.en.md) without reauthoring. Existing render_deck.py behavior and per-slide rendering acceptance for new decks remain unchanged; conversion does not replace visual review.
