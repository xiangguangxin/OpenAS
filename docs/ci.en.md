# Automated CI

[中文](ci.md) | English

The [GitHub Actions configuration](../.github/workflows/ci.yml) runs one `checks` job on GitHub-hosted Ubuntu:

1. Plugin structural validation.
2. Root Python unit tests.
3. Workflow Python unit tests.
4. JavaScript workflow mock-host tests.

Runtimes are Python 3.10 and Node.js 22. CI installs pinned presentation-creation/requirements.txt dependencies to test editable PPTX generation, but not system Office. It needs no self-hosted runner, GitLab, model credentials, or custom image. Real Claude hot-reload tests are explicitly disabled; CI success does not establish native loading.

## Triggers and results

- PR creation, reopening, or updates, including forks (first contributions may require administrator approval).
- Merge/direct push to `main`.
- Manual **CI → Run workflow** in Actions.

Ordinary branch pushes do not trigger separate duplicate runs. Documentation edits still run all checks. New runs cancel older unfinished runs for the same PR/branch, with a 10-minute job limit. Any failing check fails the job; inspect Actions logs.

## Merge gate

Workflow execution and branch-protection enforcement are distinct. Configure `main` to require `checks` and an up-to-date base before merge. Single-maintainer use need not require another person's approval. Checks must run successfully before appearing as selectable requirements.

The repository provides a reviewable configuration script:

```bash
python3 scripts/configure_ci_gate.py
# Apply only with authenticated gh and target-repository Administration permission.
python3 scripts/configure_ci_gate.py --apply
```

Default behavior prints a plan. Apply requires PRs, `checks`, a current base, and administrator enforcement without extra reviewers, then reads back configuration. Existing branch protection/rulesets cause refusal rather than overwrite; inspect them first. See [historical remediation/acceptance](review-remediation.md) for recorded execution, not unit tests as proof of active remote enforcement. API authority: [GitHub branch protection](https://docs.github.com/en/rest/branches/branch-protection#update-branch-protection).

## Reproduce locally

On Linux / WSL with Python 3.10+ and Node.js 22:

```bash
export PYTHONDONTWRITEBYTECODE=1
export OPENAS_RUN_CLAUDE_TESTS=0
python3 scripts/check_plugin.py
python3 -m unittest discover -s tests -v
python3 -m unittest discover -s plugins/openas/workflows/tests -p 'test_*.py' -v
node plugins/openas/workflows/tests/agent-team.test.mjs
```

## Official references

- [GitHub Actions](https://docs.github.com/en/actions/get-started/quickstart)
- [Protected branches and required checks](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
