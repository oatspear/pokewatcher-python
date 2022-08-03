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
from pokewatcher.data.states import initial_state

###############################################################################
# Constants
###############################################################################

logger: Final = logging.getLogger(__name__)

###############################################################################
# Interface
###############################################################################


@define
class GameInterface:
    retroarch: RetroArchBridge = field(factory=RetroArchBridge)
    gamehook: GameHookBridge = field(factory=GameHookBridge)
    state: Any = field(init=False, default=None)

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
        logger.info('setting up')
        retroarch = settings['retroarch']
        self.retroarch.setup(retroarch)
        gamehook = settings['gamehook']
        self.gamehook.setup(gamehook)
        self.gamehook.on_change = self._on_property_changed
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

    def _on_property_changed(self, prop: str, value: Any):
        new_state = self.state.on_property_changed(prop, value)
        if new_state is not self.state:
            logger.info(f'state transition: {self.state.name} -> {new_state.name}')
        self.state = new_state
