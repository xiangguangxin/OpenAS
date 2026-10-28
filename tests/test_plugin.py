import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / 'plugins/openas'


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PluginTests(unittest.TestCase):
    def test_catalog_points_to_self_contained_plugin(self):
        catalog = json.loads((ROOT / '.claude-plugin/marketplace.json').read_text())
        manifest = json.loads((PLUGIN / '.claude-plugin/plugin.json').read_text())
        self.assertEqual(catalog['plugins'][0]['name'], manifest['name'])
        self.assertEqual((ROOT / catalog['plugins'][0]['source']).resolve(), PLUGIN)
        self.assertEqual(manifest['name'], 'openas')

    def test_packaged_resources_validate(self):
        checker = load(ROOT / 'scripts/check_plugin.py', 'plugin_check')
        inventory = checker.check(PLUGIN)
        self.assertTrue({'cto', 'developer', 'it', 'product-manager', 'red-team',
                         'security-reviewer', 'tech-writer', 'verifier'}.issubset(inventory['agents']))
        self.assertGreaterEqual(len(inventory['skills']), 14)
        self.assertIn('bug-fix', inventory['skills'])
        self.assertIn('project-memory', inventory['skills'])

    def test_translations_are_complete_and_plugin_remains_relocatable(self):
        checker = load(ROOT / 'scripts/check_plugin.py', 'plugin_check_translations')
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)/'plugin'
            shutil.copytree(PLUGIN, target)
            inventory = checker.check(target)
            self.assertEqual(len(inventory['skills']), 49)
            self.assertEqual(len(inventory['agents']), 12)
            self.assertEqual(inventory['translations'], 73)

    def test_stale_missing_and_duplicate_translations_are_rejected(self):
        checker = load(ROOT / 'scripts/check_plugin.py', 'plugin_check_translation_failures')
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)/'plugin'
            shutil.copytree(PLUGIN, target)
            registry = target/'references/translations.json'
            original = registry.read_text()
            data = json.loads(original)
            entry = data['entries'][0]
            for field in ('source', 'target'):
                with self.subTest(changed=field):
                    path = target/entry[field]
                    before = path.read_bytes()
                    path.write_bytes(before + b'\nA behavior change needing translation review.\n')
                    with self.assertRaisesRegex(ValueError, 'needs review'):
                        checker.check_translations(target)
                    path.write_bytes(before)
            for kind in ('missing_file', 'missing_pair', 'duplicate', 'escape', 'missing_registry', 'invalid_registry'):
                with self.subTest(kind=kind):
                    edited = json.loads(original)
                    path = target/entry['target']
                    before = path.read_bytes()
                    if kind == 'missing_file':
                        path.unlink()
                    elif kind == 'missing_pair':
                        edited['entries'].pop()
                    elif kind == 'duplicate':
                        edited['entries'].append(edited['entries'][0])
                    elif kind == 'escape':
                        edited['entries'][0]['source'] = '../outside.md'
                    elif kind == 'invalid_registry':
                        edited = []
                    registry.write_text(json.dumps(edited))
                    if kind == 'missing_registry':
                        registry.unlink()
                    with self.assertRaises(ValueError):
                        checker.check_translations(target)
                    path.write_bytes(before)
                    registry.write_text(original)

    def test_validator_rejects_bad_skill_without_modifying_package(self):
        checker = load(ROOT / 'scripts/check_plugin.py', 'plugin_check_bad')
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'plugin'
            shutil.copytree(PLUGIN, target)
            p = target / 'skills/bug-fix/SKILL.md'
            p.write_text('broken')
            with self.assertRaises(ValueError):
                checker.check(target)
            self.assertEqual(p.read_text(), 'broken')

    def test_validator_rejects_escaping_symlink(self):
        checker = load(ROOT / 'scripts/check_plugin.py', 'plugin_check_link')
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'plugin'
            shutil.copytree(PLUGIN, target)
            (target / 'escape').symlink_to('/tmp')
            with self.assertRaises(ValueError):
                checker.check(target)

    def test_moved_memory_cli_requires_project_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'moved-plugin'
            shutil.copytree(PLUGIN, target)
            script = target / 'skills/project-memory/scripts/project_memory.py'
            no_root = subprocess.run([sys.executable, str(script), 'inspect'], cwd=tmp, capture_output=True)
            self.assertNotEqual(no_root.returncode, 0)
            root = Path(tmp) / 'consumer'; root.mkdir()
            result = subprocess.run([sys.executable, str(script), '--root', str(root), 'inspect'], cwd=tmp,
                                    text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout), [])
            self.assertFalse((target / 'memory/records.json').exists())

    def test_memory_is_scoped_to_consumer_and_survives_plugin_removal(self):
        module = load(PLUGIN / 'skills/project-memory/scripts/project_memory.py', 'consumer_memory')
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); a = root/'a'; b = root/'b'; a.mkdir(); b.mkdir()
            (a/'proof.json').write_text('{"value":true}')
            memory = module.Memory(a)
            item = memory.propose('scope', 'fact', 'consumer A fact', ['scope'], [memory.evidence('proof.json', '/value')])
            memory.review(item['id'], 'approve', 'test reviewer', 'fixture only')
            self.assertEqual(memory.directory, a/'.openas/memory')
            self.assertEqual(len(memory.query('scope')), 1)
            self.assertEqual(module.Memory(b).query('scope'), [])
            # No records are shipped inside the plugin or shared between projects.
            self.assertFalse((PLUGIN/'memory/records.json').exists())
            self.assertTrue((a/'.openas/memory/records.json').exists())
            copied_plugin = root/'installed-plugin'
            shutil.copytree(PLUGIN, copied_plugin)
            copied_module = load(copied_plugin/'skills/project-memory/scripts/project_memory.py', 'removed_plugin_memory')
            shutil.rmtree(copied_plugin)
            self.assertEqual(copied_module.Memory(a).query('scope')[0]['id'], item['id'])

    def test_plugin_cache_cannot_be_used_as_memory_target(self):
        module = load(PLUGIN / 'skills/project-memory/scripts/project_memory.py', 'cache_memory')
        with self.assertRaises(ValueError):
            module.Memory(PLUGIN)
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                module.Memory(Path(tmp), directory=PLUGIN/'memory')
            with self.assertRaises(ValueError):
                module.Memory(Path(tmp)/'missing-project')

    def test_moved_harness_resolves_resources_and_consumer_memory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); target = root/'renamed-plugin'; shutil.copytree(PLUGIN, target)
            harness = load(target/'workflows/codex-team.py', 'moved_harness')
            workspace = root/'workspace'; workspace.mkdir()
            consumer = root/'consumer'; consumer.mkdir()
            task = {'requirement':'test', 'scope':['a'], 'acceptance':['test'], 'checks':[[sys.executable,'-c','print(1)']]}
            runner = harness.Runner(task, workspace, root/'run', 'codex', memory_enabled=True, project_root=consumer)
            self.assertEqual(runner.memory.root, consumer)
            self.assertTrue((consumer/'.openas/memory/current-task.json').exists())
            self.assertFalse((target/'memory/current-task.json').exists())
            self.assertEqual({p.name for p in (harness.ROOT/'agents').glob('*.md')},
                             {p.name for p in (PLUGIN/'agents').glob('*.md')})
            # Relocated resources and consumer-specific constraints reach the actual client handoff.
            task['constraints'] = ['Keep the existing public API and use the consumer test command']
            captured = []
            def fake_execute(argv, cwd, timeout, stdout, stderr, stdin=None):
                captured.append(stdin)
                Path(argv[argv.index('-o') + 1]).write_text(json.dumps({
                    'verdict': 'complete', 'summary': 'test handoff', 'findings': [],
                    'evidence': ['mock client only'],
                }))
                return 0
            with patch.object(harness, 'execute', side_effect=fake_execute):
                runner.call('cto', 'design', 'Read the consumer project', {'complete'})
            self.assertIn((target/'references/project-context.md').read_text(), captured[0])
            self.assertIn(task['constraints'][0], captured[0])

    def test_generic_example_has_failing_baseline_and_repairable_contract(self):
        harness = load(PLUGIN/'workflows/codex-team.py', 'pagination_harness')
        examples = PLUGIN/'workflows/examples'
        task = json.loads((examples/'pagination-task.json').read_text())
        task['checks'][0][0] = sys.executable
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace = root/'standalone-tool'
            shutil.copytree(examples/'pagination-fixture', workspace)
            original_tests = (workspace/'test_pagination.py').read_bytes()
            runner = harness.Runner(task, workspace, root/'run', 'unused-client')
            baseline = runner.checks('baseline')
            self.assertNotEqual(baseline[0]['exit_code'], 0)
            self.assertIn('FAIL', baseline[0]['stderr'])
            # Reference repair validates the exercise contract without a model call.
            (workspace/'pagination.py').write_text(
                'def paginate(items, page, page_size):\n'
                '    for value in (page, page_size):\n'
                '        if type(value) is not int or value <= 0:\n'
                '            raise ValueError("expected a positive integer")\n'
                '    start = (page - 1) * page_size\n'
                '    return items[start:start + page_size]\n'
            )
            (workspace/'DESIGN.md').write_text('One-based pages use (page - 1) * page_size; validate positive integers first.\n')
            repaired = runner.checks('repaired')
            self.assertEqual(repaired[0]['exit_code'], 0, repaired[0]['stderr'])
            runner.check_scope()
            self.assertEqual((workspace/'test_pagination.py').read_bytes(), original_tests)
            self.assertEqual(set(p.name for p in workspace.iterdir()),
                             {'pagination.py', 'test_pagination.py', 'DESIGN.md'})

    def test_no_plugin_resource_paths_point_to_host_claude_folder(self):
        for folder in ['skills', 'agents', 'references']:
            for path in (PLUGIN/folder).rglob('*.md'):
                if 'reverse-engineer-anything' in path.parts:
                    continue  # Vendored upstream examples may discuss client configuration.
                text = path.read_text()
                for old in ['.claude/skills/', '.claude/agents/', '.claude/references/', '.claude/workflows/']:
                    self.assertNotIn(old, text, str(path))


if __name__ == '__main__':
    unittest.main()
