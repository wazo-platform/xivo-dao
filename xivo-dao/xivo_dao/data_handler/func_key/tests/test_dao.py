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

from contextlib import contextmanager
from hamcrest import assert_that, equal_to, instance_of, contains, is_not, \
    none, has_property
from mock import patch, Mock, ANY

from xivo_dao.tests.test_dao import DAOTestCase

from xivo_dao.data_handler.exception import ElementNotExistsError
from xivo_dao.data_handler.exception import ElementCreationError
from xivo_dao.data_handler.exception import ElementDeletionError
from xivo_dao.data_handler.func_key.model import FuncKey
from xivo_dao.data_handler.func_key import dao
from xivo_dao.helpers.abstract_model import SearchResult
from xivo_dao.alchemy.func_key import FuncKey as FuncKeySchema
from xivo_dao.alchemy.func_key_type import FuncKeyType as FuncKeyTypeSchema
from xivo_dao.alchemy.func_key_dest_user import FuncKeyDestUser as FuncKeyDestUserSchema
from xivo_dao.alchemy.func_key_destination_type import FuncKeyDestinationType as FuncKeyDestinationTypeSchema
from xivo_dao.alchemy.userfeatures import test_dependencies as user_test_dependencies
from xivo_dao.alchemy.userfeatures import UserFeatures as UserSchema


class BaseTestFuncKeyDao(DAOTestCase):

    tables = [
        FuncKeySchema,
        FuncKeyTypeSchema,
        FuncKeyDestinationTypeSchema,
        FuncKeyDestUserSchema,
        UserSchema,
    ] + user_test_dependencies

    def setUp(self):
        self.empty_tables()


class TestFuncKeyDao(BaseTestFuncKeyDao):

    def setUp(self):
        BaseTestFuncKeyDao.setUp(self)
        self.create_types_and_destinations()

    def create_types_and_destinations(self):
        func_key_type_row = self.add_func_key_type(name='speeddial')
        user_destination_row = self.add_func_key_destination_type(id=1, name='user')

        self.type_id = func_key_type_row.id
        self.user_destination_id = user_destination_row.id

    def add_func_key_for_user(self, user_row):
        func_key_row = self.add_func_key(type_id=self.type_id,
                                         destination_type_id=self.user_destination_id)

        dest_user = FuncKeyDestUserSchema(user_id=user_row.id,
                                          func_key_id=func_key_row.id,
                                          destination_type_id=self.user_destination_id)
        self.add_me(dest_user)

        return func_key_row

    def prepare_user_destination(self, user_row):
        func_key_row = self.add_func_key_for_user(user_row)

        return FuncKey(id=func_key_row.id,
                       type='speeddial',
                       destination='user',
                       destination_id=user_row.id)


        return func_key

    def find_user_destination(self, user_id):
        row = (self.session.query(FuncKeyDestUserSchema)
               .filter(FuncKeyDestUserSchema.user_id == user_id)
               .first())

        return row

    @contextmanager
    def mocked_session(self):
        patcher = patch('xivo_dao.helpers.db_manager.AsteriskSession')
        mock = patcher.start()
        yield mock.return_value
        patcher.stop()


class TestFuncKeySearch(TestFuncKeyDao):

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

    def test_given_user_destination_when_searching_then_one_result_returned(self):
        user_row = self.add_user()
        func_key = self.prepare_user_destination(user_row)

        result = dao.search()

        assert_that(result.total, 1)
        assert_that(result.items, contains(func_key))


class TestFuncKeyFindAllByDestination(TestFuncKeyDao):

    def test_given_no_destinations_then_returns_empty_list(self):
        result = dao.find_all_by_destination('user', 1)

        assert_that(result, contains())

    def test_given_one_user_destination_then_returns_list_with_one_element(self):
        user_row = self.add_user()
        func_key = self.prepare_user_destination(user_row)

        result = dao.find_all_by_destination('user', user_row.id)

        assert_that(result, contains(func_key))

    def test_given_2_user_destinations_then_returns_list_with_right_destination(self):
        first_user = self.add_user()
        second_user = self.add_user()

        self.prepare_user_destination(first_user)
        func_key = self.prepare_user_destination(second_user)

        result = dao.find_all_by_destination('user', second_user.id)

        assert_that(result, contains(func_key))

    def test_given_user_destination_when_searching_wrong_type_then_returns_empty_list(self):
        user_row = self.add_user()
        self.prepare_user_destination(user_row)

        result = dao.find_all_by_destination('invalidtype', user_row.id)

        assert_that(result, contains())


class TestFuncKeyGet(TestFuncKeyDao):

    def test_when_no_func_key_then_raises_error(self):
        self.assertRaises(ElementNotExistsError, dao.get, 1)

    def test_when_user_func_key_in_db_then_func_key_model_returned(self):
        user_row = self.add_user()
        func_key = self.prepare_user_destination(user_row)

        result = dao.get(func_key.id)

        assert_that(result, equal_to(func_key))

    def test_when_two_func_keys_in_db_then_right_model_returned(self):
        user_row = self.add_user()

        self.prepare_user_destination(user_row)
        second_func_key = self.prepare_user_destination(user_row)

        result = dao.get(second_func_key.id)

        assert_that(result, equal_to(second_func_key))


class TestFuncKeyCreate(TestFuncKeyDao):

    def test_given_user_destination_then_func_key_created(self):
        user_row = self.add_user()

        func_key = FuncKey(type='speeddial',
                           destination='user',
                           destination_id=user_row.id)

        created_func_key = dao.create(func_key)
        assert_that(created_func_key, instance_of(FuncKey))
        assert_that(created_func_key, has_property('id', is_not(none())))

        user_destination_row = self.find_user_destination(user_row.id)
        assert_that(user_destination_row, is_not(none()))

        self.assert_func_key_row_created(user_destination_row)

    @patch('xivo_dao.data_handler.func_key.dao.commit_or_abort')
    def test_given_db_error_then_transaction_rollbacked(self, commit_or_abort):
        func_key = FuncKey(type='speeddial',
                           destination='user',
                           destination_id=1)

        with self.mocked_session() as session:
            dao.create(func_key)
            commit_or_abort.assert_any_call(session, ElementCreationError, 'FuncKey')

    def assert_func_key_row_created(self, destination_row):
        row = (self.session.query(FuncKeySchema)
               .filter(FuncKeySchema.id == destination_row.func_key_id)
               .first())
        assert_that(row, is_not(none()))


class TestFuncKeyDelete(TestFuncKeyDao):

    def test_given_user_destination_then_func_key_deleted(self):
        user_row = self.add_user()
        func_key = self.prepare_user_destination(user_row)

        dao.delete(func_key)

        self.assert_func_key_deleted(func_key.id)
        self.assert_user_destination_deleted(user_row.id)

    @patch('xivo_dao.data_handler.func_key.dao.commit_or_abort')
    def test_given_db_error_then_transaction_rollbacked(self, commit_or_abort):
        func_key = FuncKey(type='speeddial',
                           destination='user',
                           destination_id=1)

        with self.mocked_session() as session:
            dao.delete(func_key)
            commit_or_abort.assert_any_call(session, ElementDeletionError, 'FuncKey')

    def assert_func_key_deleted(self, func_key_id):
        row = (self.session.query(FuncKeySchema)
               .filter(FuncKeySchema.id == func_key_id)
               .first())
        assert_that(row, none())

    def assert_user_destination_deleted(self, user_id):
        row = self.find_user_destination(user_id)
        assert_that(row, none())
