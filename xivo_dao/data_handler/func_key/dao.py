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

from sqlalchemy.sql import null, and_

from xivo_dao import alchemy as tbl

from xivo_dao.data_handler.func_key.model import Hint, Forward, ForwardTypeConverter
from xivo_dao.data_handler import errors
from xivo_dao.data_handler.utils.search import SearchResult
from xivo_dao.data_handler.exception import DataError
from xivo_dao.helpers.db_manager import daosession
from xivo_dao.helpers.db_utils import commit_or_abort
from xivo_dao.data_handler.func_key.database import db_converter, QueryHelper


@daosession
def search(session, **parameters):
    rows, total = QueryHelper(session).search(parameters)

    func_keys = [db_converter.to_model(row) for row in rows]
    return SearchResult(total, func_keys)


@daosession
def find_all_by_destination(session, destination, destination_id):
    if not QueryHelper.destination_exists(destination):
        return []

    query = QueryHelper(session).select_destination(destination, destination_id)

    func_key_rows = query.all()
    return [db_converter.to_model(row) for row in func_key_rows]


@daosession
def get(session, func_key_id):
    query = QueryHelper(session).select_func_key(func_key_id)
    row = query.first()

    if not row:
        raise errors.not_found('FuncKey', id=func_key_id)

    return db_converter.to_model(row)


@daosession
def create(session, func_key):
    func_key_row = db_converter.create_func_key_row(func_key)
    with commit_or_abort(session, DataError.on_create, 'FuncKey'):
        session.add(func_key_row)

    func_key.id = func_key_row.id

    destination_row = db_converter.create_destination_row(func_key)
    with commit_or_abort(session, DataError.on_create, 'FuncKey'):
        session.add(destination_row)

    return func_key


@daosession
def delete(session, func_key):
    helper = QueryHelper(session)
    func_key_query = helper.delete_func_key(func_key.id)
    destination_query = helper.delete_destination(func_key.destination,
                                                  func_key.destination_id)

    with commit_or_abort(session, DataError.on_delete, 'FuncKey'):
        destination_query.delete()
        func_key_query.delete()


@daosession
def find_all_hints(session, context):
    query = (
        session.query(
            tbl.UserFeatures.id.label('user_id'),
            tbl.Extension.typeval.label('type'),
            tbl.Extension.exten.label('exten'),
            null().label('number'))
        .join(tbl.UserLine,
              and_(
                  tbl.UserLine.user_id == tbl.UserFeatures.id,
                  tbl.UserLine.main_user == True))
        .join(tbl.LineFeatures,
              tbl.LineFeatures.id == tbl.UserLine.line_id)
        .join(tbl.FuncKeyMapping,
              tbl.FuncKeyMapping.template_id == tbl.UserFeatures.func_key_private_template_id)
        .join(tbl.FuncKeyDestService,
              and_(
                  tbl.FuncKeyMapping.func_key_id == tbl.FuncKeyDestService.func_key_id,
                  tbl.FuncKeyMapping.destination_type_id == tbl.FuncKeyDestService.destination_type_id))
        .join(tbl.Extension,
              tbl.FuncKeyDestService.extension_id == tbl.Extension.id)
        .filter(
            tbl.FuncKeyMapping.blf == True)
        .filter(
            tbl.LineFeatures.context == context)
    )

    return [Hint(user_id=row.user_id,
                 type=row.type,
                 exten=row.exten,
                 number=row.number)
            for row in query]


@daosession
def find_all_forwards(session, user_id, fwd_type):
    type_converter = ForwardTypeConverter()

    query = (session.query(tbl.FuncKeyDestForward.number.label('number'),
                           tbl.UserFeatures.id.label('user_id'),
                           tbl.Extension.typeval.label('type'))
             .join(tbl.Extension,
                   tbl.FuncKeyDestForward.extension_id == tbl.Extension.id)
             .join(tbl.FuncKeyMapping,
                   tbl.FuncKeyMapping.func_key_id == tbl.FuncKeyDestForward.func_key_id)
             .join(tbl.UserFeatures,
                   tbl.UserFeatures.func_key_private_template_id == tbl.FuncKeyMapping.template_id)
             .filter(tbl.UserFeatures.id == user_id)
             .filter(tbl.Extension.typeval == type_converter.model_to_db(fwd_type))
             )

    return [Forward(user_id=row.user_id,
                    type=type_converter.db_to_model(row.type),
                    number=row.number)
            for row in query]
