# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Any, Final, Mapping, Optional

import logging
from pathlib import Path

from attrs import define, field
import yaml

from pokewatcher.core.gamehook import GameHookBridge, GameHookError
from pokewatcher.core.retroarch import RetroArchBridge
from pokewatcher.core.util import SimpleClock
from pokewatcher.data.crystal.gamehook import load_data_handler as load_gen2_data_handler
from pokewatcher.data.emerald.gamehook import load_data_handler as load_gen3_data_handler
from pokewatcher.data.firered.gamehook import load_data_handler as load_gen3_remakes_data_handler
from pokewatcher.data.structs import GameData
from pokewatcher.data.yellow.gamehook import load_data_handler as load_gen1_data_handler
from pokewatcher.logic.crystal.fsm import Initial as InitialCrystalState
from pokewatcher.logic.emerald.fsm import Initial as InitialEmeraldState
from pokewatcher.logic.firered.fsm import Initial as InitialFireRedState
from pokewatcher.logic.fsm import GameState, StateMachine
from pokewatcher.logic.yellow.fsm import Initial as InitialYellowState

###############################################################################
# Constants
###############################################################################

logger: Final[logging.Logger] = logging.getLogger(__name__)

###############################################################################
# Interface
###############################################################################


@define
class GameInterface:
    data: GameData = field(factory=GameData)
    clock: SimpleClock = field(factory=SimpleClock)
    retroarch: RetroArchBridge = field(factory=RetroArchBridge)
    gamehook: GameHookBridge = field(factory=GameHookBridge)
    fsm: StateMachine = field(init=False, factory=StateMachine)

    @property
    def rom(self) -> Optional[str]:
        return self.retroarch.rom

    @property
    def version(self) -> Optional[str]:
        return self.gamehook.game_name

    @property
    def state(self) -> GameState:
        return self.fsm.state

    @property
    def has_custom_clock(self) -> bool:
        return type(self.clock) != SimpleClock

    def data_dict(self) -> Mapping[str, Any]:
        return {
            'rom': self.rom or 'NULL',
            'version': self.version or 'NULL',
            'state': self.state.name,
            'realtime': self.clock.get_elapsed_time(),
            'player': self.data.player,
            'time': self.data.time,
            'location': self.data.location,
            'battle': self.data.battle,
            'custom': self.data.custom,
        }

    def setup(self, settings: Mapping[str, Any]):
        logger.info('setting up infrastructure')
        retroarch = settings['retroarch']
        self.retroarch.setup(retroarch)
        gamehook = settings['gamehook']
        self.gamehook.setup(gamehook)
        self._load_data_handler(gamehook.get('properties', {}))

    def start(self):
        logger.info('starting low-level components')
        self.retroarch.start()
        self.gamehook.start()
        self.clock.reset_start_time()

    def update(self, delta):
        # logger.debug('update')
        self.retroarch.update(delta)
        self.gamehook.update(delta)

    def cleanup(self):
        logger.info('cleaning up')
        self.gamehook.cleanup()
        self.retroarch.cleanup()

    def _load_data_handler(self, properties: Mapping[str, str]):
        logger.info('setting up data handlers')

        version = self.gamehook.game_name.lower()
        if 'yellow' in version:
            self.fsm.state = InitialYellowState()
            load_data_handler = load_gen1_data_handler
        elif 'crystal' in version:
            self.fsm.state = InitialCrystalState()
            load_data_handler = load_gen2_data_handler
        elif 'gold' in version and 'silver' in version:
            self.fsm.state = InitialCrystalState()
            load_data_handler = load_gen2_data_handler
        elif 'emerald' in version:
            self.fsm.state = InitialEmeraldState()
            load_data_handler = load_gen3_data_handler
        elif 'firered' in version:
            self.fsm.state = InitialFireRedState()
            load_data_handler = load_gen3_remakes_data_handler
        elif 'red' in version and 'blue' in version:
            self.fsm.state = InitialYellowState()
            load_data_handler = load_gen1_data_handler
        else:
            raise GameHookError.unknown_game(version)

        config = None
        config_path = properties.get(self.gamehook.game_name)
        if config_path:
            try:
                path = Path(config_path).resolve(strict=True)
                logger.info(f'loading game properties from {path}')
                text = path.read_text(encoding='utf-8')
                config = yaml.safe_load(text)
            except IOError as e:
                logger.error(f'unable to read GameHook properties file: {e}')
        handler = load_data_handler(self.data, self.fsm, properties=config)
        self.gamehook.on_change = handler.on_property_changed
