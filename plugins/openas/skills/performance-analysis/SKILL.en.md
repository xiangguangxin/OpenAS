---
name: performance-analysis
description: Establish reproducible benchmarks, profile execution, and test bottleneck and optimization hypotheses with controlled comparisons rather than single-run timings.
---

[中文](SKILL.md) | English

Follow the [language policy](../../references/language.md).

# Performance analysis

Confirm the question, target metrics, representative workload, version, environment and budget. Distinguish user experience, throughput, resources and simulation metrics; keep units, windows and success criteria consistent.

Record commit, build options, hardware, system/dependencies, input size, concurrency and cache state. Reuse benchmarks, separating warmup, measurement and cleanup. Choose repetition by cost and variance. Distinguish cold start/steady state and single-request/aggregate metrics.

Preserve raw samples and report relevant distributions, spread or intervals, not just best runs. Check load-generator limits, output correctness and profiling overhead. Weaken conclusions when environments differ or samples are insufficient instead of selecting favorable results.

Use runtime-appropriate CPU/memory/I/O profiling to locate hotspots and call paths; separate waiting/execution and total/self cost. Correlation is not causation. Form falsifiable hypotheses and change one main factor while keeping inputs/configuration/metrics comparable. Write benchmarks and collection scripts only in authorized directories; product optimization needs implementation authorization. Do not load-test production or provision paid resources by implication. Bound time/resources and stop on errors or instability.

Deliver baseline/comparison settings, commands, raw data, hotspot evidence, changed factor, benefit calculation and uncertainty. Check correctness and relevant tail-latency/memory costs. Report when improvement is not demonstrated; simulated or non-target hardware results have limited applicability. Performance engineering investigates, IT supports environment, developers handle out-of-scope code, and verifier checks acceptance.
