"""Create, execute, resume and independently verify GUI goals."""
import argparse
import json
from pathlib import Path

from .agent import run
from .model_connection import add_model_arguments, resolve_model_connection
from .recovery import reconcile
from .session import browser_scope, open_session
from .state import create, load
from .tool_trace import compare_checkpoints
from .verification import FileVerifier


def main():
    parser = argparse.ArgumentParser(description="OpenAS GUI Agent")
    commands = parser.add_subparsers(dest="command", required=True)

    goal = commands.add_parser("create")
    goal.add_argument("checkpoint", type=Path)
    goal.add_argument("--goal", required=True)
    goal.add_argument("--criterion", action="append", required=True)
    goal.add_argument("--max-steps", type=int, default=40)
    commands.add_parser("status").add_argument("checkpoint", type=Path)
    comparison = commands.add_parser("compare-traces", help="Find the first recorded checkpoint difference")
    comparison.add_argument("baseline", type=Path)
    comparison.add_argument("candidate", type=Path)

    verifier_command = commands.add_parser("verify", help="Recheck artifacts for a checkpoint without a model")
    verifier_command.add_argument("checkpoint", type=Path)
    verifier_command.add_argument("--verifier", type=Path, required=True)
    recovery = commands.add_parser("reconcile")
    recovery.add_argument("checkpoint", type=Path)
    recovery.add_argument("--outcome", choices=("executed", "not-executed"), required=True)
    recovery.add_argument("--note", required=True)

    for name in ("run", "resume"):
        execution = commands.add_parser(name)
        execution.add_argument("checkpoint", type=Path)
        backend = execution.add_mutually_exclusive_group(required=True)
        backend.add_argument("--nova")
        backend.add_argument("--browser-url", help="Start URL for an isolated Chromium browser")
        execution.add_argument("--download-dir", type=Path, help="Existing directory for new browser downloads")
        execution.add_argument("--browser-executable")
        add_model_arguments(execution)
        execution.add_argument("--approve-pending", action="store_true")
        execution.add_argument("--trace-tools", action="store_true",
                               help="Record local tool names, outcomes, and times in the checkpoint")
        execution.add_argument("--verifier", type=Path, help="JSON rules for independent artifact verification")
        execution.add_argument("--max-model-calls", type=int, default=0)
        execution.add_argument("--max-model-tokens", type=int, default=0)
        execution.add_argument("--max-ui-text-chars", type=int, default=5000)
        execution.add_argument("--max-images", type=int, default=1)
        execution.add_argument("--experience-store", type=Path)
        execution.add_argument("--experience-environment", default="")

    args = parser.parse_args()
    try:
        if args.command == "create":
            result = create(args.checkpoint, args.goal, args.criterion, max_steps=args.max_steps)
        elif args.command == "status":
            result = load(args.checkpoint)
        elif args.command == "compare-traces":
            result = compare_checkpoints(load(args.baseline), load(args.candidate))
        elif args.command == "reconcile":
            result = reconcile(args.checkpoint, outcome=args.outcome, note=args.note)
        elif args.command == "verify":
            result = FileVerifier.from_json(args.verifier).evaluate(load(args.checkpoint))
        else:
            result = _execute(args)
    except (OSError, ValueError, RuntimeError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.command == "verify" and not result["passed"]:
        raise SystemExit(1)


def _execute(args):
    from .experience import ExperienceStore
    from .planner import ModelPlanner

    connection = resolve_model_connection(args)
    if min(args.max_model_calls, args.max_model_tokens, args.max_ui_text_chars, args.max_images) < 0:
        raise ValueError("Token limits must be nonnegative")
    if bool(args.experience_store) != bool(args.experience_environment):
        raise ValueError("--experience-store and --experience-environment must be used together")
    if not args.browser_url and (args.download_dir is not None or args.browser_executable):
        raise ValueError("Browser settings require --browser-url")

    download_dir = args.download_dir.resolve(strict=True) if args.download_dir else None
    planner = ModelPlanner(connection.model, connection.api_key, connection.endpoint,
                           max_tokens=args.max_model_tokens,
                           max_calls=args.max_model_calls, max_text_chars=args.max_ui_text_chars,
                           max_images=args.max_images,
                           experience_store=ExperienceStore(args.experience_store) if args.experience_store else None,
                           experience_environment=args.experience_environment)
    verifier = FileVerifier.from_json(args.verifier) if args.verifier else None
    scope = browser_scope(args.browser_url, download_dir) if args.browser_url else None
    with open_session(planner, nova=args.nova, browser_url=args.browser_url,
                      download_dir=download_dir, browser_executable=args.browser_executable) as backend:
        return run(args.checkpoint, backend, planner, approval=args.approve_pending,
                   verifier=verifier, backend_scope=scope, trace_tools=args.trace_tools)


if __name__ == "__main__":
    main()
