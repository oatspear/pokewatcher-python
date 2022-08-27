# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Any, Final

import logging

from attrs import define, field

from pokewatcher.data.crystal.constants import (
    BATTLE_MODE_NONE,
    BATTLE_MODE_TRAINER,
    BATTLE_MODE_WILD,
    BATTLE_RESULT_DRAW,
    BATTLE_RESULT_LOSE,
    BATTLE_RESULT_WIN,
    MAP_GROUPS,
    SFX_SAVE_FILE,
    TRAINER_CLASS_CHAMPION,
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


@define
class MapTracker:
    _map_group: int = 0
    _map_number: int = 0
    _changed: bool = True

    @property
    def map_group(self) -> int:
        return self._map_group

    @map_group.setter
    def map_group(self, value: int):
        self._map_group = value
        self._changed = True

    @property
    def map_number(self) -> int:
        return self._map_number

    @map_number.setter
    def map_number(self, value: int):
        self._map_number = value
        self._changed = True

    def commit(self, data: GameData):
        if self._changed:
            group = MAP_GROUPS[self._map_group]
            map = f'{self._map_number:02d}'
            data.location = f'{group}/{map}'
            logger.info(f'map changed: {data.location}')
            events.on_map_changed.emit()
            self._changed = False


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
    wBattleMode = transition  # noqa: N815
    wBattleType = transition  # noqa: N815
    wBattleResult = transition  # noqa: N815
    wMapGroup = transition  # noqa: N815
    wMapNumber = transition  # noqa: N815
    wXCoord = transition  # noqa: N815
    wYCoord = transition  # noqa: N815


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
    map_tracker: MapTracker = field(init=False, factory=MapTracker, eq=False, repr=False)
    _map_group_changed: bool = field(init=False, default=False, eq=False, repr=False)
    _map_number_changed: bool = field(init=False, default=False, eq=False, repr=False)
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

    def wMapGroup(self, prev: Any, value: int, _d: GameData) -> GameState:  # noqa: N815
        logger.debug(f'map group changed: {prev!r} -> {value!r}')
        self.map_tracker.map_group = value
        if not self._map_group_changed:
            # first loaded map
            self._map_group_changed = True
            return self
        # already late
        return _press_continue()

    def wMapNumber(self, prev: Any, value: int, _d: GameData) -> GameState:  # noqa: N815
        logger.debug(f'map number changed: {prev!r} -> {value!r}')
        self.map_tracker.map_number = value
        if not self._map_number_changed:
            # first loaded map
            self._map_number_changed = True
            return self
        # already late
        return _press_continue()

    def wXCoord(self, prev: int, value: int, data: GameData) -> GameState:  # noqa: N815
        logger.debug(f'player x coordinate changed: {prev} -> {value}')
        self.map_tracker.commit(data)
        if not self._x_changed:
            # first loaded coordinates
            self._x_changed = True
            return self
        # already late
        return _press_continue()

    def wYCoord(self, prev: int, value: int, data: GameData) -> GameState:  # noqa: N815
        logger.debug(f'player y coordinate changed: {prev} -> {value}')
        self.map_tracker.commit(data)
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
    map_tracker: MapTracker = field(init=False, factory=MapTracker, eq=False, repr=False)

    def wBattleMode(self, prev: Any, value: int, data: GameData) -> GameState:  # noqa: N815
        logger.debug(f'battle mode changed: {prev!r} -> {value!r}')
        if value == BATTLE_MODE_WILD:
            logger.info('wild battle started')
            data.battle.set_wild_battle()
            data.battle.set_victory()
            data.battle.ongoing = True
            events.on_battle_started.emit()
            return InBattle()
        if value == BATTLE_MODE_TRAINER:
            logger.info('trainer battle started')
            data.battle.set_trainer_battle()
            data.battle.set_victory()
            data.battle.ongoing = True
            events.on_battle_started.emit()
            return InBattle()
        return self

    def wChannel5MusicID(self, _p: Any, value: int, _d: GameData) -> GameState:  # noqa: N815
        if value == SFX_SAVE_FILE:
            logger.info('saved game')
            events.on_save_game.emit()
        return self

    def wMapGroup(self, prev: Any, value: int, _d: GameData) -> GameState:  # noqa: N815
        logger.debug(f'map group changed: {prev!r} -> {value!r}')
        self.map_tracker.map_group = value
        return self

    def wMapNumber(self, prev: Any, value: int, _d: GameData) -> GameState:  # noqa: N815
        logger.debug(f'map number changed: {prev!r} -> {value!r}')
        self.map_tracker.map_number = value
        return self

    def wXCoord(self, prev: int, value: int, data: GameData) -> GameState:  # noqa: N815
        logger.debug(f'player x coordinate changed: {prev} -> {value}')
        self.map_tracker.commit(data)
        return self

    def wYCoord(self, prev: int, value: int, data: GameData) -> GameState:  # noqa: N815
        logger.debug(f'player y coordinate changed: {prev} -> {value}')
        self.map_tracker.commit(data)
        return self


@define
class InBattle(InGame):
    @property
    def is_battle_state(self) -> bool:
        return True

    def wBattleMode(self, prev: int, value: int, data: GameData) -> GameState:  # noqa: N815
        logger.debug(f'battle mode changed: {prev!r} -> {value!r}')
        if value == self.BATTLE_MODE_NONE:
            data.battle.ongoing = False
            events.on_battle_ended()
            return InOverworld()
        else:
            self.inconsistent('wBattleMode', value)
        return self

    def wBattleResult(self, prev: int, value: int, data: GameData) -> GameState:  # noqa: N815
        logger.debug(f'battle result changed: {prev!r} -> {value!r}')
        value = value & 0x03
        if value == BATTLE_RESULT_WIN:
            data.battle.set_victory()
        elif value == BATTLE_RESULT_DRAW:
            data.battle.set_draw()
        elif value == BATTLE_RESULT_LOSE:
            data.battle.set_defeat()
        data.battle.ongoing = True
        return self

    def wBattleLowHealthAlarm(self, p: Any, v: bool, data: GameData) -> GameState:  # noqa: N815
        logger.debug(f'low health alarm changed: {p!r} -> {v!r}')
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

    def wBattleMode(self, prev: Any, value: int, _d: GameData) -> GameState:  # noqa: N815
        logger.debug(f'battle mode changed: {prev!r} -> {value!r}')
        if value == BATTLE_MODE_NONE:
            return InOverworld()
        elif value == BATTLE_MODE_WILD or value == BATTLE_MODE_TRAINER:
            self.inconsistent('wBattleMode', value)
        else:
            logger.warning(f'unknown battle mode: {value}')
        return self

    def wBattleLowHealthAlarm(self, _p: Any, v: bool, _d: GameData) -> GameState:  # noqa: N815
        if v:
            self.inconsistent('wBattleLowHealthAlarm', v)
        return self
