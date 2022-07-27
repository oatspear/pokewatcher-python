# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

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

    def emit(self, *args, **kwargs):
        for f in self:
            f(*args, **kwargs)

    def subscribe(self, callback):
        return self.append(callback)

    def unsubscribe(self, callback):
        return self.remove(callback)

    def __call__(self, *args, **kwargs):
        for f in self:
            f(*args, **kwargs)

    def __repr__(self):
        return f'Event({list.__repr__(self)})'


###############################################################################
# Global Interface
###############################################################################


class EventSystem:
    def __init__(self):
        pass

    def __getattr__(self, attr):
        e = Event()
        setattr(self, attr, e)
        return e


_events = EventSystem()

