# -*- coding: utf-8 -*-
# Copyright 2014-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import unicode_literals

import unittest

from mock import Mock, sentinel as s
from hamcrest import assert_that
from hamcrest import calling
from hamcrest import equal_to
from hamcrest import contains
from hamcrest import contains_inanyorder
from hamcrest import has_length
from hamcrest import is_in
from hamcrest import raises

from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.resources.utils.search import SearchConfig
from xivo_dao.resources.utils.search import SearchSystem
from xivo_dao.resources.utils.search import CriteriaBuilderMixin
from xivo_dao.helpers.exception import InputError

from xivo_dao.alchemy.userfeatures import UserFeatures


class TestCriteriaBuilderMixin(unittest.TestCase):

    class Table(object):

        id = s.id
        name = s.name
        number = s.number

    class QueryMock(object):

        filter_by = []

        def filter(self, expr):
            self.filter_by.append(expr)
            return self

        def assert_filter_by(self, expr):
            assert_that(expr, is_in(self.filter_by))

    def setUp(self):
        class TestedClass(CriteriaBuilderMixin):

            _search_table = self.Table

        self.klass = TestedClass()
        self.query = self.QueryMock()

    def test_that_build_criteria_with_unknown_column_raises(self):
        criteria = {'foo': 'bar'}

        assert_that(calling(self.klass.build_criteria).with_args(self.query, criteria),
                    raises(InputError))

    def test_that_criterias_are_filtered(self):
        criteria = {'name': 'foo', 'number': 'bar'}

        resulting_query = self.klass.build_criteria(self.query, criteria)

        resulting_query.assert_filter_by(s.name == 'foo')
        resulting_query.assert_filter_by(s.number == 'bar')


class TestSearchSystem(DAOTestCase):

    def setUp(self):
        DAOTestCase.setUp(self)
        self.config = SearchConfig(table=UserFeatures,
                                   columns={'lastname': UserFeatures.lastname,
                                            'firstname': UserFeatures.firstname,
                                            'simultcalls': UserFeatures.simultcalls,
                                            'userfield': UserFeatures.userfield},
                                   default_sort='lastname')
        self.search = SearchSystem(self.config)

    def test_given_no_parameters_then_sorts_rows_using_default_sort_and_direction(self):
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
        self.assertRaises(InputError,
                          self.search.search,
                          self.session, {'limit': -1})

    def test_given_limit_is_zero_then_raises_error(self):
        self.assertRaises(InputError,
                          self.search.search,
                          self.session, {'limit': 0})

    def test_given_offset_is_negative_number_then_raises_error(self):
        self.assertRaises(InputError,
                          self.search.search,
                          self.session, {'offset': -1})

    def test_given_limit_then_returns_same_number_of_rows_as_limit(self):
        self.add_user()
        self.add_user()

        rows, total = self.search.search(self.session, {'limit': 1})

        assert_that(total, equal_to(2))
        assert_that(rows, has_length(1))

    def test_given_offset_then_offsets_a_number_of_rows(self):
        self.add_user(lastname='Abigale')
        last_user_row = self.add_user(lastname='Zintrabi')

        rows, total = self.search.search(self.session, {'offset': 1})

        assert_that(total, equal_to(2))
        assert_that(rows, contains(last_user_row))

    def test_given_offset_is_zero_then_does_not_offset_rows(self):
        first_user_row = self.add_user(lastname='Abigale')
        last_user_row = self.add_user(lastname='Zintrabi')

        rows, total = self.search.search(self.session, {'offset': 0})

        assert_that(total, equal_to(2))
        assert_that(rows, contains(first_user_row, last_user_row))

    def test_given_search_without_accent_term_then_searches_in_column_with_accent(self):
        user_row = self.add_user(firstname='accênt')

        rows, total = self.search.search(self.session, {'search': 'accent'})

        assert_that(total, equal_to(1))
        assert_that(rows, contains(user_row))

    def test_given_search_wit_accent_term_then_searches_in_column_without_accent(self):
        user_row1 = self.add_user(firstname='accént')
        user_row2 = self.add_user(firstname='unaccent')

        rows, total = self.search.search(self.session, {'search': 'accént'})

        assert_that(total, equal_to(2))
        assert_that(rows, contains(user_row1, user_row2))

    def test_given_search_term_then_searches_in_columns_and_uses_default_sort(self):
        user_row1 = self.add_user(firstname='a123bcd', lastname='eeefghi')
        user_row2 = self.add_user(firstname='eeefghi', lastname='a123zzz')
        self.add_user(description='123')

        rows, total = self.search.search(self.session, {'search': '123'})

        assert_that(total, equal_to(2))
        assert_that(rows, contains(user_row2, user_row1))

    def test_given_search_term_then_searches_in_numeric_columns(self):
        self.add_user(simultcalls=1)
        user_row2 = self.add_user(simultcalls=2)

        rows, total = self.search.search(self.session, {'search': '2'})

        assert_that(total, equal_to(1))
        assert_that(rows, contains(user_row2))

    def test_given_exact_match_numeric_term_in_param(self):
        self.add_user(firstname='Alice', lastname='First', simultcalls=3)
        user_row2 = self.add_user(firstname='Alice', lastname='Second', simultcalls=2)

        rows, total = self.search.search(self.session, {'search': 'ali', 'simultcalls': '2'})

        assert_that(total, equal_to(1))
        assert_that(rows, contains(user_row2))

    def test_given_exact_match_userfield_term_in_param(self):
        self.add_user(firstname='Alice', lastname='First', userfield='mtl')
        user_row2 = self.add_user(firstname='Alice', lastname='Second', userfield='qc')

        rows, total = self.search.search(self.session, {'search': 'ali', 'userfield': 'qc'})

        assert_that(total, equal_to(1))
        assert_that(rows, contains(user_row2))

    def test_given_exact_match_string_term_in_param_numeric_column(self):
        self.add_user(firstname='Alice', lastname='First', simultcalls=2)

        rows, total = self.search.search(self.session, {'simultcalls': 'invalid-integer'})

        assert_that(total, equal_to(0))

    def test_given_no_search_with_params(self):
        self.add_user(firstname='Alïce', userfield='mtl')
        user_row2 = self.add_user(firstname='Bõb', userfield='qc')
        user_row3 = self.add_user(firstname='Çharles', userfield='qc')

        rows, total = self.search.search(self.session, {'userfield': 'qc'})

        assert_that(total, equal_to(2))
        assert_that(rows, contains(user_row2, user_row3))


class TestSearchConfig(unittest.TestCase):

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

        self.assertRaises(InputError, config.column_for_sorting, 'toto')

    def test_given_sort_column_does_not_exist_when_sorting_then_raises_error(self):
        table = Mock()

        config = SearchConfig(table=table,
                              columns={'column1': 'column1'},
                              default_sort='column1')

        self.assertRaises(InputError, config.column_for_sorting, 'column2')

    def test_given_list_of_search_columns_then_returns_only_all_search_columns(self):
        table = Mock()
        column = Mock()

        config = SearchConfig(table=table,
                              columns={'column1': column, 'column2': Mock()},
                              search=['column1'],
                              default_sort='column1')

        result = config.all_search_columns()

        assert_that(result, contains(column))

    def test_given_list_of_columns_then_returns_all_all_search_columns(self):
        table = Mock()
        column1 = Mock()
        column2 = Mock()

        config = SearchConfig(table=table,
                              columns={'column1': column1, 'column2': column2},
                              default_sort='column1')

        result = config.all_search_columns()

        assert_that(result, contains_inanyorder(column1, column2))

    def test_that_column_for_searching_results_the_column(self):
        table = Mock()
        column1 = Mock()
        column2 = Mock()

        config = SearchConfig(table=table,
                              columns={'column1': column1, 'column2': column2},
                              default_sort='column1')

        result = config.column_for_searching('column1')

        assert_that(result, equal_to(column1))

    def test_that_column_for_searching_results_the_column_or_none(self):
        table = Mock()
        column1 = Mock()
        column2 = Mock()

        config = SearchConfig(table=table,
                              columns={'column1': column1, 'column2': column2},
                              default_sort='column1')

        result = config.column_for_searching('column3')

        assert_that(result, equal_to(None))
