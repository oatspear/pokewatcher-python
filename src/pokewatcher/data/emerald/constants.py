# SPDX-License-Identifier: MIT
# Copyright © 2022 André 'Oatspear' Santos

###############################################################################
# Imports
###############################################################################

from typing import Final, Mapping, Tuple

###############################################################################
# Constants
###############################################################################

BATTLE_DIALOGUE_IN_BATTLE: Final[int] = 0x12
BATTLE_RESULT_NONE: Final[int] = 0x00
BATTLE_RESULT_WIN: Final[int] = 0x01
BATTLE_RESULT_LOSE: Final[int] = 0x02
BATTLE_RESULT_RUN: Final[int] = 0x04

WRAM_PLAYER_NAME: Final[str] = 'player_name'
WRAM_TEAM_COUNT: Final[str] = 'team_count'
WRAM_BATTLE_OUTCOME: Final[str] = 'battle_outcome'
WRAM_BATTLE_BG_TILES: Final[str] = 'battle_bg_tiles'
