# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Any, Final, Mapping, Set

import logging

from attrs import define, field

from pokewatcher.core.game import GameInterface
from pokewatcher.core.retroarch import RetroArchError
from pokewatcher.data.structs import GameMap
from pokewatcher.events import on_map_changed, on_reset, on_save_game

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
    _last_map: str = field(init=False, default='', eq=False, repr=False)
    _just_reset: bool = field(init=False, default=True, eq=False, repr=False)
    _not_visited: Set[str] = field(init=False, factory=set, eq=False, repr=False)

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

        self._last_map = ''
        self._just_reset = True
        self._not_visited = set(self.maps_save_once)

        on_map_changed.watch(self.on_map_changed)
        on_reset.watch(self.on_reset)
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

    def on_map_changed(self):
        map = self.game.data.location
        if not map:
            # possibly in intro screen
            return

        if map == self._last_map:
            return

        if self._just_reset:
            # ignore the first map change, when loading up the game
            self._just_reset = False
            return

        if map in self.maps_always_save:
            try:
                self.game.retroarch.request_save_state()
            except RetroArchError as e:
                logger.error(str(e))
        elif map in self._not_visited:
            try:
                self.game.retroarch.request_save_state()
                self._not_visited.remove(map)
            except RetroArchError as e:
                logger.error(str(e))
        self._last_map = map

    def on_reset(self):
        self._just_reset = True

    def on_save_game(self):
        try:
            self.game.retroarch.request_save_state()
        except RetroArchError as e:
            logger.error(str(e))


def new(game: GameInterface) -> AutoSaveComponent:
    instance = AutoSaveComponent(game)
    return instance
