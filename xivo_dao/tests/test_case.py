# Copyright 2014-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest


class TestCase(unittest.TestCase):

    def assertNotCalled(self, callee):
        assert callee.call_count == 0, f"{callee} was called {callee.call_count:d} times"
