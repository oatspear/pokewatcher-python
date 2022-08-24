# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Final, Tuple

###############################################################################
# Constants
###############################################################################

SFX_SAVE_FILE = 9472

WRAM_PLAYER_ID: Final[str] = 'wPlayerID'
WRAM_PLAY_TIME_HOURS: Final[str] = 'wGameTimeHours'
WRAM_PLAY_TIME_MINUTES: Final[str] = 'wGameTimeMinutes'
WRAM_PLAY_TIME_MINUTES: Final[str] = 'wGameTimeSeconds'
WRAM_PLAY_TIME_SECONDS: Final[str] = 'wGameTimeFrames'
WRAM_MAP_GROUP: Final[str] = 'wMapGroup'
WRAM_MAP_NUMBER: Final[str] = 'wMapNumber'
WRAM_X_COORD: Final[str] = 'wXCoord'
WRAM_Y_COORD: Final[str] = 'wYCoord'
WRAM_AUDIO_CHANNEL5: Final[str] = 'wChannel5_0'
WRAM_BATTLE_MODE: Final[str] = 'wBattleMode'
WRAM_BATTLE_TYPE: Final[str] = 'wBattleType'
WRAM_BATTLE_RESULT: Final[str] = 'wBattleResult'
WRAM_LOW_HEALTH_ALARM: Final[str] = 'wBattleLowHealthAlarm'

ALL_WRAM: Final[Tuple] = tuple(v for k, v in globals().items() if k.startswith('WRAM_'))
