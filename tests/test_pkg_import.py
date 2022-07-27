# SPDX-License-Identifier: MIT
# Copyright © 2022 André "Oatspear" Santos

###############################################################################
# Imports
###############################################################################

import pokewatcher

###############################################################################
# Tests
###############################################################################


def test_import_was_ok():
    assert True


def test_pkg_has_version():
    assert hasattr(pokewatcher, '__version__')
    assert isinstance(pokewatcher.__version__, str)
    assert pokewatcher.__version__ != ''

