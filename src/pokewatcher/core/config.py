# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Any, Callable, Dict, Final, Iterable, List, Tuple

import logging
from logging.config import dictConfig
from pathlib import Path

from attrs import define, field, frozen
import yaml

from pokewatcher.data.constants import (
    VAR_BATTLE_PLAYER_ATTACK,
    VAR_BATTLE_PLAYER_DEFENSE,
    VAR_BATTLE_PLAYER_SP_ATTACK,
    VAR_BATTLE_PLAYER_SP_DEFENSE,
    VAR_BATTLE_PLAYER_SPEED,
    VAR_BATTLE_PLAYER_STAGE_ACCURACY,
    VAR_BATTLE_PLAYER_STAGE_ATTACK,
    VAR_BATTLE_PLAYER_STAGE_DEFENSE,
    VAR_BATTLE_PLAYER_STAGE_EVASION,
    VAR_BATTLE_PLAYER_STAGE_SP_ATTACK,
    VAR_BATTLE_PLAYER_STAGE_SP_DEFENSE,
    VAR_BATTLE_PLAYER_STAGE_SPEED,
    VAR_PARTY_MON1_LEVEL,
    VAR_PARTY_MON1_MOVE1,
    VAR_PARTY_MON1_MOVE2,
    VAR_PARTY_MON1_MOVE3,
    VAR_PARTY_MON1_MOVE4,
    VAR_PARTY_MON1_SPECIES,
)
from pokewatcher.errors import PokeWatcherConfigurationError

###############################################################################
# Constants
###############################################################################

logger = logging.getLogger(__name__)


@frozen
class Param:
    is_required: bool = False
    types: Tuple[Callable] = field(factory=lambda: (str,))
    default: Any = None

    @classmethod
    def with_default(cls, value: Any) -> 'Param':
        types = (type(value),)
        return cls(is_required=False, types=types, default=value)

    @classmethod
    def required(cls, *types: Iterable[Callable]) -> 'Param':
        return cls(is_required=True, types=tuple(types))

    @classmethod
    def optional(cls, *types: Iterable[Callable], default: Any = None) -> 'Param':
        return cls(is_required=False, types=tuple(types), default=default)

    def validate(self, value: Any, key: str):
        if value is None:
            if self.is_required:
                raise PokeWatcherConfigurationError.required(key, self.types)
        else:
            self._validate_value(value, key)

    def check_presence(self, value: Any, key: str):
        if value is None:
            if self.is_required:
                raise PokeWatcherConfigurationError.required(key, self.types)

    def _validate_value(self, value: Any, key: str):
        if not isinstance(value, self.types):
            raise PokeWatcherConfigurationError.bad_type(key, self.types, value)


@frozen
class ListParam(Param):
    allows_empty: bool = True
    allows_alias: bool = False

    @classmethod
    def required(cls, *types: Iterable[Callable], allows_empty: bool = False) -> 'ListParam':
        return cls(is_required=True, types=tuple(types), allows_empty=allows_empty)

    def _validate_value(self, value: Any, key: str):
        if isinstance(value, str):
            if not self.allows_alias:
                raise PokeWatcherConfigurationError.expects_list(key, self.types)
        else:
            if not isinstance(value, list):
                raise PokeWatcherConfigurationError.expects_list(key, self.types)
            if len(value) == 0 and not self.allows_empty:
                raise PokeWatcherConfigurationError.no_empty(key)
            for item in value:
                if not isinstance(item, self.types):
                    path = key + '[item]'
                    raise PokeWatcherConfigurationError.bad_type(path, self.types, item)


@frozen
class DictParam(Param):
    allows_empty: bool = True
    allows_alias: bool = False

    @classmethod
    def optional_alias(cls, *types: Iterable[Callable], default: Any = None) -> 'DictParam':
        return cls(is_required=False, types=tuple(types), default=default, allows_alias=True)

    def _validate_value(self, value: Any, key: str):
        if isinstance(value, str):
            if not self.allows_alias:
                raise PokeWatcherConfigurationError.expects_map(key)
        else:
            if not isinstance(value, dict):
                raise PokeWatcherConfigurationError.expects_map(key)
            if len(value) == 0 and not self.allows_empty:
                raise PokeWatcherConfigurationError.no_empty(key)
            for k, item in value.values():
                if not isinstance(item, self.types):
                    path = f'{key}[{k}]'
                    raise PokeWatcherConfigurationError.bad_type(path, self.types, item)


SCHEMA: Final[Dict[str, Param]] = {
    'options': {
        'update_frequency': Param.with_default(50.0),
    },
    'retroarch': {
        'host': Param.with_default('127.0.0.1'),
        'port': Param.with_default(55355),
        'timeout': Param.with_default(3.0),
    },
    'gamehook': {
        'url': {
            'signalr': Param.with_default('http://localhost:8085/updates'),
            'requests': Param.with_default('http://localhost:8085/mapper'),
        },
    },
    'auto_save': {
        'enabled': Param.with_default(False),
        'maps': DictParam.optional(str, dict),
    },
    'save_backup': {
        'enabled': Param.with_default(True),
        'n_checks': Param.with_default(5),
        'check_interval': Param.with_default(3.0),
        'min_backup_interval': Param.with_default(1.0),
        'file_name_format': Param.with_default('{rom}-{realtime}.srm'),
        'dest_dir': Param.with_default('.'),
    },
    'splitter': {
        'enabled': Param.with_default(True),
        'labels': DictParam.optional(str),
        'output': {
            'csv': {
                'path': Param.with_default('{rom}.csv'),
                'labels': DictParam.optional(str),
                'attributes': ListParam.required(str, allows_empty=False),
            }
        },
        'trainers': DictParam.optional_alias(list),
    },
    'livesplit': {
        'enabled': Param.with_default(False),
        'host': Param.with_default('localhost'),
        'port': Param.with_default(16834),
        'timeout': Param.with_default(3.0),
    },
    'obsstudio': {
        'enabled': Param.with_default(False),
        'url': Param.with_default('ws://localhost:4455'),
        'password': Param.optional(str),
    },
}

DEFAULTS: Final[Dict[str, Any]] = {
    'options': {'update_frequency': 50.0},
    'retroarch': {
        'host': '127.0.0.1',
        'port': 55355,
        'timeout': 3.0,
    },
    'gamehook': {
        'url': {
            'signalr': 'http://localhost:8085/updates',
            'requests': 'http://localhost:8085/mapper',
        },
    },
    'auto_save': {
        'enabled': True,
        'maps': {
            'Pokemon Red and Blue': 'Pokemon Yellow',
            'Pokemon Yellow': {
                'always': {
                    'Kanto': [
                        'Viridian Forest',
                        'Silph Co - 1F',
                        'Indigo Plateau - Lobby',
                        'Viridian City - Gym',
                        'Pewter City - Gym',
                        'Cerulean City - Gym',
                        'Vermilion City - Gym',
                        'Celadon City - Gym',
                        'Fuchsia City - Gym',
                        'Saffron City - Gym',
                        'Cinnabar Island - Gym',
                        "Lorelei's Room",
                        "Bruno's Room",
                        "Agatha's Room",
                        "Lance's Room",
                        'Champions Room',
                        'Route 22',
                    ]
                },
                'once': {
                    'Kanto': [
                        'Viridian City',
                        'Pewter City',
                        'Cerulean City',
                        'Lavender Town',
                        'Vermilion City',
                        'Celadon City',
                        'Fuchsia City',
                        'Cinnabar Island',
                        'Saffron City',
                        'Rock Tunnel - 1',
                        'Mt Moon - 1',
                        'Victory Road',
                        'Pokemon Tower - 1F',
                        'Route 1',
                        'Route 2',
                        'Route 3',
                        'Route 4',
                        'Route 5',
                        'Route 6',
                        'Route 7',
                        'Route 8',
                        'Route 9',
                        'Route 10',
                        'Route 11',
                        'Route 12',
                        'Route 13',
                        'Route 14',
                        'Route 15',
                        'Route 16',
                        'Route 17',
                        'Route 18',
                        'Route 19',
                        'Route 20',
                        'Route 21',
                        'Route 23',
                        'Route 24',
                        'Route 25',
                    ]
                },
            },
        },
    },
    'save_backup': {
        'enabled': True,
        'n_checks': 5,
        'check_interval': 3.0,
        'min_backup_interval': 1.0,
        'file_name_format': '{rom} - lvl{player.team.slot1.level}-{realtime}-{location}.srm',
        'dest_dir': '.',
    },
    'splitter': {
        'enabled': True,
        'labels': {},
        'output': {
            'csv': {
                'path': '{rom}.csv',
                'labels': {
                    'rom': 'ROM',
                    VAR_PARTY_MON1_SPECIES: 'Species',
                    'trainer_name': 'Trainer',
                    'realtime.end.hours': 'RTHours',
                    'realtime.end.minutes': 'RTMinutes',
                    'realtime.end.seconds': 'RTSeconds',
                    'realtime.end.millis': 'RTMilliseconds',
                    'realtime.start': 'Start Time',
                    'realtime.end': 'Real Time',
                    'time': 'Game Time',
                    VAR_PARTY_MON1_LEVEL: 'Level',
                    VAR_PARTY_MON1_MOVE1: 'Move 1',
                    VAR_PARTY_MON1_MOVE2: 'Move 2',
                    VAR_PARTY_MON1_MOVE3: 'Move 3',
                    VAR_PARTY_MON1_MOVE4: 'Move 4',
                    'previous.team.slot1.stats.attack': 'Attack',
                    'previous.team.slot1.stats.defense': 'Defense',
                    'previous.team.slot1.stats.sp_attack': 'Sp. Attack',
                    'previous.team.slot1.stats.sp_defense': 'Sp. Defense',
                    'previous.team.slot1.stats.speed': 'Speed',
                    VAR_BATTLE_PLAYER_STAGE_ATTACK: 'Attack Stage',
                    VAR_BATTLE_PLAYER_STAGE_DEFENSE: 'Defense Stage',
                    VAR_BATTLE_PLAYER_STAGE_SP_ATTACK: 'Sp. Attack Stage',
                    VAR_BATTLE_PLAYER_STAGE_SP_DEFENSE: 'Sp. Defense Stage',
                    VAR_BATTLE_PLAYER_STAGE_SPEED: 'Speed Stage',
                    VAR_BATTLE_PLAYER_STAGE_ACCURACY: 'Accuracy Stage',
                    VAR_BATTLE_PLAYER_STAGE_EVASION: 'Evasion Stage',
                    VAR_BATTLE_PLAYER_ATTACK: 'Battle Attack',
                    VAR_BATTLE_PLAYER_DEFENSE: 'Battle Defense',
                    VAR_BATTLE_PLAYER_SP_ATTACK: 'Battle Sp. Attack',
                    VAR_BATTLE_PLAYER_SP_DEFENSE: 'Battle Sp. Defense',
                    VAR_BATTLE_PLAYER_SPEED: 'Battle Speed',
                    'resets': 'Resets',
                },
                'attributes': [
                    'rom',
                    VAR_PARTY_MON1_SPECIES,
                    'trainer_name',
                    'realtime.start',
                    'realtime.end',
                    'time',
                    VAR_PARTY_MON1_LEVEL,
                    'resets',
                    'realtime.end.hours',
                    'realtime.end.minutes',
                    'realtime.end.seconds',
                    'realtime.end.millis',
                    VAR_PARTY_MON1_MOVE1,
                    VAR_PARTY_MON1_MOVE2,
                    VAR_PARTY_MON1_MOVE3,
                    VAR_PARTY_MON1_MOVE4,
                    'previous.team.slot1.stats.attack',
                    'previous.team.slot1.stats.defense',
                    'previous.team.slot1.stats.sp_attack',
                    'previous.team.slot1.stats.sp_defense',
                    'previous.team.slot1.stats.speed',
                    VAR_BATTLE_PLAYER_STAGE_ATTACK,
                    VAR_BATTLE_PLAYER_STAGE_DEFENSE,
                    VAR_BATTLE_PLAYER_STAGE_SP_ATTACK,
                    VAR_BATTLE_PLAYER_STAGE_SP_DEFENSE,
                    VAR_BATTLE_PLAYER_STAGE_SPEED,
                    VAR_BATTLE_PLAYER_STAGE_ACCURACY,
                    VAR_BATTLE_PLAYER_STAGE_EVASION,
                    VAR_BATTLE_PLAYER_ATTACK,
                    VAR_BATTLE_PLAYER_DEFENSE,
                    VAR_BATTLE_PLAYER_SP_ATTACK,
                    VAR_BATTLE_PLAYER_SP_DEFENSE,
                    VAR_BATTLE_PLAYER_SPEED,
                ],
            }
        },
        'trainers': {
            'Pokemon Red and Blue': 'Pokemon Yellow',
            'Pokemon Yellow': [
                {
                    'class': 'BROCK',
                    'number': 1,
                    'name': 'Brock',
                },
                {
                    'class': 'MISTY',
                    'number': 1,
                    'name': 'Misty',
                },
                {
                    'class': 'LASS',
                    'number': 10,
                    'name': 'Oddish Lass',
                },
                {
                    'class': 'ROCKET',
                    'number': 5,
                    'name': 'Rocket',
                },
                {
                    'class': 'LT.SURGE',
                    'number': 1,
                    'name': 'Lt. Surge',
                },
                {
                    'class': 'JR TRAINER F',
                    'number': 5,
                    'name': 'RTG1 - Wrapping Lass',
                },
                {
                    'class': 'POKEMANIAC',
                    'number': 7,
                    'name': 'RTG2 - Pokemaniac 1',
                },
                {
                    'class': 'POKEMANIAC',
                    'number': 5,
                    'name': 'RTG3 - Pokemaniac 2',
                },
                {
                    'class': 'JR TRAINER F',
                    'number': 10,
                    'name': 'RTG4 - Status Jr Trainer',
                },
                {
                    'class': 'HIKER',
                    'number': 9,
                    'name': 'RTG5 - Self-destructing Hiker',
                },
                {
                    'class': 'JR TRAINER F',
                    'number': 18,
                    'name': 'RTG6 - Finisher',
                },
                {
                    'class': 'ERIKA',
                    'number': 1,
                    'name': 'Erika',
                },
                {
                    'class': 'KOGA',
                    'number': 1,
                    'name': 'Koga',
                },
                {
                    'class': 'BLAINE',
                    'number': 1,
                    'name': 'Blaine',
                },
                {
                    'class': 'SABRINA',
                    'number': 1,
                    'name': 'Sabrina',
                },
                {
                    'class': 'GIOVANNI',
                    'number': 2,
                    'name': 'Giovanni (Silph)',
                },
                {
                    'class': 'GIOVANNI',
                    'number': 3,
                    'name': 'Giovanni',
                },
                {
                    'class': 'LORELEI',
                    'number': 1,
                    'name': 'Lorelei',
                },
                {
                    'class': 'BRUNO',
                    'number': 1,
                    'name': 'Bruno',
                },
                {
                    'class': 'AGATHA',
                    'number': 1,
                    'name': 'Agatha',
                },
                {
                    'class': 'LANCE',
                    'number': 1,
                    'name': 'Lance',
                },
                {
                    'class': 'RIVAL1',
                    'number': 2,
                    'name': 'Rival (Optional)',
                },
                {
                    'class': 'RIVAL1',
                    'number': 3,
                    'name': 'Rival (Nugget Bridge)',
                },
                {
                    'class': 'RIVAL2',
                    'number': 1,
                    'name': 'Rival (SS Anne)',
                },
                {
                    'class': 'RIVAL2',
                    'number': 2,
                    'name': 'Rival (Pokemon Tower)',
                },
                {
                    'class': 'RIVAL2',
                    'number': 3,
                    'name': 'Rival (Pokemon Tower)',
                },
                {
                    'class': 'RIVAL2',
                    'number': 4,
                    'name': 'Rival (Pokemon Tower)',
                },
                {
                    'class': 'RIVAL2',
                    'number': 5,
                    'name': 'Rival (Silph Co.)',
                },
                {
                    'class': 'RIVAL2',
                    'number': 6,
                    'name': 'Rival (Silph Co.)',
                },
                {
                    'class': 'RIVAL2',
                    'number': 7,
                    'name': 'Rival (Silph Co.)',
                },
                {
                    'class': 'RIVAL2',
                    'number': 8,
                    'name': 'Rival (Final)',
                },
                {
                    'class': 'RIVAL2',
                    'number': 9,
                    'name': 'Rival (Final)',
                },
                {
                    'class': 'RIVAL2',
                    'number': 10,
                    'name': 'Rival (Final)',
                },
                {
                    'class': 'RIVAL3',
                    'number': 1,
                    'name': 'Champion',
                },
                {
                    'class': 'RIVAL3',
                    'number': 2,
                    'name': 'Champion',
                },
                {
                    'class': 'RIVAL3',
                    'number': 3,
                    'name': 'Champion',
                },
            ],
            'Pokemon Crystal': [
                {
                    'class': 'RIVAL1',
                    'number': 1,
                    'name': 'Rival 1',
                },
                {
                    'class': 'RIVAL1',
                    'number': 2,
                    'name': 'Rival 1',
                },
                {
                    'class': 'RIVAL1',
                    'number': 3,
                    'name': 'Rival 1',
                },
                {
                    'class': 'FALKNER',
                    'number': 1,
                    'name': 'Falkner',
                },
                {
                    'class': 'RIVAL1',
                    'number': 4,
                    'name': 'Rival 2',
                },
                {
                    'class': 'RIVAL1',
                    'number': 5,
                    'name': 'Rival 2',
                },
                {
                    'class': 'RIVAL1',
                    'number': 6,
                    'name': 'Rival 2',
                },
                {
                    'class': 'BUGSY',
                    'number': 1,
                    'name': 'Bugsy',
                },
                {
                    'class': 'WHITNEY',
                    'number': 1,
                    'name': 'Whitney',
                },
                {
                    'class': 'RIVAL1',
                    'number': 7,
                    'name': 'Rival 3',
                },
                {
                    'class': 'RIVAL1',
                    'number': 8,
                    'name': 'Rival 3',
                },
                {
                    'class': 'RIVAL1',
                    'number': 9,
                    'name': 'Rival 3',
                },
                {
                    'class': 'MORTY',
                    'number': 1,
                    'name': 'Morty',
                },
                {
                    'class': 'CHUCK',
                    'number': 1,
                    'name': 'Chuck',
                },
                {
                    'class': 'PRYCE',
                    'number': 1,
                    'name': 'Pryce',
                },
                {
                    'class': 'JASMINE',
                    'number': 1,
                    'name': 'Jasmine',
                },
                {
                    'class': 'RIVAL1',
                    'number': 10,
                    'name': 'Rival 4',
                },
                {
                    'class': 'RIVAL1',
                    'number': 11,
                    'name': 'Rival 4',
                },
                {
                    'class': 'RIVAL1',
                    'number': 12,
                    'name': 'Rival 4',
                },
                {
                    'class': 'CLAIR',
                    'number': 1,
                    'name': 'Clair',
                },
                {
                    'class': 'WILL',
                    'number': 1,
                    'name': 'Will',
                },
                {
                    'class': 'KOGA',
                    'number': 1,
                    'name': 'Koga',
                },
                {
                    'class': 'BRUNO',
                    'number': 1,
                    'name': 'Bruno',
                },
                {
                    'class': 'KAREN',
                    'number': 1,
                    'name': 'Karen',
                },
                {
                    'class': 'Champion',
                    'number': 1,
                    'name': 'Champion',
                },
                {
                    'class': 'SABRINA',
                    'number': 1,
                    'name': 'Sabrina',
                },
                {
                    'class': 'ERIKA',
                    'number': 1,
                    'name': 'Erika',
                },
                {
                    'class': 'MISTY',
                    'number': 1,
                    'name': 'Misty',
                },
                {
                    'class': 'LT. SURGE',
                    'number': 1,
                    'name': 'Lt. Surge',
                },
                {
                    'class': 'BROCK',
                    'number': 1,
                    'name': 'Brock',
                },
                {
                    'class': 'BLAINE',
                    'number': 1,
                    'name': 'Blaine',
                },
                {
                    'class': 'JANINE',
                    'number': 1,
                    'name': 'Janine',
                },
                {
                    'class': 'BLUE',
                    'number': 1,
                    'name': 'Blue',
                },
                {
                    'class': 'RED',
                    'number': 1,
                    'name': 'Red',
                },
            ],
        },
    },
    'livesplit': {
        'enabled': True,
        'host': 'localhost',
        'port': 16834,
        'timeout': 3.0,
    },
    'obsstudio': {
        'enabled': True,
        'url': 'ws://localhost:4455',
        'password': 'ObH0UK3sW67Q6kvW',
    },
}

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '[%(levelname)s] %(module)s (%(asctime)s): %(message)s',
        },
        'detailed': {
            'format': (
                '[%(levelname)s]'
                '[%(module)s:%(funcName)s:%(lineno)d]'
                '[%(asctime)s]'
                ' %(message)s'
            ),
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'simple',
            'stream': 'ext://sys.stdout',
        },
        'logfile': {
            'class': 'logging.FileHandler',
            'level': 'DEBUG',
            'formatter': 'detailed',
            'filename': 'pokewatcher.log',
            'mode': 'w',
            'encoding': 'utf-8',
        },
    },
    'loggers': {
        '': {
            'level': 'DEBUG',
            'handlers': ['console', 'logfile'],
            'propagate': False,
        },
    },
}

###############################################################################
# Interface
###############################################################################


def load(args: Dict[str, Any]) -> Dict[str, Any]:
    path = args.get('config_path')
    if path is None:
        logger.info('using default settings')
        return DEFAULTS

    logger.info(f'loading settings from {path}')
    try:
        text = path.read_text(encoding='utf-8')
        config = yaml.safe_load(text)

        sanity = SanityChecker(config)
        sanity.check(SCHEMA)

        return config
    except Exception as err:
        logger.error('loading configuration failed: ' + str(err))
        return DEFAULTS


def dump(args: Dict[str, Any]) -> None:
    path = args.get('config_path')
    if path is None:
        path = Path.cwd() / 'pokewatcher.yml'
    text = yaml.dump(DEFAULTS, default_flow_style=False)
    logger.info(f'dumping default settings to {path}')
    path.write_text(text, encoding='utf-8')


def setup_logging() -> None:
    dictConfig(LOGGING_CONFIG)


###############################################################################
# Helper Functions
###############################################################################


@frozen
class SanityChecker:
    data: Dict[str, Any]
    path: str = ''

    def check(self, schema: Dict[str, Any]):
        for key, param in schema.items():
            subpath = key if not self.path else f'{self.path}.{key}'
            value = self.data.get(key)

            if isinstance(param, dict):
                if value is None:
                    value = {}
                if isinstance(value, dict):
                    sanity = SanityChecker(value, path=subpath)
                    sanity.check(param)
                else:
                    self._fail_expects_map(key)
            else:
                assert isinstance(param, Param), f'{param!r} ({type(param)})'
                param.validate(value)

    def _fail_expects_map(self, path: str):
        raise PokeWatcherConfigurationError.expects_map(path)

    def _fail_required(self, path: str, types: Iterable[Callable]):
        raise PokeWatcherConfigurationError.required(path, types)
