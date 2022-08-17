# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Any, Final

import logging

from attrs import define

from pokewatcher.data.structs import GameData

# from pokewatcher.data.yellow.constants import (
#     BATTLE_TYPE_LOST,
#     BATTLE_TYPE_NONE,
#     BATTLE_TYPE_TRAINER,
#     BATTLE_TYPE_WILD,
#     DEFAULT_PLAYER_NAME,
#     SFX_SAVE_FILE,
# )
import pokewatcher.events as events
from pokewatcher.logic.fsm import GameState, transition

###############################################################################
# Constants
###############################################################################

logger: Final[logging.Logger] = logging.getLogger(__name__)

###############################################################################
# Interface
###############################################################################


class CrystalState(GameState):
    wPlayerID = transition  # noqa: N815
    wPlayerName = transition  # noqa: N815
    wIsInBattle = transition  # noqa: N815
    wChannelSoundIDs_5 = transition  # noqa: N815
    wLowHealthAlarmDisabled = transition  # noqa: N815


@define
class Initial(CrystalState):
    def wPlayerName(self, prev: str, value: str, _data: GameData) -> GameState:  # noqa: N815
        logger.debug(f'player name changed from {prev!r} to {value!r}')
        # if value != DEFAULT_PLAYER_NAME:
        #     logger.info('found saved game')
        #     return MainMenu()
        return self

    def wPlayerID(self, prev: int, value: int, _data: GameData) -> GameState:  # noqa: N815
        logger.debug(f'player ID changed from {prev} to {value}')
        # if value != 0 and prev == 0:
        #     logger.info('starting a new game')
        #     events.on_new_game.emit()
        #     return InOverworld()
        return self
