---
name: technical-diagrams
description: Create maintainable architecture, data-flow, state, sequence, and data-structure diagrams using Mermaid, D2, or native SVG and verify meaning and rendering.
---

[中文](SKILL.md) | English

Follow the [language policy](../../references/language.md).

For factual answers, tests, reviews or completion claims, first read and follow the [shared evidence policy](../../references/evidence-policy.en.md).

# Technical diagrams

Represent requested structure/flow accurately and readably, normally locally without external services. Preserve document language and visual conventions.

Prefer Mermaid for flows/states/sequences, native SVG for precise architecture or memory/pointer/record layouts, and available D2 for larger automatic layouts. Preserve source alongside exports. Connected tldraw/FigJam may support requested collaboration; do not invent tools or upload repository content unsolicited. Wrapping a bitmap in SVG does not create vectors. Read [tool guidance](references/tools.md) only when needed; avoid installing a full toolchain for simple figures.

First establish nodes, edges, directions, states and premises from current source/docs. Keep each figure focused; distinguish calls, data, events and returns with labels. Logical relationships are not deployment and static dependencies are not runtime order. Identify boundaries, omitted parts and failures. Keep main paths consistently oriented, group related nodes, align layers, separate external/internal systems and minimize crossings, detours and obscured labels. Split overview/details instead of crowding.

Use existing image locations, or adjacent `images/`, short hyphenated filenames and relative links with document-language alt text. SVG needs `viewBox`, title/description, readable type (typically 16–18px body, 24–30px title), margins and non-color cues. Use the [template](assets/diagram-template.svg) if useful. Escape XML, keep IDs/markers valid and route arrows around text/unrelated nodes. Chinese text can use Noto Sans CJK SC/Microsoft YaHei/sans-serif fallback; local rendering does not guarantee other systems' fonts.

Run `python3 scripts/check_svg.py IMAGE` from this skill directory for XML/dimensions/local references; it is not a layout validator or security scanner. Preview with available renderers and inspect text, clipping, direction, legend, grouping/crossings and zoom readability. Record actual export results for Mermaid/D2; missing tools permit source delivery but not rendering/visual-pass claims. Check Markdown links, diff and source consistency. Deliver files/embedding location and semantic explanation. Commit/push only within task authorization.
