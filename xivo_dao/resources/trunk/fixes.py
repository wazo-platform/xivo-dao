# -*- coding: utf-8 -*-
# Copyright 2016-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.orm import Load

from xivo_dao.alchemy.endpoint_sip import EndpointSIP
from xivo_dao.alchemy.trunkfeatures import TrunkFeatures
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
                                    EndpointSIP,
                                    UserIAX,
                                    UserCustom)
                 .outerjoin(TrunkFeatures.endpoint_sip)
                 .outerjoin(TrunkFeatures.endpoint_iax)
                 .outerjoin(TrunkFeatures.endpoint_custom)
                 .options(
                     Load(TrunkFeatures).load_only("id", "context"),
                     Load(EndpointSIP),  # TODO(pc-m): filter only required fields
                     Load(UserIAX).load_only("id", "category", "context"),
                     Load(UserCustom).load_only("id", "category", "context"))
                 .filter(TrunkFeatures.id == trunk_id)
                 )

        return query.first()

    def fix_protocol(self, row):
        if row.EndpointSIP:
            row.EndpointSIP.context = row.TrunkFeatures.context_rel
        elif row.UserIAX:
            row.UserIAX.context = row.TrunkFeatures.context
            row.UserIAX.category = 'trunk'
        elif row.UserCustom:
            row.UserCustom.context = row.TrunkFeatures.context
            row.UserCustom.category = 'trunk'
