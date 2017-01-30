# -*- coding: UTF-8 -*-

# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
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

from xivo_dao.alchemy.moh import MOH

from xivo_dao.helpers import errors
from xivo_dao.resources.utils.search import SearchResult, CriteriaBuilderMixin


class MOHPersistor(CriteriaBuilderMixin):

    _search_table = MOH

    def __init__(self, session, moh_search):
        self.session = session
        self.moh_search = moh_search

    def find_by(self, criteria):
        query = self._find_query(criteria)
        return query.first()

    def _find_query(self, criteria):
        query = self.session.query(MOH)
        return self.build_criteria(query, criteria)

    def get_by(self, criteria):
        moh = self.find_by(criteria)
        if not moh:
            raise errors.not_found('MOH', **criteria)
        return moh

    def find_all_by(self, criteria):
        query = self._find_query(criteria)
        return query.all()

    def search(self, parameters):
        rows, total = self.moh_search.search(self.session, parameters)
        return SearchResult(total, rows)

    def create(self, moh):
        self.session.add(moh)
        self.session.flush()
        return moh

    def edit(self, moh):
        self.session.add(moh)
        self.session.flush()

    def delete(self, moh):
        self.session.delete(moh)
        self.session.flush()