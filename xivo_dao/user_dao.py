# Copyright 2012-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from sqlalchemy import and_

from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.line_extension import LineExtension
from xivo_dao.alchemy.linefeatures import LineFeatures
from xivo_dao.alchemy.user_line import UserLine
from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.helpers.db_manager import daosession

logger = logging.getLogger(__name__)


@daosession
def get(session, user_id):
    if isinstance(user_id, int):
        result = session.query(UserFeatures).filter(UserFeatures.id == user_id).first()
    else:
        result = (
            session
            .query(UserFeatures)
            .filter(UserFeatures.uuid == user_id)
            .first()
        )  # fmt: skip
    if result is None:
        raise LookupError()
    return result


@daosession
def get_user_by_agent_id(session, agent_id):
    result = (
        session.
        query(UserFeatures)
        .filter(UserFeatures.agent_id == agent_id)
        .first()
    )  # fmt: skip
    if not result:
        raise LookupError()
    return result


@daosession
def get_user_by_number_context(session, exten, context):
    user = (
        session.query(UserFeatures)
        .join(
            Extension,
            and_(
                Extension.context == context,
                Extension.exten == exten,
                Extension.commented == 0,
            ),
        )
        .join(LineExtension, LineExtension.extension_id == Extension.id)
        .join(
            UserLine,
            and_(
                UserLine.user_id == UserFeatures.id,
                UserLine.line_id == LineExtension.line_id,
                UserLine.main_line == True,  # noqa
            ),
        )
        .join(LineFeatures, and_(LineFeatures.commented == 0))
        .first()
    )

    if not user:
        raise LookupError('No user with number %s in context %s', (exten, context))

    return user
