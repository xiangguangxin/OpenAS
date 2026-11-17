#!/usr/bin/env python3
"""Reduce a JSON array while an explicitly supplied local check still fails."""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile


def minimize(items, fails):
    """Return a one-element-minimal subsequence for a deterministic predicate."""
    if not fails(items):
        raise ValueError("The original input does not reproduce the requested failure")
    if not items or fails([]):
        return []

    partitions = 2
    while len(items) > 1:
        size = (len(items) + partitions - 1) // partitions
        for start in range(0, len(items), size):
            trial = items[:start] + items[start + size:]
            if fails(trial):
                items = trial
                partitions = max(2, partitions - 1)
                break
        else:
            if size == 1:
                break
            partitions = min(len(items), partitions * 2)
    if not fails(items):
        raise ValueError("The reduced input stopped reproducing the failure")
    return items


def main():
    parser = argparse.ArgumentParser(description=__doc__, epilog="Put {input} in a check argument after --.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--failure-exit", type=int, default=1)
    parser.add_argument("--failure-marker", help="Required substring in the check output")
    parser.add_argument("--max-runs", type=int, default=100)
    parser.add_argument("--timeout", type=float, default=10, help="Seconds per check")
    options, sep, command = _split_args()
    args = parser.parse_args(options)
    if not sep or not command or "{input}" not in command:
        parser.error("Specify a local check after -- with a {input} argument")
    if args.failure_exit <= 0 or args.max_runs <= 0 or args.timeout <= 0:
        parser.error("Failure exit, check budget and timeout must be positive")
    if args.output.exists() or args.output.is_symlink():
        parser.error("Choose a new output path")
    runs = 0
    try:
        items = json.loads(args.input.read_text(encoding="utf-8"))
        if not isinstance(items, list):
            raise ValueError("Expected a JSON array")

        with tempfile.TemporaryDirectory(prefix="openas-repro-") as temp:
            fixture = Path(temp) / "input.json"
            argv = [str(fixture) if arg == "{input}" else arg for arg in command]

            def fails(candidate):
                nonlocal runs
                if runs >= args.max_runs:
                    raise ValueError("Check budget exhausted before confirming a minimal input")
                runs += 1
                fixture.write_text(json.dumps(candidate, ensure_ascii=False), encoding="utf-8")
                result = subprocess.run(argv, capture_output=True, timeout=args.timeout)
                marker = args.failure_marker
                if result.returncode not in (0, args.failure_exit):
                    raise ValueError(f"Unexpected check exit code {result.returncode}")
                return (result.returncode == args.failure_exit and
                        (not marker or marker.encode() in result.stdout or marker.encode() in result.stderr))

            reduced = minimize(items, fails)
        with args.output.open("x", encoding="utf-8") as output:
            json.dump(reduced, output, ensure_ascii=False, indent=2)
            output.write("\n")
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        parser.error(str(exc))

    print(json.dumps({"original_items": len(items), "reduced_items": len(reduced), "checks": runs}))


def _split_args():
    import sys
    options = sys.argv[1:]
    if "--" in options:
        split = options.index("--")
        return options[:split], True, options[split + 1:]
    return options, False, []


if __name__ == "__main__":
    main()
