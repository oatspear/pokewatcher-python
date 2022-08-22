# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Any, Final, Mapping

import logging

from attrs import define

from pokewatcher.core.game import GameInterface

###############################################################################
# Constants
###############################################################################

logger: Final = logging.getLogger(__name__)

DEFAULTS: Final[Mapping[str, Any]] = {'enabled': True}

###############################################################################
# Interface
###############################################################################


@define
class Component:
    game: GameInterface

    def setup(self, settings: Mapping[str, Any]):
        logger.info('setting up')
        return

    def start(self):
        logger.info('starting')
        return

    def update(self, delta):
        # logger.debug('update')
        return

    def cleanup(self):
        logger.info('cleaning up')
        return


def new(game: GameInterface) -> Component:
    instance = Component(game)
    return instance


def default_settings() -> Mapping[str, Any]:
    return dict(DEFAULTS)
