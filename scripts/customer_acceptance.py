#!/usr/bin/env python3
"""Opt-in real Praxis execution followed by independent artifact verification."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import shutil
import sys

SPEC = importlib.util.spec_from_file_location('acceptance_harness', Path(__file__).resolve().parents[1]/'plugins/openas/workflows/codex-team.py')
h = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(h)


def run(checkpoint, verifier, output, nova=None, browser_url=None, downloads=None,
        resume=False, client='praxis', timeout=900):
    if bool(nova) == bool(browser_url):
        raise ValueError('Select exactly one real backend: Nova or browser URL')
    if nova and platform.system() not in ('Windows', 'Darwin'):
        raise ValueError('Nova desktop acceptance requires native Windows or macOS')
    if timeout <= 0:
        raise ValueError('Positive timeout required')
    executable = shutil.which(client)
    if not executable:
        raise ValueError('Install the independent Praxis package before real acceptance')
    checkpoint = checkpoint.resolve(strict=True)
    verifier = verifier.resolve(strict=True)
    initial = json.loads(checkpoint.read_text(encoding='utf-8'))
    config = json.loads(verifier.read_text(encoding='utf-8'))
    criteria = initial.get('criteria', [])
    if not criteria or any(not isinstance(config.get('criteria', {}).get(c), dict)
                           or config['criteria'][c].get('fresh') is not True
                           or not config['criteria'][c].get('run_id_pointer') for c in criteria):
        raise ValueError('Every criterion requires fresh artifact and run ID verification rules')
    output = output.absolute()
    if any(p.is_symlink() for p in (output, *output.parents)):
        raise ValueError('Evidence output must not traverse symlinks')
    output.mkdir(parents=True, exist_ok=False)
    command = [executable, 'resume' if resume else 'run', str(checkpoint), '--verifier', str(verifier)]
    if nova:
        command += ['--nova', str(nova.resolve())]
    else:
        if not downloads or not downloads.is_dir():
            raise ValueError('Browser acceptance requires an existing download directory')
        command += ['--browser-url', browser_url, '--download-dir', str(downloads.resolve())]
    receipt = {'version': 1, 'backend': 'nova' if nova else 'browser', 'platform': platform.system(),
               'checkpoint_id': initial['id'], 'status': 'failed',
               'business_semantics': 'requires_human_review', 'simulation': False}
    try:
        rc = h.execute(command, output, timeout, output/'execution.stdout.log', output/'execution.stderr.log')
        verify_rc = h.execute([executable, 'verify', str(checkpoint), '--verifier', str(verifier)],
                              output, 30, output/'verification.json', output/'verification.stderr.log')
        final = json.loads(checkpoint.read_text(encoding='utf-8'))
        verification = json.loads((output/'verification.json').read_text(encoding='utf-8'))
        receipt.update(execution_exit_code=rc, verification_exit_code=verify_rc,
                       checkpoint_status=final.get('status'), verification=verification,
                       checkpoint_sha256=hashlib.sha256(checkpoint.read_bytes()).hexdigest(),
                       verifier_sha256=hashlib.sha256(verifier.read_bytes()).hexdigest())
        if rc == 0 and verify_rc == 0 and final.get('id') == initial['id'] and final.get('status') == 'completed' and verification.get('passed'):
            receipt['status'] = 'passed'
    except (h.HarnessError, OSError, ValueError) as exc:
        receipt['error'] = str(exc)
    (output/'receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding='utf-8')
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--checkpoint', type=Path, required=True)
    parser.add_argument('--verifier', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    backend = parser.add_mutually_exclusive_group(required=True)
    backend.add_argument('--nova', type=Path)
    backend.add_argument('--browser-url')
    parser.add_argument('--download-dir', type=Path)
    parser.add_argument('--resume', action='store_true')
    parser.add_argument('--timeout', type=int, default=900)
    parser.add_argument('--client', default='praxis')
    args = parser.parse_args()
    try:
        receipt = run(args.checkpoint, args.verifier, args.output, args.nova, args.browser_url,
                      args.download_dir, args.resume, args.client, args.timeout)
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(json.dumps(receipt, ensure_ascii=False))
    return 0 if receipt['status'] == 'passed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
