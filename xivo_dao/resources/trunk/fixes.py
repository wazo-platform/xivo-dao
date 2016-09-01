# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
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

from xivo_dao.alchemy.trunkfeatures import TrunkFeatures
from xivo_dao.alchemy.usersip import UserSIP
from xivo_dao.alchemy.useriax import UserIAX
from xivo_dao.alchemy.usercustom import UserCustom


class TrunkFixes(object):

    def __init__(self, session):
        self.session = session

    def fix(self, trunk_id):
        row = self.get_row(trunk_id)
        self.fix_protocol(row)
        self.session.flush()

    def get_row(self, trunk_id):
        query = (self.session.query(TrunkFeatures,
                                    UserSIP,
                                    UserIAX,
                                    UserCustom)
                 .outerjoin(TrunkFeatures.sip_endpoint)
                 .outerjoin(TrunkFeatures.iax_endpoint)
                 .outerjoin(TrunkFeatures.custom_endpoint)
                 .options(
                     Load(TrunkFeatures).load_only("id", "context"),
                     Load(UserSIP).load_only("id", "context"),
                     Load(UserIAX).load_only("id", "context"),
                     Load(UserCustom).load_only("id", "context"))
                 .filter(TrunkFeatures.id == trunk_id)
                 )

        return query.first()

    def fix_protocol(self, row):
        protocol = row.TrunkFeatures.protocol
        if protocol == 'sip':
            self.fix_sip(row)
        elif protocol == 'iax':
            self.fix_iax(row)
        elif protocol == 'custom':
            self.fix_custom(row)
        else:
            self.remove_endpoint(row)

    def fix_sip(self, row):
        if row.UserSIP:
            row.UserSIP.context = row.TrunkFeatures.context
        else:
            self.remove_endpoint(row)

    def fix_iax(self, row):
        if row.UserIAX:
            row.UserIAX.context = row.TrunkFeatures.context
        else:
            self.remove_endpoint(row)

    def fix_custom(self, row):
        if row.UserCustom:
            row.UserCustom.context = row.TrunkFeatures.context
        else:
            self.remove_endpoint(row)

    def remove_endpoint(self, row):
        row.TrunkFeatures.remove_endpoint()
