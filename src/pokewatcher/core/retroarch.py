# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Any, Final, Mapping, Optional

import logging

from attrs import define, field

from pokewatcher.errors import PokeWatcherError
from pokewatcher.core.util import noop, SleepLoop, UdpConnection

###############################################################################
# Constants
###############################################################################

GET_STATUS: Final[str] = b'GET_STATUS\n'
SAVE_STATE: Final[str] = b'SAVE_STATE\n'

logger: Final = logging.getLogger(__name__)

###############################################################################
# Interface
###############################################################################


class RetroArchError(PokeWatcherError):
    @classmethod
    def get_rom(cls, address):
        return cls(f'Failed to get ROM status from {address}')

    @classmethod
    def save_state(cls, address):
        return cls(f'Failed to save game state at {address}')


@define
class RetroArchBridge:
    rom: Optional[str] = field(init=False, default=None)
    _socket: Optional[UdpConnection] = field(init=False, default=None, repr=False)

    def setup(self, settings: Mapping[str, Any]):
        logger.info('setting up')
        logger.debug(f'settings: {settings}')
        host = settings['host']
        port = settings['port']
        timeout = settings['timeout']
        self._socket = UdpConnection(host, port, timeout=timeout)
        self.request_status()

    def start(self):
        return

    def update(self, delta):
        # logger.debug('update')
        return

    def cleanup(self):
        logger.info('cleaning up')
        logger.info(f'disconnecting from {self._socket.address}')
        self._socket.disconnect()
        self._socket = None

    def request_status(self) -> str:
        with SleepLoop(n=3, delay=1.0) as loop:
            while loop.iterate():
                logger.info(f'connecting to {self._socket.address}')
                try:
                    self._socket.connect()
                    logger.info('requesting status')
                    self._socket.send(GET_STATUS)
                    reply = self._socket.receive(bytes=4096)
                except ConnectionError as e:
                    logger.error('failed to establish a connection')

                if not reply.startswith('GET_STATUS '):
                    logger.warning('unexpected response: ' + reply)
                else:
                    reply = reply[11:]
                    if reply.startswith('CONTENTLESS'):
                        logger.warning('no ROM content')
                    else:
                        parts = reply.split(',')
                        self.rom = parts[1]
                        logger.info('got ROM: ' + self.rom)
                        return self.rom  # break the loop
        logger.warning('unable to get RetroArch status')
        raise RetroArchError.get_rom(self._socket.address)

    def request_save_state(self):
        with SleepLoop(n=3, delay=0.1) as loop:
            while loop.iterate():
                try:
                    self._socket.connect()
                    logger.info('requesting save state')
                    self._socket.send(SAVE_STATE)
                    # no reply
                    # logger.info('requesting increment save slot')
                    # self._socket.send(b'STATE_SLOT_PLUS\n')
                    # no reply
                except ConnectionError as e:
                    logger.error('failed to establish a connection')
                return
        logger.warning('unable to create a saved state')
        raise RetroArchError.save_state(self._socket.address)


def new():
    instance = RetroArchBridge()
    return instance
