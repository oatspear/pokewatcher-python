# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Any, Final, Mapping

import logging

from attrs import define

from pokewatcher.core.game import GameInterface
from pokewatcher.errors import PokeWatcherComponentError

###############################################################################
# Constants
###############################################################################

logger: Final = logging.getLogger(__name__)

###############################################################################
# Interface
###############################################################################


@define
class LiveSplitInterface:
    game: GameInterface

    def setup(self, settings: Mapping[str, Any]):
        logger.info('setting up')
        if self.game.has_custom_clock:
            name = type(self.game.clock).__name__
            raise PokeWatcherComponentError(f'found pre-existing custom clock: {name}')
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


@define
class LivesplitClock:
    time_start: TimeRecord = field(factory=time.time, converter=TimeRecord.converter)

    def reset_start_time(self):
        self.time_start = TimeRecord.from_float_seconds(time.time())

    def get_current_time(self) -> TimeRecord:
        return TimeRecord.from_float_seconds(time.time()) - self.time_start

    def get_elapsed_time(self) -> TimeInterval:
        return TimeInterval(start=self.time_start, end=time.time())


def new(game: GameInterface) -> LiveSplitInterface:
    instance = LiveSplitInterface(game)
    return instance
