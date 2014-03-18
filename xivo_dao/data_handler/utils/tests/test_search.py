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

import unittest
from mock import patch, Mock
from hamcrest import assert_that, equal_to

from xivo_dao.data_handler.utils.search import SearchFilter


class TestSearchFilter(unittest.TestCase):

    def setUp(self):
        self.base_query = Mock()
        self.columns = [Mock(), Mock()]
        self.default_column = Mock()
        self.search_filter = SearchFilter(self.base_query, self.columns, self.default_column)

    @patch.object(SearchFilter, 'paginate')
    @patch.object(SearchFilter, 'sort')
    @patch.object(SearchFilter, 'search_for')
    def test_search(self, search_for, sort, paginate):
        term = ''
        limit = 1
        skip = 2
        order = Mock()
        direction = 'desc'

        search_query = search_for.return_value = Mock()
        sort_query = sort.return_value = Mock()
        paginate_query = paginate.return_value = Mock()
        mock_items = paginate_query.all.return_value = Mock()
        mock_total = search_query.count.return_value = Mock()

        items, total = self.search_filter.search(term, limit, skip, order, direction)

        search_for.assert_called_once_with(self.base_query, term)
        sort.assert_called_once_with(search_query, order, direction)
        paginate.assert_called_once_with(sort_query, limit, skip)

        assert_that(items, equal_to(mock_items))
        assert_that(total, equal_to(mock_total))

    def test_search_for_no_term(self):
        search_query = self.search_filter.search_for(None)

        assert_that(search_query, equal_to(self.base_query))

    @patch('xivo_dao.data_handler.utils.search.or_')
    def test_search_for_with_term(self, sql_or):
        term = 'term'
        mock_criteria = sql_or.return_value = Mock()
        search_query = self.base_query.filter.return_value = Mock()
        column1, column2 = self.columns

        result = self.search_filter.search_for(self.base_query, term)

        sql_or.assert_called_once_with(column1.ilike.return_value, column2.ilike.return_value)
        self.base_query.filter.assert_called_once_with(mock_criteria)
        column1.ilike.assert_called_once_with('%term%')
        column2.ilike.assert_called_once_with('%term%')
        assert_that(result, equal_to(search_query))

    def test_paginate_no_parameters(self):
        result = self.search_filter.paginate(self.base_query, None, None)

        assert_that(result, equal_to(self.base_query))

    def test_paginate_with_limit(self):
        limit = 1
        limit_query = self.base_query.limit.return_value = Mock()

        result = self.search_filter.paginate(self.base_query, limit, None)

        self.base_query.limit.assert_called_once_with(limit)
        assert_that(result, equal_to(limit_query))

    def test_paginate_with_skip(self):
        skip = 2
        skip_query = self.base_query.offset.return_value = Mock()

        result = self.search_filter.paginate(self.base_query, None, skip)

        self.base_query.offset.assert_called_once_with(skip)
        assert_that(result, equal_to(skip_query))

    def test_paginate_with_limit_and_skip(self):
        limit = 1
        skip = 2

        skip_query = self.base_query.offset.return_value = Mock()
        limit_query = skip_query.limit.return_value = Mock()

        result = self.search_filter.paginate(self.base_query, limit, skip)

        self.base_query.offset.assert_called_once_with(skip)
        skip_query.limit.assert_called_once_with(limit)
        assert_that(result, equal_to(limit_query))

    @patch('xivo_dao.data_handler.utils.search.asc')
    def test_sort_with_default_parameters(self, sql_asc):
        order_query = self.base_query.order_by.return_value = Mock()
        mock_order = sql_asc.return_value = Mock()

        result = self.search_filter.sort(self.base_query, None, None)

        sql_asc.assert_called_once_with(self.default_column)
        self.base_query.order_by.assert_called_once_with(mock_order)

        assert_that(result, equal_to(order_query))

    @patch('xivo_dao.data_handler.utils.search.asc')
    def test_sort_with_different_order(self, sql_asc):
        order_query = self.base_query.order_by.return_value = Mock()
        mock_order = sql_asc.return_value = Mock()
        column = Mock()

        result = self.search_filter.sort(self.base_query, column, None)

        sql_asc.assert_called_once_with(column)
        self.base_query.order_by.assert_called_once_with(mock_order)

        assert_that(result, equal_to(order_query))

    @patch('xivo_dao.data_handler.utils.search.desc')
    def test_sort_with_different_direction(self, sql_desc):
        order_query = self.base_query.order_by.return_value = Mock()
        mock_order = sql_desc.return_value = Mock()
        column = Mock()

        result = self.search_filter.sort(self.base_query, column, 'desc')

        sql_desc.assert_called_once_with(column)
        self.base_query.order_by.assert_called_once_with(mock_order)

        assert_that(result, equal_to(order_query))
