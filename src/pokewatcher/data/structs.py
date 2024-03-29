# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Any, Dict, Final, List, Optional, Tuple

from collections import defaultdict
import logging

from attrs import asdict, define, field

###############################################################################
# Constants
###############################################################################

logger: Final[logging.Logger] = logging.getLogger(__name__)

BATTLE_RESULT_WIN: Final[int] = 1
BATTLE_RESULT_DRAW: Final[int] = 0
BATTLE_RESULT_LOSE: Final[int] = -1

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
    def special(self, value: int):
        self.sp_attack = value
        self.sp_defense = value

    def copy(self) -> 'MonStats':
        return MonStats(
            hp=self.hp,
            attack=self.attack,
            defense=self.defense,
            speed=self.speed,
            sp_attack=self.sp_attack,
            sp_defense=self.sp_defense,
        )


@define
class MonSpecies:
    dex_number: int
    name: str
    base_stats: MonStats = field(factory=MonStats)


@define
class PartyMon:
    species: str = ''
    name: str = ''
    level: int = 1
    stats: MonStats = field(factory=MonStats)
    hp: int = -1
    move1: str = ''
    move2: str = ''
    move3: str = ''
    move4: str = ''

    def __attrs_post_init__(self):
        if self.hp < 0:
            self.hp = self.stats.hp

    @property
    def max_hp(self) -> int:
        return self.stats.hp

    @max_hp.setter
    def max_hp(self, value: int):
        self.stats.hp = value

    @property
    def is_valid_species(self) -> bool:
        return self.species != ''

    def copy(self) -> 'PartyMon':
        return PartyMon(
            species=self.species,
            name=self.name,
            level=self.level,
            stats=self.stats.copy(),
            hp=self.hp,
            move1=self.move1,
            move2=self.move2,
            move3=self.move3,
            move4=self.move4,
        )


@define
class TrainerParty:
    size: int = 0
    slot1: PartyMon = field(factory=PartyMon)
    slot2: PartyMon = field(factory=PartyMon)
    slot3: PartyMon = field(factory=PartyMon)
    slot4: PartyMon = field(factory=PartyMon)
    slot5: PartyMon = field(factory=PartyMon)
    slot6: PartyMon = field(factory=PartyMon)

    @property
    def slots(self) -> Tuple[PartyMon]:
        return (self.slot1, self.slot2, self.slot3, self.slot4, self.slot5, self.slot6)

    def as_list(self) -> List[PartyMon]:
        return list(self.slots[: self.size])

    @property
    def lead(self) -> PartyMon:
        return self.slot1

    @property
    def last(self) -> PartyMon:
        return self.slot6

    def copy(self) -> 'TrainerParty':
        return TrainerParty(
            size=self.size,
            slot1=self.slot1.copy(),
            slot2=self.slot2.copy(),
            slot3=self.slot3.copy(),
            slot4=self.slot4.copy(),
            slot5=self.slot5.copy(),
            slot6=self.slot6.copy(),
        )

    def __getitem__(self, i: int) -> PartyMon:
        return self.slots[i]

    def __len__(self) -> int:
        return self.size


###############################################################################
# Battle Pokémon Data
###############################################################################


@define
class TrainerData:
    name: str = ''
    number: int = 0
    trainer_class: str = ''
    team: TrainerParty = field(factory=TrainerParty)

    @property
    def lead(self) -> PartyMon:
        return self.team.lead

    def reset(self):
        self.name = ''
        self.number = 0
        self.trainer_class = ''
        self.team.size = 0


@define
class BattleMonStatStages:
    attack: int = 0
    defense: int = 0
    speed: int = 0
    sp_attack: int = 0
    sp_defense: int = 0
    accuracy: int = 0
    evasion: int = 0

    @property
    def special(self) -> int:
        return self.sp_attack

    @special.setter
    def special(self, value: int):
        self.sp_attack = value
        self.sp_defense = value


@define
class BattleMon:
    name: str = ''
    hp: int = -1
    stats: MonStats = field(factory=MonStats)
    stages: BattleMonStatStages = field(factory=BattleMonStatStages)
    party_index: int = 0


@define
class BattleData:
    ongoing: bool = False
    is_vs_wild: bool = False
    result: int = BATTLE_RESULT_WIN
    player: BattleMon = field(factory=BattleMon)
    enemy: BattleMon = field(factory=BattleMon)
    trainer: TrainerData = field(factory=TrainerData)

    @property
    def is_victory(self) -> bool:
        return not self.ongoing and self.result == BATTLE_RESULT_WIN

    @property
    def is_draw(self) -> bool:
        return not self.ongoing and self.result == BATTLE_RESULT_DRAW

    @property
    def is_defeat(self) -> bool:
        return not self.ongoing and self.result == BATTLE_RESULT_LOSE

    def set_wild_battle(self):
        self.ongoing = True
        self.is_vs_wild = True
        self.result = BATTLE_RESULT_DRAW

    def set_trainer_battle(self):
        self.ongoing = True
        self.is_vs_wild = False
        self.result = BATTLE_RESULT_DRAW

    def set_victory(self):
        self.ongoing = False
        self.result = BATTLE_RESULT_WIN

    def set_defeat(self):
        self.ongoing = False
        self.result = BATTLE_RESULT_LOSE

    def set_draw(self):
        self.ongoing = False
        self.result = BATTLE_RESULT_DRAW


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

    def copy(self) -> 'BadgeData':
        return BadgeData(
            badge1=self.badge1,
            badge2=self.badge2,
            badge3=self.badge3,
            badge4=self.badge4,
            badge5=self.badge5,
            badge6=self.badge6,
            badge7=self.badge7,
            badge8=self.badge8,
        )

    def __getitem__(self, i: Any) -> bool:
        if i == 0 or i == 'badge1':
            return self.badge1
        if i == 1 or i == 'badge2':
            return self.badge2
        if i == 2 or i == 'badge3':
            return self.badge3
        if i == 3 or i == 'badge4':
            return self.badge4
        if i == 4 or i == 'badge5':
            return self.badge5
        if i == 5 or i == 'badge6':
            return self.badge6
        if i == 6 or i == 'badge7':
            return self.badge7
        if i == 7 or i == 'badge8':
            return self.badge8
        raise IndexError(f'expected 0 <= i < 8; got {i}')

    def __setitem__(self, i: Any, value: bool):
        if i == 0 or i == 'badge1':
            self.badge1 = value
        elif i == 1 or i == 'badge2':
            self.badge2 = value
        elif i == 2 or i == 'badge3':
            self.badge3 = value
        elif i == 3 or i == 'badge4':
            self.badge4 = value
        elif i == 4 or i == 'badge5':
            self.badge5 = value
        elif i == 5 or i == 'badge6':
            self.badge6 = value
        elif i == 6 or i == 'badge7':
            self.badge7 = value
        elif i == 7 or i == 'badge8':
            self.badge8 = value
        else:
            raise IndexError(f'expected 0 <= i < 8; got {i}')

    def __len__(self) -> int:
        return 8


@define
class PlayerData:
    name: str = ''
    number: int = -1
    badges: BadgeData = field(factory=BadgeData)
    team: TrainerParty = field(factory=TrainerParty)
    money: int = 0

    @property
    def lead(self) -> PartyMon:
        return self.team.lead

    def copy(self) -> 'PlayerData':
        return PlayerData(
            name=self.name,
            number=self.number,
            badges=self.badges.copy(),
            team=self.team.copy(),
            money=self.money,
        )


###############################################################################
# Map Data
###############################################################################


@define
class GameMap:
    name: str
    group: str
    is_indoors: bool = False
    is_gym: bool = False

    @property
    def uid(self) -> str:
        return f'{self.group}/{self.name}'

    @staticmethod
    def make_uid(group: str, name: str) -> str:
        return f'{group}/{name}'


###############################################################################
# Game Data
###############################################################################


@define
class GameTime:
    hours: int = 0
    minutes: int = 0
    seconds: int = 0
    frames: int = 0

    def copy(self) -> 'GameTime':
        return GameTime(
            hours=self.hours,
            minutes=self.minutes,
            seconds=self.seconds,
            frames=self.frames,
        )

    def formatted(self, zeroes: bool = True, frames: bool = True) -> str:
        t = f'{self.seconds:02}' if not frames else f'{self.seconds:02}.{self.frames:02}'
        if not zeroes:
            if self.hours == 0:
                return t if self.minutes == 0 else f'{self.minutes:02}:{t}'
        return f'{self.hours:02}:{self.minutes:02}:{t}'

    def __str__(self) -> str:
        return self.formatted(zeroes=True, frames=True)


def dict_of_dicts() -> Dict[str, Any]:
    return defaultdict(dict_of_dicts)


@define
class GameData:
    player: PlayerData = field(factory=PlayerData)
    time: GameTime = field(factory=GameTime)
    location: str = ''
    battle: BattleData = field(factory=BattleData)
    dex: List[MonSpecies] = field(factory=list, repr=False)
    maps: Dict[str, GameMap] = field(factory=dict, repr=False)
    custom: Dict[str, Any] = field(factory=dict_of_dicts)

    @property
    def current_map(self) -> Optional[GameMap]:
        return self.maps.get(self.location)

    @property
    def is_in_battle(self) -> bool:
        return self.battle.ongoing

    def serialize(self) -> Dict[str, Any]:
        return asdict(self)
