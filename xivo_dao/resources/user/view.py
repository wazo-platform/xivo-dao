# -*- coding: utf-8 -*-

# Copyright (C) 2014-2016 Avencall
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

from sqlalchemy.sql import func

from xivo_dao.resources.utils.view import ViewSelector, View
from xivo_dao.resources.user.model import UserDirectory

from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.userfeatures import UserFeatures as User
from xivo_dao.alchemy.voicemail import Voicemail
from xivo_dao.alchemy.user_line import UserLine


class UserView(View):

    def query(self, session):
        return session.query(User)

    def convert(self, model):
        return model


class DirectoryView(View):

    def query(self, session):
        query = (session.query(User.id.label('id'),
                               UserLine.line_id.label('line_id'),
                               User.agentid.label('agent_id'),
                               User.firstname.label('firstname'),
                               func.nullif(User.lastname, '').label('lastname'),
                               func.nullif(User.email, '').label('email'),
                               func.nullif(User.mobilephonenumber, '').label('mobile_phone_number'),
                               Voicemail.mailbox.label('voicemail_number'),
                               func.nullif(User.userfield, '').label('userfield'),
                               func.nullif(User.description, '').label('description'),
                               Extension.exten.label('exten'),
                               Extension.context.label('context')))
        return query

    def convert(self, row):
        return UserDirectory(id=row.id,
                             line_id=row.line_id,
                             agent_id=row.agent_id,
                             firstname=row.firstname,
                             lastname=row.lastname,
                             email=row.email,
                             mobile_phone_number=row.mobile_phone_number,
                             voicemail_number=row.voicemail_number,
                             exten=row.exten,
                             userfield=row.userfield,
                             description=row.description,
                             context=row.context)


user_view = ViewSelector(default=UserView(),
                         directory=DirectoryView())
