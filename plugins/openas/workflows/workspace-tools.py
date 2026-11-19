#!/usr/bin/env python3
"""Inspect an existing engineering workspace or prepare an isolated task copy."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import stat
import tempfile

SPEC = importlib.util.spec_from_file_location('workspace_harness', Path(__file__).with_name('codex-team.py'))
h = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(h)


def relative(value):
    path = Path(value)
    if path.is_absolute() or '..' in path.parts or path == Path('.'):
        raise ValueError('Expected an explicit project-relative path')
    return path


def inspect(source, task):
    source = source.resolve(strict=True)
    h.validate_task(task)
    count = size = 0
    links, special = [], []
    # No dereferencing here; inspection never opens link targets.
    for path in source.rglob('*'):
        if path.is_symlink():
            links.append(path.relative_to(source).as_posix())
        elif path.is_file():
            count += 1; size += path.stat().st_size
        elif not path.is_dir():
            special.append(path.relative_to(source).as_posix())
    collisions = [p for p in task.get('artifacts', []) if (source/p).exists() or (source/p).is_symlink()]
    return {'source': str(source), 'files': count, 'bytes': size, 'symlinks': links,
            'special_files': special, 'existing_artifacts': collisions,
            'direct_run_ready': not links and not special and not collisions,
            'unmapped_acceptance': [i+1 for i, indexes in enumerate(task.get('acceptance_checks', [[]]*len(task['acceptance']))) if not indexes],
            'recommendation': 'Use prepare for isolation, existing build outputs or internal symlinks. No source files were modified.'}


def prepare(source, output, task, include=(), exclude=(), materialize=False):
    source = source.resolve(strict=True)
    output = output.absolute()
    h.validate_task(task)
    if output.exists() or output.is_symlink() or output == source or source in output.parents:
        raise ValueError('Output must be new and outside the source workspace')
    if any(p.is_symlink() for p in output.parents):
        raise ValueError('Output must not traverse symlinks')
    included = tuple(map(relative, include))
    excluded = (Path('.git'), Path('.openas'), *map(relative, task.get('artifacts', [])), *map(relative, exclude))
    for name in map(Path, task['scope']):
        if any(name == p or p in name.parents for p in excluded):
            raise ValueError('Excluded path overlaps task scope')
        if included and not any(name == p or p in name.parents for p in included):
            raise ValueError('Include list must cover all task scope files')
    output.parent.mkdir(parents=True, exist_ok=True)
    receipt = {'version': 1, 'source': str(source), 'excluded': [p.as_posix() for p in excluded],
               'included': [p.as_posix() for p in included], 'materialized_links': [], 'files': {}}
    with tempfile.TemporaryDirectory(prefix='.openas-workspace-', dir=output.parent) as temporary:
        staging = Path(temporary)/'prepared'
        workspace = staging/'workspace'
        workspace.mkdir(parents=True)
        def copy(path, relative_path, parents):
            if any(relative_path == p or p in relative_path.parents for p in excluded):
                return
            if included and relative_path != Path('.') and not any(
                    relative_path == p or p in relative_path.parents or relative_path in p.parents for p in included):
                return
            if path.is_symlink():
                if not materialize:
                    raise ValueError('Symlink requires --materialize-symlinks: '+str(relative_path))
                resolved = path.resolve(strict=True)
                if resolved != source and source not in resolved.parents:
                    raise ValueError('Symlink escapes the source workspace: '+str(relative_path))
                target_relative = resolved.relative_to(source)
                if any(target_relative == p or p in target_relative.parents for p in excluded):
                    raise ValueError('Symlink points into an excluded directory')
                receipt['materialized_links'].append(relative_path.as_posix())
                path = resolved
            destination = workspace/relative_path
            if path.is_dir():
                resolved = path.resolve()
                if resolved in parents:
                    raise ValueError('Symlink directory cycle: '+str(relative_path))
                destination.mkdir(exist_ok=True)
                for child in sorted(path.iterdir()):
                    copy(child, relative_path/child.name, parents | {resolved})
            elif path.is_file():
                content = path.read_bytes()
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(content)
                destination.chmod(stat.S_IMODE(path.stat().st_mode))
                receipt['files'][relative_path.as_posix()] = hashlib.sha256(content).hexdigest()
            else:
                raise ValueError('Special files are not supported: '+str(relative_path))
        copy(source, Path('.'), set())
        (staging/'preparation.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding='utf-8')
        staging.replace(output)
    return {'workspace': str(output/'workspace'), 'receipt': str(output/'preparation.json'),
            'files': len(receipt['files']), 'source_modified': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('inspect', 'prepare'))
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--task', type=Path, required=True)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--include', action='append', default=[])
    parser.add_argument('--exclude', action='append', default=[])
    parser.add_argument('--materialize-symlinks', action='store_true')
    args = parser.parse_args()
    try:
        task = json.loads(args.task.read_text(encoding='utf-8'))
        if args.action == 'prepare':
            if not args.output:
                raise ValueError('prepare requires --output')
            result = prepare(args.source, args.output, task, args.include, args.exclude, args.materialize_symlinks)
        else:
            result = inspect(args.source, task)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result.get('direct_run_ready', True) else 1
    except (OSError, ValueError, h.HarnessError) as exc:
        print(json.dumps({'status': 'failed', 'error': str(exc)}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
