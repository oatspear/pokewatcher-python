# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Any, Final, Mapping

import logging

import pokewatcher.data.constants as game_data
from pokewatcher.data.gamehook import DataHandler
from pokewatcher.data.structs import GameData

import pokewatcher.data.crystal.constants as crystal
from pokewatcher.logic.fsm import StateMachine

###############################################################################
# Constants
###############################################################################

logger: Final[logging.Logger] = logging.getLogger(__name__)

P_SPECIES: Final[str] = 'player.team.0.species'
P_LEVEL: Final[str] = 'player.team.0.level'
P_MOVE1: Final[str] = 'player.team.0.move1'
P_MOVE2: Final[str] = 'player.team.0.move2'
P_MOVE3: Final[str] = 'player.team.0.move3'
P_MOVE4: Final[str] = 'player.team.0.move4'
P_MON_ATK: Final[str] = 'player.team.0.attack'
P_MON_DEF: Final[str] = 'player.team.0.defense'
P_MON_SPD: Final[str] = 'player.team.0.speed'
P_MON_SPATK: Final[str] = 'player.team.0.specialAttack'
P_MON_SPDEF: Final[str] = 'player.team.0.specialDefense'

P_MAP_GROUP: Final[str] = 'overworld.mapGroup'
P_MAP_NUMBER: Final[str] = 'overworld.mapNumber'
P_X_COORD: Final[str] = 'overworld.x'
P_Y_COORD: Final[str] = 'overworld.y'

P_AUDIO_CHANNEL5: Final[str] = 'audio.channel5MusicID'

P_BATTLE_MODE: Final[str] = 'battle.mode'
P_BATTLE_TYPE: Final[str] = 'battle.type'
P_BATTLE_RESULT: Final[str] = 'battle.result'
P_TRAINER_CLASS: Final[str] = 'battle.trainer.class'
P_TRAINER_NUMBER: Final[str] = 'battle.trainer.id'
P_BATTLE_ALARM: Final[str] = 'battle.lowHealthAlarm'

P_STAGE_ATK: Final[str] = 'battle.yourPokemon.modStageAttack'
P_STAGE_DEF: Final[str] = 'battle.yourPokemon.modStageDefense'
P_STAGE_SPD: Final[str] = 'battle.yourPokemon.modStageSpeed'
P_STAGE_SPATK: Final[str] = 'battle.yourPokemon.modStageSpecialAttack'
P_STAGE_SPDEF: Final[str] = 'battle.yourPokemon.modStageSpecialDefense'
P_STAGE_ACC: Final[str] = 'battle.yourPokemon.modStageAccuracy'
P_STAGE_EVA: Final[str] = 'battle.yourPokemon.modStageEvasion'

P_BATTLE_ATK: Final[str] = 'battle.yourPokemon.battleStatAttack'
P_BATTLE_DEF: Final[str] = 'battle.yourPokemon.battleStatDefense'
P_BATTLE_SPD: Final[str] = 'battle.yourPokemon.battleStatSpeed'
P_BATTLE_SPATK: Final[str] = 'battle.yourPokemon.battleStatSpecialAttack'
P_BATTLE_SPDEF: Final[str] = 'battle.yourPokemon.battleStatSpecialDefense'

P_PLAYER_ID: Final[str] = 'player.playerId'
P_GAME_TIME_HOURS: Final[str] = 'gameTime.hours'
P_GAME_TIME_MINUTES: Final[str] = 'gameTime.minutes'
P_GAME_TIME_SECONDS: Final[str] = 'gameTime.seconds'
P_GAME_TIME_FRAMES: Final[str] = 'gameTime.frames'

P_BADGE1: Final[str] = 'player.badges.zephyrBadge'
P_BADGE2: Final[str] = 'player.badges.hiveBadge'
P_BADGE3: Final[str] = 'player.badges.plainBadge'
P_BADGE4: Final[str] = 'player.badges.fogBadge'
P_BADGE5: Final[str] = 'player.badges.stormBadge'
P_BADGE6: Final[str] = 'player.badges.mineralBadge'
P_BADGE7: Final[str] = 'player.badges.glacierBadge'
P_BADGE8: Final[str] = 'player.badges.risingBadge'

P_KANTO_BADGE1: Final[str] = 'player.badges.boulderBadge'
P_KANTO_BADGE2: Final[str] = 'player.badges.cascadeBadge'
P_KANTO_BADGE3: Final[str] = 'player.badges.thunderBadge'
P_KANTO_BADGE4: Final[str] = 'player.badges.rainbowBadge'
P_KANTO_BADGE5: Final[str] = 'player.badges.soulBadge'
P_KANTO_BADGE6: Final[str] = 'player.badges.marshBadge'
P_KANTO_BADGE7: Final[str] = 'player.badges.volcanoBadge'
P_KANTO_BADGE8: Final[str] = 'player.badges.earthBadge'

PROPERTIES: Final[Mapping[str, Mapping[str, Any]]] = {
    P_PLAYER_ID: {
        'type': 'int',
        'bytes': True,
        'label': crystal.WRAM_PLAYER_ID,
        'store': game_data.VAR_PLAYER_ID,
    },
    P_GAME_TIME_HOURS: {
        'type': 'int',
        'bytes': True,
        'label': crystal.WRAM_PLAY_TIME_HOURS,
        'store': game_data.VAR_GAME_TIME_HOURS,
    },
    P_GAME_TIME_MINUTES: {
        'type': 'int',
        'bytes': True,
        'label': crystal.WRAM_PLAY_TIME_MINUTES,
        'store': game_data.VAR_GAME_TIME_MINUTES,
    },
    P_GAME_TIME_SECONDS: {
        'type': 'int',
        'bytes': True,
        'label': crystal.WRAM_PLAY_TIME_SECONDS,
        'store': game_data.VAR_GAME_TIME_SECONDS,
    },
    P_GAME_TIME_FRAMES: {
        'type': 'int',
        'bytes': True,
        'label': crystal.WRAM_PLAY_TIME_FRAMES,
        'store': game_data.VAR_GAME_TIME_FRAMES,
    },
    P_SPECIES: {
        'type': 'string',
        'key': 'name',
        'store': game_data.VAR_PARTY_MON1_SPECIES,
    },
    P_LEVEL: {
        'type': 'int',
        'bytes': True,
        'store': game_data.VAR_PARTY_MON1_LEVEL,
    },
    P_MOVE1: {
        'type': 'string',
        # 'bytes': True,
        'store': game_data.VAR_PARTY_MON1_MOVE1,
    },
    P_MOVE2: {
        'type': 'string',
        # 'bytes': True,
        'store': game_data.VAR_PARTY_MON1_MOVE2,
    },
    P_MOVE3: {
        'type': 'string',
        # 'bytes': True,
        'store': game_data.VAR_PARTY_MON1_MOVE3,
    },
    P_MOVE4: {
        'type': 'string',
        # 'bytes': True,
        'store': game_data.VAR_PARTY_MON1_MOVE4,
    },
    P_MON_ATK: {
        'type': 'int',
        'bytes': True,
        'store': game_data.VAR_PARTY_MON1_ATTACK,
    },
    P_MON_DEF: {
        'type': 'int',
        'bytes': True,
        'store': game_data.VAR_PARTY_MON1_DEFENSE,
    },
    P_MON_SPD: {
        'type': 'int',
        'bytes': True,
        'store': game_data.VAR_PARTY_MON1_SPEED,
    },
    P_MON_SPATK: {
        'type': 'int',
        'bytes': True,
        'store': game_data.VAR_PARTY_MON1_SP_ATTACK,
    },
    P_MON_SPDEF: {
        'type': 'int',
        'bytes': True,
        'store': game_data.VAR_PARTY_MON1_SP_DEFENSE,
    },
    P_MAP_GROUP: {
        'type': 'string',
        # 'store': game_data.VAR_MAP,
        'label': crystal.WRAM_MAP_GROUP,
    },
    P_MAP_NUMBER: {
        'type': 'int',
        # 'store': game_data.VAR_MAP,
        'label': crystal.WRAM_MAP_NUMBER,
    },
    P_X_COORD: {
        'type': 'int',
        'label': crystal.WRAM_X_COORD,
    },
    P_Y_COORD: {
        'type': 'int',
        'label': crystal.WRAM_Y_COORD,
    },
    P_AUDIO_CHANNEL5: {
        'type': 'int',
        'bytes': True,
        'label': crystal.WRAM_AUDIO_CHANNEL5,
    },
    P_BATTLE_MODE: {
        'type': 'int',
        'bytes': True,
        'label': crystal.WRAM_BATTLE_MODE,
    },
    P_BATTLE_TYPE: {
        'type': 'int',
        'bytes': True,
        'label': crystal.WRAM_BATTLE_TYPE,
    },
    P_BATTLE_RESULT: {
        'type': 'int',
        'bytes': True,
        'label': crystal.WRAM_BATTLE_RESULT,
    },
    P_TRAINER_CLASS: {
        'type': 'string',
        'store': game_data.VAR_BATTLE_TRAINER_CLASS,
    },
    P_TRAINER_NUMBER: {
        'type': 'int',
        'bytes': True,
        'store': game_data.VAR_BATTLE_TRAINER_ID,
    },
    P_BATTLE_ALARM: {
        'type': 'bool',
        'bytes': True,
        'label': crystal.WRAM_LOW_HEALTH_ALARM,
    },
    P_STAGE_ATK: {
        'type': 'int',
        'store': game_data.VAR_BATTLE_PLAYER_STAGE_ATTACK,
        'default': 0,
    },
    P_STAGE_DEF: {
        'type': 'int',
        'store': game_data.VAR_BATTLE_PLAYER_STAGE_DEFENSE,
        'default': 0,
    },
    P_STAGE_SPD: {
        'type': 'int',
        'store': game_data.VAR_BATTLE_PLAYER_STAGE_SPEED,
        'default': 0,
    },
    P_STAGE_SPATK: {
        'type': 'int',
        'store': game_data.VAR_BATTLE_PLAYER_STAGE_SP_ATTACK,
        'default': 0,
    },
    P_STAGE_SPDEF: {
        'type': 'int',
        'store': game_data.VAR_BATTLE_PLAYER_STAGE_SP_DEFENSE,
        'default': 0,
    },
    P_STAGE_ACC: {
        'type': 'int',
        'store': game_data.VAR_BATTLE_PLAYER_STAGE_ACCURACY,
        'default': 0,
    },
    P_STAGE_EVA: {
        'type': 'int',
        'store': game_data.VAR_BATTLE_PLAYER_STAGE_EVASION,
        'default': 0,
    },
    P_BATTLE_ATK: {
        'type': 'int',
        'bytes': True,
        'store': game_data.VAR_BATTLE_PLAYER_ATTACK,
    },
    P_BATTLE_DEF: {
        'type': 'int',
        'bytes': True,
        'store': game_data.VAR_BATTLE_PLAYER_DEFENSE,
    },
    P_BATTLE_SPD: {
        'type': 'int',
        'bytes': True,
        'store': game_data.VAR_BATTLE_PLAYER_SPEED,
    },
    P_BATTLE_SPATK: {
        'type': 'int',
        'bytes': True,
        'store': game_data.VAR_BATTLE_PLAYER_SP_ATTACK,
    },
    P_BATTLE_SPDEF: {
        'type': 'int',
        'bytes': True,
        'store': game_data.VAR_BATTLE_PLAYER_SP_DEFENSE,
    },
    P_BADGE1: {
        'type': 'bool',
        'bytes': True,
        'store': game_data.VAR_PLAYER_BADGE1,
    },
    P_BADGE2: {
        'type': 'bool',
        'bytes': True,
        'store': game_data.VAR_PLAYER_BADGE2,
    },
    P_BADGE3: {
        'type': 'bool',
        'bytes': True,
        'store': game_data.VAR_PLAYER_BADGE3,
    },
    P_BADGE4: {
        'type': 'bool',
        'bytes': True,
        'store': game_data.VAR_PLAYER_BADGE4,
    },
    P_BADGE5: {
        'type': 'bool',
        'bytes': True,
        'store': game_data.VAR_PLAYER_BADGE5,
    },
    P_BADGE6: {
        'type': 'bool',
        'bytes': True,
        'store': game_data.VAR_PLAYER_BADGE6,
    },
    P_BADGE7: {
        'type': 'bool',
        'bytes': True,
        'store': game_data.VAR_PLAYER_BADGE7,
    },
    P_BADGE8: {
        'type': 'bool',
        'bytes': True,
        'store': game_data.VAR_PLAYER_BADGE8,
    },
}

###############################################################################
# Interface
###############################################################################


def load_data_handler(data: GameData, fsm: StateMachine) -> DataHandler:
    handler = DataHandler(data, fsm)
    for prop, metadata in PROPERTIES.items():
        handler.configure_property(prop, metadata)
    return handler
