# -*- coding: utf-8 -*-
# Copyright 2015-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import unicode_literals

import json

from xivo_dao.alchemy.ctidirectories import CtiDirectories
from xivo_dao.alchemy.ctireversedirectories import CtiReverseDirectories
from xivo_dao.alchemy.directories import Directories
from xivo_dao.helpers.db_manager import daosession


@daosession
def get_config(session):
    row = (
        session
        .query(CtiReverseDirectories)
        .filter(CtiReverseDirectories.directories != '')
        .first()
    )

    sources = json.loads(row.directories) if row else []
    if sources:
        rows = session.query(
            CtiDirectories.name,
            Directories.dirtype,
        ).join(
            Directories,
        ).filter(CtiDirectories.name.in_(sources))
        name_to_type = {row.name: row.dirtype for row in rows.all()}
    else:
        name_to_type = {}

    types = [name_to_type.get(name, 'ldap') for name in sources]

    return {'sources': sources, 'types': types}
