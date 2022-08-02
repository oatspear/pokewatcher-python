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

    @property
    def rom(self) -> Optional[str]:
        return self.retroarch.rom

    @property
    def version(self) -> Optional[str]:
        return self.gamehook.game_name

    def setup(self, settings: Mapping[str, Any]):
        logger.info('setting up')
        retroarch = settings['retroarch']
        self.retroarch.setup(retroarch)
        gamehook = settings['gamehook']
        self.gamehook.setup(gamehook)

    def start(self):
        logger.info('starting')
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
