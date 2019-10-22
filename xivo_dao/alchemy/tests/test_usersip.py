# -*- coding: utf-8 -*-
# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    has_properties,
)

from xivo_dao.tests.test_dao import DAOTestCase


class TestUserSIP(DAOTestCase):

    def test_exclude_options_confd_ignore_options_key(self):
        exclude_options_confd = {
            'name': 'foo',
            'username': 'foobar',
            'secret': 's3cret',
            'type': 'peer',
            'host': 'my-host',
            'context': 'my-context',
            'category': 'user',
            'protocol': 'sip',
        }

        body = dict(exclude_options_confd)
        body['options'] = []
        sip = self.add_usersip(**body)

        assert_that(sip, has_properties(exclude_options_confd))
