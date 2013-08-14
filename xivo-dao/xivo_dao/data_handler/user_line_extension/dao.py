# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Avencall
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

from xivo_dao.alchemy.user_line import UserLine as ULESchema
from xivo_dao.helpers.db_manager import daosession
from xivo_dao.data_handler.exception import ElementNotExistsError, \
    ElementCreationError, ElementDeletionError, ElementEditionError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from model import UserLineExtension


@daosession
def get(session, ule_id):
    res = _new_query(session).filter(ULESchema.id == ule_id).first()

    if not res:
        raise ElementNotExistsError('UserLineExtension', id=ule_id)

    return UserLineExtension.from_data_source(res)


@daosession
def find_all(session):
    res = session.query(ULESchema).all()
    if not res:
        return []

    tmp = []
    for ule in res:
        tmp.append(UserLineExtension.from_data_source(ule))

    return tmp


@daosession
def find_all_by_user_id(session, user_id):
    ules = session.query(ULESchema).filter(ULESchema.user_id == user_id).all()
    return [UserLineExtension.from_data_source(ule) for ule in ules]


@daosession
def find_all_by_extension_id(session, extension_id):
    ules = session.query(ULESchema).filter(ULESchema.extension_id == extension_id).all()
    return [UserLineExtension.from_data_source(ule) for ule in ules]


@daosession
def find_all_by_line_id(session, line_id):
    ules = session.query(ULESchema).filter(ULESchema.line_id == line_id).all()
    return [UserLineExtension.from_data_source(ule) for ule in ules]


@daosession
def create(session, user_line_extension):
    user_line_extension_row = user_line_extension.to_data_source(ULESchema)
    session.begin()
    session.add(user_line_extension_row)

    try:
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        raise ElementCreationError('UserLineExtension', e)
    except IntegrityError as e:
        session.rollback()
        raise ElementCreationError('UserLineExtension', e)

    user_line_extension.id = user_line_extension_row.id

    return user_line_extension


@daosession
def edit(session, user_line_extension):
    session.begin()
    nb_row_affected = (session.query(ULESchema)
                       .filter(ULESchema.id == user_line_extension.id)
                       .update(user_line_extension.to_data_dict()))

    try:
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        raise ElementEditionError('UserLineExtension', e)

    if nb_row_affected == 0:
        raise ElementEditionError('UserLineExtension', 'user_line_extension_id %s not exsit' % user_line_extension.id)

    return nb_row_affected


@daosession
def delete(session, user_line_extension):
    session.begin()
    try:
        nb_row_affected = session.query(ULESchema).filter(ULESchema.id == user_line_extension.id).delete()
        session.commit()
    except SQLAlchemyError, e:
        session.rollback()
        raise ElementDeletionError('UserLineExtension', e)

    if nb_row_affected == 0:
        raise ElementDeletionError('UserLineExtension', 'user_line_extension_id %s not exsit' % user_line_extension.id)

    return nb_row_affected


def _new_query(session):
    return session.query(ULESchema)
