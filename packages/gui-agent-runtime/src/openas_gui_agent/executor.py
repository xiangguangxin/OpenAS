"""Live desktop adapter; transient MCP evidence is not checkpointed."""
from .adapters.nova import NovaMCP
from .planner import ModelPlanner
class LiveDesktop:
    def __init__(self, nova: NovaMCP, planner: ModelPlanner):
        self.nova, self.planner = nova, planner

    def observe(self):
        return self.nova.observe()

    def act(self, action):
        result = self.nova.act(action)
        # Feed recent tool evidence back to the planner, never to disk.
        self.planner.last_tool_content = result.pop("content", [])[:8]
        return result


