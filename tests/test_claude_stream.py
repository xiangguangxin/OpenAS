"""Local transport/false-positive checks; these never certify native hot reload."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location('claude_stream_unit', Path(__file__).parents[1]/'scripts/claude_stream.py')
s = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(s)


def result(text='TOKEN', session='same', **extra):
    return {'type':'result','subtype':'success','is_error':False,'result':text,'session_id':session,**extra}


class StreamTests(unittest.TestCase):
    def test_old_marker_and_failure_result_are_rejected(self):
        for event in [result('OLD'), result('NEW', is_error=True), result('NEW', subtype='error_during_execution'),
                      {'type':'assistant','result':'NEW'}, result('NEW with explanation')]:
            with self.subTest(event=event), self.assertRaises(s.ProtocolError):
                s.require_token(event, 'NEW')

    def test_model_claim_is_not_a_native_reload(self):
        for event in [result('Reloaded: 1 plugins'), result('Reloaded: 0 plugins',local_command='reload-plugins'),
                      result('Run /reload-plugins --force to apply',local_command='reload-plugins'),
                      result('Reloaded: 1 plugins; 1 errors during load',local_command='reload-plugins')]:
            with self.subTest(event=event), self.assertRaises(s.ProtocolError):
                s.require_reload(event)
        s.require_reload(result('Reloaded: 1 plugins · 15 skills', local_command='reload-plugins'))

    def test_session_change_or_missing_id_is_rejected(self):
        for events in [(result(),result(session='new')), (result(),result(session=''))]:
            with self.assertRaises(s.ProtocolError):s.require_same_session(*events)
        self.assertEqual(s.require_same_session(result(),result()), 'same')

    def test_pipe_transport_handshake_and_result_filtering(self):
        code = '''import json,sys
for line in sys.stdin:
    request=json.loads(line)
    if request['type']=='control_request':
        out={'type':'control_response','response':{'subtype':'success','request_id':request['request_id'],'response':{'ready':True}}}
    else:
        print(json.dumps({'type':'user','message':{'content':'DECOY'}}),flush=True)
        out={'type':'result','subtype':'success','is_error':False,'result':'TOKEN','session_id':'same'}
    print(json.dumps(out),flush=True)
'''
        with tempfile.TemporaryDirectory() as tmp:
            with s.Session([sys.executable,'-u','-c',code],Path(tmp),2) as session:
                self.assertEqual(session.control({'subtype':'initialize'}), {'ready':True})
                s.require_token(session.turn('/probe'), 'TOKEN')
                proc=session.proc
            self.assertIsNotNone(proc.poll())

    def test_timeout_and_early_exit_do_not_hang(self):
        with tempfile.TemporaryDirectory() as tmp:
            for code in ['import time;time.sleep(20)', 'raise SystemExit(7)']:
                with self.subTest(code=code):
                    with self.assertRaises(s.ProtocolError):
                        with s.Session([sys.executable,'-c',code],Path(tmp),0.1) as session:
                            proc=session.proc
                            session.turn('/probe')
                    self.assertIsNotNone(proc.poll())


if __name__ == '__main__':
    unittest.main()
