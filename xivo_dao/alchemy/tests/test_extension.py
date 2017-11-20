# -*- coding: utf-8 -*-
# Copyright 2016 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import unittest

from hamcrest import assert_that, equal_to
from xivo_dao.alchemy.extension import Extension


class TestIsPattern(unittest.TestCase):

    def test_is_not_pattern(self):
        extension = Extension(exten='1000')
        assert_that(extension.is_pattern(), equal_to(False))

    def test_is_pattern(self):
        extension = Extension(exten='_XXXX')
        assert_that(extension.is_pattern(), equal_to(True))
