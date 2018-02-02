# -*- coding: UTF-8 -*-
# Copyright 2015-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy import sql, Integer

from xivo_dao.alchemy.callfiltermember import Callfiltermember
from xivo_dao.helpers.db_manager import daosession
from xivo_dao.resources.bsfilter.model import FilterMember


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
