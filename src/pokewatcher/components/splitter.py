# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Any, Mapping

import logging

###############################################################################
# Constants
###############################################################################

logger = logging.getLogger(__name__)

###############################################################################
# Interface
###############################################################################


class SplitComponent:
    def setup(self, settings: Mapping[str, Any]):
        logger.info('setting up')
        return

    def start(self):
        logger.info('starting')
        return

    def update(self, delta):
        # logger.debug('update')
        return

    def cleanup(self):
        logger.info('cleaning up')
        return


def new():
    instance = SplitComponent()
    return instance
