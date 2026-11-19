import importlib.util
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

PLUGIN = Path(__file__).parents[2]
ROOT = PLUGIN.parents[1]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


app = module('customer_demo_app', PLUGIN/'workflows/examples/customer-gui/demo_app.py')
acceptance = module('customer_acceptance', ROOT/'scripts/customer_acceptance.py')
demo = module('customer_demo', ROOT/'scripts/customer_demo.py')


class CustomerDemoTests(unittest.TestCase):
    def test_real_http_build_test_download_and_order_enforcement(self):
        session = app.Session({'id': 'current-run', 'criteria': ['Report passes']})
        server = app.serve(session, 0)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        url = 'http://127.0.0.1:'+str(server.server_port)
        try:
            with self.assertRaises(HTTPError) as error:
                urlopen(url+'/export', timeout=3)
            self.assertEqual(error.exception.code, 409)
            error.exception.close()
            for action in ('build', 'test'):
                with urlopen(Request(url+'/api/'+action, method='POST'), timeout=3) as response:
                    self.assertEqual(response.status, 200)
            with urlopen(url+'/export', timeout=3) as response:
                self.assertIn('attachment', response.headers['Content-Disposition'])
                report = json.load(response)
            self.assertEqual(report['run_id'], 'current-run')
            self.assertTrue(report['tests']['passed'])
            self.assertEqual(report['tests']['count'], 4)
            self.assertEqual(report['coverage'], 'not_measured')
            with urlopen(Request(url+'/api/build', method='POST'), timeout=3):
                pass
            with self.assertRaises(HTTPError) as error:
                urlopen(url+'/export', timeout=3)
            self.assertEqual(error.exception.code, 409)
            error.exception.close()
            with self.assertRaises(HTTPError) as error:
                urlopen(Request(url+'/api/test', method='POST', headers={'Origin': 'https://untrusted.example'}), timeout=3)
            self.assertEqual(error.exception.code, 403)
            error.exception.close()
        finally:
            server.shutdown(); server.server_close(); thread.join(timeout=3)

    def test_demo_preparation_preserves_fixture_and_uses_current_interpreter(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp)/'demo'
            result = demo.prepare(output)
            self.assertFalse(result['model_started'])
            task = json.loads((output/'pagination-task.json').read_text())
            self.assertEqual(task['checks'][0][0], demo.sys.executable)
            self.assertEqual((output/'workspace/pagination.py').read_bytes(),
                             (demo.EXAMPLES/'pagination-fixture/pagination.py').read_bytes())

    def test_model_completion_alone_cannot_pass_real_acceptance(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            checkpoint = root/'checkpoint.json'
            checkpoint.write_text(json.dumps({'id': 'run', 'status': 'completed', 'criteria': ['Report']}))
            verifier = root/'rules.json'
            verifier.write_text(json.dumps({'criteria': {'Report': {'fresh': True, 'run_id_pointer': '/run_id'}}}))
            downloads = root/'downloads'; downloads.mkdir()
            def execute(command, cwd, timeout, stdout, stderr):
                stdout.write_text(json.dumps({'passed': False, 'checks': {'Report': {'status': 'stale_artifact'}}}))
                stderr.write_text('')
                return 0 if command[1] == 'run' else 1
            with patch.object(acceptance.shutil, 'which', return_value='fixture-only'), patch.object(acceptance.h, 'execute', execute):
                result = acceptance.run(checkpoint, verifier, root/'evidence', browser_url='http://127.0.0.1:8080', downloads=downloads)
            self.assertEqual(result['status'], 'failed')
            self.assertEqual(result['verification']['checks']['Report']['status'], 'stale_artifact')


if __name__ == '__main__':
    unittest.main()
