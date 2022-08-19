# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Any, Final

import logging

from attrs import define, field

from pokewatcher.data.structs import GameData
from pokewatcher.data.yellow.constants import (
    BATTLE_TYPE_LOST,
    BATTLE_TYPE_NONE,
    BATTLE_TYPE_TRAINER,
    BATTLE_TYPE_WILD,
    DEFAULT_PLAYER_NAME,
    JOY_MASK_ALL,
    JOY_MASK_NONE,
    MENU_ITEM_CONTINUE,
    MENU_ITEM_NEW_GAME,
    SFX_PRESS_A_B,
    SFX_SAVE_FILE,
    TRAINER_CLASS_CHAMPION,
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
    wCurMap = transition  # noqa: N815
    wJoyIgnore = transition  # noqa: N815
    wXCoord = transition  # noqa: N815
    wYCoord = transition  # noqa: N815
    wCurrentMenuItem = transition  # noqa: N815
    wd732_0 = transition  # noqa: N815
    wPlayTimeHours = transition  # noqa: N815
    wPlayTimeMinutes = transition  # noqa: N815
    wPlayTimeSeconds = transition  # noqa: N815
    wPlayTimeFrames = transition  # noqa: N815


@define
class Initial(YellowState):
    def wPlayerName(self, prev: str, value: str, _data: GameData) -> GameState:  # noqa: N815
        logger.debug(f'player name changed: {prev!r} -> {value!r}')
        if value == DEFAULT_PLAYER_NAME:
            # title screen
            return MainMenu()
        return self


@define
class MainMenu(YellowState):
    def wPlayerID(self, prev: int, value: int, _data: GameData) -> GameState:  # noqa: N815
        logger.debug(f'player ID changed: {prev} -> {value}')
        if value == 0:
            return _reset_game()
        if prev <= 0:
            return _press_new_game()
        return self

    def wPlayerName(self, prev: str, value: str, _data: GameData) -> GameState:  # noqa: N815
        logger.debug(f'player name changed: {prev!r} -> {value!r}')
        # this should update before wPlayerID
        if value == DEFAULT_PLAYER_NAME:
            return self
        return self._check_saved_game(value.strip())

    # def wd732_0(self, _p: Any, value: bool, _data: GameData) -> GameState:  # noqa: N815
    #     logger.debug(f'count play time changed: {value}')
    #     return self._check_saved_game(value)

    # def wPlayTimeHours(self, _p: Any, value: int, _data: GameData) -> GameState:  # noqa: N815
    #     logger.debug(f'play time hours changed: {value}')
    #     return self._check_saved_game(value)

    # def wPlayTimeMinutes(self, _p: Any, value: int, _data: GameData) -> GameState:  # noqa: N815
    #     logger.debug(f'play time minutes changed: {value}')
    #     return self._check_saved_game(value)

    # def wPlayTimeSeconds(self, _p: Any, value: int, _data: GameData) -> GameState:  # noqa: N815
    #     logger.debug(f'play time seconds changed: {value}')
    #     return self._check_saved_game(value)

    # def wPlayTimeFrames(self, _p: Any, value: int, _data: GameData) -> GameState:  # noqa: N815
    #     logger.debug(f'play time frames changed: {value}')
    #     return self._check_saved_game(value)

    def _check_saved_game(self, value: Any) -> GameState:
        if value:
            logger.info('found saved game')
            return MainMenuContinue()
        return self


@define
class MainMenuContinue(YellowState):
    _menu_item: int = field(init=False, default=MENU_ITEM_CONTINUE, eq=False, repr=False)
    _map_changed: bool = field(init=False, default=False, eq=False, repr=False)
    _x_changed: bool = field(init=False, default=False, eq=False, repr=False)
    _y_changed: bool = field(init=False, default=False, eq=False, repr=False)

    def wPlayerID(self, prev: int, value: int, _data: GameData) -> GameState:  # noqa: N815
        logger.debug(f'player ID changed: {prev} -> {value}')
        if value == 0:
            return _reset_game()
        if prev > 0:
            return _press_new_game()
        return self

    def wPlayerName(self, prev: str, value: str, _data: GameData) -> GameState:  # noqa: N815
        logger.debug(f'player name changed: {prev!r} -> {value!r}')
        if value == DEFAULT_PLAYER_NAME and not prev.strip():
            return _press_new_game()
        return self

    def wCurrentMenuItem(self, prev: int, value: int, _data: GameData) -> GameState:  # noqa: N815
        logger.debug(f'current menu item changed: {prev} -> {value}')
        self._menu_item = value
        return self

    def wJoyIgnore(self, prev: int, value: int, _data: GameData) -> GameState:  # noqa: N815
        logger.debug(f'joypad ignore mask changed: {prev} -> {value}')
        if value == JOY_MASK_ALL and prev == JOY_MASK_NONE:
            return _press_continue()
        return self

    def wCurMap(self, prev: Any, value: str, _d: GameData) -> GameState:  # noqa: N815
        logger.debug(f'map changed: {prev!r} -> {value!r}')
        if not self._map_changed:
            # first loaded map
            self._map_changed = True
            return self
        if self._menu_item == MENU_ITEM_CONTINUE:
            # already late
            return _press_continue()
        elif self._menu_item == MENU_ITEM_NEW_GAME:
            return _press_new_game()
        return self

    def wXCoord(self, prev: int, value: int, data: GameData) -> GameState:  # noqa: N815
        # safety net in case we miss an update to wJoyIgnore
        logger.debug(f'player x coordinate changed: {prev} -> {value}')
        if not self._x_changed:
            # first loaded coordinates
            self._x_changed = True
            return self
        if self._menu_item == MENU_ITEM_CONTINUE:
            # already late
            return _press_continue()
        elif self._menu_item == MENU_ITEM_NEW_GAME:
            return _press_new_game()
        return self

    def wYCoord(self, prev: int, value: int, data: GameData) -> GameState:  # noqa: N815
        # safety net in case we miss an update to wJoyIgnore
        logger.debug(f'player y coordinate changed: {prev} -> {value}')
        if not self._y_changed:
            # first loaded coordinates
            self._y_changed = True
            return self
        if self._menu_item == MENU_ITEM_CONTINUE:
            # already late
            return _press_continue()
        elif self._menu_item == MENU_ITEM_NEW_GAME:
            return _press_new_game()
        return self


@define
class InGame(YellowState):
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
            if not data.is_vs_wild:
                if data.trainer.trainer_class == TRAINER_CLASS_CHAMPION:
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
