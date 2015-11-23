# -*- coding: utf-8 -*-

# Copyright (C) 2014-2015 Avencall
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

from sqlalchemy.sql import and_

from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.alchemy.linefeatures import LineFeatures
from xivo_dao.alchemy.voicemail import Voicemail
from xivo_dao.alchemy.user_line import UserLine
from xivo_dao.alchemy.extension import Extension
from xivo_dao.resources.utils.search import SearchSystem
from xivo_dao.resources.utils.search import SearchConfig


config = SearchConfig(table=UserFeatures,
                      columns={'firstname': UserFeatures.firstname,
                               'lastname': UserFeatures.lastname,
                               'fullname': (UserFeatures.firstname + " " + UserFeatures.lastname),
                               'caller_id': UserFeatures.callerid,
                               'description': UserFeatures.description,
                               'userfield': UserFeatures.userfield,
                               'mobile_phone_number': UserFeatures.mobilephonenumber,
                               'voicemail_number': Voicemail.mailbox,
                               'exten': Extension.exten},
                      search=['fullname', 'caller_id', 'description', 'userfield', 'mobile_phone_number', 'exten'],
                      default_sort='lastname')


class UserSearchSystem(SearchSystem):

    def search_from_query(self, query, parameters):
        query = self._search_on_extension(query)
        return super(UserSearchSystem, self).search_from_query(query, parameters)

    def _search_on_extension(self, query):
        return (query
                .outerjoin(UserLine,
                           UserLine.user_id == UserFeatures.id)
                .outerjoin(LineFeatures,
                           and_(LineFeatures.id == UserLine.line_id,
                                LineFeatures.commented == 0))
                .outerjoin(Extension,
                           and_(UserLine.extension_id == Extension.id,
                                Extension.commented == 0))
                .outerjoin(Voicemail,
                           and_(UserFeatures.voicemailid == Voicemail.uniqueid,
                                Voicemail.commented == 0)))


user_search = UserSearchSystem(config)
