# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Any, Callable, Dict, Optional

import json
import logging
import requests

from attrs import define, field
from signalrcore.hub_connection_builder import HubConnectionBuilder

from pokewatcher.errors import PokeWatcherError
from pokewatcher.core.util import noop, SleepLoop

###############################################################################
# Constants
###############################################################################

logger = logging.getLogger(__name__)

###############################################################################
# Interface
###############################################################################


class GameHookError(PokeWatcherError):
    @classmethod
    def get_mapper(cls, url):
        return cls(f'Failed to get GameHook mapper from {url}')


@define
class GameHookBridge:
    meta: Dict[str, Any] = field(init=False, default={})
    mapper: Dict[str, Any] = field(init=False, default={})
    on_connect: Callable = noop
    on_disconnect: Callable = noop
    on_error: Callable = noop
    on_change: Callable = noop
    on_load: Callable = noop
    hub: Optional[HubConnectionBuilder] = field(init=False, default=None)

    @property
    def game_name(self) -> Optional[str]:
        return self.meta.get('gameName')

    def connect(self, url):
        if self.hub is None:
            logger.info(f'connecting to {url}')
            handler = logging.StreamHandler()
            handler.setLevel(logging.WARNING)
            self.hub = HubConnectionBuilder()\
                .with_url(url, options={'verify_ssl': False})\
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
            logger.info('disconnecting')
            self.hub.stop()
            self.hub = None

    def request_mapper(self, url, ntries=3) -> str:
        with SleepLoop(n=ntries, delay=1.0) as loop:
            while loop.iterate():
                logger.info(f'requesting mapper from {url}')
                response = requests.get(url)
                response = json.loads(response.text)
                try:
                    self.meta = response['meta']
                    self.mapper = response['properties']
                    name = self.meta['gameName']
                    logger.info('received mapper')
                    return name
                except KeyError:
                    logger.warning('mapper not yet loaded')
        logger.warning('gave up on mapper request')
        raise GameHookError.get_mapper(url)

    def _on_property_changed(self, args):
        prop, _address, value, _bytes, _frozen, changed_fields = args
        if 'value' in changed_fields:
            self.mapper[prop] = value
            self.on_change(prop, value)
