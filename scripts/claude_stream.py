"""Minimal POSIX stream-json test driver; not an Agent SDK or production runner.

Wire envelope follows Anthropic's SDK control protocol. Unknown requests fail
closed. Transcripts stay in memory; CLI stderr stays in a temporary file.
"""
import json
import math
import os
from pathlib import Path
import re
import selectors
import signal
import subprocess
import tempfile
import time
import uuid


class ProtocolError(RuntimeError):
    pass


def require_success(event):
    if (event.get('type') != 'result' or event.get('subtype') != 'success'
            or event.get('is_error') is not False):
        raise ProtocolError('Client returned a failed or malformed result; no native pass recorded')


def require_token(event, expected):
    require_success(event)
    if event.get('result', '').strip() != expected:
        raise ProtocolError('Probe output does not exactly match the expected skill revision')


def require_reload(event):
    require_success(event)
    if event.get('local_command', '').lstrip('/') != 'reload-plugins':
        raise ProtocolError('No native local_command=reload-plugins evidence; model prose is insufficient')
    text = event.get('result', '')
    if (not re.search(r'\bReloaded:\s*[1-9]\d*\s+plugins?\b', text, re.I)
            or re.search(r'\b[1-9]\d*\s+errors?\s+during\s+load\b', text, re.I)):
        raise ProtocolError('Reload was held, failed, or had no active plugin; inspect client locally')


def require_same_session(*events):
    ids = [event.get('session_id') for event in events]
    if not ids or not all(isinstance(s, str) and s for s in ids) or len(set(ids)) != 1:
        raise ProtocolError('Hot reload must use one nonempty, unchanged session ID')
    return ids[0]


class Session:
    def __init__(self, argv, cwd, timeout=120):
        if os.name != 'posix':
            raise ProtocolError('This pipe driver targets Linux/WSL/macOS; run on POSIX')
        if not math.isfinite(timeout) or timeout <= 0:
            raise ValueError('timeout must be finite and positive')
        self.argv, self.cwd, self.timeout = argv, Path(cwd), timeout
        self.session_id = ''
        self.buffer = b''

    def __enter__(self):
        self.stderr = tempfile.TemporaryFile()
        self.selector = selectors.DefaultSelector()
        try:
            self.proc = subprocess.Popen(self.argv, cwd=self.cwd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                         stderr=self.stderr, bufsize=0, start_new_session=True)
            self.selector.register(self.proc.stdout, selectors.EVENT_READ)
            return self
        except BaseException:
            self.__exit__(None, None, None)
            raise

    def __exit__(self, *args):
        proc = getattr(self, 'proc', None)
        if proc is not None:
            try:
                # Terminate the process group on error or successful test completion.
                os.killpg(proc.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                proc.wait(timeout=3)
            for pipe in (proc.stdin, proc.stdout):
                if pipe is not None:pipe.close()
        self.selector.close()
        self.stderr.close()

    def send(self, message):
        try:
            data = (json.dumps(message)+'\n').encode()
            if len(data) > 4096:
                raise ProtocolError('Test input exceeds bounded pipe message size')
            self.proc.stdin.write(data)
        except (BrokenPipeError, OSError) as exc:
            raise ProtocolError('CLI closed stdin before completing the test') from exc

    def next_event(self, deadline):
        while True:
            if b'\n' in self.buffer:
                line, self.buffer = self.buffer.split(b'\n',1)
                try:
                    event=json.loads(line)
                except (ValueError, UnicodeError) as exc:
                    raise ProtocolError('Malformed stream-json event (raw content withheld)') from exc
                if not isinstance(event, dict):
                    raise ProtocolError('Expected stream-json object')
                if event.get('type') == 'control_request':
                    raise ProtocolError('Unexpected permission/hook request; this probe permits no tools')
                return event
            remaining = deadline-time.monotonic()
            if remaining <= 0 or not self.selector.select(remaining):
                raise ProtocolError('Timed out waiting for native CLI response')
            chunk=os.read(self.proc.stdout.fileno(),65536)
            if not chunk:
                raise ProtocolError('CLI stdout closed before a complete response')
            self.buffer += chunk
            if len(self.buffer) > 4*1024*1024:
                raise ProtocolError('CLI event exceeded test buffer limit')

    def control(self, request):
        ident=uuid.uuid4().hex
        self.send({'type':'control_request','request_id':ident,'request':request})
        deadline=time.monotonic()+self.timeout
        while True:
            event=self.next_event(deadline)
            if event.get('type') != 'control_response':continue
            response=event.get('response',{})
            if response.get('request_id') != ident:continue
            if response.get('subtype') != 'success':
                raise ProtocolError('Native control initialization failed')
            return response.get('response',{})

    def turn(self, text):
        self.send({'type':'user','session_id':self.session_id,'parent_tool_use_id':None,
                   'message':{'role':'user','content':text}})
        deadline=time.monotonic()+self.timeout
        while True:
            event=self.next_event(deadline)
            if event.get('type') == 'result':
                require_success(event)
                self.session_id=event.get('session_id','')
                return event
