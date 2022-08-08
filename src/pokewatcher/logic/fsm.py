# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Any, Final, Mapping

import logging

from attrs import define, field

from pokewatcher.events import Event

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

    def on_property_changed(self, prop: str, prev: Any, value: Any, data: Mapping[str, Any]):
        new_state = self.state.on_property_changed(prop, prev, value, data)
        if new_state is not self.state:
            logger.info(f'state transition: {self.state.name} -> {new_state.name}')
        self.state = new_state
