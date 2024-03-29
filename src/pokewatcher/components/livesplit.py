# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Any, Final, Mapping

import logging

from attrs import define, field

from pokewatcher.core.game import GameInterface
from pokewatcher.core.util import TcpConnection, TimeInterval, TimeRecord
from pokewatcher.errors import PokeWatcherComponentError

from pokewatcher.events import on_battle_ended, on_champion_victory, on_new_game

###############################################################################
# Constants
###############################################################################

logger: Final = logging.getLogger(__name__)

DEFAULTS: Final[Mapping[str, Any]] = {
    'enabled': False,
    'host': 'localhost',
    'port': 16834,
    'timeout': 3.0,
}

###############################################################################
# Interface
###############################################################################


@define
class LiveSplitInterface:
    game: GameInterface

    def setup(self, settings: Mapping[str, Any]):
        logger.info('setting up')
        logger.debug(f'settings: {settings}')

        if self.game.has_custom_clock:
            if not isinstance(self.game.clock, LivesplitClock):
                name = type(self.game.clock).__name__
                raise PokeWatcherComponentError(f'found pre-existing custom clock: {name}')

        host = settings['host']
        port = settings['port']
        timeout = settings['timeout']
        socket = TcpConnection(host, port, timeout=timeout)

        logger.info('setting livesplit as the default time server')
        if isinstance(self.game.clock, LivesplitClock):
            self.game.clock._socket.disconnect()
        self.game.clock = LivesplitClock(socket)

        on_new_game.watch(self.on_new_game)

        if self.is_gen2():
            on_battle_ended.watch(self.on_red_victory)
        else:
            on_champion_victory.watch(self.on_champion_victory)

    def start(self):
        logger.info('starting')
        if not isinstance(self.game.clock, LivesplitClock):
            name = type(self.game.clock).__name__
            raise PokeWatcherComponentError(f'found unexpected custom clock: {name}')

        logger.info('connect to livesplit')
        self.game.clock._socket.connect()

    def update(self, delta):
        # logger.debug('update')
        return

    def cleanup(self):
        logger.info('cleaning up')
        logger.info('disconnect from livesplit')
        self.game.clock._socket.disconnect()

    def on_new_game(self):
        logger.info('new game: start timer')
        self.game.clock.request_start()

    def on_champion_victory(self):
        logger.info('champion victory: pause timer')
        self.game.clock.request_pause()

    def on_red_victory(self):
        battle = self.game.data.battle
        if not battle.is_vs_wild:
            if battle.trainer.trainer_class == 'RED':
                logger.info('Red victory: pause timer')
                self.game.clock.request_pause()

    def is_gen2(self) -> bool:
        version = self.game.version.lower()
        return 'crystal' in version or 'gold' in version or 'silver' in version


@define
class LivesplitClock:
    _socket: TcpConnection
    time_start: TimeRecord = field(factory=TimeRecord)

    def reset_start_time(self):
        if self._socket.is_connected:
            try:
                self.request_reset()
            except ConnectionError as e:
                logger.error(f'unable to reset start time: {e}')

    def get_current_time(self) -> TimeRecord:
        if self._socket.is_connected:
            try:
                return self.request_current_time()
            except ConnectionError as e:
                logger.error(f'unable to get current time: {e}')
        return TimeRecord()

    def get_elapsed_time(self) -> TimeInterval:
        if self._socket.is_connected:
            try:
                now = self.request_current_time()
                return TimeInterval(start=self.time_start, end=now)
            except ConnectionError as e:
                logger.error(f'unable to get current time: {e}')
        return TimeInterval()

    def request_reset(self):
        logger.debug('request reset timer')
        self._socket.send(b'reset\r\n')
        # no reply

    def request_start(self):
        logger.debug('request start timer')
        self._socket.send(b'starttimer\r\n')
        # no reply

    def request_pause(self):
        logger.debug('request pause timer')
        self._socket.send(b'pause\r\n')
        # no reply

    def request_current_time(self) -> TimeRecord:
        logger.debug('request get current time')
        self._socket.send(b'getcurrenttime\r\n')
        reply = self._socket.receive(bytes=1024, encoding='utf-8')
        time_string = reply.strip()
        if '.' not in time_string:
            time_string = time_string + '.0'
        if ':' not in time_string:
            time_string = f'0:0:{time_string}'
        elif time_string.count(':') < 2:
            time_string = f'0:{time_string}'

        parts = time_string.rsplit('.', maxsplit=1)
        try:
            ms = int(parts[1])
            parts = parts[0].rsplit(':', maxsplit=2)
            h = int(parts[0])
            m = int(parts[1])
            s = int(parts[2])
            return TimeRecord(hours=h, minutes=m, seconds=s, millis=ms)
        except (IndexError, ValueError) as e:
            logger.error(f'getcurrenttime: unexpected reply: {reply}')
            logger.error(str(e))
            return TimeRecord()


def new(game: GameInterface) -> LiveSplitInterface:
    instance = LiveSplitInterface(game)
    return instance


def default_settings() -> Mapping[str, Any]:
    return dict(DEFAULTS)
