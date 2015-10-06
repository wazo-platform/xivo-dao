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

from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.user_line import UserLine
from xivo_dao.resources.line.fixes import LineFixes


class ExtensionFixes(object):

    def __init__(self, session):
        self.session = session

    def fix(self, extension_id):
        self.fix_extension(extension_id)
        self.fix_line(extension_id)
        self.session.flush()

    def fix_extension(self, extension_id):
        user_id, _ = self.find_user_and_line_id(extension_id)
        if user_id:
            self.adjust_destination(extension_id, user_id)
        else:
            self.reset_destination(extension_id)

    def fix_line(self, extension_id):
        _, line_id = self.find_user_and_line_id(extension_id)
        if line_id:
            self.adjust_line(line_id)

    def find_user_and_line_id(self, extension_id):
        row = (self.session
               .query(UserLine.user_id,
                      UserLine.line_id)
               .filter(UserLine.main_user == True)  # noqa
               .filter(UserLine.main_line == True)
               .filter(UserLine.extension_id == extension_id)
               .first())

        return (row.user_id, row.line_id) if row else (None, None)

    def adjust_destination(self, extension_id, user_id):
        (self.session
         .query(Extension)
         .filter(Extension.id == extension_id)
         .update({'type': 'user',
                  'typeval': str(user_id)}))

    def reset_destination(self, extension_id):
        destination = self.get_destination(extension_id)
        if destination == 'user':
            self.remove_destination_id(extension_id)

    def get_destination(self, extension_id):
        return (self.session
                .query(Extension.type)
                .filter(Extension.id == extension_id)
                .scalar())

    def remove_destination_id(self, extension_id):
            (self.session
             .query(Extension)
             .filter(Extension.id == extension_id)
             .update({'typeval': '0'}))

    def adjust_line(self, line_id):
        LineFixes(self.session).fix(line_id)
