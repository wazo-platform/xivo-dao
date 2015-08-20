# -*- coding: utf-8 -*-

# Copyright (C) 2012-2015 Avencall
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
from xivo_dao.alchemy.cti_displays import CtiDisplays
from xivo_dao.helpers.db_manager import daosession


@daosession
def get_config(session):
    rows = session.query(CtiDisplays)
    return {row.name: json.loads(row.data) for row in rows.all()}


@daosession
def get_profile_configuration(session):
    rows = session.query(
        CtiDisplays.name.label('display'),
        CtiContexts.name,
        CtiContexts.directories,
    ).join(
        CtiContexts,
        CtiContexts.display == CtiDisplays.name
    )

    return {row.name: {'display': row.display,
                       'sources': row.directories.split(',')} for row in rows.all()}
