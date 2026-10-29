"""Actual PDF extraction, page provenance and failure boundaries; no OCR claims."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT/'plugins/openas/skills/pdf-extraction/scripts/extract_pdf.py'
SPEC = importlib.util.spec_from_file_location('pdf_extraction', SCRIPT)
pdf = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(pdf)
HAS_PYPDF = importlib.util.find_spec('pypdf') is not None


def make_pdf(path, texts=('Alpha report', None, 'Gamma result', ''), password=None, broken_page=None):
    """Create text, image-only and genuinely blank pages without a renderer."""
    from pypdf import PdfWriter
    from pypdf.generic import DictionaryObject, NameObject, NumberObject, DecodedStreamObject
    writer = PdfWriter()
    font = DictionaryObject({NameObject('/Type'): NameObject('/Font'),
                             NameObject('/Subtype'): NameObject('/Type1'),
                             NameObject('/BaseFont'): NameObject('/Helvetica')})
    font_ref = writer._add_object(font)
    for index, text in enumerate(texts, 1):
        page = writer.add_blank_page(width=200, height=200)
        resources = DictionaryObject({NameObject('/Font'): DictionaryObject({NameObject('/F1'): font_ref})})
        page[NameObject('/Resources')] = resources
        if text is None:
            image = DecodedStreamObject()
            image.set_data(b'\xff\x00\x00')
            image.update({NameObject('/Type'): NameObject('/XObject'), NameObject('/Subtype'): NameObject('/Image'),
                          NameObject('/Width'): NumberObject(1), NameObject('/Height'): NumberObject(1),
                          NameObject('/ColorSpace'): NameObject('/DeviceRGB'), NameObject('/BitsPerComponent'): NumberObject(8)})
            resources[NameObject('/XObject')] = DictionaryObject({NameObject('/Im0'): writer._add_object(image)})
            content = b'q 50 0 0 50 20 20 cm /Im0 Do Q'
        elif text:
            escaped = text.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')
            content = ('BT /F1 12 Tf 20 100 Td ('+escaped+') Tj ET').encode('cp1252')
        else:
            content = b''
        if index == broken_page:
            content = b'BT /F1 12 Tf (unterminated'
        stream = DecodedStreamObject(); stream.set_data(content)
        page[NameObject('/Contents')] = writer._add_object(stream)
    if password is not None:
        # Small fixture only; no optional crypto package required by these tests.
        writer.encrypt(password, algorithm='RC4-128')
    writer.write(path)


class PageSelectionTests(unittest.TestCase):
    def test_ranges_and_requested_order(self):
        self.assertEqual(pdf.select_pages(None, 4), [1, 2, 3, 4])
        self.assertEqual(pdf.select_pages('4, 1-2', 4), [4, 1, 2])

    def test_invalid_overlapping_or_reversed_pages(self):
        for selection in ('', '0', '5', '2-1', '1,1', '1-3,2', '1.0', '-1', '1,', '1-999999999'):
            with self.subTest(selection=selection), self.assertRaises(ValueError):
                pdf.select_pages(selection, 4)
        with self.assertRaises(ValueError):
            pdf.select_pages(None, 0)


@unittest.skipUnless(HAS_PYPDF, 'Optional pypdf dependency required')
class ExtractionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name); self.source = self.root/'source.pdf'
        make_pdf(self.source)
        self.original = self.source.read_bytes(); self.output = self.root/'extracted'

    def test_actual_text_with_physical_page_provenance_and_hashes(self):
        report = pdf.extract(self.source, self.output, pages='3,1')
        self.assertEqual(report['status'], 'completed')
        self.assertEqual(report['selected_pages'], [3, 1])
        self.assertEqual(report['source_sha256'], hashlib.sha256(self.original).hexdigest())
        payload = json.loads((self.output/'pages.json').read_text())
        self.assertEqual([p['page_number'] for p in payload['pages']], [3, 1])
        self.assertEqual([p['text'] for p in payload['pages']], ['Gamma result', 'Alpha report'])
        text = (self.output/'text.txt').read_text()
        self.assertLess(text.index('Gamma result'), text.index('Alpha report'))
        for name, digest in report['output_sha256'].items():
            self.assertEqual(hashlib.sha256((self.output/name).read_bytes()).hexdigest(), digest)
        self.assertNotIn('Alpha report', json.dumps(report))
        self.assertEqual(self.source.read_bytes(), self.original)

    def test_image_only_and_true_blank_are_not_claimed_as_recognized(self):
        report = pdf.extract(self.source, self.output, pages='2,4')
        self.assertEqual(report['status'], 'needs_review')
        self.assertEqual(report['empty_pages'], [2, 4])
        self.assertFalse(report['ocr_performed'])
        payload = json.loads((self.output/'pages.json').read_text())
        self.assertTrue(all(p['status']=='no_text' and p['review_or_ocr_suggested'] for p in payload['pages']))
        self.assertTrue(all(not p['text'].strip() for p in payload['pages']))
        self.assertEqual(report['failed_pages'], [])

    def test_image_page_with_existing_hidden_text_layer_needs_no_new_ocr(self):
        from pypdf import PdfWriter
        from pypdf.generic import DecodedStreamObject, NameObject
        writer = PdfWriter(clone_from=self.source)
        page = writer.pages[1]
        stream = DecodedStreamObject()
        stream.set_data(page['/Contents'].get_object().get_data() +
                        b' BT /F1 12 Tf 3 Tr 20 100 Td (Existing OCR layer) Tj ET')
        page[NameObject('/Contents')] = writer._add_object(stream)
        writer.write(self.source)
        report = pdf.extract(self.source, self.output, pages='2')
        payload = json.loads((self.output/'pages.json').read_text())
        self.assertIn('Existing OCR layer', payload['pages'][0]['text'])
        self.assertEqual(report['empty_pages'], [])
        self.assertFalse(report['ocr_performed'])

    def test_layout_mode_and_json_only_output(self):
        report = pdf.extract(self.source, self.output, pages='1', output_format='json', mode='layout')
        self.assertEqual(report['mode'], 'layout')
        self.assertFalse((self.output/'text.txt').exists())
        self.assertIn('Alpha report', json.loads((self.output/'pages.json').read_text())['pages'][0]['text'])

    def test_txt_only_does_not_create_json_text_payload(self):
        report = pdf.extract(self.source, self.output, pages='1', output_format='txt')
        self.assertEqual(report['outputs'], ['text.txt'])
        self.assertFalse((self.output/'pages.json').exists())
        self.assertTrue((self.output/'extraction-report.json').is_file())

    def test_existing_output_is_preserved(self):
        self.output.mkdir(); (self.output/'keep').write_text('original')
        with self.assertRaisesRegex(ValueError, 'must be new'):
            pdf.extract(self.source, self.output)
        self.assertEqual((self.output/'keep').read_text(), 'original')
        self.assertEqual(self.source.read_bytes(), self.original)

    def test_invalid_pages_and_options_create_no_output(self):
        for options in ({'pages':'6'}, {'pages':'1,1'}, {'output_format':'xml'}, {'mode':'ocr'}):
            with self.subTest(options=options), self.assertRaises(ValueError):
                pdf.extract(self.source, self.output, **options)
            self.assertFalse(self.output.exists())

    def test_malformed_pdf_and_empty_document_fail_before_output(self):
        self.source.write_bytes(b'%PDF-1.4\ninvalid')
        with self.assertRaises(Exception):
            pdf.extract(self.source, self.output)
        self.assertFalse(self.output.exists())
        make_pdf(self.source, texts=())
        with self.assertRaisesRegex(ValueError, 'no pages'):
            pdf.extract(self.source, self.output)
        self.assertFalse(self.output.exists())

    def test_encrypted_pdf_requires_supplied_correct_password_without_disclosure(self):
        secret = 'fixture-password-do-not-log'
        make_pdf(self.source, texts=('Protected text',), password=secret)
        for password in (None, 'incorrect'):
            with self.subTest(password=password), self.assertRaises(ValueError):
                pdf.extract(self.source, self.output, password=password)
            self.assertFalse(self.output.exists())
        report = pdf.extract(self.source, self.output, password=secret)
        self.assertTrue(report['encrypted'])
        self.assertIn('Protected text', (self.output/'text.txt').read_text())
        for path in self.output.iterdir():
            self.assertNotIn(secret, path.read_text())

    def test_actual_broken_page_yields_partial_results_instead_of_empty_text(self):
        make_pdf(self.source, texts=('Alpha report', 'Broken page', 'Gamma result'), broken_page=2)
        report = pdf.extract(self.source, self.output)
        self.assertEqual(report['status'], 'partial')
        self.assertEqual(report['failed_pages'], [2])
        self.assertEqual(report['empty_pages'], [])
        pages = json.loads((self.output/'pages.json').read_text())['pages']
        self.assertEqual(pages[0]['text'], 'Alpha report')
        self.assertEqual(pages[1]['status'], 'error')
        self.assertIsNone(pages[1]['text'])
        self.assertEqual(pages[2]['text'], 'Gamma result')

    def test_interruption_preserves_failed_report_without_success_claim(self):
        from pypdf._page import PageObject
        with patch.object(PageObject, 'extract_text', side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                pdf.extract(self.source, self.output)
        self.assertEqual(json.loads((self.output/'extraction-report.json').read_text())['status'], 'failed')

    def test_cli_exit_codes_for_complete_partial_and_invalid_selection(self):
        for name, broken, pages, expected in [('ok', None, '1', 0), ('partial', 2, None, 1), ('bad', None, '9', 2)]:
            make_pdf(self.source, texts=('Alpha', 'Beta'), broken_page=broken)
            args = [sys.executable, '-B', str(SCRIPT), str(self.source), '--output-dir', str(self.root/name)]
            if pages is not None:args.extend(['--pages', pages])
            result = subprocess.run(args, capture_output=True, text=True)
            with self.subTest(name=name):self.assertEqual(result.returncode, expected, result.stderr)

    def test_password_file_cli_never_echoes_secret(self):
        secret = 'fixture-private-value'
        make_pdf(self.source, texts=('Protected text',), password=secret)
        password_file = self.root/'password.txt'; password_file.write_text(secret+'\n')
        result = subprocess.run([sys.executable, '-B', str(SCRIPT), str(self.source), '--output-dir', str(self.output),
                                 '--password-file', str(password_file)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn(secret, result.stdout+result.stderr)


if __name__ == '__main__':
    unittest.main()
