# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Any, Final

import logging

from attrs import define, field

from pokewatcher.data.emerald.constants import (
    BATTLE_RESULT_LOSE,
    BATTLE_RESULT_NONE,
    BATTLE_RESULT_RUN,
    BATTLE_RESULT_WIN,
)
from pokewatcher.data.structs import GameData
import pokewatcher.events as events
from pokewatcher.logic.fsm import GameState, transition

###############################################################################
# Constants
###############################################################################

logger: Final[logging.Logger] = logging.getLogger(__name__)

###############################################################################
# Helper Functions
###############################################################################


def _reset_game() -> GameState:
    logger.info('game reset')
    events.on_reset.emit()
    return Initial()


###############################################################################
# Interface
###############################################################################


class EmeraldState(GameState):
    player_name = transition
    team_count = transition
    battle_outcome = transition
    battle_bg_tiles = transition
    # wGameTimeHours = transition  # noqa: N815
    # wGameTimeMinutes = transition  # noqa: N815
    # wGameTimeSeconds = transition  # noqa: N815
    # wGameTimeFrames = transition  # noqa: N815
    # wChannel5MusicID = transition  # noqa: N815
    # wBattleLowHealthAlarm = transition  # noqa: N815
    # wBattleMode = transition  # noqa: N815
    # wBattleType = transition  # noqa: N815
    # wBattleResult = transition  # noqa: N815
    # wMapGroup = transition  # noqa: N815
    # wMapNumber = transition  # noqa: N815
    # wXCoord = transition  # noqa: N815
    # wYCoord = transition  # noqa: N815


@define
class Initial(EmeraldState):
    def player_name(self, prev: str, value: str, _data: GameData) -> GameState:
        logger.debug(f'player name changed: {prev} -> {value}')
        if not value:
            return _reset_game()
        if not prev:
            return NewGameOrContinue()
        return self


@define
class NewGameOrContinue(EmeraldState):
    def team_count(self, prev: int, value: int, _data: GameData) -> GameState:
        logger.debug(f'team count changed: {prev} -> {value}')
        if value > 0:
            logger.info('found saved game')
            return InOverworld()
        return self


@define
class InGame(EmeraldState):
    def player_name(self, prev: str, value: str, _data: GameData) -> GameState:
        logger.debug(f'player name changed: {prev} -> {value}')
        if not value:
            return _reset_game()
        return self


@define
class InOverworld(InGame):
    def battle_bg_tiles(self, prev: int, value: int, data: GameData) -> GameState:
        logger.debug(f'battle background tiles changed: {prev} -> {value}')
        if value != 0:
            logger.info('battle started')
            #data.battle.set_wild_battle()
            #data.battle.set_victory()
            data.battle.ongoing = True
            events.on_battle_started.emit()
            return InBattle()
        return self


@define
class InBattle(InGame):
    @property
    def is_battle_state(self) -> bool:
        return True

    def battle_bg_tiles(self, prev: int, value: int, data: GameData) -> GameState:
        logger.debug(f'battle background tiles changed: {prev} -> {value}')
        if value == 0:
            data.battle.ongoing = False
            events.on_battle_ended()
            return InOverworld()
        else:
            self.inconsistent('battle_bg_tiles', value)
        return self

    def battle_outcome(self, prev: int, value: int, data: GameData) -> GameState:
        logger.debug(f'battle outcome changed: {prev} -> {value}')
        value = value & 0x07
        if value == BATTLE_RESULT_WIN:
            data.battle.set_victory()
        elif value == BATTLE_RESULT_RUN:
            data.battle.set_draw()
        elif value == BATTLE_RESULT_LOSE:
            data.battle.set_defeat()
        data.battle.ongoing = True
        return self
