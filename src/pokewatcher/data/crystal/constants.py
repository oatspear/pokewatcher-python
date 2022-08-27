# SPDX-License-Identifier: MIT
# Copyright © 2022 André 'Oatspear' Santos

###############################################################################
# Imports
###############################################################################

from typing import Final, Mapping, Tuple

###############################################################################
# Constants
###############################################################################

BATTLE_MODE_NONE: Final[int] = 0x00
BATTLE_MODE_WILD: Final[int] = 0x01
BATTLE_MODE_TRAINER: Final[int] = 0x02

BATTLE_TYPE_NORMAL: Final[int] = 0x00
BATTLE_TYPE_CAN_LOSE: Final[int] = 0x01
BATTLE_TYPE_DEBUG: Final[int] = 0x02
BATTLE_TYPE_TUTORIAL: Final[int] = 0x03
BATTLE_TYPE_FISH: Final[int] = 0x04
BATTLE_TYPE_ROAMING: Final[int] = 0x05
BATTLE_TYPE_CONTEST: Final[int] = 0x06
BATTLE_TYPE_SHINY: Final[int] = 0x07
BATTLE_TYPE_TREE: Final[int] = 0x08
BATTLE_TYPE_TRAP: Final[int] = 0x09
BATTLE_TYPE_FORCE_ITEM: Final[int] = 0x0A
BATTLE_TYPE_CELEBI: Final[int] = 0x0B
BATTLE_TYPE_SUICUNE: Final[int] = 0x0C

BATTLE_RESULT_WIN: Final[int] = 0x00
BATTLE_RESULT_LOSE: Final[int] = 0x01
BATTLE_RESULT_DRAW: Final[int] = 0x02

SFX_SAVE_FILE: Final[int] = 9472

MAP_GROUPS: Final[Mapping[int, str]] = {
    0x01: 'OLIVINE',
    0x02: 'MAHOGANY',
    0x03: 'DUNGEONS',
    0x04: 'ECRUTEAK',
    0x05: 'BLACKTHORN',
    0x06: 'CINNABAR',
    0x07: 'CERULEAN',
    0x08: 'AZALEA',
    0x09: 'LAKE OF RAGE',
    0x0A: 'VIOLET',
    0x0B: 'GOLDENROD',
    0x0C: 'VERMILION',
    0x0D: 'PALLET',
    0x0E: 'PEWTER',
    0x0F: 'FAST SHIP',
    0x10: 'INDIGO',
    0x11: 'FUCHSIA',
    0x12: 'LAVENDER',
    0x13: 'SILVER',
    0x14: 'CABLE CLUB',
    0x15: 'CELADON',
    0x16: 'CIANWOOD',
    0x17: 'VIRIDIAN',
    0x18: 'NEW BARK',
    0x19: 'SAFFRON',
    0x1A: 'CHERRYGROVE',
}



WRAM_PLAYER_ID: Final[str] = 'wPlayerID'
WRAM_PLAYER_NAME: Final[str] = 'wPlayerName'
WRAM_PLAYER_MONEY: Final[str] = 'wMoney'
WRAM_PLAY_TIME_HOURS: Final[str] = 'wGameTimeHours'
WRAM_PLAY_TIME_MINUTES: Final[str] = 'wGameTimeMinutes'
WRAM_PLAY_TIME_MINUTES: Final[str] = 'wGameTimeSeconds'
WRAM_PLAY_TIME_SECONDS: Final[str] = 'wGameTimeFrames'
WRAM_MAP_GROUP: Final[str] = 'wMapGroup'
WRAM_MAP_NUMBER: Final[str] = 'wMapNumber'
WRAM_X_COORD: Final[str] = 'wXCoord'
WRAM_Y_COORD: Final[str] = 'wYCoord'
WRAM_AUDIO_CHANNEL5: Final[str] = 'wChannel5MusicID'
WRAM_BATTLE_MODE: Final[str] = 'wBattleMode'
WRAM_BATTLE_TYPE: Final[str] = 'wBattleType'
WRAM_BATTLE_RESULT: Final[str] = 'wBattleResult'
WRAM_LOW_HEALTH_ALARM: Final[str] = 'wBattleLowHealthAlarm'

ALL_WRAM: Final[Tuple] = tuple(v for k, v in globals().items() if k.startswith('WRAM_'))
