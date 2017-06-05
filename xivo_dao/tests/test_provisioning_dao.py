# -*- coding: utf-8 -*-

# Copyright 2013-2017 The Wazo Authors  (see the AUTHORS file)
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

from __future__ import unicode_literals

from xivo_dao import provisioning_dao
from xivo_dao.alchemy.provisioning import Provisioning
from xivo_dao.tests.test_dao import DAOTestCase


class TestProvisionningDao(DAOTestCase):

    def test_get_provd_rest_host_and_port(self):
        self._insert_provisionning()
        result = provisioning_dao.get_provd_rest_host_and_port()
        self.assertEqual(result, ('127.0.0.1', 1234))

    def _insert_provisionning(self):
        provisioning = Provisioning(
            net4_ip='',
            net4_ip_rest='127.0.0.1',
            username='admin',
            password='admin',
            dhcp_integration=0,
            rest_port=1234,
            http_port=8667,
            private=0,
            secure=0,
        )

        self.add_me(provisioning)

        return provisioning
