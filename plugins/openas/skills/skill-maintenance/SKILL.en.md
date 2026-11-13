---
name: skill-maintenance
description: "Improve an existing Agent Skill from reproducible routing or execution failures, comparing versions against realistic and held-out cases."
---

[中文](SKILL.md) | English

Follow the [language policy](../../references/language.md) and the [shared evidence policy](../../references/evidence-policy.en.md).

# Maintain an existing skill

Use this for a maintained skill revision. Identify the skill, host, behavior to fix, and observable acceptance criteria. Locate the problem in a scrubbed session excerpt, tool trace, or actual artifact and record the source and location. Distinguish host discovery, incorrect routing, procedure failures after loading, and external tool failures. Use real evidence for observed failures and label synthetic cases.

1. Pin the old commit and complete skill bundle. Convert the failure into a reproducible positive case and add a similar request that should take another route. Cover pressure to skip verification, missing tools, or incomplete inputs where relevant. Freeze independent acceptance cases in advance. Use reproduction and development cases while revising.
2. Run the old version first and retain actual outputs and failure evidence. Make the smallest change at the responsible layer. Start with the description for routing changes. Update relevant references and both language editions for procedure changes. Record feedback that could not be reproduced and evidence limits.
3. Compare versions in fresh workspaces with the same host, model, inputs, authorization, budget, and host assertions. Check routing, artifacts or behavior, constraints, and evidence. Treat exit status and reported skill selection as evidence for their specific checks. Preserve samples and variation when the host exposes timing and token data.
4. Check the final candidate on the frozen cases. Record any required case regression, missing evidence, or client execution failure. If you tune against those cases, use fresh cases for final acceptance. Record both versions, per-case differences, and the rollback point. Submit revisions through the project's review process.

For OpenAS, use repository-root `scripts/evaluate_skills.py --baseline-plugin` and its evaluation guide as needed. For learning and generating candidates in a consumer project, use [project-memory](../project-memory/SKILL.en.md). See [method provenance](FUSION_SOURCES.json) for pinned sources and mappings.
