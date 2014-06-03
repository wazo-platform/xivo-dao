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

    sort_directions = {
        'asc': sql.asc,
        'desc': sql.desc,
    }

    def __init__(self, config):
        self.config = config

    def search(self, session, parameters=None):
        query = self.config.query(session)
        return self.search_from_query(query, parameters)

    def search_from_query(self, query, parameters=None):
        parameters = parameters or {}
        query = self._filter(query, parameters)
        sorted_query = self._sort(query, parameters)
        paginated_query = self._paginate(sorted_query, parameters)

        return paginated_query.all(), sorted_query.count()

    def _filter(self, query, parameters):
        term = parameters.get('search', None)
        if not term:
            return query

        criteria = []
        for column in self.config.columns_for_filtering():
            expression = sql.cast(column, sa.String).ilike('%%%s%%' % term)
            criteria.append(expression)

        return query.filter(sql.or_(*criteria))

    def _sort(self, query, parameters):
        order = parameters.get('order', None)
        direction = parameters.get('direction', 'asc')

        column = self.config.sort_by_column(order)
        sorted_column = self.sort_directions[direction](column)

        return query.order_by(sorted_column)

    def _paginate(self, query, parameters):
        self._validate_skip_limit(parameters)

        skip = parameters.get('skip', 0)
        if skip > 0:
            query = query.offset(parameters['skip'])

        if 'limit' in parameters:
            query = query.limit(parameters['limit'])

        return query

    def _validate_skip_limit(self, parameters):
        if 'skip' in parameters:
            if parameters['skip'] < 0:
                raise InvalidParametersError(['skip must be a positive number'])

        if 'limit' in parameters:
            if parameters['limit'] < 0:
                raise InvalidParametersError(['limit must be a positive number'])
