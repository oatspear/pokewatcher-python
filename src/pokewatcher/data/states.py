# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Any, Mapping

import logging

from pokewatcher.data._game_state import GameState

###############################################################################
# Constants
###############################################################################

logger: Final = logging.getLogger(__name__)

###############################################################################
# Interface
###############################################################################


def initial_state(version: str, data: Mapping[str, Any]) -> GameState:
    logger.debug(f'initial state for {version} version')
    if 'yellow' in version:
        from pokewatcher.data.yellow.states import InitialState
        return InitialState.new(data=data)
    if 'crystal' in version:
        from pokewatcher.data.crystal.states import InitialState
        return InitialState.new(data=data)
    raise ValueError(f'Unknown game version: {version}')
