import json
from pathlib import Path
import subprocess
import sys
import unittest


class ReportTests(unittest.TestCase):
    def invoke(self, data):
        return subprocess.run([sys.executable, str(Path(__file__).with_name('report.py'))],
                              input=data, text=True, capture_output=True)

    def test_numbers(self):
        result = self.invoke('[1, -2, 3.5]')
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout), {'count': 3, 'total': 2.5})
        self.assertEqual(result.stderr, '')

    def test_empty(self):
        result = self.invoke('[]')
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout), {'count': 0, 'total': 0})

    def test_invalid(self):
        for data in ('broken', '{}', '[true]', '["2"]', '[null]', '[NaN]', '[Infinity]'):
            with self.subTest(data=data):
                result = self.invoke(data)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, '')
                self.assertTrue(result.stderr.strip())
                self.assertNotIn('Traceback', result.stderr)


if __name__ == '__main__':
    unittest.main()
