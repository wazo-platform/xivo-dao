# -*- coding: utf-8 -*-
# Copyright 2015-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import Integer
from sqlalchemy.sql import cast

from xivo_dao.helpers.db_manager import daosession
from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.alchemy.linefeatures import LineFeatures
from xivo_dao.alchemy.user_line import UserLine
from xivo_dao.alchemy.userfeatures import UserFeatures


@daosession
def find_by_incall_id(session, incall_id):
    row = (
        session.query(UserFeatures.uuid.label('xivo_user_uuid'), LineFeatures.context.label('profile'))
        .filter(
            Dialaction.category == 'incall',
            Dialaction.categoryval == str(incall_id),
            Dialaction.action == 'user',
            UserFeatures.id == cast(Dialaction.actionarg1, Integer),
            UserLine.user_id == UserFeatures.id,
            UserLine.line_id == LineFeatures.id,
            UserLine.main_line.is_(True),
            UserLine.main_user.is_(True),
        )
    ).first()
    return row
