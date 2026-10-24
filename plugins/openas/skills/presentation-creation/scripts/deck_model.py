"""Copyright 2026 OpenAS contributors. SPDX-License-Identifier: Apache-2.0.
Original OpenAS specification and OOXML checks; see ../NOTICE.md for workflow sources.
"""
import json
import math
from pathlib import Path
import re
import unicodedata
import xml.etree.ElementTree as ET
import zipfile

SIZES = {'wide': (13.333333, 7.5), 'standard': (10.0, 7.5)}
TYPES = {'cover', 'section', 'bullets', 'two-column', 'process', 'chart', 'table', 'image', 'closing'}
EMU = 914400
NS = {'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
      'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
      'c': 'http://schemas.openxmlformats.org/drawingml/2006/chart'}


def text(value, maximum=1000):
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise ValueError('Expected bounded nonempty text')
    if any(ord(c) < 32 and c not in '\n\t' for c in value):
        raise ValueError('Unsupported control character in text')
    return value


def lines(value, maximum=6):
    if not isinstance(value, list) or not 1 <= len(value) <= maximum:
        raise ValueError('Expected a bounded nonempty text list')
    return [text(item, 300) for item in value]


def image_path(root, name):
    relative = Path(text(name, 600))
    path = (root/relative).resolve()
    if relative.is_absolute() or '..' in relative.parts or root not in path.parents or not path.is_file():
        raise ValueError('Image must be an existing file within assets-root')
    return path


def validate(spec, assets_root):
    if not isinstance(spec, dict) or type(spec.get('version')) is not int or spec.get('version') != 1:
        raise ValueError('Deck specification version must be 1')
    if set(spec) - {'version', 'title', 'audience', 'size', 'duration_minutes', 'theme', 'slides'}:
        raise ValueError('Unknown deck field')
    text(spec.get('title'), 150)
    if 'audience' in spec:
        text(spec['audience'], 200)
    if spec.get('size', 'wide') not in SIZES:
        raise ValueError('size must be wide or standard')
    slides = spec.get('slides')
    if not isinstance(slides, list) or not 1 <= len(slides) <= 100:
        raise ValueError('Expected 1-100 slides')
    if not isinstance(spec.get('theme', {}), dict):
        raise ValueError('theme must be an object')
    for key, value in spec.get('theme', {}).items():
        if key in ('background', 'foreground', 'accent', 'surface', 'muted'):
            if not isinstance(value, str) or not re.fullmatch(r'[A-Fa-f0-9]{6}', value):
                raise ValueError('Theme colors require six hex digits')
        elif key in ('font', 'cjk_font'):
            text(value, 100)
        else:
            raise ValueError('Unknown theme field')
    for slide in slides:
        if not isinstance(slide, dict):
            raise ValueError('Each slide must be an object')
        kind = slide.get('type')
        if kind not in TYPES:
            raise ValueError('Unsupported slide type')
        allowed = {'type', 'title', 'notes', 'seconds', 'sources'}
        allowed |= {'cover': {'subtitle'}, 'section': {'subtitle'}, 'bullets': {'bullets', 'caption'},
                    'closing': {'bullets', 'caption'}, 'two-column': {'left', 'right', 'caption'},
                    'process': {'steps', 'caption'}, 'chart': {'chart_type', 'categories', 'series', 'unit', 'caption'},
                    'table': {'columns', 'rows', 'caption'}, 'image': {'image', 'alt', 'caption'}}[kind]
        if set(slide) - allowed:
            raise ValueError('Unknown or inapplicable slide field')
        text(slide.get('title'), 150)
        text(slide.get('notes'), 4000)
        seconds = slide.get('seconds')
        if type(seconds) is not int or not 1 <= seconds <= 600:
            raise ValueError('Each slide needs a 1-600 second speaking budget')
        if not isinstance(slide.get('sources', []), list) or len(slide.get('sources', [])) > 12:
            raise ValueError('sources must be a list')
        for source in slide.get('sources', []):
            text(source, 500)
        if 'subtitle' in slide:
            text(slide['subtitle'], 500)
        if kind in ('bullets', 'closing'):
            lines(slide.get('bullets'))
        elif kind == 'two-column':
            for side in ('left', 'right'):
                if not isinstance(slide.get(side), dict):
                    raise ValueError('Column must be an object')
                text(slide.get(side, {}).get('heading'), 80)
                lines(slide[side].get('bullets'), 5)
        elif kind == 'process':
            if not isinstance(slide.get('steps'), list) or not 2 <= len(slide['steps']) <= 4:
                raise ValueError('Process slides need 2-4 steps')
            for step in slide['steps']:
                if not isinstance(step, dict):
                    raise ValueError('Process step must be an object')
                text(step.get('label'), 80); text(step.get('detail'), 180)
        elif kind == 'chart':
            if slide.get('chart_type', 'column') not in ('column', 'line'):
                raise ValueError('Only native column and line charts are supported')
            categories = lines(slide.get('categories'), 10)
            series = slide.get('series')
            if not isinstance(series, list) or not 1 <= len(series) <= 4:
                raise ValueError('Charts need 1-4 series')
            for item in series:
                if not isinstance(item, dict):
                    raise ValueError('Chart series must be an object')
                text(item.get('name'), 60)
                values = item.get('values')
                if not isinstance(values, list) or len(values) != len(categories) or any(type(v) not in (int, float) or not math.isfinite(v) for v in values):
                    raise ValueError('Chart values must be finite and match categories')
            text(slide.get('unit'), 80)
            if not slide.get('sources'):
                raise ValueError('Chart data needs a source; label illustrative data explicitly')
        elif kind == 'table':
            columns = lines(slide.get('columns'), 5)
            rows = slide.get('rows')
            if not isinstance(rows, list) or not 1 <= len(rows) <= 6:
                raise ValueError('Tables need 1-6 data rows')
            for row in rows:
                if not isinstance(row, list) or len(row) != len(columns):
                    raise ValueError('Table row width mismatch')
                for cell in row:
                    text(cell, 160)
            if not slide.get('sources'):
                raise ValueError('Table needs a source')
        elif kind == 'image':
            image_path(assets_root, slide.get('image'))
            text(slide.get('alt'), 600)
        if 'caption' in slide:
            text(slide['caption'], 500)
    duration = spec.get('duration_minutes')
    if duration is not None and (type(duration) not in (int, float) or not math.isfinite(duration) or duration <= 0 or sum(x['seconds'] for x in slides) > duration*60):
        raise ValueError('Speaking budgets exceed the positive duration_minutes limit')
    return spec


def estimated_lines(content, width, font_size):
    capacity = max(1, width*72/font_size)
    result = 0
    for line in content.split('\n'):
        units = sum(1.0 if unicodedata.east_asian_width(c) in ('W', 'F') else .57 for c in line if not unicodedata.combining(c))
        result += max(1, math.ceil(units/capacity))
    return result


def inspect_pptx(path):
    errors, warnings, result = [], [], []
    with zipfile.ZipFile(path) as archive:
        if len(archive.infolist()) > 10000 or sum(x.file_size for x in archive.infolist()) > 200*1024*1024:
            raise ValueError('Oversized PPTX package')
        presentation = ET.fromstring(archive.read('ppt/presentation.xml'))
        size = presentation.find('p:sldSz', NS)
        width, height = int(size.attrib['cx'])/EMU, int(size.attrib['cy'])/EMU
        rels = ET.fromstring(archive.read('ppt/_rels/presentation.xml.rels'))
        targets = {x.attrib['Id']: x.attrib['Target'] for x in rels}
        for number, item in enumerate(presentation.findall('p:sldIdLst/p:sldId', NS), 1):
            rid = item.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']
            target = targets[rid]
            part = 'ppt/' + target.lstrip('/') if not target.startswith('/') else target.lstrip('/')
            if '..' in Path(part).parts:
                raise ValueError('Unexpected slide relationship path')
            doc = ET.fromstring(archive.read(part))
            shapes, content_boxes = [], []
            for element in doc.find('p:cSld/p:spTree', NS):
                if element.tag.rsplit('}', 1)[-1] in ('nvGrpSpPr', 'grpSpPr'):
                    continue
                name_node = element.find('.//p:cNvPr', NS)
                name = name_node.attrib.get('name', '') if name_node is not None else ''
                content = '\n'.join(x.text or '' for x in element.findall('.//a:t', NS))
                transform = element.find('p:spPr/a:xfrm', NS)
                if transform is None:
                    transform = element.find('p:xfrm', NS)
                box = None
                if transform is not None:
                    off, ext = transform.find('a:off', NS), transform.find('a:ext', NS)
                    if off is not None and ext is not None:
                        box = [int(off.attrib['x'])/EMU, int(off.attrib['y'])/EMU, int(ext.attrib['cx'])/EMU, int(ext.attrib['cy'])/EMU]
                        x, y, w, h = box
                        if x < -.005 or y < -.005 or w <= 0 or h <= 0 or x+w > width+.005 or y+h > height+.005:
                            errors.append(f'Slide {number}: out-of-bounds shape {name}')
                        if not name.startswith('decor:'):
                            content_boxes.append((name, box))
                elif element.tag.endswith('grpSp'):
                    warnings.append(f'Slide {number}: group geometry requires manual review')
                if re.search(r'\b(?:TODO|TBD|lorem ipsum)\b', content, re.I):
                    warnings.append(f'Slide {number}: possible leftover placeholder in {name}')
                shapes.append({'name': name, 'text': content, 'box': box,
                               'native_chart': element.find('.//c:chart', NS) is not None,
                               'native_table': element.find('.//a:tbl', NS) is not None})
            for i, (name, box) in enumerate(content_boxes):
                for other, second in content_boxes[i+1:]:
                    overlap_w = min(box[0]+box[2], second[0]+second[2])-max(box[0], second[0])
                    overlap_h = min(box[1]+box[3], second[1]+second[3])-max(box[1], second[1])
                    if overlap_w > .01 and overlap_h > .01 and overlap_w*overlap_h > .02:
                        errors.append(f'Slide {number}: overlapping content {name} / {other}')
            result.append({'number': number, 'shapes': shapes})
    return {'passed': not errors, 'slide_count': len(result), 'width': width, 'height': height,
            'errors': errors, 'warnings': warnings, 'slides': result,
            'scope': 'OOXML package, native elements and top-level geometry only; no rendered text-fit, font, accessibility or PowerPoint compatibility claim'}
