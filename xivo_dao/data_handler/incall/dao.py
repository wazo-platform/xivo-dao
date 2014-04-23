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

from sqlalchemy import Integer, cast, and_

from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.incall import Incall
from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.alchemy.user_line import UserLine
from xivo_dao.helpers.db_manager import daosession

from xivo_dao.data_handler.line_extension.model import db_converter as line_extension_db_converter


@daosession
def find_all_line_extensions_by_line_id(session, line_id):
    query = (session.query(UserLine.line_id,
                           Extension.id.label('extension_id'))
             .join(Dialaction,
                   and_(Dialaction.action == 'user',
                        cast(Dialaction.actionarg1, Integer) == UserLine.user_id,
                        UserLine.main_line == True))
             .join(Incall,
                   and_(Dialaction.category == 'incall',
                        cast(Dialaction.categoryval, Integer) == Incall.id))
             .join(Extension,
                   and_(Incall.exten == Extension.exten,
                        Incall.context == Extension.context))
             .filter(UserLine.line_id == line_id))

    return [line_extension_db_converter.to_model(row) for row in query]
