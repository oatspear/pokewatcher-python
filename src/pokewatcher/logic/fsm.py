# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Any, Final

import logging

from attrs import define

from pokewatcher.data.structs import BattleData, GameData
# from pokewatcher.errors import StateMachineError
import pokewatcher.events as events

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

    def enter(self, *args, **kwargs):
        logger.debug(f'enter state: {self.name}')
        # set event handlers, etc.
        return

    def exit(self):
        logger.debug(f'exit state: {self.name}')
        # remove event handlers, etc.
        return

    def transition(self, prev: Any, value: Any, data: GameData) -> 'GameState':
        # this is just a template for other transition functions
        logger.debug(f'on state input: {self.name} -> transition ({prev}, {value})')
        return self


###############################################################################
# State Machine Interface
###############################################################################


@define
class StateMachine:
    state: GameState
    data: GameData

    def on_input(self, label: str, prev: Any, value: Any):
        logger.debug(f'on {label}: {prev} -> {value}')
        transition = getattr(self.state, label)
        if transition is None:
            logger.debug(f'no state transition: {self.state.name} -> {label} ({prev}, {value})')
        else:
            new_state = transition(prev, value, self.data)
            if new_state is not self.state:
                logger.info(f'state transition: {self.state.name} -> {new_state.name}')
            self.state = new_state
