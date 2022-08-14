# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Any, Final, Mapping

import logging

from attrs import define

from pokewatcher.core.game import GameInterface
from pokewatcher.events import on_save_game

###############################################################################
# Constants
###############################################################################

logger: Final = logging.getLogger(__name__)

###############################################################################
# Interface
###############################################################################


@define
class SaveFileBackupComponent:
    game: GameInterface
    dirty: bool = False

    def setup(self, settings: Mapping[str, Any]):
        logger.info('setting up')
        on_save_game.watch(self.on_save_game)

    def start(self):
        logger.info('starting')
        return

    def update(self, delta):
        # logger.debug('update')
        return

    def cleanup(self):
        logger.info('cleaning up')
        return

    def on_save_game(self):
        self.dirty = True


def new(game: GameInterface):
    instance = SaveFileBackupComponent(game)
    return instance
