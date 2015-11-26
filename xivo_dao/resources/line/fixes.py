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

from sqlalchemy.orm import Load

from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.alchemy.linefeatures import LineFeatures
from xivo_dao.alchemy.user_line import UserLine
from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.usersip import UserSIP
from xivo_dao.alchemy.sccpline import SCCPLine
from xivo_dao.alchemy.sccpdevice import SCCPDevice


class LineFixes(object):

    def __init__(self, session):
        self.session = session

    def fix(self, line_id):
        query = (self.session.query(LineFeatures,
                                    UserSIP,
                                    SCCPLine,
                                    SCCPDevice,
                                    UserFeatures,
                                    Extension)
                 .outerjoin(LineFeatures.sip_endpoint)
                 .outerjoin(LineFeatures.sccp_endpoint)
                 .outerjoin(SCCPDevice,
                            SCCPLine.name == SCCPDevice.line)
                 .outerjoin(LineFeatures.user_lines)
                 .outerjoin(UserLine.main_user_rel)
                 .outerjoin(UserLine.main_extension_rel)
                 .options(
                     Load(LineFeatures).load_only("id", "name", "number", "context"),
                     Load(UserSIP).load_only("id", "callerid", "setvar", "context"),
                     Load(SCCPLine).load_only("id", "name", "context", "cid_name", "cid_num"),
                     Load(SCCPDevice).load_only("id", "line"),
                     Load(UserFeatures).load_only("id", "firstname", "webi_lastname", "callerid"),
                     Load(Extension).load_only("id", "exten", "context"))
                 .filter(LineFeatures.id == line_id)
                 )

        row = query.first()

        self.fix_protocol(row)
        self.fix_number_and_context(row)
        self.fix_name(row)
        self.session.flush()

    def fix_protocol(self, row):
        protocol = row.LineFeatures.protocol
        if protocol == 'sip':
            self.fix_sip(row)
        elif protocol == 'sccp':
            self.fix_sccp(row)
        else:
            self.remove_endpoint(row)

    def fix_sip(self, row):
        if row.UserSIP:
            self.update_usersip(row)
        else:
            self.remove_endpoint(row)

    def update_usersip(self, row):
        row.UserSIP.context = row.LineFeatures.context
        if row.UserFeatures:
            row.UserSIP.update_setvar(row.UserFeatures)
            row.UserSIP.update_caller_id(row.UserFeatures, row.Extension)
        else:
            row.UserSIP.clear_setvar()
            row.UserSIP.clear_caller_id()

    def remove_endpoint(self, row):
        row.LineFeatures.remove_endpoint()

    def fix_sccp(self, row):
        if row.SCCPLine:
            self.fix_sccp_device(row)
            self.fix_sccp_line(row)
        else:
            self.remove_endpoint(row)

    def fix_sccp_device(self, row):
        if row.Extension:
            (self.session.query(SCCPDevice)
             .filter(SCCPDevice.line == row.LineFeatures.name)
             .update({'line': row.Extension.exten}))

    def fix_sccp_line(self, row):
        if row.Extension:
            row.SCCPLine.update_extension(row.Extension)

        if row.UserFeatures:
            row.SCCPLine.update_caller_id(row.UserFeatures, row.Extension)

    def fix_number_and_context(self, row):
        if row.Extension:
            row.LineFeatures.update_extension(row.Extension)
        else:
            row.LineFeatures.clear_extension()

    def fix_name(self, row):
        row.LineFeatures.update_name()
