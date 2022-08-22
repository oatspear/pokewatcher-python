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

DEFAULTS: Final[Mapping[str, Any]] = {
    'enabled': False,
    'maps': {
        'Pokemon Red and Blue': 'Pokemon Yellow',
        'Pokemon Yellow': {
            'always': {
                'Kanto': [
                    'Indigo Plateau - Lobby',
                    'Viridian City - Gym',
                    'Pewter City - Gym',
                    'Cerulean City - Gym',
                    'Vermilion City - Gym',
                    'Celadon City - Gym',
                    'Fuchsia City - Gym',
                    'Saffron City - Gym',
                    'Cinnabar Island - Gym',
                    "Lorelei's Room",
                    "Bruno's Room",
                    "Agatha's Room",
                    "Lance's Room",
                    'Champions Room',
                ]
            },
            'once': {
                'Kanto': [
                    'Viridian City',
                    'Pewter City',
                    'Cerulean City',
                    'Lavender Town',
                    'Vermilion City',
                    'Celadon City',
                    'Fuchsia City',
                    'Cinnabar Island',
                    'Saffron City',
                    'Viridian Forest',
                    'Rock Tunnel - 1',
                    'Mt Moon - 1',
                    'Victory Road',
                    'Pokemon Tower - 1F',
                    'Silph Co - 1F',
                    'Route 1',
                    'Route 2',
                    'Route 3',
                    'Route 4',
                    'Route 5',
                    'Route 6',
                    'Route 7',
                    'Route 8',
                    'Route 9',
                    'Route 10',
                    'Route 11',
                    'Route 12',
                    'Route 13',
                    'Route 14',
                    'Route 15',
                    'Route 16',
                    'Route 17',
                    'Route 18',
                    'Route 19',
                    'Route 20',
                    'Route 21',
                    'Route 22',
                    'Route 23',
                    'Route 24',
                    'Route 25',
                ]
            },
        },
    },
}

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


def default_settings() -> Mapping[str, Any]:
    return dict(DEFAULTS)
