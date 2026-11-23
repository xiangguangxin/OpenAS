---
name: remotion-render
description: Render and verify video or still artifacts from an existing Remotion composition without implying recording or animation-authoring capability.
---

[中文](SKILL.md) | English

Follow the [language policy](../../references/language.md), [evidence policy](../../references/evidence-policy.en.md), and [project context](../../references/project-context.en.md). Inspect pinned project versions, entry points, dependencies, assets, and scripts; do not automatically initialize projects or fetch missing dependencies.

# Remotion media export

Identify composition ID, input props, dimensions, frame rate, output type, and destination. Check actual project commands or installed CLI help before listing compositions. Prefer the local binary. If absent, report the blocker and use existing installation authorization; do not let `npx` silently fetch an unknown version.

These command shapes assume an installed CLI; substitute actual entry points and IDs:

```text
remotion compositions <entry-point> --props=<props.json>
remotion render <entry-point> <composition-id> <output.mp4> --props=<props.json>
remotion still <entry-point> <composition-id> <output.png> --props=<props.json>
```

Using the same props, confirm effective composition dimensions, fps, and frame count match the request; resolve mismatches within authorization rather than inventing version-specific override flags. Keep credentials out of props. Record their fingerprint and a non-sensitive summary of actual inputs. Preserve existing rendering-browser configuration and report missing browser/font errors. Cloud rendering, paid resources, and media uploads require task authorization. Check current Remotion and asset terms; this skill grants no commercial media license.

Inspect existing destinations before export; use fresh paths or replacements within authorization. Record commands, versions, exit codes, and output hashes. With available media tools, verify decoding, dimensions, frame rate, duration, and expected audio, then inspect first/middle/last frames. Open stills. Existence or exit code zero alone does not establish media correctness; disclose missing decoding or preview checks.

Primary references: [render](https://www.remotion.dev/docs/cli/render), [compositions](https://www.remotion.dev/docs/cli/compositions). Independently written CLI guidance; upstream skill text is not distributed. See [provenance](../../references/skill-methods/NOTICE.md).
