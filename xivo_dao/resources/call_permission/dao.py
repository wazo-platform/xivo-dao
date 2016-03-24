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

from xivo_dao.resources.call_permission.persistor import CallPermissionPersistor
from xivo_dao.resources.call_permission.search import call_permission_search


@daosession
def search(session, **parameters):
    return CallPermissionPersistor(session, call_permission_search).search(parameters)


@daosession
def get(session, call_permission_id):
    return CallPermissionPersistor(session, call_permission_search).get_by({'id': call_permission_id})


@daosession
def get_by(session, **criteria):
    return CallPermissionPersistor(session, call_permission_search).get_by(criteria)


@daosession
def find(session, call_permission_id):
    return CallPermissionPersistor(session, call_permission_search).find_by({'id': call_permission_id})


@daosession
def find_by(session, **criteria):
    return CallPermissionPersistor(session, call_permission_search).find_by(criteria)


@daosession
def find_all_by(session, **criteria):
    return CallPermissionPersistor(session, call_permission_search).find_all_by(criteria)


@daosession
def create(session, user):
    return CallPermissionPersistor(session, call_permission_search).create(user)


@daosession
def edit(session, user):
    CallPermissionPersistor(session, call_permission_search).edit(user)


@daosession
def delete(session, user):
    CallPermissionPersistor(session, call_permission_search).delete(user)
