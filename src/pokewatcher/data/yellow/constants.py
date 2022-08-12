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

WRAM_PLAYER_ID: Final[str] = 'wPlayerID'
WRAM_PLAYER_NAME: Final[str] = 'wPlayerName'
WRAM_BATTLE_TYPE: Final[str] = 'wIsInBattle'
WRAM_LOW_HEALTH_ALARM: Final[str] = 'wLowHealthAlarmDisabled'
WRAM_AUDIO_CHANNEL5: Final[str] = 'wChannelSoundIDs_5'

ALL_WRAM: Final[Tuple] = tuple(v for k, v in globals().items() if k.startswith('WRAM_'))
