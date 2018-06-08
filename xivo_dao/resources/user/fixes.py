# -*- coding: utf-8 -*-
# Copyright (C) 2015-2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.alchemy.userfeatures import UserFeatures as User
from xivo_dao.alchemy.user_line import UserLine
from xivo_dao.alchemy.voicemail import Voicemail

from xivo_dao.resources.line.fixes import LineFixes


class UserFixes(object):

    def __init__(self, session):
        self.session = session

    def fix(self, user_id):
        self.fix_user(user_id)
        self.fix_lines(user_id)
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

    def fix_lines(self, user_id):
        user_lines = self.find_user_line(user_id)
        for user_line in user_lines:
            LineFixes(self.session).fix(user_line.line_id)

    def find_user_line(self, user_id):
        return (self.session
                .query(UserLine.line_id)
                .filter(UserLine.main_user == True)  # noqa
                .filter(UserLine.user_id == user_id)
                .all())
