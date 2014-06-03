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

from collections import namedtuple

import sqlalchemy as sa
from sqlalchemy import sql

from xivo_dao.data_handler.exception import InvalidParametersError

SearchResult = namedtuple('SearchResult', ['total', 'items'])


class SearchConfig(object):

    REQUIRED = ('table', 'columns', 'default_sort')

    def __init__(self, **parameters):
        parameters.setdefault('search', None)
        parameters.setdefault('sort', None)
        self._validate_required_params(parameters)

        for key, value in parameters.items():
            setattr(self, key, value)

    def columns_for_searching(self):
        if self.search:
            return [self.columns[s] for s in self.search]
        return self.columns.values()

    def column_for_sorting(self, name=None):
        column_name = self._get_sort_column_name(name)
        return self.columns[column_name]

    def _validate_required_params(self, parameters):
        for param_name in self.REQUIRED:
            if param_name not in parameters:
                raise AttributeError("search config is missing '%s' parameter" % param_name)

    def _get_sort_column_name(self, name=None):
        name = name or self.default_sort
        sort_columns = self.sort or self.columns.keys()

        if name not in sort_columns:
            raise InvalidParametersError(["ordering column '%s' does not exist" % name])

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
        'skip': 0
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
        sorted_query = self._sort(query, parameters['order'], parameters['direction'])
        paginated_query = self._paginate(sorted_query, parameters['limit'], parameters['skip'])

        return paginated_query.all(), sorted_query.count()

    def _populate_parameters(self, parameters=None):
        new_params = dict(self.DEFAULTS)
        if parameters:
            new_params.update(parameters)
        return new_params

    def _validate_parameters(self, parameters):
        invalid = []

        if parameters['skip'] < 0:
            invalid.append('skip must be a positive number')

        if parameters['limit'] and parameters['limit'] <= 0:
            invalid.append('limit must be a positive number')

        if parameters['direction'] not in self.SORT_DIRECTIONS.keys():
            invalid.append("direction must be 'asc' or 'desc'")

        if invalid:
            raise InvalidParametersError(invalid)

    def _filter(self, query, term=None):
        if not term:
            return query

        criteria = []
        for column in self.config.columns_for_searching():
            expression = sql.cast(column, sa.String).ilike('%%%s%%' % term)
            criteria.append(expression)

        query = query.filter(sql.or_(*criteria))
        return query

    def _sort(self, query, order=None, direction='asc'):
        column = self.config.column_for_sorting(order)
        direction = self.SORT_DIRECTIONS[direction]

        return query.order_by(direction(column))

    def _paginate(self, query, limit=None, skip=0):
        if skip > 0:
            query = query.offset(skip)

        if limit:
            query = query.limit(limit)

        return query
