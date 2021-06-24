
from contextlib import contextmanager
import io, os, sys

class PipeIO(io.IOBase):
    """File-like object that writes to a pipe connection"""
    #? There are possibly better ways to do this
    #? Todo- implement read
    def __init__(self, connection, mode):
        super().__init__()
        self._pid = os.getpid()
        self._cache = ''
        self.connection = connection
        self.buffer = ''
        if not (mode == 'r' or mode == 'w'):
            raise ValueError("Invalid mode: '{}'".format(str(mode)))
        self.mode = mode

    @property
    def cache(self):
        """Fork-safe, discard cache, from multiprocessing doc"""
        pid = os.getpid()
        if pid != self._pid:
            self._pid = pid
            self._cache = ''
        return self._cache

    @cache.setter
    def cache(self, value):
        self._cache = value

    def close(self):
        self.flush()
        self.connection.close()
        self.closed = True

    def fileno(self):
        return self.connection.fileno()

    def readable(self):
        return self.mode == 'r'

    def read(self, size=-1):
        if not self.readable():
            raise io.UnsupportedOperation('not readable')
        if size < 0:
            if self.cache == '':
                self.cache = self.connection.recv()
            result = self.cache
            self.cache = ''
            return result
        while len(self.cache) < size:
            self.cache += self.connection.recv()
        result = self.cache[:size]
        self.cache = self.cache[size:]
        return result

    # To do if required:
    # def readline(size=-1):
    #     pass
    # def readlines(hint=-1):
    #     pass

    def writable(self):
        return self.mode == 'w'

    def write(self, text):
        if not self.writable():
            raise io.UnsupportedOperation('not writable')
        # no buff, just send
        self.connection.send(text)
        # temp = self.buffer + text
        # self.buffer = ''
        # for line in temp.splitlines(True):
        #     if line[-1] == '\n':
        #         self.connection.send(line)
        #     else:
        #         self.buffer += line

    def writelines(self, lines):
        for line in lines:
            self.connection.send(line+'\n')

    def flush(self):
        if self.buffer != '':
            self.connection.send(self.buffer)
        self.buffer = ''


@contextmanager
def _redirect(module=sys, stream='stdout', dest=None):
    """Redirect module stream to file stream"""
    original = getattr(module, stream)
    original.flush()
    setattr(module, stream, dest)
    try:
        yield dest
    finally:
        dest.flush()
        setattr(module, stream, original)

@contextmanager
def redirect(module=sys, stream='stdout', dest=None, mode='w'):
    """
    Redirect module's stream according to `dest`:
    - If None: Do nothing
    - If String: Open file and redirect
    - Else: Assume IOWrapper, redirect
    """
    if dest is None:
        yield getattr(module, stream)
    elif isinstance(dest, str):
        with open(dest, mode) as file, _redirect(module, stream, file) as f:
            yield f
    else:
        with _redirect(module, stream, dest) as f:
            yield f
