# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from pokewatcher.data.yellow.gamehook import LABELS
from pokewatcher.logic.fsm import transition
from pokewatcher.logic.yellow.fsm import YellowState

###############################################################################
# State Transitions
###############################################################################

def test_state_transitions():
    for prop, label in LABELS.items():
        f = getattr(YellowState, label)
        assert f is transition
