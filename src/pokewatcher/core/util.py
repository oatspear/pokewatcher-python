# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Any, Callable, Optional

import socket
import time

from attrs import define, field

###############################################################################
# Useful Functions
###############################################################################


def noop(*args, **kwargs):
    pass


def const_false(*args, **kwargs):
    return False


def identity(x: Any) -> Any:
    return x


###############################################################################
# Data Handling
###############################################################################


@define
class Attribute:
    obj: Any
    name: str
    path: str = ''

    def __attrs_post_init__(self):
        if not self.path:
            self.path = self.name

    def get(self) -> Any:
        return getattr(self.obj, self.name)

    def set(self, value: Any) -> None:
        setattr(self.obj, self.name, value)

    @classmethod
    def of(cls, obj: Any, path: str) -> 'Attribute':
        parts = path.split('.')
        for attr in parts[:-1]:
            obj = getattr(obj, attr)
        assert hasattr(obj, parts[-1])
        return cls(obj, parts[-1], path=path)


# @define
# class EventfulData(Generic[T]):
#     data: T
#     on_change: Event = field(factory=Event)
#
#     def get_leaf(self, path: str) -> Attribute:
#         return Attribute.leaf(self.data, path)
#
#     def get(self, path: str) -> Any:
#         return Attribute.leaf(self.data, path).get()
#
#     def set(self, path: str, value: Any, emit: bool = True) -> None:
#         attr = Attribute.leaf(self.data, path)
#         prev = attr.get()
#         attr.set(value)
#         if emit:
#             self.on_change.emit(path, prev, value, self.data)
#
#     def setter(self, path: str, emit: bool = True) -> Callable:
#         attr = Attribute.leaf(self.data, path)
#         return self._setter(path, attr, emit)
#
#     def _setter(self, path: str, attr: Attribute, emit: bool) -> Callable:
#         def set_and_emit(value: Any):
#             prev = attr.get()
#             attr.set(value)
#             if emit:
#                 self.on_change.emit(path, prev, value, self.data)
#         return set_and_emit


###############################################################################
# Time Management
###############################################################################


@define
class TimeRecord:
    hours: int = 0
    minutes: int = 0
    seconds: int = 0
    millis: int = 0

    @classmethod
    def from_float_seconds(cls, secs: float) -> 'TimeRecord':
        # milliseconds
        i = int(secs)
        ms = int((secs - i) * 1000)

        # hours
        h = i // 3600
        i %= 3600

        # minutes, seconds
        m = i // 60
        s = i % 60

        return cls(hours=h, minutes=m, seconds=s, millis=ms)

    @classmethod
    def converter(cls, value: Any) -> 'TimeRecord':
        if isinstance(value, TimeRecord):
            return cls(
                hours=value.hours,
                minutes=value.minutes,
                seconds=value.seconds,
                millis=value.millis,
            )
        if isinstance(value, float):
            return cls.from_float_seconds(value)
        if isinstance(value, int):
            return cls.from_float_seconds(float(value))
        raise TypeError(f'expected TimeRecord, int or float, got {type(value)}')

    def copy(self) -> 'TimeRecord':
        return TimeRecord(
            hours=self.hours,
            minutes=self.minutes,
            seconds=self.seconds,
            millis=self.millis,
        )

    def formatted(self, zeroes: bool = True, millis: bool = True) -> str:
        t = f'{self.seconds:02}' if not millis else f'{self.seconds:02}.{self.millis:03}'
        if not zeroes:
            if self.hours == 0:
                return t if self.minutes == 0 else f'{self.minutes:02}:{t}'
        return f'{self.hours:02}:{self.minutes:02}:{t}'

    def __str__(self) -> str:
        return self.formatted(zeroes=True, millis=True)

    def __sub__(self, other: Any) -> 'TimeRecord':
        if not isinstance(other, TimeRecord):
            raise TypeError(f'expected TimeRecord, got {type(other)}')
        h = self.hours - other.hours
        m = self.minutes - other.minutes
        s = self.seconds - other.seconds
        ms = self.millis - other.millis
        if ms < 0:
            ms += 1000
            s -= 1
        if s < 0:
            s += 60
            m -= 1
        if m < 0:
            m += 60
            h -= 1
        return TimeRecord(hours=h, minutes=m, seconds=s, millis=ms)


@define
class TimeInterval:
    start: TimeRecord = field(factory=time.time, converter=TimeRecord.converter)
    end: TimeRecord = field(factory=time.time, converter=TimeRecord.converter)

    @property
    def duration(self) -> TimeRecord:
        return self.end - self.start

    def copy(self) -> 'TimeInterval':
        return TimeInterval(start=self.start.copy(), end=self.end.copy())

    def __str__(self) -> str:
        return str(self.duration)


@define
class SimpleClock:
    time_start: TimeRecord = field(factory=time.time, converter=TimeRecord.converter)

    def reset_start_time(self):
        self.time_start = TimeRecord.from_float_seconds(time.time())

    def get_current_time(self) -> TimeRecord:
        return TimeRecord.from_float_seconds(time.time()) - self.time_start

    def get_elapsed_time(self) -> TimeInterval:
        return TimeInterval(start=self.time_start, end=time.time())


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


###############################################################################
# Networking
###############################################################################


@define
class SocketConnection:
    host: str
    port: int
    timeout: float = 0.0
    _socket: Optional[socket.socket] = field(init=False, default=None, repr=False)

    @property
    def address(self) -> str:
        return f'{self.host}:{self.port}'

    @property
    def protocol(self) -> socket.SocketKind:
        raise NotImplementedError()

    def connect(self):
        if self._socket is None:
            self._socket = socket.socket(socket.AF_INET, self.protocol)
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


@define
class UdpConnection(SocketConnection):
    @property
    def protocol(self) -> socket.SocketKind:
        return socket.SOCK_DGRAM


@define
class TcpConnection(SocketConnection):
    @property
    def protocol(self) -> socket.SocketKind:
        return socket.SOCK_STREAM
