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

from sqlalchemy import sql, Integer

from xivo_dao.alchemy.callfiltermember import Callfiltermember
from xivo_dao.helpers.db_manager import daosession
from xivo_dao.resources.bsfilter.model import FilterMember


@daosession
def filter_member_exists(session, filter_member_id):
    query = (session.query(Callfiltermember)
             .filter(Callfiltermember.id == filter_member_id)
             )

    return query.count() > 0


@daosession
def find_all_by_member_id(session, member_id):
    query = (session.query(Callfiltermember.id,
                           sql.cast(Callfiltermember.typeval, Integer).label('member_id'),
                           Callfiltermember.bstype.label('role'))
             .filter(Callfiltermember.type == 'user')
             .filter(Callfiltermember.bstype.in_(['boss', 'secretary']))
             .filter(sql.cast(Callfiltermember.typeval, Integer) == member_id)
             )

    return [FilterMember(id=row.id, member_id=row.member_id, role=row.role)
            for row in query]
