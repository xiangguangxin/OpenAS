"""Nova stdio MCP transport."""
from __future__ import annotations
import json, queue, subprocess, threading
from typing import Any
class NovaMCP:
    def __init__(self, executable: str):
        self.process = subprocess.Popen([executable], stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        self.responses: queue.Queue[dict[str, Any]] = queue.Queue()
        self.next_id = 0
        self._reader = threading.Thread(target=self._read, daemon=True)
        self._reader.start()
        initialization = self._rpc("initialize", {"protocolVersion": "2025-03-26",
                                 "capabilities": {}, "clientInfo": {"name": "openas-goal-runtime", "version": "0.1"}})
        server = initialization.get("serverInfo") if isinstance(initialization, dict) else None
        version = server.get("version") if isinstance(server, dict) else None
        self.backend_version = version[:128] if isinstance(version, str) else None
        self._notify("notifications/initialized", {})
        self.tools = self._rpc("tools/list", {}).get("tools", [])
        self.names = {tool["name"] for tool in self.tools}

    def _read(self):
        assert self.process.stdout is not None
        for line in self.process.stdout:
            try:
                self.responses.put(json.loads(line))
            except (ValueError, UnicodeDecodeError):
                continue

    def _notify(self, method, params):
        assert self.process.stdin is not None
        self.process.stdin.write((json.dumps({"jsonrpc": "2.0", "method": method,
                                              "params": params}) + "\n").encode())
        self.process.stdin.flush()

    def _rpc(self, method, params):
        self.next_id += 1
        ident = self.next_id
        assert self.process.stdin is not None
        self.process.stdin.write((json.dumps({"jsonrpc": "2.0", "id": ident,
                                              "method": method, "params": params}) + "\n").encode())
        self.process.stdin.flush()
        while True:
            try:
                response = self.responses.get(timeout=30)
            except queue.Empty as exc:
                raise TimeoutError(f"MCP timeout: {method}") from exc
            if response.get("id") != ident:
                continue
            if "error" in response:
                raise RuntimeError(str(response["error"]))
            return response.get("result", {})

    def call(self, name, arguments):
        if name not in self.names:
            raise ValueError(f"Unknown MCP tool: {name}")
        return self._rpc("tools/call", {"name": name, "arguments": arguments})

    def observe(self):
        # Discover rather than guess Nova's tool names and schemas.
        # The planner chooses an observation tool from actual advertised tools.
        return {"summary": "Tools available; choose a read-only observation action first",
                "tools": self.tools}

    def act(self, action):
        result = self.call(action["name"], action.get("arguments", {}))
        return {"ok": not result.get("isError", False),
                "summary": "MCP call completed" if not result.get("isError") else "MCP tool error",
                "content": result.get("content", [])}

    def close(self):
        self.process.terminate()
        try:
            self.process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            self.process.kill()


