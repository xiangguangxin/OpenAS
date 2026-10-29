---
name: office
description: "Route Office tasks by format and operation: DOCX, XLSX, PPTX authoring, image rendering, PDF export, or formula recalculation."
---

[中文](SKILL.md) | English

Follow explicit language preferences, otherwise the task language; preserve existing document language and machine-readable fields. See the [language policy](../../references/language.md).

# Office task routing

Separate the editable format from any requested image export, PDF conversion, or refreshed calculation results. Reuse existing authorization and tools; clear requests do not need another interview, and available conversions do not justify extra deliverables.

| Goal | Skill |
| --- | --- |
| Create, read, or edit Word .docx | [office-docx](../office-docx/SKILL.en.md) |
| Create, read, or edit Excel .xlsx | [office-xlsx](../office-xlsx/SKILL.en.md) |
| Organize, create, or edit PPTX | Reuse [presentation-creation](../presentation-creation/SKILL.en.md), without a duplicate PPT entry |
| Export page images or inspect visual layout | [office-render](../office-render/SKILL.en.md) |
| Convert a saved Office file to PDF | [office-export-pdf](../office-export-pdf/SKILL.en.md) |
| Refresh XLSX formula caches through a real engine | [office-recalculate](../office-recalculate/SKILL.en.md) |

Standalone export, rendering, or recalculation needs only its operation skill, not every format skill. Reuse loaded instructions; read actual files when the host lacks a skill tool instead of inventing registration. Ordinary project Markdown belongs to project-documentation, not the Office toolchain.

Format skills own editable content/structure; operation skills own the requested conversion. Ordinary text/data changes and incidental bold headers do not require rendering. Use office-render when layout, colors, alignment, or visual review is the primary task, honoring explicit requests to skip rendering. Existing presentation-creation rendering acceptance for new decks still applies.

Use the project's selected or existing Python/Office environment rather than DSH-specific load_workspace_dependencies, present, or sidecar tools. Optional Python dependencies are in [requirements.txt](requirements.txt); shared helpers and actual capabilities are in the [operations guide](references/operations.md). Missing tools should block only dependent operations while allowing usable work; do not automatically install system software, upload files, or switch to paid services.

Write to the task workspace, preserve originals, and create new files by default. Keep outputs/caches/check records out of skill resources. Deliver requested files and concise validation, excluding temporary previews by default. Creation/reopening, conversion success, and visual inspection are separate claims. See [provenance and licensing](../../references/dsh-office-provenance.md).
