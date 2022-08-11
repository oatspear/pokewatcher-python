# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Any, Callable, Final, Mapping

import logging

from attrs import define, field

from pokewatcher.core.util import Attribute, noop
from pokewatcher.data.structs import GameData
from pokewatcher.events import on_data_changed

###############################################################################
# Constants
###############################################################################

logger: Final[logging.Logger] = logging.getLogger(__name__)

###############################################################################
# Interface
###############################################################################


@define
class BaseDataHandler:
    data: GameData
    handlers: Mapping[str, Callable] = field(factory=dict)

    def on_property_changed(self, prop: str, prev: Any, value: Any, mapper: Mapping[str, Any]):
        handler = self.handlers.get(prop, noop)
        handler(prev, value, mapper)

    def store(self, prop: str, path: str):
        logger.debug(f'data store: {prop} -> {path}')
        attr = Attribute.of(self.data, path)
        self.do(prop, self._lazy_set_and_emit(path, attr))

    def do(self, prop: str, handler: Callable):
        logger.debug(f'handle {prop}: {handler}')
        f = self.handlers.get(prop)
        if f is not None:
            handler = self._chain(f, handler)
        self.handlers[prop] = handler

    def _chain(self, f: Callable, g: Callable) -> Callable:
        def gof(prev: Any, value: Any, mapper: Mapping[str, Any]):
            f(prev, value, mapper)
            g(prev, value, mapper)
        return gof

    def _lazy_set(self, obj: Any, attr: Attribute) -> Callable:
        def just_set(prev: Any, value: Any, mapper: Mapping[str, Any]):
            attr.set(value)
        return just_set

    def _lazy_set_and_emit(self, path: str, attr: Attribute) -> Callable:
        def set_and_emit(prev: Any, value: Any, mapper: Mapping[str, Any]):
            # prev = attr.get()
            attr.set(value)
            on_data_changed.emit(path, prev, value)
        return set_and_emit
