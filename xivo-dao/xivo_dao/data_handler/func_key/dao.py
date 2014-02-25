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

from xivo_dao.data_handler.exception import ElementNotExistsError
from xivo_dao.data_handler.utils.search import SearchFilter
from xivo_dao.helpers.abstract_model import SearchResult
from xivo_dao.helpers.db_manager import daosession
from xivo_dao.data_handler.func_key.model import db_converter, FuncKey
from xivo_dao.alchemy.func_key import FuncKey as FuncKeySchema
from xivo_dao.alchemy.func_key_type import FuncKeyType as FuncKeyTypeSchema
from xivo_dao.alchemy.func_key_dest_user import FuncKeyDestUser as FuncKeyDestUserSchema
from xivo_dao.alchemy.func_key_destination_type import FuncKeyDestinationType as FuncKeyDestinationTypeSchema


@daosession
def search(session, term=None, limit=None, skip=None, order=None, direction='asc'):
    query = _func_key_query(session)
    search_filter = SearchFilter(query, FuncKey.SEARCH_COLUMNS, FuncKeySchema.id)
    rows, total = search_filter.search(term, limit, skip, order, direction)

    func_keys = [db_converter.to_model(row) for row in rows]
    return SearchResult(total, func_keys)


@daosession
def get(session, func_key_id):
    query = _func_key_query(session)
    row = query.filter(FuncKeySchema.id == func_key_id).first()

    if not row:
        raise ElementNotExistsError('FuncKey')

    return db_converter.to_model(row)


@daosession
def type_exists(session, name):
    count = _count_using_name(session, FuncKeyTypeSchema, name)
    return count > 0


@daosession
def destination_type_exists(session, name):
    count = _count_using_name(session, FuncKeyDestinationTypeSchema, name)
    return count > 0


def _count_using_name(session, schema, name):
    return (session.query(schema)
            .filter(schema.name == name)
            .count())


def _func_key_query(session):
    query = (session
             .query(FuncKeySchema.id,
                    FuncKeyTypeSchema.name.label('type'),
                    FuncKeyDestinationTypeSchema.name.label('destination'),
                    FuncKeyDestUserSchema.user_id.label('destination_id'))
             .join(FuncKeyTypeSchema)
             .join(FuncKeyDestinationTypeSchema)
             .join(FuncKeyDestUserSchema, FuncKeyDestUserSchema.func_key_id == FuncKeySchema.id))
    return query
