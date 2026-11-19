#!/usr/bin/env python3
"""Loopback-only build/test/export fixture. Test results are real; coverage is not measured."""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import io
import json
from pathlib import Path
import threading
import unittest
from urllib.parse import urlsplit

SOURCE = '''def paginate(items, page, size):
    if type(page) is not int or type(size) is not int or page < 1 or size < 1:
        raise ValueError('Positive integer page and size required')
    return list(items[(page-1)*size:page*size])
'''
PAGE = '''<!doctype html><html lang="zh-CN"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>OpenAS 客户演示</title>
<style>body{font:18px system-ui;max-width:800px;margin:60px auto;padding:20px;color:#172033}
button,a{display:inline-block;padding:14px;margin:8px;border:1px solid #ccd3e0;border-radius:8px}
pre{white-space:pre-wrap;background:#eef2ff;padding:20px}</style>
<h1>构建 → 测试 → 导出报告</h1><p>真实 Python 测试的演示工程。此页面不测量覆盖率，不代表客户生产工具。</p>
<button id="build">1. 构建工程</button><button id="test">2. 运行测试</button>
<a href="/export" download="test-report.json">3. 导出测试报告</a>
<pre id="status" role="status" aria-live="polite">尚未构建</pre>
<script>
for (const name of ['build','test']) document.getElementById(name).onclick=async()=>{
const response=await fetch('/api/'+name,{method:'POST'});
document.getElementById('status').textContent=JSON.stringify(await response.json(),null,2);};
fetch('/api/status').then(r=>r.json()).then(s=>document.getElementById('status').textContent=JSON.stringify(s,null,2));
</script></html>'''


class Session:
    def __init__(self, checkpoint):
        self.checkpoint = checkpoint
        self.built = False
        self.result = None
        self.lock = threading.Lock()

    def build(self):
        compile(SOURCE, 'demo_pagination.py', 'exec')
        self.built = True
        self.result = None
        return {'build': 'passed', 'run_id': self.checkpoint['id']}

    def test(self):
        if not self.built:
            raise ValueError('Build the project first')
        namespace = {}
        exec(compile(SOURCE, 'demo_pagination.py', 'exec'), namespace)
        paginate = namespace['paginate']
        class Tests(unittest.TestCase):
            def test_one_based(self): self.assertEqual(paginate([1, 2, 3], 1, 2), [1, 2])
            def test_empty(self): self.assertEqual(paginate([], 1, 2), [])
            def test_beyond_end(self): self.assertEqual(paginate([1], 5, 2), [])
            def test_invalid(self):
                for page, size in ((0, 1), (1, 0), (True, 2), (1, 1.5)):
                    with self.subTest(page=page, size=size), self.assertRaises(ValueError):
                        paginate([1], page, size)
        result = unittest.TextTestRunner(stream=io.StringIO()).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
        self.result = {'passed': result.wasSuccessful(), 'count': result.testsRun,
                       'failures': len(result.failures), 'errors': len(result.errors)}
        return self.result

    def report(self):
        if not self.result or not self.result['passed']:
            raise ValueError('Run passing tests before exporting')
        return {'version': 1, 'run_id': self.checkpoint['id'], 'build': 'passed',
                'tests': self.result, 'coverage': 'not_measured', 'fixture': 'OpenAS customer demo'}


def serve(session, port=8080):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def send(self, status, payload, content_type='application/json; charset=utf-8', download=False):
            data = payload.encode('utf-8') if isinstance(payload, str) else json.dumps(payload).encode('utf-8')
            self.send_response(status)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(data)))
            self.send_header('Cache-Control', 'no-store')
            if download:
                self.send_header('Content-Disposition', 'attachment; filename="test-report.json"')
            self.end_headers(); self.wfile.write(data)

        def dispatch(self, method):
            # Restrict browser-origin writes and DNS rebinding to this loopback service.
            if self.headers.get('Host') != '127.0.0.1:'+str(self.server.server_port):
                self.send(403, {'error': 'Loopback host required'}); return
            origin = self.headers.get('Origin')
            if origin and origin != 'http://127.0.0.1:'+str(self.server.server_port):
                self.send(403, {'error': 'Same-origin requests required'}); return
            path = urlsplit(self.path).path
            with session.lock:
                try:
                    if method == 'GET' and path == '/':
                        self.send(200, PAGE, 'text/html; charset=utf-8')
                    elif method == 'GET' and path == '/api/status':
                        self.send(200, {'run_id': session.checkpoint['id'], 'built': session.built, 'tests': session.result})
                    elif method == 'POST' and path in ('/api/build', '/api/test'):
                        self.send(200, session.build() if path.endswith('build') else session.test())
                    elif method == 'GET' and path == '/export':
                        self.send(200, session.report(), download=True)
                    else:
                        self.send(404, {'error': 'Unknown route'})
                except ValueError as exc:
                    self.send(409, {'error': str(exc)})

        def do_GET(self): self.dispatch('GET')
        def do_POST(self): self.dispatch('POST')
    return ThreadingHTTPServer(('127.0.0.1', port), Handler)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--checkpoint', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--port', type=int, default=8080)
    args = parser.parse_args()
    checkpoint = json.loads(args.checkpoint.read_text(encoding='utf-8'))
    if not isinstance(checkpoint.get('id'), str) or not checkpoint.get('criteria'):
        parser.error('Create a Praxis checkpoint with acceptance criteria first')
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output/'downloads').mkdir()
    rule = {'path': 'downloads/test-report.json', 'fresh': True, 'run_id_pointer': '/run_id',
            'json_fields': {'/build': 'passed', '/tests/passed': True, '/tests/count': 4, '/coverage': 'not_measured'}}
    (args.output/'verifier.json').write_text(json.dumps({'criteria': {c: rule for c in checkpoint['criteria']}}, indent=2), encoding='utf-8')
    server = serve(Session(checkpoint), args.port)
    print(json.dumps({'url': 'http://127.0.0.1:'+str(server.server_port),
                      'download_directory': str((args.output/'downloads').resolve()),
                      'verifier': str((args.output/'verifier.json').resolve())}), flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
