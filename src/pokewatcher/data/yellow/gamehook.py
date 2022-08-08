# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Any, Final, Mapping

import logging

from attrs import define

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

###############################################################################
# Interface
###############################################################################


@define
class DataHandler(BaseDataHandler):
    def __attrs_post_init__(self):
        # player data
        self.store(P_PLAYER_ID, 'player.number', emit=True)
        self.handlers[P_PLAYER_ID] = self.on_player_id_changed
        self.store_int(P_GAME_TIME_HOURS)
        self.store_int(P_GAME_TIME_MINUTES)
        self.store_int(P_GAME_TIME_SECONDS)
        self.store_bool(P_BADGE1)
        self.store_bool(P_BADGE2)
        self.store_bool(P_BADGE3)
        self.store_bool(P_BADGE4)
        self.store_bool(P_BADGE5)
        self.store_bool(P_BADGE6)
        self.store_bool(P_BADGE7)
        self.store_bool(P_BADGE8)

        # world data
        self.emit_event(P_MAP, events.on_map_changed)

        # party lead data
        self.store_key(P_SPECIES, 'name')
        self.store_int(P_LEVEL)
        self.store_int(P_MON_ATK)
        self.store_int(P_MON_DEF)
        self.store_int(P_MON_SPD)
        self.handlers[P_MON_SPC] = self.on_special_changed

        # battle data
        self.store_int(P_GYM_LEADER)
        self.handlers[P_BATTLE_TYPE] = self.battle.on_battle_type_changed
        self.handlers[P_TRAINER_CLASS] = self.battle.on_trainer_class_changed
        self.handlers[P_TRAINER_NUMBER] = self.battle.on_trainer_number_changed
        self.handlers[P_BATTLE_ALARM] = self.battle.on_low_health_alarm_changed

        # battle lead data
        self.store_int(P_BATTLE_ATK)
        self.store_int(P_BATTLE_DEF)
        self.store_int(P_BATTLE_SPD)
        self.store_int(P_BATTLE_SPC)
        self.store_int(P_STAGE_ATK)
        self.store_int(P_STAGE_DEF)
        self.store_int(P_STAGE_SPD)
        self.store_int(P_STAGE_SPC)
        self.store_int(P_STAGE_ACC)
        self.store_int(P_STAGE_EVA)

        # other game aspects
        # self.handlers[P_AUDIO_SOUND] = self.on_audio_changed
        self.handlers[P_AUDIO_CH5] = self.on_audio_changed
        # self.handlers[P_AUDIO_CH6] = self.on_audio_changed

    def on_special_changed(self, prev: Any, value: Any, data: Mapping[str, Any]):
        value = int(value)
        data[P_MON_SPC] = value
        data[P_MON_SPATK] = value
        data[P_MON_SPDEF] = value

    def on_audio_changed(self, prev: Any, value: Any, data: Mapping[str, Any]):
        if value == SFX_SAVE_FILE:
            events.on_save_game.emit(data)
