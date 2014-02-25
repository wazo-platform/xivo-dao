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

from hamcrest import assert_that, equal_to, instance_of, contains
from mock import patch, Mock, ANY

from xivo_dao.tests.test_dao import DAOTestCase

from xivo_dao.data_handler.exception import ElementNotExistsError
from xivo_dao.data_handler.func_key.model import FuncKey
from xivo_dao.data_handler.func_key import dao
from xivo_dao.helpers.abstract_model import SearchResult
from xivo_dao.alchemy.func_key import FuncKey as FuncKeySchema
from xivo_dao.alchemy.func_key_type import FuncKeyType as FuncKeyTypeSchema
from xivo_dao.alchemy.func_key_dest_user import FuncKeyDestUser as FuncKeyDestUserSchema
from xivo_dao.alchemy.func_key_destination_type import FuncKeyDestinationType as FuncKeyDestinationTypeSchema
from xivo_dao.alchemy.userfeatures import test_dependencies as user_test_dependencies
from xivo_dao.alchemy.userfeatures import UserFeatures as UserSchema


class TestFuncKeyDao(DAOTestCase):

    tables = [
        FuncKeySchema,
        FuncKeyTypeSchema,
        FuncKeyDestinationTypeSchema,
        FuncKeyDestUserSchema,
        UserSchema,
    ] + user_test_dependencies

    def setUp(self):
        self.empty_tables()

    def add_type(self, name):
        func_key_type_row = FuncKeyTypeSchema(name=name)
        self.add_me(func_key_type_row)
        return func_key_type_row

    def add_destination_type(self, id, name):
        destination_type_row = FuncKeyDestinationTypeSchema(id=id, name=name)
        self.add_me(destination_type_row)
        return destination_type_row


class TestUserFuncKey(TestFuncKeyDao):

    def setUp(self):
        TestFuncKeyDao.setUp(self)
        self.create_types_and_destinations()

    def create_types_and_destinations(self):
        func_key_type_row = self.add_type('speeddial')
        destination_type_row = self.add_destination_type(1, 'user')

        self.type_id = func_key_type_row.id
        self.destination_type_id = destination_type_row.id

    def add_func_key_for_user(self, user_row):
        func_key_row = FuncKeySchema(type_id=self.type_id,
                                     destination_type_id=self.destination_type_id)

        self.add_me(func_key_row)

        dest_user = FuncKeyDestUserSchema(user_id=user_row.id,
                                          func_key_id=func_key_row.id,
                                          destination_type_id=self.destination_type_id)

        self.add_me(dest_user)

        return func_key_row

    def prepare_speeddial_with_user_destination(self, user_row):
        func_key_row = self.add_func_key_for_user(user_row)

        func_key = FuncKey(id=func_key_row.id,
                           type='speeddial',
                           destination='user',
                           destination_id=user_row.id)

        return func_key_row, func_key


class TestFuncKeySearch(TestUserFuncKey):

    @patch('xivo_dao.data_handler.func_key.dao.db_converter')
    @patch('xivo_dao.data_handler.func_key.dao.SearchFilter')
    def test_search_calls_search_filter(self, SearchFilter, db_converter):
        search_filter = SearchFilter.return_value

        item = Mock()
        mock_items, mock_total = search_filter.search.return_value = ([item], 1)
        converted_item = db_converter.to_model.return_value = Mock()

        result = dao.search()

        SearchFilter.assert_called_once_with(ANY, FuncKey.SEARCH_COLUMNS, FuncKeySchema.id)
        db_converter.to_model.assert_called_once_with(item)

        assert_that(result, instance_of(SearchResult))
        assert_that(result.items, contains(converted_item))
        assert_that(result.total, equal_to(mock_total))

    def test_search_one_func_key(self):
        user_row = self.add_user()
        _, func_key = self.prepare_speeddial_with_user_destination(user_row)

        result = dao.search()

        assert_that(result.total, 1)
        assert_that(result.items, contains(func_key))


class TestFuncKeyGet(TestUserFuncKey):

    def test_when_no_func_key_then_raises_error(self):
        self.assertRaises(ElementNotExistsError, dao.get, 1)

    def test_when_one_func_key_in_db_then_func_key_model_returned(self):
        user_row = self.add_user()
        func_key_row, func_key = self.prepare_speeddial_with_user_destination(user_row)

        result = dao.get(func_key_row.id)

        assert_that(result, equal_to(func_key))

    def test_when_two_func_keys_in_db_then_right_model_returned(self):
        user_row = self.add_user()

        self.prepare_speeddial_with_user_destination(user_row)
        second_func_key_row, second_func_key = self.prepare_speeddial_with_user_destination(user_row)

        result = dao.get(second_func_key_row.id)

        assert_that(result, equal_to(second_func_key))
