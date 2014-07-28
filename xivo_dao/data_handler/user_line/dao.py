# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
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

from sqlalchemy.exc import SQLAlchemyError


from xivo_dao.alchemy.user_line import UserLine as UserLineSchema
from xivo_dao.data_handler.line_extension import dao as line_extension_dao
from xivo_dao.data_handler.user_line_extension import dao as ule_dao
from xivo_dao.data_handler.user_line.model import db_converter
from xivo_dao.data_handler.user_line.exception import UserLineNotExistsError
from xivo_dao.data_handler.exception import ElementCreationError, \
    ElementDeletionError
from xivo_dao.helpers.db_manager import daosession


@daosession
def find_by_user_id_and_line_id(session, user_id, line_id):
    row = (session.query(UserLineSchema)
           .filter(UserLineSchema.user_id == user_id)
           .filter(UserLineSchema.line_id == line_id)
           .first())

    if not row:
        return None

    return db_converter.to_model(row)


@daosession
def get_by_user_id_and_line_id(session, user_id, line_id):
    user_line = find_by_user_id_and_line_id(user_id, line_id)

    if not user_line:
        raise UserLineNotExistsError('UserLine', user_id=user_id, line_id=line_id)

    return user_line


@daosession
def find_all_by_user_id(session, user_id):
    rows = (session.query(UserLineSchema)
            .filter(UserLineSchema.user_id == user_id)
            .all())

    if not rows:
        return []

    return [db_converter.to_model(row) for row in rows]


@daosession
def find_all_by_line_id(session, line_id):
    rows = (session.query(UserLineSchema)
            .filter(UserLineSchema.line_id == line_id)
            .filter(UserLineSchema.user_id != None)
            .all())

    if not rows:
        return []

    return [db_converter.to_model(row) for row in rows]


@daosession
def find_main_user_line(session, line_id):
    row = (session.query(UserLineSchema)
           .filter(UserLineSchema.main_user == True)
           .filter(UserLineSchema.line_id == line_id)
           .filter(UserLineSchema.user_id != None)
           .first())

    if not row:
        return None

    return db_converter.to_model(row)


@daosession
def associate(session, user_line):
    session.begin()
    try:
        user_line_id = _associate_user_line(session, user_line)
    except SQLAlchemyError as e:
        session.rollback()
        raise ElementCreationError('UserLine', e)

    user_line.id = user_line_id

    return user_line


def _associate_user_line(session, user_line):
    count = (session.query(UserLineSchema)
             .filter(UserLineSchema.line_id == user_line.line_id)
             .filter(UserLineSchema.user_id == None)
             .count())

    if count == 0:
        _create_user_line(session, user_line)
    else:
        _update_user_line(session, user_line)

    session.commit()

    return _find_user_line_id(session, user_line)


def _create_user_line(session, user_line):
    user_line_row = db_converter.to_source(user_line)
    line_extension = line_extension_dao.find_by_line_id(user_line.line_id)
    if line_extension:
        user_line_row.extension_id = line_extension.extension_id
    session.add(user_line_row)


def _update_user_line(session, user_line):
    (session.query(UserLineSchema)
     .filter(UserLineSchema.user_id == None)
     .filter(UserLineSchema.line_id == user_line.line_id)
     .update({'user_id': user_line.user_id}))


def _find_user_line_id(session, user_line):
    return (session.query(UserLineSchema.id)
            .filter(UserLineSchema.user_id == user_line.user_id)
            .filter(UserLineSchema.line_id == user_line.line_id)
            .first()).id


@daosession
def dissociate(session, user_line):
    session.begin()
    try:
        _dissasociate_user_line(session, user_line)
        ule_dao.delete_association_if_necessary(session)
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        raise ElementDeletionError('UserLine', e)


def _dissasociate_user_line(session, user_line):
    query = (session.query(UserLineSchema)
             .filter(UserLineSchema.user_id == user_line.user_id)
             .filter(UserLineSchema.line_id == user_line.line_id))
    if line_has_secondary_user(user_line):
        query.delete()
    else:
        query.update({'user_id': None})


@daosession
def line_has_secondary_user(session, user_line):
    count = (session.query(UserLineSchema)
             .filter(UserLineSchema.line_id == user_line.line_id)
             .filter(UserLineSchema.main_user == False)
             .count())

    return count > 0
