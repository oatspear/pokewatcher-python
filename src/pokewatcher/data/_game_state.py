# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Any, Mapping

import logging

from attrs import define, field

###############################################################################
# Constants
###############################################################################

logger: Final = logging.getLogger(__name__)

###############################################################################
# Interface
###############################################################################


@define
class GameState:
    name: str
    data: Mapping[str, Any] = field(factory=dict)
    is_game_started: bool = True
    is_overworld: bool = False
    is_battle: bool = False

    def on_property_changed(self, prop: str, value: Any) -> 'GameState':
        return self
