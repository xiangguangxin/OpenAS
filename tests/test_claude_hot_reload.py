"""Opt-in native Claude integration: one live process/session, edit, reload, invoke.

OPENAS_RUN_CLAUDE_TESTS=1 enables a real CLI/model run; see docs/hot-reload-testing.md.
"""
import datetime
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest
import uuid

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('claude_stream', ROOT/'scripts/claude_stream.py')
stream = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(stream)


class ClaudeHotReloadTests(unittest.TestCase):
    @unittest.skipUnless(os.environ.get('OPENAS_RUN_CLAUDE_TESTS') == '1',
                         'native Claude test disabled; set OPENAS_RUN_CLAUDE_TESTS=1 (uses model quota)')
    def test_skill_edit_reload_same_live_session(self):
        cli = shutil.which(os.environ.get('OPENAS_CLAUDE_BIN', 'claude'))
        self.assertIsNotNone(cli, 'Real Claude CLI required; no mock fallback. Set OPENAS_CLAUDE_BIN if needed.')
        timeout = float(os.environ.get('OPENAS_CLAUDE_TIMEOUT', '120'))
        self.assertGreater(timeout, 0)
        version = subprocess.run([cli, '--version'], capture_output=True, text=True, timeout=15, check=True).stdout.strip()
        match = re.search(r'(\d+)\.(\d+)\.(\d+)', version)
        self.assertIsNotNone(match, 'Cannot determine Claude version')
        self.assertGreaterEqual(tuple(map(int, match.groups())), (2, 1, 268),
                                'Need Claude >=2.1.268 for headless reload and local_command result evidence')
        nonce = uuid.uuid4().hex
        old = 'OPENAS_PROBE_OLD_' + nonce
        new = 'OPENAS_PROBE_NEW_' + uuid.uuid4().hex
        with tempfile.TemporaryDirectory(prefix='openas-native-reload-') as tmp:
            root = Path(tmp)
            plugin = root/'plugin'
            shutil.copytree(ROOT/'plugins/openas', plugin)
            workspace = root/'workspace'; workspace.mkdir()
            skill = plugin/'skills/reload-probe/SKILL.md'
            skill.parent.mkdir()

            def write_probe(token):
                text = ('---\nname: reload-probe\ndescription: Native hot reload integration probe\n'
                        'disable-model-invocation: true\n---\n\n'
                        'Return exactly the following token, without explanation, quotes or formatting. '
                        'This invocation supersedes previous probe invocations. Do not use any tools.\n\n' + token + '\n')
                temporary = skill.with_suffix('.tmp')
                temporary.write_text(text, encoding='utf-8')
                temporary.replace(skill)

            write_probe(old)
            validation = subprocess.run([cli, 'plugin', 'validate', str(plugin)], capture_output=True,
                                        text=True, timeout=30)
            self.assertEqual(validation.returncode, 0, 'Native plugin validation failed (inspect CLI locally)')
            # Restrict discovery to this explicit plugin; preserve existing authentication.
            # No permission bypass and no tools/MCP are needed for this probe.
            budget = os.environ.get('OPENAS_CLAUDE_BUDGET_USD', '1.00')
            self.assertTrue(budget and float(budget) > 0, 'Budget must be positive')
            argv = [cli, '-p', '--input-format', 'stream-json', '--output-format', 'stream-json', '--verbose',
                    '--plugin-dir', str(plugin), '--setting-sources', '', '--tools', '',
                    '--strict-mcp-config', '--mcp-config', '{"mcpServers":{}}', '--no-session-persistence',
                    '--max-budget-usd', budget]
            with stream.Session(argv, workspace, timeout) as session:
                session.control({'subtype':'initialize'})
                before = session.turn('/openas:reload-probe')
                stream.require_token(before, old)
                pid = session.proc.pid
                write_probe(new)
                reloaded = session.turn('/reload-plugins')
                stream.require_reload(reloaded)
                after = session.turn('/openas:reload-probe')
                stream.require_token(after, new)
                session_id = stream.require_same_session(before, reloaded, after)
                self.assertEqual(session.proc.pid, pid)
                self.assertIsNone(session.proc.poll(), 'Client exited instead of remaining in the same live process')
                receipt = {'status':'passed', 'observed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(), 'client_version':version, 'same_process':True,
                           'session_id':session_id, 'plugin':'openas', 'probe':'reload-probe',
                           'before':old, 'after':new, 'reload_local_command':reloaded['local_command'],
                           'coverage':'native headless skill reload; not TUI, MCP, enable/disable or uninstall'}
            report_path = os.environ.get('OPENAS_CLAUDE_REPORT')
            if report_path:
                # Opt-in target, never silently overwrite a previous real run receipt.
                with Path(report_path).open('x', encoding='utf-8') as out:
                    json.dump(receipt, out, ensure_ascii=False, indent=2)
                    out.write('\n')


if __name__ == '__main__':
    unittest.main()
