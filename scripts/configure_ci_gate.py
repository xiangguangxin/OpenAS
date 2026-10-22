#!/usr/bin/env python3
"""Prepare or apply the CI gate to an unprotected GitHub branch using an authenticated gh CLI."""
import argparse
import json
import shutil
import subprocess
from urllib.parse import quote


def gate_payload():
    return {
        'required_status_checks': {'strict': True, 'contexts': [], 'checks': [{'context': 'checks'}]},
        'enforce_admins': True,
        'required_pull_request_reviews': {'required_approving_review_count': 0},
        'restrictions': None,
        'allow_force_pushes': False,
        'allow_deletions': False,
    }


def gh_api(method, path, data=None):
    command = ['gh', 'api', '--method', method, path]
    if data is not None:
        command += ['--input', '-']
    result = subprocess.run(command, input=json.dumps(data) if data is not None else None,
                            capture_output=True, text=True, timeout=45)
    if result.returncode:
        raise RuntimeError('GitHub API request failed; check gh authentication and repository Administration permission locally.')
    return json.loads(result.stdout)


def apply_gate(api, repo, branch):
    path = f'repos/{repo}/branches/{quote(branch, safe="")}'
    current = api('GET', path)
    if current['protected']:
        raise RuntimeError('Branch already protected; inspect existing protection/rulesets instead of replacing them.')
    api('PUT', path + '/protection', gate_payload())
    actual = api('GET', path + '/protection')
    checks = actual.get('required_status_checks') or {}
    contexts = set(checks.get('contexts', [])) | {x['context'] for x in checks.get('checks', [])}
    reviews = actual.get('required_pull_request_reviews')
    if (not checks.get('strict') or 'checks' not in contexts
            or not actual.get('enforce_admins', {}).get('enabled') or reviews is None):
        raise RuntimeError('Protection update returned, but required gate settings did not verify. Inspect GitHub settings.')
    return actual


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', default='xiangguangxin/OpenAS')
    parser.add_argument('--branch', default='main')
    parser.add_argument('--apply', action='store_true', help='Apply the printed plan; requires gh auth with repository admin access')
    args = parser.parse_args()
    if len(args.repo.split('/')) != 2 or any(not x or x in ('.', '..') for x in args.repo.split('/')):
        parser.error('--repo must be owner/name')
    if not args.apply:
        print(json.dumps({'repo': args.repo, 'branch': args.branch, 'mode': 'plan-only', 'payload': gate_payload()}, indent=2))
        return 0
    if not shutil.which('gh'):
        parser.exit(2, 'GitHub CLI is missing. Install gh and authenticate with repository Administration access; no settings changed.\n')
    try:
        apply_gate(gh_api, args.repo, args.branch)
    except (RuntimeError, OSError, ValueError, subprocess.TimeoutExpired) as exc:
        parser.exit(1, str(exc) + '\n')
    print('CI gate applied and verified.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
