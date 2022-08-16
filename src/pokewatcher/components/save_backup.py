# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Any, Final, Mapping, Optional

import logging
from pathlib import Path
import shutil
import time

from attrs import define, field

from pokewatcher.core.game import GameInterface
from pokewatcher.core.util import SleepLoop
from pokewatcher.events import on_save_game

###############################################################################
# Constants
###############################################################################

logger: Final = logging.getLogger(__name__)

N_CHECKS: Final[int] = 5
FILE_CHECK_INTERVAL: Final[float] = 3.0  # seconds
MIN_BACKUP_INTERVAL: Final[float] = 1.0  # seconds
FILE_NAME_FORMAT: Final[str] = '{rom}-{realtime}-{location}.srm'

###############################################################################
# Interface
###############################################################################


@define
class SaveFileBackupComponent:
    game: GameInterface
    dirty: bool = False
    requested: bool = False
    n_checks: int = N_CHECKS
    check_interval: float = FILE_CHECK_INTERVAL
    min_backup_interval: float = MIN_BACKUP_INTERVAL
    file_name_format: str = FILE_NAME_FORMAT
    dest_dir: Path = field(factory=Path.cwd)
    _timestamp: float = field(init=False, default=0.0, eq=False, repr=False)
    _data: Mapping[str, Any] = field(init=False, factory=dict, eq=False, repr=False)
    _last_modified: float = 0.0

    def setup(self, settings: Mapping[str, Any]):
        logger.info('setting up')
        self.n_checks = settings.get('n_checks', N_CHECKS)
        self.check_interval = settings.get('check_interval', FILE_CHECK_INTERVAL)
        self.min_backup_interval = settings.get('min_backup_interval', MIN_BACKUP_INTERVAL)
        self.file_name_format = settings.get('file_name_format', FILE_NAME_FORMAT)
        self.dest_dir = Path(settings.get('dest_dir', '.')).resolve(strict=True)
        on_save_game.watch(self.on_save_game)

    def start(self):
        logger.info('starting')
        return

    def update(self, delta):
        # logger.debug('update')
        if self.requested:
            with SleepLoop(n=self.n_checks, delay=self.check_interval) as loop:
                while loop.iterate() and not self.dirty:
                    self.look_for_changes()
            self.do_backup()
        return

    def cleanup(self):
        logger.info('cleaning up')
        return

    def on_save_game(self):
        logger.info('player saved the game')
        # not thread-safe but should be ok, since many fields are static
        t = time.time()
        if (t - self._timestamp) < self.min_backup_interval:
            logger.info('skipping save file backup request: too recent')
            return  # discard too many requests in a short period

        save_file = self.save_file
        if save_file is None:
            logger.warning('unable to get save file path')
            return

        data = self.game.data_dict()

        data['location'] = data['location'].replace(' ', '').replace('-', '')

        if '{realtime}' in self.file_name_format:
            tr = self.game.clock.get_current_time()
            time_string = tr.formatted(zeroes=True, millis=True)
            time_string = time_string.replace(':', '').replace('.', '').rstrip()
            data['realtime'] = time_string

        try:
            self._last_modified = save_file.stat().st_mtime
        except FileNotFoundError:
            self._last_modified = 0

        logger.info('requesting save file backup')
        logger.debug(f'game data: {data}')
        self._data = data
        self._timestamp = t
        self.requested = True

    def look_for_changes(self):
        save_file = self.save_file
        if save_file is None:
            logger.warning('unable to get save file path')
            return

        try:
            stamp = save_file.stat().st_mtime
        except FileNotFoundError:
            stamp = 0
        if stamp > self._last_modified:
            self._last_modified = stamp
            self.dirty = True

    def do_backup(self):
        save_file = self.save_file
        if save_file is None:
            logger.warning('unable to get save file path')
            return

        if self.dirty:
            logger.info('detected changes to save file')
        else:
            logger.info('no changes to save file')

        self.dirty = False
        self.requested = False

        logger.info('create save file backup')
        filename = self.file_name_format.format(**self._data)
        dest_file = self.dest_dir / filename
        shutil.copy(save_file, dest_file)
        logger.info('save file backup complete')

    @property
    def save_file(self) -> Optional[Path]:
        d = self.game.retroarch.savefile_dir
        if d is None:
            return None
        rom = self.game.retroarch.rom
        if rom is None:
            return None
        return d / f'{rom}.srm'


def new(game: GameInterface):
    instance = SaveFileBackupComponent(game)
    return instance
