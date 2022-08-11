# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Any, Final

import logging

from attrs import define

from pokewatcher.data.yellow.constants import (
    ALARM_DISABLED,
    ALARM_ENABLED,
    BATTLE_TYPE_LOST,
    BATTLE_TYPE_NONE,
    BATTLE_TYPE_TRAINER,
    BATTLE_TYPE_WILD,
)
import pokewatcher.events as events
from pokewatcher.logic.fsm import GameState

###############################################################################
# Constants
###############################################################################

logger: Final[logging.Logger] = logging.getLogger(__name__)

###############################################################################
# Interface
###############################################################################


@define
class Start(GameState):
    def wPlayerID(self, prev: int, value: int, data: GameData) -> GameState:
        logger.debug(f'player ID changed from {prev} to {value}')
        if value != 0 and prev == 0:
            events.on_new_game.emit()
            return InOverworld()
        return self


@define
class MainMenu(GameState):
    def wPlayerID(self, prev: int, value: int, data: GameData) -> GameState:
        logger.debug(f'player ID changed from {prev} to {value}')
        if value != 0 and prev == 0:
            events.on_continue.emit()
            return InOverworld()
        return self


@define
class InGame(GameState):
    def wPlayerID(self, prev: int, value: int, data: GameData) -> GameState:
        logger.debug(f'player ID changed from {prev} to {value}')
        if value == 0:
            events.on_reset.emit()
            return MainMenu()
        return state


@define
class InOverworld(InGame):
    def wIsInBattle(self, prev: Any, value: Any, data: GameData) -> GameState:
        if value == BATTLE_TYPE_WILD:
            data.battle.set_wild_battle()
            events.on_battle_started.emit()
            return InBattle()
        elif value == BATTLE_TYPE_TRAINER:
            assert not data.battle.is_vs_wild
            data.battle.ongoing = True
            events.on_battle_started.emit()
            return InBattle()
        elif value == BATTLE_TYPE_LOST:
            data.battle.set_defeat()
            events.on_blackout.emit()
        else:
            logger.warning(f'unknown battle type: {value}')
        return self


@define
class InBattle(InGame):
    @property
    def is_battle_state(self) -> bool:
        return True

    def wIsInBattle(self, prev: int, value: int, data: GameData) -> GameState:
        if value == BATTLE_TYPE_NONE:
            data.battle.set_draw()
            events.on_battle_ended()
            # events.on_run_away()
            return InOverworld()
        elif value == BATTLE_TYPE_WILD:
            self.inconsistent()
        elif value == BATTLE_TYPE_TRAINER:
            self.inconsistent()
        elif value == BATTLE_TYPE_LOST:
            self.inconsistent()
        else:
            logger.warning(f'unknown battle type: {value}')
        return self

    def wLowHealthAlarmDisabled(self, prev: int, value: int, data: GameData) -> GameState:
        if value == ALARM_DISABLED:
            data.battle.set_victory()
            events.on_battle_ended.emit()
            return VictorySequence()
        return self


@define
class VictorySequence(InGame):
    def wIsInBattle(self, prev: int, value: int, data: GameData) -> GameState:
        if value == BATTLE_TYPE_NONE:
            return InOverworld()
        elif value == BATTLE_TYPE_WILD:
            self.inconsistent()
        elif value == BATTLE_TYPE_TRAINER:
            self.inconsistent()
        elif value == BATTLE_TYPE_LOST:
            self.inconsistent()
        else:
            logger.warning(f'unknown battle type: {value}')
        return self

    def wLowHealthAlarmDisabled(self, prev: int, value: int, data: GameData) -> GameState:
        if value == ALARM_DISABLED:
            self.inconsistent()
        return self
