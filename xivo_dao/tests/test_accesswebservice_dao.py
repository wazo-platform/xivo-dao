# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
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

from xivo_dao import accesswebservice_dao
from xivo_dao.alchemy.accesswebservice import AccessWebService
from xivo_dao.tests.test_dao import DAOTestCase


class TestAccessWebServiceDao(DAOTestCase):

    def test_get_password(self):
        access = self._insert_access_web_service('')
        password = accesswebservice_dao.get_password(access.login)
        self.assertEqual(password, access.passwd)

    def test_get_password_not_exist(self):
        password = accesswebservice_dao.get_password('toto')
        self.assertEqual(password, None)

    def test_get_allowed_hosts(self):
        self._insert_access_web_service('15.15.15.15')
        self._insert_access_web_service('11.11.11.11')
        hosts = set(accesswebservice_dao.get_allowed_hosts())
        self.assertEqual(hosts, set(['15.15.15.15', '11.11.11.11']))

    def _insert_access_web_service(self, host):
        access = AccessWebService()
        access.name = ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(6))
        access.login = 'test_login'
        access.passwd = 'test_password'
        access.description = ''
        access.disable = 0
        access.host = host
        access.obj = ''

        self.session.begin()
        self.session.add(access)
        self.session.commit()

        return access
