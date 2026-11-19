#!/usr/bin/env python3
"""Install a self-contained OpenAS bundle with repo-scoped Codex skill entries."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import queue
import re
import shutil
import subprocess
import tempfile
import threading
import time

PLUGIN = Path(__file__).resolve().parents[1]
_SUPPORT_SPEC = importlib.util.spec_from_file_location('installer_support', PLUGIN/'skills/project-memory/scripts/runtime_support.py')
support = importlib.util.module_from_spec(_SUPPORT_SPEC)
_SUPPORT_SPEC.loader.exec_module(support)


def files(root):
    result = {}
    for path in sorted(root.rglob('*')):
        if path.is_symlink():
            raise ValueError('Bundle and managed installation must not contain symlinks')
        if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc':
            result[path.relative_to(root).as_posix()] = path.read_bytes()
    return result


def hashes(content):
    return {p: hashlib.sha256(b).hexdigest() for p, b in content.items()}


def target(project):
    root = Path(project).absolute()
    if not root.is_dir():
        raise ValueError('Existing project directory required')
    agents = root/'.agents'
    for path in (agents/'skills', agents, root, *root.parents):
        if path.is_symlink():
            raise ValueError('Installation path must not traverse symlinks')
    return agents


def payload(plugin=PLUGIN):
    data = {'openas/'+p: b for p, b in files(plugin).items()}
    names = []
    for skill in sorted((plugin/'skills').glob('*/SKILL.md')):
        header = skill.read_text(encoding='utf-8').split('---', 2)[1]
        name = 'openas-'+skill.parent.name
        names.append(name)
        header = re.sub(r'^name:.*$', 'name: '+name, header, flags=re.M)
        wrapper = ('---'+header+'---\n\n'
                   'Read and follow the complete [OpenAS method](../../openas/skills/'
                   + skill.parent.name+'/SKILL.md) before executing this task. Resolve all of that '
                   'method\'s relative resources from its original bundled location. '
                   'Use only tools actually available and actions authorized for the current task.\n')
        data['skills/'+name+'/SKILL.md'] = wrapper.encode('utf-8')
    return data, names


def installed(agents):
    manifest = agents/'openas-install.json'
    if manifest.is_symlink():
        raise ValueError('Installation manifest must not be a symlink')
    receipt = json.loads(manifest.read_text(encoding='utf-8'))
    names = receipt.get('skills', [])
    if (receipt.get('version') != 1 or not isinstance(names, list) or not names
            or any(not isinstance(n, str) or not re.fullmatch(r'openas-[a-z0-9-]+', n) for n in names) or len(names) != len(set(names))):
        raise ValueError('Invalid installation manifest')
    owned = ['openas', *('skills/'+n for n in names)]
    actual = {}
    for folder in owned:
        if (agents/folder).is_symlink() or not (agents/folder).is_dir():
            raise ValueError('Managed installation missing or replaced')
        actual.update({folder+'/'+p: b for p, b in files(agents/folder).items()})
    if hashes(actual) != receipt.get('files'):
        raise ValueError('Installed files changed; preserve local edits before update or removal')
    return receipt, owned


def install(project, action='install', plugin=PLUGIN):
    agents = target(project)
    if Path(project).resolve() == plugin.resolve() or plugin.resolve() in Path(project).resolve().parents:
        raise ValueError('Install into a consumer project outside the source plugin')
    if action == 'check':
        return _install(project, action, plugin)
    agents.mkdir(exist_ok=True)
    lock_path = agents/'.openas-install.lock'
    if lock_path.is_symlink():
        raise ValueError('Installation lock must not be a symlink')
    with lock_path.open('a+') as stream, support.locked(stream, blocking=False):
        return _install(project, action, plugin)


def _install(project, action='install', plugin=PLUGIN):
    agents = target(project)
    data, names = payload(plugin)
    old = []
    if (agents/'openas-install.json').is_symlink():
        raise ValueError('Installation manifest must not be a symlink')
    if action != 'install':
        receipt, old = installed(agents)
        if action == 'check':
            return {'integrity': True, 'source_matches': receipt['files'] == hashes(data),
                    'skills': names, 'native_discovery': 'not_checked'}
    folders = ['openas', *('skills/'+n for n in names)] if action != 'uninstall' else []
    for folder in folders:
        if folder not in old and ((agents/folder).exists() or (agents/folder).is_symlink()):
            raise ValueError('Installation conflicts with an existing path: '+folder)
    if action == 'install' and (agents/'openas-install.json').exists():
        raise ValueError('Already installed; use check or update')
    agents.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.openas-stage-', dir=agents) as temporary:
        stage = Path(temporary)
        if action != 'uninstall':
            for path, content in data.items():
                destination = stage/'new'/path
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(content)
            receipt = {'version': 1, 'skills': names, 'files': hashes(data),
                       'plugin_version': json.loads((plugin/'.claude-plugin/plugin.json').read_text())['version']}
            (stage/'manifest.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
        moved, created = [], []
        try:
            for folder in old + (['openas-install.json'] if old else []):
                backup = stage/'old'/folder
                backup.parent.mkdir(parents=True, exist_ok=True)
                (agents/folder).replace(backup)
                moved.append(folder)
            for folder in folders:
                (agents/folder).parent.mkdir(parents=True, exist_ok=True)
                (stage/'new'/folder).replace(agents/folder)
                created.append(folder)
            if action != 'uninstall':
                (stage/'manifest.json').replace(agents/'openas-install.json')
        except BaseException:
            for folder in reversed(created):
                shutil.rmtree(agents/folder)
            for folder in reversed(moved):
                (stage/'old'/folder).replace(agents/folder)
            raise
    return {'action': action, 'skills': names if action != 'uninstall' else [],
            'native_discovery': 'not_checked'}


def native_check(project, names, client='codex', timeout=20):
    """Ask the real client's discovery API, without starting a model turn."""
    messages = queue.Queue()
    process = subprocess.Popen([client, 'app-server'], cwd=project, stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                               text=True, encoding='utf-8')
    def read():
        for line in process.stdout:
            messages.put(line)
        messages.put(None)
    thread = threading.Thread(target=read, daemon=True)
    thread.start()
    deadline = time.monotonic()+timeout
    def send(value):
        process.stdin.write(json.dumps(value)+'\n'); process.stdin.flush()
    def response(ident):
        while True:
            remaining = deadline-time.monotonic()
            if remaining <= 0:
                raise ValueError('Native discovery timed out; no model task was started')
            try:
                line = messages.get(timeout=remaining)
            except queue.Empty as exc:
                raise ValueError('Native discovery timed out') from exc
            if line is None:
                raise ValueError('Client exited before discovery; check its local configuration, writable state directory and supported app-server API')
            item = json.loads(line)
            if item.get('id') == ident:
                if 'error' in item:
                    raise ValueError('Client rejected discovery API; check supported client version')
                return item['result']
    try:
        send({'id': 1, 'method': 'initialize', 'params': {
            'clientInfo': {'name': 'openas_discovery', 'version': '1.0.0'}}})
        response(1)
        send({'method': 'initialized', 'params': {}})
        send({'id': 2, 'method': 'skills/list', 'params': {'cwds': [str(Path(project).resolve())], 'forceReload': True}})
        data = response(2)
        entries = [s for row in data.get('data', []) for s in row.get('skills', [])]
        expected_root = Path(project).resolve()/'.agents/skills'
        found = {s.get('name') for s in entries if s.get('enabled', True)
                 and expected_root in Path(s.get('path', '')).resolve().parents}
        missing = sorted(set(names)-found)
        return {'native_discovery': 'passed' if not missing else 'failed', 'missing': missing,
                'model_turn_started': False}
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill(); process.wait()
        thread.join(timeout=1)
        process.stdin.close(); process.stdout.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('install', 'update', 'check', 'uninstall'))
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--native', action='store_true', help='Check real Codex discovery; never starts a model turn')
    parser.add_argument('--client', default='codex')
    args = parser.parse_args()
    try:
        if args.native and args.action != 'check':
            raise ValueError('--native requires check')
        result = install(args.project, args.action)
        if args.native:
            result.update(native_check(args.project, result['skills'], args.client))
        print(json.dumps(result, ensure_ascii=False))
        return 1 if result.get('source_matches') is False or result.get('native_discovery') == 'failed' else 0
    except (OSError, ValueError) as exc:
        print(json.dumps({'status': 'failed', 'error': str(exc)}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
