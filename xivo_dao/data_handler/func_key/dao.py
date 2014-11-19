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

from sqlalchemy import Integer
from sqlalchemy.sql import cast

from xivo_dao import alchemy as tbl

from xivo_dao.data_handler.func_key.model import UserFuncKey, Forward, ForwardTypeConverter, BSFilterFuncKey
from xivo_dao.data_handler.exception import DataError
from xivo_dao.helpers.db_manager import daosession
from xivo_dao.helpers.db_utils import commit_or_abort
from xivo_dao.data_handler.func_key.database import func_key_manager


@daosession
def create(session, func_key):
    repository = func_key_manager.for_func_key(func_key)
    with commit_or_abort(session, DataError.on_create, 'FuncKey'):
        created_func_key = repository.create(session, func_key)
    return created_func_key


@daosession
def delete(session, func_key):
    repository = func_key_manager.for_func_key(func_key)
    with commit_or_abort(session, DataError.on_delete, 'FuncKey'):
        repository.delete(session, func_key)


@daosession
def find_user_destination(session, user_id):
    row = (session
           .query(tbl.FuncKeyDestUser.func_key_id,
                  tbl.FuncKeyDestUser.user_id)
           .filter(tbl.FuncKeyDestUser.user_id == user_id)
           .first())

    if not row:
        return None

    return UserFuncKey(id=row.func_key_id,
                       user_id=row.user_id)


@daosession
def find_bsfilter_destinations_for_user(session, user_id):
    query = (session
             .query(tbl.FuncKeyDestBSFilter.func_key_id,
                    tbl.Callfiltermember.callfilterid.label('filter_id'),
                    cast(tbl.Callfiltermember.typeval, Integer).label('secretary_id'))
             .join(tbl.Callfiltermember,
                   tbl.FuncKeyDestBSFilter.filtermember_id == tbl.Callfiltermember.id)
             .filter(cast(tbl.Callfiltermember.typeval, Integer) == user_id))

    return [BSFilterFuncKey(id=row.func_key_id,
                            filter_id=row.filter_id,
                            secretary_id=row.secretary_id)
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
