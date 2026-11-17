import argparse
import os
import unittest
from unittest.mock import patch

from openas_gui_agent.model_connection import add_model_arguments, resolve_model_connection


class ModelConnectionTests(unittest.TestCase):
    def setUp(self):
        self.parser = argparse.ArgumentParser()
        add_model_arguments(self.parser)

    def resolve(self, flags, environ):
        with patch.dict(os.environ, environ, clear=True):
            return resolve_model_connection(self.parser.parse_args(flags))

    def test_direct_endpoint_and_default_keep_the_existing_credential(self):
        env = {"OPENAS_GUI_API_KEY": "fixture-direct", "OPENAS_GUI_MODEL": "provider-model",
               "LITELLM_API_KEY": "fixture-gateway"}
        default = self.resolve([], env)
        self.assertEqual(default.endpoint, "https://api.openai.com/v1/chat/completions")
        self.assertEqual(default.api_key, "fixture-direct")
        self.assertEqual(default.kind, "openai-compatible")
        custom = self.resolve([], dict(env, OPENAS_GUI_API_URL="https://example.test/model"))
        self.assertEqual(custom.endpoint, "https://example.test/model")

    def test_litellm_uses_the_gateway_alias_and_separate_credential(self):
        env = {"OPENAS_GUI_API_KEY": "fixture-direct", "LITELLM_API_KEY": "fixture-gateway",
               "OPENAS_GUI_MODEL": "configured-alias"}
        for base_url in ("https://example.test/gateway", "https://example.test/gateway/v1/"):
            with self.subTest(base_url=base_url):
                gateway = self.resolve(["--litellm-base-url", base_url, "--model", "explicit-alias"], env)
                self.assertEqual(gateway.endpoint, "https://example.test/gateway/v1/chat/completions")
                self.assertEqual(gateway.model, "explicit-alias")
                self.assertEqual(gateway.api_key, "fixture-gateway")
                self.assertEqual(gateway.kind, "litellm")
                self.assertNotIn(gateway.api_key, repr(gateway))
        with self.assertRaisesRegex(ValueError, "Set LITELLM_API_KEY"):
            self.resolve(["--litellm-base-url", "http://127.0.0.1:4000"],
                         {key: val for key, val in env.items() if key != "LITELLM_API_KEY"})

    def test_explicit_route_overrides_environment_routes(self):
        env = {"OPENAS_GUI_API_KEY": "fixture-direct", "LITELLM_API_KEY": "fixture-gateway",
               "OPENAS_GUI_MODEL": "configured-model", "OPENAS_GUI_API_URL": "https://direct.test/path",
               "OPENAS_LITELLM_BASE_URL": "https://proxy.test"}
        with self.assertRaisesRegex(ValueError, "Both model routes are configured"):
            self.resolve([], env)
        self.assertEqual(self.resolve(["--endpoint", "https://alternate.test/chat"], env).kind,
                         "openai-compatible")
        self.assertEqual(self.resolve(["--litellm-base-url", "http://127.0.0.1:4000"], env).kind, "litellm")
        del env["OPENAS_GUI_API_URL"]
        self.assertEqual(self.resolve([], env).endpoint, "https://proxy.test/v1/chat/completions")

    def test_litellm_validates_the_url(self):
        env = {"LITELLM_API_KEY": "fixture-gateway", "OPENAS_GUI_MODEL": "fixture"}
        for invalid in ("", "example.test", "https://name@example.test", "https://example.test:0",
                        "https://example.test:100000", "https://example.test?x=1", "https://exam ple.test",
                        "https://example.test/#anchor", "https://example.test/v1/chat/completions"):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                self.resolve(["--litellm-base-url", invalid], env)
