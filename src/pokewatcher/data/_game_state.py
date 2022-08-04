# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Any, Mapping

import logging

import pokewatcher.events as events

###############################################################################
# Constants
###############################################################################

logger: Final = logging.getLogger(__name__)

###############################################################################
# Interface
###############################################################################


class GameState:
    @property
    def name(self) -> str:
        name = type(self).name
        if name.endswith('State'):
            name = name[:-5]
        return name

    @property
    def is_game_started(self) -> bool:
        return True

    @property
    def is_overworld(self) -> bool:
        return False

    @property
    def is_battle(self) -> bool:
        return False

    def on_property_changed(self, prop: str, value: Any, data: Mapping[str, Any]) -> 'GameState':
        return self

    def _on_map_changed(self, value: str, prev: str):
        logger.debug(f'map changed from {prev} to {value}')
        events.on_map_changed.emit(value)
