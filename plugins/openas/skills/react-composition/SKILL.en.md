---
name: react-composition
description: Design or refactor React component composition, state ownership, and explicit APIs within the existing React project.
---

[中文](SKILL.md) | English

Follow the [language policy](../../references/language.md), [evidence policy](../../references/evidence-policy.en.md), and [project context](../../references/project-context.en.md). Confirm the actual React version, consumers, component contracts, styling, and accessibility mechanisms.

# React composition

Start with concrete duplication, invalid prop combinations, or unsynchronized state. Identify supported consumer combinations and behavior to preserve. Simple props/children suffice for small components; do not build a framework for hypothetical reuse. Express mutually exclusive modes through explicit variants or type constraints and migrate actual consumers before removing old APIs.

Place shared state at the nearest common owner that must coordinate it. Distinguish controlled values, defaults, transient internal state, and notifications to avoid competing sources of truth. Use scoped Context only for real deep sharing, defining missing-provider behavior. Compose children with clear responsibilities while preserving stable keys, focus, and semantics. Use function slots when callers need runtime values.

Preserve existing React APIs and server/client boundaries. Do not upgrade React or replace state libraries as an incidental refactor. Context splitting and memoization require measured rendering evidence before performance claims.

For authorized implementation, use existing tests for controlled/uncontrolled state, event counts, variants, and keyboard behavior; check actual consumers and type/build commands. Review-only requests return findings and proposals. Without a browser run, disclose visual and focus acceptance gaps.

Primary references: [state sharing](https://react.dev/learn/sharing-state-between-components), [Context](https://react.dev/learn/passing-data-deeply-with-context). Independently written; no Vercel candidate prose/examples copied. See [provenance](../../references/skill-methods/NOTICE.md).
