"""Compatibility wrapper for the optional standalone package."""
import sys
from openas_gui_agent.cli import main
from openas_gui_agent.adapters.nova import NovaMCP
from openas_gui_agent.planner import ModelPlanner
from openas_gui_agent.executor import LiveDesktop

if __name__ == "__main__":
    sys.argv.insert(1, "run")
    main()
