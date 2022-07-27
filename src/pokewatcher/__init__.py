# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from importlib.metadata import PackageNotFoundError, version  # pragma: no cover

###############################################################################
# Constants
###############################################################################

try:
    __version__ = version('pokewatcher')
except PackageNotFoundError:  # pragma: no cover
    # package is not installed
    __version__ = 'unknown'

