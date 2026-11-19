import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location('portable_harness', Path(__file__).parents[1]/'codex-team.py')
h = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(h)


class PortableRuntimeTests(unittest.TestCase):
    def test_nonblocking_lock_excludes_another_process_and_releases(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)/'lock'
            support = h.MEMORY_MODULE.support
            command = [sys.executable, '-B', '-c',
                       'import importlib.util,sys; from pathlib import Path; '
                       's=importlib.util.spec_from_file_location("support",sys.argv[1]); '
                       'm=importlib.util.module_from_spec(s); s.loader.exec_module(m); '
                       'f=open(sys.argv[2],"a+"); m.lock(f,blocking=False); m.unlock(f)',
                       str(Path(support.__file__)), str(path)]
            with path.open('a+') as stream:
                support.lock(stream, blocking=False)
                self.assertNotEqual(subprocess.run(command, capture_output=True, timeout=10).returncode, 0)
                support.unlock(stream)
                self.assertEqual(subprocess.run(command, capture_output=True, timeout=10).returncode, 0)

    def test_timeout_terminates_process(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            with self.assertRaises(h.HarnessError) as caught:
                h.execute([sys.executable, '-c', 'import time; time.sleep(30)'], root, .2,
                          root/'stdout', root/'stderr')
            self.assertEqual(caught.exception.kind, 'timeout')


if __name__ == '__main__':
    unittest.main()
