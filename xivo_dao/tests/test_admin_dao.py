# -*- coding: utf-8 -*-
#
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

from hamcrest import assert_that, equal_to

from xivo_dao import admin_dao
from xivo_dao.tests.test_dao import DAOTestCase


class TestAdminUserDAO(DAOTestCase):

    def test_check_username_password(self):
        self.add_admin(login='foo', passwd='bar')

        valid = admin_dao.check_username_password('foo', 'bar')

        assert_that(valid, equal_to(True))

    def test_check_username_password_invalid(self):
        self.add_admin(login='foo', passwd='bar', valid=0)

        valid = admin_dao.check_username_password('foo', 'bar')

        assert_that(valid, equal_to(False))

    def test_get_admin_id(self):
        admin = self.add_admin(login='foo', passwd='bar')

        result = admin_dao.get_admin_id('foo')

        assert_that(result, equal_to(admin.id))
