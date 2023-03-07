# SPDX-License-Identifier: MIT
# Copyright © 2022 André 'Oatspear' Santos

###############################################################################
# Imports
###############################################################################

from typing import Final, Mapping, Tuple

###############################################################################
# Constants
###############################################################################

TRAINER_CLASSES_FINAL_BATTLE: Final[Tuple[str]] = (
    'CHAMPION_FIRST_SQUIRTLE',
    'CHAMPION_FIRST_BULBASAUR',
    'CHAMPION_FIRST_CHARMANDER',
)

BATTLE_DIALOGUE_IN_BATTLE: Final[int] = 0x12
BATTLE_RESULT_NONE: Final[int] = 0x00
BATTLE_RESULT_WIN: Final[int] = 0x01
BATTLE_RESULT_LOSE: Final[int] = 0x02
BATTLE_RESULT_DRAW: Final[int] = 0x03
BATTLE_RESULT_RUN: Final[int] = 0x04
BATTLE_RESULT_TELEPORTED: Final[int] = 0x05
BATTLE_RESULT_POKEMON_FLED: Final[int] = 0x06
BATTLE_RESULT_CAUGHT: Final[int] = 0x07
BATTLE_RESULT_NO_SAFARI_BALLS: Final[int] = 0x08
BATTLE_RESULT_FORFEITED: Final[int] = 0x09
BATTLE_RESULT_POKEMON_TELEPORTED: Final[int] = 0x0A

MAIN_STATE_NONE: Final[int] = 0
MAIN_STATE_OVERWORLD: Final[int] = 134571337
MAIN_STATE_BATTLE: Final[int] = 134292473

SUBSTATE_NONE: Final[int] = 0
SUBSTATE_OVERWORLD: Final[int] = 134571465
SUBSTATE_BATTLE: Final[int] = 134287637
SUBSTATE_BATTLE_ANIMATION: Final[int] = 134571453
SUBSTATE_TRANSITION_OVERWORLD: Final[int] = 134766589
SUBSTATE_INTRO_CINEMATIC: Final[int] = 135711745

WRAM_PLAYER_NAME: Final[str] = 'player_name'
WRAM_TEAM_COUNT: Final[str] = 'team_count'
WRAM_BATTLE_OUTCOME: Final[str] = 'battle_outcome'
WRAM_BATTLE_BG_TILES: Final[str] = 'battle_bg_tiles'
WRAM_CALLBACK1: Final[str] = 'callback1'
WRAM_CALLBACK2: Final[str] = 'callback2'
