#!/usr/bin/env python3
"""Copyright 2026 OpenAS contributors. SPDX-License-Identifier: Apache-2.0.
Inspect OOXML structure and top-level geometry; no renderer required.
"""
import argparse
import json
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
sys.dont_write_bytecode = True
from deck_model import inspect_pptx


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('deck', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        report = inspect_pptx(args.deck)
        raw = json.dumps(report, ensure_ascii=False, indent=2)
        if args.output:
            with args.output.open('x', encoding='utf-8') as stream:
                stream.write(raw+'\n')
        print(raw)
        return 0 if report['passed'] else 1
    except (OSError, ValueError, KeyError, ET.ParseError, zipfile.BadZipFile) as exc:
        print(f'Inspection failed: {type(exc).__name__}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
