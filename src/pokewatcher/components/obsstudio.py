# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Any, Final, Mapping

import asyncio
import logging

from attrs import define, field
from simpleobsws import Request, WebSocketClient

from pokewatcher.core.game import GameInterface
from pokewatcher.events import on_new_game

###############################################################################
# Constants
###############################################################################

logger: Final = logging.getLogger(__name__)

###############################################################################
# Interface
###############################################################################


@define
class ObsStudioInterface:
    game: GameInterface
    ws: WebSocketClient = field(init=False, factory=WebSocketClient, eq=False, repr=False)

    def setup(self, settings: Mapping[str, Any]):
        logger.info('setting up')
        self.ws.url = settings['url']
        self.ws.password = settings['password']

        on_new_game.watch(self.on_new_game)

    def start(self):
        logger.info('starting')
        self.ws.loop.run_until_complete(self.connect())

    def update(self, delta):
        # logger.debug('update')
        return

    def cleanup(self):
        logger.info('cleaning up')
        self.ws.loop.run_until_complete(self.disconnect())

    def on_new_game(self):
        logger.info('new game: start OBS recording')
        self.ws.loop.run_until_complete(self.start_record())

    async def connect(self):
        logger.info('connect to OBS websocket')
        await self.ws.connect()
        # Wait for the identification handshake to complete
        await self.ws.wait_until_identified()

    async def disconnect(self):
        logger.info('disconnect from OBS websocket')
        await ws.disconnect()

    async def start_record(self):
        request = Request('StartRecord')
        response = await self.ws.call(request)
        if response.ok():
            logger.info('start recording success')
        else:
            code = response.requestStatus.code
            comment = response.requestStatus.comment
            logger.error(f'start recording failure (code {code}): {comment!r}')


def new(game: GameInterface) -> ObsStudioInterface:
    instance = ObsStudioInterface(game)
    return instance
