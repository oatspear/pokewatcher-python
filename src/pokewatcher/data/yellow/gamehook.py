# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Any, Final, Optional, Mapping

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

P_PLAYER_ID = 'player.playerId'
P_PLAYER_NAME = 'player.name'
P_JOYPAD_IGNORE = 'player.joypadIgnore'

P_SPECIES = 'player.team.0.species'
P_LEVEL = 'player.team.0.level'
P_MOVE1 = 'player.team.0.move1'
P_MOVE2 = 'player.team.0.move2'
P_MOVE3 = 'player.team.0.move3'
P_MOVE4 = 'player.team.0.move4'
P_MON_ATK = 'player.team.0.attack'
P_MON_DEF = 'player.team.0.defense'
P_MON_SPD = 'player.team.0.speed'
P_MON_SPC = 'player.team.0.special'
P_MON_SPATK = 'player.team.0.specialAttack'
P_MON_SPDEF = 'player.team.0.specialDefense'

P_MAP = 'overworld.map'
P_X_COORD = 'overworld.x'
P_Y_COORD = 'overworld.y'

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
P_GAME_TIME_FRAMES = 'gameTime.frames'
P_COUNT_GAME_TIME = 'events.overworldFlags.countPlayTime'

P_BADGE1 = 'player.badges.badge1'
P_BADGE2 = 'player.badges.badge2'
P_BADGE3 = 'player.badges.badge3'
P_BADGE4 = 'player.badges.badge4'
P_BADGE5 = 'player.badges.badge5'
P_BADGE6 = 'player.badges.badge6'
P_BADGE7 = 'player.badges.badge7'
P_BADGE8 = 'player.badges.badge8'

P_CUR_MENU_ITEM = 'screen.menu.currentItem'

PROPERTIES: Final[Mapping[str, Mapping[str, Any]]] = {
    P_PLAYER_ID: {
        'type': 'int',
        'bytes': True,
        'label': yellow.WRAM_PLAYER_ID,
        'store': game_data.VAR_PLAYER_ID,
    },
    P_PLAYER_NAME: {
        'type': 'string',
        'label': yellow.WRAM_PLAYER_NAME,
        'store': game_data.VAR_PLAYER_NAME,
    },
    P_JOYPAD_IGNORE: {
        'type': 'int',
        'bytes': True,
        'label': yellow.WRAM_JOY_IGNORE,
    },
    P_CUR_MENU_ITEM: {
        'type': 'int',
        'bytes': True,
        'label': yellow.WRAM_CURRENT_MENU_ITEM,
    },
    P_GAME_TIME_HOURS: {
        'type': 'int',
        'bytes': True,
        'store': game_data.VAR_GAME_TIME_HOURS,
        'label': yellow.WRAM_PLAY_TIME_HOURS,
    },
    P_GAME_TIME_MINUTES: {
        'type': 'int',
        'bytes': True,
        'store': game_data.VAR_GAME_TIME_MINUTES,
        'label': yellow.WRAM_PLAY_TIME_MINUTES,
    },
    P_GAME_TIME_SECONDS: {
        'type': 'int',
        'bytes': True,
        'store': game_data.VAR_GAME_TIME_SECONDS,
        'label': yellow.WRAM_PLAY_TIME_SECONDS,
    },
    P_GAME_TIME_FRAMES: {
        'type': 'int',
        'bytes': True,
        'store': game_data.VAR_GAME_TIME_FRAMES,
        'label': yellow.WRAM_PLAY_TIME_FRAMES,
    },
    P_COUNT_GAME_TIME: {
        'type': 'bool',
        'label': yellow.WRAM_COUNT_PLAY_TIME,
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
    P_MAP: {
        'type': 'string',
        'store': game_data.VAR_MAP,
        'processors': [
            ['prefix', 'Kanto/'],
        ],
        'label': yellow.WRAM_CUR_MAP,
    },
    P_X_COORD: {
        'type': 'int',
        'label': yellow.WRAM_X_COORD,
    },
    P_Y_COORD: {
        'type': 'int',
        'label': yellow.WRAM_Y_COORD,
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
        'type': 'bool',
        'bytes': True,
        'label': yellow.WRAM_LOW_HEALTH_ALARM,
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
