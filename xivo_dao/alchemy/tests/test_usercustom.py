# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from hamcrest import (
    assert_that,
    equal_to,
    none,
)

from ..usercustom import UserCustom


class TestInterfaceSuffix(unittest.TestCase):

    def test_getter(self):
        custom = UserCustom(intfsuffix='toto')

        assert_that(custom.interface_suffix, equal_to('toto'))

    def test_getter_when_empty_string(self):
        custom = UserCustom(intfsuffix='')

        assert_that(custom.interface_suffix, none())

    def test_setter(self):
        custom = UserCustom(interface_suffix='toto')

        assert_that(custom.intfsuffix, equal_to('toto'))

    def test_setter_when_none(self):
        custom = UserCustom(interface_suffix=None)

        assert_that(custom.intfsuffix, equal_to(''))
