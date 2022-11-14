# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Any, Final

import logging

from attrs import define, field

from pokewatcher.data.structs import GameData
from pokewatcher.data.emerald.constants import (
    BATTLE_TYPE_LOST,
    BATTLE_TYPE_NONE,
    BATTLE_TYPE_TRAINER,
    BATTLE_TYPE_WILD,
    DEFAULT_PLAYER_NAME,
    JOY_MASK_ALL,
    JOY_MASK_NONE,
    MENU_ITEM_CONTINUE,
    MENU_ITEM_NEW_GAME,
    SFX_SAVE_FILE,
    TRAINER_CLASS_CHAMPION,
)
import pokewatcher.events as events
from pokewatcher.logic.fsm import GameState, transition

###############################################################################
# Constants
###############################################################################

logger: Final[logging.Logger] = logging.getLogger(__name__)

###############################################################################
# Interface
###############################################################################
