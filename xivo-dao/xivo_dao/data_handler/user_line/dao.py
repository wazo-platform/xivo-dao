# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from sqlalchemy.exc import SQLAlchemyError

from xivo_dao.alchemy.user_line import UserLine as UserLineSchema
from xivo_dao.data_handler.user_line.model import db_converter
from xivo_dao.data_handler.user_line.exception import UserLineNotExistsError
from xivo_dao.data_handler.exception import ElementCreationError, \
    ElementDeletionError
from xivo_dao.helpers.db_manager import daosession


@daosession
def get_by_user_id_and_line_id(session, user_id, line_id):
    row = (session.query(UserLineSchema)
           .filter(UserLineSchema.user_id == user_id)
           .filter(UserLineSchema.line_id == line_id)
           .first())

    if not row:
        raise UserLineNotExistsError('UserLine', user_id=user_id, line_id=line_id)

    return db_converter.to_model(row)


@daosession
def find_all_by_user_id(session, user_id):
    rows = (session.query(UserLineSchema)
            .filter(UserLineSchema.user_id == user_id)
            .all())

    if not rows:
        return []

    tmp = []
    for row in rows:
        tmp.append(db_converter.to_model(row))

    return tmp


@daosession
def find_main_user_line(session, user_line):
    row = (session.query(UserLineSchema)
           .filter(UserLineSchema.main_user == True)
           .filter(UserLineSchema.line_id == user_line.line_id)
           .first())

    if not row:
        return None

    return db_converter.to_model(row)


@daosession
def associate(session, user_line):
    session.begin()
    user_line_row = db_converter.to_source(user_line)
    try:
        session.add(user_line_row)
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        raise ElementCreationError('UserLine', e)

    user_line.id = user_line_row.id

    return user_line


@daosession
def dissociate(session, user_line):
    session.begin()
    try:
        (session.query(UserLineSchema)
                .filter(UserLineSchema.user_id == user_line.user_id)
                .filter(UserLineSchema.line_id == user_line.line_id)
                .delete())
        session.commit()
    except SQLAlchemyError, e:
        session.rollback()
        raise ElementDeletionError('UserLine', e)


@daosession
def line_has_secondary_user(session, user_line):
    count = (session.query(UserLineSchema)
             .filter(UserLineSchema.line_id == user_line.line_id)
             .filter(UserLineSchema.main_user == False)
             .count())

    return count > 0


@daosession
def extension_associated_to_this_user_line(session, user_line):
    row = (session.query(UserLineSchema.extension_id)
           .filter(UserLineSchema.user_id == user_line.user_id)
           .filter(UserLineSchema.line_id == user_line.line_id)
           .first())

    return row.extension_id is not None
