---
name: office-xlsx
description: "Create, read, or edit Excel XLSX data, formulas, and styles while preserving workbook structure; writing a formula does not calculate it."
---

[中文](SKILL.md) | English

Follow explicit language preferences, otherwise the task language; preserve existing document language and machine-readable fields. See the [language policy](../../references/language.md).

# Excel XLSX

Reuse project environments; openpyxl suits ordinary creation and targeted workbook edits. Inspect actual sheets, affected ranges, cell types, formulas, merges, and references. Preserve the original and save a separate result by default. See the [operations guide](../office/references/operations.md) and optional [authoring examples](references/authoring.md).

Load with data_only=False when formulas must survive. Treat numbers, dates, booleans, text identifiers, and display formats separately; styling is not a type conversion. Writing an identifier as a number does not preserve its original leading-zero text. Store external text as text rather than interpreting its prefix as an authorized formula.

pandas helps analyze tabular data, but a DataFrame is not a workbook. Write results to intended ranges without replacing other sheets, formulas, charts, or formatting. XlsxWriter creates files and cannot read/edit existing ones. Renaming .xls, .xlsb, encrypted, or macro files does not make them XLSX; establish dedicated preservation checks for macros, links, pivots, and advanced features rather than promising lossless generic-library round trips.

Writing formulas is not calculation. openpyxl/XlsxWriter do not evaluate them; data_only=True reads caches that may be stale or absent. Use [office-recalculate](../office-recalculate/SKILL.en.md) for refreshed results or immediately available calculated values. Do not replace requested formulas with constants or call stale caches fresh results. Saving again with openpyxl can clear caches, so recalculate the final saved version.

Reopen and check requested sheets, ranges, values, types, formulas, merges, and content to preserve. Verify business results against source data/expected totals separately. Data/formula edits with incidental bold headers or number formats do not require rendering. Use [office-render](../office-render/SKILL.en.md) for appearance-focused tasks or requested visual checks unless explicitly skipped. Change print settings only as requested; use [office-export-pdf](../office-export-pdf/SKILL.en.md) for PDF.

Deliver the actual XLSX and distinguish structure, formula preservation, cache refresh, and visual status. Saving is not proof of calculation, business correctness, or native Excel acceptance. See [provenance and licensing](../../references/dsh-office-provenance.md).
