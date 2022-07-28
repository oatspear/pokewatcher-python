# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

"""
Module that contains the command line program.

Why does this file exist, and why not put this in __main__?

  In some cases, it is possible to import `__main__.py` twice.
  This approach avoids that. Also see:
  https://click.palletsprojects.com/en/5.x/setuptools/#setuptools-integration

Some of the structure of this file came from this StackExchange question:
  https://softwareengineering.stackexchange.com/q/418600
"""

###############################################################################
# Imports
###############################################################################

from typing import Any, Dict, List, Optional

import argparse
import logging
import sys

from pokewatcher import __version__ as current_version

###############################################################################
# Constants
###############################################################################

logger = logging.getLogger(__name__)

LOG_FILE = Path().resolve() / 'pokewatcher.log'

###############################################################################
# Argument Parsing
###############################################################################


def parse_arguments(argv: Optional[List[str]]) -> Dict[str, Any]:
    msg = 'A short description of the project.'
    parser = argparse.ArgumentParser(description=msg)

    parser.add_argument(
        '--version',
        action='version',
        version=f'{current_version}',
        help='Prints the program version.',
    )

    parser.add_argument(
        'args', metavar='ARG', nargs=argparse.ZERO_OR_MORE, help='An argument for the program.'
    )

    args = parser.parse_args(args=argv)
    return vars(args)


###############################################################################
# Setup
###############################################################################


def load_configs(args: Dict[str, Any]) -> Dict[str, Any]:
    try:
        config: Dict[str, Any] = {}
        # with open(args['config_path'], 'r') as file_pointer:
        # yaml.safe_load(file_pointer)

        # arrange and check configs here

        return config
    except Exception as err:
        # log or raise errors
        print(err, file=sys.stderr)
        if str(err) == 'Really Bad':
            raise err

        # Optional: return some sane fallback defaults.
        sane_defaults: Dict[str, Any] = {}
        return sane_defaults


def _setup_logging():
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.FileHandler(str(LOG_FILE), mode='w'))


###############################################################################
# Commands
###############################################################################


def workflow(args: Dict[str, Any], configs: Dict[str, Any]) -> None:
    print(f'Arguments: {args}')
    print(f'Configurations: {configs}')


###############################################################################
# Entry Point
###############################################################################


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_arguments(argv)

    # setup phase --------------------------------------------------------------
    try:
        config = load_configs(args)
        _setup_logging()
    except KeyboardInterrupt:
        logger.error('Aborted manually.')
        print('Aborted manually.', file=sys.stderr)
        return 1
    except Exception as err:
        logger.exception('Unhandled exception during setup.', err)
        print('Unhandled exception during setup.', file=sys.stderr)
        return 1

    # main phase ---------------------------------------------------------------
    try:
        workflow(args, config)
    except KeyboardInterrupt:
        logger.error('Aborted manually.')
        print('Aborted manually.', file=sys.stderr)
        return 1
    except Exception as err:
        logger.exception('Unhandled exception during execution.', err)
        print('Unhandled exception during execution.', file=sys.stderr)
        return 1

    return 0  # success
