# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Callable, Final

###############################################################################
# Event Class
###############################################################################

# Credit to StackOverflow user Longpoke. See:
# https://stackoverflow.com/a/2022629


class Event(list):
    """Event subscription.

    A list of callable objects. Calling an instance of this will cause a
    call to each item in the list in ascending order by index.

    Example Usage:
    >>> def f(x):
    ...     print 'f(%s)' % x
    >>> def g(x):
    ...     print 'g(%s)' % x
    >>> e = Event()
    >>> e()
    >>> e.append(f)
    >>> e(123)
    f(123)
    >>> e.remove(f)
    >>> e()
    >>> e += (f, g)
    >>> e(10)
    f(10)
    g(10)
    >>> del e[0]
    >>> e(2)
    g(2)
    """

    def emit(self, *args, **kwargs) -> None:
        for f in self:
            f(*args, **kwargs)

    def watch(self, callback: Callable) -> None:
        return self.append(callback)

    def forget(self, callback: Callable) -> None:
        return self.remove(callback)

    def __call__(self, *args, **kwargs) -> None:
        for f in self:
            f(*args, **kwargs)

    def __repr__(self) -> str:
        return f'Event({list.__repr__(self)})'


###############################################################################
# Global Interface
###############################################################################

on_new_game: Final[Event] = Event()
