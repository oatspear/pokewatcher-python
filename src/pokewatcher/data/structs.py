# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Any, Dict, Final, List, Optional

import logging

from attrs import define, field

###############################################################################
# Constants
###############################################################################

logger: Final[logging.Logger] = logging.getLogger(__name__)


###############################################################################
# General Purpose
###############################################################################


@define
class TimeStamp:
    hours: int = 0
    minutes: int = 0
    seconds: int = 0
    millis: int = 0

    def formatted(self, zeroes: bool = True, millis: bool = True) -> str:
        t = f'{self.seconds:02}' if not millis else f'{self.seconds:02}.{self.millis:03}'
        if not zeroes:
            if self.hours == 0:
                return t if self.minutes == 0 else f'{self.minutes:02}:{t}'
        return f'{self.hours:02}:{self.minutes:02}:{t}'


###############################################################################
# Pokémon Data
###############################################################################


@define
class MonStats:
    hp: int = 1
    attack: int = 1
    defense: int = 1
    speed: int = 1
    sp_attack: int = 1
    sp_defense: int = 1

    @property
    def special(self) -> int:
        return self.sp_attack

    @special.setter
    def _set_special(self, value: int):
        self.sp_attack = value
        self.sp_defense = value


@define
class MonSpecies:
    dex_number: int
    name: str
    base_stats: MonStats = field(factory=MonStats)


@define
class PartyMon:
    species: int = 1
    name: str = ''
    level: int = 1
    stats: MonStats = field(factory=MonStats)
    hp: int = -1

    def __attrs_post_init__(self):
        if self.hp < 0:
            self.hp = self.stats.hp

    @property
    def max_hp(self) -> int:
        return self.stats.hp

    @max_hp.setter
    def _set_max_hp(self, value: int):
        self.stats.hp = value


###############################################################################
# Battle Pokémon Data
###############################################################################


@define
class TrainerData:
    name: str = ''
    trainer_class: str = ''
    team: List[PartyMon] = field(factory=list)

    @property
    def lead(self) -> Optional[PartyMon]:
        return None if not self.team else self.team[0]


@define
class BattleMonStatStages:
    attack: int = 0
    defense: int = 0
    speed: int = 0
    sp_attack: int = 0
    sp_defense: int = 0
    accuracy: int = 0
    evasion: int = 0


@define
class BattleMon:
    name: str
    hp: int = -1
    stats: MonStats = field(factory=MonStats)
    stages: BattleMonStatStages = field(factory=BattleMonStatStages)
    party_index: int = 0


@define
class BattleData:
    player: BattleMon
    enemy: BattleMon
    trainer: Optional[TrainerData] = None

    @property
    def is_vs_wild(self) -> bool:
        return self.trainer is None


###############################################################################
# Player Data
###############################################################################


@define
class BadgeData:
    badge1: bool = False
    badge2: bool = False
    badge3: bool = False
    badge4: bool = False
    badge5: bool = False
    badge6: bool = False
    badge7: bool = False
    badge8: bool = False

    def __getitem__(self, i: Any):
        if i == 0:
            return self.badge1
        if i == 1:
            return self.badge2
        if i == 2:
            return self.badge3
        if i == 3:
            return self.badge4
        if i == 4:
            return self.badge5
        if i == 5:
            return self.badge6
        if i == 6:
            return self.badge7
        if i == 7:
            return self.badge8
        raise IndexError(f'expected 0 <= i < 8; got {i}')

    def __setitem__(self, i: Any, value: bool):
        if i == 0:
            self.badge1 = value
        elif i == 1:
            self.badge2 = value
        elif i == 2:
            self.badge3 = value
        elif i == 3:
            self.badge4 = value
        elif i == 4:
            self.badge5 = value
        elif i == 5:
            self.badge6 = value
        elif i == 6:
            self.badge7 = value
        elif i == 7:
            self.badge8 = value
        else:
            raise IndexError(f'expected 0 <= i < 8; got {i}')

    def __len__(self) -> int:
        return 8


@define
class PlayerData:
    name: str = ''
    number: int = 0
    badges: BadgeData = field(factory=BadgeData)
    team: List[PartyMon] = field(factory=list)
    money: int = 0

    @property
    def lead(self) -> Optional[PartyMon]:
        return None if not self.team else self.team[0]


###############################################################################
# Map Data
###############################################################################


@define
class GameMap:
    name: str
    is_indoors: bool = False
    is_gym: bool = False


###############################################################################
# Game Data
###############################################################################


@define
class GameTime:
    hours: int = 0
    minutes: int = 0
    seconds: int = 0
    frames: int = 0

    def formatted(self, zeroes: bool = True, frames: bool = True) -> str:
        t = f'{self.seconds:02}' if not frames else f'{self.seconds:02}.{self.frames:02}'
        if not zeroes:
            if self.hours == 0:
                return t if self.minutes == 0 else f'{self.minutes:02}:{t}'
        return f'{self.hours:02}:{self.minutes:02}:{t}'


@define
class GameData:
    player: PlayerData = field(factory=PlayerData)
    time: GameTime = field(factory=GameTime)
    location: str = ''
    dex: List[MonSpecies] = field(factory=list, repr=False)
    maps: Dict[str, GameMap] = field(factory=dict, repr=False)

    @property
    def current_map(self) -> Optional[GameMap]:
        return self.maps.get(self.location)

    # def set(self, attr: str, value: Any, emit: bool = False):
    #     parts = attr.split('.')
    #     holder = self
    #     for part in parts[:-1]:
    #         holder = getattr(holder, part)
    #     prev = getattr(holder, parts[-1])
    #     setattr(holder, parts[-1], value)
    #     if emit:
    #         self.on_change.emit(attr, prev, value, self)