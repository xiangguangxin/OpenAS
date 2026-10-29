#!/usr/bin/env python3
"""Extract local PDF text with physical page provenance; no OCR or conversion.

Exit 0: selected pages processed (empty pages still require review).
Exit 1: page-level errors retained as partial/failed results.
Exit 2: invalid input, environment, password, or output failure.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import sys


def select_pages(specification, count):
    """Return 1-based physical PDF pages in requested order, without duplicates."""
    if count < 1:
        raise ValueError('PDF contains no pages')
    if specification is None:
        return list(range(1, count + 1))
    result = []
    seen = set()
    for token in specification.split(','):
        match = re.fullmatch(r'\s*([0-9]+)(?:\s*-\s*([0-9]+))?\s*', token)
        if not match:
            raise ValueError('pages must contain 1-based numbers or inclusive ranges, e.g. 1,3-5')
        first = int(match[1]); last = int(match[2]) if match[2] is not None else first
        if not 1 <= first <= last <= count:
            raise ValueError('Page selection is reversed or outside the PDF')
        for number in range(first, last + 1):
            if number in seen:
                raise ValueError('Duplicate or overlapping page selection')
            seen.add(number); result.append(number)
    return result


def extract(source, output, *, pages=None, output_format='both', mode='plain', password=None):
    from pypdf import PdfReader
    source, output = Path(source).resolve(), Path(output).resolve()
    if not source.is_file() or source.suffix.lower() != '.pdf':
        raise ValueError('An existing local .pdf file is required')
    if output_format not in ('txt', 'json', 'both') or mode not in ('plain', 'layout'):
        raise ValueError('Unsupported extraction format or mode')
    if output.exists():
        raise ValueError('Output directory must be new; existing files are preserved')
    data = source.read_bytes()
    reader = PdfReader(io.BytesIO(data))
    encrypted = reader.is_encrypted
    if encrypted:
        if password is None:
            raise ValueError('Encrypted PDF requires a supplied password; no output was created')
        if not reader.decrypt(password):
            raise ValueError('PDF password was not accepted; no output was created')
    count = len(reader.pages)
    selected = select_pages(pages, count)
    report = {'version': 1, 'source_name': source.name, 'source_sha256': hashlib.sha256(data).hexdigest(),
              'pdf_page_count': count, 'selected_pages': selected, 'encrypted': encrypted,
              'mode': mode, 'status': 'running', 'pages': [], 'outputs': [],
              'empty_pages': [], 'failed_pages': [], 'ocr_performed': False,
              'limits': 'Physical PDF pages, not printed labels. Empty text is not proof of a scan. '
                        'Reading order, tables, formulas, glyphs and completeness require review.'}
    output.mkdir(parents=True, exist_ok=False)
    records = []
    try:
        for number in selected:
            try:
                text = reader.pages[number - 1].extract_text(extraction_mode=mode) or ''
                status = 'text_extracted' if text.strip() else 'no_text'
                record = {'page_number': number, 'status': status, 'text': text,
                          'character_count': len(text), 'review_or_ocr_suggested': status == 'no_text'}
                if status == 'no_text':
                    report['empty_pages'].append(number)
            except Exception as exc:
                # A failed parser is not an empty page or a successful OCR result.
                record = {'page_number': number, 'status': 'error', 'text': None,
                          'character_count': 0, 'review_or_ocr_suggested': False,
                          'error_kind': type(exc).__name__, 'error': str(exc)}
                report['failed_pages'].append(number)
            records.append(record)
            report['pages'].append({key: value for key, value in record.items() if key != 'text'})
        payload = {key: report[key] for key in ('version', 'source_name', 'source_sha256', 'pdf_page_count', 'selected_pages', 'mode')}
        payload['pages'] = records
        if output_format in ('json', 'both'):
            (output/'pages.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
            report['outputs'].append('pages.json')
        if output_format in ('txt', 'both'):
            sections = []
            for record in records:
                header = f'===== PDF page {record["page_number"]} | {record["status"]} ====='
                content = record['text'] if record['text'] is not None else '[Text extraction failed; see extraction-report.json]'
                if record['status'] == 'no_text':
                    content = '[No text extracted; inspect the page or use a separate OCR workflow]'
                sections.append(header + '\n' + content)
            (output/'text.txt').write_text('\n\n'.join(sections)+'\n', encoding='utf-8')
            report['outputs'].append('text.txt')
        failed = len(report['failed_pages'])
        report['status'] = ('failed' if failed == len(selected) else 'partial') if failed else (
            'needs_review' if report['empty_pages'] else 'completed')
        report['output_sha256'] = {name: hashlib.sha256((output/name).read_bytes()).hexdigest()
                                   for name in report['outputs']}
    except (Exception, KeyboardInterrupt) as exc:
        report.update(status='failed', error_kind=type(exc).__name__, error=str(exc))
        raise
    finally:
        (output/'extraction-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--output-dir', required=True, type=Path)
    parser.add_argument('--pages', help='1-based physical PDF pages, e.g. 1,3-5; default all')
    parser.add_argument('--format', choices=['txt', 'json', 'both'], default='both', dest='output_format')
    parser.add_argument('--mode', choices=['plain', 'layout'], default='plain')
    parser.add_argument('--password-file', type=Path, help='Read a supplied password from this file, never command-line text')
    args = parser.parse_args()
    try:
        password = args.password_file.read_text(encoding='utf-8').rstrip('\r\n') if args.password_file else None
        report = extract(args.source, args.output_dir, pages=args.pages, output_format=args.output_format,
                         mode=args.mode, password=password)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1 if report['failed_pages'] else 0
    except Exception as exc:
        print(f'PDF extraction failed: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
