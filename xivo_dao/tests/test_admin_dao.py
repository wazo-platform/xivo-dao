# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2016 Avencall
# Copyright (C) 2016 Proformatique Inc.
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

    def test_given_right_credentials_when_check_username_password_then_return_true(self):
        self.add_admin(login='foo', passwd='bar')

        valid = admin_dao.check_username_password('foo', 'bar')

        assert_that(valid, equal_to(True))

    def test_given_invalid_account_when_check_username_password_then_return_false(self):
        self.add_admin(login='foo', passwd='bar', valid=0)

        valid = admin_dao.check_username_password('foo', 'bar')

        assert_that(valid, equal_to(False))

    def test_given_invalid_login_when_check_username_password_then_return_false(self):
        self.add_admin(login='foo', passwd='bar')

        valid = admin_dao.check_username_password('alice', 'bar')

        assert_that(valid, equal_to(False))

    def test_given_invalid_password_when_check_username_password_then_return_false(self):
        self.add_admin(login='foo', passwd='bar')

        valid = admin_dao.check_username_password('foo', 'superdupersecret')

        assert_that(valid, equal_to(False))

    def test_get_admin_id(self):
        admin = self.add_admin(login='foo', passwd='bar')

        result = admin_dao.get_admin_id('foo')

        assert_that(result, equal_to(admin.id))

    def test_get_admin_entity(self):
        entity = self.add_entity(name='test')
        self.add_admin(login='foo', passwd='bar', entity_id=entity.id)

        result = admin_dao.get_admin_entity('foo')

        assert_that(result, equal_to('test'))

    def test_get_admin_entity_no_entify(self):
        self.add_admin(login='alice', passwd='foobar')

        result = admin_dao.get_admin_entity('alice')

        assert_that(result, equal_to(None))
