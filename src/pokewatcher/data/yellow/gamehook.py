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
import pokewatcher.data.yellow.constants as yellow
from pokewatcher.logic.fsm import StateMachine

###############################################################################
# Constants
###############################################################################

logger: Final[logging.Logger] = logging.getLogger(__name__)

P_PLAYER_ID = 'playerId'

P_SPECIES = 'player.team.0.species'
P_LEVEL = 'player.team.0.level'
P_MOVE1 = 'player.team.0.move1'
P_MOVE2 = 'player.team.0.move2'
P_MOVE3 = 'player.team.0.move3'
P_MOVE4 = 'player.team.0.move4'
P_MON_ATK = 'player.team.0.Attack'
P_MON_DEF = 'player.team.0.Defense'
P_MON_SPD = 'player.team.0.Speed'
P_MON_SPC = 'player.team.0.Special'
P_MON_SPATK = 'player.team.0.SpecialAttack'
P_MON_SPDEF = 'player.team.0.SpecialDefense'

P_MAP = 'overworld.map'

P_AUDIO_SOUND = 'audio.currentSound'
P_AUDIO_CH5 = 'audio.channel5'
P_AUDIO_CH6 = 'audio.channel6'

P_BATTLE_TYPE = 'battle.type'
P_TRAINER_CLASS = 'battle.trainer.class'
P_TRAINER_NUMBER = 'battle.trainer.number'
P_GYM_LEADER = 'battle.trainer.gymLeader'
P_BATTLE_ALARM = 'battle.lowHealthAlarm'

P_STAGE_ATK = 'battle.yourPokemon.modStageAttack'
P_STAGE_DEF = 'battle.yourPokemon.modStageDefense'
P_STAGE_SPD = 'battle.yourPokemon.modStageSpeed'
P_STAGE_SPC = 'battle.yourPokemon.modStageSpecial'
P_STAGE_ACC = 'battle.yourPokemon.modStageAccuracy'
P_STAGE_EVA = 'battle.yourPokemon.modStageEvasion'

P_BATTLE_ATK = 'battle.yourPokemon.battleStatAttack'
P_BATTLE_DEF = 'battle.yourPokemon.battleStatDefense'
P_BATTLE_SPD = 'battle.yourPokemon.battleStatSpeed'
P_BATTLE_SPC = 'battle.yourPokemon.battleStatSpecial'

P_GAME_TIME_HOURS = 'gameTime.hours'
P_GAME_TIME_MINUTES = 'gameTime.minutes'
P_GAME_TIME_SECONDS = 'gameTime.seconds'

P_BADGE1 = 'player.badges.boulderBadge'
P_BADGE2 = 'player.badges.cascadeBadge'
P_BADGE3 = 'player.badges.thunderBadge'
P_BADGE4 = 'player.badges.rainbowBadge'
P_BADGE5 = 'player.badges.soulBadge'
P_BADGE6 = 'player.badges.marshBadge'
P_BADGE7 = 'player.badges.volcanoBadge'
P_BADGE8 = 'player.badges.earthBadge'

PROPERTIES: Final[Mapping[str, Mapping[str, Any]]] = {
    P_PLAYER_ID: {
        'type': 'int',
        'bytes': True,
        'label': yellow.WRAM_PLAYER_ID,
        'store': game_data.VAR_PLAYER_ID,
    },
    P_GAME_TIME_HOURS: {
        'type': 'int',
        'bytes': True,
        'store': game_data.VAR_GAME_TIME_HOURS,
    },
    P_GAME_TIME_MINUTES: {
        'type': 'int',
        'bytes': True,
        'store': game_data.VAR_GAME_TIME_MINUTES,
    },
    P_GAME_TIME_SECONDS: {
        'type': 'int',
        'bytes': True,
        'store': game_data.VAR_GAME_TIME_SECONDS,
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
        'type': 'int',
        'bytes': True,
        'store': game_data.VAR_PARTY_MON1_MOVE1,
    },
    P_MOVE2: {
        'type': 'int',
        'bytes': True,
        'store': game_data.VAR_PARTY_MON1_MOVE2,
    },
    P_MOVE3: {
        'type': 'int',
        'bytes': True,
        'store': game_data.VAR_PARTY_MON1_MOVE3,
    },
    P_MOVE4: {
        'type': 'int',
        'bytes': True,
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
    P_MON_SPC: {
        'type': 'int',
        'bytes': True,
        'store': game_data.VAR_PARTY_MON1_SPECIAL,
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
    P_MAP: {
        'type': 'string',
        'store': game_data.VAR_MAP,
    },
    # P_AUDIO_SOUND: {},
    P_AUDIO_CH5: {
        'type': 'int',
        'bytes': True,
        'label': yellow.WRAM_AUDIO_CHANNEL5,
    },
    # P_AUDIO_CH6: {},
    P_BATTLE_TYPE: {
        'type': 'int',
        'bytes': True,
        'label': yellow.WRAM_BATTLE_TYPE,
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
    # P_GYM_LEADER: {},
    P_BATTLE_ALARM: {
        'type': 'int',
        'bytes': True,
        'label': yellow.WRAM_LOW_HEALTH_ALARM,
    },
    P_STAGE_ATK: {
        'type': 'int',
        'bytes': True,
        'store': game_data.VAR_BATTLE_PLAYER_STAGE_ATTACK,
    },
    P_STAGE_DEF: {
        'type': 'int',
        'bytes': True,
        'store': game_data.VAR_BATTLE_PLAYER_STAGE_DEFENSE,
    },
    P_STAGE_SPD: {
        'type': 'int',
        'bytes': True,
        'store': game_data.VAR_BATTLE_PLAYER_STAGE_SPEED,
    },
    P_STAGE_SPC: {
        'type': 'int',
        'bytes': True,
        'store': game_data.VAR_BATTLE_PLAYER_STAGE_SPECIAL,
    },
    P_STAGE_ACC: {
        'type': 'int',
        'bytes': True,
        'store': game_data.VAR_BATTLE_PLAYER_STAGE_ACCURACY,
    },
    P_STAGE_EVA: {
        'type': 'int',
        'bytes': True,
        'store': game_data.VAR_BATTLE_PLAYER_STAGE_EVASION,
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
    P_BATTLE_SPC: {
        'type': 'int',
        'bytes': True,
        'store': game_data.VAR_BATTLE_PLAYER_SPECIAL,
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
