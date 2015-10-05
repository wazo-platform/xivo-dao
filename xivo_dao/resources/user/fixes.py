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
from xivo_dao.alchemy.voicemail import Voicemail

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


class UserFixes(object):

    def __init__(self, session):
        self.session = session

    def fix_user(self, user_id):
        self.adjust_line(user_id)
        self.adjust_voicemail(user_id)
        self.adjust_extension(user_id)
        self.session.flush()

    def adjust_line(self, user_id):
        protocol, protocol_id = self.find_protocol(user_id)
        if protocol:
            if protocol == 'sip':
                self.fix_sip_line(user_id, protocol_id)
            elif protocol == 'sccp':
                self.fix_sccp_line(user_id, protocol_id)

    def find_protocol(self, user_id):
        query = (self.session
                 .query(Line.protocol,
                        Line.protocolid)
                 .join(UserLine, UserLine.line_id == Line.id)
                 .filter(UserLine.user_id == user_id)
                 .filter(UserLine.main_user == True)
                 .filter(UserLine.main_line == True))

        row = query.first()
        return (row.protocol, row.protocolid) if row else (None, None)

    def fix_sip_line(self, user_id, usersip_id):
        callerid = self.get_callerid(user_id)
        updates = {'callerid': callerid,
                   'setvar': 'XIVO_USERID={}'.format(user_id)}

        (self.session
         .query(UserSIP)
         .filter(UserSIP.id == usersip_id)
         .update(updates))

    def get_callerid(self, user_id):
        return (self.session
                .query(User.callerid)
                .filter(User.id == user_id)
                .scalar())

    def fix_sccp_line(self, user_id, protocol_id):
        callerid = self.get_callerid(user_id)
        match = caller_id_regex.match(callerid)
        if match:
            (self.session
             .query(SCCPLine)
             .filter(SCCPLine.id == protocol_id)
             .update({'cid_name': match.group('name'),
                      'cid_num': match.group('num')}))

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
                      (User.firstname + " " + User.lastname).label('fullname'))
               .filter(User.id == user_id)
               .first())
        return row.voicemailid, row.fullname.strip()

    def adjust_extension(self, user_id):
        extension_id = self.find_extension_id(user_id)
        if extension_id:
            (self.session
             .query(Extension)
             .filter(Extension.id == extension_id)
             .update({'type': 'user',
                      'typeval': str(user_id)}))

    def find_extension_id(self, user_id):
        return (self.session
                .query(Extension.id)
                .join(UserLine, UserLine.extension_id == Extension.id)
                .filter(UserLine.user_id == user_id)
                .filter(UserLine.main_user == True)
                .filter(UserLine.main_line == True)
                .scalar())
