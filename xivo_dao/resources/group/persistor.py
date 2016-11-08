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

from xivo_dao.alchemy.groupfeatures import GroupFeatures as Group
from xivo_dao.alchemy.rightcallmember import RightCallMember
from xivo_dao.alchemy.schedulepath import SchedulePath

from xivo_dao.helpers import errors
from xivo_dao.resources.utils.search import SearchResult, CriteriaBuilderMixin


class GroupPersistor(CriteriaBuilderMixin):

    _search_table = Group

    def __init__(self, session, group_search):
        self.session = session
        self.group_search = group_search

    def find_by(self, criteria):
        query = self._find_query(criteria)
        return query.first()

    def _find_query(self, criteria):
        query = self.session.query(Group)
        return self.build_criteria(query, criteria)

    def get_by(self, criteria):
        group = self.find_by(criteria)
        if not group:
            raise errors.not_found('Group', **criteria)
        return group

    def find_all_by(self, criteria):
        query = self._find_query(criteria)
        return query.all()

    def search(self, parameters):
        rows, total = self.group_search.search(self.session, parameters)
        return SearchResult(total, rows)

    def create(self, group):
        self.session.add(group)
        self.session.flush()
        return group

    def edit(self, group):
        group.fix_group()
        self.session.add(group)
        self.session.flush()

    def delete(self, group):
        self._delete_associations(group)
        self.session.delete(group)
        self.session.flush()

    def _delete_associations(self, group):
        (self.session.query(RightCallMember)
         .filter(RightCallMember.type == 'group')
         .filter(RightCallMember.typeval == str(group.id))
         .delete())

        (self.session.query(SchedulePath)
         .filter(SchedulePath.path == 'group')
         .filter(SchedulePath.pathid == group.id)
         .delete())

        for extension in group.extensions:
            extension.type = 'user'
            extension.typeval = '0'
