# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Final, Tuple

###############################################################################
# Constants
###############################################################################

# attribute constants for GameData in data/structs.py

VAR_PLAYER_NAME: Final[str] = 'player.name'
VAR_PLAYER_ID: Final[str] = 'player.number'
VAR_PLAYER_MONEY: Final[str] = 'player.money'

VAR_PLAYER_BADGE1: Final[str] = 'player.badges.badge1'
VAR_PLAYER_BADGE2: Final[str] = 'player.badges.badge2'
VAR_PLAYER_BADGE3: Final[str] = 'player.badges.badge3'
VAR_PLAYER_BADGE4: Final[str] = 'player.badges.badge4'
VAR_PLAYER_BADGE5: Final[str] = 'player.badges.badge5'
VAR_PLAYER_BADGE6: Final[str] = 'player.badges.badge6'
VAR_PLAYER_BADGE7: Final[str] = 'player.badges.badge7'
VAR_PLAYER_BADGE8: Final[str] = 'player.badges.badge8'

VAR_PLAYER_PARTY_COUNT: Final[str] = 'player.badges.team.size'

VAR_PARTY_MON1_SPECIES: Final[str] = 'player.badges.team.slot1.species'
VAR_PARTY_MON1_NAME: Final[str] = 'player.badges.team.slot1.name'
VAR_PARTY_MON1_LEVEL: Final[str] = 'player.badges.team.slot1.level'
VAR_PARTY_MON1_HP: Final[str] = 'player.badges.team.slot1.hp'
VAR_PARTY_MON1_MAX_HP: Final[str] = 'player.badges.team.slot1.stats.hp'
VAR_PARTY_MON1_ATTACK: Final[str] = 'player.badges.team.slot1.stats.attack'
VAR_PARTY_MON1_DEFENSE: Final[str] = 'player.badges.team.slot1.stats.defense'
VAR_PARTY_MON1_SPEED: Final[str] = 'player.badges.team.slot1.stats.speed'
VAR_PARTY_MON1_SP_ATTACK: Final[str] = 'player.badges.team.slot1.stats.sp_attack'
VAR_PARTY_MON1_SP_DEFENSE: Final[str] = 'player.badges.team.slot1.stats.sp_defense'

VAR_PARTY_MON2_SPECIES: Final[str] = 'player.badges.team.slot2.species'
VAR_PARTY_MON2_NAME: Final[str] = 'player.badges.team.slot2.name'
VAR_PARTY_MON2_LEVEL: Final[str] = 'player.badges.team.slot2.level'
VAR_PARTY_MON2_HP: Final[str] = 'player.badges.team.slot2.hp'
VAR_PARTY_MON2_MAX_HP: Final[str] = 'player.badges.team.slot2.stats.hp'
VAR_PARTY_MON2_ATTACK: Final[str] = 'player.badges.team.slot2.stats.attack'
VAR_PARTY_MON2_DEFENSE: Final[str] = 'player.badges.team.slot2.stats.defense'
VAR_PARTY_MON2_SPEED: Final[str] = 'player.badges.team.slot2.stats.speed'
VAR_PARTY_MON2_SP_ATTACK: Final[str] = 'player.badges.team.slot2.stats.sp_attack'
VAR_PARTY_MON2_SP_DEFENSE: Final[str] = 'player.badges.team.slot2.stats.sp_defense'

VAR_PARTY_MON3_SPECIES: Final[str] = 'player.badges.team.slot3.species'
VAR_PARTY_MON3_NAME: Final[str] = 'player.badges.team.slot3.name'
VAR_PARTY_MON3_LEVEL: Final[str] = 'player.badges.team.slot3.level'
VAR_PARTY_MON3_HP: Final[str] = 'player.badges.team.slot3.hp'
VAR_PARTY_MON3_MAX_HP: Final[str] = 'player.badges.team.slot3.stats.hp'
VAR_PARTY_MON3_ATTACK: Final[str] = 'player.badges.team.slot3.stats.attack'
VAR_PARTY_MON3_DEFENSE: Final[str] = 'player.badges.team.slot3.stats.defense'
VAR_PARTY_MON3_SPEED: Final[str] = 'player.badges.team.slot3.stats.speed'
VAR_PARTY_MON3_SP_ATTACK: Final[str] = 'player.badges.team.slot3.stats.sp_attack'
VAR_PARTY_MON3_SP_DEFENSE: Final[str] = 'player.badges.team.slot3.stats.sp_defense'

VAR_PARTY_MON4_SPECIES: Final[str] = 'player.badges.team.slot4.species'
VAR_PARTY_MON4_NAME: Final[str] = 'player.badges.team.slot4.name'
VAR_PARTY_MON4_LEVEL: Final[str] = 'player.badges.team.slot4.level'
VAR_PARTY_MON4_HP: Final[str] = 'player.badges.team.slot4.hp'
VAR_PARTY_MON4_MAX_HP: Final[str] = 'player.badges.team.slot4.stats.hp'
VAR_PARTY_MON4_ATTACK: Final[str] = 'player.badges.team.slot4.stats.attack'
VAR_PARTY_MON4_DEFENSE: Final[str] = 'player.badges.team.slot4.stats.defense'
VAR_PARTY_MON4_SPEED: Final[str] = 'player.badges.team.slot4.stats.speed'
VAR_PARTY_MON4_SP_ATTACK: Final[str] = 'player.badges.team.slot4.stats.sp_attack'
VAR_PARTY_MON4_SP_DEFENSE: Final[str] = 'player.badges.team.slot4.stats.sp_defense'

VAR_PARTY_MON5_SPECIES: Final[str] = 'player.badges.team.slot5.species'
VAR_PARTY_MON5_NAME: Final[str] = 'player.badges.team.slot5.name'
VAR_PARTY_MON5_LEVEL: Final[str] = 'player.badges.team.slot5.level'
VAR_PARTY_MON5_HP: Final[str] = 'player.badges.team.slot5.hp'
VAR_PARTY_MON5_MAX_HP: Final[str] = 'player.badges.team.slot5.stats.hp'
VAR_PARTY_MON5_ATTACK: Final[str] = 'player.badges.team.slot5.stats.attack'
VAR_PARTY_MON5_DEFENSE: Final[str] = 'player.badges.team.slot5.stats.defense'
VAR_PARTY_MON5_SPEED: Final[str] = 'player.badges.team.slot5.stats.speed'
VAR_PARTY_MON5_SP_ATTACK: Final[str] = 'player.badges.team.slot5.stats.sp_attack'
VAR_PARTY_MON5_SP_DEFENSE: Final[str] = 'player.badges.team.slot5.stats.sp_defense'

VAR_PARTY_MON6_SPECIES: Final[str] = 'player.badges.team.slot6.species'
VAR_PARTY_MON6_NAME: Final[str] = 'player.badges.team.slot6.name'
VAR_PARTY_MON6_LEVEL: Final[str] = 'player.badges.team.slot6.level'
VAR_PARTY_MON6_HP: Final[str] = 'player.badges.team.slot6.hp'
VAR_PARTY_MON6_MAX_HP: Final[str] = 'player.badges.team.slot6.stats.hp'
VAR_PARTY_MON6_ATTACK: Final[str] = 'player.badges.team.slot6.stats.attack'
VAR_PARTY_MON6_DEFENSE: Final[str] = 'player.badges.team.slot6.stats.defense'
VAR_PARTY_MON6_SPEED: Final[str] = 'player.badges.team.slot6.stats.speed'
VAR_PARTY_MON6_SP_ATTACK: Final[str] = 'player.badges.team.slot6.stats.sp_attack'
VAR_PARTY_MON6_SP_DEFENSE: Final[str] = 'player.badges.team.slot6.stats.sp_defense'

VAR_GAME_TIME_HOURS: Final[str] = 'time.hours'
VAR_GAME_TIME_MINUTES: Final[str] = 'time.minutes'
VAR_GAME_TIME_SECONDS: Final[str] = 'time.seconds'
VAR_GAME_TIME_FRAMES: Final[str] = 'time.frames'

VAR_MAP: Final[str] = 'location'
VAR_MAP_ID: Final[str] = 'current_map.name'
VAR_MAP_GROUP: Final[str] = 'current_map.group'

VARIABLES: Final[Tuple] = tuple(v for k, v in list(globals().items()) if k.startswith('VAR_'))
