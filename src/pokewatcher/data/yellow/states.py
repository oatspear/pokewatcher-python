# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Any, Final, Mapping

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
    is_game_started: bool = False

    @classmethod
    def new(cls, data: Mapping[str, Any]) -> GameState:
        return cls()

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
    @classmethod
    def new(cls, data: Mapping[str, Any]) -> GameState:
        return cls()

    def on_property_changed(self, prop: str, value: Any, data: Mapping[str, Any]) -> GameState:
        if prop == P_MAP:
            if value:
                super()._on_map_changed(value)
            else:
                self.is_overworld = False
        return self
