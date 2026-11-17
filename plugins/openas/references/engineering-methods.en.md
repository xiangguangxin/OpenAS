# Testing, architecture, and debugging methods

[中文](engineering-methods.md) | English

Choose methods for the current risk. Record the environment, expected behavior, direct evidence, and remaining unknowns.

## Testing

| Method | Execution and acceptance |
| --- | --- |
| Fault injection | Inject model timeout and lost acknowledgement after an adapter dispatch separately. Verify zero dispatches in the first case and preserved unresolved state with no automatic replay in the second. Fix the injection boundary and assert the side effect and recovery state. |
| Metamorphic testing | Define a relationship between a source input and a transformation. Inserting a read-only observation into an ordered trajectory should preserve artifact acceptance and the download count. Reordering required calls or adding a duplicate export should fail the relevant check. |
| Mutation testing | Weaken one guard in a scratch copy and run the same regression. Require the reference code to pass and the mutant to fail the expected assertion. Exclude import and environment errors from detected mutants. |
| Stateful properties | Define legal transitions and invariants. Exercise execution, pause, blocking, reconciliation, and resumption in generated sequences. Retain a failing sequence and its seed. |

Method references: [FoundationDB deterministic simulation](https://apple.github.io/foundationdb/client-testing.html), [metamorphic testing survey](https://arxiv.org/abs/2605.13898), [PIT concepts](https://pitest.org/quickstart/basic_concepts/), and [Hypothesis stateful testing](https://hypothesis.readthedocs.io/en/latest/stateful.html).

## Architecture

- A **quality attribute scenario** specifies the source, stimulus, environment, affected component, expected response, and measure. For a browser action whose acknowledgement is lost in a test run, the runtime retains the unresolved action and makes zero duplicate dispatches before reconciliation.
- Use a **lightweight ATAM review** to exercise top-risk scenarios across alternatives. Compare latency, replaceability, and recovery semantics. Record sensitivity points, tradeoffs, risks, and testable assumptions. Preserve the resulting choice in an ADR.
- An **ADR** records context, alternatives, rationale, consequences, status, and triggers for reconsideration. Link superseded decisions to their replacements.
- An **architectural fitness function** turns an accepted constraint into an automated check. The Runtime example keeps state, trace, and artifact verification on the core side of the dependency boundary from model gateways and GUI adapters.

Method references: [SEI ATAM](https://www.sei.cmu.edu/library/the-architecture-tradeoff-analysis-method/), [Architecture Decision Records](https://adr.github.io/), and [Thoughtworks fitness functions](https://www.thoughtworks.com/insights/articles/fitness-function-driven-development).

## Debugging

1. Hold versions, input, gateway model, application state, and the failure predicate fixed. Capture one passing baseline and one failing run.
2. Align comparable evidence. Locate the first meaningful difference in tool names and outcomes, then compare artifact checks, final status, and any available gateway errors. Ignore incidental timing differences. Mark missing or unresolved trace data as inconclusive.
3. Use **delta debugging** to delete chunks of a reproducible input while preserving the same failure. For suitable JSON arrays, use OpenAS `scripts/minimize_repro.py` and give the target failure a distinctive exit code or output marker.
4. Use the first difference to narrow hypotheses. Confirm the causal explanation in a separate check and preserve the minimal repro as a regression.

Method reference: [Cleve and Zeller on delta debugging](https://www.st.cs.uni-saarland.de/publications/details/cleve-aadebug-2000/).
