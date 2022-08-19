# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Any, Callable, Iterable

###############################################################################
# Base Class
###############################################################################


class PokeWatcherError(Exception):
    pass


class PokeWatcherConfigurationError(PokeWatcherError):
    @classmethod
    def expects_map(cls, key: str) -> PokeWatcherError:
        return cls(f'expected a mapping on "{key}"')

    @classmethod
    def required(cls, key: str, types: Iterable[Callable]) -> PokeWatcherError:
        allowed = []
        for data_type in types:
            allowed.append(data_type.__name__)
        return cls(f'missing required setting "{key}" {allowed}')

    @classmethod
    def bad_type(cls, key: str, types: Iterable[Callable], value: Any) -> PokeWatcherError:
        allowed = []
        for data_type in types:
            allowed.append(data_type.__name__)
        what = type(value).__name__
        return cls(f'expected {allowed} on "{key}", found {what}')

    @classmethod
    def expects_list(cls, key: str, types: Iterable[Callable]) -> PokeWatcherError:
        allowed = []
        for data_type in types:
            allowed.append(data_type.__name__)
        return cls(f'expected list of {allowed} on "{key}"')

    @classmethod
    def no_empty(cls, key: str) -> PokeWatcherError:
        return cls(f'"{key}" must not be empty')


class PokeWatcherComponentError(PokeWatcherError):
    pass


class StateMachineError(PokeWatcherError):
    @classmethod
    def no_transition(cls, state: str, label: str, value: Any) -> 'StateMachineError':
        return cls(f'No transition from state {state} via {label} ({value})')

    @classmethod
    def inconsistent(cls, state: str, label: str, value: Any) -> 'StateMachineError':
        return cls(f'Unexpected transition ({label}, {value}) on state {state}')
