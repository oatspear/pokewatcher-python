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

from typing import Any, Dict, Final, List, Optional

import argparse
import logging
import sys

from pokewatcher import __version__ as current_version
from pokewatcher.components import ALL_COMPONENTS
from pokewatcher.core.config import load as load_configs, setup_logging
from pokewatcher.core.game import GameInterface
from pokewatcher.core.util import SleepLoop

###############################################################################
# Constants
###############################################################################

logger: Final[logging.Logger] = logging.getLogger(__name__)

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


def _load_game_interface(configs: Dict[str, Any]) -> GameInterface:
    logger.info('loading game interface')
    game = GameInterface()
    game.setup(configs)
    return game


def _load_components(configs: Dict[str, Any]) -> List[Any]:
    logger.info('loading components')
    components = []
    for module in ALL_COMPONENTS:
        key = module.__name__.split('.')[-1]
        settings: Dict[str, Any] = configs[key]
        if settings.get('enabled', True):
            logger.info(f'loading component: {key}')
            instance = module.new()
            instance.setup(settings)
            components.append(instance)
        else:
            logger.info(f'skipping disabled component: {key}')
    return components


###############################################################################
# Main Logic
###############################################################################


def workflow(
    args: Dict[str, Any],
    configs: Dict[str, Any],
    game: GameInterface,
    components: List[Any],
) -> int:
    logger.debug(f'arguments: {args}')
    logger.debug(f'configurations: {configs}')

    game.start()
    for component in components:
        component.start()

    freq = configs['options']['update_frequency']
    delay = 1.0 / freq  # hz to sec
    with SleepLoop(delay=delay) as loop:
        while loop.iterate():
            game.update(loop.delta)
            for component in components:
                component.update(loop.delta)
    return 0


def cleanup(game: GameInterface, components: List[Any]) -> None:
    logger.info('cleaning up game and components')
    game.cleanup()
    for component in components:
        component.cleanup()


###############################################################################
# Entry Point
###############################################################################


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_arguments(argv)

    # setup phase --------------------------------------------------------------
    logger.info('running setup operations')
    try:
        configs = load_configs(args)
        setup_logging()
        game = _load_game_interface(configs)
        components = _load_components(configs)
    except KeyboardInterrupt:
        logger.error('aborted manually')
        return 1
    except Exception as err:
        logger.exception('exception during setup')
        return 1

    # main phase ---------------------------------------------------------------
    try:
        rcode = workflow(args, configs, game, components)
    except KeyboardInterrupt:
        logger.error('aborted manually')
        rcode = 1
    except Exception as err:
        logger.exception('exception during execution')
        return 1

    if rcode != 0:
        logger.critical(f'terminating with error code: {rcode}')
    cleanup(game, components)
    return rcode
