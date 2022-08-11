# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Any

###############################################################################
# Base Class
###############################################################################


class PokeWatcherError(Exception):
    pass


class StateMachineError(PokeWatcherError):
    @classmethod
    def no_transition(cls, state: str, label: str, value: Any) -> 'StateMachineError':
        return cls(f'No transition from state {state} via {label} ({value})')

    @classmethod
    def inconsistent(cls, state: str, label: str, value: Any) -> 'StateMachineError':
        return cls(f'Unexpected transition ({label}, {value}) on state {state}')
