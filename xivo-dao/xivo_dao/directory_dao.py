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
    raw_display_data = session.query(
        CtiDisplays.data
    ).filter(
        and_(CtiContexts.name == context,
             CtiContexts.display == CtiDisplays.name)
    )

    display_data = [cjson.decode(display.data) for display in raw_display_data.all()]

    results = []

    for display in display_data:
        for entry in display.itervalues():
            results.append(entry[0])

    return list(set(results))
