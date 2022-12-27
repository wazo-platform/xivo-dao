# Copyright 2012-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.context import Context
from xivo_dao.helpers.db_manager import daosession


@daosession
def get(session, context_name):
    return session.query(Context).filter(Context.name == context_name).first()
