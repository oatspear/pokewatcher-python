# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Any, Final

import logging

from attrs import define

from pokewatcher.data.structs import GameData

# from pokewatcher.data.yellow.constants import (
#     BATTLE_TYPE_LOST,
#     BATTLE_TYPE_NONE,
#     BATTLE_TYPE_TRAINER,
#     BATTLE_TYPE_WILD,
#     DEFAULT_PLAYER_NAME,
#     SFX_SAVE_FILE,
# )
import pokewatcher.events as events
from pokewatcher.logic.fsm import GameState, transition

###############################################################################
# Constants
###############################################################################

logger: Final[logging.Logger] = logging.getLogger(__name__)

###############################################################################
# Interface
###############################################################################

# Crystal resets all memory to zeroes when starting the game.
# On selecting New Game, a new memory reset is called and the new player ID
# is set right afterwards (see engine/menus/intro_menu.asm:ResetWRAM).
# wSavedAtLeastOnce is set to 0 on New Game, and seems to be set to 1 when saving,
# or when certain milestones are reached. It is part of wPlayerData, and would
# be a useful indicator to distinguish New Game from Continue.
# wEnteredMapFromContinue is another good indicator of a Continue.
# After the change to player ID, a New Game can likely be detected with a change
# to the first party species.
# engine/menus/save:TryLoadSaveFile, called from Continue, will finish loading
# all of wPlayerData before loading wPokemonData. A New Game, on the other hand,
# will only set a handful of things before setting wPartyCount to 0 and the
# first byte of wPartySpecies to -1. This change to -1 can be the trigger of
# either event, but a Continue will have changed wPlayerName and other things
# beforehand.
# On a change to wPlayerID, we must jump to a NewGameOrContinue state.
# In this state, a change to wPartySpecies triggers a New Game, while a change
# to wPlayerName triggers a Continue, or transitions to another state that awaits
# the entrance to the overworld.

class CrystalState(GameState):
    wPlayerID = transition  # noqa: N815
    wPlayerName = transition  # noqa: N815
    wMoney = transition  # noqa: N815
    wGameTimeFrames = transition  # noqa: N815
    wChannel5MusicID = transition  # noqa: N815
    wBattleLowHealthAlarm = transition  # noqa: N815


@define
class Initial(CrystalState):
    def wPlayerID(self, prev: int, value: int, _data: GameData) -> GameState:  # noqa: N815
        logger.debug(f'player ID changed: {prev} -> {value}')
        if value == 0:
            return _reset_game()
        if prev <= 0:
            return NewGameOrContinue()
        return self


@define
class NewGameOrContinue(CrystalState):
    def wPlayerName(self, prev: str, value: str, _data: GameData) -> GameState:  # noqa: N815
        logger.debug(f'player name changed: {prev!r} -> {value!r}')
        if value:
            logger.info('found saved game')
            return MainMenuContinue()
        return self

    def wMoney(self, prev: int, value: int, _data: GameData) -> GameState:  # noqa: N815
        logger.debug(f'player money changed: {prev!r} -> {value!r}')
        if value > 0:
            return _press_new_game()
        return self


@define
class MainMenuContinue(CrystalState):
    _map_changed: bool = field(init=False, default=False, eq=False, repr=False)
    _x_changed: bool = field(init=False, default=False, eq=False, repr=False)
    _y_changed: bool = field(init=False, default=False, eq=False, repr=False)
    _time_changed: bool = field(init=False, default=False, eq=False, repr=False)

    def wPlayerID(self, prev: int, value: int, _data: GameData) -> GameState:  # noqa: N815
        logger.debug(f'player ID changed: {prev} -> {value}')
        if value == 0:
            return _reset_game()
        return _press_new_game()

    def wGameTimeFrames(self, _p: Any, value: int, _data: GameData) -> GameState:  # noqa: N815
        logger.debug(f'play time frames changed: {value}')
        if not self._time_changed:
            # first loaded game time
            self._time_changed = True
            return self
        if value != 0:
            # both overflow and reset will turn into zero
            return _press_continue()
        return self

    def wCurMap(self, prev: Any, value: str, _d: GameData) -> GameState:  # noqa: N815
        logger.debug(f'map changed: {prev!r} -> {value!r}')
        if not self._map_changed:
            # first loaded map
            self._map_changed = True
            return self
        # already late
        return _press_continue()

    def wXCoord(self, prev: int, value: int, data: GameData) -> GameState:  # noqa: N815
        # safety net in case we miss an update to wJoyIgnore
        logger.debug(f'player x coordinate changed: {prev} -> {value}')
        if not self._x_changed:
            # first loaded coordinates
            self._x_changed = True
            return self
        # already late
        return _press_continue()

    def wYCoord(self, prev: int, value: int, data: GameData) -> GameState:  # noqa: N815
        # safety net in case we miss an update to wJoyIgnore
        logger.debug(f'player y coordinate changed: {prev} -> {value}')
        if not self._y_changed:
            # first loaded coordinates
            self._y_changed = True
            return self
        # already late
        return _press_continue()


@define
class InGame(CrystalState):
    def wPlayerID(self, prev: int, value: int, _data: GameData) -> GameState:  # noqa: N815
        logger.debug(f'player ID changed: {prev} -> {value}')
        if value == 0:
            return _reset_game()
        return self


@define
class InOverworld(InGame):
    def wIsInBattle(self, _p: Any, value: Any, data: GameData) -> GameState:  # noqa: N815
        if value == BATTLE_TYPE_WILD:
            data.battle.set_wild_battle()
            events.on_battle_started.emit()
            return InBattle()
        elif value == BATTLE_TYPE_TRAINER:
            data.battle.set_trainer_battle()
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

    def wCurMap(self, _p: Any, value: str, _d: GameData) -> GameState:  # noqa: N815
        logger.info(f'map changed: {value}')
        events.on_map_changed.emit()
        return self


@define
class InBattle(InGame):
    @property
    def is_battle_state(self) -> bool:
        return True

    def wIsInBattle(self, _p: int, value: int, data: GameData) -> GameState:  # noqa: N815
        if value == BATTLE_TYPE_NONE:
            if data.battle.is_vs_wild:
                data.battle.ongoing = False
            else:
                data.battle.set_defeat()
            events.on_battle_ended()
            return InOverworld()
        if value == BATTLE_TYPE_LOST:
            data.battle.set_defeat()
            events.on_battle_ended()
            return InOverworld()
        elif value == BATTLE_TYPE_WILD or value == BATTLE_TYPE_TRAINER:
            self.inconsistent('wIsInBattle', value)
        else:
            logger.warning(f'unknown battle type: {value}')
        return self

    def wLowHealthAlarmDisabled(self, _p: int, v: bool, data: GameData) -> GameState:  # noqa: N815
        if v:
            data.battle.set_victory()
            events.on_battle_ended.emit()
            if not data.battle.is_vs_wild:
                if data.battle.trainer.trainer_class == TRAINER_CLASS_CHAMPION:
                    events.on_champion_victory.emit()
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


###############################################################################
# Helper Functions
###############################################################################


def _press_new_game() -> GameState:
    logger.info('starting a new game')
    events.on_new_game.emit()
    return InOverworld()


def _press_continue() -> GameState:
    logger.info('continue previous game')
    events.on_continue.emit()
    return InOverworld()


def _reset_game() -> GameState:
    logger.info('game reset')
    events.on_reset.emit()
    return Initial()
