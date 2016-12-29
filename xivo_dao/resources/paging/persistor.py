# -*- coding: UTF-8 -*-

# Copyright 2016 The Wazo Authors  (see the AUTHORS file)
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

from xivo_dao.alchemy.paging import Paging

from xivo_dao.helpers import errors
from xivo_dao.resources.utils.search import SearchResult, CriteriaBuilderMixin


class PagingPersistor(CriteriaBuilderMixin):

    _search_table = Paging

    def __init__(self, session, paging_search):
        self.session = session
        self.paging_search = paging_search

    def find_by(self, criteria):
        query = self._find_query(criteria)
        return query.first()

    def _find_query(self, criteria):
        query = self.session.query(Paging)
        return self.build_criteria(query, criteria)

    def get_by(self, criteria):
        paging = self.find_by(criteria)
        if not paging:
            raise errors.not_found('Paging', **criteria)
        return paging

    def find_all_by(self, criteria):
        query = self._find_query(criteria)
        return query.all()

    def search(self, parameters):
        rows, total = self.paging_search.search(self.session, parameters)
        return SearchResult(total, rows)

    def create(self, paging):
        self.session.add(paging)
        self.session.flush()
        return paging

    def edit(self, paging):
        self.session.add(paging)
        self.session.flush()

    def delete(self, paging):
        self.session.delete(paging)
        self.session.flush()
