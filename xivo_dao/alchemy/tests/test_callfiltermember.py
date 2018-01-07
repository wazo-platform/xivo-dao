# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from hamcrest import assert_that, equal_to

from xivo_dao.tests.test_dao import DAOTestCase


class TestUser(DAOTestCase):

    def test_getter(self):
        user = self.add_user()
        member = self.add_call_filter_member(type='user', typeval=str(user.id))

        assert_that(member.user, equal_to(user))
