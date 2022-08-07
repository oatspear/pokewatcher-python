# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Any, Callable, Final, Mapping

import logging

from attrs import define, field

from pokewatcher.core.util import noop
import pokewatcher.events as events

###############################################################################
# Constants
###############################################################################

logger: Final[logging.Logger] = logging.getLogger(__name__)

###############################################################################
# Interface
###############################################################################


@define
class BaseDataHandler:
    handlers: Mapping[str, Callable] = field(factory=dict)

    def on_property_changed(self, prop: str, prev: Any, value: Any, data: Mapping[str, Any]):
        handler = self.handlers.get(prop, noop)
        handler(prev, value, data)

    def on_player_id_changed(self, prev: int, value: int, data: Mapping[str, Any]):
        logger.debug(f'player ID changed from {prev} to {value}')
        if value == 0:
            events.on_reset.emit()
        elif prev == 0:
            if self.is_game_started:
                events.on_continue.emit()
            else:
                events.on_new_game.emit()

    def store_int(self, prop: str):
        self.handlers[prop] = convert_to_int(prop)

    def store_bool(self, prop: str):
        self.handlers[prop] = convert_to_bool(prop)

    def store_key(self, prop: str, key: str):
        self.handlers[prop] = extract_key(prop, key)

    def emit_event(self, prop: str, event: events.Event):
        self.handlers[prop] = event.emit


def convert_to_int(prop: str):
    def setter(prev: Any, value: Any, data: Mapping[str, Any]):
        data[prop] = int(value)
    return setter


def convert_to_bool(prop: str):
    def setter(prev: Any, value: Any, data: Mapping[str, Any]):
        data[prop] = bool(value)
    return setter


def extract_key(prop: str, key: str):
    def setter(prev: Any, value: Mapping[str, Any], data: Mapping[str, Any]):
        data[prop] = value[key]
    return setter
