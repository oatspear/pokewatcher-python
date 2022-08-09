# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Callable, Final, Iterable, List

from attrs import define, field

###############################################################################
# Event Class
###############################################################################

# Based on solution by StackOverflow user Longpoke. See:
# https://stackoverflow.com/a/2022629


@define
class Event:
    """Event subscription.

    A list of callable objects. Calling an instance of this will cause a
    call to each item in the list in ascending order by index.

    Example Usage:
    >>> def f(x):
    ...     print(f'f({x})')
    >>> def g(x):
    ...     print(f'g({x})')
    >>> e = Event()
    >>> e()
    >>> e.watch(f)
    >>> e(123)
    f(123)
    >>> e.forget(f)
    >>> e()
    >>> e += (f, g)
    >>> e(10)
    f(10)
    g(10)
    >>> del e.callbacks[0]
    >>> e(2)
    g(2)
    """

    name: str = 'Event'
    callbacks: List[Callable] = field(factory=list)
    count: int = field(init=False, default=0, repr=False)

    def emit(self, *args, **kwargs) -> None:
        self.count += 1
        for f in self.callbacks:
            f(*args, **kwargs)

    def watch(self, callback: Callable) -> None:
        return self.callbacks.append(callback)

    def append(self, callback: Callable) -> None:
        return self.callbacks.append(callback)

    def forget(self, callback: Callable) -> None:
        return self.callbacks.remove(callback)

    def remove(self, callback: Callable) -> None:
        return self.callbacks.remove(callback)

    def clear(self) -> None:
        return self.callbacks.clear()

    def __call__(self, *args, **kwargs) -> None:
        return self.emit(*args, **kwargs)

    def __iadd__(self, callbacks: Iterable[Callable]) -> 'Event':
        self.callbacks += callbacks
        return self


###############################################################################
# Global Interface
###############################################################################

on_data_changed: Final[Event] = Event(name='on_data_changed')

on_new_game: Final[Event] = Event(name='on_new_game')
on_reset: Final[Event] = Event(name='on_reset')
on_continue: Final[Event] = Event(name='on_continue')
on_save_game: Final[Event] = Event(name='on_save_game')

on_map_changed: Final[Event] = Event(name='on_map_changed')
