# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

################################################################################
# Imports
################################################################################

from typing import Any, Dict, Tuple

from collections import Counter, namedtuple
import json
import logging
import os
from pathlib import Path
import requests
import shutil
import socket
import sys
import time
from types import SimpleNamespace
import warnings

from signalrcore.hub_connection_builder import HubConnectionBuilder

################################################################################
# Constants
################################################################################

OATS = True

if OATS:
    SRC_DIR = Path(r'C:\RetroArch-Win64\saves')
    DST_DIR = Path(r'C:\Users\Andre\Games\ScottsThoughts')
else:
    SRC_DIR = Path(r'F:\Desktop\filming files\saves')
    DST_DIR = Path(r'F:\Desktop\filming files\backup saves')

GAMEHOOK_SIGNALR = 'http://localhost:8085/updates'
GAMEHOOK_REQUESTS = 'http://localhost:8085/mapper'

RETROARCH_HOST = ('127.0.0.1', 55355)
TIME_SERVER = ('localhost', 16834)

DEFAULT_LOOP_ITERATIONS = 5
DEFAULT_SLEEP_DELAY = 3.0  # seconds

DEFAULT_BACKUP_NAME_FORMAT = '{rom} - lvl{level}-{time}-{location}.srm'

CSV_FILE = DST_DIR / 'splits.csv'

################################################################################
# Main Function
################################################################################


def main(argv) -> int:
    try:
        watcher = GameWatcher()

        try:
            watcher.setup()
        except DataRequestError as err:
            print(str(err))
            return 1

        try:
            watcher.main_loop()
        finally:
            watcher.cleanup()

    except KeyboardInterrupt:
        print('[User] interrupted')

    print('Exiting.')
    return 0


################################################################################
# Top-level Game Watcher
################################################################################


class GameWatcher:
    def __init__(self):
        self.gamehook = None
        self.backup_agent = None
        self.data_handler = None
        self.time_splitter = None

    def setup(self):
        rom = request_retroarch_status()
        print('[Watcher] got ROM:', rom)
        self.backup_agent = SaveFileBackupAgent(rom)

        version, data = request_gamehook_data()
        print('[Watcher] got game version:', version)
        self._build_data_handler(rom, version, data)

        self.gamehook = GameHookBridge(
            on_connect=lambda: print('[GameHook] stream connected'),
            on_disconnect=lambda: print('[GameHook] stream disconnected'),
            on_error=lambda err: print('[GameHook] error:', err),
        )

        self.time_splitter = BattleTimeSplitter(version)

        # connect everything
        self._connect_event_handlers()

    def main_loop(self):
        self.gamehook.connect()
        while True:
            self.backup_agent.watch_once()
            self.time_splitter.store_updates()
            time.sleep(DEFAULT_SLEEP_DELAY)

    def cleanup(self):
        if self.gamehook is not None:
            self.gamehook.disconnect()
            self.gamehook = None
        self.backup_agent = None
        self.data_handler = None

    def _build_data_handler(self, rom, version, data):
        game_string = version.lower()
        if 'yellow' in game_string:
            self.data_handler = YellowDataHandler(rom, version, data)
        elif 'crystal' in game_string:
            self.data_handler = CrystalDataHandler(rom, version, data)
        else:
            raise ValueError(f'[Watcher] unknown game version: {version}')

    def _connect_event_handlers(self):
        # connect in-game save events to save file backup agent
        self.data_handler.events.on_save = self.backup_agent.save
        # connect GameHook property events to data handler callbacks
        self.gamehook.on_change = self.data_handler.on_property_changed
        # connect in-game battle events
        self.data_handler.events.on_battle_started = self.time_splitter.on_battle_started
        self.data_handler.events.on_battle_ended = self.time_splitter.on_battle_ended


################################################################################
# Data Handling
################################################################################


class PokemonDataHandler:
    def __init__(self, rom, version, data):
        self.data = {
            'rom': rom,
            'version': version,
            'time': '00:00:00.000',
        }
        self.events = GameEvents()
        self.battle = self._new_battle_monitor()
        self.battle.on_battle_started = self._emit_battle_started
        self.battle.on_battle_ended = self._emit_battle_ended
        self._handlers = {}
        self._set_property_handlers()
        for prop in data:
            handle = self._handlers.get(prop['path'], noop)
            handle(prop['value'])

    def __getitem__(self, key):
        return self.data[key]

    def on_property_changed(self, args):
        prop, value, _bytes, _frozen = args
        handle = self._handlers.get(prop, noop)
        handle(value)

    def _simple_setter(self, attr, quiet=True):
        def handle(value):
            if not quiet:
                print(f'[Data] new {attr}:', value)
            self.data[attr] = value
        return handle

    def _key_setter(self, attr, key, quiet=True):
        def handle(value):
            if not quiet:
                print(f'[Data] new {attr}:', value)
            self.data[attr] = value[key] if value is not None else None
        return handle

    def _string_setter(self, attr, quiet=True):
        def handle(value):
            if not quiet:
                print(f'[Data] new {attr}:', value)
            self.data[attr] = str(value)
        return handle

    def _int_setter(self, attr, quiet=True):
        def handle(value):
            if not quiet:
                print(f'[Data] new {attr}:', value)
            self.data[attr] = int(value)
        return handle

    def _bool_setter(self, attr, quiet=True):
        def handle(value):
            if not quiet:
                print(f'[Data] new {attr}:', value)
            self.data[attr] = bool(value)
        return handle

    def _new_battle_monitor(self):
        raise NotImplementedError('_new_battle_monitor')

    def _emit_battle_started(self):
        self.events.on_battle_started(self.battle, data=self)

    def _emit_battle_ended(self):
        self.events.on_battle_ended(self.battle, data=self)

    @property
    def slot1_attack(self):
        return self.data.get('attack', 0)

    @property
    def slot1_defense(self):
        return self.data.get('defense', 0)

    @property
    def slot1_sp_attack(self):
        return self.data.get('specialAttack', 0)

    @property
    def slot1_sp_defense(self):
        return self.data.get('specialDefense', 0)

    @property
    def slot1_speed(self):
        return self.data.get('speed', 0)


class YellowDataHandler(PokemonDataHandler):
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

    P_LOCATION = 'overworld.map'
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

    def _new_battle_monitor(self):
        return YellowBattleMonitor()

    def _set_property_handlers(self):
        self._handlers[self.P_SPECIES] = self._key_setter('species', 'name', quiet=False)
        self._handlers[self.P_LEVEL] = self._int_setter('level', quiet=False)
        self._handlers[self.P_MOVE1] = self._string_setter('move1')
        self._handlers[self.P_MOVE2] = self._string_setter('move2')
        self._handlers[self.P_MOVE3] = self._string_setter('move3')
        self._handlers[self.P_MOVE4] = self._string_setter('move4')
        self._handlers[self.P_MON_ATK] = self._int_setter('attack')
        self._handlers[self.P_MON_DEF] = self._int_setter('defense')
        self._handlers[self.P_MON_SPD] = self._int_setter('speed')
        self._handlers[self.P_MON_SPC] = self._set_special
        self._handlers[self.P_LOCATION] = self._string_setter('location', quiet=False)

        self._handlers[self.P_BATTLE_TYPE] = self.battle.on_battle_type_changed
        self._handlers[self.P_TRAINER_CLASS] = self.battle.on_trainer_class_changed
        self._handlers[self.P_TRAINER_NUMBER] = self.battle.on_trainer_number_changed
        self._handlers[self.P_GYM_LEADER] = self._int_setter('gym_leader')
        self._handlers[self.P_BATTLE_ALARM] = self.battle.on_low_health_alarm_changed

        self._handlers[self.P_STAGE_ATK] = self.battle.on_stage_attack_changed
        self._handlers[self.P_STAGE_DEF] = self.battle.on_stage_defense_changed
        self._handlers[self.P_STAGE_SPD] = self.battle.on_stage_speed_changed
        self._handlers[self.P_STAGE_SPC] = self.battle.on_stage_special_changed
        self._handlers[self.P_STAGE_ACC] = self.battle.on_stage_accuracy_changed
        self._handlers[self.P_STAGE_EVA] = self.battle.on_stage_evasion_changed

        self._handlers[self.P_BATTLE_ATK] = self.battle.on_battle_attack_changed
        self._handlers[self.P_BATTLE_DEF] = self.battle.on_battle_defense_changed
        self._handlers[self.P_BATTLE_SPD] = self.battle.on_battle_speed_changed
        self._handlers[self.P_BATTLE_SPC] = self.battle.on_battle_special_changed

        self._handlers[self.P_BADGE1] = self._bool_setter('badge1')
        self._handlers[self.P_BADGE2] = self._bool_setter('badge2')
        self._handlers[self.P_BADGE3] = self._bool_setter('badge3')
        self._handlers[self.P_BADGE4] = self._bool_setter('badge4')
        self._handlers[self.P_BADGE5] = self._bool_setter('badge5')
        self._handlers[self.P_BADGE6] = self._bool_setter('badge6')
        self._handlers[self.P_BADGE7] = self._bool_setter('badge7')
        self._handlers[self.P_BADGE8] = self._bool_setter('badge8')

        self._handlers[self.P_GAME_TIME_HOURS] = self._int_setter('game_time_h')
        self._handlers[self.P_GAME_TIME_MINUTES] = self._int_setter('game_time_m')
        self._handlers[self.P_GAME_TIME_SECONDS] = self._int_setter('game_time_s')

        # self._handlers[self.P_AUDIO_SOUND] = self._handle_sound_effects
        self._handlers[self.P_AUDIO_CH5] = self._handle_sound_effects
        # self._handlers[self.P_AUDIO_CH6] = self._handle_sound_effects

    SFX_SAVE_FILE = 0xB6

    def _handle_sound_effects(self, value):
        # self.data['sound'] = int(value)
        if value == self.SFX_SAVE_FILE:
            print('[Events] saved game')
            self.events.on_save(self.data)
        # self.battle.on_music_changed(value)

    def _set_special(self, value):
        x = int(value)
        self.data['specialAttack'] = x
        self.data['specialDefense'] = x

    @property
    def slot1_attack(self):
        mult = 1.125 if self.data.get('badge1') else 1
        return int(self.data.get('attack', 0) * mult)

    @property
    def slot1_defense(self):
        mult = 1.125 if self.data.get('badge3') else 1
        return int(self.data.get('defense', 0) * mult)

    @property
    def slot1_sp_attack(self):
        mult = 1.125 if self.data.get('badge7') else 1
        return int(self.data.get('specialAttack', 0) * mult)

    @property
    def slot1_sp_defense(self):
        mult = 1.125 if self.data.get('badge7') else 1
        return int(self.data.get('specialDefense', 0) * mult)

    @property
    def slot1_speed(self):
        mult = 1.125 if self.data.get('badge6') else 1
        return int(self.data.get('speed', 0) * mult)


class CrystalDataHandler(PokemonDataHandler):
    P_SPECIES = 'team[0].species'
    P_LEVEL = 'team[0].level'
    P_MOVE1 = 'team[0].move1'
    P_MOVE2 = 'team[0].move2'
    P_MOVE3 = 'team[0].move3'
    P_MOVE4 = 'team[0].move4'
    P_MON_ATK = 'team[0].summaryAtk'
    P_MON_DEF = 'team[0].summaryDef'
    P_MON_SPD = 'team[0].summarySpd'
    P_MON_SPATK = 'team[0].summarySpcA'
    P_MON_SPDEF = 'team[0].summarySpcD'

    P_MAP_GROUP = 'overworld.mapGroup'
    P_MAP_NUMBER = 'overworld.mapNumber'
    P_AUDIO_SOUND = 'audio.currentSound'
    P_AUDIO_MUSIC = 'audio.musicID'

    P_BATTLE_MODE = 'battle.mode'
    P_BATTLE_TYPE = 'battle.type'
    P_BATTLE_RESULT = 'battle.result'
    P_TRAINER_CLASS = 'battle.trainer.class'
    P_TRAINER_ID = 'battle.trainer.id'
    
    P_STAGE_ATK = 'battle.yourPokemon.modStageAtk'
    P_STAGE_DEF = 'battle.yourPokemon.modStageDef'
    P_STAGE_SPD = 'battle.yourPokemon.modStageSpd'
    P_STAGE_SPATK = 'battle.yourPokemon.modStageSpcA'
    P_STAGE_SPDEF = 'battle.yourPokemon.modStageSpcD'
    P_STAGE_ACC = 'battle.yourPokemon.modStageAcc'
    P_STAGE_EVA = 'battle.yourPokemon.modStageEva'

    P_BATTLE_ATK = 'battle.yourPokemon.battleStatAtk'
    P_BATTLE_DEF = 'battle.yourPokemon.battleStatDef'
    P_BATTLE_SPD = 'battle.yourPokemon.battleStatSpd'
    P_BATTLE_SPATK = 'battle.yourPokemon.battleStatSpcA'
    P_BATTLE_SPDEF = 'battle.yourPokemon.battleStatSpcD'

    P_TEXT_PROMPT = 'screen.text.prompt'
    P_GAME_TIME_HOURS = 'gameTime.hours'
    P_GAME_TIME_MINUTES = 'gameTime.minutes'
    P_GAME_TIME_SECONDS = 'gameTime.seconds'

    P_BADGE1 = 'player.badges.zephyrBadge'
    P_BADGE2 = 'player.badges.hiveBadge'
    P_BADGE3 = 'player.badges.plainBadge'
    P_BADGE4 = 'player.badges.fogBadge'
    P_BADGE5 = 'player.badges.stormBadge'
    P_BADGE6 = 'player.badges.mineralBadge'
    P_BADGE7 = 'player.badges.glacierBadge'
    P_BADGE8 = 'player.badges.risingBadge'

    SFX_SAVE_FILE = 37

    def _new_battle_monitor(self):
        return CrystalBattleMonitor()

    def _set_property_handlers(self):
        self._handlers[self.P_SPECIES] = self._key_setter('species', 'name', quiet=False)
        self._handlers[self.P_LEVEL] = self._int_setter('level', quiet=False)
        self._handlers[self.P_MOVE1] = self._string_setter('move1')
        self._handlers[self.P_MOVE2] = self._string_setter('move2')
        self._handlers[self.P_MOVE3] = self._string_setter('move3')
        self._handlers[self.P_MOVE4] = self._string_setter('move4')
        self._handlers[self.P_MON_ATK] = self._int_setter('attack')
        self._handlers[self.P_MON_DEF] = self._int_setter('defense')
        self._handlers[self.P_MON_SPD] = self._int_setter('speed')
        self._handlers[self.P_MON_SPATK] = self._int_setter('specialAttack')
        self._handlers[self.P_MON_SPDEF] = self._int_setter('specialDefense')
        self._handlers[self.P_MAP_GROUP] = self._set_map_group_and_location
        self._handlers[self.P_MAP_NUMBER] = self._int_setter('map_number')

        self._handlers[self.P_BATTLE_MODE] = self.battle.on_battle_mode_changed
        self._handlers[self.P_BATTLE_TYPE] = self.battle.on_battle_type_changed
        self._handlers[self.P_BATTLE_RESULT] = self.battle.on_battle_result_changed
        self._handlers[self.P_TRAINER_CLASS] = self.battle.on_trainer_class_changed
        self._handlers[self.P_TRAINER_ID] = self.battle.on_trainer_id_changed

        self._handlers[self.P_STAGE_ATK] = self.battle.on_stage_attack_changed
        self._handlers[self.P_STAGE_DEF] = self.battle.on_stage_defense_changed
        self._handlers[self.P_STAGE_SPD] = self.battle.on_stage_speed_changed
        self._handlers[self.P_STAGE_SPATK] = self.battle.on_stage_sp_attack_changed
        self._handlers[self.P_STAGE_SPDEF] = self.battle.on_stage_sp_defense_changed
        self._handlers[self.P_STAGE_ACC] = self.battle.on_stage_accuracy_changed
        self._handlers[self.P_STAGE_EVA] = self.battle.on_stage_evasion_changed

        self._handlers[self.P_BATTLE_ATK] = self.battle.on_battle_attack_changed
        self._handlers[self.P_BATTLE_DEF] = self.battle.on_battle_defense_changed
        self._handlers[self.P_BATTLE_SPD] = self.battle.on_battle_speed_changed
        self._handlers[self.P_BATTLE_SPATK] = self.battle.on_battle_sp_attack_changed
        self._handlers[self.P_BATTLE_SPDEF] = self.battle.on_battle_sp_defense_changed

        self._handlers[self.P_BADGE1] = self._bool_setter('badge1')
        self._handlers[self.P_BADGE2] = self._bool_setter('badge2')
        self._handlers[self.P_BADGE3] = self._bool_setter('badge3')
        self._handlers[self.P_BADGE4] = self._bool_setter('badge4')
        self._handlers[self.P_BADGE5] = self._bool_setter('badge5')
        self._handlers[self.P_BADGE6] = self._bool_setter('badge6')
        self._handlers[self.P_BADGE7] = self._bool_setter('badge7')
        self._handlers[self.P_BADGE8] = self._bool_setter('badge8')

        self._handlers[self.P_GAME_TIME_HOURS] = self._int_setter('game_time_h')
        self._handlers[self.P_GAME_TIME_MINUTES] = self._int_setter('game_time_m')
        self._handlers[self.P_GAME_TIME_SECONDS] = self._int_setter('game_time_s')

        self._handlers[self.P_AUDIO_SOUND] = self._handle_sound_effects
        self._handlers[self.P_AUDIO_MUSIC] = self._handle_music
        self._handlers[self.P_TEXT_PROMPT] = self._handle_text_prompt

    def _set_map_group_and_location(self, value):
        self.data['map_group'] = str(value)
        self.data['location'] = str(value)
        print('[Data] new location:', value)

    def _handle_sound_effects(self, value):
        # self.data['sound'] = int(value)
        if value == self.SFX_SAVE_FILE:
            print('[Events] saved game')
            self.events.on_save(self.data)

    def _handle_music(self, value):
        # self.data['music'] = int(value)
        self.battle.on_music_changed(value)

    def _handle_text_prompt(self, value):
        if value:
            self.battle.on_text_prompt()

    @property
    def slot1_attack(self):
        mult = 1.125 if self.data.get('badge1') else 1
        return int(self.data.get('attack', 0) * mult)

    @property
    def slot1_defense(self):
        mult = 1.125 if self.data.get('badge6') else 1
        return int(self.data.get('defense', 0) * mult)

    @property
    def slot1_sp_attack(self):
        mult = 1.125 if self.data.get('badge7') else 1
        return int(self.data.get('specialAttack', 0) * mult)

    @property
    def slot1_sp_defense(self):
        mult = 1.125 if self.data.get('badge7') else 1
        return int(self.data.get('specialDefense', 0) * mult)

    @property
    def slot1_speed(self):
        mult = 1.125 if self.data.get('badge3') else 1
        return int(self.data.get('speed', 0) * mult)


################################################################################
# Battle Monitor
################################################################################


def MonStats():
    return SimpleNamespace(
        attack=1,
        defense=1,
        speed=1,
        sp_attack=1,
        sp_defense=1,
    )


def StatStages():
    return SimpleNamespace(
        attack=0,
        defense=0,
        speed=0,
        sp_attack=0,
        sp_defense=0,
        accuracy=0,
        evasion=0,
    )


def BattleMon():
    return SimpleNamespace(
        stats=MonStats(),
        stages=StatStages(),
    )


class YellowBattleMonitor:
    # "battle.lowHealthAlarm" [wLowHealthAlarmDisabled]
    #   set to 0 at the start of every battle (InitBattleVariables)
    #   set to 1 on victory against wild mon or trainer (EndLowHealthAlarm)
    # "battle.type" [wIsInBattle]
    #   set to 0 at the end of battle (EndOfBattle)
    #   set to 2 at the start of a trainer battle (InitBattleCommon)
    #   set to 1 at the start of a wild battle (InitWildBattle)
    #   set to 0 on blackout (ResetStatusAndHalveMoneyOnBlackout)
    #   set to 0xFF if all mons faint in overworld (AllPokemonFainted)
    #   set to 0 on Fly or map warp (HandleFlyWarpOrDungeonWarp)

    BATTLE_TYPE_NONE = 'None'
    BATTLE_TYPE_WILD = 'Wild'
    BATTLE_TYPE_TRAINER = 'Trainer'
    BATTLE_TYPE_LOST = 'Lost Battle'

    ALARM_ENABLED = 'Enabled'
    ALARM_DISABLED = 'Disabled'

    STATE_OUT_OF_BATTLE = 0
    STATE_IN_BATTLE = 1
    STATE_PLAYER_WON = 2

    TRAINER_CLASS_NONE = 'NOBODY'

    def __init__(self):
        self.on_battle_started = noop
        self.on_battle_ended = noop
        self._reset()

    def on_battle_type_changed(self, value):
        self.battle_type = value

        if value == self.BATTLE_TYPE_NONE:
            if self.state == self.STATE_IN_BATTLE:
                self._run_away()
            elif self.state == self.STATE_PLAYER_WON:
                self._reset()

        elif value == self.BATTLE_TYPE_WILD:
            self.state = self.STATE_IN_BATTLE
            self.trainer_class = None
            self.on_battle_started()

        elif value == self.BATTLE_TYPE_TRAINER:
            self.state = self.STATE_IN_BATTLE
            self.on_battle_started()

        elif value == self.BATTLE_TYPE_LOST:
            self._white_out()

        else:
            print('[Battle] unknown battle type value:', value)

    def on_trainer_class_changed(self, value):
        if value == self.TRAINER_CLASS_NONE:
            self.trainer_class = None
        else:
            self.trainer_class = value

    def on_trainer_number_changed(self, value):
        self.trainer_id = value

    def on_low_health_alarm_changed(self, value):
        if value == self.ALARM_DISABLED:
            if self.state != self.STATE_IN_BATTLE:
                print("[Battle] player won but monitor is not in the correct state")
                print("[Battle] state:", self.state)
            self._win_battle()

        elif value == self.ALARM_ENABLED:
            # game reset or battle starting after a previous victory
            # print("[Battle] game reset or battle starting")
            # print("[Battle] state:", self.state)
            pass

    def on_stage_attack_changed(self, value):
        self.battle_mon.stages.attack = value

    def on_stage_defense_changed(self, value):
        self.battle_mon.stages.defense = value

    def on_stage_speed_changed(self, value):
        self.battle_mon.stages.speed = value

    def on_stage_special_changed(self, value):
        self.battle_mon.stages.sp_attack = value
        self.battle_mon.stages.sp_defense = value

    def on_stage_accuracy_changed(self, value):
        self.battle_mon.stages.accuracy = value

    def on_stage_evasion_changed(self, value):
        self.battle_mon.stages.evasion = value

    def on_battle_attack_changed(self, value):
        self.battle_mon.stats.attack = value

    def on_battle_defense_changed(self, value):
        self.battle_mon.stats.defense = value

    def on_battle_speed_changed(self, value):
        self.battle_mon.stats.speed = value

    def on_battle_special_changed(self, value):
        self.battle_mon.stats.sp_attack = value
        self.battle_mon.stats.sp_defense = value

    def _reset(self):
        self.state = self.STATE_OUT_OF_BATTLE
        self.battle_type = self.BATTLE_TYPE_NONE
        self.trainer_class = None
        self.trainer_id = None
        self.enemy_species = None
        # battle_result:
        #   True: Won
        #   False: Lost
        #   None: Draw/Run/Other
        self.battle_result = None
        self.battle_mon = BattleMon()

    def _run_away(self):
        self.state = self.STATE_OUT_OF_BATTLE
        self.battle_result = None
        self.on_battle_ended()

    def _white_out(self):
        self.state = self.STATE_OUT_OF_BATTLE
        self.battle_result = False
        self.on_battle_ended()

    def _win_battle(self):
        self.state = self.STATE_PLAYER_WON
        self.battle_result = True
        self.on_battle_ended()


# BattleIntro:
#   farcall PlayBattleMusic
#       read [wBattleType]
#       read [wOtherTrainerClass]
#       read [wOtherTrainerID]
#   farcall ClearBattleRAM
#       write [wBattleResult]
#   call InitEnemy
#       read [wOtherTrainerClass]
#       write [wTrainerClass]
#       write [wBattleMode]
#   call BattleStartMessage
# ExitBattle:
#   call CleanUpBattleRAM
#       write [wBattleType]
#       write [wBattleMode]
#       write [wOtherTrainerClass]
# WinTrainerBattle:
#   write [wBattleEnded]
#   call PlayVictoryMusic

# state machine:
# overworld -> music -> prompt -> music -> prompt -> overworld

class CrystalBattleMonitor:
    MUSIC_KANTO_GYM_LEADER_BATTLE = 0x0600
    MUSIC_KANTO_TRAINER_BATTLE = 0x0700
    MUSIC_KANTO_WILD_BATTLE = 0x0800
    MUSIC_TRAINER_VICTORY = 0x1700
    MUSIC_WILD_VICTORY = 0x1800
    MUSIC_GYM_VICTORY = 0x1900
    MUSIC_JOHTO_WILD_BATTLE = 0x2900
    MUSIC_JOHTO_TRAINER_BATTLE = 0x2A00
    MUSIC_JOHTO_GYM_LEADER_BATTLE = 0x2E00
    MUSIC_CHAMPION_BATTLE = 0x2F00
    MUSIC_RIVAL_BATTLE = 0x3000
    MUSIC_JOHTO_WILD_BATTLE_NIGHT = 0x4A00

    MUSIC_BATTLE_ANY = (
        MUSIC_KANTO_GYM_LEADER_BATTLE,
        MUSIC_KANTO_TRAINER_BATTLE,
        MUSIC_KANTO_WILD_BATTLE,
        MUSIC_JOHTO_WILD_BATTLE,
        MUSIC_JOHTO_TRAINER_BATTLE,
        MUSIC_JOHTO_GYM_LEADER_BATTLE,
        MUSIC_CHAMPION_BATTLE,
        MUSIC_RIVAL_BATTLE,
        MUSIC_JOHTO_WILD_BATTLE_NIGHT,
    )
    MUSIC_VICTORY_ANY = (
        MUSIC_TRAINER_VICTORY,
        MUSIC_WILD_VICTORY,
        MUSIC_GYM_VICTORY,
    )

    BATTLE_TYPE_NORMAL = 'NORMAL'
    BATTLE_TYPE_CANLOSE = 'CANLOSE'

    BATTLE_MODE_NONE = 'NONE'
    BATTLE_MODE_WILD = 'WILD'
    BATTLE_MODE_TRAINER = 'TRAINER'

    BATTLE_RESULT_WIN = 'WIN'
    BATTLE_RESULT_LOSE = 'LOSE'
    BATTLE_RESULT_DRAW = 'DRAW'

    STATE_OUT_OF_BATTLE = 0
    STATE_ENTERED_BATTLE = 1
    STATE_BATTLE_STARTED = 2
    STATE_VICTORY_SEQUENCE = 3
    STATE_PLAYER_WON = 4

    TRAINER_CLASS_NONE = 'NOBODY'

    def __init__(self):
        self.on_battle_started = noop
        self.on_battle_ended = noop
        self._reset()

    def on_battle_mode_changed(self, value):
        if self.battle_type == self.BATTLE_TYPE_CANLOSE:
            if value == self.BATTLE_MODE_NONE:
                self.battle_mode = value
            elif value == self.BATTLE_MODE_TRAINER:
                self.battle_mode = value
            else:
                return
        else:
            self.battle_mode = value

        if self.state == self.STATE_OUT_OF_BATTLE:
            # alternative enter event besides the music update
            if value != self.BATTLE_MODE_NONE:
                self.state = self.STATE_ENTERED_BATTLE
                self.battle_result = None

        elif self.state == self.STATE_ENTERED_BATTLE:
            if value == self.BATTLE_MODE_NONE:
                self._end_battle()

        elif self.state == self.STATE_BATTLE_STARTED:
            if value == self.BATTLE_MODE_NONE:
                self._end_battle()

        elif self.state == self.STATE_PLAYER_WON:
            if value == self.BATTLE_MODE_NONE:
                print('[Battle] back to overworld')
                self.state = self.STATE_OUT_OF_BATTLE

    def on_battle_type_changed(self, value):
        self.battle_type = value

    def on_battle_result_changed(self, value):
        if value == self.BATTLE_RESULT_WIN:
            self.battle_result = True
        elif value == self.BATTLE_RESULT_LOSE:
            self.battle_result = False
        else:
            self.battle_result = None

    def on_trainer_class_changed(self, value):
        if value == self.TRAINER_CLASS_NONE:
            self.trainer_class = None
        else:
            self.trainer_class = value

    def on_trainer_id_changed(self, value):
        self.trainer_id = value

    def on_music_changed(self, value):
        # print('music changed:', value)
        # if self.state == self.STATE_OUT_OF_BATTLE:
        #     if value in self.MUSIC_BATTLE_ANY:
        #         print('entered via music', value)
        #         self.state = self.STATE_ENTERED_BATTLE
        #         self.battle_mode = self.BATTLE_MODE_NONE
        #         self.battle_result = None

        #el
        if self.state == self.STATE_BATTLE_STARTED:
            if value in self.MUSIC_VICTORY_ANY:
                self.state = self.STATE_VICTORY_SEQUENCE
                self.battle_result = True

    def on_text_prompt(self):
        if self.state == self.STATE_ENTERED_BATTLE:
            self.state = self.STATE_BATTLE_STARTED
            self.on_battle_started()

        elif self.state == self.STATE_VICTORY_SEQUENCE:
            self.state = self.STATE_PLAYER_WON
            self.on_battle_ended()

    def on_stage_attack_changed(self, value):
        self.battle_mon.stages.attack = value

    def on_stage_defense_changed(self, value):
        self.battle_mon.stages.defense = value

    def on_stage_speed_changed(self, value):
        self.battle_mon.stages.speed = value

    def on_stage_sp_attack_changed(self, value):
        self.battle_mon.stages.sp_attack = value

    def on_stage_sp_defense_changed(self, value):
        self.battle_mon.stages.sp_defense = value

    def on_stage_accuracy_changed(self, value):
        self.battle_mon.stages.accuracy = value

    def on_stage_evasion_changed(self, value):
        self.battle_mon.stages.evasion = value

    def on_battle_attack_changed(self, value):
        self.battle_mon.stats.attack = value

    def on_battle_defense_changed(self, value):
        self.battle_mon.stats.defense = value

    def on_battle_speed_changed(self, value):
        self.battle_mon.stats.speed = value

    def on_battle_sp_attack_changed(self, value):
        self.battle_mon.stats.sp_attack = value

    def on_battle_sp_defense_changed(self, value):
        self.battle_mon.stats.sp_defense = value

    def _reset(self):
        self.state = self.STATE_OUT_OF_BATTLE
        self.battle_mode = self.BATTLE_MODE_NONE
        self.battle_type = None
        self.trainer_class = None
        self.trainer_id = None
        self.enemy_species = None
        # battle_result:
        #   True: Won
        #   False: Lost
        #   None: Draw/Run/Other
        self.battle_result = None
        self.battle_mon = BattleMon()

    def _end_battle(self):
        self.state = self.STATE_OUT_OF_BATTLE
        self.on_battle_ended()
        print('[Battle] back to overworld')


################################################################################
# Game Events
################################################################################


class GameEvents:
    def __init__(self):
        self.on_save = noop
        self.on_battle_started = noop
        self.on_battle_ended = noop


################################################################################
# Event Observers
################################################################################


class BattleTimeSplitter:
    BOSSES = {
        'Pokemon Yellow': [
            # CLASS,    ID,  NAME
            ('RIVAL1',   2, 'RIVAL'),
            ('BROCK',    1, 'BROCK'),
            ('MISTY',    1, 'MISTY'),
            ('LT.SURGE', 1, 'LT.SURGE'),
            ('ERIKA',    1, 'ERIKA'),
            ('KOGA',     1, 'KOGA'),
            ('BLAINE',   1, 'BLAINE'),
            ('SABRINA',  1, 'SABRINA'),
            ('GIOVANNI', 3, 'GIOVANNI'),
            ('LORELEI',  1, 'LORELEI'),
            ('BRUNO',    1, 'BRUNO'),
            ('AGATHA',   1, 'AGATHA'),
            ('LANCE',    1, 'LANCE'),
            ('RIVAL2',   5, 'RIVAL (SILPH CO.)'),
            ('RIVAL2',   6, 'RIVAL (SILPH CO.)'),
            ('RIVAL2',   7, 'RIVAL (SILPH CO.)'),
            ('RIVAL2',   8, 'RIVAL (FINAL)'),
            ('RIVAL2',   9, 'RIVAL (FINAL)'),
            ('RIVAL2',  10, 'RIVAL (FINAL)'),
            ('RIVAL3',   1, 'CHAMPION'),
            ('RIVAL3',   2, 'CHAMPION'),
            ('RIVAL3',   3, 'CHAMPION'),
        ],
        'Pokemon Crystal': [
            # CLASS,    ID,  NAME
            # ('YOUNGSTER', 1, 'YOUNGSTER JOEY'),
            # ('YOUNGSTER', 2, 'YOUNGSTER MIKEY'),
            # ('RIVAL1',   1, 'RIVAL'),
            # ('RIVAL1',   2, 'RIVAL'),
            # ('RIVAL1',   3, 'RIVAL'),
            ('FALKNER',   1, 'FALKNER'),
            ('WHITNEY',   1, 'WHITNEY'),
            ('BUGSY',     1, 'BUGSY'),
            ('MORTY',     1, 'MORTY'),
            ('PRYCE',     1, 'PRYCE'),
            ('JASMINE',   1, 'JASMINE'),
            ('CHUCK',     1, 'CHUCK'),
            ('CLAIR',     1, 'CLAIR'),
            ('WILL',      1, 'WILL'),
            ('KOGA',      1, 'KOGA'),
            ('BRUNO',     1, 'BRUNO'),
            ('KAREN',     1, 'KAREN'),
            ('CHAMPION',  1, 'CHAMPION'),
            ('BROCK',     1, 'BROCK'),
            ('MISTY',     1, 'MISTY'),
            ('LT. SURGE', 1, 'LT. SURGE'),
            ('ERIKA',     1, 'ERIKA'),
            ('JANINE',    1, 'JANINE'),
            ('SABRINA',   1, 'SABRINA'),
            ('BLAINE',    1, 'BLAINE'),
            ('BLUE',      1, 'BLUE'),
            ('RED',       1, 'RED'),
        ],
    }

    def __init__(self, version):
        self.dataset = self.BOSSES[version]
        self.records = []
        self.attempts = Counter()
        self._reset()

    def on_battle_started(self, monitor, data=None):
        self._reset()
        if monitor.trainer_class is None:
            if OATS:
                print('[Battle] vs wild Pokémon')
            return
        name = self._find_key_battle(monitor.trainer_class, monitor.trainer_id)
        if not name:
            if OATS:
                print('[Battle] vs random trainer')
            return
        self._stats.attack = data.slot1_attack
        self._stats.defense = data.slot1_defense
        self._stats.sp_attack = data.slot1_sp_attack
        self._stats.sp_defense = data.slot1_sp_defense
        self._stats.speed = data.slot1_speed
        self.time_start = request_real_time()
        self.name = name
        print(f'[Battle] [{self.time_start}] started vs {name}')

    def on_battle_ended(self, monitor, data=None):
        name = self._find_key_battle(monitor.trainer_class, monitor.trainer_id)
        if name != self.name:
            print('[ERROR] it seems that a battle was skipped')
            print('  was tracking:', self.name)
            if not name:
                print('  battle end: (untracked opponent)')
            else:
                print('  battle end:', name)
        if not name:
            if OATS:
                print('[Battle] ended (untracked)')
            return  # not tracking this battle
        if data:
            h = data['game_time_h']
            m = data['game_time_m']
            s = data['game_time_s']
            self.game_time = f'{h}:{m}:{s}'
        key = (monitor.trainer_class, monitor.trainer_id)
        if not monitor.battle_result:
            print(f'[Battle] failed attempt vs {self.name}')
            self.attempts[key] += 1
            self._reset()
            return  # not tracking a loss/draw
        self.time_end = request_real_time()
        print(f'[Battle] [{self.time_end}] [{self.game_time}] won vs {self.name}')
        self.records.append(self._make_record(monitor, data, resets=self.attempts[key]))

    CSV_HEADERS = (
        'ROM',
        'Trainer',
        'Real Time',
        'Game Time',
        'Level',
        'Move 1',
        'Move 2',
        'Move 3',
        'Move 4',
        'Attack',
        'Defense',
        'Sp. Attack',
        'Sp. Defense',
        'Speed',
        'Attack Stage',
        'Defense Stage',
        'Sp. Attack Stage',
        'Sp. Defense Stage',
        'Speed Stage',
        'Accuracy Stage',
        'Evasion Stage',
        'Battle Attack',
        'Battle Defense',
        'Battle Sp. Attack',
        'Battle Sp. Defense',
        'Battle Speed',
        'Resets',
    )

    def store_updates(self):
        if not self.records:
            return

        records = self.records  # save reference because this is multithreaded
        self.records = []

        if not CSV_FILE.exists():
            text = ','.join(self.CSV_HEADERS) + '\n'
            CSV_FILE.write_text(text, encoding='utf-8')
        
        contents = list(','.join(r) for r in records)
        contents.append('')
        text = '\n'.join(contents)
        with CSV_FILE.open(mode='a', encoding='utf-8') as f:
            f.write(text)

    def _reset(self):
        self.time_start = None
        self.time_end = None
        self.game_time = None
        self.name = None
        self._stats = MonStats()

    def _find_key_battle(self, trainer_class, trainer_id):
        if trainer_class is not None and trainer_id is not None:
            for c, i, name in self.dataset:
                if c != trainer_class:
                    continue
                if i != trainer_id:
                    continue
                return name
        return None

    def _make_record(self, monitor, data, resets=0):
        return (
            data['rom'],
            self.name,
            self.time_end,
            self.game_time,
            str(data['level']),
            data['move1'],
            data['move2'],
            data['move3'],
            data['move4'],
            str(self._stats.attack),
            str(self._stats.defense),
            str(self._stats.sp_attack),
            str(self._stats.sp_defense),
            str(self._stats.speed),
            str(monitor.battle_mon.stages.attack),
            str(monitor.battle_mon.stages.defense),
            str(monitor.battle_mon.stages.sp_attack),
            str(monitor.battle_mon.stages.sp_defense),
            str(monitor.battle_mon.stages.speed),
            str(monitor.battle_mon.stages.accuracy),
            str(monitor.battle_mon.stages.evasion),
            str(monitor.battle_mon.stats.attack),
            str(monitor.battle_mon.stats.defense),
            str(monitor.battle_mon.stats.sp_attack),
            str(monitor.battle_mon.stats.sp_defense),
            str(monitor.battle_mon.stats.speed),
            str(resets),
        )


################################################################################
# Requests
################################################################################


def request_retroarch_status() -> str:
    print('[RetroArch] connecting')
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(RETROARCH_HOST)
        with SleepLoop(DEFAULT_LOOP_ITERATIONS) as loop:
            while loop.iterate():
                print('[RetroArch] request status')
                s.send(b'GET_STATUS\n')
                reply = s.recv(4096).decode('utf-8')
                if not reply.startswith('GET_STATUS '):
                    warnings.warn('[RetroArch] unexpected response: ' + reply)
                else:
                    reply = reply[11:]
                    if reply.startswith('CONTENTLESS'):
                        warnings.warn('[RetroArch] no content')
                    else:
                        parts = reply.split(',')
                        return parts[1]
    warnings.warn('[RetroArch] gave up on request')
    raise DataRequestError.get_rom()


def request_real_time() -> str:
    if OATS:
        return time.strftime("%H:%M:%S", time.localtime())
    else:
        print('[Time Server] connecting')
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(TIME_SERVER)
            print('[Time Server] request current time')
            s.send(b'getcurrenttime\r\n')
            timevalue = s.recv(1024)
            return timevalue.decode('utf-8').strip()


def request_gamehook_data() -> Tuple[str, Any]:
    with SleepLoop(DEFAULT_LOOP_ITERATIONS) as loop:
        while loop.iterate():
            print('[GameHook] request mapper')
            response = requests.get(GAMEHOOK_REQUESTS)
            response = json.loads(response.text)
            try:
                data = response['properties']
                game = response['meta']['gameName']
                return game, data
            except KeyError:
                warnings.warn('[GameHook] mapper not loaded')
    warnings.warn('[GameHook] gave up on request')
    raise DataRequestError.get_mapper()


################################################################################
# GameHook Watcher
################################################################################

class GameHookBridge:
    def __init__(self, on_connect=None, on_disconnect=None, on_error=None,
                 on_change=None, on_load=None):
        self.on_connect = on_connect or noop
        self.on_disconnect = on_disconnect or noop
        self.on_error = on_error or noop
        self.on_change = on_change or noop
        self.on_load = on_load or noop
        self.hub = None

    def connect(self):
        if self.hub is None:
            handler = logging.StreamHandler()
            handler.setLevel(logging.WARNING)
            self.hub = HubConnectionBuilder()\
                .with_url(GAMEHOOK_SIGNALR, options={'verify_ssl': False}) \
                .configure_logging(logging.WARNING, socket_trace=True, handler=handler) \
                .with_automatic_reconnect({
                    'type': 'raw',
                    'keep_alive_interval': 10,
                    'reconnect_interval': 5,
                    'max_attempts': 5,
                }).build()
            self.hub.on_open(self.on_connect)
            self.hub.on_close(self.on_disconnect)
            self.hub.on_error(self.on_error)
            self.hub.on('PropertyChanged', self.on_change)
            self.hub.on('GameHookError', self.on_error)
            self.hub.on('DriverError', self.on_error)
            self.hub.on('MapperLoaded', self.on_load)
            self.hub.start()

    def disconnect(self):
        if self.hub is not None:
            self.hub.stop()
            self.hub = None


################################################################################
# File Watcher
################################################################################


class SaveFileBackupAgent:
    def __init__(self, rom: str, delay=DEFAULT_SLEEP_DELAY, format=DEFAULT_BACKUP_NAME_FORMAT):
        self.rom = rom
        self.file = SRC_DIR / (rom + '.srm')
        self.delay = delay
        self.save_signal = False
        self.dirty = False
        try:
            self._cached_stamp = self.file.stat().st_mtime
        except FileNotFoundError:
            self._cached_stamp = 0
        self.name_format = format
        self.saved_data = {
            'rom': rom,
            'time': 0,
            'species': 'NULL',
            'level': 0,
            'location': 'NULL',
        }

    def watch(self):
        while True:
            self.watch_once()
            time.sleep(self.delay)

    def watch_once(self):
        # self.look_for_changes()
        if self.save_signal:
            self.backup_loop()
        # elif self.dirty:
        #    self.do_backup()

    def backup_loop(self):
        with SleepLoop(DEFAULT_LOOP_ITERATIONS) as loop:
            while loop.iterate() and not self.dirty:
                self.look_for_changes()
        self.do_backup()

    def look_for_changes(self):
        try:
            stamp = self.file.stat().st_mtime
        except FileNotFoundError:
            stamp = 0
        if stamp > self._cached_stamp:
            self.dirty = True
            self._cached_stamp = stamp

    def do_backup(self):
        if self.dirty:
            print('[Save File] detected changes')
        else:
            print('[Save File] no modifications')

        self.dirty = False
        self.save_signal = False

        print('[Save File] creating backup')
        filename = self.name_format.format(**self.saved_data)
        dest_file = DST_DIR / filename
        shutil.copy(self.file, dest_file)
        print('[Save File] backup complete')

    def save(self, params: Dict[str, Any]):
        self.saved_data.update(params)

        location = params.get('location', 'NULL')
        location = location.replace(' ', '').replace('-', '')
        self.saved_data['location'] = location

        if '{time}' in self.name_format:
            time_string = request_real_time()
            time_string = time_string.replace(':', '').replace('.', '').rstrip()
            self.saved_data['time'] = time_string

        try:
            self._cached_stamp = self.file.stat().st_mtime
        except FileNotFoundError:
            self._cached_stamp = 0

        print("[Save File] requesting backup")
        self.save_signal = True


################################################################################
# General Utility
################################################################################


class DataRequestError(Exception):
    @classmethod
    def get_rom(cls):
        return cls('[RetroArch] failed to get ROM status')

    @classmethod
    def get_mapper(cls):
        return cls('[GameHook] failed to get mapper')


class SleepLoop:
    def __init__(self, n=0, delay=DEFAULT_SLEEP_DELAY):
        self.n = n
        self.delay = delay
        self.iterate = self._no_loop
        self.i = -1

    @property
    def iteration(self):
        return self.i + 1

    def _first_iteration(self):
        self.iterate = self._other_iterations
        return True

    def _other_iterations(self):
        time.sleep(self.delay)
        self.i += 1
        if self.i < self.n:
            return True
        self.iterate = self._no_loop
        return False

    def _infinite_loop(self):
        return True

    def _no_loop(self):
        return False

    def __enter__(self):
        self.i = 0
        if self.n <= 0:
            self.iterate = self._infinite_loop
        else:
            self.iterate = self._first_iteration
        return self

    def __exit__(self, type, value, traceback):
        self.i = -1
        self.iterate = self._no_loop


def noop(*args, **kwargs):
    pass


################################################################################
# Script Entry Point
################################################################################

if __name__ == '__main__':
    sys.exit(main(sys.argv))
