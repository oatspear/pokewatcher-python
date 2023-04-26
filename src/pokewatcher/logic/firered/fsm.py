# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Any, Final

import logging

from attrs import define, field

from pokewatcher.data.firered.constants import (
    BATTLE_RESULT_CAUGHT,
    BATTLE_RESULT_DRAW,
    BATTLE_RESULT_FORFEITED,
    BATTLE_RESULT_LOSE,
    BATTLE_RESULT_NO_SAFARI_BALLS,
    BATTLE_RESULT_NONE,
    BATTLE_RESULT_POKEMON_FLED,
    BATTLE_RESULT_POKEMON_TELEPORTED,
    BATTLE_RESULT_RUN,
    BATTLE_RESULT_TELEPORTED,
    BATTLE_RESULT_WIN,
    MAIN_STATE_NONE,
    MAIN_STATE_OVERWORLD,
    MAIN_STATE_BATTLE,
    SUBSTATE_NONE,
    SUBSTATE_OVERWORLD,
    SUBSTATE_BATTLE,
    SUBSTATE_BATTLE_ANIMATION,
    SUBSTATE_INTRO_CINEMATIC,
    SUBSTATE_TRANSITION_OVERWORLD,
    TRAINER_CLASSES_FINAL_BATTLE,
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


def _go_to_battle(data: GameData) -> GameState:
    logger.info('battle started')
    # logger.info(f'vs wild: {data.battle.is_vs_wild}')
    # logger.info(f'trainer: {data.battle.trainer.trainer_class}')
    data.battle.ongoing = True
    events.on_battle_started.emit()
    return InBattle()


###############################################################################
# Interface
###############################################################################


class FireRedState(GameState):
    player_name = transition
    team_count = transition
    battle_outcome = transition
    callback1 = transition
    callback2 = transition
    current_map = transition
    # wGameTimeHours = transition  # noqa: N815
    # wGameTimeMinutes = transition  # noqa: N815
    # wGameTimeSeconds = transition  # noqa: N815
    # wGameTimeFrames = transition  # noqa: N815
    # wChannel5MusicID = transition  # noqa: N815
    # wBattleLowHealthAlarm = transition  # noqa: N815
    # wBattleMode = transition  # noqa: N815
    # wBattleType = transition  # noqa: N815
    # wBattleResult = transition  # noqa: N815
    # wXCoord = transition  # noqa: N815
    # wYCoord = transition  # noqa: N815


@define
class Initial(FireRedState):
    def callback1(self, prev: int, value: int, data: GameData) -> GameState:
        logger.debug(f'callback1 changed: {prev} -> {value}')
        if value == MAIN_STATE_OVERWORLD:
            # logger.info('Initial -> Overworld')
            return InOverworld()
        if value == MAIN_STATE_BATTLE:
            # logger.info('Initial -> Battle')
            return _go_to_battle(data)
        return self


# @define
# class NewGameOrContinue(FireRedState):
#     def team_count(self, prev: int, value: int, _data: GameData) -> GameState:
#         logger.debug(f'team count changed: {prev} -> {value}')
#         if value > 0:
#             logger.info('found saved game')
#             return InOverworld()
#         return self


@define
class InGame(FireRedState):
    @property
    def is_battle_state(self) -> bool:
        return False


@define
class InOverworld(InGame):
    maybe_reset: bool = False

    def callback1(self, prev: int, value: int, data: GameData) -> GameState:
        logger.debug(f'callback1 changed: {prev} -> {value}')
        self.maybe_reset = value == MAIN_STATE_NONE
        if value == MAIN_STATE_BATTLE:
            # logger.info('Overworld -> Battle')
            return _go_to_battle(data)
        return self

    def callback2(self, prev: int, value: int, data: GameData) -> GameState:
        logger.debug(f'callback2 changed: {prev} -> {value}')
        if self.maybe_reset and value == SUBSTATE_INTRO_CINEMATIC:
            return _reset_game()
        return self

    def current_map(self, _p: Any, value: str, _d: GameData) -> GameState:
        logger.info(f'map changed: {value}')
        events.on_map_changed.emit()
        return self


@define
class InBattle(InGame):
    maybe_reset: bool = False

    @property
    def is_battle_state(self) -> bool:
        return True

    def callback1(self, prev: int, value: int, data: GameData) -> GameState:
        logger.debug(f'callback1 changed: {prev} -> {value}')
        if value == MAIN_STATE_NONE:
            self.maybe_reset = True
        else:
            self.maybe_reset = False
            if value != MAIN_STATE_BATTLE:
                # logger.info('Battle -> Overworld (via callback1)')
                data.battle.ongoing = False
                events.on_battle_ended()
                return InOverworld()
        return self

    def callback2(self, prev: int, value: int, data: GameData) -> GameState:
        logger.debug(f'callback2 changed: {prev} -> {value}')
        if self.maybe_reset and value == SUBSTATE_INTRO_CINEMATIC:
            data.battle.set_defeat()
            return _reset_game()
        return self

    def battle_outcome(self, prev: int, value: int, data: GameData) -> GameState:
        logger.debug(f'battle outcome changed: {prev} -> {value}')
        # value = value & 0x07
        if value == BATTLE_RESULT_WIN or value == BATTLE_RESULT_CAUGHT:
            # logger.info('Battle -> Overworld (via outcome)')
            data.battle.set_victory()
            events.on_battle_ended.emit()
            if not data.battle.is_vs_wild:
                if data.battle.trainer.trainer_class in TRAINER_CLASSES_FINAL_BATTLE:
                    events.on_champion_victory.emit()
            return InOverworld()
        elif value == BATTLE_RESULT_LOSE or value == BATTLE_RESULT_FORFEITED:
            # logger.info('Battle -> Overworld (via outcome)')
            data.battle.set_defeat()
            events.on_battle_ended.emit()
            return InOverworld()
        elif value != BATTLE_RESULT_NONE:
            # logger.info('Battle -> Overworld (via outcome)')
            data.battle.set_draw()
            events.on_battle_ended.emit()
            return InOverworld()
        # data.battle.ongoing = True
        return self
