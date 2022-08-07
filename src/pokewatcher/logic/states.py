# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Any, Final, Mapping

import logging

from attrs import define

import pokewatcher.events as events

###############################################################################
# Constants
###############################################################################

logger: Final[logging.Logger] = logging.getLogger(__name__)

###############################################################################
# Interface
###############################################################################


@define
class GameState:
    @property
    def name(self) -> str:
        name = type(self).__name__
        # if name.endswith('State'):
        #    name = name[:-5]
        return name

    @property
    def is_game_started(self) -> bool:
        return True

    @property
    def is_overworld(self) -> bool:
        return False

    @property
    def is_battle(self) -> bool:
        return False

    def enter(self, *args, **kwargs):
        logger.debug(f'enter state: {self.name}')
        # set event handlers, etc.
        return

    def exit(self):
        logger.debug(f'exit state: {self.name}')
        # remove event handlers, etc.
        return

    def on_property_changed(
        self,
        prop: str,
        prev: Any,
        value: Any,
        data: Mapping[str, Any],
    ) -> 'GameState':
        return self

    def on_player_id_changed(self, prev: int, value: int) -> 'GameState':
        logger.debug(f'player ID changed from {prev} to {value}')
        if value == 0:
            events.on_reset.emit()
            return self.state_on_reset
        elif prev == 0:
            if self.is_game_started:
                events.on_continue.emit()
                return self.state_on_continue
            else:
                events.on_new_game.emit()
                return self.state_on_new_game

    @property
    def state_on_reset(self) -> 'GameState':
        return self

    @property
    def state_on_new_game(self) -> 'GameState':
        return self

    @property
    def state_on_continue(self) -> 'GameState':
        return self


@define
class OverworldState(GameState):
    location: str

    @property
    def is_overworld(self) -> bool:
        return True

    def on_map_changed(self, value: str, prev: str):
        logger.debug(f'map changed from {prev} to {value}')
        self.location = value
        events.on_map_changed.emit(value)


@define
class BattleState(GameState):
    @property
    def is_battle(self) -> bool:
        return True

    @property
    def is_trainer(self) -> bool:
        return False

    @property
    def is_wild(self) -> bool:
        return False


@define
class VersusWildState(BattleState):
    @property
    def is_wild(self) -> bool:
        return True


@define
class VersusTrainerState(BattleState):
    @property
    def is_trainer(self) -> bool:
        return True
