"""Explicit opt-in experience curation and search."""
import argparse
import json
from pathlib import Path
from .experience import ExperienceStore
from .verification import FileVerifier

def main():
    parser = argparse.ArgumentParser(description="OpenAS verified experience store")
    parser.add_argument("--store", type=Path, required=True)
    sub = parser.add_subparsers(dest="command", required=True)
    add = sub.add_parser("add")
    add.add_argument("checkpoint", type=Path)
    add.add_argument("--verifier", type=Path, required=True)
    add.add_argument("--environment", required=True)
    add.add_argument("--note", required=True)
    search = sub.add_parser("search")
    search.add_argument("query")
    search.add_argument("--environment", required=True)
    feedback = sub.add_parser("feedback")
    feedback.add_argument("experience_id")
    feedback.add_argument("--outcome", choices=["success", "failure"], required=True)
    feedback.add_argument("--note", required=True)
    invalidate = sub.add_parser("invalidate")
    invalidate.add_argument("experience_id")
    invalidate.add_argument("--reason", required=True)
    sub.add_parser("expire")
    args = parser.parse_args()
    store = ExperienceStore(args.store)
    if args.command == "add":
        verifier = FileVerifier.from_json(args.verifier)
        result = store.add_verified(args.checkpoint, verifier=verifier,
                                    environment=args.environment, note=args.note)
    elif args.command == "search":
        result = store.search(args.query, environment=args.environment)
    elif args.command == "feedback":
        result = store.feedback(args.experience_id, outcome=args.outcome, note=args.note)
    elif args.command == "invalidate":
        result = store.invalidate(args.experience_id, reason=args.reason)
    else:
        result = {"expired": store.expire()}
    print(json.dumps(result, ensure_ascii=False, indent=2))
if __name__ == "__main__":
    main()
