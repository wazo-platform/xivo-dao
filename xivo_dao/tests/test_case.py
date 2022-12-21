# Copyright 2014-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest


class TestCase(unittest.TestCase):

    def assertNotCalled(self, callee):
        self.assertEqual(callee.call_count, 0,
                         "%s was called %d times" % (callee, callee.call_count))
