#!/usr/bin/env python3
"""Plan skill combinations or validate a trusted host evidence receipt; never execute tasks."""
import argparse
import json
from pathlib import Path
import sys
from workflow_policy import plan, check_evidence


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--task', type=Path, help='Task JSON with task_kind, rigor, scope and risk_factors')
    mode.add_argument('--evidence', type=Path, help='Trusted runner state JSON; validates completeness only')
    args = parser.parse_args()
    try:
        data = json.loads((args.task or args.evidence).read_text(encoding='utf-8'))
        result = plan(data) if args.task else check_evidence(data)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__': sys.exit(main())
