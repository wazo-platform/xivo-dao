# -*- coding: utf-8 -*-
# Copyright 2014-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import six

from collections import namedtuple
from unidecode import unidecode

import sqlalchemy as sa

from sqlalchemy import sql
from sqlalchemy.sql.functions import ReturnTypeFromArgs
from sqlalchemy.types import Integer

from xivo_dao.helpers import errors

SearchResult = namedtuple('SearchResult', ['total', 'items'])


class unaccent(ReturnTypeFromArgs):
    pass


class CriteriaBuilderMixin(object):

    def build_criteria(self, query, criteria):
        for name, value in six.iteritems(criteria):
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
        return list(self._columns.values())

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
            parameters.setdefault('offset', self.DEFAULTS['offset'])
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
            clean_term = unidecode(term)
            expression = unaccent(sql.cast(column, sa.String)).ilike('%%%s%%' % clean_term)
            criteria.append(expression)

        query = query.filter(sql.or_(*criteria))
        return query

    def _filter_exact_match(self, query, parameters):
        for column_name, value in six.iteritems(parameters):
            column = self.config.column_for_searching(column_name)
            if column is not None:
                if isinstance(column.type, Integer) and not self._represents_int(value):
                    return query.filter(False)
                query = query.filter(column == value)

        return query

    def _represents_int(self, value):
        try:
            int(value)
            return True
        except ValueError:
            return False

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
