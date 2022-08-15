# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Any, Final

import logging

from attrs import define

from pokewatcher.data.structs import GameData
from pokewatcher.data.yellow.constants import (
    BATTLE_TYPE_LOST,
    BATTLE_TYPE_NONE,
    BATTLE_TYPE_TRAINER,
    BATTLE_TYPE_WILD,
    DEFAULT_PLAYER_NAME,
    SFX_SAVE_FILE,
)
import pokewatcher.events as events
from pokewatcher.logic.fsm import GameState, transition

###############################################################################
# Constants
###############################################################################

logger: Final[logging.Logger] = logging.getLogger(__name__)

###############################################################################
# Interface
###############################################################################


class YellowState(GameState):
    wPlayerID = transition  # noqa: N815
    wPlayerName = transition  # noqa: N815
    wIsInBattle = transition  # noqa: N815
    wChannelSoundIDs_5 = transition  # noqa: N815
    wLowHealthAlarmDisabled = transition  # noqa: N815


@define
class Initial(YellowState):
    def wPlayerName(self, prev: str, value: str, _data: GameData) -> GameState:  # noqa: N815
        logger.debug(f'player name changed from {prev!r} to {value!r}')
        if value != DEFAULT_PLAYER_NAME:
            logger.info('found saved game')
            return MainMenu()
        return self

    def wPlayerID(self, prev: int, value: int, _data: GameData) -> GameState:  # noqa: N815
        logger.debug(f'player ID changed from {prev} to {value}')
        if value != 0 and prev == 0:
            logger.info('starting a new game')
            events.on_new_game.emit()
            return InOverworld()
        return self


@define
class MainMenu(YellowState):
    def wPlayerID(self, prev: int, value: int, _data: GameData) -> GameState:  # noqa: N815
        logger.debug(f'player ID changed from {prev} to {value}')
        if value != 0:
            if prev <= 0:
                logger.info('continue previous game')
                events.on_continue.emit()
                return InOverworld()
            else:
                logger.info('starting a new game')
                events.on_new_game.emit()
                return InOverworld()
        return self


@define
class InGame(YellowState):
    def wPlayerID(self, prev: int, value: int, _data: GameData) -> GameState:  # noqa: N815
        logger.debug(f'player ID changed from {prev} to {value}')
        if value == 0:
            logger.info('game reset')
            events.on_reset.emit()
            return MainMenu()
        return self


@define
class InOverworld(InGame):
    def wIsInBattle(self, _p: Any, value: Any, data: GameData) -> GameState:  # noqa: N815
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
        elif value != BATTLE_TYPE_NONE:
            logger.warning(f'unknown battle type: {value}')
        return self

    def wChannelSoundIDs_5(self, _p: Any, value: int, _d: GameData) -> GameState:  # noqa: N815
        if value == SFX_SAVE_FILE:
            logger.info('saved game')
            events.on_save_game.emit()
        return self


@define
class InBattle(InGame):
    @property
    def is_battle_state(self) -> bool:
        return True

    def wIsInBattle(self, _p: int, value: int, data: GameData) -> GameState:  # noqa: N815
        if value == BATTLE_TYPE_NONE:
            # result should be set at this point
            data.battle.ongoing = False
            events.on_battle_ended()
            return InOverworld()
        elif value in (BATTLE_TYPE_WILD, BATTLE_TYPE_TRAINER, BATTLE_TYPE_LOST):
            self.inconsistent('wIsInBattle', value)
        else:
            logger.warning(f'unknown battle type: {value}')
        return self

    def wLowHealthAlarmDisabled(self, _p: int, v: bool, data: GameData) -> GameState:  # noqa: N815
        if v:
            data.battle.set_victory()
            events.on_battle_ended.emit()
            return VictorySequence()
        return self


@define
class VictorySequence(InGame):
    @property
    def is_battle_state(self) -> bool:
        return True

    def wIsInBattle(self, _p: int, value: int, _d: GameData) -> GameState:  # noqa: N815
        if value == BATTLE_TYPE_NONE:
            return InOverworld()
        elif value in (BATTLE_TYPE_WILD, BATTLE_TYPE_TRAINER, BATTLE_TYPE_LOST):
            self.inconsistent('wIsInBattle', value)
        else:
            logger.warning(f'unknown battle type: {value}')
        return self

    def wLowHealthAlarmDisabled(self, _p: int, v: bool, _d: GameData) -> GameState:  # noqa: N815
        if v:
            self.inconsistent('wLowHealthAlarmDisabled', v)
        return self
