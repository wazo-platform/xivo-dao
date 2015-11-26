# -*- coding: utf-8 -*-

# Copyright (C) 2012-2015 Avencall
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

import logging

from sqlalchemy import and_

from xivo_dao.alchemy.linefeatures import LineFeatures
from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.helpers.db_manager import daosession
from xivo_dao.alchemy.user_line import UserLine
from xivo_dao.alchemy.extension import Extension as ExtensionSchema

logger = logging.getLogger(__name__)


@daosession
def get(session, user_id):
    result = session.query(UserFeatures).filter(UserFeatures.id == int(user_id)).first()
    if result is None:
        raise LookupError()
    return result


@daosession
def get_user_by_number_context(session, exten, context):
    user = (session.query(UserFeatures)
            .join(ExtensionSchema, and_(ExtensionSchema.context == context,
                                        ExtensionSchema.exten == exten,
                                        ExtensionSchema.commented == 0))
            .join(LineFeatures, and_(LineFeatures.commented == 0))
            .join(UserLine, and_(UserLine.user_id == UserFeatures.id,
                                 UserLine.extension_id == ExtensionSchema.id,
                                 UserLine.line_id == LineFeatures.id,
                                 UserLine.main_line == True,
                                 UserLine.main_line == True))
            .first())

    if not user:
        raise LookupError('No user with number %s in context %s', (exten, context))

    return user
