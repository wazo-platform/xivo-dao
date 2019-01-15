# -*- coding: utf-8 -*-
# Copyright (C) 2007-2015 Avencall
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.extension import Extension
from xivo_dao.helpers.db_manager import daosession


@daosession
def exten_by_name(session, funckey_name):
    exten = session.query(Extension.exten).filter(Extension.typeval == funckey_name).first()
    if exten is None:
        return ''
    return exten[0]
