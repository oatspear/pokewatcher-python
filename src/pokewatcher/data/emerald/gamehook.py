# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Any, Final, Mapping, Optional

import logging

import pokewatcher.data.constants as game_data
from pokewatcher.data.gamehook import DataHandler
from pokewatcher.data.structs import GameData
import pokewatcher.data.emerald.constants as emerald
from pokewatcher.logic.fsm import StateMachine

###############################################################################
# Constants
###############################################################################

logger: Final[logging.Logger] = logging.getLogger(__name__)

P_PLAYER_NAME: Final[str] = 'player.name'
P_TEAM_COUNT: Final[str] = 'player.teamCount'

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

P_BATTLE_TYPE: Final[str] = 'battle.type'
P_TRAINER_CLASS: Final[str] = 'battle.trainer.class'
P_TRAINER_NUMBER: Final[str] = 'battle.trainer.number'
P_BATTLE_OUTCOME: Final[str] = 'battle.turnInfo.battleOutcome'
P_BATTLE_BACKGROUND: Final[str] = 'battle.turnInfo.battleBackgroundTiles'
P_BATTLE_DIALOGUE: Final[str] = 'battle.turnInfo.battleDialogue'

P_STAGE_ATK: Final[str] = 'battle.yourPokemon.modStageAttack'
P_STAGE_DEF: Final[str] = 'battle.yourPokemon.modStageDefense'
P_STAGE_SPD: Final[str] = 'battle.yourPokemon.modStageSpeed'
P_STAGE_SPC: Final[str] = 'battle.yourPokemon.modStageSpecial'
P_STAGE_ACC: Final[str] = 'battle.yourPokemon.modStageAccuracy'
P_STAGE_EVA: Final[str] = 'battle.yourPokemon.modStageEvasion'

P_BATTLE_ATK: Final[str] = 'battle.yourPokemon.battleStatAttack'
P_BATTLE_DEF: Final[str] = 'battle.yourPokemon.battleStatDefense'
P_BATTLE_SPD: Final[str] = 'battle.yourPokemon.battleStatSpeed'
P_BATTLE_SPATK: Final[str] = 'battle.yourPokemon.battleStatSpecialAttack'
P_BATTLE_SPDEF: Final[str] = 'battle.yourPokemon.battleStatSpecialDefense'

P_GAME_TIME_HOURS: Final[str] = 'gameTime.hours'
P_GAME_TIME_MINUTES: Final[str] = 'gameTime.minutes'
P_GAME_TIME_SECONDS: Final[str] = 'gameTime.seconds'
P_GAME_TIME_FRAMES: Final[str] = 'gameTime.frames'

P_BADGE1: Final[str] = 'player.badges.badge1'
P_BADGE2: Final[str] = 'player.badges.badge2'
P_BADGE3: Final[str] = 'player.badges.badge3'
P_BADGE4: Final[str] = 'player.badges.badge4'
P_BADGE5: Final[str] = 'player.badges.badge5'
P_BADGE6: Final[str] = 'player.badges.badge6'
P_BADGE7: Final[str] = 'player.badges.badge7'
P_BADGE8: Final[str] = 'player.badges.badge8'

PROPERTIES: Final[Mapping[str, Mapping[str, Any]]] = {
    P_PLAYER_NAME: {
        'type': 'string',
        'label': emerald.WRAM_PLAYER_NAME,
        'store': game_data.VAR_PLAYER_NAME,
    },
    P_TEAM_COUNT: {
        'type': 'int',
        'label': emerald.WRAM_TEAM_COUNT,
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
    P_GAME_TIME_FRAMES: {
        'type': 'int',
        'bytes': True,
        'store': game_data.VAR_GAME_TIME_FRAMES,
    },
    P_SPECIES: {
        'type': 'string',
        # 'key': 'name',
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
    P_STAGE_SPC: {
        'type': 'int',
        'store': game_data.VAR_BATTLE_PLAYER_STAGE_SPECIAL,
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


def load_data_handler(
    data: GameData,
    fsm: StateMachine,
    properties: Optional[Mapping[str, Any]] = None,
) -> DataHandler:
    handler = DataHandler(data, fsm)
    properties = properties or PROPERTIES
    for prop, metadata in properties.items():
        handler.configure_property(prop, metadata)
    return handler
