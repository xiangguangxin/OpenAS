---
name: office-render
description: "Render saved DOCX, XLSX, PPTX, or PDF to page images and inspect layout; conversion success is not visual acceptance."
---

[中文](SKILL.md) | English

Follow explicit language preferences, otherwise the task language; preserve existing document language and machine-readable fields. See the [language policy](../../references/language.md).

For factual answers, tests, reviews or completion claims, first read and follow the [shared evidence policy](../../references/evidence-policy.en.md).

# Page images and visual review

Render the final saved file through a real renderer rather than drawing a substitute preview from source data. Prefer project/host tools. The shared [operations helper](../office/references/operations.md) supports local LibreOffice → PDF → Poppler PNG; existing PDFs render without LibreOffice. It does not require DSH sidecars, install alternatives, or upload files.

Separate requested image exports from temporary inspection images. Use a new isolated output directory for the current version; reuse unchanged-source renders instead of repeating conversion for diagnosis. DOCX/PPTX/PDF pages are 1-based PDF page numbers. XLSX uses existing print layout: PDF pages are not worksheet indexes, and the helper does not render cell ranges. Exact worksheet regions require a capable host tool; never silently alter print areas/scaling to imply this capability.

For appearance tasks inspect affected pages, regions, charts, and labels; whole-document reviews cover all requested pages. Check CJK/fonts, wrapping/clipping, alignment, table widths, chart scales, and number formats. Command success, PNG existence, or opening an image is not visual approval; the helper's visual_review starts as not_run.

Use the session's actual image-reading capability. Without it, deliver requested images but leave visual review incomplete; do not switch models, guess text geometry, or repeatedly reopen blank previews. Unexpectedly blank/corrupt populated pages require preserving source/diagnostics, stopping blind retries, and reporting the incomplete check. Rerender the corresponding version after fixing a real source defect.

Deliver requested images and review scope; omit inspection-only temporary files by default and do not link deleted outputs. Existing PPT authoring's per-slide render acceptance still applies. Rendering does not refresh source XLSX caches or certify media, animations, native Office layout, or accessibility. See [provenance and licensing](../../references/dsh-office-provenance.md).
