#!/usr/bin/env python3
"""Native OpenAS study/build/compare entry point; no Craft Anything install required."""
import importlib.util
from pathlib import Path

SPEC = importlib.util.spec_from_file_location('openas_reconstruction', Path(__file__).resolve().parents[1]/'skills/software-reconstruction/scripts/reconstruction.py')
implementation = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(implementation)

if __name__ == '__main__':
    raise SystemExit(implementation.main())
