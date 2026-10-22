"""Opt-in native plugin lifecycle in an isolated configuration; does not invoke a model."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ClaudeLifecycleTests(unittest.TestCase):
    @unittest.skipUnless(os.environ.get('OPENAS_RUN_CLAUDE_LIFECYCLE') == '1',
                         'native lifecycle disabled; set OPENAS_RUN_CLAUDE_LIFECYCLE=1')
    def test_local_install_disable_enable_uninstall_preserves_memory(self):
        cli = shutil.which(os.environ.get('OPENAS_CLAUDE_BIN', 'claude'))
        self.assertIsNotNone(cli, 'Real Claude CLI required; no mock fallback')
        with tempfile.TemporaryDirectory(prefix='openas-lifecycle-') as tmp:
            root = Path(tmp); market = root/'market'; workspace = root/'project'
            workspace.mkdir()
            shutil.copytree(ROOT/'.claude-plugin', market/'.claude-plugin')
            shutil.copytree(ROOT/'plugins/openas', market/'plugins/openas')
            memory = workspace/'.openas/memory/records.json'
            memory.parent.mkdir(parents=True)
            memory.write_text('{"sentinel":"consumer memory"}')
            env = dict(os.environ, CLAUDE_CONFIG_DIR=str(root/'config'),
                       CLAUDE_CODE_PLUGIN_CACHE_DIR=str(root/'config/plugins'),
                       CLAUDE_CODE_DEBUG_LOGS_DIR=str(root/'config/debug'))
            commands = []
            def command(*args):
                r = subprocess.run([cli, *args], cwd=workspace, env=env, capture_output=True,
                                   text=True, timeout=90)
                commands.append({'args': list(args), 'exit_code': r.returncode})
                self.assertEqual(r.returncode, 0, 'Native command failed; inspect locally: ' + ' '.join(args[:3]))
                return r.stdout
            def installed():
                entries = json.loads(command('plugin', 'list', '--json'))
                self.assertIsInstance(entries, list)
                return [x for x in entries if x['id'] == 'openas@openas-marketplace' and x['scope'] == 'project']
            command('plugin', 'validate', str(market/'plugins/openas'))
            command('plugin', 'marketplace', 'add', str(market))
            command('plugin', 'install', 'openas@openas-marketplace', '--scope', 'project')
            self.assertTrue(installed()[0]['enabled'])
            command('plugin', 'disable', 'openas@openas-marketplace', '--scope', 'project')
            self.assertFalse(installed()[0]['enabled'])
            command('plugin', 'enable', 'openas@openas-marketplace', '--scope', 'project')
            self.assertTrue(installed()[0]['enabled'])
            command('plugin', 'uninstall', 'openas@openas-marketplace', '--scope', 'project')
            self.assertEqual(installed(), [])
            self.assertEqual(memory.read_text(), '{"sentinel":"consumer memory"}')
            report = os.environ.get('OPENAS_CLAUDE_LIFECYCLE_REPORT')
            if report:
                receipt = {'status': 'passed', 'coverage': 'local native plugin lifecycle; not model invocation or hot reload',
                           'commands': commands, 'consumer_memory_preserved': True,
                           'isolated_configuration': True}
                with Path(report).open('x') as f:
                    json.dump(receipt, f, indent=2)
