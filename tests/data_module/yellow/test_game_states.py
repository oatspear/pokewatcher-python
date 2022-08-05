# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from pokewatcher.data.yellow.states import (
    BeforeReceivingStarterState,
    InitialState,
    P_MAP,
    P_PLAYER_ID,
)
import pokewatcher.events as events

###############################################################################
# Tests
###############################################################################


def test_initial_state():
    s = InitialState.new({})
    assert s.name == 'Initial'
    assert s.is_game_started is False
    assert s.is_overworld is False
    assert s.is_battle is False


def test_initial_change_dummy_property():
    c = events.on_new_game.count
    s1 = InitialState.new({})
    s2 = s1.on_property_changed('test', 'value', {})
    assert events.on_new_game.count == c
    assert s2 is s1


def test_initial_change_player_id():
    e = events.on_new_game
    c = e.count
    pid0 = {P_PLAYER_ID: 0, P_MAP: ''}
    pid1 = {P_PLAYER_ID: 12345, P_MAP: ''}
    s1 = InitialState.new({})
    s2 = s1.on_property_changed(P_PLAYER_ID, 0, pid0)
    assert e.count == c
    assert s2 is s1
    s2 = s1.on_property_changed(P_PLAYER_ID, 12345, pid1)
    assert e.count == c
    assert s2 is s1
    s2 = s1.on_property_changed(P_PLAYER_ID, 0, pid1)
    assert e.count == c
    assert s2 is s1
    s2 = s1.on_property_changed(P_PLAYER_ID, 12345, pid0)
    assert e.count == (c + 1)
    assert s2 != s1
