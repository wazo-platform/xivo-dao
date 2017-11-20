# -*- coding: UTF-8 -*-
# Copyright (C) 2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

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
                 .outerjoin(TrunkFeatures.endpoint_sip)
                 .outerjoin(TrunkFeatures.endpoint_iax)
                 .outerjoin(TrunkFeatures.endpoint_custom)
                 .options(
                     Load(TrunkFeatures).load_only("id", "context"),
                     Load(UserSIP).load_only("id", "category", "context"),
                     Load(UserIAX).load_only("id", "category", "context"),
                     Load(UserCustom).load_only("id", "category", "context"))
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
            row.UserSIP.category = 'trunk'
        else:
            self.remove_endpoint(row)

    def fix_iax(self, row):
        if row.UserIAX:
            row.UserIAX.context = row.TrunkFeatures.context
            row.UserIAX.category = 'trunk'
        else:
            self.remove_endpoint(row)

    def fix_custom(self, row):
        if row.UserCustom:
            row.UserCustom.context = row.TrunkFeatures.context
            row.UserCustom.category = 'trunk'
        else:
            self.remove_endpoint(row)

    def remove_endpoint(self, row):
        row.TrunkFeatures.remove_endpoint()
