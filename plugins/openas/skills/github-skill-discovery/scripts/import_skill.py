#!/usr/bin/env python3
"""Stage pinned GitHub skills, install reviewed local packages, and record provenance."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import sys
import tempfile

RECORD = 'OPENAS_SOURCE.json'
ORIGIN = '_openas_origin'
MAX_FILES = 1000
MAX_BYTES = 50 * 1024 * 1024


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def package_sha(files):
    return sha(json.dumps(files, sort_keys=True, ensure_ascii=False).encode())


def relative(value, allow_root=False):
    if not isinstance(value, str) or not value or '\\' in value or ':' in value or any(ord(c) < 32 for c in value):
        raise ValueError('Invalid relative path')
    path = PurePosixPath(value)
    if path.is_absolute() or '..' in path.parts or '.git' in path.parts or (path == PurePosixPath('.') and not allow_root):
        raise ValueError('Path must stay within its package')
    return path.as_posix()


def bounded(value):
    if not isinstance(value, str) or not value.strip() or len(value) > 4000:
        raise ValueError('Review text must be nonempty and bounded')
    return value


def git(checkout, *args):
    process = subprocess.run(['git', '-C', str(checkout), *args], capture_output=True, timeout=30,
                             env=dict(os.environ, GIT_NO_REPLACE_OBJECTS='1'))
    if process.returncode:
        raise ValueError('Cannot read pinned Git objects or origin; check checkout and commit')
    return process.stdout


def origin_repository(value):
    match = re.fullmatch(r'(?:https://github\.com/|git@github\.com:|ssh://git@github\.com/)([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+?)(?:\.git)?/?', value.strip())
    if not match:
        raise ValueError('Origin must be a credential-free GitHub.com URL')
    return match[1].lower()


def skill_name(raw):
    content = raw.decode('utf-8-sig')
    if not content.startswith('---\n') or '\n---\n' not in content[4:]:
        raise ValueError('SKILL.md requires YAML frontmatter')
    header = content.split('---', 2)[1]
    match = re.search(r'^name:\s*(?:([\"\x27])([a-z0-9-]+)\1|([a-z0-9-]+))\s*(?:#.*)?$', header, re.M)
    if not match:
        raise ValueError('SKILL.md requires a conventional scalar name')
    name = match[2] or match[3]
    if len(name) > 64 or name.startswith('-') or name.endswith('-') or '--' in name:
        raise ValueError('Invalid skill name')
    if not re.search(r'^description:\s*\S', header, re.M):
        raise ValueError('SKILL.md requires description; use a host validator for full YAML checks')
    return name


def local(path):
    path = Path(path).absolute()
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError('Package paths cannot contain symlinks')
    return path


def write_record(root, value):
    fd, temporary = tempfile.mkstemp(prefix='.openas-source-', dir=root)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write('\n')
            stream.flush(); os.fsync(stream.fileno())
        os.replace(temporary, root/RECORD)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def read_package(root):
    root = local(root)
    if not root.is_dir():
        raise ValueError('Package directory must exist')
    blobs, files = {}, {}
    total = 0
    for path in sorted(root.rglob('*')):
        if path.is_symlink():
            raise ValueError('Package contains a symlink')
        if path.is_dir():
            continue
        if not path.is_file():
            raise ValueError('Package contains a special file')
        name = relative(path.relative_to(root).as_posix())
        if name == RECORD:
            continue
        if len(files) >= MAX_FILES or path.stat().st_size > MAX_BYTES - total:
            raise ValueError('Package exceeds 1000 files or 50 MiB')
        raw = path.read_bytes()
        total += len(raw)
        blobs[name] = raw
        files[name] = {'sha256': sha(raw), 'mode': stat.S_IMODE(path.stat().st_mode)}
    if 'SKILL.md' not in blobs:
        raise ValueError('Missing SKILL.md')
    skill_name(blobs['SKILL.md'])
    return blobs, files


def metadata(root):
    path = local(root)/RECORD
    if path.is_symlink():
        raise ValueError('Provenance record cannot be a symlink')
    value = json.loads(path.read_text(encoding='utf-8'))
    if value.get('version') != 1 or not isinstance(value.get('original_files'), dict) or not value.get('legal_files'):
        raise ValueError('Invalid provenance record')
    return value


def legal_intact(record, files):
    for item in record['legal_files']:
        for key in ('stored_path', 'package_path'):
            if item.get(key) and files.get(relative(item[key]), {}).get('sha256') != item['sha256']:
                raise ValueError('Applicable license/notice file was removed or changed')


def write_new(root, blobs, files, record):
    root = local(root)
    if root.exists():
        raise ValueError('Destination already exists; no files overwritten')
    root.parent.mkdir(parents=True, exist_ok=True)
    root.mkdir()  # Exclusive creation also prevents replacing an existing empty directory.
    try:
        for name, raw in blobs.items():
            path = root/relative(name)
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open('xb') as stream:
                stream.write(raw)
            path.chmod(files[name]['mode'])
        write_record(root, record)
    except BaseException:
        shutil.rmtree(root)
        raise


def stage(checkout, repository, commit, skill_path, legal, output):
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repository) or not re.fullmatch(r'(?:[0-9a-f]{40}|[0-9a-f]{64})', commit):
        raise ValueError('Use owner/repo and a full lowercase commit SHA')
    if origin_repository(git(checkout, 'remote', 'get-url', 'origin').decode()) != repository.lower():
        raise ValueError('Declared repository differs from checkout origin')
    if git(checkout, 'rev-parse', '--verify', commit + '^{commit}').decode().strip() != commit:
        raise ValueError('Commit must resolve exactly')
    source = relative(skill_path, allow_root=True)
    prefix = '' if source == '.' else source + '/'
    selected = {}
    all_files = {}
    for entry in git(checkout, 'ls-tree', '-r', '-z', '--full-tree', commit).split(b'\0'):
        if not entry:
            continue
        info, name = entry.split(b'\t', 1)
        mode, kind, oid = info.decode().split()
        name = name.decode('utf-8')
        all_files[name] = (mode, kind, oid)
        if name.startswith(prefix):
            rel = relative(name[len(prefix):])
            if rel == RECORD or PurePosixPath(rel).parts[0] == ORIGIN:
                raise ValueError('Source uses reserved provenance paths')
            selected[rel] = (mode, kind, oid)
    if not selected or len(selected) > MAX_FILES:
        raise ValueError('Missing or oversized skill directory')
    if not legal:
        raise ValueError('Provide applicable license/notice paths reviewed at this commit')
    legal_items = []
    for name in dict.fromkeys(legal):
        name = relative(name)
        if name not in all_files:
            raise ValueError('Legal file missing from pinned commit')
        target = f'{ORIGIN}/legal/{name}'
        selected[target] = all_files[name]
        legal_items.append({'origin_path': name, 'stored_path': target,
                            'package_path': name[len(prefix):] if name.startswith(prefix) else None})
    blobs, files = {}, {}
    total = 0
    for name, (mode, kind, oid) in selected.items():
        if kind != 'blob' or mode not in ('100644', '100755'):
            raise ValueError('Symlinks, submodules and special entries require manual adaptation')
        size = int(git(checkout, 'cat-file', '-s', oid))
        if size > MAX_BYTES - total or len(files) >= MAX_FILES:
            raise ValueError('Package exceeds 1000 files or 50 MiB')
        raw = git(checkout, 'cat-file', 'blob', oid)
        total += len(raw)
        blobs[name] = raw
        files[name] = {'sha256': sha(raw), 'mode': int(mode, 8) & 0o777}
    if 'SKILL.md' not in blobs:
        raise ValueError('No SKILL.md at selected directory root')
    name = skill_name(blobs['SKILL.md'])
    for item in legal_items:
        item['sha256'] = files[item['stored_path']]['sha256']
    record = {'version': 1, 'repository': repository, 'url': 'https://github.com/' + repository,
              'commit': commit, 'skill_path': source, 'name': name, 'staged_at': now(),
              'state': 'staged', 'original_files': files, 'legal_files': legal_items, 'validation_history': []}
    write_new(output, blobs, files, record)
    return inspect(output)


def inspect(root):
    record = metadata(root)
    _, files = read_package(root)
    legal_intact(record, files)
    original = record['original_files']
    changes = sorted(name for name in set(original) | set(files) if original.get(name) != files.get(name))
    return {'repository': record['repository'], 'commit': record['commit'], 'skill_path': record['skill_path'],
            'state': record['state'], 'package_sha256': package_sha(files), 'changed_files': changes,
            'files': files, 'name': skill_name((Path(root)/'SKILL.md').read_bytes())}


def validations(items, required):
    if not isinstance(items, list) or not items:
        raise ValueError('Validation entries required')
    kinds = set()
    for item in items:
        kind = bounded(item.get('kind'))
        if kind in kinds or item.get('status') not in ('passed', 'failed', 'not_run'):
            raise ValueError('Invalid or duplicate validation entry')
        kinds.add(kind)
        if not isinstance(item.get('evidence'), list) or not item['evidence']:
            raise ValueError('Validation needs actual evidence or an explicit limitation')
        for evidence in item['evidence']:
            bounded(evidence)
    if not required <= kinds:
        raise ValueError('Required validation categories missing')
    return all(item['status'] == 'passed' for item in items)


def install(candidate, report, destination):
    candidate, destination = local(candidate), local(destination)
    if candidate == destination or candidate in destination.parents or destination in candidate.parents:
        raise ValueError('Candidate and destination cannot overlap')
    record = metadata(candidate)
    if record['state'] != 'staged':
        raise ValueError('Install from a staged candidate')
    current = inspect(candidate)
    for key in ('repository', 'commit', 'skill_path', 'package_sha256'):
        if report.get(key) != current[key]:
            raise ValueError('Review is not bound to this repository, commit and package')
    if report.get('decision') != 'accept' or any(report.get('checks', {}).get(key) is not True for key in ('content', 'dependencies', 'license', 'fit')):
        raise ValueError('Content, dependency, license and fit review must pass')
    bounded(report.get('reviewer'))
    for key in ('expression', 'usage', 'notes'):
        bounded(report.get('license', {}).get(key))
    dependencies = report.get('dependencies')
    if not isinstance(dependencies, list):
        raise ValueError('Explicit dependency inventory required; use [] when none')
    for item in dependencies:
        bounded(item.get('name')); bounded(item.get('version'))
        if item.get('status') != 'available':
            raise ValueError('Resolve missing dependencies before installation')
    if not validations(report.get('validation'), {'structure', 'behavior'}):
        raise ValueError('Staged structure and behavior must be validated before installation')
    changes = report.get('changes')
    if report.get('mode') not in ('copy', 'adapted') or not isinstance(changes, list):
        raise ValueError('Specify copy/adapted mode and changes')
    for change in changes:
        bounded(change)
    if current['changed_files'] and (report['mode'] != 'adapted' or not changes):
        raise ValueError('Adaptations require a change description')
    if report['mode'] == 'copy' and changes:
        raise ValueError('Copy mode cannot declare adaptations')
    if report['mode'] == 'adapted' and not changes:
        raise ValueError('Adapted mode requires a change description')
    if destination.name != current['name']:
        raise ValueError('Destination directory must match the skill name')
    blobs, files = read_package(candidate)
    if package_sha(files) != current['package_sha256']:
        raise ValueError('Candidate changed during inspection')
    record.update(state='installed_unverified', installed_at=now(), installed_name=current['name'], installed_files=files,
                  package_sha256=current['package_sha256'], review=report)
    write_new(destination, blobs, files, record)
    return {'destination': str(destination), 'state': record['state'], 'package_sha256': record['package_sha256']}


def verify(root):
    record = metadata(root)
    _, files = read_package(root)
    if 'installed_files' not in record:
        raise ValueError('No installed file inventory')
    changed = sorted(name for name in set(record['installed_files']) | set(files) if record['installed_files'].get(name) != files.get(name))
    return {'unchanged': not changed, 'changed_files': changed, 'state': record['state']}


def record_validation(root, report):
    root = local(root)
    if not verify(root)['unchanged']:
        raise ValueError('Installed files changed; re-review before recording validation')
    passed = validations(report.get('validation'), {'host-discovery', 'host-invocation'})
    record = metadata(root)
    record['validation_history'].append({'at': now(), 'report': report})
    record['state'] = 'validated' if passed else 'installed_unverified'
    write_record(root, record)
    return {'state': record['state'], 'note': 'Caller-reported host validation; file integrity alone does not prove behavior'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    p = sub.add_parser('stage')
    p.add_argument('--checkout', type=Path, required=True)
    p.add_argument('--repository', required=True)
    p.add_argument('--commit', required=True)
    p.add_argument('--skill-path', required=True)
    p.add_argument('--legal', nargs='+', required=True)
    p.add_argument('--output', type=Path, required=True)
    p = sub.add_parser('install')
    p.add_argument('--candidate', type=Path, required=True)
    p.add_argument('--review', type=Path, required=True)
    p.add_argument('--destination', type=Path, required=True)
    for command in ('inspect', 'verify', 'record-validation'):
        p = sub.add_parser(command); p.add_argument('directory', type=Path)
        if command == 'record-validation':
            p.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.action == 'stage':
            result = stage(args.checkout, args.repository, args.commit, args.skill_path, args.legal, args.output)
        elif args.action == 'install':
            result = install(args.candidate, json.loads(args.review.read_text()), args.destination)
        elif args.action == 'record-validation':
            result = record_validation(args.directory, json.loads(args.report.read_text()))
        else:
            result = globals()[args.action](args.directory)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1 if args.action == 'verify' and not result['unchanged'] else 0
    except (OSError, ValueError, KeyError, TypeError, UnicodeError, subprocess.TimeoutExpired):
        print('Import failed: check pinned source, paths, legal files, review and validation; existing destinations are preserved.', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
