# -*- coding: utf-8 -*-

# Copyright (C) 2012-2013 Avencall
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
