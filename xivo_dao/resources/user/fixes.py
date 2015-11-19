# -*- coding: UTF-8 -*-

# Copyright (C) 2015 Avencall
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

from xivo_dao.alchemy.userfeatures import UserFeatures as User
from xivo_dao.alchemy.user_line import UserLine
from xivo_dao.alchemy.voicemail import Voicemail

from xivo_dao.resources.line.fixes import LineFixes


class UserFixes(object):

    def __init__(self, session):
        self.session = session

    def fix(self, user_id):
        self.fix_user(user_id)
        self.fix_line(user_id)
        self.session.flush()

    def fix_user(self, user_id):
        self.adjust_voicemail(user_id)

    def adjust_voicemail(self, user_id):
        voicemail_id, fullname = self.get_voicemail_id_and_fullname(user_id)
        if voicemail_id:
            (self.session
             .query(Voicemail)
             .filter(Voicemail.uniqueid == voicemail_id)
             .update({'fullname': fullname}))

    def get_voicemail_id_and_fullname(self, user_id):
        row = (self.session
               .query(User.voicemailid,
                      User.fullname.label('fullname'))
               .filter(User.id == user_id)
               .first())
        return row.voicemailid, row.fullname.strip()

    def fix_line(self, user_id):
        line_id = self.find_line_id(user_id)
        if line_id:
            LineFixes(self.session).fix(line_id)

    def find_line_id(self, user_id):
        return (self.session
                .query(UserLine.line_id)
                .filter(UserLine.main_user == True)  # noqa
                .filter(UserLine.main_line == True)
                .filter(UserLine.user_id == user_id)
                .scalar())
