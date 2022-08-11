# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Any, Final, Mapping

import logging

from attrs import define

import pokewatcher.data.constants as const
from pokewatcher.data.gamehook import BaseDataHandler
import pokewatcher.events as events

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

SFX_SAVE_FILE = 0xB6

TRAINER_CLASS_NONE = 'NOBODY'

LABELS = {
    P_PLAYER_ID: 'wPlayerID',
    P_BATTLE_TYPE: 'wIsInBattle',
    P_BATTLE_ALARM: 'wLowHealthAlarmDisabled',
}

###############################################################################
# Interface
###############################################################################


@define
class DataHandler(BaseDataHandler):
    def __attrs_post_init__(self):
        self.labels.update(LABELS)

        # player data
        self.store(P_PLAYER_ID, const.VAR_PLAYER_ID)
        self.store(P_GAME_TIME_HOURS, const.VAR_GAME_TIME_HOURS)
        self.store(P_GAME_TIME_MINUTES, const.VAR_GAME_TIME_MINUTES)
        self.store(P_GAME_TIME_SECONDS, const.VAR_GAME_TIME_SECONDS)
        self.store(P_BADGE1, const.VAR_PLAYER_BADGE1)
        self.store(P_BADGE2, const.VAR_PLAYER_BADGE2)
        self.store(P_BADGE3, const.VAR_PLAYER_BADGE3)
        self.store(P_BADGE4, const.VAR_PLAYER_BADGE4)
        self.store(P_BADGE5, const.VAR_PLAYER_BADGE5)
        self.store(P_BADGE6, const.VAR_PLAYER_BADGE6)
        self.store(P_BADGE7, const.VAR_PLAYER_BADGE7)
        self.store(P_BADGE8, const.VAR_PLAYER_BADGE8)

        # world data
        self.store(P_MAP, const.VAR_MAP)

        # party lead data
        self.store(P_SPECIES, const.VAR_PARTY_MON1_SPECIES)
        self.store(P_LEVEL, const.VAR_PARTY_MON1_LEVEL)
        self.store(P_MON_ATK, const.VAR_PARTY_MON1_ATTACK)
        self.store(P_MON_DEF, const.VAR_PARTY_MON1_DEFENSE)
        self.store(P_MON_SPD, const.VAR_PARTY_MON1_SPEED)
        self.store(P_MON_SPC, const.VAR_PARTY_MON1_SP_ATTACK)
        self.store(P_MON_SPC, const.VAR_PARTY_MON1_SP_DEFENSE)

        # battle data
        # self.store_int(P_GYM_LEADER)
        self.store(P_TRAINER_CLASS, const.VAR_BATTLE_TRAINER_CLASS)
        self.store(P_TRAINER_NUMBER, const.VAR_BATTLE_TRAINER_ID)

        # battle lead data
        self.store(P_BATTLE_ATK, const.VAR_BATTLE_PLAYER_ATTACK)
        self.store(P_BATTLE_DEF, const.VAR_BATTLE_PLAYER_DEFENSE)
        self.store(P_BATTLE_SPD, const.VAR_BATTLE_PLAYER_SPEED)
        self.store(P_BATTLE_SPC, const.VAR_BATTLE_PLAYER_SP_ATTACK)
        self.store(P_BATTLE_SPC, const.VAR_BATTLE_PLAYER_SP_DEFENSE)
        self.store(P_STAGE_ATK, const.VAR_BATTLE_PLAYER_STAGE_ATTACK)
        self.store(P_STAGE_DEF, const.VAR_BATTLE_PLAYER_STAGE_DEFENSE)
        self.store(P_STAGE_SPD, const.VAR_BATTLE_PLAYER_STAGE_SPEED)
        self.store(P_STAGE_SPC, const.VAR_BATTLE_PLAYER_STAGE_SP_ATTACK)
        self.store(P_STAGE_SPC, const.VAR_BATTLE_PLAYER_STAGE_SP_DEFENSE)
        self.store(P_STAGE_ACC, const.VAR_BATTLE_PLAYER_STAGE_ACCURACY)
        self.store(P_STAGE_EVA, const.VAR_BATTLE_PLAYER_STAGE_EVASION)

        # other game aspects
        # self.handlers[P_AUDIO_SOUND] = self.on_audio_changed
        self.handlers[P_AUDIO_CH5] = self.on_audio_changed
        # self.handlers[P_AUDIO_CH6] = self.on_audio_changed

    def on_audio_changed(self, prev: Any, value: Any, mapper: Mapping[str, Any]):
        if self.state != STATE_OUT_OF_BATTLE:
            return
        if value == SFX_SAVE_FILE:
            events.on_save_game.emit()
