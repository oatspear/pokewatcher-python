# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Callable, Final, Generic, TypeVar

import logging

from attrs import field, fields, frozen

from pokewatcher.events import Event

###############################################################################
# Constants
###############################################################################

logger: Final[logging.Logger] = logging.getLogger(__name__)

T: Final[TypeVar] = TypeVar('T')

###############################################################################
# Atomic Variables
###############################################################################


@frozen
class Variable(Generic[T]):
    value: T
    on_change: Event = field(
        init=False,
        factory=lambda: Event(name='on_change'),
        repr=False,
        eq=False,
        order=False,
    )

    def get(self) -> T:
        return self.value

    def set(self, value: T) -> None:
        prev = self.value
        object.__setattr__(self, 'value', value)
        self.on_change.emit(prev, value)

    def set_silent(self, value: T) -> None:
        object.__setattr__(self, 'value', value)

    def __str__(self) -> str:
        return str(self.value)

    def __lt__(self, other):
        return self.value < other

    def __le__(self, other):
        return self.value <= other

    def __gt__(self, other):
        return self.value > other

    def __ge__(self, other):
        return self.value >= other


def varfactory(value: T) -> Variable[T]:
    return lambda: Variable(value)


@frozen
class VarInt(Variable[int]):
    @classmethod
    def zero(cls) -> 'VarInt':
        return cls(0)

    @classmethod
    def one(cls) -> 'VarInt':
        return cls(1)

    @classmethod
    def minus_one(cls) -> 'VarInt':
        return cls(-1)


@frozen
class VarBool(Variable[bool]):
    @classmethod
    def true(cls) -> 'VarBool':
        return cls(True)

    @classmethod
    def false(cls) -> 'VarBool':
        return cls(False)


@frozen
class VarString(Variable[str]):
    @classmethod
    def empty(cls) -> 'VarString':
        return cls('')


###############################################################################
# Composite Objects
###############################################################################


@frozen
class Composite:
    on_change: Event = field(
        init=False,
        factory=lambda: Event(name='on_change'),
        repr=False,
        eq=False,
        order=False,
    )

    def __attrs_post_init__(self):
        attrs = fields(self.__class__)
        for a in attrs:
            v = getattr(self, a.name)
            if isinstance(v, Variable):
                v.on_change.watch(self._propagate_atomic(a.name))
            elif isinstance(v, Composite):
                v.on_change.watch(self._propagate_composite(a.name))

    def _propagate_atomic(self, name: str) -> Callable:
        def cb(*args, **kwargs):
            self.on_change.emit(name, *args, **kwargs)
        return cb

    def _propagate_composite(self, prefix: str) -> Callable:
        def cb(name, *args, **kwargs):
            self.on_change.emit(f'{prefix}.{name}', *args, **kwargs)
        return cb
