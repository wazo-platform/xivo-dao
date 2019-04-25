# -*- coding: utf-8 -*-
# Copyright 2013-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import and_

from xivo_dao.alchemy.linefeatures import LineFeatures as LineSchema
from xivo_dao.alchemy.user_line import UserLine

from xivo_dao.helpers.db_manager import daosession


@daosession
def get_line_identity_by_user_id(session, user_id):
    row = (session.query(LineSchema.protocol,
                         LineSchema.name)
           .join(UserLine, and_(UserLine.line_id == LineSchema.id,
                                UserLine.user_id == int(user_id),
                                UserLine.main_user == True,  # noqa
                                UserLine.main_line == True))
           .first())
    if not row:
        raise LookupError('Could not find a line for user %s', user_id)
    elif row.protocol.lower() == 'custom':
        return row.name
    else:
        return '%s/%s' % (row.protocol, row.name)
