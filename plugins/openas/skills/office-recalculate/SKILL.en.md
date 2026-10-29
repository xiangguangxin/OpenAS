---
name: office-recalculate
description: "Refresh XLSX formula caches with a real spreadsheet engine and verify formulas and results; constants, stale caches, and PDF export are not recalculation."
---

[中文](SKILL.md) | English

Follow explicit language preferences, otherwise the task language; preserve existing document language and machine-readable fields. See the [language policy](../../references/language.md).

For factual answers, tests, reviews or completion claims, first read and follow the [shared evidence policy](../../references/evidence-policy.en.md).

# Recalculate XLSX formulas

Use this for refreshed caches or immediately readable calculated values, not every ordinary data/formula edit. Save final inputs/formulas first and retain the original. Use Excel, LibreOffice, or a real host engine supporting the requested functions. Without an engine, report unrefreshed caches rather than substituting Python eval, a partial formula interpreter, or manually written constants.

The shared [operations helper](../office/references/operations.md) recalculate command resaves a temporary copy as a new XLSX with an isolated LibreOffice profile. Before engine execution, openpyxl clears old caches in the copy and requests full automatic calculation, so simply copying old values cannot pass. This staging round trip also does not guarantee advanced-feature fidelity. It supports ordinary local workbooks, rejecting macros, external data connections/links, and recognized external-data formulas. Array/data-table formula preservation is unsupported. Complex functions, dynamic arrays, add-ins, live data, or Excel-specific requirements need an appropriate real engine; external-source refresh is not implied.

Reopen results with both openpyxl data_only=False and data_only=True: check original formula expressions/locations separately from caches, errors, and requested values/totals. The helper checks unchanged formula maps, available caches, and no formula errors, distinguishing cached empty strings from missing caches. Missing/changed formulas, errors, or absent caches retain output and a failure report rather than passing recalculation.

Cache presence is not business correctness. Verify requested results against inputs and check sheets, styles, and other preservation requirements. LibreOffice round trips can affect advanced features/native presentation. Do not overwrite refreshed output with a subsequent save that discards caches; recalculate the final version after any changes.

Deliver a new formula-preserving workbook, engine, and verification scope. Use [office-render](../office-render/SKILL.en.md) / [office-export-pdf](../office-export-pdf/SKILL.en.md) separately for images/PDF. Distinguish untouched source, preserved formulas, refreshed caches, and correct business results. See [provenance and licensing](../../references/dsh-office-provenance.md).
