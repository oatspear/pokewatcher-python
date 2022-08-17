# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Any, Dict

import logging
from logging.config import dictConfig

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

###############################################################################
# Constants
###############################################################################

logger = logging.getLogger(__name__)

DEFAULTS: Dict[str, Any] = {
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
                        'Route 22',
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
                    'realtime.end.hours',
                    'realtime.end.minutes',
                    'realtime.end.seconds',
                    'realtime.end.millis',
                    'realtime.start',
                    'realtime.end',
                    'time',
                    VAR_PARTY_MON1_LEVEL,
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
                    'resets',
                ],
            }
        },
        'trainers': {
            'Pokemon Red and Blue': 'Pokemon Yellow',
            'Pokemon Yellow': [
                {
                    'class': 'BROCK',
                    'number': 1,
                    'name': 'BROCK',
                },
                {
                    'class': 'MISTY',
                    'number': 1,
                    'name': 'MISTY',
                },
                {
                    'class': 'LASS',
                    'number': 10,
                    'name': 'ODDISH LASS',
                },
                {
                    'class': 'ROCKET',
                    'number': 5,
                    'name': 'ROCKET',
                },
                {
                    'class': 'LT.SURGE',
                    'number': 1,
                    'name': 'LT.SURGE',
                },
                {
                    'class': 'JR TRAINER F',
                    'number': 5,
                    'name': 'RTG1 - WRAPPING LASS',
                },
                {
                    'class': 'POKEMANIAC',
                    'number': 7,
                    'name': 'RTG2 - POKEMANIAC 1',
                },
                {
                    'class': 'POKEMANIAC',
                    'number': 5,
                    'name': 'RTG3 - POKEMANIAC 2',
                },
                {
                    'class': 'JR TRAINER F',
                    'number': 10,
                    'name': 'RTG4 - STATUS JR TRAINER',
                },
                {
                    'class': 'HIKER',
                    'number': 9,
                    'name': 'RTG5 - SELF-DESTRUCTING HIKER',
                },
                {
                    'class': 'JR TRAINER F',
                    'number': 18,
                    'name': 'RTG6 - FINISHER',
                },
                {
                    'class': 'ERIKA',
                    'number': 1,
                    'name': 'ERIKA',
                },
                {
                    'class': 'KOGA',
                    'number': 1,
                    'name': 'KOGA',
                },
                {
                    'class': 'BLAINE',
                    'number': 1,
                    'name': 'BLAINE',
                },
                {
                    'class': 'SABRINA',
                    'number': 1,
                    'name': 'SABRINA',
                },
                {
                    'class': 'GIOVANNI',
                    'number': 2,
                    'name': 'GIOVANNI (SILPH)',
                },
                {
                    'class': 'GIOVANNI',
                    'number': 3,
                    'name': 'GIOVANNI',
                },
                {
                    'class': 'LORELEI',
                    'number': 1,
                    'name': 'LORELEI',
                },
                {
                    'class': 'BRUNO',
                    'number': 1,
                    'name': 'BRUNO',
                },
                {
                    'class': 'AGATHA',
                    'number': 1,
                    'name': 'AGATHA',
                },
                {
                    'class': 'LANCE',
                    'number': 1,
                    'name': 'LANCE',
                },
                {
                    'class': 'RIVAL1',
                    'number': 2,
                    'name': 'RIVAL (OPTIONAL)',
                },
                {
                    'class': 'RIVAL1',
                    'number': 3,
                    'name': 'RIVAL (NUGGET BRIDGE)',
                },
                {
                    'class': 'RIVAL2',
                    'number': 1,
                    'name': 'RIVAL (SS ANNE)',
                },
                {
                    'class': 'RIVAL2',
                    'number': 2,
                    'name': 'RIVAL (PKMN TOWER)',
                },
                {
                    'class': 'RIVAL2',
                    'number': 3,
                    'name': 'RIVAL (PKMN TOWER)',
                },
                {
                    'class': 'RIVAL2',
                    'number': 4,
                    'name': 'RIVAL (PKMN TOWER)',
                },
                {
                    'class': 'RIVAL2',
                    'number': 5,
                    'name': 'RIVAL (SILPH CO.)',
                },
                {
                    'class': 'RIVAL2',
                    'number': 6,
                    'name': 'RIVAL (SILPH CO.)',
                },
                {
                    'class': 'RIVAL2',
                    'number': 7,
                    'name': 'RIVAL (SILPH CO.)',
                },
                {
                    'class': 'RIVAL2',
                    'number': 8,
                    'name': 'RIVAL (FINAL)',
                },
                {
                    'class': 'RIVAL2',
                    'number': 9,
                    'name': 'RIVAL (FINAL)',
                },
                {
                    'class': 'RIVAL2',
                    'number': 10,
                    'name': 'RIVAL (FINAL)',
                },
                {
                    'class': 'RIVAL3',
                    'number': 1,
                    'name': 'CHAMPION',
                },
                {
                    'class': 'RIVAL3',
                    'number': 2,
                    'name': 'CHAMPION',
                },
                {
                    'class': 'RIVAL3',
                    'number': 3,
                    'name': 'CHAMPION',
                },
            ],
            'Pokemon Crystal': [
                {
                    'class': 'RIVAL1',
                    'number': 1,
                    'name': 'RIVAL1',
                },
                {
                    'class': 'RIVAL1',
                    'number': 2,
                    'name': 'RIVAL1',
                },
                {
                    'class': 'RIVAL1',
                    'number': 3,
                    'name': 'RIVAL1',
                },
                {
                    'class': 'FALKNER',
                    'number': 1,
                    'name': 'FALKNER',
                },
                {
                    'class': 'RIVAL1',
                    'number': 4,
                    'name': 'RIVAL2',
                },
                {
                    'class': 'RIVAL1',
                    'number': 5,
                    'name': 'RIVAL2',
                },
                {
                    'class': 'RIVAL1',
                    'number': 6,
                    'name': 'RIVAL2',
                },
                {
                    'class': 'BUGSY',
                    'number': 1,
                    'name': 'BUGSY',
                },
                {
                    'class': 'WHITNEY',
                    'number': 1,
                    'name': 'WHITNEY',
                },
                {
                    'class': 'RIVAL1',
                    'number': 7,
                    'name': 'RIVAL3',
                },
                {
                    'class': 'RIVAL1',
                    'number': 8,
                    'name': 'RIVAL3',
                },
                {
                    'class': 'RIVAL1',
                    'number': 9,
                    'name': 'RIVAL3',
                },
                {
                    'class': 'MORTY',
                    'number': 1,
                    'name': 'MORTY',
                },
                {
                    'class': 'CHUCK',
                    'number': 1,
                    'name': 'CHUCK',
                },
                {
                    'class': 'PRYCE',
                    'number': 1,
                    'name': 'PRYCE',
                },
                {
                    'class': 'JASMINE',
                    'number': 1,
                    'name': 'JASMINE',
                },
                {
                    'class': 'RIVAL1',
                    'number': 10,
                    'name': 'RIVAL4',
                },
                {
                    'class': 'RIVAL1',
                    'number': 11,
                    'name': 'RIVAL4',
                },
                {
                    'class': 'RIVAL1',
                    'number': 12,
                    'name': 'RIVAL4',
                },
                {
                    'class': 'CLAIR',
                    'number': 1,
                    'name': 'CLAIR',
                },
                {
                    'class': 'WILL',
                    'number': 1,
                    'name': 'WILL',
                },
                {
                    'class': 'KOGA',
                    'number': 1,
                    'name': 'KOGA',
                },
                {
                    'class': 'BRUNO',
                    'number': 1,
                    'name': 'BRUNO',
                },
                {
                    'class': 'KAREN',
                    'number': 1,
                    'name': 'KAREN',
                },
                {
                    'class': 'CHAMPION',
                    'number': 1,
                    'name': 'CHAMPION',
                },
                {
                    'class': 'SABRINA',
                    'number': 1,
                    'name': 'SABRINA',
                },
                {
                    'class': 'ERIKA',
                    'number': 1,
                    'name': 'ERIKA',
                },
                {
                    'class': 'MISTY',
                    'number': 1,
                    'name': 'MISTY',
                },
                {
                    'class': 'LT. SURGE',
                    'number': 1,
                    'name': 'LT. SURGE',
                },
                {
                    'class': 'BROCK',
                    'number': 1,
                    'name': 'BROCK',
                },
                {
                    'class': 'BLAINE',
                    'number': 1,
                    'name': 'BLAINE',
                },
                {
                    'class': 'JANINE',
                    'number': 1,
                    'name': 'JANINE',
                },
                {
                    'class': 'BLUE',
                    'number': 1,
                    'name': 'BLUE',
                },
                {
                    'class': 'RED',
                    'number': 1,
                    'name': 'RED',
                },
            ],
        },
    },
    'timer': {'enabled': True},
    'video_record': {'enabled': True},
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
    try:
        config: Dict[str, Any] = DEFAULTS
        # with open(args['config_path'], 'r') as file_pointer:
        # yaml.safe_load(file_pointer)

        # arrange and check configs here

        return config
    except Exception as err:
        logger.error('loading configuration failed: ' + str(err))
        return DEFAULTS


def setup_logging() -> None:
    dictConfig(LOGGING_CONFIG)
