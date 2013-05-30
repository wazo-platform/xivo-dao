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

from sqlalchemy.sql.expression import and_
from xivo_dao.alchemy.linefeatures import LineFeatures as LineSchema
from xivo_dao.helpers.db_manager import daosession
from xivo_dao.models.line import Line


def get_line_by_user_id(user_id):
    user_id_filter = LineSchema.iduserfeatures == user_id
    err_msg = 'No line associated with user %s' % user_id

    return _get_line_with_filter(user_id_filter, err_msg)


def get_line_by_number_context(number, context):
    number_context_filter = and_(LineSchema.number == number,
                                 LineSchema.context == context)
    err_msg = 'No line matching number %s in context %s' % (number, context)

    return _get_line_with_filter(number_context_filter, err_msg)


@daosession
def _get_line_with_filter(session, filter_, err_msg):
    line = (session
        .query(LineSchema)
        .filter(filter_)
        .filter(LineSchema.commented == 0)
        .first()
    )

    if not line:
        raise LookupError(err_msg)

    return Line.from_data_source(line)
