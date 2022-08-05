# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Any, Final, Mapping

import logging

from attrs import define

import pokewatcher.events as events

###############################################################################
# Constants
###############################################################################

logger: Final = logging.getLogger(__name__)

###############################################################################
# Interface
###############################################################################


@define
class GameState:
    name: str = ''
    is_game_started: bool = True
    is_overworld: bool = False
    is_battle: bool = False

    def __attrs_post_init__(self):
        if not self.name:
            self.name = type(self).__name__
            if self.name.endswith('State'):
                self.name = self.name[:-5]

    def on_property_changed(self, prop: str, value: Any, data: Mapping[str, Any]) -> 'GameState':
        return self

    def _on_map_changed(self, value: str, prev: str):
        logger.debug(f'map changed from {prev} to {value}')
        self.is_overworld = True
        events.on_map_changed.emit(value)
