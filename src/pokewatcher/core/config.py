# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Any, Dict

import logging
from logging.config import dictConfig

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
    'auto_save': {'enabled': True},
    'save_backup': {
        'enabled': True,
        'n_checks': 5,
        'check_interval': 3.0,
        'min_backup_interval': 1.0,
        'file_name_format': '{rom} - lvl{player["team"]["slot1"]["level"]}-{realtime}-{location}.srm',
        'dest_dir': '.',
    },
    'splitter': {'enabled': True},
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
