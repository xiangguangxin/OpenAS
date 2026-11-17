"""Legacy OpenAS wrapper. Install Praxis: pip install git+https://github.com/xiangguangxin/Praxis.git"""
try:
    from praxis_agent.state import create, load, _save, persist as _persist, _record
    from praxis_agent.agent import run
    from praxis_agent.cli import main
    from praxis_agent.adapters.base import Desktop, Planner
except ModuleNotFoundError as exc:
    if (exc.name or "").startswith("praxis_agent"):
        raise RuntimeError("Install Praxis first: pip install git+https://github.com/xiangguangxin/Praxis.git") from exc
    raise

if __name__ == "__main__":
    main()
