# 决策地图模板 / Decision map template

Use the project's artifact language. Example IDs are placeholders, not remote issue numbers.

## Destination / 终点

Observable condition that makes the route clear; exclusions and resource limits.

## Decisions / 已决定

| ID | Title | Decision detail | Evidence/version | Consequences |
| --- | --- | --- | --- | --- |
| D-01 | State ownership | Link to retained rationale | Source ref or experiment | Affected questions |

## Questions / 问题

| ID | Question | Type | Depends on | Owner | Status | Closure evidence |
| --- | --- | --- | --- | --- | --- | --- |
| D-02 | Which recovery boundary is required? | decision | D-01 | Unclaimed | open | Agreed recovery scenario |

Use open/in_progress/closed/superseded. Explain every closure; superseded prerequisites require revalidation of dependants. Record claims before starting; do not infer concurrency from separate rows.

## Not yet precise / 待明确

In-scope unknowns that cannot yet be stated as concrete questions.

## Out of scope / 非目标

Excluded work and why; it does not automatically graduate into tasks.

## Handoff / 交接

Current source/artifact versions, frontier, blockers, next step, and authorization limits.
