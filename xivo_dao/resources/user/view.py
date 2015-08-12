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

from sqlalchemy.sql import and_, func

from xivo_dao.resources.utils.view import ViewSelector, View, ModelView
from xivo_dao.resources.user.model import UserDirectory
from xivo_dao.resources.user.database import db_converter

from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.linefeatures import LineFeatures
from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.alchemy.user_line import UserLine


class UserView(ModelView):

    table = UserFeatures
    db_converter = db_converter


class DirectoryView(View):

    def query(self, session):
        query = (session.query(UserFeatures.id.label('id'),
                               UserLine.line_id.label('line_id'),
                               UserFeatures.agentid.label('agent_id'),
                               UserFeatures.firstname.label('firstname'),
                               func.nullif(UserFeatures.lastname, '').label('lastname'),
                               func.nullif(UserFeatures.mobilephonenumber, '').label('mobile_phone_number'),
                               Extension.exten.label('exten'))
                 .outerjoin(UserLine,
                            and_(UserLine.user_id == UserFeatures.id))
                 .outerjoin(LineFeatures,
                            and_(LineFeatures.id == UserLine.line_id,
                                 LineFeatures.commented == 0))
                 .outerjoin(Extension,
                            and_(Extension.id == UserLine.extension_id,
                                 Extension.commented == 0)))
        return query

    def convert(self, row):
        return UserDirectory(id=row.id,
                             line_id=row.line_id,
                             agent_id=row.agent_id,
                             firstname=row.firstname,
                             lastname=row.lastname,
                             mobile_phone_number=row.mobile_phone_number,
                             exten=row.exten)


user_view = ViewSelector(default=UserView(),
                         directory=DirectoryView())
