# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Any, Mapping, Optional

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
    def new(cls, data: Optional[Mapping[str, Any]] = None) -> GameState:
        return cls(
            'initial',
            data=data,
            is_game_started=False,
            is_overworld=False,
            is_battle=False,
        )

    def on_property_changed(self, prop: str, value: Any) -> GameState:
        if prop == 'playerId':
            pass  # TODO
        return self
