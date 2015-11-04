# -*- coding: utf-8 -*-

# Copyright (C) 2015 Avencall
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

from xivo_dao.helpers.db_manager import daosession
from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.alchemy.linefeatures import LineFeatures
from xivo_dao.alchemy.user_line import UserLine
from xivo_dao.alchemy.userfeatures import UserFeatures


@daosession
def find_by_incall_id(session, incall_id):
    result = (session.query(UserFeatures.uuid, LineFeatures.context)
                     .filter(Dialaction.category == 'incall',
                             Dialaction.categoryval == str(incall_id),
                             Dialaction.action == 'user',
                             UserFeatures.id == cast(Dialaction.actionarg1, Integer),
                             UserLine.user_id == UserFeatures.id,
                             UserLine.line_id == LineFeatures.id,
                             UserLine.main_line == True,  # noqa
                             UserLine.main_user == True,  # noqa
                            )).first()
    if result is not None:
        return result.uuid, result.context
    return None
