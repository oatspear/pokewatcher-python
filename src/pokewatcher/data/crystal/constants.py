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
        8: 'Mart',
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
        29: 'Ruins of Alph Ho-oh Item Room',
        30: 'Ruins of Alph Kabuto Item Room',
        31: 'Ruins of Alph Omanyte Item Room',
        32: 'Ruins of Alph Aerodactyl Item Room',
        33: 'Ruins of Alph Ho-oh Word Room',
        34: 'Ruins of Alph Kabuto Word Room',
        35: 'Ruins of Alph Omanyte Word Room',
        36: 'Ruins of Alph Aerodactyl Word Room',
        37: 'Union Cave 1F',
        38: 'Union Cave B1F',
        39: 'Union Cave B2F',
        40: 'Slowpoke Well B1F',
        41: 'Slowpoke Well B2F',
        42: 'Olivine Lighthouse 1F',
        43: 'Olivine Lighthouse 2F',
        44: 'Olivine Lighthouse 3F',
        45: 'Olivine Lighthouse 4F',
        46: 'Olivine Lighthouse 5F',
        47: 'Olivine Lighthouse 6F',
        48: 'Mahogany Mart 1F',
        49: 'Team Rocket Base B1F',
        50: 'Team Rocket Base B2F',
        51: 'Team Rocket Base B3F',
        52: 'Ilex Forest',
        53: 'Goldenrod Underground',
        54: 'Goldenrod Underground Switch Room Entrances',
        55: 'Goldenrod Dept. Store B1F',
        56: 'Goldenrod Underground Warehouse',
        57: 'Mount Mortar 1F Outside',
        58: 'Mount Mortar 1F Inside',
        59: 'Mount Mortar 2F Inside',
        60: 'Mount Mortar B1F',
        61: 'Ice Path 1F',
        62: 'Ice Path B1F',
        63: 'Ice Path B2F Mahogany Side',
        64: 'Ice Path B2F Blackthorn Side',
        65: 'Ice Path B3F',
        66: 'Whirl Island NW',
        67: 'Whirl Island NE',
        68: 'Whirl Island SW',
        69: 'Whirl Island Cave',
        70: 'Whirl Island SE',
        71: 'Whirl Island B1F',
        72: 'Whirl Island B2F',
        73: 'Whirl Island Lugia Chamber',
        74: 'Silver Cave Room 1',
        75: 'Silver Cave Room 2',
        76: 'Silver Cave Room 3',
        77: 'Silver Cave Item Rooms',
        78: 'Dark Cave Violet Entrance',
        79: 'Dark Cave Blackthorn Entrance',
        80: "Dragon's Den 1F",
        81: "Dragon's Den B1F",
        82: 'Dragon Shrine',
        83: 'Tohjo Falls',
        84: "Diglett's Cave",
        85: 'Mount Moon',
        86: 'Underground Path',
        87: 'Rock Tunnel 1F',
        88: 'Rock Tunnel B1F',
        89: 'Safari Zone Fuchsia Gate Beta',
        90: 'Safari Zone Beta',
        91: 'Victory Road',
    },
    MAP_GROUP_ECRUTEAK: {
        1: 'Tin Tower Entrance',
        2: "Wise Trio's Room",
        3: 'Pokemon Center 1F',
        4: 'Lugia Speech House',
        5: 'Dance Theatre',
        6: 'Mart',
        7: 'Gym',
        8: 'Itemfinder House',
        9: 'City',
    },
    MAP_GROUP_BLACKTHORN: {
        1: 'Gym 1F',
        2: 'Gym 2F',
        3: 'Dragon Speech House',
        4: "Emy's House",
        5: 'Mart',
        6: 'Pokemon Center 1F',
        7: "Move Deleter's House",
        8: 'Route 45',
        9: 'Route 46',
        10: 'City',
    },
    MAP_GROUP_CINNABAR: {
        1: 'Pokemon Center 1F',
        2: 'Pokemon Center 2F Beta',
        3: 'Route 19 Fuchsia Gate',
        4: 'Seafoam Gym',
        5: 'Route 19',
        6: 'Route 20',
        7: 'Route 21',
        8: 'Island',
    },
    MAP_GROUP_CERULEAN: {
        1: 'Gym Badge Speech House',
        2: 'Police Station',
        3: 'Trade Speech House',
        4: 'Pokemon Center 1F',
        5: 'Pokemon Center 2F Beta',
        6: 'Gym',
        7: 'Mart',
        8: 'Route 10 Pokemon Center 1F',
        9: 'Route 10 Pokemon Center 2F Beta',
        10: 'Power Plant',
        11: "Bill's House",
        12: 'Route 4',
        13: 'Route 9',
        14: 'Route 10 North',
        15: 'Route 24',
        16: 'Route 25',
        17: 'City',
    },
    MAP_GROUP_AZALEA: {
        1: 'Pokemon Center 1F',
        2: 'Charcoal Kiln',
        3: 'Mart',
        4: "Kurt's House",
        5: 'Gym',
        6: 'Route 33',
        7: 'Town',
    },
    MAP_GROUP_LAKE_OF_RAGE: {
        1: 'Hidden Power House',
        2: 'Magikarp House',
        3: 'Route 43 Mahogany Gate',
        4: 'Route 43 Gate',
        5: 'Route 43',
        6: 'Lake',
    },
    MAP_GROUP_VIOLET: {
        1: 'Route 32',
        2: 'Route 35',
        3: 'Route 36',
        4: 'Route 37',
        5: 'City',
        6: 'Mart',
        7: 'Gym',
        8: "Earl's Pokemon Academy",
        9: 'Nickname Speech House',
        10: 'Pokemon Center 1F',
        11: "Kyle's House",
        12: 'Route 32 Ruins of Alph Gate',
        13: 'Route 32 Pokemon Center 1F',
        14: 'Route 35 Goldenrod Gate',
        15: 'Route 35 National Park Gate',
        16: 'Route 36 Ruins of Alph Gate',
        17: 'Route 36 National Park Gate',
    },
    MAP_GROUP_GOLDENROD: {
        1: 'Route 34',
        2: 'City',
        3: 'Gym',
        4: 'Bike Shop',
        5: 'Happiness Rater',
        6: "Bill's Family's House",
        7: 'Magnet Train Station',
        8: 'Flower Shop',
        9: 'PP Speech House',
        10: 'Name Rater',
        11: 'Dept. Store 1F',
        12: 'Dept. Store 2F',
        13: 'Dept. Store 3F',
        14: 'Dept. Store 4F',
        15: 'Dept. Store 5F',
        16: 'Dept. Store 6F',
        17: 'Dept. Store Elevator',
        18: 'Dept. Store Roof',
        19: 'Game Corner',
        20: 'Pokemon Center 1F',
        21: 'PokeCom Center Admin Office Mobile',
        22: 'Ilex Forest Azalea Gate',
        23: 'Route 34 Ilex Forest Gate',
        24: 'Day Care',
    },
    MAP_GROUP_VERMILION: {
        1: 'Route 6',
        2: 'Route 11',
        3: 'City',
        4: 'Fishing Speech House',
        5: 'Pokemon Center 1F',
        6: 'Pokemon Center 2F_BETA',
        7: 'Pokemon Fan Club',
        8: 'Magnet Train Speech House',
        9: 'Mart',
        10: "Diglett's Cave Speech House",
        11: 'Gym',
        12: 'Route 6 Saffron Gate',
        13: 'Route 6 Underground Path Entrance',
    },
    MAP_GROUP_PALLET: {
        1: 'Route 1',
        2: 'Town',
        3: "Red's House 1F",
        4: "Red's House 2F",
        5: "Blue's House",
        6: "Oak's Lab",
    },
    MAP_GROUP_PEWTER: {
        1: 'Route 3',
        2: 'City',
        3: 'Nidoran Speech House',
        4: 'Gym',
        5: 'Mart',
        6: 'Pokemon Center 1F',
        7: 'Pokemon Center 2F Beta',
        8: 'Snooze Speech House',
    },
    MAP_GROUP_FAST_SHIP: {
        1: 'Olivine Port',
        2: 'Vermilion Port',
        3: '1F',
        4: 'Cabins NNW NNE NE',
        5: 'Cabins SW SSW NW',
        6: 'Cabins SE SSE CAPTAIN',
        7: 'B1F',
        8: 'Olivine Port Passage',
        9: 'Vermilion Port Passage',
        10: 'Mount Moon Square',
        11: 'Mount Moon Gift Shop',
        12: 'Tin Tower Roof',
    },
    MAP_GROUP_INDIGO: {
        1: 'Route 23',
        2: 'Pokemon Center 1F',
        3: "Will's Room",
        4: "Koga's Room",
        5: "Bruno's Room",
        6: "Karen's Room",
        7: "Lance's Room",
        8: 'Hall of Fame',
    },
    MAP_GROUP_FUCHSIA: {
        1: 'Route 13',
        2: 'Route 14',
        3: 'Route 15',
        4: 'Route 18',
        5: 'City',
        6: 'Mart',
        7: 'Safari Zone Main Office',
        8: 'Gym',
        9: "Bill's Brother's House",
        10: 'Pokemon Center 1F',
        11: 'Pokemon Center 2F Beta',
        12: "Safari Zone Warden's Home",
        13: 'Route 15 Fuchsia Gate',
    },
    MAP_GROUP_LAVENDER: {
        1: 'Route 8',
        2: 'Route 12',
        3: 'Route 10 South',
        4: 'Town',
        5: 'Pokemon Center 1F',
        6: 'Pokemon Center 2F Beta',
        7: "Mr. Fuji's House",
        8: 'Lavender Speech House',
        9: 'Name Rater',
        10: 'Mart',
        11: 'Soul House',
        12: 'Radio Tower 1F',
        13: 'Route 8 Saffron Gate',
        14: 'Route 12 Super Rod House',
    },
    MAP_GROUP_SILVER: {
        1: 'Route 28',
        2: 'Silver Cave Outside',
        3: 'Silver Cave Pokemon Center 1F',
        4: 'Route 28 Steel Wing House',
    },
    MAP_GROUP_CABLE_CLUB: {
        1: 'Pokemon Center 2F',
        2: 'Trade Center',
        3: 'Colosseum',
        4: 'Time Capsule',
        5: 'Mobile Trade Room',
        6: 'Mobile Battle Room',
    },
    MAP_GROUP_CELADON: {
        1: 'Route 7',
        2: 'Route 16',
        3: 'Route 17',
        4: 'City',
        5: 'Dept. Store 1F',
        6: 'Dept. Store 2F',
        7: 'Dept. Store 3F',
        8: 'Dept. Store 4F',
        9: 'Dept. Store 5F',
        10: 'Dept. Store 6F',
        11: 'Dept. Store Elevator',
        12: 'Mansion 1F',
        13: 'Mansion 2F',
        14: 'Mansion 3F',
        15: 'Mansion Roof',
        16: 'Mansion Roof House',
        17: 'Pokemon Center 1F',
        18: 'Pokemon Center 2F Beta',
        19: 'Game Corner',
        20: 'Game Corner Prize Room',
        21: 'Gym',
        22: 'Cafe',
        23: 'Route 16 Fuchsia Speech House',
        24: 'Route 16 Gate',
        25: 'Route 7 Saffron Gate',
        26: 'Route 17 Route 18 Gate',
    },
    MAP_GROUP_CIANWOOD: {
        1: 'Route 40',
        2: 'Route 41',
        3: 'City',
        4: "Mania's House",
        5: 'Gym',
        6: 'Pokemon Center 1F',
        7: 'Pharmacy',
        8: 'Photo Studio',
        9: 'Lugia Speech House',
        10: "Poke Seer's House",
        11: 'Battle Tower 1F',
        12: 'Battle Tower Battle Room',
        13: 'Battle Tower Elevator',
        14: 'Battle Tower Hallway',
        15: 'Route 40 Battle Tower Gate',
        16: 'Battle Tower Outside',
    },
    MAP_GROUP_VIRIDIAN: {
        1: 'Route 2',
        2: 'Route 22',
        3: 'City',
        4: 'Gym',
        5: 'Nickname Speech House',
        6: 'Trainer House 1F',
        7: 'Trainer House B1F',
        8: 'Mart',
        9: 'Pokemon Center 1F',
        10: 'Pokemon Center 2F Beta',
        11: 'Route 2 Nugget House',
        12: 'Route 2 Gate',
        13: 'Victory Road Gate',
    },
    MAP_GROUP_NEW_BARK: {
        1: 'Route 26',
        2: 'Route 27',
        3: 'Route 29',
        4: 'Town',
        5: "Elm's Lab",
        6: "Player's House_1F",
        7: "Player's House_2F",
        8: "Player's Neighbor's House",
        9: "Elm's House",
        10: 'Route 26 Heal House',
        11: "Day of Week Siblings' House",
        12: 'Route 27 Sandstorm House',
        13: 'Route 29 Route 46 Gate',
    },
    MAP_GROUP_SAFFRON: {
        1: 'Route 5',
        2: 'City',
        3: 'Fighting Dojo',
        4: 'Gym',
        5: 'Mart',
        6: 'Pokemon Center 1F',
        7: 'Pokemon Center 2F Beta',
        8: "Mr. Psychic's House",
        9: 'Magnet Train Station',
        10: 'Silph Co. 1F',
        11: "Copycat's House 1F",
        12: "Copycat's House 2F",
        13: 'Route 5 Underground Path Entrance',
        14: 'Route 5 Saffron Gate',
        15: 'Route 5 Cleanse Tag House',
    },
    MAP_GROUP_CHERRYGROVE: {
        1: 'Route 30',
        2: 'Route 31',
        3: 'City',
        4: 'Mart',
        5: 'Pokemon Center 1F',
        6: 'Gym Speech House',
        7: "Guide Gent's House",
        8: 'Evolution Speech House',
        9: 'Route 30 Berry House',
        10: "Mr. Pokemon's House",
        11: 'Route 31 Violet Gate',
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
