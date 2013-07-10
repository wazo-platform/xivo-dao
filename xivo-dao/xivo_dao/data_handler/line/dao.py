# -*- coding: utf-8 -*-

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

from sqlalchemy import Integer
from sqlalchemy.sql import and_, cast
from sqlalchemy.exc import SQLAlchemyError
from xivo_dao.alchemy.extenumber import ExteNumber
from xivo_dao.alchemy.linefeatures import LineFeatures as LineSchema
from xivo_dao.alchemy.usersip import UserSIP as UserSIPSchema
from xivo_dao.alchemy.user_line import UserLine as UserLineSchema
from xivo_dao.alchemy.extension import Extension
from xivo_dao.helpers.db_manager import daosession
from xivo_dao.data_handler.line.model import Line
from xivo_dao.data_handler.exception import ElementNotExistsError, \
    ElementDeletionError


@daosession
def get_by_user_id(session, user_id):
    line = (_new_query(session)
            .filter(UserLineSchema.user_id == user_id)
            .filter(UserLineSchema.line_id == LineSchema.id)
    ).first()

    if not line:
        raise ElementNotExistsError('Line', user_id=user_id)

    return Line.from_data_source(line)


@daosession
def get_by_number_context(session, number, context):
    line = (_new_query(session)
            .join((ExteNumber, and_(
                ExteNumber.type == 'user',
                LineSchema.id == cast(ExteNumber.typeval, Integer))))
        .filter(ExteNumber.exten == number)
        .filter(ExteNumber.context == context)
    ).first()

    if not line:
        raise ElementNotExistsError('Line', number=number, context=context)

    return Line.from_data_source(line)


@daosession
def find_line(session, number, context):
    line = (session.query(LineSchema)
            .filter(LineSchema.number == number)
            .filter(LineSchema.context == context)
            .first())

    if not line:
        return None

    return Line.from_data_source(line)


@daosession
def delete(session, line):
    session.begin()
    try:
        nb_row_affected = _delete_line()
        session.commit()
    except SQLAlchemyError, e:
        session.rollback()
        raise ElementDeletionError('Line', e)

    if nb_row_affected == 0:
        raise ElementDeletionError('Line', 'line_id %s not exsit' % line.id)

    return nb_row_affected


def _delete_line(session, line):
    result = (session.query(UserSIPSchema).filter(UserSIPSchema.id == line.protocolid).delete())
    (session.query(Extension).filter(Extension.exten == line.number)
                             .filter(Extension.context == line.context)
                             .delete())
    (session.query(ExteNumber).filter(ExteNumber.exten == line.number)
                              .filter(ExteNumber.context == line.context)
                              .delete())
    return result


def _new_query(session):
    return session.query(LineSchema).filter(LineSchema.commented == 0)
