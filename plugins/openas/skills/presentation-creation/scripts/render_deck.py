#!/usr/bin/env python3
"""Copyright 2026 OpenAS contributors. SPDX-License-Identifier: Apache-2.0.
Render through local LibreOffice and Poppler; create PNG pages and a contact sheet.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile

sys.dont_write_bytecode = True
from deck_model import inspect_pptx


def execute(command, output, timeout):
    with (output/'render.log').open('a', encoding='utf-8') as log:
        process = subprocess.Popen(command, stdout=log, stderr=log, start_new_session=True)
        try:
            code = process.wait(timeout=timeout)
        except (subprocess.TimeoutExpired, KeyboardInterrupt):
            if os.name == 'posix':
                os.killpg(process.pid, signal.SIGTERM)
            else:
                process.terminate()
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                if os.name == 'posix':
                    os.killpg(process.pid, signal.SIGKILL)
                else:
                    process.kill()
                process.wait()
            raise
    if code:
        raise ValueError('Rendering command failed; see render.log')


def render(deck, output, office=None, poppler=None, timeout=120):
    office = shutil.which(str(office)) if office else shutil.which('soffice') or shutil.which('libreoffice')
    poppler = shutil.which(str(poppler)) if poppler else shutil.which('pdftoppm')
    if not office or not poppler:
        raise ValueError('Local LibreOffice and pdftoppm are required; no tools were installed')
    from PIL import Image, ImageDraw
    deck = Path(deck).resolve(); output = Path(output).resolve()
    if not deck.is_file() or deck.suffix.lower() != '.pptx' or timeout <= 0:
        raise ValueError('Existing .pptx and positive timeout required')
    expected_pages = inspect_pptx(deck)['slide_count']
    output.mkdir(parents=True, exist_ok=False)
    with tempfile.TemporaryDirectory(prefix='openas-office-profile-') as profile:
        execute([office, '-env:UserInstallation='+Path(profile).as_uri(), '--headless', '--convert-to', 'pdf',
                 '--outdir', str(output), str(deck)], output, timeout)
    pdf = output/(deck.stem+'.pdf')
    if not pdf.is_file():
        raise ValueError('Office returned without a PDF; inspect render.log')
    pages = output/'pages'; pages.mkdir()
    execute([poppler, '-png', '-scale-to', '1600', str(pdf), str(pages/'slide')], output, timeout)
    images = sorted(pages.glob('slide-*.png'), key=lambda p: int(re.search(r'-(\d+)\.png$', p.name)[1]))
    if not images or len(images) > 100:
        raise ValueError('Unexpected rendered page count')
    if len(images) != expected_pages:
        raise ValueError('Rendered page count differs from the source deck; review export settings and hidden slides')
    columns = min(3, len(images)); rows = (len(images)+columns-1)//columns
    sheet = Image.new('RGB', (columns*500+20, rows*310+20), '#DDE2E7')
    draw = ImageDraw.Draw(sheet)
    for index, image_path in enumerate(images):
        with Image.open(image_path) as image:
            thumb = image.convert('RGB'); thumb.thumbnail((480, 270))
            x, y = 20+(index%columns)*500, 20+(index//columns)*310
            sheet.paste(thumb, (x, y))
            draw.text((x, y+278), f'Slide {index+1}', fill='#18232F')
    sheet.save(output/'montage.png')
    report = {'deck_sha256': hashlib.sha256(deck.read_bytes()).hexdigest(), 'pdf': pdf.name,
              'expected_slide_count': expected_pages,
              'pages': [str(p.relative_to(output)) for p in images], 'montage': 'montage.png',
              'renderer': 'LibreOffice + Poppler', 'rendering': 'completed', 'human_visual_review': 'not_run',
              'limits': 'Rendered output is available for review; no automated claim of correct content, fonts, reading order or PowerPoint compatibility'}
    (output/'render-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('deck', type=Path)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--soffice')
    parser.add_argument('--pdftoppm')
    parser.add_argument('--timeout', type=int, default=120)
    args = parser.parse_args()
    try:
        result = render(args.deck, args.output_dir, args.soffice, args.pdftoppm, args.timeout)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, ImportError, KeyError, ET.ParseError, zipfile.BadZipFile, subprocess.TimeoutExpired) as exc:
        print(f'Render failed: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
