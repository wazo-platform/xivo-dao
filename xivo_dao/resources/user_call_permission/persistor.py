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
from xivo_dao.alchemy.rightcallmember import RightCallMember as UserCallPermission


class Persistor(object):

    def __init__(self, session):
        self.session = session

    def find_by(self, **criteria):
        query = self._find_query(criteria)
        return query.first()

    def _find_query(self, criteria):
        query = self.session.query(UserCallPermission)
        for name, value in criteria.iteritems():
            column = self._get_column(name)
            query = query.filter(column == value)
        return query

    def _get_column(self, name):
        column = getattr(UserCallPermission, name, None)
        if column is None:
            raise errors.unknown(name)
        return column

    def get_by(self, **criteria):
        user_call_permission = self.find_by(**criteria)
        if not user_call_permission:
            raise errors.not_found('UserCallPermission', **criteria)
        return user_call_permission

    def find_all_by(self, **criteria):
        query = self._find_query(criteria)
        return query.all()

    def associate_user_call_permission(self, user, call_permission):
        user_call_permission = UserCallPermission(user_id=user.id, call_permission_id=call_permission.id)
        self.session.add(user_call_permission)
        self.session.flush()
        return user_call_permission

    def dissociate_user_call_permission(self, user, call_permission):
        user_call_permission = self.get_by(user_id=user.id, call_permission_id=call_permission.id)
        self.session.delete(user_call_permission)
        self.session.flush()
        return user_call_permission
