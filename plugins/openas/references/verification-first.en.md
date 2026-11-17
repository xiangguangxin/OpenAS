# Verification first

[中文](verification-first.md) | English

Use this for repairs, behavior changes, architecture consolidation, and release acceptance. Select evidence and entry points proportionate to risk under the [shared evidence policy](evidence-policy.en.md) and existing authorization.

## §0 Treat the active contract as binding

Locate the applicable requirements, design, and test oracle first. Repair implementation that diverges from a valid contract. Escalate missing, conflicting, or disproved contracts upstream, then correct the design and test oracle before code within scope. Review both required behavior that is missing and new behavior that lacks an agreed contract. Preserve business assertions and test semantics during experiments.

Before changing behavior, obtain a baseline that distinguishes the reported failure from an environment problem. Exercise the current target before asserting a fix. Record expected and observed results and missing evidence. Match evidence to the task, including documentation and static constraints.

## CC-A through CC-Q

| Clause | OpenAS application |
| --- | --- |
| CC-A | Review design and the oracle, then trace the last correct and first anomalous value. Revisit contracts, ownership, and ordering for repeated failures in the same area. Use the attribution matrix below. |
| CC-B | Treat a reported cause as a hypothesis. Run the smallest experiment that discriminates between candidates. |
| CC-C | Separate model and tool claims from target observations. Check the exit code, target execution, business assertion, and artifact state as relevant. |
| CC-D | Stop changes that depend on an unreproduced premise. Return evidence and inputs needing revision upstream. Continue independent read-only investigation where useful. |
| CC-E | Exercise the actual candidate package in isolation. For overlay delivery, apply it to a supported installation and run the relevant regression. |
| CC-F | Start with a small document map for authoritative requirements, design, tests, and interfaces. Note versions, disagreements, and gaps. |
| CC-G | Record the baseline branch and commit and follow the project PR/MR flow. When the task includes merge, read back the target branch and verification state before marking it complete. |
| CC-H | Make logs, stacks, and checks locatable. Use `file:function:line` for source when available and bind run evidence to version, command, target, and correlation ID. |
| CC-I | Pass the active contract, baseline, acceptance, preserved constraints, and evidence locations to the actual implementer and verifier using host capabilities. |
| CC-J | Pass paths, environments, and data through ordinary parameters, configuration, or fixtures. Preserve production entry points and avoid single-test or machine-local special cases. |
| CC-K | Include motivation, proven cause or contract, checks, and evidence in commits. Report unchecked items or deployment limits in the PR/MR. |
| CC-L | Put the regression that caught the issue in the appropriate existing gate. For costly or externally dependent checks, register a separate entry point. |
| CC-M | Prefer maintainable structured observations for phase, target, relevant values, and errors. Remove exploratory probes or turn them into controlled logs. |
| CC-N | Verify the gate and ownership as soon as the result lands. Record skip conditions, reasons, and impact separately from passes. |
| CC-O | Attach inspectable evidence and its strength to consequential claims. Distinguish runtime, simulated, static, inferred, and unverified results. |
| CC-P | Use a tool that actually observes the relevant target and property in the current environment. A skipped target, wrong loaded object, or inadequate simulation leaves the claim unverified. |
| CC-Q | In a handoff, single-source migration, or consolidation, test both the benefited path and the path giving way. Verify caller compatibility, preserved behavior, and applicable rollback. |

## Attribution and document review

Use the repository's terminology for cases, the test platform, and the device or system under test. Record evidence, version, and the experiment that distinguishes each candidate.

| Target | Plan and oracle | Implementation and execution | Documents and versions |
| --- | --- | --- | --- |
| Test case | Expected result, equivalence classes, or the assertion | Fixture, data, and actual execution of the assertion | Case preconditions, expected behavior, and applicable version |
| Test platform | Environment, observation, and isolation strategy | Loaded target, dependencies, execution, and collection | Tool versions, configuration, and recorded limits |
| System under test | Boundary contract, state, and timing | First divergence, propagation, and side effects | Interface, build, and release documents for the current artifact |

## Executable check

The Python `repair` workflow accepts `repair_probe`. It checks the configured failing exit and observed failure marker before model stages. It requires the same command to exit successfully, emit a target pass marker, and omit the old failure marker before completion. Use observable output identifying the affected case. See the [workflow guide](../workflows/README.en.md) and [pagination example](../workflows/examples/pagination-task.json). Design correctness, tool fitness, and packaged-release acceptance have their own evidence requirements.
