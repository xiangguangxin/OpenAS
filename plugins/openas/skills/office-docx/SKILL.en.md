---
name: office-docx
description: "Create, read, or edit Word DOCX files while preserving relevant formatting and validating saved content; ordinary edits are not tracked changes."
---

[中文](SKILL.md) | English

Follow explicit language preferences, otherwise the task language; preserve existing document language and machine-readable fields. See the [language policy](../../references/language.md).

# Word DOCX

Identify creation, reading, targeted editing, or template redesign. Inspect relevant paragraphs, tables, styles, and content the user requires preserved. Prefer project tools; python-docx suits ordinary tasks. See the [Office operations guide](../office/references/operations.md) for environments. Read-only and outline requests do not need new documents.

Save a new file by default. Locate actual text and runs before replacing it: assigning paragraph.text rebuilds runs and does not preserve local fonts, links, or emphasis. Handle a target spanning runs within the affected runs and verify formatting instead of rebuilding the document for one sentence. A title may be a normal paragraph rather than a Heading style or document property.

Use paragraph styles for new headings/body text. Size tables for the section, merged cells, and margins. CJK text may need an eastAsia font assignment; a font name does not establish installation or correct rendering. Read [authoring examples](references/authoring.md) when needed.

Ordinary edits do not need ZIP inventories or unrelated metadata scans. Inspect relevant OOXML for ambiguity, unsupported features, or concrete failure. For real revisions, comments, fields, complex embedded objects, or fidelity-sensitive templates, establish tool support and preserve originals/package parts. Colored text and ordinary replacements are not tracked changes.

Reopen the saved file with python-docx and verify target text, paragraphs/tables, preserved content, and relevant formatting. Content edits with incidental basic styles do not automatically need rendering. Use [office-render](../office-render/SKILL.en.md) for requested visual review or when layout, colors, sizing, spacing, or alignment is the main task, unless skipped explicitly. python-docx does not paginate or render; structural checks do not prove absence of overflow. Use [office-export-pdf](../office-export-pdf/SKILL.en.md) separately for requested PDF output.

Deliver the actual DOCX and verification scope. State gaps in rendering or native Word acceptance without inventing previews or overwriting originals. See [provenance and licensing](../../references/dsh-office-provenance.md).
