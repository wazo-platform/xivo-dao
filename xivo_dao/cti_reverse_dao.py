# -*- coding: utf-8 -*-

# Copyright (C) 2015 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import json

from xivo_dao.alchemy.ctidirectories import CtiDirectories
from xivo_dao.alchemy.ctireversedirectories import CtiReverseDirectories
from xivo_dao.alchemy.directories import Directories
from xivo_dao.helpers.db_manager import daosession


@daosession
def get_config(session):
    rows = session.query(CtiReverseDirectories)
    sources = json.loads(rows.first().directories)
    if sources:
        rows = session.query(
            CtiDirectories.name,
            Directories.dirtype,
        ).join(
            Directories,
            Directories.uri == CtiDirectories.uri
        ).filter(CtiDirectories.name.in_(sources))
        name_to_type = {row.name: row.dirtype for row in rows.all()}
    else:
        name_to_type = {}

    types = [name_to_type.get(name, u'ldap') for name in sources]

    return {'sources': sources, 'types': types}
