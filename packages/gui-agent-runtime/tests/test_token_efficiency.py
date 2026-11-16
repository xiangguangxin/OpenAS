"""Deterministic planner token/call accounting and context-size tests."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from openas_gui_agent.planner import ModelPlanner, TokenBudgetExceeded, _compact_observation
from openas_gui_agent.agent import run
from openas_gui_agent.state import create, load

class Response:
    def __init__(self, usage):
        self.payload = {"choices": [{"message": {"content": json.dumps({"type": "pause", "reason": "done"})}}]}
        if usage is not None: self.payload["usage"] = usage
    def __enter__(self): return self
    def __exit__(self, *args): pass
    def read(self): return json.dumps(self.payload).encode()

class Desktop:
    def observe(self): return {"summary": "screen"}

class Tests(unittest.TestCase):
    def test_compact_observation(self):
        observation = {"summary": "ok", "secret": "NEVER_SEND",
                       "tools": [{"name": "click", "description": "x"*500,
                                  "inputSchema": {"type": "object"}, "noise": "NEVER_SEND"}]}
        compact = _compact_observation(observation)
        self.assertNotIn("NEVER_SEND", json.dumps(compact))
        self.assertEqual(compact["tools"][0]["name"], "click")
        self.assertEqual(compact["tools"][0]["inputSchema"]["type"], "object")

    def test_usage_and_multimodal_cap(self):
        planner = ModelPlanner("fake", "key", "https://invalid", max_images=1, max_text_chars=10)
        planner.last_tool_content = [
            {"type": "image", "data": "abc", "mimeType": "image/png"},
            {"type": "image", "data": "def", "mimeType": "image/png"},
            {"type": "text", "text": "x"*500}]
        captured = []
        def mock_open(req, timeout):
            captured.append(json.loads(req.data))
            return Response({"prompt_tokens": 120, "completion_tokens": 10})
        with patch("openas_gui_agent.planner.urllib.request.urlopen", side_effect=mock_open):
            planner.decide({"goal": "test", "criteria": ["done"], "steps": 0, "max_steps": 5}, {"summary": "ok"})
        self.assertEqual(planner.usage["input_tokens"], 120)
        self.assertEqual(planner.usage["output_tokens"], 10)
        parts = captured[0]["messages"][-1]["content"]
        self.assertEqual(sum(x["type"] == "image_url" for x in parts), 1)
        self.assertEqual(len(next(x["text"] for x in parts if x["type"] == "text")), 10)

    def test_budget_pause_and_persist(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/"goal.json"
            create(p, "test", ["done"])
            planner = ModelPlanner("fake", "key", "https://invalid", max_calls=1)
            with patch("openas_gui_agent.planner.urllib.request.urlopen", return_value=Response({"prompt_tokens": 40, "completion_tokens": 10})):
                result = run(p, Desktop(), planner)
            self.assertEqual(result["status"], "paused")
            self.assertEqual(load(p)["model_usage"]["calls"], 1)
            self.assertEqual(load(p)["model_usage"]["input_tokens"], 40)

    def test_budget_is_checked_before_request(self):
        planner = ModelPlanner("fake", "key", "https://invalid", max_calls=1)
        with self.assertRaises(TokenBudgetExceeded):
            planner.decide({"goal": "test", "criteria": [], "steps": 0, "max_steps": 5,
                            "model_usage": {"calls": 1}}, {"summary": "ok"})

    def test_missing_usage_estimated_not_claimed_actual(self):
        planner = ModelPlanner("fake", "key", "https://invalid")
        with patch("openas_gui_agent.planner.urllib.request.urlopen", return_value=Response(None)):
            planner.decide({"goal": "test", "criteria": [], "steps": 0, "max_steps": 5}, {"summary": "ok"})
        self.assertEqual(planner.usage["input_tokens"], 0)
        self.assertGreater(planner.usage["estimated_input_tokens"], 0)
        self.assertEqual(planner.usage["usage_missing_calls"], 1)

if __name__ == "__main__": unittest.main()
