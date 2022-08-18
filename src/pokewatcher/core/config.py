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
