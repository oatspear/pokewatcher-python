# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from types import SimpleNamespace
from typing import Any, Final, List, Mapping, Optional, Set

import asyncio
from collections import Counter, defaultdict
import json
import logging
from pathlib import Path
from threading import Lock, Thread, get_native_id

from attrs import asdict, define, field
from attrs.validators import instance_of
import websockets

from pokewatcher.core.game import GameInterface
from pokewatcher.core.util import Attribute, TimeInterval, TimeRecord
from pokewatcher.data.structs import BadgeData, GameData, GameTime, TrainerParty
from pokewatcher.events import on_battle_ended, on_battle_started, on_reset

###############################################################################
# Constants
###############################################################################

logger: Final = logging.getLogger(__name__)

BattleRecord = List[Any]

DEFAULTS: Final[Mapping[str, Any]] = {
    'enabled': True,
    'labels': {},
    'output': {
        'csv': {
            'path': '{rom}.csv',
            'labels': {
                'rom': 'ROM',
                'trainer_name': 'Trainer',
                'realtime.end': 'Real Time',
                'time': 'Game Time',
                'resets': 'Resets',
            },
            'attributes': [
                'rom',
                'trainer_name',
                'realtime.end',
                'time',
                'resets',
            ],
        },
        'websocket': {
            'host': 'localhost',
            'port': 6789,
            'labels': {
                'rom': 'rom',
                'trainer_name': 'trainerName',
                'realtime.end': 'realTime',
                'time': 'gameTime',
                'resets': 'resets',
            },
            'attributes': [
                'rom',
                'trainer_name',
                'realtime.end',
                'time',
                'resets',
            ],
        }
    },
    'trainers': {
        'Pokemon Red and Blue': 'Pokemon Yellow',
        'Pokemon Yellow': [
            {
                'class': 'BROCK',
                'number': 1,
                'name': 'Brock',
            },
            {
                'class': 'MISTY',
                'number': 1,
                'name': 'Misty',
            },
            {
                'class': 'LT.SURGE',
                'number': 1,
                'name': 'Lt. Surge',
            },
            {
                'class': 'ERIKA',
                'number': 1,
                'name': 'Erika',
            },
            {
                'class': 'KOGA',
                'number': 1,
                'name': 'Koga',
            },
            {
                'class': 'BLAINE',
                'number': 1,
                'name': 'Blaine',
            },
            {
                'class': 'SABRINA',
                'number': 1,
                'name': 'Sabrina',
            },
            {
                'class': 'GIOVANNI',
                'number': 3,
                'name': 'Giovanni',
            },
            {
                'class': 'RIVAL3',
                'number': 1,
                'name': 'Champion',
            },
            {
                'class': 'RIVAL3',
                'number': 2,
                'name': 'Champion',
            },
            {
                'class': 'RIVAL3',
                'number': 3,
                'name': 'Champion',
            },
        ],
        'Pokemon Crystal': [
            {
                'class': 'FALKNER',
                'number': 1,
                'name': 'Falkner',
            },
            {
                'class': 'BUGSY',
                'number': 1,
                'name': 'Bugsy',
            },
            {
                'class': 'WHITNEY',
                'number': 1,
                'name': 'Whitney',
            },
            {
                'class': 'MORTY',
                'number': 1,
                'name': 'Morty',
            },
            {
                'class': 'CHUCK',
                'number': 1,
                'name': 'Chuck',
            },
            {
                'class': 'PRYCE',
                'number': 1,
                'name': 'Pryce',
            },
            {
                'class': 'JASMINE',
                'number': 1,
                'name': 'Jasmine',
            },
            {
                'class': 'CLAIR',
                'number': 1,
                'name': 'Clair',
            },
            {
                'class': 'CHAMPION',
                'number': 1,
                'name': 'Champion',
            },
            {
                'class': 'BROCK',
                'number': 1,
                'name': 'Brock',
            },
            {
                'class': 'MISTY',
                'number': 1,
                'name': 'Misty',
            },
            {
                'class': 'LT. SURGE',
                'number': 1,
                'name': 'Lt. Surge',
            },
            {
                'class': 'ERIKA',
                'number': 1,
                'name': 'Erika',
            },
            {
                'class': 'JANINE',
                'number': 1,
                'name': 'Janine',
            },
            {
                'class': 'SABRINA',
                'number': 1,
                'name': 'Sabrina',
            },
            {
                'class': 'BLAINE',
                'number': 1,
                'name': 'Blaine',
            },
            {
                'class': 'BLUE',
                'number': 1,
                'name': 'Blue',
            },
            {
                'class': 'RED',
                'number': 1,
                'name': 'Red',
            },
        ],
    },
}

###############################################################################
# Helper Classes
###############################################################################


@define
class PreviousData:
    badges: BadgeData
    team: TrainerParty
    money: int
    time: GameTime

    @classmethod
    def from_data(cls, data: GameData) -> 'PreviousData':
        return cls(
            data.player.badges.copy(),
            data.player.team.copy(),
            data.player.money,
            data.time.copy(),
        )


@define
class TrackedBattle:
    trainer_class: str
    trainer_id: int
    trainer_name: str
    realtime: TimeInterval
    previous: PreviousData

    @property
    def key(self) -> str:
        return f'{self.trainer_class}/{self.trainer_id}'

    @classmethod
    def from_data(cls, data: GameData, name: str, t: TimeRecord) -> 'TrackedBattle':
        tc = data.battle.trainer.trainer_class
        tid = data.battle.trainer.number
        prev = PreviousData.from_data(data)
        rt = TimeInterval(start=t)
        return cls(tc, tid, name, rt, prev)


@define
class OutputHandler:
    attributes: List[str] = field(validator=instance_of(list))
    labels: Mapping[str, str] = field(validator=instance_of(dict))
    records: List[BattleRecord] = field(init=False, factory=list, eq=False, repr=False)

    @classmethod
    def from_settings(
        cls,
        settings: Mapping[str, Any],
        data: Mapping[str, Any],
        default_labels: Mapping[str, str],
    ) -> 'OutputHandler':
        attributes = settings.get('attributes', [])
        labels = dict(default_labels)
        labels.update(settings.get('labels', {}))
        return cls(attributes=attributes, labels=labels)

    def cleanup(self):
        pass

    def add_record(self, data: SimpleNamespace):
        rec = [Attribute.of(data, attr).get() for attr in self.attributes]
        self.records.append(rec)

    def store_records(self):
        # to override
        for rec in self.records:
            logger.debug(f'store record: {rec}')


@define
class CsvHandler(OutputHandler):
    filepath: Path = field(default=Path('splits.csv'), validator=instance_of(Path))

    @classmethod
    def from_settings(
        cls,
        settings: Mapping[str, Any],
        data: Mapping[str, Any],
        default_labels: Mapping[str, str],
    ) -> 'CsvHandler':
        filepath = Path(settings.get('path', 'splits.csv').format(**data))
        attributes = settings.get('attributes', [])
        labels = dict(default_labels)
        labels.update(settings.get('labels', {}))
        return cls(attributes=attributes, labels=labels, filepath=filepath)

    def store_records(self):
        if self.records:
            try:
                if not self.filepath.exists():
                    self._write_headers()
                self._write_contents()
                self.records = []
            except OSError as e:
                logger.error(f'unable to write to {self.filepath}: {e}')

    def _write_headers(self):
        logger.debug(f'write CSV headers for {self.filepath}')
        headers = list(map(lambda k: self.labels.get(k, k), self.attributes))
        text = ','.join(headers) + '\n'
        self.filepath.write_text(text, encoding='utf-8')

    def _write_contents(self):
        contents = list(','.join(map(str, r)) for r in self.records)
        contents.append('')
        text = '\n'.join(contents)
        logger.debug(f'write CSV entries:\n{text}')
        with self.filepath.open(mode='a', encoding='utf-8') as f:
            f.write(text)


@define
class WebSocketHandler(OutputHandler):
    host: str = field(default='localhost', validator=instance_of(str))
    port: int = field(default=6789, validator=instance_of(int))
    loop: asyncio.AbstractEventLoop = field(factory=asyncio.new_event_loop)
    history: List[BattleRecord] = field(init=False, factory=list, eq=False, repr=False)
    clients: Set[Any] = field(init=False, factory=set, eq=False, repr=False)

    def __attrs_post_init__(self):
        logger.debug(f'initializing websocket server on {self.host}:{self.port}')
        # t = Thread(target=start_background_loop, args=(self.loop,), daemon=True)
        t = Thread(target=self._start_background_loop, daemon=True)
        t.start()
        asyncio.run_coroutine_threadsafe(self._run_websocket_server(), self.loop)

    @classmethod
    def from_settings(
        cls,
        settings: Mapping[str, Any],
        data: Mapping[str, Any],
        default_labels: Mapping[str, str],
    ) -> 'WebSocketHandler':
        host = settings.get('host', 'localhost')
        port = settings.get('port', 6789)
        attributes = settings.get('attributes', [])
        labels = dict(default_labels)
        labels.update(settings.get('labels', {}))
        return cls(attributes=attributes, labels=labels, host=host, port=port)

    def cleanup(self):
        self.loop.stop()

    def store_records(self):
        # manipulate collections while the main thread is holding the lock
        if self.records:
            print(f'[MAIN][{get_native_id()}] store records')
            records = self.records
            self.records = []
            logger.debug(f'broadcasting new splits to clients:\n{records}')
            task = asyncio.run_coroutine_threadsafe(self._broadcast(records), self.loop)
            # do not wait for result
            # r = task.result()
            self.history.extend(records)
            print(f'[MAIN][{get_native_id()}] store records done')

    async def _broadcast(self, records):
        # It is probably better to call send asynchronously on each connection.
        # From websockets docs:
        #   `broadcast()` pushes the message synchronously to all connections
        #   even if their write buffers are overflowing.
        # With send we can yield control and ensure async execution.
        print(f'[THREAD][{get_native_id()}] broadcast records')
        for record in records:
            payload = self._record_to_json(record)
            # websockets.broadcast(self.clients, message)
            for websocket in self.clients:
                await self._send_message(payload, websocket)

    def _start_background_loop(self):
        print(f'[THREAD][{get_native_id()}] starting')
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    async def _run_websocket_server(self):
        print(f'[THREAD][{get_native_id()}] running server')
        stop = self.loop.create_future()
        try:
            async with websockets.serve(self._connection_handler, self.host, self.port):
                # await asyncio.Future()  # run forever
                await stop
        except GeneratorExit:
            print(f'[THREAD][{get_native_id()}] GeneratorExit - server closed')

    async def _connection_handler(self, websocket):
        print(f'[THREAD][{get_native_id()}] new connection')
        self.clients.add(websocket)
        try:
            # send initial data
            records = list(self.history)
            print(f'[THREAD][{get_native_id()}] send history')
            for record in records:
                payload = self._record_to_json(record)
                await self._send_message(payload, websocket)
            # keep the connection open
            print(f'[THREAD][{get_native_id()}] keep connection open')
            # await websocket.wait_closed()
            async for msg in websocket:
                pass  # keep alive mechanism

            # NOTE: the except below is needed if we do a websocket.recv() loop
            # instead of websocket.wait_closed()
        # except websockets.ConnectionClosedOK:
        #     pass
        finally:
            self.clients.remove(websocket)

    async def _send_message(self, payload, websocket):
        print(f'[THREAD][{get_native_id()}] send message')
        try:
            print(f'[THREAD][{get_native_id()}] send message (send)')
            await websocket.send(payload)
            print(f'[THREAD][{get_native_id()}] send message (sleep)')
            await asyncio.sleep(0)
        except websockets.ConnectionClosed:
            pass
        print(f'[THREAD][{get_native_id()}] send message (done)')

    def _record_to_json(self, record: BattleRecord) -> str:
        data = {}
        print(f'[THREAD][{get_native_id()}] record to JSON')
        for i, key in enumerate(self.attributes):
            label = self.labels.get(key, key)
            data[label] = str(record[i])
        print(f'[THREAD][{get_native_id()}] record to JSON (done)')
        print(data)
        return json.dumps(data)


###############################################################################
# Interface
###############################################################################


@define
class SplitComponent:
    game: GameInterface
    trainers: Mapping[str, Mapping[int, str]] = field(factory=dict)
    default_labels: Mapping[str, str] = field(factory=dict)
    _tracked: Optional[TrackedBattle] = field(init=False, default=None, eq=False, repr=False)
    _lock: Lock = field(init=False, factory=Lock, eq=False, repr=False)
    _resets: Counter = field(init=False, factory=Counter, eq=False, repr=False)
    _outputs: List[OutputHandler] = field(init=False, factory=list, eq=False, repr=False)

    def setup(self, settings: Mapping[str, Any]):
        logger.info('setting up')
        self.trainers = defaultdict(dict)
        trainers = settings['trainers'].get(self.game.version, ())
        if isinstance(trainers, str):  # alias
            trainers = settings['trainers'][trainers]
        for trainer in trainers:
            self._register_trainer(trainer)
        self.default_labels = settings.get('labels', {})
        self._setup_output_handlers(settings)
        on_battle_started.watch(self.on_battle_started)
        on_battle_ended.watch(self.on_battle_ended)
        on_reset.watch(self.on_reset)

    def start(self):
        logger.info('starting')
        return

    def update(self, _delta):
        # runs in main thread
        with self._lock:
            for handler in self._outputs:
                handler.store_records()

    def cleanup(self):
        # runs in main thread
        logger.info('cleaning up')
        with self._lock:
            for handler in self._outputs:
                handler.cleanup()

    def on_battle_started(self):
        battle = self.game.data.battle
        if not battle.is_vs_wild:
            trainer_class = battle.trainer.trainer_class
            trainers = self.trainers[trainer_class]
            trainer_id = battle.trainer.number
            name = trainers.get(trainer_id)
            if name is not None:
                logger.info(f'track battle vs {name} ({trainer_class} {trainer_id})')
                t = self.game.clock.get_current_time()
                assert self._tracked is None
                self._tracked = TrackedBattle.from_data(self.game.data, name, t)

    def on_battle_ended(self):
        if self._tracked is None:
            return
        name = self._tracked.trainer_name
        trainer_class = self._tracked.trainer_class
        trainer_id = self._tracked.trainer_id
        time_start = self._tracked.realtime.start
        time_end = self.game.clock.get_current_time()
        self._tracked.realtime.end = time_end
        duration = time_end - time_start
        game_time = self.game.data.time
        logger.info(f'end of tracked battle vs {name} ({trainer_class} {trainer_id})')
        logger.info(f'split time - {time_end}')
        logger.info(f'game time  - {game_time}')
        if self.game.data.battle.is_victory:
            logger.info('result: victory')
            self._record_victory()
        elif self.game.data.battle.is_defeat:
            logger.info('result: defeat')
            self._record_failure()
        else:
            logger.info('result: draw')
        self._tracked = None

    def on_reset(self):
        if self._tracked is not None:
            logger.info('failed attempt: detected game reset')
            self._record_failure()
            self._tracked = None

    def _register_trainer(self, data: Mapping[str, Any]):
        trainer_class = data['class']
        trainer_id = data['number']
        name = data['name']
        logger.debug(f'watch trainer battle: {trainer_class} {trainer_id} ({name})')
        trainers = self.trainers[trainer_class]
        previous = trainers.get(trainer_id)
        if previous is not None:
            logger.warning(f'multiple entries for {trainer_class} {trainer_id}: {previous} {name}')
        trainers[trainer_id] = name

    def _setup_output_handlers(self, settings: Mapping[str, Any]):
        self._outputs = []
        output = settings.get('output')
        if output is None:
            return
        if not isinstance(output, dict):
            logger.error(f'"output" should be a mapping, found {type(output)}')
            return

        data = self.game.data_dict()

        conf = output.get('csv')
        if conf is not None:
            try:
                handler = CsvHandler.from_settings(conf, data, self.default_labels)
                self._outputs.append(handler)
            except TypeError as e:
                logger.error(str(e))

        conf = output.get('websocket')
        if conf is not None:
            try:
                handler = WebSocketHandler.from_settings(conf, data, self.default_labels)
                self._outputs.append(handler)
            except TypeError as e:
                logger.error(str(e))

    def _record_victory(self):
        assert self._tracked is not None
        data = self.game.data_dict()
        data.update(asdict(self._tracked, recurse=False))
        data['resets'] = self._resets[self._tracked.key]
        ns = SimpleNamespace(**data)
        with self._lock:
            for handler in self._outputs:
                handler.add_record(ns)

    def _record_failure(self):
        assert self._tracked is not None
        self._resets[self._tracked.key] += 1


def new(game: GameInterface) -> SplitComponent:
    instance = SplitComponent(game)
    return instance


def default_settings() -> Mapping[str, Any]:
    return dict(DEFAULTS)
