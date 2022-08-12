# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Any, Dict, Final, List, Optional, Tuple

import logging

from attrs import asdict, field, frozen

from pokewatcher.data.abstract import VarBool, Variable, VarInt, VarString
from pokewatcher.data.structs import GameMap, MonSpecies

###############################################################################
# Constants
###############################################################################

logger: Final[logging.Logger] = logging.getLogger(__name__)

###############################################################################
# Pokémon Data
###############################################################################


@frozen
class MonStats:
    hp: VarInt = field(factory=VarInt.one, converter=VarInt)
    attack: VarInt = field(factory=VarInt.one, converter=VarInt)
    defense: VarInt = field(factory=VarInt.one, converter=VarInt)
    speed: VarInt = field(factory=VarInt.one, converter=VarInt)
    sp_attack: VarInt = field(factory=VarInt.one, converter=VarInt)
    sp_defense: VarInt = field(factory=VarInt.one, converter=VarInt)

    @property
    def special(self) -> VarInt:
        return self.sp_attack


@frozen
class PartyMon:
    species: VarInt = field(factory=VarInt.zero, converter=VarInt)
    name: VarString = field(factory=VarString.empty, converter=VarString)
    level: VarInt = field(factory=VarInt.one, converter=VarInt)
    stats: MonStats = field(factory=MonStats)
    hp: VarInt = field(factory=VarInt.minus_one, converter=VarInt)

    def __attrs_post_init__(self):
        if self.hp.value < 0:
            self.hp.set(self.stats.hp.value)

    @property
    def max_hp(self) -> VarInt:
        return self.stats.hp

    @property
    def is_valid_species(self) -> bool:
        return self.species.value > 0


@frozen
class TrainerParty:
    size: VarInt = field(factory=VarInt.zero, converter=VarInt)
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
        return list(self.slots[:self.size])

    @property
    def lead(self) -> PartyMon:
        return self.slot1

    @property
    def last(self) -> PartyMon:
        return self.slot6

    def __getitem__(self, i: int) -> PartyMon:
        return self.slots[i]

    def __len__(self) -> int:
        return self.size


###############################################################################
# Battle Pokémon Data
###############################################################################


@frozen
class TrainerData:
    name: VarString = field(factory=VarString.empty, converter=VarString)
    trainer_class: VarString = field(factory=VarString.empty, converter=VarString)
    team: TrainerParty = field(factory=TrainerParty)

    @property
    def lead(self) -> PartyMon:
        return self.team.lead


@frozen
class BattleMonStatStages:
    attack: VarInt = field(factory=VarInt.zero, converter=VarInt)
    defense: VarInt = field(factory=VarInt.zero, converter=VarInt)
    speed: VarInt = field(factory=VarInt.zero, converter=VarInt)
    sp_attack: VarInt = field(factory=VarInt.zero, converter=VarInt)
    sp_defense: VarInt = field(factory=VarInt.zero, converter=VarInt)
    accuracy: VarInt = field(factory=VarInt.zero, converter=VarInt)
    evasion: VarInt = field(factory=VarInt.zero, converter=VarInt)


@frozen
class BattleMon:
    name: VarString = field(converter=VarString)
    hp: VarInt = field(factory=VarInt.minus_one, converter=VarInt)
    stats: MonStats = field(factory=MonStats)
    stages: BattleMonStatStages = field(factory=BattleMonStatStages)
    party_index: VarInt = field(factory=VarInt.zero, converter=VarInt)


@frozen
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


@frozen
class BadgeData:
    badge1: VarBool = field(factory=VarBool.false, converter=VarBool)
    badge2: VarBool = field(factory=VarBool.false, converter=VarBool)
    badge3: VarBool = field(factory=VarBool.false, converter=VarBool)
    badge4: VarBool = field(factory=VarBool.false, converter=VarBool)
    badge5: VarBool = field(factory=VarBool.false, converter=VarBool)
    badge6: VarBool = field(factory=VarBool.false, converter=VarBool)
    badge7: VarBool = field(factory=VarBool.false, converter=VarBool)
    badge8: VarBool = field(factory=VarBool.false, converter=VarBool)

    def __getitem__(self, i: Any) -> VarBool:
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
            self.badge1.set(value)
        elif i == 1:
            self.badge2.set(value)
        elif i == 2:
            self.badge3.set(value)
        elif i == 3:
            self.badge4.set(value)
        elif i == 4:
            self.badge5.set(value)
        elif i == 5:
            self.badge6.set(value)
        elif i == 6:
            self.badge7.set(value)
        elif i == 7:
            self.badge8.set(value)
        else:
            raise IndexError(f'expected 0 <= i < 8; got {i}')

    def __len__(self) -> int:
        return 8


@frozen
class PlayerData:
    name: VarString = field(factory=VarString.empty, converter=VarString)
    number: VarInt = field(factory=VarInt.zero, converter=VarInt)
    badges: BadgeData = field(factory=BadgeData)
    team: TrainerParty = field(factory=TrainerParty)
    money: VarInt = field(factory=VarInt.zero, converter=VarInt)

    @property
    def lead(self) -> PartyMon:
        return self.team.lead


###############################################################################
# Game Data
###############################################################################


@frozen
class GameTime:
    hours: VarInt = field(factory=VarInt.zero, converter=VarInt)
    minutes: VarInt = field(factory=VarInt.zero, converter=VarInt)
    seconds: VarInt = field(factory=VarInt.zero, converter=VarInt)
    frames: VarInt = field(factory=VarInt.zero, converter=VarInt)

    def formatted(self, zeroes: bool = True, frames: bool = True) -> str:
        t = f'{self.seconds.value:02}'
        if frames:
            t = f'{t}.{self.frames.value:02}'
        if not zeroes:
            if self.hours.value == 0:
                return t if self.minutes.value == 0 else f'{self.minutes.value:02}:{t}'
        return f'{self.hours.value:02}:{self.minutes.value:02}:{t}'


@frozen
class GameData:
    player: PlayerData = field(factory=PlayerData)
    time: GameTime = field(factory=GameTime)
    location: VarString = field(factory=VarString.empty, converter=VarString)
    dex: List[MonSpecies] = field(factory=list, repr=False)
    maps: Dict[str, GameMap] = field(factory=dict, repr=False)

    @property
    def current_map(self) -> Optional[GameMap]:
        return self.maps.get(self.location.value)

    def serialize(self) -> Dict[str, Any]:
        return asdict(self, value_serializer=_serializer)


def _serializer(obj, attr, value):
    return value.value if isinstance(value, Variable) else value
