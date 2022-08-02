# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Any

import logging

from attrs import define

from pokewatcher.data._game_state import GameState

###############################################################################
# Constants
###############################################################################

logger: Final = logging.getLogger(__name__)

###############################################################################
# Interface
###############################################################################


@define
class InitialState(GameState):
    @classmethod
    def new(cls) -> GameState:
        return cls(
            'initial',
            is_game_started=False,
            is_overworld=False,
            is_battle=False,
        )

    def on_property_changed(self, prop: str, value: Any) -> GameState:
        return self
