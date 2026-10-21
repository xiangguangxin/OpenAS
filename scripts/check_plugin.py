#!/usr/bin/env python3
"""Read-only structural checks for the OpenAS bundle (not a Claude client emulator)."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys


def metadata(path):
    text = path.read_text(encoding='utf-8')
    if not text.startswith('---\n') or '\n---\n' not in text[4:]:
        raise ValueError(f'Missing frontmatter: {path}')
    header = text.split('---', 2)[1]
    fields = {}
    for key in ('name', 'description'):
        match = re.search(r'^' + key + r':\s*(.+)$', header, re.MULTILINE)
        if not match or not match.group(1).strip():
            raise ValueError(f'Missing {key}: {path}')
        fields[key] = match.group(1).strip().strip('\"\'')
    if any(c in fields['description'] for c in '<>'):
        raise ValueError(f'Angle brackets in description: {path}')
    return fields


def check(root):
    root = Path(root).resolve()
    manifest = json.loads((root/'.claude-plugin/plugin.json').read_text())
    if not re.fullmatch(r'[a-z][a-z0-9-]*', manifest.get('name', '')):
        raise ValueError('Invalid plugin name')
    if not re.fullmatch(r'\d+\.\d+\.\d+', manifest.get('version', '')):
        raise ValueError('Expected release version x.y.z')
    # This package uses standard default directories only; no hidden executable hooks.
    if set(manifest) - {'name','version','description','author','repository','keywords'}:
        raise ValueError('Unexpected manifest fields; update checks before extending components')
    paths = list(root.rglob('*'))
    for p in paths:
        if p.is_symlink():
            raise ValueError(f'Package must be self-contained; symlink: {p}')
    files = [p for p in paths if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']
    skills = []
    for p in sorted((root/'skills').glob('*/SKILL.md')):
        info = metadata(p)
        if info['name'] != p.parent.name:
            raise ValueError(f'Skill name/directory mismatch: {p}')
        skills.append(info['name'])
    agents = []
    for p in sorted((root/'agents').glob('*.md')):
        info = metadata(p)
        if info['name'] != p.stem:
            raise ValueError(f'Agent name/file mismatch: {p}')
        agents.append(info['name'])
    if not skills or not agents:
        raise ValueError('No skills or agents')
    for p in files:
        if p.suffix != '.md':
            continue
        for link in re.findall(r'\]\(([^)]+)\)', p.read_text(encoding='utf-8')):
            if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:', link) or link.startswith('#'):
                continue
            target = link.split('#',1)[0]
            if not target or not (p.parent/target).exists():
                raise ValueError(f'Broken relative link {link}: {p}')
    content = hashlib.sha256()
    for p in sorted(files):
        rel = p.relative_to(root).as_posix()
        content.update(rel.encode()); content.update(b'\0'); content.update(p.read_bytes()); content.update(b'\0')
    return {'name':manifest['name'], 'version':manifest['version'], 'skills':skills,
            'agents':agents, 'files':len(files), 'sha256':content.hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('path', nargs='?', type=Path, default=Path(__file__).resolve().parents[1]/'plugins/openas')
    args = parser.parse_args()
    try:
        print(json.dumps(check(args.path), ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, TypeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
