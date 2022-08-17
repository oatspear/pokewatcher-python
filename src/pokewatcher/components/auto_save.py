# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Any, Final, Mapping, Set

import logging

from attrs import define, field

from pokewatcher.core.game import GameInterface
from pokewatcher.data.structs import GameMap
from pokewatcher.events import on_map_changed

###############################################################################
# Constants
###############################################################################

logger: Final = logging.getLogger(__name__)

###############################################################################
# Interface
###############################################################################


@define
class AutoSaveComponent:
    game: GameInterface
    maps_always_save: Set[str] = field(factory=set)
    maps_save_once: Set[str] = field(factory=set)

    def setup(self, settings: Mapping[str, Any]):
        logger.info('setting up')
        maps = settings['maps'].get(self.game.version, {})
        if isinstance(maps, str):  # alias
            maps = settings['maps'][maps]
        self.maps_always_save = set()
        for map_group, map_names in maps.get('always', {}).items():
            for map_name in map_names:
                uid = GameMap.make_uid(map_group, map_name)
                self.maps_always_save.add(uid)
        self.maps_save_once = set()
        for map_group, map_names in maps.get('once', {}).items():
            for map_name in map_names:
                uid = GameMap.make_uid(map_group, map_name)
                self.maps_save_once.add(uid)
        on_map_changed.watch(self.on_map_changed)

    def start(self):
        logger.info('starting')
        return

    def update(self, delta):
        # logger.debug('update')
        return

    def cleanup(self):
        logger.info('cleaning up')
        return

    def on_map_changed(self):
        return


def new(game: GameInterface):
    instance = AutoSaveComponent(game)
    return instance
