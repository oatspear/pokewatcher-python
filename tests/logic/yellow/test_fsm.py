# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from pokewatcher.data.structs import GameData
from pokewatcher.data.yellow.constants import (
    BATTLE_TYPE_LOST,
    BATTLE_TYPE_NONE,
    BATTLE_TYPE_TRAINER,
    BATTLE_TYPE_WILD,
)
from pokewatcher.errors import StateMachineError
import pokewatcher.events as events
from pokewatcher.logic.yellow.fsm import InBattle, Initial, InOverworld, MainMenu, VictorySequence

###############################################################################
# Initial State
###############################################################################


def test_initial_attributes():
    s = Initial()
    assert s.name == 'Initial'
    assert not s.is_battle_state


def test_initial_player_id_no_transition():
    c = events.on_new_game.count
    s1 = Initial()
    data = GameData()
    inputs = [(1, 0), (1, 2), (0, 0)]
    for prev, value in inputs:
        s2 = s1.wPlayerID(prev, value, data)
        assert s2 is s1
        assert events.on_new_game.count == c


def test_initial_player_id_new_game():
    c = events.on_new_game.count
    s1 = Initial()
    data = GameData()
    s2 = s1.wPlayerID(0, 1, data)
    assert isinstance(s2, InOverworld)
    assert events.on_new_game.count == c + 1


###############################################################################
# MainMenu State
###############################################################################


def test_main_menu_attributes():
    s = MainMenu()
    assert s.name == 'MainMenu'
    assert not s.is_battle_state


def test_main_menu_player_id_no_transition():
    c = events.on_continue.count
    s1 = MainMenu()
    data = GameData()
    inputs = [(1, 0), (1, 2), (0, 0)]
    for prev, value in inputs:
        s2 = s1.wPlayerID(prev, value, data)
        assert s2 is s1
        assert events.on_continue.count == c


def test_main_menu_player_id_continue():
    c = events.on_continue.count
    s1 = MainMenu()
    data = GameData()
    s2 = s1.wPlayerID(0, 1, data)
    assert isinstance(s2, InOverworld)
    assert events.on_continue.count == c + 1


###############################################################################
# InOverworld State
###############################################################################


def test_in_overworld_attributes():
    s = InOverworld()
    assert s.name == 'InOverworld'
    assert not s.is_battle_state


def test_in_overworld_player_id_no_transition():
    _in_game_player_id_no_transition(InOverworld())


def test_in_overworld_player_id_reset():
    _in_game_player_id_reset(InOverworld())


def test_in_overworld_battle_type_wild():
    c = events.on_battle_started.count
    s1 = InOverworld()
    data = GameData()
    s2 = s1.wIsInBattle(BATTLE_TYPE_NONE, BATTLE_TYPE_WILD, data)
    assert s2 is not s1
    assert isinstance(s2, InBattle)
    assert events.on_battle_started.count == c + 1
    assert data.battle.ongoing
    assert data.battle.is_vs_wild


def test_in_overworld_battle_type_trainer():
    c = events.on_battle_started.count
    s1 = InOverworld()
    data = GameData()
    data.battle.trainer.trainer_class = 'TRAINER'
    s2 = s1.wIsInBattle(BATTLE_TYPE_NONE, BATTLE_TYPE_TRAINER, data)
    assert s2 is not s1
    assert isinstance(s2, InBattle)
    assert events.on_battle_started.count == c + 1
    assert data.battle.ongoing
    assert not data.battle.is_vs_wild


def test_in_overworld_battle_type_lost():
    c = events.on_blackout.count
    s1 = InOverworld()
    data = GameData()
    s2 = s1.wIsInBattle(BATTLE_TYPE_NONE, BATTLE_TYPE_LOST, data)
    assert s2 is s1
    assert events.on_blackout.count == c + 1


def test_in_overworld_battle_type_none():
    c = events.on_battle_started.count
    s1 = InOverworld()
    data = GameData()
    s2 = s1.wIsInBattle(BATTLE_TYPE_WILD, BATTLE_TYPE_NONE, data)
    assert s2 is s1
    assert events.on_battle_started.count == c


###############################################################################
# InBattle State
###############################################################################


def test_in_battle_attributes():
    s = InBattle()
    assert s.name == 'InBattle'
    assert s.is_battle_state


def test_in_battle_player_id_no_transition():
    _in_game_player_id_no_transition(InBattle())


def test_in_battle_player_id_reset():
    _in_game_player_id_reset(InBattle())


def test_in_battle_battle_type_none():
    c = events.on_battle_ended.count
    s1 = InBattle()
    data = GameData()
    data.battle.ongoing = True
    s2 = s1.wIsInBattle(BATTLE_TYPE_WILD, BATTLE_TYPE_NONE, data)
    assert s2 is not s1
    assert isinstance(s2, InOverworld)
    assert events.on_battle_ended.count == c + 1
    assert data.battle.ongoing is False


def test_in_battle_battle_type_other():
    c = events.on_battle_ended.count
    s = InBattle()
    data = GameData()
    data.battle.ongoing = True
    values = [BATTLE_TYPE_WILD, BATTLE_TYPE_TRAINER, BATTLE_TYPE_LOST]
    for value in values:
        try:
            s.wIsInBattle(BATTLE_TYPE_WILD, value, data)
            raise AssertionError()
        except StateMachineError:
            assert data.battle.ongoing is True
            assert events.on_battle_ended.count == c


def test_in_battle_alarm_disabled():
    c = events.on_battle_ended.count
    s1 = InBattle()
    data = GameData()
    data.battle.ongoing = True
    s2 = s1.wLowHealthAlarmDisabled(False, True, data)
    assert s2 is not s1
    assert isinstance(s2, VictorySequence)
    assert events.on_battle_ended.count == c + 1
    assert data.battle.is_victory


def test_in_battle_alarm_enabled():
    c = events.on_battle_ended.count
    s1 = InBattle()
    data = GameData()
    data.battle.ongoing = True
    s2 = s1.wLowHealthAlarmDisabled(True, False, data)
    assert s2 is s1
    assert events.on_battle_ended.count == c
    assert data.battle.ongoing


###############################################################################
# VictorySequence State
###############################################################################


def test_victory_sequence_attributes():
    s = VictorySequence()
    assert s.name == 'VictorySequence'
    assert s.is_battle_state


def test_victory_sequence_player_id_no_transition():
    _in_game_player_id_no_transition(VictorySequence())


def test_victory_sequence_player_id_reset():
    _in_game_player_id_reset(VictorySequence())


def test_victory_sequence_battle_type_none():
    c = events.on_battle_ended.count
    s1 = VictorySequence()
    data = GameData()
    s2 = s1.wIsInBattle(BATTLE_TYPE_WILD, BATTLE_TYPE_NONE, data)
    assert s2 is not s1
    assert isinstance(s2, InOverworld)
    assert events.on_battle_ended.count == c


def test_victory_sequence_battle_type_other():
    s = VictorySequence()
    data = GameData()
    values = [BATTLE_TYPE_WILD, BATTLE_TYPE_TRAINER, BATTLE_TYPE_LOST]
    for value in values:
        try:
            s.wIsInBattle(BATTLE_TYPE_WILD, value, data)
            raise AssertionError()
        except StateMachineError:
            pass


def test_victory_sequence_alarm_disabled():
    s = VictorySequence()
    data = GameData()
    try:
        s.wLowHealthAlarmDisabled(False, True, data)
        raise AssertionError()
    except StateMachineError:
        pass


###############################################################################
# Helper Functions
###############################################################################


def _in_game_player_id_no_transition(s1):
    c = events.on_reset.count
    data = GameData()
    inputs = [(0, 1), (1, 2)]
    for prev, value in inputs:
        s2 = s1.wPlayerID(prev, value, data)
        assert s2 is s1
        assert events.on_reset.count == c


def _in_game_player_id_reset(s1):
    data = GameData()
    inputs = [(0, 0), (1, 0)]
    for prev, value in inputs:
        c = events.on_reset.count
        s2 = s1.wPlayerID(prev, value, data)
        assert s2 is not s1
        assert isinstance(s2, MainMenu)
        assert events.on_reset.count == c + 1
