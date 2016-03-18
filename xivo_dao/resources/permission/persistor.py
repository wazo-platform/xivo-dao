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

from xivo_dao.alchemy.rightcall import RightCall as Permission
from xivo_dao.alchemy.rightcallmember import RightCallMember

from xivo_dao.helpers import errors
from xivo_dao.resources.utils.search import SearchResult


class PermissionPersistor(object):

    def __init__(self, session, permission_search):
        self.session = session
        self.permission_search = permission_search

    def find_by(self, criteria):
        query = self._find_query(criteria)
        return query.first()

    def _find_query(self, criteria):
        query = self.session.query(Permission)
        for name, value in criteria.iteritems():
            column = self._get_column(name)
            query = query.filter(column == value)
        return query

    def _get_column(self, name):
        column = getattr(Permission, name, None)
        if column is None:
            raise errors.unknown(name)
        return column

    def get_by(self, criteria):
        user = self.find_by(criteria)
        if not user:
            raise errors.not_found('Permission', **criteria)
        return user

    def find_all_by(self, criteria):
        query = self._find_query(criteria)
        return query.all()

    def search(self, parameters):
        rows, total = self.permission_search.search(self.session, parameters)
        return SearchResult(total, rows)

    def create(self, permission):
        self.session.add(permission)
        self.session.flush()
        return permission

    def edit(self, permission):
        self.session.add(permission)
        self.session.flush()

    def delete(self, permission):
        (self.session.query(RightCallMember)
         .filter(RightCallMember.rightcallid == permission.id)
         .delete())
        self.session.delete(permission)
        self.session.flush()
