# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Any, Mapping

import logging

from attrs import define

from pokewatcher.data._game_state import GameState
import pokewatcher.events as events

###############################################################################
# Constants
###############################################################################

logger: Final = logging.getLogger(__name__)

P_PLAYER_ID = 'playerId'
P_MAP = 'overworld.map'

###############################################################################
# Interface
###############################################################################


@define
class InitialState(GameState):
    @classmethod
    def new(cls, data: Mapping[str, Any]) -> GameState:
        return cls()

    @property
    def is_game_started(self) -> bool:
        return False

    def on_property_changed(self, prop: str, value: Any, data: Mapping[str, Any]) -> GameState:
        if prop == P_PLAYER_ID:
            prev = data[P_PLAYER_ID]
            if value > 0 and prev == 0:
                logger.info('starting a new game')
                events.on_new_game.emit()
                assert not data[P_MAP]
                return BeforeReceivingStarterState.new(data)
        return self


@define
class BeforeReceivingStarterState(GameState):
    _in_overworld: bool = False

    @classmethod
    def new(cls, data: Mapping[str, Any]) -> GameState:
        return cls()

    @property
    def is_overworld(self) -> bool:
        return self._in_overworld

    def on_property_changed(self, prop: str, value: Any, data: Mapping[str, Any]) -> GameState:
        if prop == P_MAP:
            if value:
                self._in_overworld = True
                super()._on_map_changed(value)
            else:
                self._in_overworld = False
        return self
