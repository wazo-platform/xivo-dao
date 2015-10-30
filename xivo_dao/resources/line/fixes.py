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

from sqlalchemy import func

from xivo_dao.alchemy.userfeatures import UserFeatures as User
from xivo_dao.alchemy.linefeatures import LineFeatures as Line
from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.user_line import UserLine
from xivo_dao.alchemy.usersip import UserSIP
from xivo_dao.alchemy.sccpline import SCCPLine
from xivo_dao.alchemy.sccpdevice import SCCPDevice

caller_id_regex = re.compile(r'''
                             "                      #name start
                             (?P<name>[^"]+)        #inside ""
                             "                      #name end
                             \s*                    #space between name and number
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
        self.fix_protocol(line_id)
        self.fix_number_and_context(line_id)
        self.fix_name(line_id)
        self.session.flush()

    def fix_protocol(self, line_id):
        protocol, protocol_id = self.find_protocol(line_id)
        if protocol == 'sip':
            self.fix_sip(line_id, protocol_id)
        elif protocol == 'sccp':
            self.fix_sccp(line_id, protocol_id)
        else:
            self.remove_protocol(line_id)

    def find_protocol(self, line_id):
        row = (self.session
               .query(Line.protocol,
                      Line.protocolid,
                      UserSIP.id.label('sip_id'),
                      SCCPLine.id.label('sccp_id'))
               .outerjoin(Line.sip_endpoint)
               .outerjoin(Line.sccp_endpoint)
               .filter(Line.id == line_id)
               .first())

        if row.protocol == 'sip' and row.sip_id is None:
            return None, None
        elif row.protocol == 'sccp' and row.sccp_id is None:
            return None, None

        return row.protocol, row.protocolid

    def fix_sip(self, line_id, protocol_id):
        user_id, name, num = self.get_user_and_caller_id(line_id)
        context = self.get_line_context(line_id)

        setvar = 'XIVO_USERID={}'.format(user_id) if user_id else ''

        if name and num:
            caller_id = '"{}" <{}>'.format(name, num)
        elif name:
            caller_id = '"{}"'.format(name)
        else:
            caller_id = None

        self.update_usersip(protocol_id, caller_id, setvar, context)

    def update_usersip(self, protocol_id, caller_id, setvar, context):
        (self.session
         .query(UserSIP)
         .filter(UserSIP.id == protocol_id)
         .update({'callerid': caller_id,
                  'setvar': setvar,
                  'context': context}))

    def get_user_and_caller_id(self, line_id):
        row = (self.session
               .query(User.id,
                      User.callerid,
                      Extension.exten)
               .join(UserLine, UserLine.user_id == User.id)
               .outerjoin(Extension, UserLine.extension_id == Extension.id)
               .filter(UserLine.line_id == line_id)
               .filter(UserLine.main_user == True)  # noqa
               .filter(UserLine.main_line == True)
               .first())

        if row:
            name, num = self.extrapolate_caller_id(row)
            return row.id, name, num

        return None, None, None

    def get_line_context(self, line_id):
        return (self.session.query(Line.context)
                .filter(Line.id == line_id)
                .scalar())

    def extrapolate_caller_id(self, row):
        user_match = caller_id_regex.match(row.callerid)
        name = user_match.group('name')
        num = user_match.group('num')
        if not num:
            num = row.exten
        return name, num

    def fix_sccp(self, line_id, protocol_id):
        self.fix_sccp_device(line_id, protocol_id)
        self.fix_sccp_line(line_id, protocol_id)

    def fix_sccp_device(self, line_id, protocol_id):
        exten, context = self.find_exten_and_context(line_id)
        if exten and context:
            current_name = (self.session.query(Line.name)
                            .filter(Line.id == line_id)
                            .scalar())

            (self.session.query(SCCPDevice)
             .filter(SCCPDevice.line == current_name)
             .update({'line': exten}))

    def fix_sccp_line(self, line_id, protocol_id):
        _, cid_name, cid_num = self.get_user_and_caller_id(line_id)
        exten, context = self.find_exten_and_context(line_id)

        fields = {}

        if exten and context:
            fields['name'] = exten
            fields['context'] = context

        if cid_name:
            fields['cid_name'] = cid_name
            fields['cid_num'] = cid_num or ''

        self.update_sccpline(protocol_id, fields)

    def find_exten_and_context(self, line_id):
        row = (self.session.query(Extension.exten,
                                  Extension.context)
               .join(UserLine,
                     UserLine.extension_id == Extension.id)
               .join(Line,
                     Line.id == UserLine.line_id)
               .filter(UserLine.main_line == True)  # noqa
               .filter(UserLine.main_user == True)
               .first())

        if row:
            return row.exten, row.context
        return None, None

    def update_sccpline(self, protocol_id, fields):
        if fields:
            (self.session
             .query(SCCPLine)
             .filter(SCCPLine.id == protocol_id)
             .update(fields))

    def remove_protocol(self, line_id):
        (self.session.query(Line)
         .filter(Line.id == line_id)
         .update({'protocol': None,
                  'protocolid': None}))

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

    def fix_name(self, line_id):
        name = self.find_line_name(line_id)
        self.update_line_name(line_id, name)

    def find_line_name(self, line_id):
        return (self.session.query(func.coalesce(UserSIP.name, SCCPLine.name))
                .outerjoin(Line.sip_endpoint)
                .outerjoin(Line.sccp_endpoint)
                .filter(Line.id == line_id)
                .scalar())

    def update_line_name(self, line_id, name):
        (self.session.query(Line)
         .filter(Line.id == line_id)
         .update({'name': name}))
