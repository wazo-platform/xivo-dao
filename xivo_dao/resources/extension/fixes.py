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
from xivo_dao.alchemy.linefeatures import LineFeatures as Line


class ExtensionFixes(object):

    def __init__(self, session):
        self.session = session

    def fix_extension(self, extension_id):
        number, context = self.get_number_context(extension_id)
        line_id = self.find_line_id(extension_id)
        if line_id:
            self.update_line_number_and_context(line_id, number, context)
            self.session.flush()

    def get_number_context(self, extension_id):
        row = (self.session
               .query(Extension.exten,
                      Extension.context)
               .filter(Extension.id == extension_id)
               .first())
        return row.exten, row.context

    def find_line_id(self, extension_id):
        return (self.session
                .query(Line.id)
                .join(UserLine, UserLine.line_id == Line.id)
                .filter(UserLine.main_user == True)
                .filter(UserLine.main_line == True)
                .filter(UserLine.extension_id == extension_id)
                .scalar())

    def update_line_number_and_context(self, line_id, number, context):
        (self.session
         .query(Line)
         .filter(Line.id == line_id)
         .update({'number': number,
                  'context': context}))
