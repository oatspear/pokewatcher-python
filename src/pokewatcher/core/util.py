# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Callable, Optional

import socket
import time

from attrs import define, field

###############################################################################
# Interface
###############################################################################


def noop(*args, **kwargs):
    pass


def const_false(*args, **kwargs):
    return False


@define
class SleepLoop:
    """Context manager for a timed sleep loop.
    Use `n <= 0` for an infinite loop.
    Use `delay` to specify the sleep time (in seconds) between iterations.
    Includes `delta` (seconds) - time spent since the previous iteration.
    Includes the `timestamp` at which the current iteration is starting.
    Usage:

    ```
    # should run three times, with 1 second pauses between iterations
    with SleepLoop(n=3, delay=1.0) as loop:
        while loop.iterate():
            print('Iteration number:', loop.iteration)
            print('Elapsed time since the previous iteration:', loop.delta)
            print('This iteration is starting at:', loop.timestamp)
        assert loop.i == loop.n
        print('Iterated', loop.i, 'times.')
    ```
    """

    n: int = 0
    delay: float = 1.0
    iterate: Callable = field(init=False, default=const_false)
    i: int = field(init=False, default=-1)
    delta: float = field(init=False, default=0.0)
    timestamp: float = field(init=False, default=0.0)

    @property
    def iteration(self):
        return self.i + 1

    def _first_iteration(self):
        self.i = 0
        self.delta = 0.0
        self.timestamp = time.time()
        self.iterate = self._other_iterations
        return True

    def _other_iterations(self):
        time.sleep(self.delay)
        now = time.time()
        self.delta = now - self.timestamp
        self.timestamp = now
        self.i += 1
        if self.n <= 0 or self.i < self.n:
            return True
        self.iterate = self._no_loop
        return False

    def _no_loop(self):
        return False

    def __enter__(self):
        self.iterate = self._first_iteration
        return self

    def __exit__(self, type, value, traceback):
        self.i = -1
        self.iterate = self._no_loop


@define
class UdpConnection:
    host: str
    port: int
    timeout: float = 0.0
    _socket: Optional[socket.socket] = field(init=False, default=None, repr=False)

    @property
    def address(self) -> str:
        return f'{self.host}:{self.port}'

    def connect(self):
        if self._socket is None:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            if self.timeout > 0.0:
                # timeout mode instead of blocking mode
                self._socket.settimeout(self.timeout)
            try:
                self._socket.connect((self.host, self.port))
            except socket.timeout as e:
                self._socket.close()
                self._socket = None
                raise ConnectionError(e)

    def disconnect(self):
        if self._socket is not None:
            self._socket.shutdown(socket.SHUT_RDWR)
            self._socket.close()
            self._socket = None

    def send(self, msg):
        self._socket.send(msg)

    def receive(self, bytes=4096, encoding='utf-8'):
        msg = self._socket.recv(bytes)
        if encoding is not None:
            msg = msg.decode('utf-8')
        return msg

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, type, value, traceback):
        self.disconnect()
