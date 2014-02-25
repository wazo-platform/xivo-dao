# -*- coding: utf-8 -*-

# Copyright (C) 2014 Avencall
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

from xivo_dao.data_handler.func_key.tests.test_dao import TestFuncKeyDao
from xivo_dao.data_handler.func_key import type_dao as dao

from hamcrest import assert_that, none, has_property


class TestFindTypeForName(TestFuncKeyDao):

    def test_given_no_types_then_returns_none(self):
        result = dao.find_type_for_name('type')

        assert_that(result, none())

    def test_given_one_type_when_queried_returns_one_row(self):
        type_name = 'speeddial'
        self.add_type(type_name)

        result = dao.find_type_for_name(type_name)

        assert_that(result, has_property('name', type_name))

    def test_given_one_type_when_other_name_queried_returns_none(self):
        self.add_type('speeddial')

        result = dao.find_type_for_name('transfer')

        assert_that(result, none())

    def test_given_two_types_when_one_queried_returns_right_row(self):
        self.add_type('speeddial')
        self.add_type('transfer')

        result = dao.find_type_for_name('transfer')

        assert_that(result, has_property('name', 'transfer'))


class TestFuncKeyDestinationTypeExists(TestFuncKeyDao):

    def test_given_no_destination_types_then_returns_none(self):
        result = dao.find_destination_type_for_name('type')

        assert_that(result, none())

    def test_given_one_destination_type_when_queried_returns_true(self):
        name = 'user'
        self.add_destination_type(1, name)

        result = dao.find_destination_type_for_name(name)

        assert_that(result, has_property('name', name))

    def test_given_one_destination_type_when_other_name_queried_returns_false(self):
        self.add_destination_type(1, 'user')

        result = dao.find_destination_type_for_name('queue')

        assert_that(result, none())

    def test_given_two_destination_types_when_one_queried_returns_true(self):
        self.add_destination_type(1, 'user')
        self.add_destination_type(2, 'queue')

        result = dao.find_destination_type_for_name('queue')

        assert_that(result, has_property('name', 'queue'))
