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

from xivo_dao.alchemy.switchboard import Switchboard

from xivo_dao.helpers import errors
from xivo_dao.resources.utils.search import SearchResult, CriteriaBuilderMixin


class SwitchboardPersistor(CriteriaBuilderMixin):

    _search_table = Switchboard

    def __init__(self, session, switchboard_search):
        self.session = session
        self.switchboard_search = switchboard_search

    def find_by(self, criteria):
        query = self._find_query(criteria)
        return query.first()

    def _find_query(self, criteria):
        query = self.session.query(Switchboard)
        return self.build_criteria(query, criteria)

    def get_by(self, criteria):
        switchboard = self.find_by(criteria)
        if not switchboard:
            raise errors.not_found('Switchboard', **criteria)
        return switchboard

    def find_all_by(self, criteria):
        query = self._find_query(criteria)
        return query.all()

    def search(self, parameters):
        rows, total = self.switchboard_search.search(self.session, parameters)
        return SearchResult(total, rows)

    def create(self, switchboard):
        self.session.add(switchboard)
        self.session.flush()
        return switchboard

    def edit(self, switchboard):
        self.session.add(switchboard)
        self.session.flush()

    def delete(self, switchboard):
        self.session.delete(switchboard)
        self.session.flush()
