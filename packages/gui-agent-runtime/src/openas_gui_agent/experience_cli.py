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
    args = parser.parse_args()
    store = ExperienceStore(args.store)
    if args.command == "add":
        verifier = FileVerifier.from_json(args.verifier)
        result = store.add_verified(args.checkpoint, verifier=verifier,
                                    environment=args.environment, note=args.note)
    else:
        result = store.search(args.query, environment=args.environment)
    print(json.dumps(result, ensure_ascii=False, indent=2))
if __name__ == "__main__":
    main()
