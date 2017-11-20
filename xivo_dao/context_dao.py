# -*- coding: utf-8 -*-
# Copyright (C) 2012-2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.alchemy.context import Context
from xivo_dao.helpers.db_manager import daosession


@daosession
def get(session, context_name):
    return session.query(Context).filter(Context.name == context_name).first()
