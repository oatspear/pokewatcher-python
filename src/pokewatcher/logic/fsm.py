# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Any, Final

import logging

from attrs import define, field

from pokewatcher.data.structs import GameData
from pokewatcher.errors import StateMachineError

###############################################################################
# Constants
###############################################################################

logger: Final[logging.Logger] = logging.getLogger(__name__)

###############################################################################
# Game State Interface
###############################################################################


@define
class GameState:
    @property
    def name(self) -> str:
        name = type(self).__name__
        # if name.endswith('State'):
        #    name = name[:-5]
        return name

    @property
    def is_battle_state(self) -> bool:
        return False

    def inconsistent(self, label: str, value: Any):
        raise StateMachineError.inconsistent(self.name, label, value)


def transition(state: GameState, prev: Any, value: Any, data: GameData) -> GameState:
    # this is just a template for other transition functions
    logger.debug(f'on state input: {state.name} -> transition ({prev}, {value})')
    return state


###############################################################################
# State Machine Interface
###############################################################################


@define
class StateMachine:
    state: GameState = field(factory=GameState)

    def on_input(self, label: str, prev: Any, value: Any, data: GameData):
        logger.debug(f'on {label}: {prev} -> {value}')
        t = getattr(self.state, label)
        if t is None:
            # logger.debug(f'no state transition: {self.state.name} -> {label} ({prev}, {value})')
            raise StateMachineError.no_transition(self.state.name, label, value)
        new_state = t(prev, value, data)
        if new_state is not self.state:
            logger.info(f'state transition: {self.state.name} -> {new_state.name}')
        self.state = new_state
