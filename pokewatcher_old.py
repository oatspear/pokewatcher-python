# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

################################################################################
# Imports
################################################################################

from types import SimpleNamespace
from typing import Any, Dict, Tuple

from collections import Counter
import json
import logging
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import time
import warnings

import keyboard
import requests
from signalrcore.hub_connection_builder import HubConnectionBuilder

################################################################################
# Constants
################################################################################

OATS = False

if OATS:
    SRC_DIR = Path(r'C:\RetroArch-Win64\saves')
    DST_DIR = Path(r'C:\Users\Andre\Games\ScottsThoughts')
else:
    SRC_DIR = Path(r'F:\Desktop\filming files\saves')
    DST_DIR = Path(r'F:\Desktop\filming files\backup saves')

LOG_FILE = DST_DIR / 'pokewatcher.log'

GAMEHOOK_SIGNALR = 'http://localhost:8085/updates'
GAMEHOOK_REQUESTS = 'http://localhost:8085/mapper'

RETROARCH_HOST = ('127.0.0.1', 55355)
TIME_SERVER = ('localhost', 16834)

DEFAULT_LOOP_ITERATIONS = 5
DEFAULT_SLEEP_DELAY = 3.0  # seconds

DEFAULT_BACKUP_NAME_FORMAT = '{rom} - lvl{level}-{time}-{location}.srm'

CSV_FILENAME = '{rom}.csv'

HERE = Path(__file__).parent
AHK_SAVE_STATE = HERE / 'scripts' / 'save_state.ahk'
AHK_TOGGLE_TIMER = HERE / 'scripts' / 'toggle_timer.ahk'
AHK_RECORD_VIDEO = HERE / 'scripts' / 'record_video.ahk'

KEY_RECORD_VIDEO = 'num lock+1'

logger = logging.getLogger(__name__)

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
        # test real-time server status
        request_real_time()

        rom = request_retroarch_status()
        print('[Watcher] got ROM:', rom)
        self.backup_agent = SaveFileBackupAgent(rom)
        # is_new_game = not self.backup_agent.file.exists()

        version, data = request_gamehook_data()
        print('[Watcher] got game version:', version)
        self._build_data_handler(rom, version, data)

        self.gamehook = GameHookBridge(
            on_connect=lambda: print('[GameHook] stream connected'),
            on_disconnect=lambda: print('[GameHook] stream disconnected'),
            on_error=lambda err: print('[GameHook] error:', err),
        )

        self.time_splitter = BattleTimeSplitter(rom, version)

        # connect everything
        self._connect_event_handlers()

        logger.setLevel(logging.DEBUG)
        logger.addHandler(logging.FileHandler(str(LOG_FILE), mode='w'))

    def main_loop(self):
        logger.info('Starting main loop.')
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
        elif 'blue' in game_string:
            self.data_handler = YellowDataHandler(rom, version, data)
        elif 'red' in game_string:
            self.data_handler = YellowDataHandler(rom, version, data)
        else:
            raise ValueError(f'[Watcher] unknown game version: {version}')
        print('[GameHook] initial data received')
        print('[New Game] tracking from this point onward')
        logger.info('data_handler.is_new_game = True')
        self.data_handler.is_new_game = True

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
            'playerId': 0,
        }
        self.events = GameEvents()
        self.battle = self._new_battle_monitor()
        self.battle.on_battle_started = self._emit_battle_started
        self.battle.on_battle_ended = self._emit_battle_ended
        self.is_new_game = False
        self.locations_to_visit = set()
        self._data_init()
        self._handlers = {}
        self._set_property_handlers()
        for prop in data:
            handle = self._handlers.get(prop['path'], noop)
            handle(prop['value'])

    def __getitem__(self, key):
        return self.data[key]

    def on_property_changed(self, args):
        prop, address, value, _bytes, _frozen, changed_fields = args
        if 'value' in changed_fields:
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

    def _handle_player_id(self, value):
        prev = self.data['playerId']
        self.data['playerId'] = value
        if value == 0:
            print('[Game Reset]')
            self.events.on_reset(self.data)
            self.battle.on_reset()
        else:
            if prev == 0 and self.is_new_game:
                print('[New Game] starting a new game')
                # autohotkey(AHK_RECORD_VIDEO)
                keyboard.send(KEY_RECORD_VIDEO)
                request_start_timer()
            self.is_new_game = False

    def _data_init(self):
        pass

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

    P_PLAYER_ID = 'player.playerId'

    def _data_init(self):
        self.locations_to_visit = set(self.ONE_TIME_LOCATIONS)

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
        self._handlers[self.P_LOCATION] = self._handle_location

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

        self._handlers[self.P_PLAYER_ID] = self._handle_player_id
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
            logger.info('[SFX] saved game')
            self.events.on_save(self.data)
        # self.battle.on_music_changed(value)

    def _set_special(self, value):
        x = int(value)
        self.data['specialAttack'] = x
        self.data['specialDefense'] = x

    CRITICAL_LOCATIONS = (
        'Viridian Forest',
        'Silph Co - 1F',
        'Indigo Plateau - Lobby',
        'Viridian City - Gym',
        'Pewter City - Gym',
        'Cerulean City - Gym',
        'Vermilion City - Gym',
        'Celadon City - Gym',
        'Fuchsia City - Gym',
        'Saffron City - Gym',
        'Cinnabar Island - Gym',
        "Lorelei's Room",
        "Bruno's Room",
        "Agatha's Room",
        "Lance's Room",
        'Champions Room',
    )

    ONE_TIME_LOCATIONS = (
        'Viridian City',
        'Pewter City',
        'Cerulean City',
        'Lavender Town',
        'Vermilion City',
        'Celadon City',
        'Fuchsia City',
        'Cinnabar Island',
        'Saffron City',
        'Rock Tunnel - 1',
        'Mt Moon - 1',
        'Victory Road',
        'Pokemon Tower - 1F',
        'Route 1',
        'Route 2',
        'Route 3',
        'Route 4',
        'Route 5',
        'Route 6',
        'Route 7',
        'Route 8',
        'Route 9',
        'Route 10',
        'Route 11',
        'Route 12',
        'Route 13',
        'Route 14',
        'Route 15',
        'Route 16',
        'Route 17',
        'Route 18',
        'Route 19',
        'Route 20',
        'Route 21',
        'Route 22',
        'Route 23',
        'Route 24',
        'Route 25',
    )

    def _handle_location(self, value):
        print('[Data] new location:', value)
        value = str(value)
        self.data['location'] = value
        if value in self.CRITICAL_LOCATIONS:
            request_save_state()
        elif value in self.locations_to_visit:
            request_save_state()
            self.locations_to_visit.remove(value)

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
    P_SPECIES = 'player.team.0.species'
    P_LEVEL = 'player.team.0.level'
    P_MOVE1 = 'player.team.0.move1'
    P_MOVE2 = 'player.team.0.move2'
    P_MOVE3 = 'player.team.0.move3'
    P_MOVE4 = 'player.team.0.move4'
    P_MON_ATK = 'player.team.0.Attack'
    P_MON_DEF = 'player.team.0.Defense'
    P_MON_SPD = 'player.team.0.Speed'
    P_MON_SPATK = 'player.team.0.SpecialAttack'
    P_MON_SPDEF = 'player.team.0.SpecialDefense'

    P_MAP_GROUP = 'overworld.mapGroup'
    P_MAP_NUMBER = 'overworld.mapNumber'

    # P_AUDIO_SOUND = 'audio.currentSound'
    # P_AUDIO_MUSIC = 'audio.musicID'
    P_AUDIO_CHANNEL5 = 'audio.channel5MusicID'

    P_BATTLE_MODE = 'battle.mode'
    P_BATTLE_TYPE = 'battle.type'
    P_BATTLE_RESULT = 'battle.result'
    P_TRAINER_CLASS = 'battle.trainer.class'
    P_TRAINER_ID = 'battle.trainer.id'
    P_BATTLE_ALARM = 'battle.lowHealthAlarm'

    P_STAGE_ATK = 'battle.yourPokemon.modStageAttack'
    P_STAGE_DEF = 'battle.yourPokemon.modStageDefense'
    P_STAGE_SPD = 'battle.yourPokemon.modStageSpeed'
    P_STAGE_SPATK = 'battle.yourPokemon.modStageSpecialAttack'
    P_STAGE_SPDEF = 'battle.yourPokemon.modStageSpecialDefense'
    P_STAGE_ACC = 'battle.yourPokemon.modStageAccuracy'
    P_STAGE_EVA = 'battle.yourPokemon.modStageEvasion'

    P_BATTLE_ATK = 'battle.yourPokemon.battleStatAttack'
    P_BATTLE_DEF = 'battle.yourPokemon.battleStatDefense'
    P_BATTLE_SPD = 'battle.yourPokemon.battleStatSpeed'
    P_BATTLE_SPATK = 'battle.yourPokemon.battleStatSpecialAttack'
    P_BATTLE_SPDEF = 'battle.yourPokemon.battleStatSpecialDefense'

    P_PLAYER_ID = 'player.playerId'
    P_GAME_TIME_HOURS = 'gameTime.hours'
    P_GAME_TIME_MINUTES = 'gameTime.minutes'
    P_GAME_TIME_SECONDS = 'gameTime.seconds'
    # P_TEXT_PROMPT = 'screen.text.prompt'

    P_BADGE1 = 'player.badges.zephyrBadge'
    P_BADGE2 = 'player.badges.hiveBadge'
    P_BADGE3 = 'player.badges.plainBadge'
    P_BADGE4 = 'player.badges.fogBadge'
    P_BADGE5 = 'player.badges.stormBadge'
    P_BADGE6 = 'player.badges.mineralBadge'
    P_BADGE7 = 'player.badges.glacierBadge'
    P_BADGE8 = 'player.badges.risingBadge'

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
        self._handlers[self.P_MAP_NUMBER] = self._set_map_number_and_location

        self._handlers[self.P_BATTLE_MODE] = self.battle.on_battle_mode_changed
        self._handlers[self.P_BATTLE_TYPE] = self.battle.on_battle_type_changed
        self._handlers[self.P_BATTLE_RESULT] = self.battle.on_battle_result_changed
        self._handlers[self.P_TRAINER_CLASS] = self.battle.on_trainer_class_changed
        self._handlers[self.P_TRAINER_ID] = self.battle.on_trainer_id_changed
        self._handlers[self.P_BATTLE_ALARM] = self.battle.on_low_health_alarm_changed

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

        self._handlers[self.P_PLAYER_ID] = self._handle_player_id
        self._handlers[self.P_GAME_TIME_HOURS] = self._int_setter('game_time_h')
        self._handlers[self.P_GAME_TIME_MINUTES] = self._int_setter('game_time_m')
        self._handlers[self.P_GAME_TIME_SECONDS] = self._int_setter('game_time_s')

        # self._handlers[self.P_AUDIO_SOUND] = self._handle_sound_effects
        self._handlers[self.P_AUDIO_CHANNEL5] = self._handle_sound_effects

    MAPS = {
        'OLIVINE': {2: 'OLIVINE_GYM'},
        'MAHOGANY': {2: 'MAHOGANY_GYM'},
        'DUNGEONS': {
            1: 'SPROUT_TOWER',
            2: 'SPROUT_TOWER',
            3: 'SPROUT_TOWER',
            4: 'TIN_TOWER',
            5: 'TIN_TOWER',
            6: 'TIN_TOWER',
            7: 'TIN_TOWER',
            8: 'TIN_TOWER',
            9: 'TIN_TOWER',
            10: 'TIN_TOWER',
            11: 'TIN_TOWER',
            12: 'TIN_TOWER',
            13: 'BURNED_TOWER',
            14: 'BURNED_TOWER',
            17: 'RADIO_TOWER',
            18: 'RADIO_TOWER',
            19: 'RADIO_TOWER',
            20: 'RADIO_TOWER',
            21: 'RADIO_TOWER',
            40: 'SLOWPOKE_WELL',
            41: 'SLOWPOKE_WELL',
            42: 'LIGHTHOUSE',
            43: 'LIGHTHOUSE',
            44: 'LIGHTHOUSE',
            45: 'LIGHTHOUSE',
            46: 'LIGHTHOUSE',
            47: 'LIGHTHOUSE',
            49: 'TEAM_ROCKET_BASE',
            50: 'TEAM_ROCKET_BASE',
            51: 'TEAM_ROCKET_BASE',
            52: 'ILEX_FOREST',
            53: 'GOLDENROD_UNDERGROUND',
            54: 'GOLDENROD_UNDERGROUND',
            55: 'GOLDENROD_UNDERGROUND',
            56: 'GOLDENROD_UNDERGROUND',
            91: 'VICTORY_ROAD',
        },
        'ECRUTEAK': {
            2: 'WISE_TRIOS_ROOM',
            5: 'DANCE_THEATRE',
            7: 'ECRUTEAK_GYM',
        },
        'BLACKTHORN': {
            1: 'BLACKTHORN_GYM',
            2: 'BLACKTHORN_GYM',
        },
        'CINNABAR': {4: 'CINNABAR_GYM'},
        'CERULEAN': {6: 'CERULEAN_GYM'},
        'AZALEA': {5: 'AZALEA_GYM'},
        'VIOLET': {7: 'VIOLET_GYM'},
        'GOLDENROD': {3: 'GOLDENROD_GYM'},
        'VERMILION': {11: 'VERMILION_GYM'},
        'PEWTER': {4: 'PEWTER_GYM'},
        'FAST SHIP': {10: 'MOUNT_MOON', 11: 'MOUNT_MOON', 12: 'TIN_TOWER_ROOF'},
        'INDIGO': {
            3: 'WILLS_ROOM',
            4: 'KOGAS_ROOM',
            5: 'BRUNOS_ROOM',
            6: 'KARENS_ROOM',
            7: 'LANCES_ROOM',
        },
        'FUCHSIA': {8: 'FUCHSIA_GYM'},
        'CELADON': {21: 'CELADON_GYM'},
        'CIANWOOD': {
            5: 'CIANWOOD_GYM',
            11: 'BATTLE_TOWER',
            12: 'BATTLE_TOWER',
            13: 'BATTLE_TOWER',
            14: 'BATTLE_TOWER',
            15: 'BATTLE_TOWER',
            16: 'BATTLE_TOWER',
        },
        'VIRIDIAN': {4: 'VIRIDIAN_GYM'},
        'SAFFRON': {4: 'SAFFRON_GYM'},
    }

    def _set_map_group_and_location(self, value):
        map_number = self.data.get('map_number', 0)
        self.data['map_group'] = str(value)
        location = str(value)
        map_group = self.MAPS.get(location)
        if map_group:
            location = map_group.get(map_number, location)
        self.data['location'] = location
        print('[Data] new location:', location)

    def _set_map_number_and_location(self, value):
        self.data['map_number'] = value
        location = self.data.get('map_group', 'NULL')
        map_group = self.MAPS.get(location)
        if map_group:
            location = map_group.get(value, location)
        self.data['location'] = location
        print('[Data] new location:', location)

    SFX_SAVE_FILE = 37
    SFX_SAVE_FILE_CH5 = 9472

    def _handle_sound_effects(self, value):
        # self.data['sound'] = int(value)
        if value == self.SFX_SAVE_FILE_CH5:
            print('[Events] saved game')
            logger.info('[SFX] saved game')
            self.events.on_save(self.data)

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
        # glitch
        sp_attack = self.data.get('specialAttack', 0)
        if sp_attack in range(0, 205) or sp_attack in range(433, 660):
            mult = 1
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

    def on_reset(self):
        logger.info('detected game reset')
        if self.state != self.STATE_OUT_OF_BATTLE:
            logger.info('battle monitor was in battle; counting as a loss')
            logger.debug(self._internal_state())
            self._white_out()

    def on_battle_type_changed(self, value):
        logger.info(f'on_battle_type_changed({value})')
        logger.debug(self._internal_state())
        self.battle_type = value

        if value == self.BATTLE_TYPE_NONE:
            if self.state == self.STATE_IN_BATTLE:
                self._run_away()
            elif self.state == self.STATE_PLAYER_WON:
                self.state = self.STATE_OUT_OF_BATTLE
                self.battle_result = None

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
        logger.info(f'on_low_health_alarm_changed({value})')
        logger.debug(self._internal_state())

        if value == self.ALARM_DISABLED:
            if self.state != self.STATE_IN_BATTLE:
                print('[Battle] player won but monitor is not in the correct state')
                print('[Battle] state:', self.state)
            self._win_battle()

        elif value == self.ALARM_ENABLED:
            # game reset or battle starting after a previous victory
            # print('[Battle] game reset or battle starting')
            # print('[Battle] state:', self.state)
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

    def _internal_state(self):
        return '\n'.join(
            (
                'YellowBattleMonitor',
                f'  state: {self.state}',
                f'  battle_type: {self.battle_type}',
                f'  trainer_class: {self.trainer_class}',
                f'  trainer_id: {self.trainer_id}',
                f'  enemy_species: {self.enemy_species}',
                f'  battle_result: {self.battle_result}',
                '  battle_mon:',
                f'    stats: {self.battle_mon.stats}',
                f'    stages: {self.battle_mon.stages}',
            )
        )


# BattleIntro:
#   farcall ClearBattleRAM
#       write [wBattleResult]
#   call InitEnemy
#       read [wOtherTrainerClass]
#       write [wTrainerClass]
#       write [wBattleMode]
# ExitBattle:
#   call CleanUpBattleRAM
#       write [wBattleType]
#       write [wBattleMode]
#       write [wOtherTrainerClass]
# WinTrainerBattle:
#   write [wBattleEnded]


class CrystalBattleMonitor:
    # wBattleMode
    #   set to 0 with CleanUpBattleRAM at the end of all battles
    #   set to 1 with InitEnemy at the start of a wild battle
    #   set to 2 with InitEnemy at the start of a trainer battle
    # wBattleLowHealthAlarm
    #   set to 0 with ClearBattleRAM at the start of every battle
    #   set to 1 with UpdateBattleStateAndExperienceAfterEnemyFaint on victory against wild
    #   set to 1 with WinTrainerBattle on victory against trainers

    BATTLE_TYPE_NORMAL = 'NORMAL'
    BATTLE_TYPE_CANLOSE = 'CANLOSE'

    BATTLE_MODE_NONE = 'NONE'
    BATTLE_MODE_WILD = 'WILD'
    BATTLE_MODE_TRAINER = 'TRAINER'

    BATTLE_RESULT_WIN = 'WIN'
    BATTLE_RESULT_LOSE = 'LOSE'
    BATTLE_RESULT_DRAW = 'DRAW'

    STATE_OUT_OF_BATTLE = 0
    STATE_IN_BATTLE = 1
    STATE_PLAYER_WON = 2

    TRAINER_CLASS_NONE = 'NOBODY'

    ALARM_ENABLED = 'Enabled'
    ALARM_DISABLED = 'Disabled'

    def __init__(self):
        self.on_battle_started = noop
        self.on_battle_ended = noop
        self._reset()

    def on_reset(self):
        logger.info('detected game reset')
        if self.state != self.STATE_OUT_OF_BATTLE:
            self.battle_result = False
            logger.info('battle monitor was in battle; counting as a loss')
            logger.debug(self._internal_state())
            self._end_battle()

    def on_battle_mode_changed(self, value):
        logger.info('transition to battle mode: ' + value)
        self.battle_mode = value
        if value == self.BATTLE_MODE_NONE:
            if self.state == self.STATE_PLAYER_WON:
                print('[Battle] back to overworld')
                logger.info('reached the end of the battle scene')
                self.state = self.STATE_OUT_OF_BATTLE
            elif self.state != self.STATE_OUT_OF_BATTLE:
                self._end_battle()
        else:
            logger.info('detected start of battle')
            logger.debug(self._internal_state())
            if self.state != self.STATE_OUT_OF_BATTLE:
                print('[Battle] battle starting but monitor was already in battle')
                logger.warning('battle monitor probably missed a battle')
            self.battle_result = True
            self.state = self.STATE_IN_BATTLE
            self.on_battle_started()

    def on_low_health_alarm_changed(self, value):
        logger.info(f'on_low_health_alarm_changed({value})')
        logger.debug(self._internal_state())

        if value == self.ALARM_DISABLED:
            if self.state != self.STATE_IN_BATTLE:
                print('[Battle] player won but monitor is not in the correct state')
                print('[Battle] state:', self.state)
            self.battle_result = True
            self.state = self.STATE_PLAYER_WON
            self.on_battle_ended()

        elif value == self.ALARM_ENABLED:
            # game reset or battle ended
            # print('[Battle] game reset or battle ended')
            # print('[Battle] state:', self.state)
            pass

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

    def _internal_state(self):
        return '\n'.join(
            (
                'CrystalBattleMonitor',
                f'  state: {self.state}',
                f'  battle_type: {self.battle_type}',
                f'  battle_mode: {self.battle_mode}',
                f'  trainer_class: {self.trainer_class}',
                f'  trainer_id: {self.trainer_id}',
                f'  enemy_species: {self.enemy_species}',
                f'  battle_result: {self.battle_result}',
                '  battle_mon:',
                f'    stats: {self.battle_mon.stats}',
                f'    stages: {self.battle_mon.stages}',
            )
        )


################################################################################
# Game Events
################################################################################


class GameEvents:
    def __init__(self):
        self.on_reset = noop
        self.on_save = noop
        self.on_battle_started = noop
        self.on_battle_ended = noop


################################################################################
# Event Observers
################################################################################


class BattleTimeSplitter:
    BOSSES = {
        'Pokemon Yellow': [
            # CLASS,         ID, NAME
            ('BROCK', 1, 'BROCK'),
            ('BROCK', 1, 'BROCK'),
            ('MISTY', 1, 'MISTY'),
            ('LASS', 10, 'ODDISH LASS'),
            ('ROCKET', 5, 'ROCKET'),
            ('LT.SURGE', 1, 'LT.SURGE'),
            ('JR TRAINER F', 5, 'RTG1 - WRAPPING LASS'),
            ('POKEMANIAC', 7, 'RTG2 - POKEMANIAC 1'),
            ('POKEMANIAC', 5, 'RTG3 - POKEMANIAC 2'),
            ('JR TRAINER F', 10, 'RTG4 - STATUS JR TRAINER'),
            ('HIKER', 9, 'RTG5 - SELF-DESTRUCTING HIKER'),
            ('JR TRAINER F', 18, 'RTG6 - FINISHER'),
            ('ERIKA', 1, 'ERIKA'),
            ('KOGA', 1, 'KOGA'),
            ('BLAINE', 1, 'BLAINE'),
            ('SABRINA', 1, 'SABRINA'),
            ('GIOVANNI', 2, 'GIOVANNI (SILPH)'),
            ('GIOVANNI', 3, 'GIOVANNI'),
            ('LORELEI', 1, 'LORELEI'),
            ('BRUNO', 1, 'BRUNO'),
            ('AGATHA', 1, 'AGATHA'),
            ('LANCE', 1, 'LANCE'),
            ('RIVAL1', 2, 'RIVAL (OPTIONAL)'),
            ('RIVAL1', 3, 'RIVAL (NUGGET BRIDGE)'),
            ('RIVAL2', 1, 'RIVAL (SS ANNE)'),
            ('RIVAL2', 2, 'RIVAL (PKMN TOWER)'),
            ('RIVAL2', 3, 'RIVAL (PKMN TOWER)'),
            ('RIVAL2', 4, 'RIVAL (PKMN TOWER)'),
            ('RIVAL2', 5, 'RIVAL (SILPH CO.)'),
            ('RIVAL2', 6, 'RIVAL (SILPH CO.)'),
            ('RIVAL2', 7, 'RIVAL (SILPH CO.)'),
            ('RIVAL2', 8, 'RIVAL (FINAL)'),
            ('RIVAL2', 9, 'RIVAL (FINAL)'),
            ('RIVAL2', 10, 'RIVAL (FINAL)'),
            ('RIVAL3', 1, 'CHAMPION'),
            ('RIVAL3', 2, 'CHAMPION'),
            ('RIVAL3', 3, 'CHAMPION'),
        ],
        'Pokemon Crystal': [
            # CLASS,    ID,  NAME
            # ('YOUNGSTER', 1, 'YOUNGSTER JOEY'),
            # ('YOUNGSTER', 2, 'YOUNGSTER MIKEY'),
            ('RIVAL1', 1, 'RIVAL1'),
            ('RIVAL1', 2, 'RIVAL1'),
            ('RIVAL1', 3, 'RIVAL1'),
            ('FALKNER', 1, 'FALKNER'),
            ('RIVAL1', 4, 'RIVAL2'),
            ('RIVAL1', 5, 'RIVAL2'),
            ('RIVAL1', 6, 'RIVAL2'),
            ('BUGSY', 1, 'BUGSY'),
            ('WHITNEY', 1, 'WHITNEY'),
            ('RIVAL1', 7, 'RIVAL3'),
            ('RIVAL1', 8, 'RIVAL3'),
            ('RIVAL1', 9, 'RIVAL3'),
            ('MORTY', 1, 'MORTY'),
            ('CHUCK', 1, 'CHUCK'),
            ('PRYCE', 1, 'PRYCE'),
            ('JASMINE', 1, 'JASMINE'),
            ('RIVAL1', 10, 'RIVAL4'),
            ('RIVAL1', 11, 'RIVAL4'),
            ('RIVAL1', 12, 'RIVAL4'),
            ('CLAIR', 1, 'CLAIR'),
            ('WILL', 1, 'WILL'),
            ('KOGA', 1, 'KOGA'),
            ('BRUNO', 1, 'BRUNO'),
            ('KAREN', 1, 'KAREN'),
            ('CHAMPION', 1, 'CHAMPION'),
            ('SABRINA', 1, 'SABRINA'),
            ('ERIKA', 1, 'ERIKA'),
            ('MISTY', 1, 'MISTY'),
            ('LT. SURGE', 1, 'LT. SURGE'),
            ('BROCK', 1, 'BROCK'),
            ('BLAINE', 1, 'BLAINE'),
            ('JANINE', 1, 'JANINE'),
            ('BLUE', 1, 'BLUE'),
            ('RED', 1, 'RED'),
        ],
    }

    def __init__(self, rom, version):
        filename = CSV_FILENAME.format(rom=rom)
        self.filepath = DST_DIR / filename
        self.dataset = self.BOSSES[version]
        self.records = []
        self.attempts = Counter()
        self._reset()

    def on_battle_started(self, monitor, data=None):
        logger.info('on_battle_started()')
        logger.debug(monitor._internal_state())
        logger.debug(f'data: {data.data}')
        self._reset()
        if monitor.trainer_class is None:
            logger.info('[Battle] vs wild Pokémon')
            if OATS:
                print('[Battle] vs wild Pokémon')
            return
        name = self._find_key_battle(monitor.trainer_class, monitor.trainer_id)
        if not name:
            logger.info('[Battle] vs random trainer')
            if OATS:
                print('[Battle] vs random trainer')
            return
        logger.info('key battle found: ' + name)
        self._stats.attack = data.slot1_attack
        self._stats.defense = data.slot1_defense
        self._stats.sp_attack = data.slot1_sp_attack
        self._stats.sp_defense = data.slot1_sp_defense
        self._stats.speed = data.slot1_speed
        self.time_start = request_real_time()
        self.name = name
        print(f'[Battle] [{self.time_start}] started vs {name}')

    def on_battle_ended(self, monitor, data=None):
        logger.info('on_battle_ended()')
        logger.debug(monitor._internal_state())
        logger.debug(f'data: {data.data}')
        name = self._find_key_battle(monitor.trainer_class, monitor.trainer_id)
        if name != self.name:
            logger.error(f'skipped battle from {self.name} to {name}')
            print('[ERROR] it seems that a battle was skipped')
            print('  was tracking:', self.name)
            if not name:
                print('  battle end: (untracked opponent)')
            else:
                print('  battle end:', name)
        if not name:
            logger.info('[Battle] ended (untracked)')
            if OATS:
                print('[Battle] ended (untracked)')
            return  # not tracking this battle
        logger.info('key battle found: ' + name)
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
        if name == 'CHAMPION':
            # logger.info('[AutoHotkey] toggle timer')
            # print('[AutoHotkey] toggle timer')
            # autohotkey(AHK_TOGGLE_TIMER)
            request_pause_timer()

    CSV_HEADERS = (
        'ROM',
        'Species',
        'Trainer',
        'RTHours',
        'RTMinutes',
        'RTSeconds',
        'RTMilliseconds',
        'Start Time',
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

        try:
            if not self.filepath.exists():
                text = ','.join(self.CSV_HEADERS) + '\n'
                self.filepath.write_text(text, encoding='utf-8')

            contents = list(','.join(r) for r in records)
            contents.append('')
            text = '\n'.join(contents)
            with self.filepath.open(mode='a', encoding='utf-8') as f:
                f.write(text)
        except OSError as e:
            print('[ERROR] unable to write to splits file')
            print(e)
            # rollback
            self.records.extend(records)

    def _reset(self):
        self.time_start = None
        self.time_end = None
        self.game_time = None
        self.name = None
        self._stats = MonStats()

    def _find_key_battle(self, trainer_class, trainer_id):
        logger.debug(f'find_key_battle({repr(trainer_class)}, {repr(trainer_id)})')
        if trainer_class is not None and trainer_id is not None:
            for c, i, name in self.dataset:
                logger.debug(f'trying ({repr(c)}, {repr(i)}, {repr(name)})')
                if c != trainer_class:
                    continue
                if i != trainer_id:
                    continue
                logger.debug(f'found key battle: {name}')
                return name
        return None

    def _make_record(self, monitor, data, resets=0):
        h, m, s, ms = time_fields(self.time_end)
        return (
            data['rom'],
            data['species'],
            self.name,
            str(h),
            str(m),
            str(s),
            str(ms),
            self.time_start,
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


BattleTimeSplitter.BOSSES['Pokemon Red and Blue'] = BattleTimeSplitter.BOSSES['Pokemon Yellow']


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


def request_save_state():
    print('[RetroArch] connecting')
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(RETROARCH_HOST)
            print('[RetroArch] request save state')
            s.send(b'SAVE_STATE\n')
            # no reply
            # print('[RetroArch] request increment save slot')
            # s.send(b'STATE_SLOT_PLUS\n')
            # no reply
    except ConnectionError as e:
        print('[RetroArch] failed to save state')
        logger.error(f'[RetroArch] {e}')


def request_real_time() -> str:
    print('[Time Server] connecting')
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(TIME_SERVER)
            print('[Time Server] request current time')
            s.send(b'getcurrenttime\r\n')
            timevalue = s.recv(1024)
            timevalue = timevalue.decode('utf-8').strip()
            if '.' not in timevalue:
                timevalue = timevalue + '.0'
            if ':' not in timevalue:
                return f'0:0:{timevalue}'
            if timevalue.count(':') < 2:
                return f'0:{timevalue}'
            return timevalue
    except ConnectionError:
        print('[Time Server] failed to connect')
        print('[Time Server] failed to connect')
        print('[Time Server] failed to connect')
        warnings.warn('[Time Server] failed to connect')
        logger.error('[Time Server] failed to connect')
        return time.strftime('%H:%M:%S', time.localtime()) + '.0'


def request_start_timer():
    print('[Time Server] connecting')
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(TIME_SERVER)
            print('[Time Server] request start timer')
            s.send(b'starttimer\r\n')
            # no reply
    except ConnectionError as e:
        print('[Time Server] failed to connect')
        print('[Time Server] failed to connect')
        print('[Time Server] failed to connect')
        warnings.warn('[Time Server] failed to connect')
        logger.error(f'[Time Server] {e}')


def request_pause_timer():
    print('[Time Server] connecting')
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(TIME_SERVER)
            print('[Time Server] request pause timer')
            s.send(b'pause\r\n')
            # no reply
    except ConnectionError as e:
        print('[Time Server] failed to connect')
        print('[Time Server] failed to connect')
        print('[Time Server] failed to connect')
        warnings.warn('[Time Server] failed to connect')
        logger.error(f'[Time Server] {e}')


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
# External Processes
################################################################################


def autohotkey(script: Path) -> bool:
    logger.info(f'[AutoHotkey] running {script}')
    cmd = f'start autohotkey {script}'
    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print('[AutoHotkey] failed to run script')
        warnings.warn(str(e))
        logger.error(f'[AutoHotkey] {e}')
        return False
    return True


################################################################################
# GameHook Watcher
################################################################################


class GameHookBridge:
    def __init__(
        self, on_connect=None, on_disconnect=None, on_error=None, on_change=None, on_load=None
    ):
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
            self.hub = (
                HubConnectionBuilder()
                .with_url(GAMEHOOK_SIGNALR, options={'verify_ssl': False})
                .configure_logging(logging.WARNING, socket_trace=True, handler=handler)
                .with_automatic_reconnect(
                    {
                        'type': 'raw',
                        'keep_alive_interval': 10,
                        'reconnect_interval': 5,
                        'max_attempts': 5,
                    }
                )
                .build()
            )
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
        self._timestamp = 0

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
        if self.save_signal:
            t = time.time()
            if (t - self._timestamp) < 1.0:
                return  # discard too many requests in a short period

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

        print('[Save File] requesting backup')
        self.save_signal = True
        self._timestamp = time.time()

        # print('[AutoHotkey] running "save state" script')
        # autohotkey(AHK_SAVE_STATE)
        request_save_state()


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


def time_fields(time_string):
    parts = time_string.split('.')
    if len(parts) < 2:
        millis = 0
    else:
        millis = int(parts[-1])
        time_string = parts[0]
    parts = time_string.split(':')
    seconds = int(parts[-1])
    if len(parts) == 1:
        hours = 0
        minutes = 0
    elif len(parts) == 2:
        hours = 0
        minutes = int(parts[-2])
    else:
        hours = int(parts[-3])
        minutes = int(parts[-2])
    return (hours, minutes, seconds, millis)


################################################################################
# Script Entry Point
################################################################################

if __name__ == '__main__':
    sys.exit(main(sys.argv))
