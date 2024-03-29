# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Any, Callable, Dict, Final, List, Mapping, Optional

import json
import logging

from attrs import define, field
import requests
from signalrcore.hub_connection_builder import HubConnectionBuilder

from pokewatcher.core.util import SleepLoop, noop
from pokewatcher.errors import PokeWatcherError

###############################################################################
# Constants
###############################################################################

logger: Final[logging.Logger] = logging.getLogger(__name__)

###############################################################################
# Interface
###############################################################################


class GameHookError(PokeWatcherError):
    @classmethod
    def get_mapper(cls, url):
        return cls(f'Failed to get GameHook mapper from {url}')

    @classmethod
    def unknown_game(cls, name):
        return cls(f'No data handlers for game {name}')


@define
class GameHookBridge:
    on_connect: Callable = noop
    on_disconnect: Callable = noop
    on_error: Callable = noop
    on_change: Callable = noop
    on_load: Callable = noop
    meta: Dict[str, Any] = field(init=False, factory=dict)
    glossary: Dict[str, Any] = field(init=False, factory=dict)
    properties: List[str] = field(init=False, factory=list)
    url_signalr: str = field(init=False, default='http://localhost:8085/updates')
    url_requests: str = field(init=False, default='http://localhost:8085/mapper')
    hub: Optional[HubConnectionBuilder] = field(init=False, default=None, repr=False)

    @property
    def game_name(self) -> str:
        return self.meta.get('gameName', '')

    def setup(self, settings: Mapping[str, Any]):
        logger.info('setting up')
        logger.debug(f'settings: {settings}')
        host = settings['host']
        port = settings['port']
        self.url_signalr = f'http://{host}:{port}/updates'
        self.url_requests = f'http://{host}:{port}/mapper'
        self.request_mapper()

    def start(self):
        self.connect()

    def update(self, delta):
        # logger.debug('update')
        return

    def cleanup(self):
        logger.info('cleaning up')
        self.disconnect()

    def connect(self):
        if self.hub is None:
            logger.info(f'connecting to {self.url_signalr}')
            handler = logging.StreamHandler()
            handler.setLevel(logging.WARNING)
            # socket_trace produces lots of debug messages
            self.hub = (
                HubConnectionBuilder()
                .with_url(self.url_signalr, options={'verify_ssl': False})
                .configure_logging(logging.WARNING, socket_trace=False, handler=handler)
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
            self.hub.on('PropertyChanged', self._on_property_changed)
            self.hub.on('GameHookError', self.on_error)
            self.hub.on('DriverError', self.on_error)
            self.hub.on('MapperLoaded', self.on_load)
            self.hub.start()
            logger.info('connected')

    def disconnect(self):
        if self.hub is not None:
            logger.info(f'disconnecting from {self.url_signalr}')
            self.hub.stop()
            self.hub = None

    def request_mapper(self, ntries: int = 3) -> str:
        with SleepLoop(n=ntries, delay=1.0) as loop:
            while loop.iterate():
                logger.info(f'requesting mapper from {self.url_requests}')
                response = requests.get(self.url_requests)
                data = json.loads(response.text)
                try:
                    self.meta = data['meta']
                    self.glossary = data['glossary']
                    self.properties = data['properties']
                    name = self.meta['gameName']
                    logger.info('received mapper')
                    return name
                except KeyError:
                    logger.warning('mapper not yet loaded')
        logger.warning('gave up on mapper request')
        raise GameHookError.get_mapper(self.url_requests)

    def _on_property_changed(self, args):
        prop, _address, value, byte_values, _frozen, changed_fields = args
        if 'bytes' in changed_fields:
            self.on_change(prop, value, byte_values)


def new():
    instance = GameHookBridge()
    return instance
