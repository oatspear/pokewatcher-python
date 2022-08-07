# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Any, Final, Mapping

import logging

from attrs import define, field

import pokewatcher.events as events

###############################################################################
# Constants
###############################################################################

logger: Final[logging.Logger] = logging.getLogger(__name__)

###############################################################################
# Interface
###############################################################################


@define
class StateMachine:
    state: GameState
    watching: bool = field(init=False, default=False, repr=False)

    def watch_events(self):
        if self.watching:
            raise RuntimeError('already initialized')
        self.watching = True
        events.on_property_changed.watch(self.on_property_changed)
        self._watch_custom_events()

    def forget_events(self):
        if self.watching:
            self.watching = False
            events.on_property_changed.forget(self.on_property_changed)
            self._forget_custom_events()

    def on_property_changed(self, prop: str, prev: Any, value: Any, data: Mapping[str, Any]):
        new_state = self.state.on_property_changed(prop, prev, value, data)
        if new_state is not self.state:
            logger.info(f'state transition: {self.state.name} -> {new_state.name}')
        self.state = new_state

    def _watch_custom_events(self):
        # state transitions for subclasses
        return

    def _forget_custom_events(self):
        return
