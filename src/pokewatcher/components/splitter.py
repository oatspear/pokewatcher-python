# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Any, Final, Mapping, Optional

from collections import defaultdict
import logging

from attrs import define, field

from pokewatcher.core.game import GameInterface
from pokewatcher.core.util import TimeRecord
from pokewatcher.events import on_battle_ended, on_battle_started, on_reset

###############################################################################
# Constants
###############################################################################

logger: Final = logging.getLogger(__name__)


###############################################################################
# Helper Classes
###############################################################################


@define
class TrackedBattle:
    trainer_class: str
    trainer_id: int
    trainer_name: str
    time_start: TimeRecord


###############################################################################
# Interface
###############################################################################


@define
class SplitComponent:
    game: GameInterface
    trainers: Mapping[str, Mapping[int, str]] = field(factory=dict)
    tracked: Optional[TrackedBattle] = None

    def setup(self, settings: Mapping[str, Any]):
        logger.info('setting up')
        self.trainers = defaultdict(dict)
        for trainer in settings['trainers'].get(self.game.version, ()):
            self._register_trainer(trainer)
        on_battle_started.watch(self.on_battle_started)
        on_battle_ended.watch(self.on_battle_ended)
        on_reset.watch(self.on_reset)

    def start(self):
        logger.info('starting')
        return

    def update(self, delta):
        # logger.debug('update')
        return

    def cleanup(self):
        logger.info('cleaning up')
        return

    def on_battle_started(self):
        battle = self.game.data.battle
        if not battle.is_vs_wild:
            trainer_class = battle.trainer.trainer_class
            trainers = self.trainers[trainer_class]
            trainer_id = battle.trainer.number
            name = trainers.get(trainer_id)
            if name is not None:
                logger.info(f'track battle vs {name} ({trainer_class} {trainer_id})')
                t = self.game.clock.get_elapsed_time()
                assert self.tracked is None
                self.tracked = TrackedBattle(trainer_class, trainer_id, name, t)

    def on_battle_ended(self):
        if self.tracked is None:
            return
        name = self.tracked.trainer_name
        trainer_class = self.tracked.trainer_class
        trainer_id = self.tracked.trainer_id
        time_start = self.tracked.time_start
        time_end = self.game.clock.get_elapsed_time()
        duration = time_end - time_start
        logger.info(f'end of tracked battle vs {name} ({trainer_class} {trainer_id})')
        logger.info(f'started at {time_start}, ended at {time_end}, lasted {duration}')
        if self.game.data.battle.is_victory:
            logger.info('result: victory')
        elif self.game.data.battle.is_defeat:
            logger.info('result: defeat')
        else:
            logger.info('result: draw')
        self.tracked = None

    def on_reset(self):
        if self.tracked is None:
            return
        # TODO
        self.tracked = None

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


def new(game: GameInterface):
    instance = SplitComponent(game)
    return instance
