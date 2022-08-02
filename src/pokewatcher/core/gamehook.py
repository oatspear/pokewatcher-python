# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Any, Callable, Dict, Final, Mapping, Optional

import json
import logging
import requests

from attrs import define, field
from signalrcore.hub_connection_builder import HubConnectionBuilder

from pokewatcher.errors import PokeWatcherError
from pokewatcher.core.util import identity, noop, SleepLoop

###############################################################################
# Constants
###############################################################################

logger: Final = logging.getLogger(__name__)

###############################################################################
# Interface
###############################################################################


class GameHookError(PokeWatcherError):
    @classmethod
    def get_mapper(cls, url):
        return cls(f'Failed to get GameHook mapper from {url}')


@define
class GameHookBridge:
    on_connect: Callable = noop
    on_disconnect: Callable = noop
    on_error: Callable = noop
    on_change: Callable = noop
    on_load: Callable = noop
    meta: Dict[str, Any] = field(init=False, factory=dict)
    mapper: Dict[str, Any] = field(init=False, factory=dict)
    transforms: Dict[str, Callable] = field(init=False, factory=dict, repr=False)
    url_signalr: str = field(init=False, default='http://localhost:8085/updates')
    url_requests: str = field(init=False, default='http://localhost:8085/mapper')
    hub: Optional[HubConnectionBuilder] = field(init=False, default=None, repr=False)

    @property
    def game_name(self) -> Optional[str]:
        return self.meta.get('gameName')

    def setup(self, settings: Mapping[str, Any]):
        logger.info('setting up')
        logger.debug(f'settings: {settings}')
        urls = settings['url']
        self.url_signalr = urls['signalr']
        self.url_requests = urls['requests']

    def start(self):
        self.connect()
        self.request_mapper()

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
            self.hub = HubConnectionBuilder()\
                .with_url(self.url_signalr, options={'verify_ssl': False})\
                .configure_logging(logging.WARNING, socket_trace=True, handler=handler)\
                .with_automatic_reconnect({
                    'type': 'raw',
                    'keep_alive_interval': 10,
                    'reconnect_interval': 5,
                    'max_attempts': 5,
                }).build()
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

    def request_mapper(self, ntries=3) -> str:
        with SleepLoop(n=ntries, delay=1.0) as loop:
            while loop.iterate():
                logger.info(f'requesting mapper from {self.url_requests}')
                response = requests.get(self.url_requests)
                response = json.loads(response.text)
                try:
                    self.meta = response['meta']
                    self.mapper = {}
                    for prop, value in response['properties'].items():
                        f = self.transforms.get(prop, identity)
                        self.mapper[prop] = f(value)
                    name = self.meta['gameName']
                    logger.info('received mapper')
                    return name
                except KeyError:
                    logger.warning('mapper not yet loaded')
        logger.warning('gave up on mapper request')
        raise GameHookError.get_mapper(self.url_requests)

    def _on_property_changed(self, args):
        prop, _address, value, _bytes, _frozen, changed_fields = args
        if 'value' in changed_fields:
            f = self.transforms.get(key, identity)
            value = f(value)
            self.mapper[prop] = value
            self.on_change(prop, value)


def new():
    instance = GameHookBridge()
    return instance
