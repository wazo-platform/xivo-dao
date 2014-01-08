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

from xivo_dao.alchemy.accesswebservice import AccessWebService
from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao import accesswebservice_dao


class TestAccessWebServiceDao(DAOTestCase):

    tables = [AccessWebService]

    def setUp(self):
        self.host = None
        self.empty_tables()

    def test_get_password(self):
        access = self._insert_access_web_service()
        password = accesswebservice_dao.get_password(access.login)
        self.assertEqual(password, access.passwd)

    def test_get_allowed_hosts(self):
        self.host = '15.15.15.15'
        self._insert_access_web_service()
        self.host = '11.11.11.11'
        self._insert_access_web_service()
        hosts = set(accesswebservice_dao.get_allowed_hosts())
        self.assertEqual(hosts, set(['15.15.15.15', '11.11.11.11']))

    def _insert_access_web_service(self):
        access = AccessWebService()
        access.name = 'test_name'
        access.login = 'test_login'
        access.passwd = 'test_password'
        access.description = ''
        access.disable = 0
        access.host = self.host
        access.obj = ''

        self.session.begin()
        self.session.add(access)
        self.session.commit()

        return access
