# Copyright 2014-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import unicodedata
from typing import Any, NamedTuple

import sqlalchemy as sa
from sqlalchemy import sql
from sqlalchemy.sql.functions import ReturnTypeFromArgs
from sqlalchemy.types import Integer
from unidecode import unidecode

from xivo_dao.helpers import errors
from xivo_dao.helpers.sequence_utils import split_by


class SearchResult(NamedTuple):
    total: int
    items: list[Any]


class unaccent(ReturnTypeFromArgs):
    inherit_cache = True


def separate_criteria(
    criteria: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    Separate a mapping of filtering criteria
    between bulk(ending in `_in`) and non-bulk criteria
    for use by the appropriate build method
    """
    bulk_criteria, single_criteria = split_by(
        criteria.items(), lambda x: x[0].endswith('_in')
    )
    return dict(bulk_criteria), dict(single_criteria)


class CriteriaBuilderMixin:
    _search_table: type[sa.Table]

    def build_bulk_criteria(self, query, bulk_criteria):
        for key, value in bulk_criteria.items():
            assert key.endswith('_in')
            column_name = key[:-3]
            column = self._get_column(column_name)
            query = query.filter(column.in_(value))
        return query

    def build_criteria(self, query, criteria):
        for name, value in criteria.items():
            column = self._get_column(name)
            query = query.filter(column == value)
        return query

    def _get_column(self, name):
        column = getattr(self._search_table, name, None)
        if column is None:
            raise errors.unknown(name)
        return column


class SearchConfig:
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


class SearchSystem:
    SORT_DIRECTIONS = {
        'asc': sql.asc,
        'desc': sql.desc,
    }

    DEFAULTS = {
        'search': None,
        'order': None,
        'direction': 'asc',
        'limit': None,
        'offset': 0,
    }

    def __init__(self, config):
        self.config = config

    def search(self, session, parameters=None):
        query = session.query(self.config.table)
        return self.search_from_query(query, parameters)

    def search_collated(self, session, parameters=None):
        query = session.query(self.config.table)
        return self.search_from_query_collated(query, parameters)

    def search_from_query(self, query, parameters=None):
        parameters = self._populate_parameters(parameters)
        self._validate_parameters(parameters)
        query = self._filter(query, parameters['search'])
        query = self._filter_exact_match(query, parameters)
        sorted_query = self._sort(query, parameters['order'], parameters['direction'])
        paginated_query = self._paginate(
            sorted_query, parameters['limit'], parameters['offset']
        )

        return paginated_query.all(), sorted_query.count()

    def search_from_query_collated(self, query, parameters=None):
        parameters, order, limit, offset, reverse = self._extract_search_params(
            parameters
        )
        rows, total = self.search_from_query(query, parameters)
        return self._apply_search_params(rows, order, limit, offset, reverse), total

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
            expression = unaccent(sql.cast(column, sa.String)).ilike(f'%{clean_term}%')
            criteria.append(expression)

        query = query.filter(sql.or_(*criteria))
        return query

    def _filter_exact_match(self, query, parameters):
        for column_name, value in parameters.items():
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

    def _extract_search_params(self, parameters):
        parameters = self._populate_parameters(parameters)
        self._validate_parameters(parameters)
        self.config.column_for_sorting(parameters['order'])

        order = parameters.pop('order', None)
        limit = parameters.pop('limit', None)
        offset = parameters.pop('offset', 0)
        reverse = False if parameters.pop('direction', 'asc') == 'asc' else True
        return parameters, order, limit, offset, reverse

    def _apply_search_params(self, rows, order, limit, offset, reverse):
        def _get_attr(o):
            a = getattr(o, order, '')
            return str(a) if a is not None else ''

        if order:
            rows = sorted(
                rows,
                key=lambda x: (
                    _get_attr(x) == '',
                    unicodedata.normalize('NFKD', _get_attr(x)),
                ),
                reverse=reverse,
            )
        elif reverse:
            rows.reverse()

        if not limit:
            return rows[offset:]
        else:
            return rows[offset : offset + limit]
