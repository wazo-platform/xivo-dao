# -*- coding: utf-8 -*-

# Copyright (C) 2012-2014 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

import json
from xivo_dao.alchemy.cti_contexts import CtiContexts
from xivo_dao.alchemy.ctireversedirectories import CtiReverseDirectories
from xivo_dao.helpers.db_manager import daosession


@daosession
def get_config(session):
    res = {}
    rows = session.query(CtiContexts).all()
    for row in rows:
        res[row.name] = {}
        res[row.name]['directories'] = row.directories.split(',')
        res[row.name]['display'] = row.display
    rows = session.query(CtiReverseDirectories).all()
    for row in rows:
        res['*'] = {}
        res['*']['didextens'] = {}
        res['*']['didextens']['*'] = json.loads(row.directories)
    return res


@daosession
def get_context_names(session):
    rows = session.query(CtiContexts.name).all()

    return [row.name for row in rows]
