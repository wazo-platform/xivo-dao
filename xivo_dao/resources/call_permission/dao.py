# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from xivo_dao.helpers.db_manager import daosession

from xivo_dao.resources.permission.persistor import PermissionPersistor
from xivo_dao.resources.permission.search import permission_search


@daosession
def search(session, **parameters):
    return PermissionPersistor(session, permission_search).search(parameters)


@daosession
def get(session, permission_id):
    return PermissionPersistor(session, permission_search).get_by({'id': permission_id})


@daosession
def get_by(session, **criteria):
    return PermissionPersistor(session, permission_search).get_by(criteria)


@daosession
def find(session, permission_id):
    return PermissionPersistor(session, permission_search).find_by({'id': permission_id})


@daosession
def find_by(session, **criteria):
    return PermissionPersistor(session, permission_search).find_by(criteria)


@daosession
def find_all_by(session, **criteria):
    return PermissionPersistor(session, permission_search).find_all_by(criteria)


@daosession
def create(session, user):
    return PermissionPersistor(session, permission_search).create(user)


@daosession
def edit(session, user):
    PermissionPersistor(session, permission_search).edit(user)


@daosession
def delete(session, user):
    PermissionPersistor(session, permission_search).delete(user)
