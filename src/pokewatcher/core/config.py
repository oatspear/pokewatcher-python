# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Any, Callable, Dict, Final, Iterable, Tuple

import logging
from logging.config import dictConfig
from pathlib import Path

from attrs import field, frozen
import yaml

from pokewatcher.errors import PokeWatcherConfigurationError

###############################################################################
# Constants
###############################################################################

logger = logging.getLogger(__name__)

DEFAULT_SETTINGS_PATH: Final[Path] = Path.cwd() / 'pokewatcher.yml'


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
            for k, item in value.items():
                if not isinstance(item, self.types):
                    path = f'{key}[{k}]'
                    raise PokeWatcherConfigurationError.bad_type(path, self.types, item)


SCHEMA: Final[Dict[str, Param]] = {
    'options': {
        'loop_frequency': Param.with_default(50.0),
    },
    'retroarch': {
        'host': Param.with_default('127.0.0.1'),
        'port': Param.with_default(55355),
        'timeout': Param.with_default(3.0),
    },
    'gamehook': {
        'host': Param.with_default('localhost'),
        'port': Param.with_default(8085),
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
        'trainers': DictParam.optional(str, list),
    },
    'livesplit': {
        'enabled': Param.with_default(False),
        'host': Param.with_default('localhost'),
        'port': Param.with_default(16834),
        'timeout': Param.with_default(3.0),
    },
    'obsstudio': {
        'enabled': Param.with_default(False),
        'host': Param.with_default('localhost'),
        'port': Param.with_default(4455),
        'password': Param.optional(str),
    },
}

DEFAULTS: Final[Dict[str, Any]] = {
    'options': {'loop_frequency': 50.0},
    'retroarch': {
        'host': '127.0.0.1',
        'port': 55355,
        'timeout': 3.0,
    },
    'gamehook': {
        'host': 'localhost',
        'port': 8085,
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
        path = DEFAULT_SETTINGS_PATH
        if not path.is_file():
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
        path = DEFAULT_SETTINGS_PATH
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
                param.validate(value, subpath)

    def _fail_expects_map(self, path: str):
        raise PokeWatcherConfigurationError.expects_map(path)

    def _fail_required(self, path: str, types: Iterable[Callable]):
        raise PokeWatcherConfigurationError.required(path, types)
