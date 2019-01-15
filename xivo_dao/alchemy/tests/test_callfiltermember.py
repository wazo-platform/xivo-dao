# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from hamcrest import (
    assert_that,
    equal_to,
    none,
)

from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.resources.func_key.tests.test_helpers import FuncKeyHelper

from ..callfiltermember import Callfiltermember as CallFilterMember
from ..func_key_dest_bsfilter import FuncKeyDestBSFilter


class TestUser(DAOTestCase):

    def test_associate(self):
        user = self.add_user()
        member = self.add_call_filter_member(type='user')

        member.user = user
        self.session.flush()

        self.session.expire_all()
        assert_that(member.user, equal_to(user))

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


class TestDelete(DAOTestCase, FuncKeyHelper):

    def setUp(self):
        super(TestDelete, self).setUp()
        self.setup_funckeys()

    def test_funckeys_are_deleted(self):
        call_filter = self.add_call_filter()
        filter_member = self.add_call_filter_member(callfilterid=call_filter.id)
        self.add_bsfilter_destination(filter_member.id)

        self.session.delete(call_filter)
        self.session.flush()

        row = self.session.query(FuncKeyDestBSFilter).first()
        assert_that(row, none())
