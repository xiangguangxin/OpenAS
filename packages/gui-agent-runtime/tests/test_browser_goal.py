"""Real Chromium, local coverage fixture and a scripted model endpoint."""
from functools import partial
from http.server import BaseHTTPRequestHandler, SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from threading import Thread
import unittest

from openas_gui_agent.adapters.browser import open_browser

EXAMPLES = Path(__file__).resolve().parents[1] / "examples"


def action(tool, **arguments):
    return {"type": "act", "action": {"name": tool, "arguments": arguments, "impact": "low"}}


def server(handler):
    instance = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = Thread(target=instance.serve_forever, daemon=True)
    thread.start()
    return instance, f"http://127.0.0.1:{instance.server_port}"


class QuietStaticServer(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass


class PlannerAPI(BaseHTTPRequestHandler):
    requests = []

    def log_message(self, *_):
        pass

    def do_POST(self):
        request = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        observation = json.loads(request["messages"][1]["content"])
        self.requests.append(request)
        step = observation["step"]
        decisions = (
            action("browser_click", role="button", name="Build instrumented fixture"),
            action("browser_click", role="button", name="Run SIL cases"),
            action("browser_wait_for_text", text="SIL cases passed"),
            action("browser_download", role="link", name="Download MC/DC report", filename="coverage.json"),
            {"type": "complete"},
        )
        result = {"choices": [{"message": {"content": json.dumps(decisions[step])}}],
                  "usage": {"prompt_tokens": 20, "completion_tokens": 5}}
        payload = json.dumps(result).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


@unittest.skipUnless(os.getenv("OPENAS_TEST_BROWSER") == "1", "opt-in test requires Chromium and Playwright")
class BrowserGoals(unittest.TestCase):
    def setUp(self):
        self.executable = os.getenv("OPENAS_TEST_BROWSER_EXECUTABLE") or shutil.which("chromium")
        static, self.site = server(partial(QuietStaticServer, directory=EXAMPLES / "coverage-web"))
        self.addCleanup(static.server_close)
        self.addCleanup(static.shutdown)
        PlannerAPI.requests = []
        api, self.endpoint = server(PlannerAPI)
        self.addCleanup(api.server_close)
        self.addCleanup(api.shutdown)
        self.env = dict(os.environ, OPENAS_GUI_API_KEY="local-fixture-key", OPENAS_GUI_MODEL="scripted-fixture")

    def command(self, module, *args):
        result = subprocess.run([sys.executable, "-m", f"openas_gui_agent.{module}", *map(str, args)],
                                env=self.env, capture_output=True, text=True, timeout=45)
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
        return json.loads(result.stdout)

    def test_browser_runtime_and_independent_verifier(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            checkpoint = root / "goal.json"
            config = root / "rules.json"
            case = json.loads((EXAMPLES / "live-coverage-suite.json").read_text())["scenarios"][0]
            criterion = next(iter(case["rules"]))
            config.write_text(json.dumps({"criteria": case["rules"]}), encoding="utf-8")
            self.command("cli", "create", checkpoint, "--goal", case["goal"], "--criterion", criterion)
            options = ["--browser-executable", self.executable] if self.executable else []
            state = self.command("cli", "run", checkpoint, "--browser-url", self.site, "--download-dir", root,
                                 "--endpoint", self.endpoint, "--verifier", config, "--trace-tools", *options)
            self.assertEqual(state["status"], "completed")
            self.assertEqual(state["steps"], 4)
            self.assertEqual([event["tool"] for event in state["tool_trace"]["events"]],
                             ["browser_click", "browser_click", "browser_wait_for_text", "browser_download"])
            self.assertEqual(state["model_usage"]["input_tokens"], 100)
            self.assertEqual(state["artifact_verification"]["checks"][criterion]["status"], "passed")
            self.assertTrue(self.command("cli", "verify", checkpoint, "--verifier", config)["passed"])

    def test_live_benchmark_browser_experience_pair(self):
        with tempfile.TemporaryDirectory() as temp:
            memory = Path(temp) / "memory.json"
            env = "fixture-linux-chromium"
            from openas_gui_agent.experience import ExperienceStore
            from openas_gui_agent.state import create, persist
            from openas_gui_agent.verification import FileVerifier
            checkpoint = Path(temp) / "verified.json"
            state = create(checkpoint, "Build the instrumented SIL fixture and save the MC/DC report", ["report"])
            state["status"] = "completed"
            persist(checkpoint, state)
            verifier = FileVerifier({"report": {"path": "fixture.json"}}, Path(temp))
            (Path(temp) / "fixture.json").write_text("{}", encoding="utf-8")
            ExperienceStore(memory).add_verified(checkpoint, verifier=verifier, environment=env,
                                                 note="Wait for the fixture to finish.")
            options = ["--browser-executable", self.executable] if self.executable else []
            suite = json.loads((EXAMPLES / "live-coverage-suite.json").read_text())
            suite["scenarios"][0]["expected_trajectory"] = {
                "match": "in_order", "tools": ["browser_click", "browser_click", "browser_download"],
                "max_counts": {"browser_download": 1},
            }
            suite_path = Path(temp) / "browser-suite.json"
            suite_path.write_text(json.dumps(suite), encoding="utf-8")
            report = self.command("benchmark", suite_path,
                                  "--browser-url", self.site, "--endpoint", self.endpoint,
                                  "--experience-store", memory, "--experience-environment", env, *options)
            self.assertEqual(report["kind"], "live-browser")
            self.assertEqual(report["success_rate"], 1)
            self.assertEqual(report["trajectory_pass_rate"], 1)
            self.assertTrue(report["provenance"]["playwright_version"])
            self.assertTrue(all(record["backend_version"] for record in report["records"]))
            self.assertEqual(report["variants"]["experience"]["avg_tokens"], 125)
            self.assertEqual(report["variants"]["baseline"]["experience_hint_calls"], 0)
            self.assertEqual(report["variants"]["experience"]["experience_hint_calls"], 5)
            self.assertEqual([record["variant"] for record in report["records"]], ["baseline", "experience"])
            self.assertFalse(any("untrusted_prior_experience_hints" in msg["content"]
                                 for msg in PlannerAPI.requests[0]["messages"]))
            self.assertTrue(any("untrusted_prior_experience_hints" in msg["content"]
                                for msg in PlannerAPI.requests[5]["messages"]))

    def test_browser_refuses_other_origin_and_existing_download(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "coverage.json").write_bytes(b"keep")
            with open_browser(self.site, root, self.executable) as browser:
                self.assertIn("Build instrumented fixture", browser.observe()["ui_tree"])
                navigation = action("browser_navigate", url="https://example.invalid/")["action"]
                self.assertFalse(browser.act(navigation)["ok"])
                for filename in ("../elsewhere.json", "coverage.json"):
                    download = action("browser_download", role="link", name="unavailable", filename=filename)
                    self.assertFalse(browser.act(download["action"])["ok"])
            self.assertEqual((root / "coverage.json").read_bytes(), b"keep")
