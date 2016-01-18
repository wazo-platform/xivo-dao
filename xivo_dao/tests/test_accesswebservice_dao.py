# -*- coding: utf-8 -*-

# Copyright (C) 2013-2016 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import random

from hamcrest import assert_that
from hamcrest import equal_to
from xivo_dao import accesswebservice_dao
from xivo_dao.alchemy.accesswebservice import AccessWebService
from xivo_dao.tests.test_dao import DAOTestCase


class TestAccessWebServiceDao(DAOTestCase):

    def test_get_password(self):
        access = self._insert_access_web_service()
        password = accesswebservice_dao.get_password(access.login)
        self.assertEqual(password, access.passwd)

    def test_get_password_not_exist(self):
        password = accesswebservice_dao.get_password('toto')
        self.assertEqual(password, None)

    def test_get_allowed_hosts(self):
        self._insert_access_web_service(host='15.15.15.15')
        self._insert_access_web_service(host='11.11.11.11')
        hosts = set(accesswebservice_dao.get_allowed_hosts())
        self.assertEqual(hosts, set(['15.15.15.15', '11.11.11.11']))

    def test_get_user_id(self):
        user = self._insert_access_web_service()

        result = accesswebservice_dao.get_user_id('test_login')

        assert_that(result, equal_to(user.id))

    def test_get_user_id_disabled(self):
        self._insert_access_web_service(disable=1)

        self.assertRaises(LookupError, accesswebservice_dao.get_user_id, 'test_login')

    def test_given_disabled_user_when_check_username_password_then_return_false(self):
        self._insert_access_web_service(disable=1)

        result = accesswebservice_dao.check_username_password('test_login', 'test_password')

        assert_that(result, equal_to(False))

    def test_given_invalid_login_when_check_username_password_then_return_false(self):
        self._insert_access_web_service()

        result = accesswebservice_dao.check_username_password('invalid', 'test_password')

        assert_that(result, equal_to(False))

    def test_given_invalid_password_when_check_username_password_then_return_false(self):
        self._insert_access_web_service()

        result = accesswebservice_dao.check_username_password('test_login', 'invalid')

        assert_that(result, equal_to(False))

    def test_given_right_credentials_when_check_username_password_then_return_false(self):
        self._insert_access_web_service()

        result = accesswebservice_dao.check_username_password('test_login', 'test_password')

        assert_that(result, equal_to(True))

    def _insert_access_web_service(self, **kwargs):
        kwargs.setdefault('name', ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(6)))
        kwargs.setdefault('login', 'test_login')
        kwargs.setdefault('passwd', 'test_password')
        kwargs.setdefault('description', '')
        kwargs.setdefault('disable', 0)
        kwargs.setdefault('host', '')

        access = AccessWebService(**kwargs)

        self.add_me(access)

        return access
