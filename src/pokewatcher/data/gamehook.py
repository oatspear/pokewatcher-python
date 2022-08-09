# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Any, Callable, Final, Mapping, Tuple

import logging

from attrs import define, field

from pokewatcher.core.util import Attribute, identity, noop
from pokewatcher.data.structs import GameData
from pokewatcher.events import Event

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
class BaseDataHandler:
    data: GameData
    on_data_changed: Event = field(factory=lambda: Event('on_data_changed'))
    handlers: Mapping[str, Callable] = field(factory=dict)
    transforms: Mapping[str, Callable] = field(factory=dict)

    def on_property_changed(self, prop: str, prev: Any, value: Any, mapper: Mapping[str, Any]):
        handler = self.handlers.get(prop, noop)
        handler(prev, value, mapper)

    def store(self, prop: str, path: str, emit: bool = True):
        logger.debug(f'data store: {prop} -> {path} (emit: {emit})')
        attr = Attribute.of(self.data, path)
        if emit:
            self.handlers[prop] = self._lazy_set_and_emit(path, obj, attr)
        else:
            self.handlers[prop] = self._lazy_set(obj, attr)

    def _lazy_set(self, obj: Any, attr: str) -> Callable:
        def just_set(prev: Any, value: Any, mapper: Mapping[str, Any]):
            # prev = attr.get()
            attr.set(value)
        return just_set

    def _lazy_set_and_emit(self, path: str, attr: Attribute) -> Callable:
        def set_and_emit(prev: Any, value: Any, mapper: Mapping[str, Any]):
            # prev = attr.get()
            attr.set(value)
            self.on_data_changed.emit(path, prev, value, self.data)
        return set_and_emit

    def setup(self, settings: Mapping[str, Any]):
        for prop, conf in settings['properties'].items():
            data_type = conf.get('data_type', '')
            key = conf.get('key', '')
            self.transforms[prop] = get_transform(data_type, key)


def get_transform(data_type: str, key: str):
    t = TRANSFORMS.get(data_type, identity)
    if key:
        return lambda x: t(x[key])
    return lambda x: t(x)
