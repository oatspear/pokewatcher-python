# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Any, Final, Mapping

import logging

import pokewatcher.data.constants as game_data
from pokewatcher.data.gamehook import DataHandler
from pokewatcher.data.structs import GameData

# import pokewatcher.data.yellow.constants as yellow
from pokewatcher.logic.fsm import StateMachine

###############################################################################
# Constants
###############################################################################

logger: Final[logging.Logger] = logging.getLogger(__name__)

PROPERTIES: Final[Mapping[str, Mapping[str, Any]]] = {}

###############################################################################
# Interface
###############################################################################


def load_data_handler(data: GameData, fsm: StateMachine) -> DataHandler:
    handler = DataHandler(data, fsm)
    for prop, metadata in PROPERTIES.items():
        handler.configure_property(prop, metadata)
    return handler
