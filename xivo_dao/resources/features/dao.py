# -*- coding: UTF-8 -*-

# Copyright (C) 2015 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from xivo_dao.alchemy.features import Features
from xivo_dao.helpers.db_manager import daosession
from xivo_dao.resources.features.database import transfer_converter


@daosession
def find_all_transfer_extensions(session):
    query = (session.query(Features.id,
                           Features.var_name,
                           Features.var_val)
             .filter(Features.commented == 0)
             .filter(Features.var_name.in_(transfer_converter.var_names()))
             )

    return [transfer_converter.to_model(row) for row in query]


@daosession
def find_park_position_range(session):
    query = (session.query(Features.var_val)
             .filter(Features.commented == 0)
             .filter(Features.var_name == 'parkpos')
             )

    raw_range = query.scalar()
    if not raw_range:
        return None

    return tuple(int(x) for x in raw_range.split("-"))
