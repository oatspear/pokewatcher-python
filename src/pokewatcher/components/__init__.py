# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Final, Tuple

from pokewatcher.components import auto_save, livesplit, save_backup, splitter, video_record

###############################################################################
# Interface
###############################################################################


ALL_COMPONENTS: Final[Tuple] = (
    auto_save,
    livesplit,
    save_backup,
    splitter,
    video_record,
)
