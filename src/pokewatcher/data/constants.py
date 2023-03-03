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

VAR_PLAYER_PARTY_COUNT: Final[str] = 'player.team.size'

VAR_PARTY_MON1_SPECIES: Final[str] = 'player.team.slot1.species'
VAR_PARTY_MON1_NAME: Final[str] = 'player.team.slot1.name'
VAR_PARTY_MON1_LEVEL: Final[str] = 'player.team.slot1.level'
VAR_PARTY_MON1_HP: Final[str] = 'player.team.slot1.hp'
VAR_PARTY_MON1_MAX_HP: Final[str] = 'player.team.slot1.stats.hp'
VAR_PARTY_MON1_ATTACK: Final[str] = 'player.team.slot1.stats.attack'
VAR_PARTY_MON1_DEFENSE: Final[str] = 'player.team.slot1.stats.defense'
VAR_PARTY_MON1_SPEED: Final[str] = 'player.team.slot1.stats.speed'
VAR_PARTY_MON1_SPECIAL: Final[str] = 'player.team.slot1.stats.special'
VAR_PARTY_MON1_SP_ATTACK: Final[str] = 'player.team.slot1.stats.sp_attack'
VAR_PARTY_MON1_SP_DEFENSE: Final[str] = 'player.team.slot1.stats.sp_defense'
VAR_PARTY_MON1_MOVE1: Final[str] = 'player.team.slot1.move1'
VAR_PARTY_MON1_MOVE2: Final[str] = 'player.team.slot1.move2'
VAR_PARTY_MON1_MOVE3: Final[str] = 'player.team.slot1.move3'
VAR_PARTY_MON1_MOVE4: Final[str] = 'player.team.slot1.move4'

VAR_PARTY_MON2_SPECIES: Final[str] = 'player.team.slot2.species'
VAR_PARTY_MON2_NAME: Final[str] = 'player.team.slot2.name'
VAR_PARTY_MON2_LEVEL: Final[str] = 'player.team.slot2.level'
VAR_PARTY_MON2_HP: Final[str] = 'player.team.slot2.hp'
VAR_PARTY_MON2_MAX_HP: Final[str] = 'player.team.slot2.stats.hp'
VAR_PARTY_MON2_ATTACK: Final[str] = 'player.team.slot2.stats.attack'
VAR_PARTY_MON2_DEFENSE: Final[str] = 'player.team.slot2.stats.defense'
VAR_PARTY_MON2_SPEED: Final[str] = 'player.team.slot2.stats.speed'
VAR_PARTY_MON2_SPECIAL: Final[str] = 'player.team.slot2.stats.special'
VAR_PARTY_MON2_SP_ATTACK: Final[str] = 'player.team.slot2.stats.sp_attack'
VAR_PARTY_MON2_SP_DEFENSE: Final[str] = 'player.team.slot2.stats.sp_defense'
VAR_PARTY_MON2_MOVE1: Final[str] = 'player.team.slot2.move1'
VAR_PARTY_MON2_MOVE2: Final[str] = 'player.team.slot2.move2'
VAR_PARTY_MON2_MOVE3: Final[str] = 'player.team.slot2.move3'
VAR_PARTY_MON2_MOVE4: Final[str] = 'player.team.slot2.move4'

VAR_PARTY_MON3_SPECIES: Final[str] = 'player.team.slot3.species'
VAR_PARTY_MON3_NAME: Final[str] = 'player.team.slot3.name'
VAR_PARTY_MON3_LEVEL: Final[str] = 'player.team.slot3.level'
VAR_PARTY_MON3_HP: Final[str] = 'player.team.slot3.hp'
VAR_PARTY_MON3_MAX_HP: Final[str] = 'player.team.slot3.stats.hp'
VAR_PARTY_MON3_ATTACK: Final[str] = 'player.team.slot3.stats.attack'
VAR_PARTY_MON3_DEFENSE: Final[str] = 'player.team.slot3.stats.defense'
VAR_PARTY_MON3_SPEED: Final[str] = 'player.team.slot3.stats.speed'
VAR_PARTY_MON3_SPECIAL: Final[str] = 'player.team.slot3.stats.special'
VAR_PARTY_MON3_SP_ATTACK: Final[str] = 'player.team.slot3.stats.sp_attack'
VAR_PARTY_MON3_SP_DEFENSE: Final[str] = 'player.team.slot3.stats.sp_defense'
VAR_PARTY_MON3_MOVE1: Final[str] = 'player.team.slot3.move1'
VAR_PARTY_MON3_MOVE2: Final[str] = 'player.team.slot3.move2'
VAR_PARTY_MON3_MOVE3: Final[str] = 'player.team.slot3.move3'
VAR_PARTY_MON3_MOVE4: Final[str] = 'player.team.slot3.move4'

VAR_PARTY_MON4_SPECIES: Final[str] = 'player.team.slot4.species'
VAR_PARTY_MON4_NAME: Final[str] = 'player.team.slot4.name'
VAR_PARTY_MON4_LEVEL: Final[str] = 'player.team.slot4.level'
VAR_PARTY_MON4_HP: Final[str] = 'player.team.slot4.hp'
VAR_PARTY_MON4_MAX_HP: Final[str] = 'player.team.slot4.stats.hp'
VAR_PARTY_MON4_ATTACK: Final[str] = 'player.team.slot4.stats.attack'
VAR_PARTY_MON4_DEFENSE: Final[str] = 'player.team.slot4.stats.defense'
VAR_PARTY_MON4_SPEED: Final[str] = 'player.team.slot4.stats.speed'
VAR_PARTY_MON4_SPECIAL: Final[str] = 'player.team.slot4.stats.special'
VAR_PARTY_MON4_SP_ATTACK: Final[str] = 'player.team.slot4.stats.sp_attack'
VAR_PARTY_MON4_SP_DEFENSE: Final[str] = 'player.team.slot4.stats.sp_defense'
VAR_PARTY_MON4_MOVE1: Final[str] = 'player.team.slot4.move1'
VAR_PARTY_MON4_MOVE2: Final[str] = 'player.team.slot4.move2'
VAR_PARTY_MON4_MOVE3: Final[str] = 'player.team.slot4.move3'
VAR_PARTY_MON4_MOVE4: Final[str] = 'player.team.slot4.move4'

VAR_PARTY_MON5_SPECIES: Final[str] = 'player.team.slot5.species'
VAR_PARTY_MON5_NAME: Final[str] = 'player.team.slot5.name'
VAR_PARTY_MON5_LEVEL: Final[str] = 'player.team.slot5.level'
VAR_PARTY_MON5_HP: Final[str] = 'player.team.slot5.hp'
VAR_PARTY_MON5_MAX_HP: Final[str] = 'player.team.slot5.stats.hp'
VAR_PARTY_MON5_ATTACK: Final[str] = 'player.team.slot5.stats.attack'
VAR_PARTY_MON5_DEFENSE: Final[str] = 'player.team.slot5.stats.defense'
VAR_PARTY_MON5_SPEED: Final[str] = 'player.team.slot5.stats.speed'
VAR_PARTY_MON5_SPECIAL: Final[str] = 'player.team.slot5.stats.special'
VAR_PARTY_MON5_SP_ATTACK: Final[str] = 'player.team.slot5.stats.sp_attack'
VAR_PARTY_MON5_SP_DEFENSE: Final[str] = 'player.team.slot5.stats.sp_defense'
VAR_PARTY_MON5_MOVE1: Final[str] = 'player.team.slot5.move1'
VAR_PARTY_MON5_MOVE2: Final[str] = 'player.team.slot5.move2'
VAR_PARTY_MON5_MOVE3: Final[str] = 'player.team.slot5.move3'
VAR_PARTY_MON5_MOVE4: Final[str] = 'player.team.slot5.move4'

VAR_PARTY_MON6_SPECIES: Final[str] = 'player.team.slot6.species'
VAR_PARTY_MON6_NAME: Final[str] = 'player.team.slot6.name'
VAR_PARTY_MON6_LEVEL: Final[str] = 'player.team.slot6.level'
VAR_PARTY_MON6_HP: Final[str] = 'player.team.slot6.hp'
VAR_PARTY_MON6_MAX_HP: Final[str] = 'player.team.slot6.stats.hp'
VAR_PARTY_MON6_ATTACK: Final[str] = 'player.team.slot6.stats.attack'
VAR_PARTY_MON6_DEFENSE: Final[str] = 'player.team.slot6.stats.defense'
VAR_PARTY_MON6_SPEED: Final[str] = 'player.team.slot6.stats.speed'
VAR_PARTY_MON6_SPECIAL: Final[str] = 'player.team.slot6.stats.special'
VAR_PARTY_MON6_SP_ATTACK: Final[str] = 'player.team.slot6.stats.sp_attack'
VAR_PARTY_MON6_SP_DEFENSE: Final[str] = 'player.team.slot6.stats.sp_defense'
VAR_PARTY_MON6_MOVE1: Final[str] = 'player.team.slot6.move1'
VAR_PARTY_MON6_MOVE2: Final[str] = 'player.team.slot6.move2'
VAR_PARTY_MON6_MOVE3: Final[str] = 'player.team.slot6.move3'
VAR_PARTY_MON6_MOVE4: Final[str] = 'player.team.slot6.move4'

VAR_GAME_TIME_HOURS: Final[str] = 'time.hours'
VAR_GAME_TIME_MINUTES: Final[str] = 'time.minutes'
VAR_GAME_TIME_SECONDS: Final[str] = 'time.seconds'
VAR_GAME_TIME_FRAMES: Final[str] = 'time.frames'

VAR_MAP: Final[str] = 'location'
VAR_MAP_ID: Final[str] = 'current_map.name'
VAR_MAP_GROUP: Final[str] = 'current_map.group'

VAR_BATTLE_VS_WILD: Final[str] = 'battle.is_vs_wild'
VAR_BATTLE_ONGOING: Final[str] = 'battle.ongoing'
VAR_BATTLE_RESULT: Final[str] = 'battle.result'

VAR_BATTLE_PLAYER_NAME: Final[str] = 'battle.player.name'
VAR_BATTLE_PLAYER_INDEX: Final[str] = 'battle.player.party_index'
VAR_BATTLE_PLAYER_HP: Final[str] = 'battle.player.hp'
VAR_BATTLE_PLAYER_MAX_HP: Final[str] = 'battle.player.stats.hp'
VAR_BATTLE_PLAYER_ATTACK: Final[str] = 'battle.player.stats.attack'
VAR_BATTLE_PLAYER_DEFENSE: Final[str] = 'battle.player.stats.defense'
VAR_BATTLE_PLAYER_SPEED: Final[str] = 'battle.player.stats.speed'
VAR_BATTLE_PLAYER_SPECIAL: Final[str] = 'battle.player.stats.special'
VAR_BATTLE_PLAYER_SP_ATTACK: Final[str] = 'battle.player.stats.sp_attack'
VAR_BATTLE_PLAYER_SP_DEFENSE: Final[str] = 'battle.player.stats.sp_defense'
VAR_BATTLE_PLAYER_STAGE_ATTACK: Final[str] = 'battle.player.stages.attack'
VAR_BATTLE_PLAYER_STAGE_DEFENSE: Final[str] = 'battle.player.stages.defense'
VAR_BATTLE_PLAYER_STAGE_SPEED: Final[str] = 'battle.player.stages.speed'
VAR_BATTLE_PLAYER_STAGE_SPECIAL: Final[str] = 'battle.player.stages.special'
VAR_BATTLE_PLAYER_STAGE_SP_ATTACK: Final[str] = 'battle.player.stages.sp_attack'
VAR_BATTLE_PLAYER_STAGE_SP_DEFENSE: Final[str] = 'battle.player.stages.sp_defense'
VAR_BATTLE_PLAYER_STAGE_ACCURACY: Final[str] = 'battle.player.stages.accuracy'
VAR_BATTLE_PLAYER_STAGE_EVASION: Final[str] = 'battle.player.stages.evasion'

VAR_BATTLE_ENEMY_NAME: Final[str] = 'battle.enemy.name'
VAR_BATTLE_ENEMY_INDEX: Final[str] = 'battle.enemy.party_index'
VAR_BATTLE_ENEMY_HP: Final[str] = 'battle.enemy.hp'
VAR_BATTLE_ENEMY_MAX_HP: Final[str] = 'battle.enemy.stats.hp'
VAR_BATTLE_ENEMY_ATTACK: Final[str] = 'battle.enemy.stats.attack'
VAR_BATTLE_ENEMY_DEFENSE: Final[str] = 'battle.enemy.stats.defense'
VAR_BATTLE_ENEMY_SPEED: Final[str] = 'battle.enemy.stats.speed'
VAR_BATTLE_ENEMY_SPECIAL: Final[str] = 'battle.enemy.stats.special'
VAR_BATTLE_ENEMY_SP_ATTACK: Final[str] = 'battle.enemy.stats.sp_attack'
VAR_BATTLE_ENEMY_SP_DEFENSE: Final[str] = 'battle.enemy.stats.sp_defense'
VAR_BATTLE_ENEMY_STAGE_ATTACK: Final[str] = 'battle.enemy.stages.attack'
VAR_BATTLE_ENEMY_STAGE_DEFENSE: Final[str] = 'battle.enemy.stages.defense'
VAR_BATTLE_ENEMY_STAGE_SPEED: Final[str] = 'battle.enemy.stages.speed'
VAR_BATTLE_ENEMY_STAGE_SPECIAL: Final[str] = 'battle.enemy.stages.special'
VAR_BATTLE_ENEMY_STAGE_SP_ATTACK: Final[str] = 'battle.enemy.stages.sp_attack'
VAR_BATTLE_ENEMY_STAGE_SP_DEFENSE: Final[str] = 'battle.enemy.stages.sp_defense'
VAR_BATTLE_ENEMY_STAGE_ACCURACY: Final[str] = 'battle.enemy.stages.accuracy'
VAR_BATTLE_ENEMY_STAGE_EVASION: Final[str] = 'battle.enemy.stages.evasion'

VAR_BATTLE_TRAINER_NAME: Final[str] = 'battle.trainer.name'
VAR_BATTLE_TRAINER_ID: Final[str] = 'battle.trainer.number'
VAR_BATTLE_TRAINER_CLASS: Final[str] = 'battle.trainer.trainer_class'

VAR_BATTLE_TRAINER_MON1_SPECIES: Final[str] = 'battle.trainer.slot1.species'
VAR_BATTLE_TRAINER_MON1_NAME: Final[str] = 'battle.trainer.slot1.name'
VAR_BATTLE_TRAINER_MON1_LEVEL: Final[str] = 'battle.trainer.slot1.level'
VAR_BATTLE_TRAINER_MON1_HP: Final[str] = 'battle.trainer.slot1.hp'
VAR_BATTLE_TRAINER_MON1_MAX_HP: Final[str] = 'battle.trainer.slot1.stats.hp'
VAR_BATTLE_TRAINER_MON1_ATTACK: Final[str] = 'battle.trainer.slot1.stats.attack'
VAR_BATTLE_TRAINER_MON1_DEFENSE: Final[str] = 'battle.trainer.slot1.stats.defense'
VAR_BATTLE_TRAINER_MON1_SPEED: Final[str] = 'battle.trainer.slot1.stats.speed'
VAR_BATTLE_TRAINER_MON1_SP_ATTACK: Final[str] = 'battle.trainer.slot1.stats.sp_attack'
VAR_BATTLE_TRAINER_MON1_SP_DEFENSE: Final[str] = 'battle.trainer.slot1.stats.sp_defense'

VAR_BATTLE_TRAINER_MON2_SPECIES: Final[str] = 'battle.trainer.slot2.species'
VAR_BATTLE_TRAINER_MON2_NAME: Final[str] = 'battle.trainer.slot2.name'
VAR_BATTLE_TRAINER_MON2_LEVEL: Final[str] = 'battle.trainer.slot2.level'
VAR_BATTLE_TRAINER_MON2_HP: Final[str] = 'battle.trainer.slot2.hp'
VAR_BATTLE_TRAINER_MON2_MAX_HP: Final[str] = 'battle.trainer.slot2.stats.hp'
VAR_BATTLE_TRAINER_MON2_ATTACK: Final[str] = 'battle.trainer.slot2.stats.attack'
VAR_BATTLE_TRAINER_MON2_DEFENSE: Final[str] = 'battle.trainer.slot2.stats.defense'
VAR_BATTLE_TRAINER_MON2_SPEED: Final[str] = 'battle.trainer.slot2.stats.speed'
VAR_BATTLE_TRAINER_MON2_SP_ATTACK: Final[str] = 'battle.trainer.slot2.stats.sp_attack'
VAR_BATTLE_TRAINER_MON2_SP_DEFENSE: Final[str] = 'battle.trainer.slot2.stats.sp_defense'

VAR_BATTLE_TRAINER_MON3_SPECIES: Final[str] = 'battle.trainer.slot3.species'
VAR_BATTLE_TRAINER_MON3_NAME: Final[str] = 'battle.trainer.slot3.name'
VAR_BATTLE_TRAINER_MON3_LEVEL: Final[str] = 'battle.trainer.slot3.level'
VAR_BATTLE_TRAINER_MON3_HP: Final[str] = 'battle.trainer.slot3.hp'
VAR_BATTLE_TRAINER_MON3_MAX_HP: Final[str] = 'battle.trainer.slot3.stats.hp'
VAR_BATTLE_TRAINER_MON3_ATTACK: Final[str] = 'battle.trainer.slot3.stats.attack'
VAR_BATTLE_TRAINER_MON3_DEFENSE: Final[str] = 'battle.trainer.slot3.stats.defense'
VAR_BATTLE_TRAINER_MON3_SPEED: Final[str] = 'battle.trainer.slot3.stats.speed'
VAR_BATTLE_TRAINER_MON3_SP_ATTACK: Final[str] = 'battle.trainer.slot3.stats.sp_attack'
VAR_BATTLE_TRAINER_MON3_SP_DEFENSE: Final[str] = 'battle.trainer.slot3.stats.sp_defense'

VAR_BATTLE_TRAINER_MON4_SPECIES: Final[str] = 'battle.trainer.slot4.species'
VAR_BATTLE_TRAINER_MON4_NAME: Final[str] = 'battle.trainer.slot4.name'
VAR_BATTLE_TRAINER_MON4_LEVEL: Final[str] = 'battle.trainer.slot4.level'
VAR_BATTLE_TRAINER_MON4_HP: Final[str] = 'battle.trainer.slot4.hp'
VAR_BATTLE_TRAINER_MON4_MAX_HP: Final[str] = 'battle.trainer.slot4.stats.hp'
VAR_BATTLE_TRAINER_MON4_ATTACK: Final[str] = 'battle.trainer.slot4.stats.attack'
VAR_BATTLE_TRAINER_MON4_DEFENSE: Final[str] = 'battle.trainer.slot4.stats.defense'
VAR_BATTLE_TRAINER_MON4_SPEED: Final[str] = 'battle.trainer.slot4.stats.speed'
VAR_BATTLE_TRAINER_MON4_SP_ATTACK: Final[str] = 'battle.trainer.slot4.stats.sp_attack'
VAR_BATTLE_TRAINER_MON4_SP_DEFENSE: Final[str] = 'battle.trainer.slot4.stats.sp_defense'

VAR_BATTLE_TRAINER_MON5_SPECIES: Final[str] = 'battle.trainer.slot5.species'
VAR_BATTLE_TRAINER_MON5_NAME: Final[str] = 'battle.trainer.slot5.name'
VAR_BATTLE_TRAINER_MON5_LEVEL: Final[str] = 'battle.trainer.slot5.level'
VAR_BATTLE_TRAINER_MON5_HP: Final[str] = 'battle.trainer.slot5.hp'
VAR_BATTLE_TRAINER_MON5_MAX_HP: Final[str] = 'battle.trainer.slot5.stats.hp'
VAR_BATTLE_TRAINER_MON5_ATTACK: Final[str] = 'battle.trainer.slot5.stats.attack'
VAR_BATTLE_TRAINER_MON5_DEFENSE: Final[str] = 'battle.trainer.slot5.stats.defense'
VAR_BATTLE_TRAINER_MON5_SPEED: Final[str] = 'battle.trainer.slot5.stats.speed'
VAR_BATTLE_TRAINER_MON5_SP_ATTACK: Final[str] = 'battle.trainer.slot5.stats.sp_attack'
VAR_BATTLE_TRAINER_MON5_SP_DEFENSE: Final[str] = 'battle.trainer.slot5.stats.sp_defense'

VAR_BATTLE_TRAINER_MON6_SPECIES: Final[str] = 'battle.trainer.slot6.species'
VAR_BATTLE_TRAINER_MON6_NAME: Final[str] = 'battle.trainer.slot6.name'
VAR_BATTLE_TRAINER_MON6_LEVEL: Final[str] = 'battle.trainer.slot6.level'
VAR_BATTLE_TRAINER_MON6_HP: Final[str] = 'battle.trainer.slot6.hp'
VAR_BATTLE_TRAINER_MON6_MAX_HP: Final[str] = 'battle.trainer.slot6.stats.hp'
VAR_BATTLE_TRAINER_MON6_ATTACK: Final[str] = 'battle.trainer.slot6.stats.attack'
VAR_BATTLE_TRAINER_MON6_DEFENSE: Final[str] = 'battle.trainer.slot6.stats.defense'
VAR_BATTLE_TRAINER_MON6_SPEED: Final[str] = 'battle.trainer.slot6.stats.speed'
VAR_BATTLE_TRAINER_MON6_SP_ATTACK: Final[str] = 'battle.trainer.slot6.stats.sp_attack'
VAR_BATTLE_TRAINER_MON6_SP_DEFENSE: Final[str] = 'battle.trainer.slot6.stats.sp_defense'

VARIABLES: Final[Tuple] = tuple(v for k, v in list(globals().items()) if k.startswith('VAR_'))
