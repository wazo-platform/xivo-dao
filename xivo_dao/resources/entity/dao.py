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

from xivo_dao.resources.entity.persistor import EntityPersistor
from xivo_dao.resources.entity.search import entity_search


@daosession
def search(session, **parameters):
    return EntityPersistor(session, entity_search).search(parameters)


@daosession
def get(session, call_permission_id):
    return EntityPersistor(session, entity_search).get_by({'id': call_permission_id})


@daosession
def get_by(session, **criteria):
    return EntityPersistor(session, entity_search).get_by(criteria)


@daosession
def find(session, call_permission_id):
    return EntityPersistor(session, entity_search).find_by({'id': call_permission_id})


@daosession
def find_by(session, **criteria):
    return EntityPersistor(session, entity_search).find_by(criteria)


@daosession
def find_all_by(session, **criteria):
    return EntityPersistor(session, entity_search).find_all_by(criteria)


@daosession
def create(session, entity):
    return EntityPersistor(session, entity_search).create(entity)


@daosession
def edit(session, entity):
    EntityPersistor(session, entity_search).edit(entity)


@daosession
def delete(session, entity):
    EntityPersistor(session, entity_search).delete(entity)
