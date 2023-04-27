# SPDX-License-Identifier: MIT
# Copyright © 2023 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

from collections import defaultdict

from pokewatcher.core.util import Attribute
from pokewatcher.data.structs import GameData

###############################################################################
# Data Structures
###############################################################################


def test_asdict_converts_defaultdict():
    data = GameData()
    attr = Attribute.of(data, 'custom.x.y')
    attr.set(42)
    assert attr.get() == 42
    assert isinstance(data.custom['x'], defaultdict)
    data = data.serialize()
    assert not isinstance(data['custom']['x'], defaultdict)
    assert isinstance(data['custom']['x'], dict)
