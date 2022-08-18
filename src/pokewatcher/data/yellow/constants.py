# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Final, Tuple

###############################################################################
# Constants
###############################################################################

BATTLE_TYPE_NONE: Final[int] = 0x00
BATTLE_TYPE_WILD: Final[int] = 0x01
BATTLE_TYPE_TRAINER: Final[int] = 0x02
BATTLE_TYPE_LOST: Final[int] = 0xFF

SFX_SAVE_FILE: Final[int] = 0xB6

DEFAULT_PLAYER_NAME: Final[str] = 'NINTEN'

JOY_MASK_A_BUTTON: Final[int] = 0x01
JOY_MASK_B_BUTTON: Final[int] = 0x02
JOY_MASK_SELECT: Final[int] = 0x04
JOY_MASK_START: Final[int] = 0x08
JOY_MASK_D_RIGHT: Final[int] = 0x10
JOY_MASK_D_LEFT: Final[int] = 0x20
JOY_MASK_D_UP: Final[int] = 0x40
JOY_MASK_D_DOWN: Final[int] = 0x80
JOY_MASK_ALL: Final[int] = 0xFF
JOY_MASK_NONE: Final[int] = 0x00

WRAM_PLAYER_ID: Final[str] = 'wPlayerID'
WRAM_PLAYER_NAME: Final[str] = 'wPlayerName'
WRAM_BATTLE_TYPE: Final[str] = 'wIsInBattle'
WRAM_LOW_HEALTH_ALARM: Final[str] = 'wLowHealthAlarmDisabled'
WRAM_AUDIO_CHANNEL5: Final[str] = 'wChannelSoundIDs_5'
WRAM_CUR_MAP: Final[str] = 'wCurMap'
WRAM_X_COORD: Final[str] = 'wXCoord'
WRAM_Y_COORD: Final[str] = 'wYCoord'
WRAM_COUNT_PLAY_TIME: Final[str] = 'wd732_0'
WRAM_JOY_IGNORE: Final[str] = 'wJoyIgnore'

ALL_WRAM: Final[Tuple] = tuple(v for k, v in globals().items() if k.startswith('WRAM_'))
