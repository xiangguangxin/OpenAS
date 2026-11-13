"""Synthetic, read-only fixtures for paired skill behavior evaluation."""

CASES = {
    'feedback-outdated': (
        'Triage the existing review feedback in fixture.txt against the current PR head. Address each thread in the report. Analysis only.',
        'pr-review-feedback',
        'Current head bbb. Contract: empty input returns 0. Current average divides sum by length. '
        'Thread REV-A on old head aaa reports an empty-list exception. REV-B reports the same issue.',
        (r'REV-A', r'REV-B', r'duplicate|重复', r'bbb'),
    ),
    'release-stale-artifact': (
        'Check release readiness from fixture.txt and identify the remaining steps. Preparation only.',
        'release-management',
        'Version 1.2.0 target bbb has passing checks. Package wheel.whl was built on aaa. '
        'The remote tag points to aaa. No upgrade smoke test is recorded.',
        (r'wheel\.whl', r'aaa', r'bbb', r'smoke|冒烟'),
    ),
    'coverage-profile-mismatch': (
        'Diagnose the coverage gap in fixture.txt and say what evidence is needed to establish coverage. Analysis only.',
        'coverage-analysis',
        'Build B17 includes the reported decision. Profile P16 comes from build B16. '
        'The report combines P16 with B17, but B17 has no matching profile.',
        (r'B17', r'P16', r'mismatch|incompatib|does not match|different|不匹配|不一致'),
    ),
    'feedback-ordinary-review': (
        'Review this repository for actual defects against README and cite the location. Analysis only.',
        'requesting-code-review',
        '',
        (r'average\.py', r'empty|ZeroDivisionError|空'),
    ),
    'release-pipeline-only': (
        'Investigate the broken CI workflow described in fixture.txt and say how to fix the configuration. Analysis only.',
        'ci-cd',
        'GitHub Actions job linux-test fails before building. Step checkout is missing; '
        'the job tries to run python3 -m unittest from an empty workspace.',
        (r'checkout', r'linux-test'),
    ),
    'coverage-test-plan-only': (
        'Design a risk-based test matrix for fixture.txt. Analysis only.',
        'test-strategy',
        'A JSON importer must reject malformed input without changing an existing record. '
        'Valid input creates a new record. The service retries one transient database failure.',
        (r'malformed|invalid|格式|非法', r'retry|retries|重试'),
    ),
    'holdout-feedback-late-reply': (
        'Disposition the remaining PR review thread using fixture.txt. Analysis only.',
        'pr-review-feedback',
        'Head f42 implements case-insensitive IDs. Thread ISSUE-Z originally reported uppercase IDs fail. '
        'A later reply includes a failing mixed-case integration test on f42. No fix has landed for mixed-case IDs.',
        (r'ISSUE-Z', r'f42', r'mixed.case|混合'),
    ),
    'holdout-release-partial-publish': (
        'Determine what to resume after an interrupted release using fixture.txt. Preparation only.',
        'release-management',
        'v2.1.0 already points at target c17. The published Linux archive linux.zip has the expected digest. '
        'The Windows archive win.zip is missing. Windows install verification has not run.',
        (r'c17', r'linux\.zip', r'win\.zip', r'install|安装'),
    ),
    'holdout-coverage-condition-counts': (
        'Assess whether the coverage evidence in fixture.txt establishes MC/DC and propose a missing test. Analysis only.',
        'coverage-analysis',
        'A and B determine whether output is 1 or 0. A=false, B=false returns 0; A=true, B=true returns 1. '
        'Only condition counters exist. Inputs can set A and B independently.',
        (r'independen|独立', r'false|假', r'true|真'),
    ),
}

SUITES = {
    'development': tuple(name for name in CASES if not name.startswith('holdout-')),
    'holdout': tuple(name for name in CASES if name.startswith('holdout-')),
}
