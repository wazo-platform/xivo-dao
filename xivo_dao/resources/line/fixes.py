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

import re

from xivo_dao.alchemy.userfeatures import UserFeatures as User
from xivo_dao.alchemy.linefeatures import LineFeatures as Line
from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.user_line import UserLine
from xivo_dao.alchemy.usersip import UserSIP
from xivo_dao.alchemy.sccpline import SCCPLine

caller_id_regex = re.compile(r'''
                             "                      #name start
                             (?P<name>[^"]+)        #inside ""
                             "                      #name end
                             \s+                    #space between name and number
                             (
                             <                      #number start
                             (?P<num>\+?[\dA-Z]+)   #inside <>
                             >                      #number end
                             )?                     #number is optional
                             ''', re.VERBOSE)


class LineFixes(object):

    def __init__(self, session):
        self.session = session

    def fix(self, line_id):
        self.fix_caller_id(line_id)
        self.fix_number_and_context(line_id)
        self.session.flush()

    def fix_caller_id(self, line_id):
        protocol, protocol_id = self.find_protocol(line_id)
        if protocol:
            if protocol == 'sip':
                self.fix_sip_caller_id(line_id, protocol_id)
            elif protocol == 'sccp':
                self.fix_sccp_caller_id(line_id, protocol_id)

    def find_protocol(self, line_id):
        row = (self.session
               .query(Line.protocol,
                      Line.protocolid)
               .filter(Line.id == line_id)
               .first())

        return row.protocol, row.protocolid

    def fix_sip_caller_id(self, line_id, protocol_id):
        user_id, caller_id = self.get_user_and_caller_id(line_id)
        setvar = 'XIVO_USERID={}'.format(user_id) if user_id else ''
        self.update_usersip(protocol_id, caller_id, setvar)

    def update_usersip(self, protocol_id, caller_id, setvar):
        (self.session
         .query(UserSIP)
         .filter(UserSIP.id == protocol_id)
         .update({'callerid': caller_id,
                  'setvar': setvar}))

    def get_user_and_caller_id(self, line_id):
        row = (self.session
               .query(User.id,
                      User.callerid)
               .join(UserLine, UserLine.user_id == User.id)
               .filter(UserLine.line_id == line_id)
               .filter(UserLine.main_user == True)  # noqa
               .filter(UserLine.main_line == True)
               .first())

        return (row.id, row.callerid) if row else (None, None)

    def fix_sccp_caller_id(self, line_id, protocol_id):
        _, caller_id = self.get_user_and_caller_id(line_id)
        match = caller_id_regex.match(caller_id)
        if match:
            self.update_sccpline(protocol_id,
                                 match.group('name'),
                                 match.group('num'))

    def update_sccpline(self, protocol_id, name, num):
        (self.session
         .query(SCCPLine)
         .filter(SCCPLine.id == protocol_id)
         .update({'cid_name': name,
                  'cid_num': num}))

    def fix_number_and_context(self, line_id):
        number, context = self.find_number_and_context(line_id)
        if number:
            self.update_number_and_context(line_id, number, context)
        else:
            self.remove_number(line_id)

    def find_number_and_context(self, line_id):
        row = (self.session
               .query(Extension.exten,
                      Extension.context)
               .join(UserLine, UserLine.extension_id == Extension.id)
               .filter(UserLine.main_user == True)  # noqa
               .filter(UserLine.main_line == True)
               .filter(UserLine.line_id == line_id)
               .first())

        return (row.exten, row.context) if row else (None, None)

    def update_number_and_context(self, line_id, number, context):
        (self.session
         .query(Line)
         .filter(Line.id == line_id)
         .update({'number': number,
                  'context': context}))

    def remove_number(self, line_id):
        (self.session
         .query(Line)
         .filter(Line.id == line_id)
         .update({'number': ''}))
