# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Any, Final, Mapping, Optional

import logging

from attrs import define, field

from pokewatcher.core.gamehook import GameHookBridge
from pokewatcher.core.retroarch import RetroArchBridge
from pokewatcher.data.structs import GameData
import pokewatcher.events as events

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

    @property
    def rom(self) -> Optional[str]:
        return self.retroarch.rom

    @property
    def version(self) -> Optional[str]:
        return self.gamehook.game_name

    @property
    def data(self) -> Mapping[str, Any]:
        return self.gamehook.mapper

    def setup(self, settings: Mapping[str, Any]):
        logger.info('setting up infrastructure')
        retroarch = settings['retroarch']
        self.retroarch.setup(retroarch)
        gamehook = settings['gamehook']
        self.gamehook.setup(gamehook)

        logger.info('setting up event handlers')
        events.on_new_game.watch(_log_event('starting a new game'))
        events.on_reset.watch(_log_event('game reset'))
        events.on_continue.watch(_log_event('continue previous game'))
        _load_data_handler(self.gamehook, self.data)

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

    def _on_property_changed(self, prop: str, prev: Any, value: Any):
        data = self.gamehook.mapper
        new_state = self.state.on_property_changed(prop, value, self.gamehook.mapper)
        if new_state is not self.state:
            logger.info(f'state transition: {self.state.name} -> {new_state.name}')
        self.state = new_state

    def _load_data_handler(self):
        version = self.gamehook.game_name.lower()
        if 'yellow' in version:
            from pokewatcher.data.yellow.gamehook import DataHandler
        elif 'crystal' in version:
            from pokewatcher.data.crystal.gamehook import DataHandler
        else:
            raise ValueError(f'Unknown game version: {version}')
        handler = DataHandler(self.data)
        # handler.setup({})
        self.gamehook.transforms = handler.transforms
        self.gamehook.on_change = handler.on_property_changed
        # handle initial data
        no_data = {}
        for prop, value in self.gamehook.mapper.items():
            handler.on_property_changed(prop, None, value, no_data)


###############################################################################
# Helper Functions
###############################################################################


def _log_event(msg):
    def info(*args, **kwargs):
        logger.info(msg)
    return info


def _fsm(version: str, data: Mapping[str, Any]) -> GameState:
    logger.debug(f'initial state for {version} version')
    if 'yellow' in version:
        from pokewatcher.data.yellow.states import InitialState
        return InitialState.new(data)
    if 'crystal' in version:
        from pokewatcher.data.crystal.states import InitialState
        return InitialState.new(data)
    raise ValueError(f'Unknown game version: {version}')
