# Copyright 2015-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.user_line import UserLine

from xivo_dao.resources.line.fixes import LineFixes


class UserFixes:
    def __init__(self, session):
        self.session = session

    def fix(self, user_id):
        self.fix_lines(user_id)
        self.session.flush()

    def fix_lines(self, user_id):
        user_lines = self.find_user_line(user_id)
        for user_line in user_lines:
            LineFixes(self.session).fix(user_line.line_id)

    def find_user_line(self, user_id):
        return (
            self.session.query(UserLine.line_id)
            .filter(UserLine.main_user == True)  # noqa
            .filter(UserLine.user_id == user_id)
            .all()
        )
