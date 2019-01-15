# -*- coding: utf-8 -*-
# Copyright (C) 2015 Avencall
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.sql.expression import and_
from xivo_dao.alchemy.accessfeatures import AccessFeatures
from xivo_dao.helpers.db_manager import daosession


@daosession
def get_authorized_subnets(session):
    rows = (session
            .query(AccessFeatures.host)
            .filter(and_(AccessFeatures.feature == 'phonebook',
                         AccessFeatures.commented == 0))
            .all())
    return [row.host for row in rows]
