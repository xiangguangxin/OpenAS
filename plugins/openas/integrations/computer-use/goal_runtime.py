"""Compatibility wrapper. Install: pip install -e packages/gui-agent-runtime."""
from openas_gui_agent.state import create, load, _save, persist as _persist, _record
from openas_gui_agent.agent import run
from openas_gui_agent.cli import main
from openas_gui_agent.adapters.base import Desktop, Planner

if __name__ == "__main__":
    main()
