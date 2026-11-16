"""CLI: create/status/run/resume."""
import argparse, json, os
from pathlib import Path
from .state import create, load
from .agent import run

def main():
    p = argparse.ArgumentParser(description="OpenAS GUI Agent")
    sub = p.add_subparsers(dest="command", required=True)
    c = sub.add_parser("create"); c.add_argument("checkpoint", type=Path); c.add_argument("--goal", required=True); c.add_argument("--criterion", action="append", required=True); c.add_argument("--max-steps", type=int, default=40)
    s = sub.add_parser("status"); s.add_argument("checkpoint", type=Path)
    r = sub.add_parser("reconcile"); r.add_argument("checkpoint", type=Path); r.add_argument("--outcome", choices=["executed", "not-executed"], required=True); r.add_argument("--note", required=True)
    for name in ("run", "resume"):
        x = sub.add_parser(name); x.add_argument("checkpoint", type=Path); x.add_argument("--nova", required=True); x.add_argument("--model", default=os.getenv("OPENAS_GUI_MODEL")); x.add_argument("--endpoint", default=os.getenv("OPENAS_GUI_API_URL", "https://api.openai.com/v1/chat/completions")); x.add_argument("--approve-pending", action="store_true"); x.add_argument("--verifier", type=Path, help="JSON rules for independent local file verification"); x.add_argument("--max-model-calls", type=int, default=0); x.add_argument("--max-model-tokens", type=int, default=0); x.add_argument("--max-ui-text-chars", type=int, default=5000); x.add_argument("--max-images", type=int, default=1); x.add_argument("--experience-store", type=Path); x.add_argument("--experience-environment", default="")
    a = p.parse_args()
    if a.command == "create": result = create(a.checkpoint, a.goal, a.criterion, max_steps=a.max_steps)
    elif a.command == "status": result = load(a.checkpoint)
    elif a.command == "reconcile":
        from .recovery import reconcile
        result = reconcile(a.checkpoint, outcome=a.outcome, note=a.note)
    else:
        from .adapters.nova import NovaMCP
        from .planner import ModelPlanner
        from .executor import LiveDesktop
        key = os.getenv("OPENAS_GUI_API_KEY")
        if not key or not a.model: p.error("Set OPENAS_GUI_API_KEY and OPENAS_GUI_MODEL (or --model)")
        if a.max_model_calls < 0 or a.max_model_tokens < 0 or a.max_ui_text_chars < 0 or a.max_images < 0: p.error("Token limits must be nonnegative")
        if bool(a.experience_store) != bool(a.experience_environment): p.error("--experience-store and --experience-environment must be used together")
        from .experience import ExperienceStore
        experience_store = ExperienceStore(a.experience_store) if a.experience_store else None
        nova = NovaMCP(a.nova)
        try:
            planner = ModelPlanner(a.model, key, a.endpoint, max_tokens=a.max_model_tokens, max_calls=a.max_model_calls, max_text_chars=a.max_ui_text_chars, max_images=a.max_images, experience_store=experience_store, experience_environment=a.experience_environment)
            from .verification import FileVerifier
            verifier = FileVerifier.from_json(a.verifier) if a.verifier else None
            result = run(a.checkpoint, LiveDesktop(nova, planner), planner, approval=a.approve_pending, verifier=verifier)
        finally: nova.close()
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__": main()
