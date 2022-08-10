# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Final

###############################################################################
# Constants
###############################################################################

BATTLE_TYPE_NONE: Final[int] = 0x00
BATTLE_TYPE_WILD: Final[int] = 0x01
BATTLE_TYPE_TRAINER: Final[int] = 0x02
BATTLE_TYPE_LOST: Final[int] = 0xFF

ALARM_ENABLED: Final[int] = 0x00
ALARM_DISABLED: Final[int] = 0x01
