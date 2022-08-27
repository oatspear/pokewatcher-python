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

MAP_GROUP_NEW_BARK: Final[str] = 'New Bark'
MAP_GROUP_CHERRYGROVE: Final[str] = 'Cherrygrove'
MAP_GROUP_VIOLET: Final[str] = 'Violet'
MAP_GROUP_AZALEA: Final[str] = 'Azalea'
MAP_GROUP_GOLDENROD: Final[str] = 'Goldenrod'
MAP_GROUP_ECRUTEAK: Final[str] = 'Ecruteak'
MAP_GROUP_OLIVINE: Final[str] = 'Olivine'
MAP_GROUP_CIANWOOD: Final[str] = 'Cianwood'
MAP_GROUP_MAHOGANY: Final[str] = 'Mahogany'
MAP_GROUP_LAKE_OF_RAGE: Final[str] = 'Lake of Rage'
MAP_GROUP_BLACKTHORN: Final[str] = 'Blackthorn'
MAP_GROUP_DUNGEONS: Final[str] = 'Dungeons'
MAP_GROUP_INDIGO: Final[str] = 'Indigo'
MAP_GROUP_FAST_SHIP: Final[str] = 'Fast Ship'
MAP_GROUP_PALLET: Final[str] = 'Pallet'
MAP_GROUP_VIRIDIAN: Final[str] = 'Viridian'
MAP_GROUP_PEWTER: Final[str] = 'Pewter'
MAP_GROUP_CERULEAN: Final[str] = 'Cerulean'
MAP_GROUP_VERMILION: Final[str] = 'Vermilion'
MAP_GROUP_LAVENDER: Final[str] = 'Lavender'
MAP_GROUP_CELADON: Final[str] = 'Celadon'
MAP_GROUP_FUCHSIA: Final[str] = 'Fuchsia'
MAP_GROUP_SAFFRON: Final[str] = 'Saffron'
MAP_GROUP_CINNABAR: Final[str] = 'Cinnabar'
MAP_GROUP_SILVER: Final[str] = 'Silver'
MAP_GROUP_CABLE_CLUB: Final[str] = 'Cable Club'

MAP_GROUPS: Final[Mapping[int, str]] = {
    0x01: MAP_GROUP_OLIVINE,
    0x02: MAP_GROUP_MAHOGANY,
    0x03: MAP_GROUP_DUNGEONS,
    0x04: MAP_GROUP_ECRUTEAK,
    0x05: MAP_GROUP_BLACKTHORN,
    0x06: MAP_GROUP_CINNABAR,
    0x07: MAP_GROUP_CERULEAN,
    0x08: MAP_GROUP_AZALEA,
    0x09: MAP_GROUP_LAKE_OF_RAGE,
    0x0A: MAP_GROUP_VIOLET,
    0x0B: MAP_GROUP_GOLDENROD,
    0x0C: MAP_GROUP_VERMILION,
    0x0D: MAP_GROUP_PALLET,
    0x0E: MAP_GROUP_PEWTER,
    0x0F: MAP_GROUP_FAST_SHIP,
    0x10: MAP_GROUP_INDIGO,
    0x11: MAP_GROUP_FUCHSIA,
    0x12: MAP_GROUP_LAVENDER,
    0x13: MAP_GROUP_SILVER,
    0x14: MAP_GROUP_CABLE_CLUB,
    0x15: MAP_GROUP_CELADON,
    0x16: MAP_GROUP_CIANWOOD,
    0x17: MAP_GROUP_VIRIDIAN,
    0x18: MAP_GROUP_NEW_BARK,
    0x19: MAP_GROUP_SAFFRON,
    0x1A: MAP_GROUP_CHERRYGROVE,
}

MAP_NAMES: Final[Mapping[str, Mapping[int, str]]] = {
    MAP_GROUP_OLIVINE: {
        1: 'Pokemon Center 1F',
        2: 'Gym',
        3: "Tim's House",
        4: 'House Beta',
        5: 'Punishment Speech House',
        6: 'Good Rod House',
        7: 'Cafe',
        8: 'Pokemon Mart',
        9: 'Route 38 Ecruteak Gate',
        10: 'Route 39 Barn',
        11: 'Route 39 Farmhouse',
        12: 'Route 38',
        13: 'Route 39',
        14: 'City',
    },
    MAP_GROUP_MAHOGANY: {
        1: 'Red Gyarados Speech House',
        2: 'Gym',
        3: 'Pokemon Center 1F',
        4: 'Route 42 Ecruteak Gate',
        5: 'Route 42',
        6: 'Route 44',
        7: 'Town',
    },
    MAP_GROUP_DUNGEONS: {
        1: 'Sprout Tower 1F',
        2: 'Sprout Tower 2F',
        3: 'Sprout Tower 3F',
        4: 'Tin Tower 1F',
        5: 'Tin Tower 2F',
        6: 'Tin Tower 3F',
        7: 'Tin Tower 4F',
        8: 'Tin Tower 5F',
        9: 'Tin Tower 6F',
        10: 'Tin Tower 7F',
        11: 'Tin Tower 8F',
        12: 'Tin Tower 9F',
        13: 'Burned Tower 1F',
        14: 'Burned Tower B1F',
        15: 'National Park',
        16: 'National Park Bug Contest',
        17: 'Radio Tower 1F',
        18: 'Radio Tower 2F',
        19: 'Radio Tower 3F',
        20: 'Radio Tower 4F',
        21: 'Radio Tower 5F',
        22: 'Ruins of Alph Outside',
        23: 'Ruins of Alph Ho-oh Chamber',
        24: 'Ruins of Alph Kabuto Chamber',
        25: 'Ruins of Alph Omanyte Chamber',
        26: 'Ruins of Alph Aerodactyl Chamber',
        27: 'Ruins of Alph Inner Chamber',
        28: 'Ruins of Alph Research Center',
        29: 'Ruins of Alph HO_OH_ITEM_ROOM',
        30: 'Ruins of Alph KABUTO_ITEM_ROOM',
        31: 'Ruins of Alph OMANYTE_ITEM_ROOM',
        32: 'Ruins of Alph AERODACTYL_ITEM_ROOM',
        33: 'Ruins of Alph HO_OH_WORD_ROOM',
        34: 'Ruins of Alph KABUTO_WORD_ROOM',
        35: 'Ruins of Alph OMANYTE_WORD_ROOM',
        36: 'Ruins of Alph AERODACTYL_WORD_ROOM',
        37: 'UNION_CAVE_1F',
        38: 'UNION_CAVE_B1F',
        39: 'UNION_CAVE_B2F',
        40: 'SLOWPOKE_WELL_B1F',
        41: 'SLOWPOKE_WELL_B2F',
        42: 'OLIVINE_LIGHTHOUSE_1F',
        43: 'OLIVINE_LIGHTHOUSE_2F',
        44: 'OLIVINE_LIGHTHOUSE_3F',
        45: 'OLIVINE_LIGHTHOUSE_4F',
        46: 'OLIVINE_LIGHTHOUSE_5F',
        47: 'OLIVINE_LIGHTHOUSE_6F',
        48: 'MAHOGANY_MART_1F',
        49: 'TEAM_ROCKET_BASE_B1F',
        50: 'TEAM_ROCKET_BASE_B2F',
        51: 'TEAM_ROCKET_BASE_B3F',
        52: 'ILEX_FOREST',
        53: 'GOLDENROD_UNDERGROUND',
        54: 'GOLDENROD_UNDERGROUND_SWITCH_ROOM_ENTRANCES',
        55: 'GOLDENROD_DEPT_STORE_B1F',
        56: 'GOLDENROD_UNDERGROUND_WAREHOUSE',
        57: 'MOUNT_MORTAR_1F_OUTSIDE',
        58: 'MOUNT_MORTAR_1F_INSIDE',
        59: 'MOUNT_MORTAR_2F_INSIDE',
        60: 'MOUNT_MORTAR_B1F',
        61: 'ICE_PATH_1F',
        62: 'ICE_PATH_B1F',
        63: 'ICE_PATH_B2F_MAHOGANY_SIDE',
        64: 'ICE_PATH_B2F_BLACKTHORN_SIDE',
        65: 'ICE_PATH_B3F',
        66: 'WHIRL_ISLAND_NW',
        67: 'WHIRL_ISLAND_NE',
        68: 'WHIRL_ISLAND_SW',
        69: 'WHIRL_ISLAND_CAVE',
        70: 'WHIRL_ISLAND_SE',
        71: 'WHIRL_ISLAND_B1F',
        72: 'WHIRL_ISLAND_B2F',
        73: 'WHIRL_ISLAND_LUGIA_CHAMBER',
        74: 'SILVER_CAVE_ROOM_1',
        75: 'SILVER_CAVE_ROOM_2',
        76: 'SILVER_CAVE_ROOM_3',
        77: 'SILVER_CAVE_ITEM_ROOMS',
        78: 'DARK_CAVE_VIOLET_ENTRANCE',
        79: 'DARK_CAVE_BLACKTHORN_ENTRANCE',
        80: 'DRAGONS_DEN_1F',
        81: 'DRAGONS_DEN_B1F',
        82: 'DRAGON_SHRINE',
        83: 'TOHJO_FALLS',
        84: 'DIGLETTS_CAVE',
        85: 'MOUNT_MOON',
        86: 'UNDERGROUND_PATH',
        87: 'ROCK_TUNNEL_1F',
        88: 'ROCK_TUNNEL_B1F',
        89: 'SAFARI_ZONE_FUCHSIA_GATE_BETA',
        90: 'SAFARI_ZONE_BETA',
        91: 'VICTORY_ROAD',
    },
    MAP_GROUP_OLIVINE: {

    },
    MAP_GROUP_OLIVINE: {

    },
    MAP_GROUP_OLIVINE: {

    },
    MAP_GROUP_OLIVINE: {

    },
    MAP_GROUP_OLIVINE: {

    },
    MAP_GROUP_OLIVINE: {

    },
    MAP_GROUP_OLIVINE: {

    },
    MAP_GROUP_OLIVINE: {

    },
    MAP_GROUP_OLIVINE: {

    },
    MAP_GROUP_OLIVINE: {

    },
    MAP_GROUP_OLIVINE: {

    },
    MAP_GROUP_OLIVINE: {

    },
    MAP_GROUP_OLIVINE: {

    },
    MAP_GROUP_OLIVINE: {

    },
    MAP_GROUP_OLIVINE: {

    },
    MAP_GROUP_OLIVINE: {

    },
    MAP_GROUP_OLIVINE: {

    },
    MAP_GROUP_OLIVINE: {

    },
    MAP_GROUP_OLIVINE: {

    },
    MAP_GROUP_OLIVINE: {

    },
    MAP_GROUP_OLIVINE: {

    },
    MAP_GROUP_OLIVINE: {

    },
    MAP_GROUP_OLIVINE: {

    },
}

TRAINER_CLASS_CHAMPION: Final[str] = 'CHAMPION'

WRAM_PLAYER_ID: Final[str] = 'wPlayerID'
WRAM_PLAYER_NAME: Final[str] = 'wPlayerName'
WRAM_PLAYER_MONEY: Final[str] = 'wMoney'
WRAM_GAME_TIME_HOURS: Final[str] = 'wGameTimeHours'
WRAM_GAME_TIME_MINUTES: Final[str] = 'wGameTimeMinutes'
WRAM_GAME_TIME_SECONDS: Final[str] = 'wGameTimeSeconds'
WRAM_GAME_TIME_FRAMES: Final[str] = 'wGameTimeFrames'
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
