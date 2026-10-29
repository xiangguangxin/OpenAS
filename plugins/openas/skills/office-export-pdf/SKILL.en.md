---
name: office-export-pdf
description: "Export saved DOCX, XLSX, or PPTX to a new PDF while preserving sources; PDF-only export does not require image rendering."
---

[中文](SKILL.md) | English

Follow explicit language preferences, otherwise the task language; preserve existing document language and machine-readable fields. See the [language policy](../../references/language.md).

# Export Office to PDF

Confirm the requested artifact is PDF rather than editable source, page images, or refreshed formula caches. Use the final saved document, preserve it, and write a new file/directory by default. Reuse configured project/host exporters or the shared [operations helper](../office/references/operations.md) export-pdf command; specify soffice explicitly when it is outside PATH.

The helper uses a temporary source copy and isolated LibreOffice profile rather than overwriting the original or joining the user's Office session. Do not change margins, print areas, orientation, or scaling by default; spreadsheet PDFs follow existing print settings. If the engine is unavailable or conversion fails, retain usable sources/diagnostics rather than renaming extensions, creating empty files, or drawing substitute images.

Check exit status, the expected nonempty PDF, and its %PDF- signature. These are the helper's stated checks; use existing PDF parsers for requested text/page checks and report actual scope. PDF-only export does not require previews, extra rendering installations, or every Office skill. Use [office-render](../office-render/SKILL.en.md) separately for requested images or visual review.

Deliver the actual PDF, adding source/temporary records only when requested. Explain applicable font/pagination differences from native Word/Excel/PowerPoint, without calling conversion success visual acceptance, native fidelity, or completed formula recalculation. See [provenance and licensing](../../references/dsh-office-provenance.md).
