# -*- coding: utf-8 -*-
# Copyright 2015-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.orm import Load

from xivo_dao.alchemy.endpoint_sip import EndpointSIP
from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.line_extension import LineExtension
from xivo_dao.alchemy.linefeatures import LineFeatures
from xivo_dao.alchemy.queuemember import QueueMember
from xivo_dao.alchemy.sccpdevice import SCCPDevice
from xivo_dao.alchemy.sccpline import SCCPLine
from xivo_dao.alchemy.user_line import UserLine
from xivo_dao.alchemy.usercustom import UserCustom
from xivo_dao.alchemy.userfeatures import UserFeatures


class LineFixes(object):

    def __init__(self, session):
        self.session = session

    def fix(self, line_id):
        row = self.get_row(line_id)
        self.fix_number_and_context(row)
        self.fix_protocol(row)
        self.fix_name(row)
        self.fix_caller_id(row)
        self.session.flush()

    def fix_line(self, line_id):
        row = self.get_row(line_id)
        self.fix_number_and_context(row)
        self.fix_protocol(row)
        self.fix_name(row)
        self.session.flush()

    def get_row(self, line_id):
        query = (self.session.query(LineFeatures,
                                    EndpointSIP,
                                    SCCPLine,
                                    SCCPDevice,
                                    UserFeatures,
                                    UserCustom,
                                    Extension)
                 .outerjoin(LineFeatures.endpoint_sip)
                 .outerjoin(LineFeatures.endpoint_sccp)
                 .outerjoin(LineFeatures.endpoint_custom)
                 .outerjoin(SCCPDevice,
                            SCCPLine.name == SCCPDevice.line)
                 .outerjoin(LineFeatures.user_lines)
                 .outerjoin(UserLine.main_user_rel)
                 .outerjoin(LineFeatures.line_extensions)
                 .outerjoin(LineExtension.main_extension_rel)
                 .options(
                     Load(LineFeatures).load_only("id", "name", "number", "context"),
                     Load(EndpointSIP).load_only("uuid", "name"),
                     Load(SCCPLine).load_only("id", "name", "context", "cid_name", "cid_num"),
                     Load(SCCPDevice).load_only("id", "line"),
                     Load(UserFeatures).load_only("id", "firstname", "webi_lastname", "callerid"),
                     Load(UserCustom).load_only("id", "context"),
                     Load(Extension).load_only("id", "exten", "context"))
                 .filter(LineFeatures.id == line_id)
                 )

        return query.first()

    def fix_protocol(self, row):
        if row.EndpointSIP:
            interface = 'SIP/{}'.format(row.EndpointSIP.name)
            self.fix_queue_member(row, interface)
        elif row.SCCPLine:
            self.fix_sccp_line(row)
            interface = 'SCCP/{}'.format(row.SCCPLine.name)
            self.fix_queue_member(row, interface)
        elif row.UserCustom:
            row.UserCustom.context = row.LineFeatures.context
            self.fix_queue_member(row, row.UserCustom.interface)

    def fix_sccp_line(self, row):
        if row.Extension:
            row.SCCPLine.update_extension(row.Extension)

    def fix_number_and_context(self, row):
        if row.Extension:
            row.LineFeatures.update_extension(row.Extension)
        else:
            row.LineFeatures.clear_extension()

    def fix_name(self, row):
        row.LineFeatures.update_name()

    def fix_caller_id(self, row):
        if row.UserFeatures:
            if row.LineFeatures.endpoint_sip_uuid:
                row.EndpointSIP.update_caller_id(row.UserFeatures, row.Extension)
            elif row.LineFeatures.endpoint_sccp_id:
                row.SCCPLine.update_caller_id(row.UserFeatures, row.Extension)

    def fix_queue_member(self, row, interface):
        if row.UserFeatures and row.UserFeatures.lines:
            if row.UserFeatures.lines[0] == row.LineFeatures:
                (self.session.query(QueueMember)
                 .filter(QueueMember.usertype == 'user')
                 .filter(QueueMember.userid == row.UserFeatures.id)
                 .filter(QueueMember.channel != 'Local')
                 .update({'interface': interface}))

                if row.Extension:
                    local_interface = 'Local/{}@{}'.format(row.Extension.exten, row.Extension.context)
                    (self.session.query(QueueMember)
                     .filter(QueueMember.usertype == 'user')
                     .filter(QueueMember.userid == row.UserFeatures.id)
                     .filter(QueueMember.channel == 'Local')
                     .update({'interface': local_interface}))
