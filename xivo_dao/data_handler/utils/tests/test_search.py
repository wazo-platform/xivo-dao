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

from mock import Mock
import unittest
from hamcrest import assert_that, equal_to, contains, has_length

from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.data_handler.utils.search import SearchConfig
from xivo_dao.data_handler.utils.search import SearchSystem
from xivo_dao.data_handler.exception import InvalidParametersError

from xivo_dao.alchemy.userfeatures import UserFeatures


class TestSearchSystem(DAOTestCase):

    def setUp(self):
        DAOTestCase.setUp(self)
        self.config = SearchConfig(select=UserFeatures,
                                   columns={'lastname': UserFeatures.lastname,
                                            'firstname': UserFeatures.firstname,
                                            'simultcalls': UserFeatures.simultcalls},
                                   order_by='lastname')
        self.search = SearchSystem(self.config)

    def test_given_no_parameters_then_sorts_rows_using_default_order_and_direction(self):
        last_user_row = self.add_user(lastname='Zintrabi')
        first_user_row = self.add_user(lastname='Abigale')

        rows, total = self.search.search(self.session)

        assert_that(total, equal_to(2))
        assert_that(rows, contains(first_user_row, last_user_row))

    def test_given_order_then_sorts_rows_using_order(self):
        last_user_row = self.add_user(firstname='Bob', lastname='Abigale')
        first_user_row = self.add_user(firstname='Alice', lastname='Zintrabi')

        rows, total = self.search.search(self.session, {'order': 'firstname'})

        assert_that(total, equal_to(2))
        assert_that(rows, contains(first_user_row, last_user_row))

    def test_given_direction_then_sorts_rows_using_direction(self):
        first_user_row = self.add_user(lastname='Abigale')
        last_user_row = self.add_user(lastname='Zintrabi')

        rows, total = self.search.search(self.session, {'direction': 'desc'})

        assert_that(total, equal_to(2))
        assert_that(rows, contains(last_user_row, first_user_row))

    def test_given_limit_is_negative_number_then_raises_error(self):
        self.assertRaises(InvalidParametersError,
                          self.search.search,
                          self.session, {'limit': -1})

    def test_given_skip_is_negative_number_then_raises_error(self):
        self.assertRaises(InvalidParametersError,
                          self.search.search,
                          self.session, {'skip': -1})

    def test_given_limit_then_returns_same_number_of_rows_as_limit(self):
        self.add_user()
        self.add_user()

        rows, total = self.search.search(self.session, {'limit': 1})

        assert_that(total, equal_to(2))
        assert_that(rows, has_length(1))

    def test_given_skip_then_skips_a_number_of_rows(self):
        self.add_user(lastname='Abigale')
        last_user_row = self.add_user(lastname='Zintrabi')

        rows, total = self.search.search(self.session, {'skip': 1})

        assert_that(total, equal_to(2))
        assert_that(rows, contains(last_user_row))

    def test_given_search_then_filters_in_configured_columns_and_uses_default_order(self):
        user_row1 = self.add_user(firstname='a123bcd', lastname='eeefghi')
        user_row2 = self.add_user(firstname='eeefghi', lastname='a123zzz')
        self.add_user(description='123')

        rows, total = self.search.search(self.session, {'search': '123'})

        assert_that(total, equal_to(2))
        assert_that(rows, contains(user_row2, user_row1))

    def test_given_search_then_filters_in_numeric_columns(self):
        self.add_user(simultcalls=1)
        user_row2 = self.add_user(simultcalls=2)

        rows, total = self.search.search(self.session, {'search': '2'})

        assert_that(total, equal_to(1))
        assert_that(rows, contains(user_row2))


class TestSearchConfig(unittest.TestCase):

    def test_given_no_table_then_raises_error(self):
        self.assertRaisesRegexp(AttributeError,
                                "search config is missing 'table' parameter",
                                SearchConfig)

    def test_given_no_columns_then_raises_error(self):
        table = Mock()

        self.assertRaisesRegexp(AttributeError,
                                "search config is missing 'columns' parameter",
                                SearchConfig, table=table)

    def test_given_no_default_sort_then_raises_error(self):
        table = Mock()

        self.assertRaisesRegexp(AttributeError,
                                "search config is missing 'default_sort' parameter",
                                SearchConfig, table=table, columns={})

    def test_given_list_of_sort_columns_then_returns_columns_for_sorting(self):
        table = Mock()
        column = Mock()
        column2 = Mock()
        config = SearchConfig(table=table,
                              columns={'column': column,
                                       'column2': column2,
                                       'column3': Mock()},
                              sort=['column', 'column2'],
                              default_sort='column')

        result = config.column_for_sorting('column2')

        assert_that(result, equal_to(column2))

    def test_given_no_columns_when_sorting_then_raises_error(self):
        table = Mock()

        config = SearchConfig(table=table, columns={}, default_sort='nothing')

        self.assertRaisesRegexp(InvalidParametersError,
                                "Invalid parameters: ordering column 'toto' does not exist",
                                config.column_for_sorting, 'toto')

    def test_given_sort_column_does_not_exist_when_sorting_then_raises_error(self):
        table = Mock()

        config = SearchConfig(table=table,
                              columns={'column1': 'column1'},
                              default_sort='column1')

        self.assertRaisesRegexp(InvalidParametersError,
                                "Invalid parameters: ordering column 'column2' does not exist",
                                config.column_for_sorting, 'column2')

    def test_given_list_of_search_columns_then_returns_only_columns_for_searching(self):
        table = Mock()
        column = Mock()

        config = SearchConfig(table=table,
                              columns={'column1': column, 'column2': Mock()},
                              search=['column1'],
                              default_sort='column1')

        result = config.columns_for_searching()

        assert_that(result, contains(column))

    def test_given_list_of_columns_then_returns_all_columns_for_searching(self):
        table = Mock()
        column1 = Mock()
        column2 = Mock()

        config = SearchConfig(table=table,
                              columns={'column1': column1, 'column2': column2},
                              default_sort='column1')

        result = config.columns_for_searching()

        assert_that(result, contains(column1, column2))
