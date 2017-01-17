# -*- coding: UTF-8 -*-

# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
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

from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.incall import Incall
from xivo_dao.alchemy.rightcallmember import RightCallMember

from xivo_dao.helpers import errors
from xivo_dao.resources.utils.search import SearchResult, CriteriaBuilderMixin


class IncallPersistor(CriteriaBuilderMixin):

    _search_table = Incall

    def __init__(self, session, incall_search):
        self.session = session
        self.incall_search = incall_search

    def find_by(self, criteria):
        query = self._find_query(criteria)
        return query.first()

    def _find_query(self, criteria):
        query = self.session.query(Incall)
        return self.build_criteria(query, criteria)

    def get_by(self, criteria):
        incall = self.find_by(criteria)
        if not incall:
            raise errors.not_found('Incall', **criteria)
        return incall

    def find_all_by(self, criteria):
        query = self._find_query(criteria)
        return query.all()

    def search(self, parameters):
        rows, total = self.incall_search.search(self.session, parameters)
        return SearchResult(total, rows)

    def create(self, incall):
        self.session.add(incall)
        self.session.flush()
        return incall

    def edit(self, incall):
        self.session.add(incall)
        self.session.flush()

    def delete(self, incall):
        self._delete_associations(incall)
        self.session.delete(incall)
        self.session.flush()

    def _delete_associations(self, incall):
        (self.session.query(RightCallMember)
         .filter(RightCallMember.type == 'incall')
         .filter(RightCallMember.typeval == str(incall.id))
         .delete())

        (self.session.query(Extension)
         .filter(Extension.type == 'incall')
         .filter(Extension.typeval == str(incall.id))
         .update({'type': 'user', 'typeval': '0'}))
