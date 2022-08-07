# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Any, Final, Mapping, Optional

import logging

from attrs import define

from pokewatcher.data.states import GameState

###############################################################################
# Constants
###############################################################################

logger: Final = logging.getLogger(__name__)

###############################################################################
# Interface
###############################################################################


@define
class InitialState(GameState):
    is_game_started: bool = False

    @classmethod
    def new(cls, data: Mapping[str, Any]) -> GameState:
        return cls()

    def on_property_changed(self, prop: str, value: Any) -> GameState:
        return self
