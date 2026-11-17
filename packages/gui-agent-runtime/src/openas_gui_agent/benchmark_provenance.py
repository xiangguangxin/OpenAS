"""Reproducibility metadata for an evaluated suite."""
import hashlib
from importlib import metadata
import json
from pathlib import Path
import platform


def package_version(name):
    try:
        return metadata.version(name)
    except metadata.PackageNotFoundError:
        return None


def manifest(scenarios, repeat):
    # Preserve mapping order because criteria follow their declared order in model context.
    suite = json.dumps(scenarios, ensure_ascii=False, separators=(",", ":")).encode()
    package = Path(__file__).resolve().parent
    code = hashlib.sha256()
    for source in sorted(package.rglob("*.py")):
        code.update(source.relative_to(package).as_posix().encode() + b"\0")
        code.update(hashlib.sha256(source.read_bytes()).digest())
    return {
        "schema_version": 1,
        "suite_sha256": hashlib.sha256(suite).hexdigest(),
        "runtime_source_sha256": code.hexdigest(),
        "runtime_package_version": package_version("openas-gui-agent"),
        "repeat": repeat,
        "python_version": platform.python_version(),
        "os": platform.system(),
        "architecture": platform.machine(),
    }
