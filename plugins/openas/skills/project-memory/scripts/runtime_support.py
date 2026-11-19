"""Small, dependency-free process and advisory lock helpers for POSIX and Windows."""
import errno
import os
import signal
import subprocess
import time
from contextlib import contextmanager

IS_WINDOWS = os.name == 'nt'
if IS_WINDOWS:
    import msvcrt
else:
    import fcntl


def lock(stream, blocking=True):
    if IS_WINDOWS:
        # msvcrt locks bytes from the current position; reserve a stable byte.
        stream.seek(0, os.SEEK_END)
        if stream.tell() == 0:
            stream.write('0')
            stream.flush()
        stream.seek(0)
        while True:
            try:
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
                break
            except OSError as exc:
                if exc.errno not in (errno.EACCES, errno.EAGAIN, errno.EDEADLK):
                    raise
                if not blocking:
                    raise BlockingIOError('Lock is held by another process') from exc
                time.sleep(.05)
    else:
        fcntl.flock(stream, fcntl.LOCK_EX | (0 if blocking else fcntl.LOCK_NB))


def unlock(stream):
    if IS_WINDOWS:
        stream.seek(0)
        msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
    else:
        fcntl.flock(stream, fcntl.LOCK_UN)


@contextmanager
def locked(stream, blocking=True):
    lock(stream, blocking)
    try:
        yield
    finally:
        unlock(stream)


def process_options():
    return {'creationflags': subprocess.CREATE_NEW_PROCESS_GROUP} if IS_WINDOWS else {'start_new_session': True}


def terminate_tree(process):
    if IS_WINDOWS:
        # Kill descendants too; terminate() alone can leave an Agent running.
        try:
            subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10, check=False)
        finally:
            if process.poll() is None:
                process.kill()
            process.wait(timeout=10)
    else:
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            return
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        finally:
            # A parent can exit promptly while a descendant ignores SIGTERM.
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
