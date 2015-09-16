# -*- coding: utf-8 -*-

# Copyright (C) 2015 Avencall
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

from hamcrest import assert_that, contains, contains_inanyorder, empty

from xivo_dao import phone_access_dao
from xivo_dao.tests.test_dao import DAOTestCase


class TestPhoneAccessDao(DAOTestCase):

    def test_get_authorized_subnets(self):
        host = '169.254.0.0/16'
        self.add_accessfeatures(host)

        hosts = phone_access_dao.get_authorized_subnets()

        assert_that(hosts, contains(host))

    def test_get_authorized_subnets_with_commented(self):
        host = '169.254.0.0/16'
        commented = 1
        self.add_accessfeatures(host, commented=commented)

        hosts = phone_access_dao.get_authorized_subnets()

        assert_that(hosts, empty())

    def test_get_authorized_subnets_multiple_results(self):
        hosts = ['169.254.0.0/16', '192.168.1.1']

        for host in hosts:
            self.add_accessfeatures(host)

        hosts = phone_access_dao.get_authorized_subnets()

        assert_that(hosts, contains_inanyorder(*hosts))
