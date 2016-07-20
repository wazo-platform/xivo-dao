# -*- coding: utf-8 -*-

# Copyright (C) 2014-2016 Avencall
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

from collections import namedtuple

import sqlalchemy as sa
from sqlalchemy import sql

from xivo_dao.helpers import errors

SearchResult = namedtuple('SearchResult', ['total', 'items'])


class CriteriaBuilderMixin(object):

    def build_criteria(self, query, criteria):
        for name, value in criteria.iteritems():
            column = self._get_column(name)
            query = query.filter(column == value)
        return query

    def _get_column(self, name):
        column = getattr(self._search_table, name, None)
        if column is None:
            raise errors.unknown(name)
        return column


class SearchConfig(object):

    def __init__(self, table, columns, default_sort, search=None, sort=None):
        self.table = table
        self._columns = columns
        self._default_sort = default_sort
        self._search = search
        self._sort = sort

    def all_search_columns(self):
        if self._search:
            return [self._columns[s] for s in self._search]
        return self._columns.values()

    def column_for_searching(self, column_name):
        return self._columns.get(column_name)

    def column_for_sorting(self, name=None):
        column_name = self._get_sort_column_name(name)
        return self._columns[column_name]

    def _get_sort_column_name(self, name=None):
        name = name or self._default_sort
        sort_columns = self._sort or self._columns.keys()

        if name not in sort_columns:
            raise errors.invalid_ordering(name)

        return name


class SearchSystem(object):

    SORT_DIRECTIONS = {
        'asc': sql.asc,
        'desc': sql.desc,
    }

    DEFAULTS = {
        'search': None,
        'order': None,
        'direction': 'asc',
        'limit': None,
        'offset': 0
    }

    def __init__(self, config):
        self.config = config

    def search(self, session, parameters=None):
        query = session.query(self.config.table)
        return self.search_from_query(query, parameters)

    def search_from_query(self, query, parameters=None):
        parameters = self._populate_parameters(parameters)
        self._validate_parameters(parameters)

        query = self._filter(query, parameters['search'])
        query = self._filter_exact_match(query, parameters)
        sorted_query = self._sort(query, parameters['order'], parameters['direction'])
        paginated_query = self._paginate(sorted_query, parameters['limit'], parameters['offset'])

        return paginated_query.all(), sorted_query.count()

    def _populate_parameters(self, parameters=None):
        new_params = dict(self.DEFAULTS)
        if parameters:
            parameters['offset'] = parameters.pop('skip', parameters.get('offset', self.DEFAULTS['offset']))
            new_params.update(parameters)

        return new_params

    def _validate_parameters(self, parameters):
        if parameters['offset'] < 0:
            raise errors.wrong_type('offset', 'positive number')

        if parameters['limit'] is not None and parameters['limit'] <= 0:
            raise errors.wrong_type('limit', 'positive number')

        if parameters['direction'] not in self.SORT_DIRECTIONS.keys():
            raise errors.invalid_direction(parameters['direction'])

    def _filter(self, query, term=None):
        if not term:
            return query

        criteria = []
        for column in self.config.all_search_columns():
            expression = sql.cast(column, sa.String).ilike('%%%s%%' % term)
            criteria.append(expression)

        query = query.filter(sql.or_(*criteria))
        return query

    def _filter_exact_match(self, query, parameters):
        for column_name, value in parameters.iteritems():
            column = self.config.column_for_searching(column_name)
            if column is not None:
                query = query.filter(column == value)

        return query

    def _sort(self, query, order=None, direction='asc'):
        column = self.config.column_for_sorting(order)
        direction = self.SORT_DIRECTIONS[direction]

        return query.order_by(direction(column))

    def _paginate(self, query, limit=None, offset=0):
        if offset > 0:
            query = query.offset(offset)

        if limit:
            query = query.limit(limit)

        return query
