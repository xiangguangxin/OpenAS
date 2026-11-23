# 规格模板 / Specification template

Use existing project formats when available; select only relevant fields.

- **ID / version / status / baseline:** stable identity, proposed/ready/implemented, actual source reference.
- **Goal and exclusions:** users, observable outcome, deferred ideas with reasons.
- **Current → expected behavior:** normal input, invalid input, failures, repeat/interruption cases.
- **Boundaries:** inputs/outputs, units, data ownership, permissions, compatibility and migration/recovery when applicable.
- **Commands:** verified project build/test/check commands, environment limits; do not invent paths.
- **Open decisions:** consequence, responsible party, evidence needed to close.

| Requirement ID | Capability/module | Task | Check | Current evidence/status |
| --- | --- | --- | --- | --- |
| R-01 | import-preview | T-01 | Preview leaves stored rows unchanged | Unexecuted |

For a shipped change, add a delta with its baseline link, exact behavioral difference, inherited constraints, new/regression criteria, and migration/recovery. Fold actual shipped results into the current specification; retain the delta and its history.
