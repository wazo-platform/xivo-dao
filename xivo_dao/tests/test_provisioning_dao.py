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

from xivo_dao import provisioning_dao
from xivo_dao.alchemy.provisioning import Provisioning
from xivo_dao.tests.test_dao import DAOTestCase


class TestProvisionningDao(DAOTestCase):

    def test_get_provd_rest_host_and_port(self):
        self._insert_provisionning()
        result = provisioning_dao.get_provd_rest_host_and_port()
        self.assertEqual(result, (u'127.0.0.1', 1234))

    def _insert_provisionning(self):
        provisioning = Provisioning()
        provisioning.net4_ip = ''
        provisioning.net4_ip_rest = '127.0.0.1'
        provisioning.username = 'admin'
        provisioning.password = 'admin'
        provisioning.dhcp_integration = 0
        provisioning.rest_port = 1234
        provisioning.http_port = 8667
        provisioning.private = 0
        provisioning.secure = 0

        self.add_me(provisioning)

        return provisioning
