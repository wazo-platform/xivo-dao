# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import unittest

from hamcrest import (
    assert_that,
    equal_to,
    none,
)

from xivo_dao.tests.test_dao import DAOTestCase

from ..callfiltermember import Callfiltermember as CallFilterMember


class TestUser(DAOTestCase):

    def test_getter(self):
        user = self.add_user()
        member = self.add_call_filter_member(type='user', typeval=str(user.id))

        assert_that(member.user, equal_to(user))


class TestTimeout(unittest.TestCase):

    def test_getter(self):
        call_filter = CallFilterMember(ringseconds=10)
        assert_that(call_filter.timeout, equal_to(10))

    def test_getter_none(self):
        call_filter = CallFilterMember(ringseconds=0)
        assert_that(call_filter.timeout, none())

    def test_setter(self):
        call_filter = CallFilterMember(timeout=10)
        assert_that(call_filter.ringseconds, equal_to(10))

    def test_setter_none(self):
        call_filter = CallFilterMember(timeout=None)
        assert_that(call_filter.ringseconds, equal_to(0))
