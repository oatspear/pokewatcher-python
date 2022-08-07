# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Any, Final, Mapping

import logging

from attrs import define

from pokewatcher.data.fsm import GameState, OverworldState
import pokewatcher.events as events

###############################################################################
# Constants
###############################################################################

logger: Final[logging.Logger] = logging.getLogger(__name__)

P_PLAYER_ID = 'playerId'
P_MAP = 'overworld.map'

###############################################################################
# Interface
###############################################################################


@define
class InitialState(GameState):
    @property
    def is_game_started(self) -> bool:
        return False

    def on_property_changed(
        self,
        prop: str,
        prev: Any,
        value: Any,
        data: Mapping[str, Any],
    ) -> GameState:
        if prop == P_PLAYER_ID:
            return self.on_player_id_changed(prev, value)
        return self

    @property
    def state_on_new_game(self) -> 'GameState':
        return BeforeReceivingStarterState()


@define
class BeforeReceivingStarterState(GameState):
    def on_property_changed(self, prop: str, value: Any, data: Mapping[str, Any]) -> GameState:
        if prop == P_MAP:
            if value:
                super()._on_map_changed(value)
            else:
                self.is_overworld = False
        return self
