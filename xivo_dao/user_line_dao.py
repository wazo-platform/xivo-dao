# -*- coding: utf-8 -*-
# Copyright 2013-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import and_

from xivo_dao.alchemy.linefeatures import LineFeatures as LineSchema
from xivo_dao.alchemy.user_line import UserLine

from xivo_dao.helpers.db_manager import daosession


@daosession
def get_line_identity_by_user_id(session, user_id):
    row = (session.query(LineSchema.endpoint_sip_uuid,
                         LineSchema.endpoint_sccp_id,
                         LineSchema.endpoint_custom_id,
                         LineSchema.name)
           .join(UserLine, and_(UserLine.line_id == LineSchema.id,
                                UserLine.user_id == int(user_id),
                                UserLine.main_user == True,  # noqa
                                UserLine.main_line == True))
           .first())
    if not row:
        raise LookupError('Could not find a line for user %s', user_id)
    elif row.endpoint_sip_uuid:
        return 'sip/{}'.format(row.name)
    elif row.endpoint_sccp_id:
        return 'sccp/{}'.format(row.name)
    elif row.endpoint_custom_id:
        return row.name
    raise LookupError('Could not find a endpoint for user %s', user_id)
