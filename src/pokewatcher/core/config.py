# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Any, Dict

import logging

###############################################################################
# Constants
###############################################################################

logger = logging.getLogger(__name__)

DEFAULTS: Dict[str, Any] = {
    'auto-save': {'enabled': True},
    'save-backup': {'enabled': True},
    'battle-monitor': {'enabled': True},
    'splits': {'enabled': True},
    'video-records': {'enabled': True},
    'timer': {'enabled': True},
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
        print('Error while loading configuration. Reverting to defaults.', file=sys.stderr)
        return DEFAULTS
