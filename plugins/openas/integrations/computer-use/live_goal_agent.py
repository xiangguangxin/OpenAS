"""Legacy OpenAS live GUI wrapper for standalone Praxis."""
import sys
try:
    from praxis_agent.cli import main
    from praxis_agent.adapters.nova import NovaMCP
    from praxis_agent.planner import ModelPlanner
    from praxis_agent.executor import LiveDesktop
except ModuleNotFoundError as exc:
    if (exc.name or "").startswith("praxis_agent"):
        raise RuntimeError("Install Praxis first: pip install git+https://github.com/xiangguangxin/Praxis.git") from exc
    raise

if __name__ == "__main__":
    sys.argv.insert(1, "run")
    main()
