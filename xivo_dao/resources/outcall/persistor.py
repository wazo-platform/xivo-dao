# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
# Copyright (C) 2016 Proformatique Inc.
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

from xivo_dao.alchemy.outcall import Outcall
from xivo_dao.alchemy.rightcallmember import RightCallMember
from xivo_dao.alchemy.schedulepath import SchedulePath

from xivo_dao.helpers import errors
from xivo_dao.resources.utils.search import SearchResult, CriteriaBuilderMixin


class OutcallPersistor(CriteriaBuilderMixin):

    _search_table = Outcall

    def __init__(self, session, outcall_search):
        self.session = session
        self.outcall_search = outcall_search

    def find_by(self, criteria):
        query = self._find_query(criteria)
        return query.first()

    def _find_query(self, criteria):
        query = self.session.query(Outcall)
        return self.build_criteria(query, criteria)

    def get_by(self, criteria):
        outcall = self.find_by(criteria)
        if not outcall:
            raise errors.not_found('Outcall', **criteria)
        return outcall

    def find_all_by(self, criteria):
        query = self._find_query(criteria)
        return query.all()

    def search(self, parameters):
        rows, total = self.outcall_search.search(self.session, parameters)
        return SearchResult(total, rows)

    def create(self, outcall):
        self.session.add(outcall)
        self.session.flush()
        return outcall

    def edit(self, outcall):
        self.session.add(outcall)
        self.session.flush()

    def delete(self, outcall):
        self._delete_associations(outcall)
        self.session.delete(outcall)
        self.session.flush()

    def _delete_associations(self, outcall):
        (self.session.query(RightCallMember)
         .filter(RightCallMember.type == 'outcall')
         .filter(RightCallMember.typeval == str(outcall.id))
         .delete())

        (self.session.query(SchedulePath)
         .filter(SchedulePath.path == 'outcall')
         .filter(SchedulePath.pathid == outcall.id)
         .delete())

        for extension in outcall.extensions:
            extension.type = 'user'
            extension.typeval = '0'
