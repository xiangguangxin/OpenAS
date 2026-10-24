"""Exercise imports against local Git objects; never download or execute third-party code."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT/'plugins/openas/skills/github-skill-discovery/scripts/import_skill.py'
SPEC = importlib.util.spec_from_file_location('skill_import', SCRIPT)
helper = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(helper)


@unittest.skipUnless(shutil.which('git'), 'Git required for pinned-source import tests')
class SkillImportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root/'repo'; self.repo.mkdir()
        self.git('init', '-q')
        self.git('config', 'user.name', 'Fixture Author')
        self.git('config', 'user.email', 'fixture@example.invalid')
        self.git('config', 'core.autocrlf', 'false')
        self.git('remote', 'add', 'origin', 'https://github.com/fixture/skills.git')
        self.source = self.repo/'skills'/'fixture-skill'; self.source.mkdir(parents=True)
        (self.source/'SKILL.md').write_text('---\nname: fixture-skill\ndescription: Diagnose the fixture contract.\n---\n\nRead the local contract.\n')
        (self.source/'scripts').mkdir()
        (self.source/'scripts'/'check.py').write_text('raise RuntimeError("This script must not be executed during import")\n')
        (self.repo/'LICENSE').write_text('Synthetic test license text, not an actual redistribution grant.\n')
        self.git('add', '.')
        self.git('commit', '-qm', 'Fixture')
        self.commit = self.git('rev-parse', 'HEAD').strip()
        self.candidate = self.root/'candidate'
        self.destination = self.root/'consumer'/'.claude'/'skills'/'fixture-skill'

    def git(self, *args):
        return subprocess.run(['git', '-C', str(self.repo), *args], check=True, capture_output=True, text=True).stdout

    def stage(self, **kwargs):
        values = dict(checkout=self.repo, repository='fixture/skills', commit=self.commit,
                      skill_path='skills/fixture-skill', legal=['LICENSE'], output=self.candidate)
        values.update(kwargs)
        return helper.stage(**values)

    def report(self):
        current = helper.inspect(self.candidate)
        return {key: current[key] for key in ('repository', 'commit', 'skill_path', 'package_sha256')} | {
            'decision': 'accept', 'reviewer': 'fixture-reviewer', 'mode': 'copy', 'changes': [],
            'checks': {key: True for key in ('content', 'dependencies', 'license', 'fit')},
            'license': {'expression': 'Synthetic-fixture-only', 'usage': 'local test', 'notes': 'Not a legal determination'},
            'dependencies': [],
            'validation': [{'kind': kind, 'status': 'passed', 'evidence': ['Synthetic fixture evidence, not a real host run']}
                           for kind in ('structure', 'behavior')]}

    def install(self):
        self.stage()
        return helper.install(self.candidate, self.report(), self.destination)

    def test_pinned_objects_ignore_dirty_worktree_and_never_execute_scripts(self):
        original = (self.source/'SKILL.md').read_bytes()
        (self.source/'SKILL.md').write_text('Uncommitted tampered content')
        (self.source/'untracked').write_text('Not part of the commit')
        result = self.stage()
        self.assertEqual((self.candidate/'SKILL.md').read_bytes(), original)
        self.assertFalse((self.candidate/'untracked').exists())
        self.assertEqual(result['commit'], self.commit)
        self.assertTrue((self.candidate/'scripts/check.py').exists())

    def test_root_skill_and_quoted_name(self):
        self.git('mv', 'skills/fixture-skill/SKILL.md', 'SKILL.md')
        path = self.repo/'SKILL.md'
        path.write_text(path.read_text().replace('name: fixture-skill', 'name: "fixture-skill"'))
        self.git('add', '.')
        self.git('commit', '-qm', 'Root skill')
        commit = self.git('rev-parse', 'HEAD').strip()
        self.stage(commit=commit, skill_path='.')
        self.assertEqual(helper.inspect(self.candidate)['name'], 'fixture-skill')

    def test_license_preserved_and_origin_recorded(self):
        self.stage()
        stored = self.candidate/'_openas_origin/legal/LICENSE'
        self.assertEqual(stored.read_bytes(), (self.repo/'LICENSE').read_bytes())
        record = helper.metadata(self.candidate)
        self.assertEqual(record['repository'], 'fixture/skills')
        self.assertEqual(record['skill_path'], 'skills/fixture-skill')
        stored.write_text('Changed license')
        with self.assertRaises(ValueError):
            helper.inspect(self.candidate)

    def test_unpinned_or_mismatched_source_is_rejected_before_writing(self):
        for values in ({'commit': 'HEAD'}, {'repository': 'other/skills'}, {'legal': ['MISSING']}, {'skill_path': '../outside'}):
            with self.subTest(values=values), self.assertRaises(ValueError):
                self.stage(**values)
            self.assertFalse(self.candidate.exists())

    def test_symlink_source_is_not_imported(self):
        (self.source/'linked').symlink_to('/etc/passwd')
        self.git('add', '.')
        self.git('commit', '-qm', 'Symlink fixture')
        with self.assertRaises(ValueError):
            self.stage(commit=self.git('rev-parse', 'HEAD').strip())
        self.assertFalse(self.candidate.exists())

    def test_gitlink_is_rejected_without_fetching_submodule(self):
        self.git('update-index', '--add', '--cacheinfo', f'160000,{self.commit},skills/fixture-skill/linked-module')
        self.git('commit', '-qm', 'Gitlink fixture')
        with self.assertRaises(ValueError):
            self.stage(commit=self.git('rev-parse', 'HEAD').strip())
        self.assertFalse(self.candidate.exists())

    def test_install_requires_current_review_and_actual_validation_categories(self):
        self.stage()
        base = self.report()
        reports = []
        for field, value in [('package_sha256', 'old'), ('decision', 'reject'), ('commit', '0'*40), ('skill_path', 'wrong/path')]:
            reports.append({**base, field: value})
        reports.append({**base, 'checks': {**base['checks'], 'license': False}})
        reports.append({**base, 'dependencies': [{'name': 'tool', 'version': '1', 'status': 'missing'}]})
        reports.append({**base, 'validation': [{'kind': 'structure', 'status': 'passed', 'evidence': ['Only static inspection']}]})
        for report in reports:
            with self.subTest(report=report), self.assertRaises(ValueError):
                helper.install(self.candidate, report, self.destination)
            self.assertFalse(self.destination.exists())

    def test_install_is_new_only_and_not_native_validation(self):
        result = self.install()
        self.assertEqual(result['state'], 'installed_unverified')
        self.assertTrue(helper.verify(self.destination)['unchanged'])
        record = (self.destination/helper.RECORD).read_bytes()
        with self.assertRaises(ValueError):
            helper.install(self.candidate, self.report(), self.destination)
        self.assertEqual((self.destination/helper.RECORD).read_bytes(), record)

    def test_existing_empty_directory_is_preserved(self):
        self.stage()
        self.destination.mkdir(parents=True)
        with self.assertRaises(ValueError):
            helper.install(self.candidate, self.report(), self.destination)
        self.assertEqual(list(self.destination.iterdir()), [])

    def test_adaptation_requires_updated_review_and_change_description(self):
        self.stage()
        report = self.report()
        with (self.candidate/'SKILL.md').open('a') as stream:
            stream.write('Use the consumer project contract.\n')
        with self.assertRaises(ValueError):
            helper.install(self.candidate, report, self.destination)
        report = self.report()
        with self.assertRaises(ValueError):
            helper.install(self.candidate, report, self.destination)
        report.update(mode='adapted', changes=['Use local project contract'])
        helper.install(self.candidate, report, self.destination)
        self.assertEqual(helper.metadata(self.destination)['review']['changes'], report['changes'])
        self.assertTrue(helper.verify(self.destination)['unchanged'])

    def test_renamed_adaptation_retains_both_upstream_and_installed_names(self):
        self.stage()
        path = self.candidate/'SKILL.md'
        path.write_text(path.read_text().replace('name: fixture-skill', 'name: adapted-fixture'))
        report = self.report()
        report.update(mode='adapted', changes=['Rename for the destination client'])
        destination = self.destination.parent/'adapted-fixture'
        helper.install(self.candidate, report, destination)
        record = helper.metadata(destination)
        self.assertEqual(record['name'], 'fixture-skill')
        self.assertEqual(record['installed_name'], 'adapted-fixture')

    def test_file_or_mode_changes_are_detected_without_refreshing_manifest(self):
        self.install()
        record = (self.destination/helper.RECORD).read_bytes()
        (self.destination/'SKILL.md').chmod(0o755)
        self.assertFalse(helper.verify(self.destination)['unchanged'])
        (self.destination/'SKILL.md').chmod(0o644)
        (self.destination/'scripts/check.py').write_text('Changed script')
        result = helper.verify(self.destination)
        self.assertIn('scripts/check.py', result['changed_files'])
        self.assertEqual((self.destination/helper.RECORD).read_bytes(), record)

    def test_host_validation_records_passes_and_limits_separately(self):
        self.install()
        report = {'validation': [{'kind': kind, 'status': 'passed', 'evidence': ['Synthetic host fixture record']}
                                 for kind in ('host-discovery', 'host-invocation')]}
        report['validation'][1]['status'] = 'not_run'
        self.assertEqual(helper.record_validation(self.destination, report)['state'], 'installed_unverified')
        report['validation'][1]['status'] = 'passed'
        self.assertEqual(helper.record_validation(self.destination, report)['state'], 'validated')
        self.assertEqual(len(helper.metadata(self.destination)['validation_history']), 2)
        (self.destination/'SKILL.md').write_text('Changed after validation')
        with self.assertRaises(ValueError):
            helper.record_validation(self.destination, report)

    def test_source_metadata_names_cannot_be_overwritten(self):
        (self.source/helper.RECORD).write_text('{}')
        self.git('add', '.')
        self.git('commit', '-qm', 'Reserved filename')
        with self.assertRaises(ValueError):
            self.stage(commit=self.git('rev-parse', 'HEAD').strip())
        self.assertFalse(self.candidate.exists())

    def test_cli_errors_do_not_echo_private_git_urls(self):
        private = 'https://private-secret@github.com/fixture/skills.git'
        self.git('remote', 'set-url', 'origin', private)
        result = subprocess.run([sys.executable, str(SCRIPT), 'stage', '--checkout', str(self.repo),
                                 '--repository', 'fixture/skills', '--commit', self.commit,
                                 '--skill-path', 'skills/fixture-skill', '--legal', 'LICENSE',
                                 '--output', str(self.candidate)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertNotIn('private-secret', result.stdout + result.stderr)

    def test_inspect_does_not_run_git_or_candidate_code(self):
        self.stage()
        result = subprocess.run([sys.executable, str(SCRIPT), 'inspect', str(self.candidate)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['state'], 'staged')


if __name__ == '__main__':
    unittest.main()
