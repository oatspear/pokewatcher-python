# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Any, Callable, Final, Mapping, Optional

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

###############################################################################
# Interface
###############################################################################


@define
class GameHookProperty:
    name: str
    previous: Any = None
    uses_bytes: bool = False
    attribute: Optional[Attribute] = None
    label: Optional[str] = None
    converter: Callable = identity
    handler: Callable = noop


@define
class DataHandler:
    data: GameData
    fsm: StateMachine
    properties: Mapping[str, GameHookProperty] = field(init=False, factory=dict)

    def on_property_changed(self, prop: str, value: Any, byte_value: int):
        ghp = self.properties.get(prop)
        if ghp is not None:
            # bytes or glossary value?
            v = byte_value if ghp.uses_bytes else value
            # convert data to something else
            v = ghp.converter(v)
            # store it in GameData
            if ghp.attribute is not None:
                prev = ghp.attribute.get()
                ghp.attribute.set(value)
                on_data_changed.emit(ghp.attribute.path, prev, v)
            # additional side effects
            ghp.handler(v, self.data)
            # feed to StateMachine
            if ghp.label:
                self.fsm.on_input(ghp.label, ghp.previous, v, self.data)
            # store previous value for posterity
            ghp.previous = v

    def ensure_property(self, prop: str) -> GameHookProperty:
        ghp = self.properties.get(prop)
        if ghp is None:
            ghp = GameHookProperty(prop)
            self.properties[prop] = ghp
        return ghp

    def configure_property(self, prop: str, metadata: Mapping[str, Any]):
        use_bytes = bool(metadata.get('bytes', False))
        if use_bytes:
            self.use_bytes(prop)

        data_type = metadata.get('type', '')
        key = metadata.get('key')
        self.convert(prop, data_type, key=key)

        attr = metadata.get('store')
        if attr:
            self.store(prop, attr)

        label = metadata.get('label')
        if label is not None:
            self.transition(prop, label)

    def use_bytes(self, prop: str):
        logger.debug(f'use bytes: {prop}')
        ghp = self.ensure_property(prop)
        ghp.uses_bytes = True

    def convert(self, prop: str, data_type: str, key: Optional[str] = None):
        logger.debug(f'convert data: {prop} -> {data_type}[{repr(key)}]')
        ghp = self.ensure_property(prop)
        f = TRANSFORMS.get(data_type, identity)
        if key is None:
            ghp.converter = f
        else:
            ghp.converter = lambda d: f(d[key])

    def store(self, prop: str, path: str):
        logger.debug(f'data store: {prop} -> {path}')
        ghp = self.ensure_property(prop)
        ghp.attribute = Attribute.of(self.data, path)

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
