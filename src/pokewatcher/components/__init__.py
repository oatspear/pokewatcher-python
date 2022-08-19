# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Final, Tuple

from pokewatcher.components import auto_save, livesplit, obsstudio, save_backup, splitter

###############################################################################
# Interface
###############################################################################


ALL_COMPONENTS: Final[Tuple] = (
    auto_save,
    livesplit,
    obsstudio,
    save_backup,
    splitter,
)
