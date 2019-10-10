# -*- coding: utf-8 -*-
# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    equal_to,
)

from xivo_dao.tests.test_dao import DAOTestCase


class TestUserSIP(DAOTestCase):

    def test_setting_a_username_when_options_is_in_the_body(self):
        params = {'username': 'foobar', 'name': 'foo', 'options': []}

        sip = self.add_usersip(**params)

        assert_that(sip.username, equal_to('foobar'))
