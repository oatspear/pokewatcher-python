# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Any, Final, Mapping, Optional

import logging

from attrs import define, field

from pokewatcher.core.gamehook import GameHookBridge, GameHookError
from pokewatcher.core.retroarch import RetroArchBridge
from pokewatcher.data.structs import GameData
from pokewatcher.logic.fsm import GameState, StateMachine

###############################################################################
# Constants
###############################################################################

logger: Final[logging.Logger] = logging.getLogger(__name__)

###############################################################################
# Interface
###############################################################################


@define
class GameInterface:
    data: GameData = field(factory=GameData)
    retroarch: RetroArchBridge = field(factory=RetroArchBridge)
    gamehook: GameHookBridge = field(factory=GameHookBridge)
    fsm: StateMachine = field(init=False, factory=StateMachine)

    @property
    def rom(self) -> Optional[str]:
        return self.retroarch.rom

    @property
    def version(self) -> Optional[str]:
        return self.gamehook.game_name

    @property
    def state(self) -> GameState:
        return self.fsm.state

    def setup(self, settings: Mapping[str, Any]):
        logger.info('setting up infrastructure')
        retroarch = settings['retroarch']
        self.retroarch.setup(retroarch)
        gamehook = settings['gamehook']
        self.gamehook.setup(gamehook)

        self._load_data_handler(self.gamehook, self.data)

        self.state = initial_state(self.version.lower(), self.gamehook.mapper)
        # TODO load mapper data type transforms

    def start(self):
        logger.info('starting low-level components')
        self.retroarch.start()
        self.gamehook.start()

    def update(self, delta):
        # logger.debug('update')
        self.retroarch.update(delta)
        self.gamehook.update(delta)

    def cleanup(self):
        logger.info('cleaning up')
        self.gamehook.cleanup()
        self.retroarch.cleanup()

    def _load_data_handler(self):
        logger.info('setting up data handlers')

        version = self.gamehook.game_name.lower()
        if 'yellow' in version:
            from pokewatcher.data.yellow.gamehook import load_data_handler
            from pokewatcher.logic.yellow.fsm import Initial
        elif 'crystal' in version:
            from pokewatcher.data.crystal.gamehook import load_data_handler
            from pokewatcher.logic.crystal.fsm import Initial
        else:
            raise GameHookError.unknown_game(version)

        self.fsm.state = Initial()
        handler = load_data_handler(self.data, self.fsm)
        self.gamehook.on_change = handler.on_property_changed
        # handle initial data
        no_data = {}
        for prop, value in self.gamehook.mapper.items():
            handler.on_property_changed(prop, None, value, no_data)
