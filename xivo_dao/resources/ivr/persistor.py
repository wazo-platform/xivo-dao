# -*- coding: UTF-8 -*-

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

from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.alchemy.ivr import IVR

from xivo_dao.helpers import errors
from xivo_dao.resources.utils.search import SearchResult, CriteriaBuilderMixin


class IVRPersistor(CriteriaBuilderMixin):

    _search_table = IVR

    def __init__(self, session, ivr_search):
        self.session = session
        self.ivr_search = ivr_search

    def find_by(self, criteria):
        query = self._find_query(criteria)
        return query.first()

    def _find_query(self, criteria):
        query = self.session.query(IVR)
        return self.build_criteria(query, criteria)

    def get_by(self, criteria):
        ivr = self.find_by(criteria)
        if not ivr:
            raise errors.not_found('IVR', **criteria)
        return ivr

    def find_all_by(self, criteria):
        query = self._find_query(criteria)
        return query.all()

    def search(self, parameters):
        rows, total = self.ivr_search.search(self.session, parameters)
        return SearchResult(total, rows)

    def create(self, ivr):
        self.session.add(ivr)
        self.session.flush()
        return ivr

    def edit(self, ivr):
        self.session.add(ivr)
        self.session.flush()

    def delete(self, ivr):
        self._delete_associations(ivr)
        self.session.delete(ivr)
        self.session.flush()

    def _delete_associations(self, ivr):
        # "unlink" dialactions that points on this IVR
        (self.session.query(Dialaction)
         .filter(Dialaction.action == 'ivr')
         .filter(Dialaction.actionarg1 == str(ivr.id))
         .update({'linked': 0}))
