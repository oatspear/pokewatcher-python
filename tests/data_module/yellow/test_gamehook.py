# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from pokewatcher.data.yellow.gamehook import PROPERTIES
from pokewatcher.logic.fsm import transition
from pokewatcher.logic.yellow.fsm import YellowState

###############################################################################
# State Transitions
###############################################################################


def test_state_transitions():
    for prop, metadata in PROPERTIES.items():
        label = metadata.get('label')
        if label:
            f = getattr(YellowState, label)
            assert f is transition, f'invalid label: {prop} -> {label}'
