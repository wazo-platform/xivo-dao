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

import cjson

from xivo_dao.helpers.db_manager import daosession

from xivo_dao.alchemy.cti_contexts import CtiContexts
from xivo_dao.alchemy.cti_displays import CtiDisplays

from sqlalchemy import and_


@daosession
def get_directory_headers(session, context):
    NAME_INDEX, TYPE_INDEX = 0, 1
    raw_display_data = session.query(
        CtiDisplays.data
    ).filter(
        and_(CtiContexts.name == context,
             CtiContexts.display == CtiDisplays.name)
    ).first()

    if not raw_display_data:
        return []

    display_data = cjson.decode(raw_display_data.data)

    indices = sorted(display_data.keys())

    results = []

    def already_in_list(new):
        for name, field_type in results:
            if new == name:
                return True
        return False

    for position in indices:
        entry = display_data[position]
        name = entry[NAME_INDEX]
        if already_in_list(name):
            continue
        field_type = 'number' if entry[TYPE_INDEX].startswith('number_') else entry[TYPE_INDEX]
        pair = name, field_type
        results.append(pair)

    return results
