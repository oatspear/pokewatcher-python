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
        self._set_data_handlers()

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
        pass

    def _set_data_handlers(self):
        version = self.version.lower()
        if 'yellow' in version:
            pass  # self.data_handler = YellowDataHandler(rom, version, data)
        elif 'crystal' in version:
            pass  # self.data_handler = CrystalDataHandler(rom, version, data)
        else:
            raise ValueError(f'Unknown game version: {version}')
        #print('[New Game] tracking from this point onward')
        #logger.info('data_handler.is_new_game = True')
        #self.data_handler.is_new_game = True
