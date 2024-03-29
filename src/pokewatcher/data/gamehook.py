# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Any, Callable, Final, Iterable, List, Mapping, Optional

import logging

from attrs import define, field

from pokewatcher.core.util import Attribute, identity, noop
from pokewatcher.data.structs import GameData
from pokewatcher.events import on_data_changed
from pokewatcher.logic.fsm import StateMachine

###############################################################################
# Constants
###############################################################################

logger: Final[logging.Logger] = logging.getLogger(__name__)

TRANSFORMS: Final[Mapping[str, Callable]] = {
    'bool': bool,
    'int': int,
    'float': float,
    'string': str,
}


def _pp_prefix(arg: Any) -> Callable:
    return lambda value: f'{arg}{value}'


def _pp_suffix(arg: Any) -> Callable:
    return lambda value: f'{value}{arg}'


def _pp_add(arg: Any) -> Callable:
    return lambda value: value + arg


def _pp_subtract(arg: Any) -> Callable:
    return lambda value: value - arg


def _pp_multiply(arg: Any) -> Callable:
    return lambda value: value * arg


def _pp_divide(arg: Any) -> Callable:
    return lambda value: value / arg


def _pp_modulo(arg: Any) -> Callable:
    return lambda value: value % arg


def _pp_negate() -> Callable:
    return lambda value: not value


PROCESSORS: Final[Mapping[str, Callable]] = {
    'prefix': _pp_prefix,
    'suffix': _pp_suffix,
    'add': _pp_add,
    'subtract': _pp_subtract,
    'multiply': _pp_multiply,
    'divide': _pp_divide,
    'modulo': _pp_modulo,
    'negate': _pp_negate,
}


###############################################################################
# Interface
###############################################################################


@define
class GameHookProperty:
    name: str
    previous: Any = None
    default: Any = None
    uses_bytes: bool = False
    is_little_endian: bool = True
    attribute: Optional[Attribute] = None
    label: Optional[str] = None
    converter: Callable = identity
    processors: List[Callable] = field(factory=list)
    handler: Callable = noop


@define
class DataHandler:
    data: GameData
    fsm: StateMachine
    properties: Mapping[str, GameHookProperty] = field(init=False, factory=dict)

    def on_property_changed(self, prop: str, value: Any, byte_values: List[int]):
        ghp = self.properties.get(prop)
        if ghp is not None:
            if value is None:
                value = ghp.default
            # bytes or glossary value?
            if ghp.uses_bytes:
                endianess = 'little' if ghp.is_little_endian else 'big'
                value = int.from_bytes(byte_values, byteorder=endianess)
            # convert data to something else
            if value is not None:
                value = ghp.converter(value)
            if value is not None:
                for processor in ghp.processors:
                    value = processor(value)
            # store it in GameData
            if ghp.attribute is not None:
                ghp.previous = ghp.attribute.get()
                ghp.attribute.set(value)
                on_data_changed.emit(ghp.attribute.path, ghp.previous, value)
            # additional side effects
            ghp.handler(value, self.data)
            # feed to StateMachine
            if ghp.label:
                self.fsm.on_input(ghp.label, ghp.previous, value, self.data)
            # store previous value for posterity
            ghp.previous = value

    def ensure_property(self, prop: str) -> GameHookProperty:
        ghp = self.properties.get(prop)
        if ghp is None:
            ghp = GameHookProperty(prop)
            self.properties[prop] = ghp
        return ghp

    def configure_property(self, prop: str, metadata: Mapping[str, Any]):
        use_bytes = bool(metadata.get('bytes', False))
        if use_bytes:
            self.use_bytes(prop, is_little_endian=metadata.get('little_endian', False))

        data_type = metadata.get('type', '')
        key = metadata.get('key')
        self.convert(prop, data_type, key=key)

        for pp in metadata.get('processors', ()):
            func = pp[0]
            args = pp[1:]
            self.process(prop, func, args)

        attr = metadata.get('store')
        default = metadata.get('default')
        if attr:
            self.store(prop, attr, default=default, data_type=data_type)

        label = metadata.get('label')
        if label is not None:
            self.transition(prop, label)

    def use_bytes(self, prop: str, is_little_endian=False):
        logger.debug(f'use bytes: {prop}')
        ghp = self.ensure_property(prop)
        ghp.uses_bytes = True
        ghp.is_little_endian = is_little_endian

    def convert(self, prop: str, data_type: str, key: Optional[str] = None):
        logger.debug(f'convert data: {prop} -> {data_type}[{repr(key)}]')
        ghp = self.ensure_property(prop)
        f = TRANSFORMS.get(data_type, identity)
        if key is None:
            ghp.converter = f
        else:
            ghp.converter = lambda d: f(d[key])

    def process(self, prop: str, func: str, args: Iterable[Any]):
        logger.debug(f'process data: {prop} -> {func}{args}')
        ghp = self.ensure_property(prop)
        f = PROCESSORS.get(func)
        if f is None:
            logger.error(f'{prop}: processor {func} does not exist')
        else:
            try:
                processor = f(*args)
                ghp.processors.append(processor)
            except TypeError as e:
                logger.error(f'{prop}: processor {func}: {e}')

    def store(self, prop: str, path: str, default: Any = None, data_type: str = ''):
        logger.debug(f'data store: {prop} -> {path}')
        ghp = self.ensure_property(prop)
        ghp.attribute = Attribute.of(self.data, path)
        ghp.previous = ghp.attribute.get()
        if default is not None:
            ghp.default = default
            ghp.attribute.set(default)
        elif prop.startswith('custom'):
            if data_type == 'int':
                ghp.default = 0
                ghp.attribute.set(0)
            elif data_type == 'bool':
                ghp.default = False
                ghp.attribute.set(False)
            elif data_type == 'string':
                ghp.default = ''
                ghp.attribute.set('')
            elif data_type == 'float':
                ghp.default = 0.0
                ghp.attribute.set(0.0)

    def transition(self, prop: str, label: str):
        logger.debug(f'transition label: {prop} -> {label}')
        ghp = self.ensure_property(prop)
        ghp.label = label

    def do(self, prop: str, handler: Callable):
        logger.debug(f'handle {prop}: {handler}')
        ghp = self.ensure_property(prop)
        if ghp.handler is noop:
            ghp.handler = handler
        else:
            ghp.handler = self._chain(ghp.handler, handler)

    def _chain(self, f: Callable, g: Callable) -> Callable:
        def gof(value: Any, data: GameData):
            f(value, data)
            g(value, data)

        return gof
