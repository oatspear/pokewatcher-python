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
    DEFAULT_PLAYER_NAME,
    JOY_MASK_ALL,
    JOY_MASK_A_BUTTON,
    JOY_MASK_NONE,
    WRAM_BATTLE_TYPE,
    WRAM_JOY_IGNORE,
    WRAM_PLAYER_ID,
    WRAM_PLAYER_NAME,
)
from pokewatcher.errors import StateMachineError
import pokewatcher.events as events
from pokewatcher.logic.yellow.fsm import (
    InBattle,
    Initial,
    InOverworld,
    MainMenu,
    MainMenuContinue,
    VictorySequence,
)

###############################################################################
# Initial State
###############################################################################


def test_initial_attributes():
    s = Initial()
    assert s.name == 'Initial'
    assert not s.is_battle_state


def test_initial_player_name_no_transition():
    check_no_transition(
        Initial,
        WRAM_PLAYER_NAME,
        (DEFAULT_PLAYER_NAME, 'TEST'),
        (DEFAULT_PLAYER_NAME, ''),
        emitted=(),
    )


def test_initial_player_name_transition():
    check_transition_happens(
        Initial,
        MainMenu,
        WRAM_PLAYER_NAME,
        ('', DEFAULT_PLAYER_NAME),
        ('TEST', DEFAULT_PLAYER_NAME),
        emitted=(),
    )


###############################################################################
# MainMenu State
###############################################################################


def test_main_menu_attributes():
    s = MainMenu()
    assert s.name == 'MainMenu'
    assert not s.is_battle_state


def test_main_menu_player_id_no_transition():
    check_no_transition(
        MainMenu,
        WRAM_PLAYER_ID,
        (1, 2),
        emitted=(),
    )


def test_main_menu_player_id_reset():
    check_transition_happens(
        MainMenu,
        Initial,
        WRAM_PLAYER_ID,
        (-1, 0),
        (1, 0),
        emitted=['on_reset'],
    )


def test_main_menu_player_id_new_game():
    check_transition_happens(
        MainMenu,
        InOverworld,
        WRAM_PLAYER_ID,
        (-1, 1),
        (0, 1),
        emitted=['on_new_game'],
    )


def test_main_menu_player_name_no_transition():
    check_no_transition(
        MainMenu,
        WRAM_PLAYER_NAME,
        ('', DEFAULT_PLAYER_NAME),
        ('TEST', DEFAULT_PLAYER_NAME),
        ('TEST', ''),
        ('TEST', '   '),
        (DEFAULT_PLAYER_NAME, ''),
        (DEFAULT_PLAYER_NAME, '   '),
        emitted=(),
    )


def test_main_menu_player_name_saved_game():
    check_transition_happens(
        MainMenu,
        MainMenuContinue,
        WRAM_PLAYER_NAME,
        ('', 'TEST'),
        ('       ', 'TEST'),
        (DEFAULT_PLAYER_NAME, 'TEST'),
        emitted=(),
    )


###############################################################################
# MainMenuContinue State
###############################################################################


def test_menu_continue_attributes():
    s = MainMenuContinue()
    assert s.name == 'MainMenuContinue'
    assert not s.is_battle_state


def test_menu_continue_player_id_no_transition():
    check_no_transition(
        MainMenuContinue,
        WRAM_PLAYER_ID,
        (0, 1),
        (-1, 1),
        emitted=(),
    )


def test_menu_continue_player_id_reset():
    check_transition_happens(
        MainMenuContinue,
        Initial,
        WRAM_PLAYER_ID,
        (-1, 0),
        (1, 0),
        emitted=['on_reset'],
    )


def test_menu_continue_player_id_new_game():
    check_transition_happens(
        MainMenuContinue,
        InOverworld,
        WRAM_PLAYER_ID,
        (1, 2),
        emitted=['on_new_game'],
    )


def test_menu_continue_player_name_no_transition():
    check_no_transition(
        MainMenuContinue,
        WRAM_PLAYER_NAME,
        ('TEST', DEFAULT_PLAYER_NAME),
        ('TEST', ''),
        ('TEST', '   '),
        (DEFAULT_PLAYER_NAME, ''),
        (DEFAULT_PLAYER_NAME, '   '),
        ('', 'TEST'),
        ('       ', 'TEST'),
        (DEFAULT_PLAYER_NAME, 'TEST'),
        emitted=(),
    )


def test_menu_continue_player_name_new_game():
    check_transition_happens(
        MainMenuContinue,
        InOverworld,
        WRAM_PLAYER_NAME,
        ('', DEFAULT_PLAYER_NAME),
        ('    ', DEFAULT_PLAYER_NAME),
        emitted=['on_new_game'],
    )


def test_menu_continue_joy_ignore_no_transition():
    check_no_transition(
        MainMenuContinue,
        WRAM_JOY_IGNORE,
        (JOY_MASK_NONE, JOY_MASK_A_BUTTON),
        (JOY_MASK_ALL, JOY_MASK_A_BUTTON),
        (JOY_MASK_A_BUTTON, JOY_MASK_ALL),
        emitted=(),
    )


def test_menu_continue_joy_ignore_continue():
    check_transition_happens(
        MainMenuContinue,
        InOverworld,
        WRAM_JOY_IGNORE,
        (JOY_MASK_NONE, JOY_MASK_ALL),
        emitted=['on_continue'],
    )


###############################################################################
# InOverworld State
###############################################################################


def test_in_overworld_attributes():
    s = InOverworld()
    assert s.name == 'InOverworld'
    assert not s.is_battle_state


def test_in_overworld_player_id_no_transition():
    check_no_transition(
        InOverworld,
        WRAM_PLAYER_ID,
        (-1, 1),
        (0, 1),
        (1, 2),
        emitted=(),
    )


def test_in_overworld_player_id_reset():
    check_transition_happens(
        InOverworld,
        Initial,
        WRAM_PLAYER_ID,
        (0, 0),
        (1, 0),
        (-1, 0),
        emitted=['on_reset'],
    )


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
    check_no_transition(
        InOverworld,
        WRAM_BATTLE_TYPE,
        (BATTLE_TYPE_NONE, BATTLE_TYPE_LOST),
        emitted=['on_blackout'],
    )


def test_in_overworld_battle_type_none():
    check_no_transition(
        InOverworld,
        WRAM_BATTLE_TYPE,
        (BATTLE_TYPE_WILD, BATTLE_TYPE_NONE),
        emitted=(),
    )


###############################################################################
# InBattle State
###############################################################################


def test_in_battle_attributes():
    s = InBattle()
    assert s.name == 'InBattle'
    assert s.is_battle_state


def test_in_battle_player_id_no_transition():
    check_no_transition(
        InBattle,
        WRAM_PLAYER_ID,
        (-1, 1),
        (0, 1),
        (1, 2),
        emitted=(),
    )


def test_in_battle_player_id_reset():
    check_transition_happens(
        InBattle,
        Initial,
        WRAM_PLAYER_ID,
        (0, 0),
        (1, 0),
        (-1, 0),
        emitted=['on_reset'],
    )


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


def test_in_battle_battle_type_lost():
    c = events.on_battle_ended.count
    s1 = InBattle()
    data = GameData()
    data.battle.ongoing = True
    s2 = s1.wIsInBattle(BATTLE_TYPE_WILD, BATTLE_TYPE_LOST, data)
    assert s2 is not s1
    assert isinstance(s2, InOverworld)
    assert events.on_battle_ended.count == c + 1
    assert data.battle.ongoing is False
    assert data.battle.is_defeat


def test_in_battle_battle_type_other():
    c = events.on_battle_ended.count
    s = InBattle()
    data = GameData()
    data.battle.ongoing = True
    values = [BATTLE_TYPE_WILD, BATTLE_TYPE_TRAINER]
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
    check_no_transition(
        VictorySequence,
        WRAM_PLAYER_ID,
        (-1, 1),
        (0, 1),
        (1, 2),
        emitted=(),
    )


def test_victory_sequence_player_id_reset():
    check_transition_happens(
        VictorySequence,
        Initial,
        WRAM_PLAYER_ID,
        (0, 0),
        (1, 0),
        (-1, 0),
        emitted=['on_reset'],
    )


def test_victory_sequence_battle_type_none():
    check_transition_happens(
        VictorySequence,
        InOverworld,
        WRAM_BATTLE_TYPE,
        (BATTLE_TYPE_WILD, BATTLE_TYPE_NONE),
        emitted=(),
    )


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


def check_transition_happens(state1, state2, label, *inputs, emitted=()):
    counts = [getattr(events, name).count for name in emitted]
    s1 = state1()
    data = GameData()
    for prev, value in inputs:
        transition = getattr(s1, label)
        s2 = transition(prev, value, data)
        assert s2 != s1, f'expected different state: {s1} == {s2}'
        assert isinstance(s2, state2), f'expected {state2.__name__}, got {s2}'
        for i in range(len(emitted)):
            c = counts[i]
            e = getattr(events, emitted[i])
            assert e.count > c, f'expected one event: {e} ({e.count} <= {c})'


def check_no_transition(state1, label, *inputs, emitted=()):
    counts = [getattr(events, name).count for name in emitted]
    s1 = state1()
    data = GameData()
    for prev, value in inputs:
        transition = getattr(s1, label)
        s2 = transition(prev, value, data)
        assert s2 is s1, f'expected same state: {s1} != {s2}'
        for i in range(len(emitted)):
            c = counts[i]
            e = getattr(events, emitted[i])
            assert e.count > c, f'expected one event: {e} ({e.count} <= {c})'
