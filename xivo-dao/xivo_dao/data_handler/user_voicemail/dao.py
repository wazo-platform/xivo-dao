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

from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.data_handler.user_voicemail.model import db_converter
from xivo_dao.helpers.db_manager import daosession


@daosession
def associate(session, user_voicemail):
    user_row = (session.query(UserFeatures)
                .filter(UserFeatures.id == user_voicemail.user_id)
                .first())

    if user_row:
        user_row.voicemailid = user_voicemail.voicemail_id

        session.begin()
        session.add(user_row)
        session.commit()


@daosession
def find_all_by_user_id(session, user_id):
    query = (session.query(UserFeatures.id.label('user_id'),
                           UserFeatures.voicemailid.label('voicemail_id'))
             .filter(UserFeatures.id == user_id)
             .filter(UserFeatures.voicemailid != None))

    return [db_converter.to_model(row) for row in query]
