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
from xivo_dao.alchemy.extenumber import ExteNumber
from xivo_dao.alchemy.linefeatures import LineFeatures as LineSchema
from xivo_dao.alchemy.user_line import UserLine as UserLineSchema
from xivo_dao.helpers.db_manager import daosession
from xivo_dao.models.line import Line


@daosession
def get_line_by_user_id(session, user_id):
    line = (_new_query(session)
        .filter(UserLineSchema.user_id == user_id)
        .filter(UserLineSchema.line_id == LineSchema.id)
    ).first()

    if not line:
        raise LookupError('No line associated with user %s' % user_id)

    return Line.from_data_source(line)


@daosession
def get_line_by_number_context(session, number, context):
    line = (_new_query(session)
        .join((ExteNumber, and_(
            ExteNumber.type == 'user',
            LineSchema.id == cast(ExteNumber.typeval, Integer))))
        .filter(ExteNumber.exten == number)
        .filter(ExteNumber.context == context)
    ).first()

    if not line:
        raise LookupError('No line matching number %s in context %s' % (number, context))

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
def delete(session, line_id):
    session.begin()
    try:
        line = session.query(LineSchema).filter(LineSchema.id == line_id).first()
        """
        session.query(UserSIP).filter(UserSIP.id == line.protocolid).delete()
        (session.query(Extension).filter(Extension.exten == line.number)
                                 .filter(Extension.context == line.context)
                                 .delete())
        (session.query(ExteNumber).filter(ExteNumber.exten == line.number)
                                  .filter(ExteNumber.context == line.context)
                                  .delete())
        (session.query(ContextNumMember).filter(ContextNumMember.type == 'user')
                                        .filter(ContextNumMember.typeval == str(line.id))
                                        .filter(ContextNumMember.context == 'default')
                                        .delete())
        """
        session.delete(line)
        session.commit()
    except Exception:
        session.rollback()
        raise


def _new_query(session):
    return session.query(LineSchema).filter(LineSchema.commented == 0)
