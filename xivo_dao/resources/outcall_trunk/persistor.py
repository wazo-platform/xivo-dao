# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
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

from xivo_dao.helpers import errors
from xivo_dao.alchemy.outcalltrunk import OutcallTrunk
from xivo_dao.resources.utils.search import CriteriaBuilderMixin


class Persistor(CriteriaBuilderMixin):

    _search_table = OutcallTrunk

    def __init__(self, session):
        self.session = session

    def find_by(self, **criteria):
        query = self._find_query(criteria)
        return query.first()

    def _find_query(self, criteria):
        query = self.session.query(OutcallTrunk).order_by(OutcallTrunk.priority)
        return self.build_criteria(query, criteria)

    def get_by(self, **criteria):
        outcall_trunk = self.find_by(**criteria)
        if not outcall_trunk:
            raise errors.not_found('OutcallTrunk', **criteria)
        return outcall_trunk

    def find_all_by(self, **criteria):
        query = self._find_query(criteria)
        return query.all()

    def associate_all_trunks(self, outcall, trunks):
        for priority, trunk in enumerate(trunks):
            outcall_trunk = OutcallTrunk(outcall_id=outcall.id, trunk_id=trunk.id, priority=priority)
            self.session.add(outcall_trunk)
        self.session.flush()
        return self.find_all_by(outcall_id=outcall.id)

    def dissociate_all_trunks_by_outcall(self, outcall):
        outcall_trunks = self.find_all_by(outcall_id=outcall.id)
        for outcall_trunk in outcall_trunks:
            self.session.delete(outcall_trunk)
        self.session.flush()
        return outcall_trunks
