# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from typing import Any, Final

import logging

from attrs import define

import pokewatcher.events as events

###############################################################################
# Constants
###############################################################################

logger: Final[logging.Logger] = logging.getLogger(__name__)

###############################################################################
# Interface
###############################################################################


@define
class BattleState:
    def on_battle_type_changed(self, value: str) -> 'BattleState':
        return self

    def on_low_health_alarm_changed(self, value: str) -> 'BattleState':
        return self


@define
class OutOfBattle(BattleState):
    def on_battle_type_changed(self, value: str) -> BattleState:
        if value == self.BATTLE_TYPE_WILD:
            self.data.battle.trainer.number = 0
            self.data.battle.trainer.trainer_class = ''
            events.on_battle_started.emit()
            return InBattle()
        elif value == self.BATTLE_TYPE_TRAINER:
            events.on_battle_started.emit()
            return InBattle()
        elif value == self.BATTLE_TYPE_LOST:
            self.data.battle.ongoing = False
            self.data.battle.result = 'Lost'
            events.on_battle_ended.emit()
        return self

    def on_low_health_alarm_changed(self, value: str) -> BattleState:
        if value == ALARM_DISABLED:
            logger.error('detected battle end but monitor is not in battle state')
        return self


@define
class InBattle(BattleState):
    def on_battle_type_changed(self, value: str) -> BattleState:
        return self

    def on_low_health_alarm_changed(self, value: str) -> BattleState:
        if value == ALARM_DISABLED:
            self.data.battle.ongoing = False
            self.data.battle.result = 'Victory'
            events.on_battle_ended.emit()
            return VictorySequence()
        return self


@define
class VictorySequence(BattleState):
    def on_battle_type_changed(self, value: str) -> BattleState:
        return self
