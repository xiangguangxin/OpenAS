"""Customer MCP configuration must preserve existing data and never disclose secrets."""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'plugins/openas/integrations/setup_mcp.py'
spec = importlib.util.spec_from_file_location('setup_mcp', SCRIPT)
mcp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mcp)


class MCPSetupTests(unittest.TestCase):
    def test_merge_preserves_existing_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = root / '.mcp.json'
            existing = {'extra': True, 'mcpServers': {'custom': {'command': 'custom'}}}
            config.write_text(json.dumps(existing))
            with contextlib.redirect_stdout(io.StringIO()):
                mcp.configure(root, mcp.SERVICES)
                first = config.read_bytes()
                mcp.configure(root, mcp.SERVICES)
            self.assertEqual(config.read_bytes(), first)
            data = json.loads(first)
            self.assertTrue(data['extra'])
            self.assertEqual(data['mcpServers']['custom'], existing['mcpServers']['custom'])
            self.assertIn('${OPENAS_GITHUB_TOKEN}', first.decode())

    def test_conflict_is_atomic_and_redacted(self):
        with tempfile.TemporaryDirectory() as tmp:
            config = Path(tmp) / '.mcp.json'
            original = '{"mcpServers":{"github":{"token":"PRIVATE_VALUE"}}}'
            config.write_text(original)
            output = io.StringIO()
            with contextlib.redirect_stderr(output):
                code = mcp.main(['configure', '--project', tmp, '--services', 'all'])
            self.assertEqual(code, 2)
            self.assertEqual(config.read_text(), original)
            self.assertNotIn('PRIVATE_VALUE', output.getvalue())

    def test_malformed_config_is_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            config = Path(tmp) / '.mcp.json'
            config.write_text('{SECRET invalid')
            with self.assertRaises(ValueError):
                mcp.configure(Path(tmp), mcp.SERVICES)
            self.assertEqual(config.read_text(), '{SECRET invalid')

    def test_check_detects_missing_prerequisites_without_disclosing_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with contextlib.redirect_stdout(io.StringIO()):
                mcp.configure(root, ('github', 'context7'))
            output = io.StringIO()
            with patch.dict(os.environ, {'OPENAS_GITHUB_TOKEN': 'SECRET_TOKEN'}, clear=True), \
                    patch.object(mcp.shutil, 'which', return_value=None), \
                    contextlib.redirect_stdout(output):
                code = mcp.check(root, ('github', 'context7'))
            self.assertEqual(code, 1)
            self.assertIn('FAIL context7 OPENAS_CONTEXT7_API_KEY', output.getvalue())
            self.assertIn('PASS github OPENAS_GITHUB_TOKEN', output.getvalue())
            self.assertNotIn('SECRET_TOKEN', output.getvalue())

    def test_local_pass_still_requires_live_acceptance(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                mcp.configure(root, ('context7',))
                with patch.dict(os.environ, {'OPENAS_CONTEXT7_API_KEY': 'SECRET_KEY'}), \
                        patch.object(mcp.shutil, 'which', return_value='/fake/claude'):
                    self.assertEqual(mcp.check(root, ('context7',)), 0)
            self.assertIn('MANUAL context7', output.getvalue())
            self.assertNotIn('SECRET_KEY', output.getvalue())

    def test_playwright_node_version_and_timeout(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with contextlib.redirect_stdout(io.StringIO()):
                mcp.configure(root, ('playwright',))
            for version, expected in [('v16.20.0\n', 1), ('v22.0.0\n', 0)]:
                with patch.object(mcp.shutil, 'which', return_value='/fake/command'), \
                        patch.object(mcp.subprocess, 'run', return_value=SimpleNamespace(returncode=0, stdout=version)), \
                        contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(mcp.check(root, ('playwright',)), expected)
            with patch.object(mcp.shutil, 'which', return_value='/fake/command'), \
                    patch.object(mcp.subprocess, 'run', side_effect=mcp.subprocess.TimeoutExpired('node', 5)), \
                    contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(mcp.check(root, ('playwright',)), 1)

    def test_symbolic_link_is_not_modified(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / 'original.json'
            target.write_text('{}')
            (root / '.mcp.json').symlink_to(target)
            with self.assertRaises(ValueError):
                mcp.configure(root, ('github',))
            self.assertEqual(target.read_text(), '{}')


if __name__ == '__main__':
    unittest.main()
